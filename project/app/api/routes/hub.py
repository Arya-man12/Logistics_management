from typing import List

from fastapi import APIRouter, Depends, Response, status

from app.controllers.hub_controller import HubController
from app.core.dependencies import get_admin_user, get_current_user
from app.schemas.hub_schema import HubCreate, HubResponse, HubUpdate


router = APIRouter(prefix="/hubs", tags=["Hubs"])
hub_controller = HubController()


@router.get("", response_model=List[HubResponse])
def list_hubs(skip: int = 0, limit: int = 50, current_user=Depends(get_current_user)):
    return hub_controller.list_hubs(skip=skip, limit=limit)


@router.get("/{hub_id}", response_model=HubResponse)
def get_hub(hub_id: str, current_user=Depends(get_current_user)):
    return hub_controller.get_hub(hub_id)


@router.post("", response_model=HubResponse, status_code=status.HTTP_201_CREATED)
def create_hub(payload: HubCreate, current_user=Depends(get_admin_user)):
    return hub_controller.create_hub(payload)


@router.put("/{hub_id}", response_model=HubResponse)
def update_hub(hub_id: str, payload: HubUpdate, current_user=Depends(get_admin_user)):
    return hub_controller.update_hub(hub_id, payload)


@router.delete("/{hub_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_hub(hub_id: str, current_user=Depends(get_admin_user)):
    hub_controller.delete_hub(hub_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

