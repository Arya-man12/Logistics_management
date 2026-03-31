from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ShipmentBase(BaseModel):
    customer_id: str = Field(...)
    origin_hub_id: str = Field(...)
    destination_hub_id: str = Field(...)
    pickup_address: str = Field(..., max_length=250)
    delivery_address: str = Field(..., max_length=250)
    package_description: str = Field(..., max_length=500)
    weight_kg: float = Field(..., gt=0)
    dimensions: Optional[PackageDimensions] = None
    service_type: str = "standard"
    status: str = "created"
    estimated_delivery_at: Optional[datetime] = None
    payment_status: str = Field(default="pending")
    assigned_agent_id: Optional[str] = None


class PackageDimensions(BaseModel):
    length_cm: Optional[float] = None
    width_cm: Optional[float] = None
    height_cm: Optional[float] = None


class ShipmentBase(BaseModel):
    customer_id: str = Field(...)
    origin_hub_id: str = Field(...)
    destination_hub_id: str = Field(...)
    pickup_address: str = Field(..., max_length=250)
    delivery_address: str = Field(..., max_length=250)
    package_description: str = Field(..., max_length=500)
    weight_kg: float = Field(..., gt=0)
    dimensions: Optional[PackageDimensions] = None
    service_type: str = "standard"
    status: str = "created"
    estimated_delivery_at: Optional[datetime] = None
    payment_status: str = Field(default="pending")
    assigned_agent_id: Optional[str] = None


class ShipmentCreate(ShipmentBase):
    pass


class ShipmentUpdate(BaseModel):
    origin_hub_id: Optional[str] = None
    destination_hub_id: Optional[str] = None
    pickup_address: Optional[str] = Field(None, max_length=250)
    delivery_address: Optional[str] = Field(None, max_length=250)
    package_description: Optional[str] = Field(None, max_length=500)
    weight_kg: Optional[float] = Field(None, gt=0)
    dimensions: Optional[PackageDimensions] = None
    service_type: Optional[str] = None
    status: Optional[str] = None
    estimated_delivery_at: Optional[datetime] = None
    payment_status: Optional[str] = None
    assigned_agent_id: Optional[str] = None


class ShipmentInDB(ShipmentBase):
    id: Optional[str] = Field(None, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        json_encoders = {datetime: lambda dt: dt.isoformat()}
