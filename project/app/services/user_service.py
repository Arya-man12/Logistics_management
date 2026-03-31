from typing import Any, Dict, List, Optional

from app.core.security import hash_password
from app.exceptions.custom_exceptions import (
    UserAlreadyExistsException,
    UserCreateException,
    UserNotFoundException,
    UserUpdateException,
)
from app.repositories.user_repository import UserRepository
from app.schemas.user_schema import UserCreate, UserUpdate


class UserService:
    def __init__(self, repository: Optional[UserRepository] = None):
        self.repository = repository or UserRepository()

    @staticmethod
    def _sanitize_user(user: Dict[str, Any]) -> Dict[str, Any]:
        sanitized = dict(user)
        sanitized.pop("hashed_password", None)
        return sanitized

    def list_users(self, skip: int = 0, limit: int = 50) -> List[Dict[str, Any]]:
        return [self._sanitize_user(user) for user in self.repository.list_users(skip=skip, limit=limit)]

    def get_user(self, user_id: str) -> Dict[str, Any]:
        user = self.repository.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundException()
        return self._sanitize_user(user)

    def create_user(self, payload: UserCreate) -> Dict[str, Any]:
        existing = self.repository.get_user_by_email(payload.email)
        if existing:
            raise UserAlreadyExistsException()

        user_data = payload.model_dump()
        user_data["hashed_password"] = hash_password(user_data.pop("password"))
        try:
            created = self.repository.create_user(user_data)
            return self._sanitize_user(created)
        except Exception as exc:
            raise UserCreateException() from exc

    def update_user(self, user_id: str, payload: UserUpdate) -> Dict[str, Any]:
        existing = self.repository.get_user_by_id(user_id)
        if not existing:
            raise UserNotFoundException()

        update_data = payload.model_dump(exclude_unset=True)
        updated = self.repository.update_user(user_id, update_data)
        if not updated:
            raise UserUpdateException()
        return self._sanitize_user(updated)

    def delete_user(self, user_id: str) -> bool:
        existing = self.repository.get_user_by_id(user_id)
        if not existing:
            raise UserNotFoundException()
        deleted = self.repository.delete_user(user_id)
        if not deleted:
            raise UserNotFoundException()
        return True

