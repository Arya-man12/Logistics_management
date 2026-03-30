from datetime import datetime
from typing import Any, Dict, List, Optional

from bson import ObjectId

from app.core.database import get_database
from app.utils.helpers import normalize_document


class HubRepository:
    def __init__(self):
        self.db = get_database()
        self.collection = self.db["hubs"]

    def list_hubs(self, query: Optional[Dict[str, Any]] = None, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        cursor = self.collection.find(query or {}).sort("created_at", -1).skip(skip).limit(limit)
        return [normalize_document(doc) for doc in cursor]

    def get_hub_by_id(self, hub_id: str) -> Optional[Dict[str, Any]]:
        if not ObjectId.is_valid(hub_id):
            return None
        return normalize_document(self.collection.find_one({"_id": ObjectId(hub_id)}))

    def get_hub_by_code(self, code: str) -> Optional[Dict[str, Any]]:
        return normalize_document(self.collection.find_one({"code": code}))

    def create_hub(self, data: Dict[str, Any]) -> Dict[str, Any]:
        now = datetime.utcnow()
        data["created_at"] = now
        data["updated_at"] = now
        result = self.collection.insert_one(data)
        return self.get_hub_by_id(str(result.inserted_id))

    def update_hub(self, hub_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not ObjectId.is_valid(hub_id):
            return None
        update_data = {key: value for key, value in update_data.items() if value is not None}
        if not update_data:
            return self.get_hub_by_id(hub_id)
        update_data["updated_at"] = datetime.utcnow()
        self.collection.update_one({"_id": ObjectId(hub_id)}, {"$set": update_data})
        return self.get_hub_by_id(hub_id)

    def delete_hub(self, hub_id: str) -> bool:
        if not ObjectId.is_valid(hub_id):
            return False
        result = self.collection.delete_one({"_id": ObjectId(hub_id)})
        return result.deleted_count == 1
