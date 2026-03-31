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


class TrackingEventInDB(TrackingEventBase):
    id: Optional[str] = Field(None, alias="_id")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        json_encoders = {datetime: lambda dt: dt.isoformat()}
