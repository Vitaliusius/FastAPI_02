import asyncio
from pathlib import Path

import aioboto3

from src.env_settings import AppSettings

settings = AppSettings()
LOCAL_FILE = Path("sites/index.html")


async def upload_existing_file():
    if not LOCAL_FILE.exists():
        print(f"[Ошибка]: Файл {LOCAL_FILE} не найден.")
        return

    content = LOCAL_FILE.read_bytes()

    session = aioboto3.Session()
    async with session.client(
        "s3",
        endpoint_url=str(settings.s3_endpoint_url),
        aws_access_key_id=settings.s3_access_key,
        aws_secret_access_key=settings.s3_secret_key.get_secret_value(),
    ) as s3:
        await s3.put_object(
            Bucket=settings.s3_bucket_name,
            Key="index.html",
            Body=content,
            ContentType="text/html",
            ContentDisposition="inline",
        )
        print(f"Файл загружен в бакет '{settings.s3_bucket_name}'!")

        base_url = f"{settings.s3_endpoint_url}{settings.s3_bucket_name}/index.html"
        print(f"Просмотр: {base_url}")
        print(f"Скачивание: {base_url}?response-content-disposition=attachment")


if __name__ == "__main__":
    asyncio.run(upload_existing_file())
