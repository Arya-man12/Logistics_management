from datetime import datetime, timezone
from typing import Any, Dict, Optional
from uuid import uuid4

from bson import ObjectId


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def generate_tracking_number() -> str:
    return f"TRK{uuid4().hex[:10].upper()}"


def normalize_document(document: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if not document:
        return None

    normalized = dict(document)
    object_id = normalized.pop("_id", None)
    if object_id is not None:
        normalized["id"] = str(object_id)
    for key, value in normalized.items():
        if isinstance(value, ObjectId):
            normalized[key] = str(value)
    return normalized
