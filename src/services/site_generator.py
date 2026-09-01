import logging
from collections.abc import AsyncGenerator
from typing import Any

import httpx
from botocore.exceptions import BotoCoreError, ClientError
from gotenberg_api import GotenbergServerError, ScreenshotHTMLRequest
from html_page_generator import AsyncPageGenerator
from openai import APIError, AuthenticationError

from src.env_settings import settings
from src.services.s3_service import upload_file, upload_html

logger = logging.getLogger(__name__)


async def capture_screenshot(
    html_code: str,
    gotenberg_client: httpx.AsyncClient,
) -> bytes:
    screenshot_request = ScreenshotHTMLRequest(
        index_html=html_code,
        width=settings.gotenberg.width,
        format=settings.gotenberg.format,
        wait_delay=settings.gotenberg.wait_delay,
    )
    return await screenshot_request.asend(gotenberg_client)


async def save_artifacts_after_generation(
    html_code: str,
    gotenberg_client: httpx.AsyncClient,
    s3_client: Any,
) -> str | None:
    try:
        await upload_html(s3_client, html_code, filename="index.html")
    except (BotoCoreError, ClientError) as e:
        logger.exception("[S3] Ошибка при сохранении HTML")
        return f"\n[Ошибка S3]: Не удалось сохранить сгенерированный сайт в хранилище ({e}).\n"

    img_format = settings.gotenberg.format
    screenshot_filename = f"index.{img_format}"
    content_type = f"image/{img_format}"

    try:
        screenshot_bytes = await capture_screenshot(html_code, gotenberg_client)
        await upload_file(
            s3_client=s3_client,
            file_bytes=screenshot_bytes,
            filename=screenshot_filename,
            content_type=content_type,
        )
    except (GotenbergServerError, httpx.HTTPError) as e:
        logger.warning(f"[Gotenberg] Ошибка генерации скриншота: {e}")
    except (BotoCoreError, ClientError) as e:
        logger.warning(f"[S3] Ошибка сохранения скриншота: {e}")

    return None


async def generate_site_stream(
    prompt: str,
    gotenberg_client: httpx.AsyncClient,
    s3_client: Any,
) -> AsyncGenerator[str, None]:
    generator = AsyncPageGenerator(debug_mode=settings.debug)

    try:
        async for chunk in generator(prompt):
            yield chunk

        if generator.html_page and generator.html_page.html_code:
            error_message = await save_artifacts_after_generation(
                generator.html_page.html_code,
                gotenberg_client,
                s3_client,
            )
            if error_message:
                yield error_message

    except AuthenticationError:
        yield "\n[Ошибка авторизации]: Проверьте правильность API-ключа в .env\n"
    except APIError as e:
        yield f"\n[Ошибка API]: {e.message}\n"
