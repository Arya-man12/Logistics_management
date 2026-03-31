from typing import Any, Dict, List, Optional

from app.schemas.shipment_schema import ShipmentCreate, ShipmentResponse, ShipmentUpdate
from app.services.shipment_service import ShipmentService


class ShipmentController:
    def __init__(self, service: Optional[ShipmentService] = None):
        self.service = service or ShipmentService()

    def list_shipments(self, current_user: Dict[str, Any], skip: int = 0, limit: int = 50) -> List[ShipmentResponse]:
        shipments = self.service.list_shipments(current_user=current_user, skip=skip, limit=limit)
        return [ShipmentResponse(**shipment) for shipment in shipments]

    def get_shipment(self, shipment_id: str) -> ShipmentResponse:
        shipment = self.service.get_shipment(shipment_id)
        return ShipmentResponse(**shipment)

    def get_shipment_by_tracking(self, tracking_number: str, current_user: Optional[Dict[str, Any]] = None) -> ShipmentResponse:
        shipment = self.service.get_shipment_by_tracking(tracking_number, current_user=current_user)
        return ShipmentResponse(**shipment)

    def create_shipment(self, payload: ShipmentCreate, customer_id: str) -> ShipmentResponse:
        shipment = self.service.create_shipment(payload, customer_id)
        return ShipmentResponse(**shipment)

    def update_shipment(self, shipment_id: str, payload: ShipmentUpdate, current_user: Dict[str, Any]) -> ShipmentResponse:
        shipment = self.service.update_shipment(shipment_id, payload, current_user)
        return ShipmentResponse(**shipment)

    def delete_shipment(self, shipment_id: str, current_user: Dict[str, Any]) -> None:
        self.service.delete_shipment(shipment_id, current_user)

    def assign_agent(self, shipment_id: str, agent_id: str) -> ShipmentResponse:
        shipment = self.service.assign_agent(shipment_id, agent_id)
        return ShipmentResponse(**shipment)

    def update_status(
        self,
        shipment_id: str,
        status: str,
        agent_id: str,
        location: Optional[str] = None,
        note: Optional[str] = None,
    ) -> ShipmentResponse:
        shipment = self.service.update_status(shipment_id, status, agent_id, location, note)
        return ShipmentResponse(**shipment)

