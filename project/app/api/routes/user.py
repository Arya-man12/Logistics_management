from typing import List

from fastapi import APIRouter, Depends, Response, status

from app.controllers.user_controller import UserController
from app.core.dependencies import get_admin_user, get_current_user
from app.schemas.user_schema import UserCreate, UserResponse, UserUpdate


router = APIRouter(prefix="/users", tags=["Users"])
user_controller = UserController()


@router.get("/", response_model=List[UserResponse])
def list_users(skip: int = 0, limit: int = 50, current_user=Depends(get_admin_user)):
    return user_controller.list_users(skip=skip, limit=limit)


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: str, current_user=Depends(get_current_user)):
    return user_controller.get_user(user_id)


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate):
    return user_controller.create_user(payload)


@router.patch("/{user_id}", response_model=UserResponse)
def update_user(user_id: str, payload: UserUpdate, current_user=Depends(get_current_user)):
    return user_controller.update_user(user_id, payload)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: str, current_user=Depends(get_admin_user)):
    user_controller.delete_user(user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

