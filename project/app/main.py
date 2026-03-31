from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.router import api_router
from app.core.config import settings
from app.exceptions.custom_exceptions import AppException
from app.exceptions.exception_handlers import app_exception_handler
from app.middleware.logging_middleware import LoggingMiddleware
from app.middleware.rate_limiter import RateLimiterMiddleware

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=settings.app_description,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(LoggingMiddleware)
app.add_middleware(RateLimiterMiddleware)

app.add_exception_handler(AppException, app_exception_handler)
app.include_router(api_router, prefix=settings.api_prefix)

frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
frontend_dist_dir = frontend_dir / "dist"

if frontend_dist_dir.exists():
    assets_dir = frontend_dist_dir / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")


@app.get("/health", tags=["Health"])
def health() -> dict:
    return {"status": "ok", "message": "Logistics API is running"}


@app.get("/", include_in_schema=False)
def root() -> FileResponse:
    return FileResponse(frontend_dist_dir / "index.html")

