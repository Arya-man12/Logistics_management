from typing import Any, Dict, Optional

from app.schemas.auth_schema import LoginRequest, RegisterRequest
from app.services.auth_service import AuthService


class AuthController:
    def __init__(self, service: Optional[AuthService] = None):
        self.service = service or AuthService()

    def register(self, payload: RegisterRequest) -> Dict[str, Any]:
        return self.service.register(payload)

    def login(self, payload: LoginRequest) -> Dict[str, Any]:
        return self.service.login(payload)

    def me(self, user_id: str) -> Dict[str, Any]:
        return self.service.get_profile(user_id)
