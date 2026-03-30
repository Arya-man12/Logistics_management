from typing import List

from fastapi import APIRouter, Depends, Response, status
from pydantic import BaseModel

from app.controllers.admin_controller import AdminController
from app.core.dependencies import get_admin_user
from app.schemas.hub_schema import HubCreate, HubResponse, HubUpdate
from app.schemas.shipment_schema import ShipmentResponse
from app.schemas.user_schema import UserResponse


class AssignAgentRequest(BaseModel):
    agent_id: str


router = APIRouter(prefix="/admin", tags=["Admin"])
admin_controller = AdminController()


@router.put("/shipments/{shipment_id}/assign-agent", response_model=ShipmentResponse)
def assign_agent(shipment_id: str, payload: AssignAgentRequest, current_user=Depends(get_admin_user)):
    return admin_controller.assign_agent(shipment_id, payload.agent_id)


@router.post("/hubs", response_model=HubResponse, status_code=status.HTTP_201_CREATED)
def create_hub(payload: HubCreate, current_user=Depends(get_admin_user)):
    return admin_controller.create_hub(payload)


@router.put("/hubs/{hub_id}", response_model=HubResponse)
def update_hub(hub_id: str, payload: HubUpdate, current_user=Depends(get_admin_user)):
    return admin_controller.update_hub(hub_id, payload)


@router.delete("/hubs/{hub_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_hub(hub_id: str, current_user=Depends(get_admin_user)):
    admin_controller.delete_hub(hub_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/reports")
def get_reports(current_user=Depends(get_admin_user)):
    return admin_controller.get_reports()


@router.get("/users", response_model=List[UserResponse])
def list_users(skip: int = 0, limit: int = 50, current_user=Depends(get_admin_user)):
    return admin_controller.list_users(skip=skip, limit=limit)


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: str, current_user=Depends(get_admin_user)):
    admin_controller.delete_user(user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
