import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from bson import ObjectId
from pymongo import MongoClient


MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "logistics_db")


class TrackingRepository:
    def __init__(self, client: Optional[MongoClient] = None):
        self.client = client or MongoClient(MONGO_URI)
        self.db = self.client[MONGO_DB]
        self.collection = self.db["tracking_updates"]

    def _serialize(self, document: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if not document:
            return None
        document["id"] = str(document["_id"])
        document.pop("_id", None)
        return document

    def list_tracking(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        cursor = self.collection.find().skip(skip).limit(limit)
        return [self._serialize(doc) for doc in cursor]

    def get_tracking_by_id(self, tracking_id: str) -> Optional[Dict[str, Any]]:
        if not ObjectId.is_valid(tracking_id):
            return None
        document = self.collection.find_one({"_id": ObjectId(tracking_id)})
        return self._serialize(document)

    def create_tracking(self, data: Dict[str, Any]) -> Dict[str, Any]:
        data["updated_at"] = datetime.utcnow()
        result = self.collection.insert_one(data)
        return self.get_tracking_by_id(str(result.inserted_id))

    def update_tracking(self, tracking_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not ObjectId.is_valid(tracking_id):
            return None
        update_data = {k: v for k, v in update_data.items() if v is not None}
        if not update_data:
            return self.get_tracking_by_id(tracking_id)
        update_data["updated_at"] = datetime.utcnow()
        self.collection.update_one({"_id": ObjectId(tracking_id)}, {"$set": update_data})
        return self.get_tracking_by_id(tracking_id)

    def delete_tracking(self, tracking_id: str) -> bool:
        if not ObjectId.is_valid(tracking_id):
            return False
        result = self.collection.delete_one({"_id": ObjectId(tracking_id)})
        return result.deleted_count == 1

    def get_tracking_by_shipment(self, shipment_id: str) -> List[Dict[str, Any]]:
        query = {"shipment_id": shipment_id}
        cursor = self.collection.find(query)
        return [self._serialize(doc) for doc in cursor]

    def get_tracking_by_agent(self, agent_id: str) -> List[Dict[str, Any]]:
        query = {"updated_by": agent_id}
        cursor = self.collection.find(query)
        return [self._serialize(doc) for doc in cursor]

    def get_tracking_by_hub(self, location: str) -> List[Dict[str, Any]]:
        query = {"location": location}
        cursor = self.collection.find(query)
        return [self._serialize(doc) for doc in cursor]

    def get_tracking_by_status(self, status: str) -> List[Dict[str, Any]]:
        query = {"status": status}
        cursor = self.collection.find(query)
        return [self._serialize(doc) for doc in cursor]
