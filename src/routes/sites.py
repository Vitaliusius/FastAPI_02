from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Path as FastApiPath, Request
from fastapi.responses import StreamingResponse

from src.s3_service import get_file_urls, get_screenshot_url
from src.schemas import (
    CreatedSiteResponse,
    CreateSitePayload,
    GenerateSitePayload,
    NotFoundErrorSchema,
    SiteSchema,
)
from src.services.site_generator import generate_site_stream

router = APIRouter(prefix="/sites", tags=["Sites"])


@router.get(
    "/my",
    response_model=list[SiteSchema],
    summary="Получить полный список сайтов пользователя",
)
async def get_my_sites():
    html_url, download_url = get_file_urls("index.html")
    screenshot_url = get_screenshot_url()
    return [
        SiteSchema(
            id="1",
            name="Сайт-визитка",
            html_url=html_url,
            download_url=download_url,
            screenshot_url=screenshot_url,
        )
    ]


@router.post(
    "/create",
    response_model=CreatedSiteResponse,
    summary="Создать новый сайт",
    status_code=200,
)
async def create_site(payload: CreateSitePayload):
    now = datetime.now(UTC)
    html_url, download_url = get_file_urls("index.html")
    screenshot_url = get_screenshot_url()

    return CreatedSiteResponse(
        id="1",
        title=payload.title,
        prompt=payload.prompt,
        created_at=now,
        updated_at=now,
        html_url=html_url,
        download_url=download_url,
        screenshot_url=screenshot_url,
    )


@router.get(
    "/{site_id}",
    response_model=SiteSchema,
    summary="Получить данные сайта",
    responses={
        200: {
            "description": "Успешное получение данных сайта",
            "model": SiteSchema,
        },
        404: {
            "description": "Сайт с указанным идентификатором не найден",
            "model": NotFoundErrorSchema,
            "content": {
                "application/json": {
                    "example": {"detail": "Сайт не найден"}
                }
            },
        },
    },
)
async def get_site_details(
    site_id: Annotated[str, FastApiPath(description="Идентификатор сайта")],
):
    html_url, download_url = get_file_urls("index.html")
    screenshot_url = get_screenshot_url()
    return SiteSchema(
        id=site_id,
        name="Сайт-визитка",
        html_url=html_url,
        download_url=download_url,
        screenshot_url=screenshot_url,
    )


@router.post(
    "/{site_id}/generate",
    summary="Генерация HTML-разметки сайта",
    response_class=StreamingResponse,
)
async def generate_site(
    site_id: Annotated[str, FastApiPath(description="Идентификатор сайта")],
    request: Request,
    payload: GenerateSitePayload | None = None,
) -> StreamingResponse:
    user_prompt = (
        payload.prompt
        if payload and payload.prompt
        else "Сайт-визитка для автосервиса с прайс-листом и формой записи"
    )

    return StreamingResponse(
        generate_site_stream(
            prompt=user_prompt,
            gotenberg_client=request.app.state.gotenberg_client,
        ),
        media_type="text/event-stream",
    )
