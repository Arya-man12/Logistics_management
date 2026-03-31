from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class HubBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    code: str = Field(..., min_length=2, max_length=30)
    address: str = Field(..., max_length=250)
    city: str
    state: str
    country: str = "India"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    status: str = "active"


class HubCreate(HubBase):
    pass


class HubUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    code: Optional[str] = Field(None, min_length=2, max_length=30)
    address: Optional[str] = Field(None, max_length=250)
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    status: Optional[str] = None


class HubResponse(HubBase):
    id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
