from typing import List

from fastapi import APIRouter, Depends, status

from app.controllers.tracking_controller import TrackingController
from app.core.dependencies import get_admin_user, get_agent_user, get_current_user
from app.schemas.tracking_schema import TrackingCreate, TrackingResponse, TrackingUpdate

router = APIRouter(prefix="/tracking", tags=["Tracking"])
tracking_controller = TrackingController()


@router.get("/", response_model=List[TrackingResponse])
def list_tracking(skip: int = 0, limit: int = 50, current_user=Depends(get_admin_user)):
    return tracking_controller.list_tracking(skip=skip, limit=limit)


@router.get("/{tracking_id}", response_model=TrackingResponse)
def get_tracking(tracking_id: str, current_user=Depends(get_current_user)):
    return tracking_controller.get_tracking(tracking_id)


@router.post("/", response_model=TrackingResponse, status_code=status.HTTP_201_CREATED)
def create_tracking(payload: TrackingCreate, current_user=Depends(get_agent_user)):
    return tracking_controller.create_tracking(payload)


@router.put("/{tracking_id}", response_model=TrackingResponse)
def update_tracking(tracking_id: str, payload: TrackingUpdate, current_user=Depends(get_agent_user)):
    return tracking_controller.update_tracking(tracking_id, payload)


@router.delete("/{tracking_id}", status_code=204)
def delete_tracking(tracking_id: str, current_user=Depends(get_admin_user)):
    tracking_controller.delete_tracking(tracking_id)
    return None


@router.get("/shipment/{shipment_id}", response_model=List[TrackingResponse])
def get_tracking_by_shipment(shipment_id: str, current_user=Depends(get_current_user)):
    return tracking_controller.get_tracking_by_shipment(shipment_id)
