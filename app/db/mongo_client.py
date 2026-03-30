from typing import Optional

from pymongo import MongoClient

try:
    from redis import Redis
    from redis.exceptions import RedisError
except ImportError:  # pragma: no cover
    Redis = None

    class RedisError(Exception):
        pass

from app.core.config import settings


_mongo_client: Optional[MongoClient] = None
_redis_client: Optional[Redis] = None


def get_mongo_client() -> MongoClient:
    global _mongo_client
    if _mongo_client is None:
        _mongo_client = MongoClient(settings.mongo_uri)
    return _mongo_client


def get_redis_client() -> Optional[Redis]:
    global _redis_client
    if Redis is None:
        return None
    if _redis_client is not None:
        return _redis_client

    try:
        client = Redis.from_url(settings.redis_url, decode_responses=True)
        client.ping()
        _redis_client = client
    except RedisError:
        _redis_client = None
    return _redis_client
