import aioboto3
from aiobotocore.config import AioConfig

from src.env_settings import AppSettings

settings = AppSettings()


class S3StorageService:
    _session: aioboto3.Session | None = None

    @classmethod
    def get_session(cls) -> aioboto3.Session:
        if cls._session is None:
            cls._session = aioboto3.Session()
        return cls._session

    @classmethod
    def get_client(cls):
        session = cls.get_session()
        config = AioConfig(
            connect_timeout=settings.s3.connect_timeout,
            read_timeout=settings.s3.read_timeout,
            max_pool_connections=settings.s3.max_connections,
        )
        return session.client(
            "s3",
            endpoint_url=str(settings.s3.endpoint_url),
            aws_access_key_id=settings.s3.access_key.get_secret_value(),
            aws_secret_access_key=settings.s3.secret_key.get_secret_value(),
            config=config,
        )

    @classmethod
    async def upload_html(cls, html_content: str, filename: str = "index.html") -> None:
        async with cls.get_client() as s3:
            await s3.put_object(
                Bucket=settings.s3.bucket_name,
                Key=filename,
                Body=html_content.encode("utf-8"),
                ContentType="text/html",
                ContentDisposition="inline",
            )

    @classmethod
    def get_file_urls(cls, filename: str = "index.html") -> tuple[str, str]:
        base_endpoint = str(settings.s3.endpoint_url).rstrip("/")
        view_url = f"{base_endpoint}/{settings.s3.bucket_name}/{filename}"
        download_url = f"{view_url}?response-content-disposition=attachment"
        return view_url, download_url

    @classmethod
    def get_screenshot_url(cls, filename: str = "index.png") -> str:
        base_endpoint = str(settings.s3.endpoint_url).rstrip("/")
        return f"{base_endpoint}/{settings.s3.bucket_name}/{filename}"

    @classmethod
    async def upload_file(
        cls,
        file_bytes: bytes,
        filename: str,
        content_type: str = "text/html",
    ) -> None:
        async with cls.get_client() as s3:
            await s3.put_object(
                Bucket=settings.s3.bucket_name,
                Key=filename,
                Body=file_bytes,
                ContentType=content_type,
                ContentDisposition="inline",
            )
