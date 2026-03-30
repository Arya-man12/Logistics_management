from typing import Any, Dict, Optional

from app.core.security import create_access_token, hash_password, verify_password
from app.exceptions.custom_exceptions import AuthenticationException, UserAlreadyExistsException
from app.repositories.user_repository import UserRepository
from app.schemas.auth_schema import LoginRequest, RegisterRequest
from app.utils.validators import validate_role


class AuthService:
    def __init__(self, repository: Optional[UserRepository] = None):
        self.repository = repository or UserRepository()

    @staticmethod
    def _sanitize_user(user: Dict[str, Any]) -> Dict[str, Any]:
        sanitized = dict(user)
        sanitized.pop("hashed_password", None)
        return sanitized

    def register(self, payload: RegisterRequest) -> Dict[str, Any]:
        if self.repository.get_user_by_email(payload.email):
            raise UserAlreadyExistsException()

        user_data = payload.dict()
        user_data["role"] = validate_role(user_data["role"])
        user_data["hashed_password"] = hash_password(user_data.pop("password"))
        created_user = self.repository.create_user(user_data)
        token = create_access_token({"sub": created_user["id"], "role": created_user["role"]})
        return {"access_token": token, "token_type": "bearer", "user": self._sanitize_user(created_user)}

    def login(self, payload: LoginRequest) -> Dict[str, Any]:
        user = self.repository.get_user_by_email(payload.email)
        if not user or not verify_password(payload.password, user.get("hashed_password", "")):
            raise AuthenticationException("Invalid email or password")
        if not user.get("is_active", True):
            raise AuthenticationException("User account is inactive")
        token = create_access_token({"sub": user["id"], "role": user["role"]})
        return {"access_token": token, "token_type": "bearer", "user": self._sanitize_user(user)}

    def get_profile(self, user_id: str) -> Dict[str, Any]:
        user = self.repository.get_user_by_id(user_id)
        if not user:
            raise AuthenticationException("User not found")
        return self._sanitize_user(user)
