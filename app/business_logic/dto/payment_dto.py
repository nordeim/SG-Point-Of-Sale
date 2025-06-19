# File: app/business_logic/dto/payment_dto.py
"""Data Transfer Objects for Payment Method operations."""
import uuid
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field

class PaymentMethodType(str, Enum):
    """Enumeration for the types of payment methods available."""
    CASH = "CASH"
    CARD = "CARD"
    NETS = "NETS"
    PAYNOW = "PAYNOW"
    VOUCHER = "VOUCHER"
    STORE_CREDIT = "STORE_CREDIT"

class PaymentMethodBaseDTO(BaseModel):
    """Base DTO with common payment method fields."""
    name: str = Field(..., min_length=2, max_length=100, description="The display name of the payment method")
    type: PaymentMethodType = Field(..., description="The type of the payment method")
    is_active: bool = Field(True, description="Indicates if the payment method is currently active and can be used")

class PaymentMethodCreateDTO(PaymentMethodBaseDTO):
    """DTO for creating a new payment method."""
    pass

class PaymentMethodUpdateDTO(PaymentMethodBaseDTO):
    """DTO for updating an existing payment method."""
    pass

class PaymentMethodDTO(PaymentMethodBaseDTO):
    """DTO representing a full payment method record for data retrieval."""
    id: uuid.UUID = Field(..., description="Unique identifier for the payment method")

    class Config:
        from_attributes = True
