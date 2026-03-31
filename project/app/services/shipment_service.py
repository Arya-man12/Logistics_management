from typing import Any, Dict, List, Optional

from app.core.database import get_redis
from app.exceptions.custom_exceptions import AuthorizationException, ShipmentNotFoundException
from app.repositories.shipment_repository import ShipmentRepository
from app.schemas.shipment_schema import ShipmentCreate, ShipmentUpdate
from app.services.tracking_service import TrackingService
from app.utils.helpers import generate_tracking_number
from app.utils.validators import validate_payment_status, validate_shipment_status


class ShipmentService:
    def __init__(
        self,
        repository: Optional[ShipmentRepository] = None,
        tracking_service: Optional[TrackingService] = None,
    ):
        self.repository = repository or ShipmentRepository()
        self.tracking_service = tracking_service or TrackingService()
        self.redis = get_redis()

    def _cache_status(self, shipment: Optional[Dict[str, Any]]) -> None:
        if not shipment or not self.redis:
            return
        self.redis.hset(
            f"shipment:{shipment['tracking_number']}",
            mapping={
                "status": shipment["status"],
                "shipment_id": shipment["id"],
                "assigned_agent_id": shipment.get("assigned_agent_id", "") or "",
            },
        )

    def list_shipments(self, current_user: Dict[str, Any], skip: int = 0, limit: int = 50) -> List[Dict[str, Any]]:
        query: Dict[str, Any] = {}
        if current_user["role"] == "customer":
            query["customer_id"] = current_user["id"]
        elif current_user["role"] == "agent":
            query["assigned_agent_id"] = current_user["id"]

        shipments = self.repository.list_shipments(query=query, skip=skip, limit=limit)
        for shipment in shipments:
            self._cache_status(shipment)
        return shipments

    def get_shipment(self, shipment_id: str) -> Dict[str, Any]:
        shipment = self.repository.get_shipment_by_id(shipment_id)
        if not shipment:
            raise ShipmentNotFoundException()
        self._cache_status(shipment)
        return shipment

    def get_shipment_by_tracking(self, tracking_number: str, current_user: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        shipment = self.repository.get_by_tracking_number(tracking_number)
        if not shipment:
            raise ShipmentNotFoundException()
        if current_user and current_user["role"] == "customer" and shipment["customer_id"] != current_user["id"]:
            raise AuthorizationException()
        if current_user and current_user["role"] == "agent" and shipment.get("assigned_agent_id") != current_user["id"]:
            raise AuthorizationException()
        self._cache_status(shipment)
        return shipment

    def create_shipment(self, payload: ShipmentCreate, customer_id: str) -> Dict[str, Any]:
        shipment_data = payload.model_dump()
        shipment_data["customer_id"] = customer_id
        shipment_data["tracking_number"] = generate_tracking_number()
        shipment_data["status"] = "created"
        shipment_data["assigned_agent_id"] = None
        shipment = self.repository.create_shipment(shipment_data)
        self.tracking_service.create_tracking_update(
            shipment_id=shipment["id"],
            status="created",
            location=shipment.get("source_address"),
            note="Shipment created",
            updated_by=customer_id,
        )
        self._cache_status(shipment)
        return shipment

    def update_shipment(self, shipment_id: str, payload: ShipmentUpdate, current_user: Dict[str, Any]) -> Dict[str, Any]:
        shipment = self.repository.get_shipment_by_id(shipment_id)
        if not shipment:
            raise ShipmentNotFoundException()
        if current_user["role"] == "customer" and shipment["customer_id"] != current_user["id"]:
            raise AuthorizationException()

        update_data = payload.model_dump(exclude_unset=True)
        if "status" in update_data:
            validate_shipment_status(update_data["status"])
        if "payment_status" in update_data:
            validate_payment_status(update_data["payment_status"])
        updated = self.repository.update_shipment(shipment_id, update_data)
        self._cache_status(updated)
        return updated

    def delete_shipment(self, shipment_id: str, current_user: Dict[str, Any]) -> bool:
        shipment = self.repository.get_shipment_by_id(shipment_id)
        if not shipment:
            raise ShipmentNotFoundException()
        if current_user["role"] != "admin" and shipment["customer_id"] != current_user["id"]:
            raise AuthorizationException()
        return self.repository.delete_shipment(shipment_id)

    def assign_agent(self, shipment_id: str, agent_id: str) -> Dict[str, Any]:
        shipment = self.repository.get_shipment_by_id(shipment_id)
        if not shipment:
            raise ShipmentNotFoundException()
        updated = self.repository.update_shipment(
            shipment_id,
            {"assigned_agent_id": agent_id, "status": "assigned"},
        )
        self.tracking_service.create_tracking_update(
            shipment_id=shipment_id,
            status="assigned",
            location=shipment.get("source_address"),
            note=f"Shipment assigned to agent {agent_id}",
            updated_by=agent_id,
        )
        self._cache_status(updated)
        return updated

    def update_status(
        self,
        shipment_id: str,
        status: str,
        agent_id: str,
        location: Optional[str] = None,
        note: Optional[str] = None,
    ) -> Dict[str, Any]:
        validate_shipment_status(status)
        shipment = self.repository.get_shipment_by_id(shipment_id)
        if not shipment:
            raise ShipmentNotFoundException()
        if shipment.get("assigned_agent_id") != agent_id:
            raise AuthorizationException("Shipment is not assigned to this agent")
        updated = self.repository.update_shipment(shipment_id, {"status": status})
        self.tracking_service.create_tracking_update(
            shipment_id=shipment_id,
            status=status,
            location=location,
            note=note,
            updated_by=agent_id,
        )
        self._cache_status(updated)
        return updated

