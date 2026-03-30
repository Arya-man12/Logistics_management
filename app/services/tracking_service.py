from typing import Any, Dict, List, Optional

from app.exceptions.custom_exceptions import TrackingNotFoundException
from app.repositories.tracking_repository import TrackingRepository
from app.schemas.tracking_schema import TrackingCreate, TrackingUpdate


class TrackingService:
    def __init__(self, repository: Optional[TrackingRepository] = None):
        self.repository = repository or TrackingRepository()

    def list_tracking(self, skip: int = 0, limit: int = 50) -> List[Dict[str, Any]]:
        return self.repository.list_tracking(skip=skip, limit=limit)

    def get_tracking(self, tracking_id: str) -> Dict[str, Any]:
        tracking = self.repository.get_tracking_by_id(tracking_id)
        if not tracking:
            raise TrackingNotFoundException()
        return tracking

    def create_tracking(self, payload: TrackingCreate) -> Dict[str, Any]:
        return self.repository.create_tracking(payload.dict())

    def create_tracking_update(
        self,
        shipment_id: str,
        status: str,
        location: Optional[str] = None,
        note: Optional[str] = None,
        updated_by: Optional[str] = None,
    ) -> Dict[str, Any]:
        return self.repository.create_tracking(
            {
                "shipment_id": shipment_id,
                "location": location,
                "status": status,
                "note": note,
                "updated_by": updated_by,
            }
        )

    def update_tracking(self, tracking_id: str, payload: TrackingUpdate) -> Dict[str, Any]:
        tracking = self.repository.update_tracking(tracking_id, payload.dict(exclude_unset=True))
        if not tracking:
            raise TrackingNotFoundException()
        return tracking

    def delete_tracking(self, tracking_id: str) -> bool:
        deleted = self.repository.delete_tracking(tracking_id)
        if not deleted:
            raise TrackingNotFoundException()
        return deleted

    def get_tracking_by_shipment(self, shipment_id: str) -> List[Dict[str, Any]]:
        return self.repository.get_tracking_by_shipment(shipment_id)

    def get_tracking_by_agent(self, agent_id: str) -> List[Dict[str, Any]]:
        return self.repository.get_tracking_by_agent(agent_id)

    def get_tracking_by_hub(self, location: str) -> List[Dict[str, Any]]:
        return self.repository.get_tracking_by_hub(location)

    def get_tracking_by_status(self, status: str) -> List[Dict[str, Any]]:
        return self.repository.get_tracking_by_status(status)
