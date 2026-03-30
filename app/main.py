from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings
from app.exceptions.custom_exceptions import AppException
from app.exceptions.exception_handlers import app_exception_handler

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

app.add_exception_handler(AppException, app_exception_handler)
app.include_router(api_router, prefix=settings.api_prefix)


@app.get("/", tags=["Health"])
def root() -> dict:
    return {"status": "ok", "message": "Logistics API is running"}
