from typing import List
from app.schemas.tracking_schema import TrackingCreate, TrackingResponse, TrackingUpdate
from app.services.tracking_service import TrackingService

class TrackingController:
    def __init__(self, service: TrackingService = None):
        self.service = service or TrackingService()

    def list_tracking(self, skip: int = 0, limit: int = 50) -> List[TrackingResponse]:
        tracking_List=self.service.list_tracking(skip=skip,limit=limit)
        return [TrackingResponse(**tracking) for tracking in tracking_List]
    def get_tracking(self,tracking_id:str)->TrackingResponse:
        tracking=self.service.get_tracking(tracking_id)
        return TrackingResponse(**tracking)
    def create_tracking(self,payload:TrackingCreate)->TrackingResponse:
        created_tracking=self.service.create_tracking(payload)
        return TrackingResponse(**created_tracking)
    def update_tracking(self,tracking_id:str,payload:TrackingUpdate)->TrackingResponse:
        updated_tracking=self.service.update_tracking(tracking_id,payload)
        return TrackingResponse(**updated_tracking)
    def delete_tracking(self,tracking_id:str)->None:
        self.service.delete_tracking(tracking_id)
    def get_tracking_by_shipment(self,shipment_id:str)->List[TrackingResponse]:
        tracking_list=self.service.get_tracking_by_shipment(shipment_id)
        return [TrackingResponse(**tracking) for tracking in tracking_list]
    def get_tracking_by_hub(self,hub_id:str)->List[TrackingResponse]:
        tracking_list=self.service.get_tracking_by_hub(hub_id)
        return [TrackingResponse(**tracking) for tracking in tracking_list]
    def get_tracking_by_agent(self,agent_id:str)->List[TrackingResponse]:
        tracking_list=self.service.get_tracking_by_agent(agent_id)
        return [TrackingResponse(**tracking) for tracking in tracking_list]
    def get_tracking_by_status(self,status:str)->List[TrackingResponse]:
        tracking_list=self.service.get_tracking_by_status(status)
        return [TrackingResponse(**tracking) for tracking in tracking_list]
