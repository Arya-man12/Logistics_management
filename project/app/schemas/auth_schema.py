from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=3, max_length=120)
    email: EmailStr
    password: str = Field(..., min_length=8)
    role: str = "customer"
    phone: Optional[str] = Field(None, max_length=30)
    address: Optional[str] = Field(None, max_length=250)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AuthResponse(TokenResponse):
    user: dict


class TokenData(BaseModel):
    email: Optional[EmailStr] = None
    role: Optional[str] = None
