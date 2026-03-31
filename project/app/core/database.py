from typing import Any

from pymongo.database import Database

from app.core.config import settings
from app.db.mongo_client import get_mongo_client, get_redis_client


def get_database() -> Database:
    return get_mongo_client()[settings.mongo_db]


def get_redis() -> Any:
    return get_redis_client()

