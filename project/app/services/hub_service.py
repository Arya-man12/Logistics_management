from typing import Dict, List, Optional

from app.exceptions.custom_exceptions import ConflictException, HubNotFoundException
from app.repositories.hub_repository import HubRepository
from app.schemas.hub_schema import HubCreate, HubUpdate
from app.utils.validators import validate_hub_status


class HubService:
    def __init__(self, repository: Optional[HubRepository] = None):
        self.repository = repository or HubRepository()

    def list_hubs(self, skip: int = 0, limit: int = 50) -> List[Dict]:
        return self.repository.list_hubs(skip=skip, limit=limit)

    def get_hub(self, hub_id: str) -> Dict:
        hub = self.repository.get_hub_by_id(hub_id)
        if not hub:
            raise HubNotFoundException()
        return hub

    def create_hub(self, payload: HubCreate) -> Dict:
        if self.repository.get_hub_by_code(payload.code):
            raise ConflictException("Hub code already exists")
        validate_hub_status(payload.status)
        return self.repository.create_hub(payload.model_dump())

    def update_hub(self, hub_id: str, payload: HubUpdate) -> Dict:
        if not self.repository.get_hub_by_id(hub_id):
            raise HubNotFoundException()
        update_data = payload.model_dump(exclude_unset=True)
        if "status" in update_data:
            validate_hub_status(update_data["status"])
        updated = self.repository.update_hub(hub_id, update_data)
        if not updated:
            raise HubNotFoundException()
        return updated

    def delete_hub(self, hub_id: str) -> bool:
        if not self.repository.get_hub_by_id(hub_id):
            raise HubNotFoundException()
        return self.repository.delete_hub(hub_id)

