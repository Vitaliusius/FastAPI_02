from collections.abc import AsyncGenerator
from pathlib import Path
from typing import Annotated

import anyio
from fastapi import FastAPI, HTTPException, Path as FastApiPath, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from html_page_generator import (
    AsyncDeepseekClient,
    AsyncPageGenerator,
    AsyncUnsplashClient,
)
from openai import APIError, AuthenticationError
from pydantic import BaseModel, Field

from src.env_settings import AppSettings

settings = AppSettings()

SITES_DIR = Path("sites")
SITES_DIR.mkdir(parents=True, exist_ok=True)
INDEX_FILE = SITES_DIR / "index.html"


app = FastAPI(title="FastAI Site Generator")

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
    html_url: str = "/sites/index.html"
    download_url: str = "/sites/index.html"


class GenerateSitePayload(BaseModel):
    prompt: str = Field(
        default="Сайт-визитка для автосервиса с прайс-листом и формой записи",
        description="Промпт с описанием тематики сайта",
    )


async def generate_site_stream(prompt: str) -> AsyncGenerator[str, None]:
    timeout = settings.unsplash_timeout or 20
    unsplash_key = (
        settings.unsplash_api_key.get_secret_value()
        if settings.unsplash_api_key
        else "Нет ключа"
    )

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
                    INDEX_FILE.write_text(
                        generator.html_page.html_code, encoding="utf-8"
                    )
                    print(f"[Success] Файл сохранен: {INDEX_FILE.resolve()}")


@app.get("/users/me", response_model=UserSchema, summary="Получить текущего пользователя")
async def get_current_user():
    return UserSchema()


@app.get("/sites/{site_id}", response_model=SiteSchema, summary="Получить данные сайта")
async def get_site_details(
    site_id: Annotated[str, FastApiPath(description="Идентификатор сайта")],
):
    return SiteSchema(
        id=site_id,
        name="Сайт-визитка",
        html_url="/sites/index.html",
        download_url=f"/sites/{site_id}/download",
    )


@app.get("/sites/{site_id}/download", summary="Скачать HTML-файл сайта")
async def download_site(
    site_id: Annotated[str, FastApiPath(description="Идентификатор сайта")],
):
    if not INDEX_FILE.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Сайт еще не сгенерирован",
        )
    return FileResponse(
        path=INDEX_FILE,
        filename="index.html",
        media_type="text/html",
    )


@app.post(
    "/sites/{site_id}/generate",
    summary="Генерация HTML-разметки сайта",
    response_class=StreamingResponse,
)
async def generate_site(
    site_id: Annotated[str, FastApiPath(description="Идентификатор сайта")],
    payload: GenerateSitePayload | None = None,
) -> StreamingResponse:
    user_prompt = (
        payload.prompt
        if payload and payload.prompt
        else "Сайт-визитка для автосервиса с прайс-листом и формой записи"
    )

    return StreamingResponse(
        generate_site_stream(user_prompt),
        media_type="text/event-stream",
    )


app.mount("/sites", StaticFiles(directory=str(SITES_DIR), html=True), name="sites")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
