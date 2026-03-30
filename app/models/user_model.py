from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    email: EmailStr
    name: str = Field(..., min_length=3, max_length=120)
    role: str = "customer"
    phone: Optional[str] = Field(None, max_length=30)
    address: Optional[str] = Field(None, max_length=250)
    is_active: bool = True


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=120)
    phone: Optional[str] = Field(None, max_length=30)
    address: Optional[str] = Field(None, max_length=250)
    is_active: Optional[bool] = None
    role: Optional[str] = None


class UserInDB(UserBase):
    id: Optional[str] = Field(None, alias="_id")
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        json_encoders = {datetime: lambda dt: dt.isoformat()}