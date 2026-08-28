import aioboto3
from aiobotocore.config import AioConfig
from pydantic import HttpUrl

from src.env_settings import settings

_session = aioboto3.Session()


def get_s3_client():
    config = AioConfig(
        connect_timeout=settings.s3.connect_timeout,
        read_timeout=settings.s3.read_timeout,
        max_pool_connections=settings.s3.max_connections,
    )
    return _session.client(
        "s3",
        endpoint_url=str(settings.s3.endpoint_url),
        aws_access_key_id=settings.s3.access_key.get_secret_value(),
        aws_secret_access_key=settings.s3.secret_key.get_secret_value(),
        config=config,
    )


async def upload_file(
    file_bytes: bytes,
    filename: str,
    content_type: str = "text/html",
) -> None:
    async with get_s3_client() as s3:
        await s3.put_object(
            Bucket=settings.s3.bucket_name,
            Key=filename,
            Body=file_bytes,
            ContentType=content_type,
            ContentDisposition="inline",
        )


async def upload_html(html_content: str, filename: str = "index.html") -> None:
    await upload_file(
        file_bytes=html_content.encode("utf-8"),
        filename=filename,
        content_type="text/html",
    )


def get_file_urls(filename: str = "index.html") -> tuple[HttpUrl, HttpUrl]:
    base_endpoint = str(settings.s3.endpoint_url).rstrip("/")
    view_url = f"{base_endpoint}/{settings.s3.bucket_name}/{filename}"
    download_url = f"{view_url}?response-content-disposition=attachment"
    return HttpUrl(view_url), HttpUrl(download_url)


def get_screenshot_url(filename: str | None = None) -> HttpUrl:
    if filename is None:
        filename = f"index.{settings.gotenberg.format}"
    base_endpoint = str(settings.s3.endpoint_url).rstrip("/")
    return HttpUrl(f"{base_endpoint}/{settings.s3.bucket_name}/{filename}")
