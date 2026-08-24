from typing import Literal

from pydantic import AliasChoices, BaseModel, Field, HttpUrl, PositiveInt, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class GotenbergSettings(BaseModel):
    endpoint_url: HttpUrl
    width: PositiveInt = 1000
    format: Literal["png", "jpeg", "webp"] = "png"
    max_connections: PositiveInt = 5
    timeout: float = 10.0
    wait_delay: float = 8.0


class S3Settings(BaseModel):
    endpoint_url: HttpUrl = Field(
        default=HttpUrl("http://localhost:9000"),
        description="Адрес MinIO API",
    )
    access_key: SecretStr = Field(description="Логин MinIO")
    secret_key: SecretStr = Field(description="Пароль MinIO")
    bucket_name: str = Field(default="sites", description="Имя бакета")
    connect_timeout: PositiveInt = Field(
        default=5,
        description="Таймаут подключения в секундах",
    )
    read_timeout: PositiveInt = Field(
        default=10,
        description="Таймаут чтения в секундах",
    )
    max_connections: PositiveInt = Field(
        default=10,
        description="Лимит одновременных подключений",
    )


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        validate_default=True,
        extra="ignore",
        env_nested_delimiter="__",
    )

    debug: bool = False

    deepseek_api_key: SecretStr
    deepseek_base_url: HttpUrl = HttpUrl("https://api.deepseek.com/v1")
    deepseek_model: str = "deepseek-chat"
    deepseek_max_connections: PositiveInt | None = None
    deepseek_timeout: PositiveInt = 20

    unsplash_api_key: SecretStr | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "unsplash_api_key",
            "unsplash_client_id",
            "unsplash_client_key",
        ),
    )
    unsplash_max_connections: PositiveInt | None = None
    unsplash_timeout: PositiveInt = 20

    s3: S3Settings

    gotenberg: GotenbergSettings


if __name__ == "__main__":
    settings = AppSettings()
    print(settings.model_dump_json(indent=2))
