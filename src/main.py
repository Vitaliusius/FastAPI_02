import asyncio
from datetime import datetime
from typing import Annotated

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, EmailStr, StringConstraints

app = FastAPI()

SiteTitle = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]
UsernameStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=254)]


class UserDetailsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    profileId: int
    email: EmailStr
    username: UsernameStr
    isActive: bool
    registeredAt: datetime
    updatedAt: datetime


class CreateSiteRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: SiteTitle | None = None
    prompt: str


class SiteGenerationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    prompt: str


class SiteResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: int
    title: str
    prompt: str
    createdAt: datetime
    updatedAt: datetime
    htmlCodeUrl: str | None = None
    htmlCodeDownloadUrl: str | None = None
    screenshotUrl: str | None = None


class GeneratedSitesResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sites: list[SiteResponse]


MOCK_HTML_CODE = """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Кофейня Аромат | Свежеобжаренный кофе</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        .hero-bg {
            background-image: linear-gradient(rgba(0, 0, 0, 0.6), rgba(0, 0, 0, 0.6)), url('https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?ixlib=rb-4.0.3&auto=format&fit=crop&w=1920&q=80');
            background-size: cover;
            background-position: center;
        }
    </style>
</head>
<body class="font-sans antialiased text-gray-800 bg-amber-50">
    <!-- Header / Navbar -->
    <header class="fixed w-full bg-amber-950/90 text-amber-100 backdrop-blur-sm z-50 transition duration-300">
        <div class="container mx-auto px-6 py-4 flex justify-between items-center">
            <a href="#" class="text-2xl font-serif font-bold tracking-wider text-amber-400 flex items-center gap-2">
                <i class="fa-solid fa-mug-hot"></i> АРОМАТ
            </a>
            <nav class="hidden md:flex space-x-8 text-sm font-medium">
                <a href="#about" class="hover:text-amber-400 transition">О нас</a>
                <a href="#menu" class="hover:text-amber-400 transition">Меню</a>
                <a href="#atmosphere" class="hover:text-amber-400 transition">Атмосфера</a>
                <a href="#contact" class="hover:text-amber-400 transition">Контакты</a>
            </nav>
            <a href="#contact" class="hidden md:inline-block bg-amber-600 hover:bg-amber-700 text-white px-5 py-2 rounded-full font-medium transition shadow-lg hover:shadow-none">
                Забронировать
            </a>
        </div>
    </header>

    <!-- Hero Section -->
    <section class="hero-bg min-h-screen flex items-center justify-center text-center text-white px-4">
        <div class="max-w-3xl space-y-6 pt-20">
            <span class="text-amber-400 font-semibold tracking-widest uppercase text-sm block mb-2">Искусство настоящего кофе</span>
            <h1 class="text-4xl md:text-6xl font-serif font-bold leading-tight">Место, где рождается идеальное утро</h1>
            <p class="text-lg md:text-xl text-gray-200 font-light max-w-2xl mx-auto">
                Авторские напитки из 100% арабики свежей обжарки, свежая выпечка и уютная атмосфера в самом центре города.
            </p>
            <div class="flex flex-col sm:flex-row justify-center gap-4 pt-4">
                <a href="#menu" class="bg-amber-600 hover:bg-amber-700 text-white px-8 py-3.5 rounded-full font-medium transition text-lg shadow-lg">
                    Посмотреть меню
                </a>
                <a href="#about" class="bg-white/20 hover:bg-white/30 backdrop-blur text-white px-8 py-3.5 rounded-full font-medium transition text-lg border border-white/40">
                    Узнать больше
                </a>
            </div>
        </div>
    </section>

    <!-- Footer -->
    <footer class="bg-amber-950 text-amber-200/60 py-8 border-t border-amber-900">
        <div class="container mx-auto px-6 text-center text-sm">
            <p>&copy; 2025 Кофейня «Аромат». Все права защищены.</p>
        </div>
    </footer>
</body>
</html>
"""  # noqa: E501

MOCK_SITE = SiteResponse(
    id=1,
    title="Фан клуб Домино",
    prompt="Сайт любителей играть в домино",
    createdAt=datetime.fromisoformat("2025-06-15T18:29:56+00:00"),
    updatedAt=datetime.fromisoformat("2025-06-15T18:29:56+00:00"),
    htmlCodeUrl="https://dvmn.org/media/filer_public/d1/4b/d14bb4e8-d8b4-49cb-928d-fd04ecae46da/index.html",
    htmlCodeDownloadUrl="https://dvmn.org/media/filer_public/d1/4b/d14bb4e8-d8b4-49cb-928d-fd04ecae46da/index.html",
    screenshotUrl="https://google.com",
)


@app.get("/frontend-api/users/me", response_model=UserDetailsResponse)
def get_user_me() -> UserDetailsResponse:
    return UserDetailsResponse(
        email="example@example.com",
        isActive=True,
        profileId=1,
        registeredAt=datetime.fromisoformat("2025-06-15T18:29:56+00:00"),
        updatedAt=datetime.fromisoformat("2025-06-15T18:29:56+00:00"),
        username="user123",
    )


@app.get("/frontend-api/sites/my", response_model=GeneratedSitesResponse)
def get_my_sites() -> GeneratedSitesResponse:
    return GeneratedSitesResponse(sites=[MOCK_SITE])


@app.post("/frontend-api/sites/create", response_model=SiteResponse)
def create_site(data: CreateSiteRequest) -> SiteResponse:
    return MOCK_SITE


async def html_streamer():
    for line in MOCK_HTML_CODE.splitlines(keepends=True):
        yield line
        await asyncio.sleep(0.02)


@app.post("/frontend-api/sites/{site_id}/generate")
async def generate_site_html(site_id: int, data: SiteGenerationRequest):
    return StreamingResponse(html_streamer(), media_type="text/plain")


@app.get("/frontend-api/sites/{site_id}", response_model=SiteResponse)
def get_site_by_id(site_id: int) -> SiteResponse:
    return MOCK_SITE


app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
