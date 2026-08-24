from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Annotated

import anyio
import httpx
from fastapi import FastAPI, Path as FastApiPath, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from gotenberg_api import GotenbergServerError, ScreenshotHTMLRequest
from html_page_generator import (
    AsyncDeepseekClient,
    AsyncPageGenerator,
    AsyncUnsplashClient,
)
from openai import APIError, AuthenticationError
from pydantic import BaseModel, Field

from src.env_settings import AppSettings
from src.s3_service import S3StorageService

settings = AppSettings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    S3StorageService.get_session()

    app.state.gotenberg_client = httpx.AsyncClient(
        base_url=str(settings.gotenberg.endpoint_url),
        timeout=settings.gotenberg.timeout,
        limits=httpx.Limits(
            max_connections=settings.gotenberg.max_connections,
            max_keepalive_connections=settings.gotenberg.max_connections,
        ),
    )

    yield
    await app.state.gotenberg_client.aclose()


app = FastAPI(title="FastAI Site Generator", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class UserSchema(BaseModel):
    id: str = "1"
    email: str = "example@example.com"
    username: str = "user123"


class SiteSchema(BaseModel):
    id: str
    name: str = "Сайт-визитка"
    html_url: str
    download_url: str
    screenshot_url: str = Field(
        default="https://placehold.co/600x400?text=Site+Preview",
        description="Ссылка на скриншот сайта в S3",
    )


class GenerateSitePayload(BaseModel):
    prompt: str = Field(
        default="Сайт-визитка для автосервиса с прайс-листом и формой записи",
        description="Промпт с описанием тематики сайта",
    )


async def generate_site_stream(prompt: str, gotenberg_client: httpx.AsyncClient) -> AsyncGenerator[str, None]:
    timeout = settings.unsplash_timeout or 20
    unsplash_key = settings.unsplash_api_key.get_secret_value() if settings.unsplash_api_key else "Нет ключа"

    async with (
        AsyncUnsplashClient.setup(unsplash_key, timeout=timeout),
        AsyncDeepseekClient.setup(
            settings.deepseek_api_key.get_secret_value(),
            str(settings.deepseek_base_url),
            settings.deepseek_model,
        ),
    ):
        generator = AsyncPageGenerator(debug_mode=settings.debug)
        try:
            async for chunk in generator(prompt):
                yield chunk
        except AuthenticationError:
            yield "\n[Ошибка авторизации]: Проверьте правильность API-ключа в .env\n"
        except APIError as e:
            yield f"\n[Ошибка API]: {e.message}\n"
        except anyio.get_cancelled_exc_class():
            print("[Streaming] Генерация была отменена клиентом.")
            raise
        finally:
            with anyio.CancelScope(shield=True):
                if generator.html_page and generator.html_page.html_code:
                    raw_html = generator.html_page.html_code
                    await S3StorageService.upload_html(raw_html, "index.html")

                    try:
                        screenshot_request = ScreenshotHTMLRequest(
                            index_html=raw_html,
                            width=1000,
                            format="png",
                            wait_delay=2,
                        )
                        screenshot_bytes = await screenshot_request.asend(gotenberg_client)
                        await S3StorageService.upload_file(
                            file_bytes=screenshot_bytes,
                            filename="index.png",
                            content_type="image/png",
                        )
                    except (GotenbergServerError, httpx.HTTPError) as e:
                        print(f"[Gotenberg] Ошибка генерации скриншота: {e}")


@app.get("/users/me", response_model=UserSchema, summary="Получить текущего пользователя")
async def get_current_user():
    return UserSchema()


@app.get("/sites", response_model=list[SiteSchema], summary="Получить список сайтов пользователя")
async def get_user_sites():
    html_url, download_url = S3StorageService.get_file_urls("index.html")
    screenshot_url = S3StorageService.get_screenshot_url("index.png")
    return [
        SiteSchema(
            id="1",
            name="Сайт-визитка",
            html_url=html_url,
            download_url=download_url,
            screenshot_url=screenshot_url,
        )
    ]


@app.get("/sites/{site_id}", response_model=SiteSchema, summary="Получить данные сайта")
async def get_site_details(
    site_id: Annotated[str, FastApiPath(description="Идентификатор сайта")],
):
    html_url, download_url = S3StorageService.get_file_urls("index.html")
    screenshot_url = S3StorageService.get_screenshot_url("index.png")
    return SiteSchema(
        id=site_id,
        name="Сайт-визитка",
        html_url=html_url,
        download_url=download_url,
        screenshot_url=screenshot_url,
    )


@app.post(
    "/sites/{site_id}/generate",
    summary="Генерация HTML-разметки сайта",
    response_class=StreamingResponse,
)
async def generate_site(
    site_id: Annotated[str, FastApiPath(description="Идентификатор сайта")],
    request: Request,
    payload: GenerateSitePayload | None = None,
) -> StreamingResponse:
    user_prompt = (
        payload.prompt if payload and payload.prompt else "Сайт-визитка для автосервиса с прайс-листом и формой записи"
    )

    return StreamingResponse(
        generate_site_stream(user_prompt, request.app.state.gotenberg_client),
        media_type="text/event-stream",
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
