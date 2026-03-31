from fastapi import APIRouter, Depends, status

from app.controllers.auth_controller import AuthController
from app.core.dependencies import get_current_user
from app.schemas.auth_schema import AuthResponse, LoginRequest, RegisterRequest


router = APIRouter(prefix="/auth", tags=["Auth"])
auth_controller = AuthController()


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest):
    return auth_controller.register(payload)


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest):
    return auth_controller.login(payload)


@router.get("/me")
def me(current_user=Depends(get_current_user)):
    return auth_controller.me(current_user["id"])

