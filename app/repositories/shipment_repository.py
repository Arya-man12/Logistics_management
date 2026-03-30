from datetime import datetime
from typing import Any, Dict, List, Optional

from bson import ObjectId

from app.core.database import get_database
from app.utils.helpers import normalize_document


class ShipmentRepository:
    def __init__(self):
        self.db = get_database()
        self.collection = self.db["shipments"]

    def list_shipments(self, query: Optional[Dict[str, Any]] = None, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        cursor = self.collection.find(query or {}).sort("created_at", -1).skip(skip).limit(limit)
        return [normalize_document(doc) for doc in cursor]

    def get_shipment_by_id(self, shipment_id: str) -> Optional[Dict[str, Any]]:
        if not ObjectId.is_valid(shipment_id):
            return None
        return normalize_document(self.collection.find_one({"_id": ObjectId(shipment_id)}))

    def get_by_tracking_number(self, tracking_number: str) -> Optional[Dict[str, Any]]:
        return normalize_document(self.collection.find_one({"tracking_number": tracking_number}))

    def create_shipment(self, data: Dict[str, Any]) -> Dict[str, Any]:
        now = datetime.utcnow()
        data["created_at"] = now
        data["updated_at"] = now
        result = self.collection.insert_one(data)
        return self.get_shipment_by_id(str(result.inserted_id))

    def update_shipment(self, shipment_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not ObjectId.is_valid(shipment_id):
            return None
        update_data = {key: value for key, value in update_data.items() if value is not None}
        if not update_data:
            return self.get_shipment_by_id(shipment_id)
        update_data["updated_at"] = datetime.utcnow()
        self.collection.update_one({"_id": ObjectId(shipment_id)}, {"$set": update_data})
        return self.get_shipment_by_id(shipment_id)

    def delete_shipment(self, shipment_id: str) -> bool:
        if not ObjectId.is_valid(shipment_id):
            return False
        result = self.collection.delete_one({"_id": ObjectId(shipment_id)})
        return result.deleted_count == 1
