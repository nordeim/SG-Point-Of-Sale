# File: app/business_logic/dto/customer_dto.py
"""Data Transfer Objects (DTOs) for the Customer entity."""
import uuid
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, EmailStr

class CustomerBaseDTO(BaseModel):
    """Base DTO with common customer fields."""
    customer_code: str = Field(..., min_length=1, max_length=50, description="Unique code for the customer")
    name: str = Field(..., min_length=1, max_length=255, description="Customer's full name")
    email: Optional[EmailStr] = Field(None, description="Customer's email address")
    phone: Optional[str] = Field(None, description="Customer's phone number")
    address: Optional[str] = Field(None, description="Customer's address")

class CustomerCreateDTO(CustomerBaseDTO):
    """DTO for creating a new customer."""
    credit_limit: Decimal = Field(Decimal("0.00"), ge=0, decimal_places=2, description="Credit limit extended to the customer")

class CustomerUpdateDTO(CustomerBaseDTO):
    """DTO for updating an existing customer."""
    credit_limit: Decimal = Field(Decimal("0.00"), ge=0, decimal_places=2, description="Credit limit extended to the customer")
    is_active: bool = True

class CustomerDTO(CustomerBaseDTO):
    """DTO representing a full customer record."""
    id: uuid.UUID = Field(..., description="Unique identifier for the customer")
    loyalty_points: int = Field(..., ge=0, description="Current loyalty points balance")
    credit_limit: Decimal = Field(..., ge=0, decimal_places=2, description="Credit limit extended to the customer")
    is_active: bool = True

    class Config:
        orm_mode = True

class LoyaltyPointAdjustmentDTO(BaseModel):
    """DTO for manually adjusting a customer's loyalty points."""
    customer_id: uuid.UUID
    points_change: int # Can be positive (add) or negative (deduct)
    reason: str = Field(..., min_length=1, description="Reason for the manual adjustment (e.g., 'Goodwill gesture', 'Point correction')")
    admin_user_id: uuid.UUID # User performing the adjustment
