from datetime import UTC, datetime

from pydantic import BaseModel, EmailStr, Field, HttpUrl


class UserSchema(BaseModel):
    id: str = "1"
    email: EmailStr = "example@example.com"
    username: str = "user123"


class SiteSchema(BaseModel):
    id: str
    name: str = "Сайт-визитка"
    html_url: HttpUrl
    download_url: HttpUrl
    screenshot_url: HttpUrl = Field(
        default="https://placehold.co/600x400?text=Site+Preview",
        description="Ссылка на скриншот сайта в S3",
    )


class NotFoundErrorSchema(BaseModel):
    detail: str = Field(
        default="Сайт не найден",
        description="Сообщение об ошибке, если ресурс отсутствует",
    )


class GenerateSitePayload(BaseModel):
    prompt: str = Field(
        default="Сайт-визитка для автосервиса с прайс-листом и формой записи",
        description="Промпт с описанием тематики сайта",
    )


class CreateSitePayload(BaseModel):
    prompt: str = Field(..., description="Промпт с описанием тематики сайта")
    title: str = Field(default="Новый сайт", description="Название сайта")


class CreatedSiteResponse(BaseModel):
    id: str = "1"
    title: str = "Новый сайт"
    prompt: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    html_url: HttpUrl
    download_url: HttpUrl
    screenshot_url: HttpUrl
