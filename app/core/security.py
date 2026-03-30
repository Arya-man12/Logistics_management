import base64
import hashlib
import hmac
import json
import secrets
from datetime import timedelta
from typing import Any, Dict

from app.core.config import settings
from app.exceptions.custom_exceptions import AuthenticationException
from app.utils.helpers import utcnow


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    password_hash = hashlib.sha256(f"{salt}:{password}".encode("utf-8")).hexdigest()
    return f"{salt}${password_hash}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        salt, existing_hash = stored_hash.split("$", 1)
    except ValueError:
        return False
    candidate = hashlib.sha256(f"{salt}:{password}".encode("utf-8")).hexdigest()
    return hmac.compare_digest(candidate, existing_hash)


def _b64encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")


def _b64decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(f"{data}{padding}")


def create_access_token(data: Dict[str, Any], expires_delta: timedelta | None = None) -> str:
    expire = utcnow() + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
    payload = {**data, "exp": int(expire.timestamp())}
    header = {"alg": settings.algorithm, "typ": "JWT"}
    header_segment = _b64encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    payload_segment = _b64encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signing_input = f"{header_segment}.{payload_segment}"
    signature = hmac.new(
        settings.secret_key.encode("utf-8"),
        signing_input.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    return f"{signing_input}.{_b64encode(signature)}"


def decode_access_token(token: str) -> Dict[str, Any]:
    try:
        header_segment, payload_segment, signature_segment = token.split(".")
    except ValueError as exc:
        raise AuthenticationException("Invalid authentication token") from exc

    signing_input = f"{header_segment}.{payload_segment}"
    expected_signature = hmac.new(
        settings.secret_key.encode("utf-8"),
        signing_input.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    if not hmac.compare_digest(_b64encode(expected_signature), signature_segment):
        raise AuthenticationException("Invalid authentication token")

    payload = json.loads(_b64decode(payload_segment).decode("utf-8"))
    if payload.get("exp", 0) < int(utcnow().timestamp()):
        raise AuthenticationException("Authentication token expired")
    return payload
