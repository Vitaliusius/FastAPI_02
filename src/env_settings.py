from functools import lru_cache
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


class DeepseekSettings(BaseModel):
    api_key: SecretStr
    base_url: HttpUrl = HttpUrl("https://api.deepseek.com/v1")
    model: str = "deepseek-chat"
    max_connections: PositiveInt | None = None
    timeout: PositiveInt = 20


class UnsplashSettings(BaseModel):
    api_key: SecretStr | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "api_key",
            "client_id",
            "client_key",
        ),
    )
    max_connections: PositiveInt | None = None
    timeout: PositiveInt = 20


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

    deepseek: DeepseekSettings
    unsplash: UnsplashSettings
    s3: S3Settings
    gotenberg: GotenbergSettings


@lru_cache
def get_settings() -> AppSettings:
    return AppSettings()


settings = get_settings()
