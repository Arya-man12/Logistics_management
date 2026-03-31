from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class TrackingEventBase(BaseModel):
    shipment_id: str = Field(...)
    location: Optional[str] = None
    status: str = "in_transit"
    note: Optional[str] = None
    updated_by: Optional[str] = None


class TrackingEventCreate(TrackingEventBase):
    pass


class TrackingEventUpdate(BaseModel):
    location: Optional[str] = None
    status: Optional[str] = None
    note: Optional[str] = None
    updated_by: Optional[str] = None


class TrackingEventResponse(TrackingEventBase):
    id: Optional[str] = None
    updated_at: datetime


TrackingCreate = TrackingEventCreate
TrackingUpdate = TrackingEventUpdate
TrackingResponse = TrackingEventResponse
