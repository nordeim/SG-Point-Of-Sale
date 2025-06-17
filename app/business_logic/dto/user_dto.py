# File: app/business_logic/dto/user_dto.py
"""Data Transfer Objects for User operations."""
import uuid
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr

class UserBaseDTO(BaseModel):
    username: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool = True

class UserCreateDTO(UserBaseDTO):
    password: str = Field(..., min_length=8, description="User's initial password")
    roles: List[uuid.UUID]

class UserUpdateDTO(UserBaseDTO):
    password: Optional[str] = Field(None, min_length=8, description="New password (if changing)")
    roles: List[uuid.UUID]

class RoleDTO(BaseModel):
    id: uuid.UUID
    name: str
    class Config:
        from_attributes = True

class UserDTO(UserBaseDTO):
    id: uuid.UUID
    roles: List[RoleDTO]
    class Config:
        from_attributes = True
