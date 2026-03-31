from typing import List, Optional

from app.schemas.hub_schema import HubCreate, HubResponse, HubUpdate
from app.services.hub_service import HubService


class HubController:
    def __init__(self, service: Optional[HubService] = None):
        self.service = service or HubService()

    def list_hubs(self, skip: int = 0, limit: int = 50) -> List[HubResponse]:
        hubs = self.service.list_hubs(skip=skip, limit=limit)
        return [HubResponse(**hub) for hub in hubs]

    def get_hub(self, hub_id: str) -> HubResponse:
        return HubResponse(**self.service.get_hub(hub_id))

    def create_hub(self, payload: HubCreate) -> HubResponse:
        return HubResponse(**self.service.create_hub(payload))

    def update_hub(self, hub_id: str, payload: HubUpdate) -> HubResponse:
        return HubResponse(**self.service.update_hub(hub_id, payload))

    def delete_hub(self, hub_id: str) -> None:
        self.service.delete_hub(hub_id)

