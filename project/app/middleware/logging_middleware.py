import logging

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = logging.getLogger("app.middleware.logging")
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
        )
    )
    logger.addHandler(handler)
logger.setLevel(logging.INFO)


class LoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        client_ip = self._get_client_ip(request)
        logger.info(
            "Incoming request: %s %s from %s",
            request.method,
            request.url.path,
            client_ip,
        )

        try:
            response: Response = await call_next(request)
        except Exception as exc:  # pragma: no cover
            logger.exception(
                "Request failed: %s %s from %s", request.method, request.url.path, client_ip
            )
            raise

        logger.info(
            "Completed request: %s %s -> %s",
            request.method,
            request.url.path,
            response.status_code,
        )
        return response

    @staticmethod
    def _get_client_ip(request: Request) -> str:
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
        if request.client and request.client.host:
            return request.client.host
        return "unknown"
