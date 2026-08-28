from collections.abc import AsyncGenerator
import logging

import httpx
from gotenberg_api import GotenbergServerError, ScreenshotHTMLRequest
from html_page_generator import AsyncPageGenerator
from openai import APIError, AuthenticationError

from src.env_settings import settings
from src.s3_service import upload_file, upload_html

logger = logging.getLogger(__name__)


async def save_html_to_s3(html_code: str, filename: str = "index.html") -> None:
    await upload_html(html_code, filename=filename)


async def capture_screenshot(
    html_code: str, gotenberg_client: httpx.AsyncClient
) -> bytes:
    screenshot_request = ScreenshotHTMLRequest(
        index_html=html_code,
        width=settings.gotenberg.width,
        format=settings.gotenberg.format,
        wait_delay=settings.gotenberg.wait_delay,
    )
    return await screenshot_request.asend(gotenberg_client)


async def save_screenshot_to_s3(
    screenshot_bytes: bytes,
    filename: str,
    content_type: str,
) -> None:
    await upload_file(
        file_bytes=screenshot_bytes,
        filename=filename,
        content_type=content_type,
    )


async def generate_site_stream(
    prompt: str,
    gotenberg_client: httpx.AsyncClient,
) -> AsyncGenerator[str, None]:
    generator = AsyncPageGenerator(debug_mode=settings.debug)

    try:
        async for chunk in generator(prompt):
            yield chunk

        if generator.html_page and generator.html_page.html_code:
            raw_html = generator.html_page.html_code
            try:
                await save_html_to_s3(raw_html, "index.html")
            except Exception as e:
                logger.exception("[S3] Ошибка при сохранении HTML")
                yield f"\n[Ошибка S3]: Не удалось сохранить сгенерированный сайт в хранилище ({e}).\n"
                return

            img_format = settings.gotenberg.format
            screenshot_filename = f"index.{img_format}"
            content_type = f"image/{img_format}"

            try:
                screenshot_bytes = await capture_screenshot(raw_html, gotenberg_client)
                await save_screenshot_to_s3(
                    screenshot_bytes=screenshot_bytes,
                    filename=screenshot_filename,
                    content_type=content_type,
                )
            except (GotenbergServerError, httpx.HTTPError) as e:
                logger.warning(f"[Gotenberg] Ошибка генерации скриншота: {e}")
            except Exception as e:
                logger.warning(f"[S3] Ошибка сохранения скриншота: {e}")

    except AuthenticationError:
        yield "\n[Ошибка авторизации]: Проверьте правильность API-ключа в .env\n"
    except APIError as e:
        yield f"\n[Ошибка API]: {e.message}\n"
