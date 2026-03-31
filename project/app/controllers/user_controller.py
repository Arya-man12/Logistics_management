from typing import List

from app.schemas.user_schema import UserCreate, UserResponse, UserUpdate
from app.services.user_service import UserService


class UserController:
    def __init__(self, service: UserService = None):
        self.service = service or UserService()

    def list_users(self, skip: int = 0, limit: int = 50) -> List[UserResponse]:
        users = self.service.list_users(skip=skip, limit=limit)
        return [UserResponse(**user) for user in users]

    def get_user(self, user_id: str) -> UserResponse:
        user = self.service.get_user(user_id)
        return UserResponse(**user)

    def create_user(self, payload: UserCreate) -> UserResponse:
        created_user = self.service.create_user(payload)
        return UserResponse(**created_user)

    def update_user(self, user_id: str, payload: UserUpdate) -> UserResponse:
        updated_user = self.service.update_user(user_id, payload)
        return UserResponse(**updated_user)

    def delete_user(self, user_id: str) -> None:
        self.service.delete_user(user_id)

