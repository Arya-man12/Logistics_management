from datetime import datetime
from typing import Any, Dict, List, Optional

from bson import ObjectId
from pymongo import MongoClient

from app.core.config import settings
from app.core.database import get_database
from app.utils.helpers import normalize_document


class UserRepository:
    def __init__(self, client: Optional[MongoClient] = None):
        self.client = client
        self.db = client[settings.mongo_db] if client is not None else get_database()
        self.collection = self.db["users"]

    def _serialize(self, document: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        return normalize_document(document)

    def list_users(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        cursor = self.collection.find().skip(skip).limit(limit)
        return [self._serialize(doc) for doc in cursor]

    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        if not ObjectId.is_valid(user_id):
            return None
        document = self.collection.find_one({"_id": ObjectId(user_id)})
        return self._serialize(document)

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        document = self.collection.find_one({"email": email})
        return self._serialize(document)

    def create_user(self, data: Dict[str, Any]) -> Dict[str, Any]:
        data["created_at"] = datetime.utcnow()
        data["updated_at"] = datetime.utcnow()
        result = self.collection.insert_one(data)
        return self.get_user_by_id(str(result.inserted_id))

    def update_user(self, user_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not ObjectId.is_valid(user_id):
            return None
        update_data = {k: v for k, v in update_data.items() if v is not None}
        if not update_data:
            return self.get_user_by_id(user_id)
        update_data["updated_at"] = datetime.utcnow()
        self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_data},
        )
        return self.get_user_by_id(user_id)

    def delete_user(self, user_id: str) -> bool:
        if not ObjectId.is_valid(user_id):
            return False
        result = self.collection.delete_one({"_id": ObjectId(user_id)})
        return result.deleted_count == 1
