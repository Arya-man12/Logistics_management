from typing import Any, Dict, List, Optional

from app.schemas.hub_schema import HubCreate, HubResponse, HubUpdate
from app.schemas.shipment_schema import ShipmentResponse
from app.schemas.user_schema import UserResponse
from app.services.hub_service import HubService
from app.services.shipment_service import ShipmentService
from app.services.user_service import UserService


class AdminController:
    def __init__(
        self,
        shipment_service: Optional[ShipmentService] = None,
        hub_service: Optional[HubService] = None,
        user_service: Optional[UserService] = None,
    ):
        self.shipment_service = shipment_service or ShipmentService()
        self.hub_service = hub_service or HubService()
        self.user_service = user_service or UserService()

    def assign_agent(self, shipment_id: str, agent_id: str) -> ShipmentResponse:
        return ShipmentResponse(**self.shipment_service.assign_agent(shipment_id, agent_id))

    def list_hubs(self, skip: int = 0, limit: int = 50) -> List[HubResponse]:
        return [HubResponse(**hub) for hub in self.hub_service.list_hubs(skip=skip, limit=limit)]

    def create_hub(self, payload: HubCreate) -> HubResponse:
        return HubResponse(**self.hub_service.create_hub(payload))

    def update_hub(self, hub_id: str, payload: HubUpdate) -> HubResponse:
        return HubResponse(**self.hub_service.update_hub(hub_id, payload))

    def delete_hub(self, hub_id: str) -> None:
        self.hub_service.delete_hub(hub_id)

    def list_users(self, skip: int = 0, limit: int = 50) -> List[UserResponse]:
        return [UserResponse(**user) for user in self.user_service.list_users(skip=skip, limit=limit)]

    def delete_user(self, user_id: str) -> None:
        self.user_service.delete_user(user_id)

    def get_reports(self) -> Dict[str, Any]:
        shipments = self.shipment_service.repository.list_shipments(limit=1000)
        users = self.user_service.repository.list_users(limit=1000)
        hubs = self.hub_service.repository.list_hubs(limit=1000)
        by_status: Dict[str, int] = {}
        for shipment in shipments:
            status = shipment.get("status", "unknown")
            by_status[status] = by_status.get(status, 0) + 1
        return {
            "total_shipments": len(shipments),
            "total_users": len(users),
            "total_hubs": len(hubs),
            "shipments_by_status": by_status,
        }
