# File: app/business_logic/dto/customer_dto.py
"""Data Transfer Objects (DTOs) for the Customer entity."""
import uuid
from decimal import Decimal
from pydantic import BaseModel, Field, EmailStr

class CustomerBaseDTO(BaseModel):
    """Base DTO with common customer fields."""
    customer_code: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr | None = None
    phone: str | None = None

class CustomerCreateDTO(CustomerBaseDTO):
    """DTO for creating a new customer."""
    credit_limit: Decimal = Field(Decimal("0.00"), ge=0)

class CustomerUpdateDTO(CustomerBaseDTO):
    """DTO for updating an existing customer."""
    credit_limit: Decimal = Field(Decimal("0.00"), ge=0)
    is_active: bool = True

class CustomerDTO(CustomerBaseDTO):
    """DTO representing a full customer record."""
    id: uuid.UUID
    loyalty_points: int
    credit_limit: Decimal
    is_active: bool

    class Config:
        orm_mode = True
