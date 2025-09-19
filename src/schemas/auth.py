from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    dueno_de_activo: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False


class UserCreate(UserBase):
    """Schema for creating a new user"""
    password: str


class UserUpdate(BaseModel):
    """Schema for updating user information"""
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    dueno_de_activo: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None


class UserResponse(UserBase):
    """Schema for user response (without password)"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """Schema for user login"""
    username: str  # Can be username or email
    password: str


class Token(BaseModel):
    """Token response schema"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token data schema for JWT payload"""
    user_id: Optional[int] = None
    username: Optional[str] = None