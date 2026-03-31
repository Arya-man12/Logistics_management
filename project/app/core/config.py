import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "Logistics Shipment Tracking API")
    app_version: str = os.getenv("APP_VERSION", "1.0.0")
    app_description: str = os.getenv(
        "APP_DESCRIPTION",
        "Backend API for shipment creation, assignment, tracking, and hub management.",
    )
    api_prefix: str = os.getenv("API_PREFIX", "/api")
    mongo_uri: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    mongo_db: str = os.getenv("MONGO_DB", "logistics_db")
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    secret_key: str = os.getenv("SECRET_KEY", "change-me-in-production")
    access_token_expire_minutes: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
    )
    algorithm: str = "HS256"
    cors_origins: list[str] = None

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "cors_origins",
            [origin.strip() for origin in os.getenv("CORS_ORIGINS", "*").split(",")],
        )


settings = Settings()
