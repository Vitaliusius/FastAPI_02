from contextlib import AsyncExitStack, asynccontextmanager
from pathlib import Path

import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from html_page_generator import AsyncDeepseekClient, AsyncUnsplashClient

from src.env_settings import settings
from src.routes.sites import router as sites_router
from src.routes.users import router as users_router

BASE_DIR = Path(__file__).resolve().parent.parent
frontend_dir = BASE_DIR / "frontend"


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with AsyncExitStack() as stack:
        app.state.gotenberg_client = await stack.enter_async_context(
            httpx.AsyncClient(
                base_url=str(settings.gotenberg.endpoint_url),
                timeout=settings.gotenberg.timeout,
                limits=httpx.Limits(
                    max_connections=settings.gotenberg.max_connections,
                    max_keepalive_connections=settings.gotenberg.max_connections,
                ),
            )
        )

        unsplash_key = settings.unsplash.api_key.get_secret_value() if settings.unsplash.api_key else "Нет ключа"
        app.state.unsplash_client = await stack.enter_async_context(
            AsyncUnsplashClient.setup(
                unsplash_key,
                timeout=settings.unsplash.timeout,
            )
        )

        app.state.deepseek_client = await stack.enter_async_context(
            AsyncDeepseekClient.setup(
                settings.deepseek.api_key.get_secret_value(),
                str(settings.deepseek.base_url),
                settings.deepseek.model,
            )
        )

        yield


app = FastAPI(title="FastAI Site Generator", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users_router, prefix="/frontend-api")
app.include_router(sites_router, prefix="/frontend-api")

if frontend_dir.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")
