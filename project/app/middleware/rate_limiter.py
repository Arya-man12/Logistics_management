import logging
import os
import threading
import time
from collections import deque
from typing import Deque, Dict, Optional, Tuple

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.db.mongo_client import get_redis_client

logger = logging.getLogger("app.middleware.rate_limiter")
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
        )
    )
    logger.addHandler(handler)
logger.setLevel(logging.INFO)

DEFAULT_MAX_REQUESTS = int(os.getenv("RATE_LIMIT_MAX_REQUESTS", "100"))
DEFAULT_WINDOW_SECONDS = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"))


class RateLimiterMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: ASGIApp,
        max_requests: int = DEFAULT_MAX_REQUESTS,
        window_seconds: int = DEFAULT_WINDOW_SECONDS,
    ) -> None:
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.redis_client = get_redis_client()
        self._local_store: Dict[str, Deque[float]] = {}
        self._lock = threading.Lock()

    async def dispatch(self, request: Request, call_next):
        client_ip = self._get_client_ip(request)
        if not client_ip:
            return await call_next(request)

        try:
            allowed, remaining = self._check_limit(client_ip)
        except Exception as exc:
            logger.warning(
                "Rate limiter failed, allowing request: %s",
                exc,
                exc_info=True,
            )
            return await call_next(request)

        headers = {
            "X-RateLimit-Limit": str(self.max_requests),
            "X-RateLimit-Remaining": str(max(remaining, 0)),
        }

        if not allowed:
            retry_after = self._get_retry_after(client_ip)
            return JSONResponse(
                {"detail": "Too Many Requests"},
                status_code=429,
                headers={
                    **headers,
                    "Retry-After": str(retry_after),
                },
            )

        response = await call_next(request)
        response.headers.update(headers)
        return response

    def _get_client_ip(self, request: Request) -> str:
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
        if request.client and request.client.host:
            return request.client.host
        return "unknown"

    def _check_limit(self, client_ip: str) -> Tuple[bool, int]:
        if self.redis_client is not None:
            return self._check_redis(client_ip)
        return self._check_local(client_ip)

    def _check_redis(self, client_ip: str) -> Tuple[bool, int]:
        key = f"rate_limit:{client_ip}"
        count = self.redis_client.incr(key)
        if count == 1:
            self.redis_client.expire(key, self.window_seconds)

        remaining = self.max_requests - count
        return count <= self.max_requests, remaining

    def _check_local(self, client_ip: str) -> Tuple[bool, int]:
        now = time.time()
        with self._lock:
            window = self._local_store.setdefault(client_ip, deque())
            cutoff = now - self.window_seconds
            while window and window[0] <= cutoff:
                window.popleft()
            window.append(now)
            remaining = self.max_requests - len(window)
            return len(window) <= self.max_requests, remaining

    def _get_retry_after(self, client_ip: str) -> int:
        if self.redis_client is not None:
            ttl = self.redis_client.ttl(f"rate_limit:{client_ip}")
            if ttl and ttl > 0:
                return ttl
            return self.window_seconds

        with self._lock:
            window = self._local_store.get(client_ip)
            if not window:
                return self.window_seconds
            retry_after = self.window_seconds - int(time.time() - window[0])
            return max(retry_after, 0)

