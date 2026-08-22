from pydantic import AliasChoices, Field, HttpUrl, PositiveInt, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        validate_default=True,
        extra="ignore",
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

    s3_endpoint_url: HttpUrl = HttpUrl("http://localhost:9000")
    s3_bucket_name: str = "sites"
    s3_access_key: str
    s3_secret_key: SecretStr


if __name__ == "__main__":
    settings = AppSettings()
    print(settings.model_dump_json(indent=2))
