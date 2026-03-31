from typing import List, Optional

from fastapi import APIRouter, Depends, Query, Response, status
from pydantic import BaseModel

from app.controllers.shipment_controller import ShipmentController
from app.core.dependencies import get_agent_user, get_current_user, get_customer_user
from app.schemas.shipment_schema import ShipmentCreate, ShipmentResponse, ShipmentUpdate


class ShipmentStatusUpdateRequest(BaseModel):
    status: str
    location: Optional[str] = None
    note: Optional[str] = None


router = APIRouter(prefix="/shipments", tags=["Shipments"])
shipment_controller = ShipmentController()


@router.post("", response_model=ShipmentResponse, status_code=status.HTTP_201_CREATED)
def create_shipment(payload: ShipmentCreate, current_user=Depends(get_customer_user)):
    return shipment_controller.create_shipment(payload, current_user["id"])


@router.get("", response_model=List[ShipmentResponse])
def list_shipments(
    skip: int = 0,
    limit: int = Query(default=50, le=100),
    current_user=Depends(get_current_user),
):
    return shipment_controller.list_shipments(current_user, skip=skip, limit=limit)


@router.get("/{tracking_number}", response_model=ShipmentResponse)
def get_shipment_by_tracking(tracking_number: str, current_user=Depends(get_current_user)):
    return shipment_controller.get_shipment_by_tracking(tracking_number, current_user=current_user)


@router.patch("/{shipment_id}", response_model=ShipmentResponse)
def update_shipment(shipment_id: str, payload: ShipmentUpdate, current_user=Depends(get_current_user)):
    return shipment_controller.update_shipment(shipment_id, payload, current_user)


@router.delete("/{shipment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_shipment(shipment_id: str, current_user=Depends(get_current_user)):
    shipment_controller.delete_shipment(shipment_id, current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{shipment_id}/status", response_model=ShipmentResponse)
def update_status(
    shipment_id: str,
    payload: ShipmentStatusUpdateRequest,
    current_user=Depends(get_agent_user),
):
    return shipment_controller.update_status(
        shipment_id=shipment_id,
        status=payload.status,
        agent_id=current_user["id"],
        location=payload.location,
        note=payload.note,
    )

