import asyncio
from aioboto3 import Session
from src.env_settings import AppSettings

SAMPLE_PNG = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00"
    b"\x1f\x15c4\x00\x00\x00\rIDATx\x9cc`\x00\x00\x00\x02\x00\x01H\xaf\xa4q\x00\x00\x00\x00IEND\xaeB`\x82"
)


async def main():
    settings = AppSettings()
    session = Session()
    async with session.client(
        "s3",
        endpoint_url=str(settings.s3.endpoint_url),
        aws_access_key_id=settings.s3.access_key.get_secret_value(),
        aws_secret_access_key=settings.s3.secret_key.get_secret_value(),
    ) as s3:
        await s3.put_object(
            Bucket=settings.s3.bucket_name,
            Key="index.png",
            Body=SAMPLE_PNG,
            ContentType="image/png",
            ContentDisposition="inline",
        )
        print("Файл index.png успешно загружен!")


if __name__ == "__main__":
    asyncio.run(main())
