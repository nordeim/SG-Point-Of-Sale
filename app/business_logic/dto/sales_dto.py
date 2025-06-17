# File: app/business_logic/dto/sales_dto.py
"""Data Transfer Objects for Sales operations."""
import uuid
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class CartItemDTO(BaseModel):
    """DTO representing an item to be added to a sales transaction."""
    product_id: uuid.UUID = Field(..., description="UUID of the product being sold")
    variant_id: Optional[uuid.UUID] = Field(None, description="UUID of the specific product variant, if any")
    quantity: Decimal = Field(..., gt=Decimal("0.00"), decimal_places=4, description="Quantity of the product sold")
    unit_price_override: Optional[Decimal] = Field(None, ge=Decimal("0.00"), decimal_places=4, description="Optional override for unit selling price")

class PaymentInfoDTO(BaseModel):
    """DTO representing a payment to be applied to a sale."""
    payment_method_id: uuid.UUID = Field(..., description="UUID of the payment method used")
    amount: Decimal = Field(..., gt=Decimal("0.00"), decimal_places=2, description="Amount paid using this method")
    reference_number: Optional[str] = Field(None, max_length=100, description="Reference number (e.g., card approval code)")

class SaleCreateDTO(BaseModel):
    """DTO for creating a new sales transaction."""
    company_id: uuid.UUID
    outlet_id: uuid.UUID
    cashier_id: uuid.UUID
    customer_id: Optional[uuid.UUID] = None
    cart_items: List[CartItemDTO] = Field(..., min_items=1)
    payments: List[PaymentInfoDTO] = Field(..., min_items=1)
    notes: Optional[str] = None

class SalesTransactionItemDTO(BaseModel):
    """DTO for a single item within a finalized sales transaction receipt."""
    product_id: uuid.UUID
    variant_id: Optional[uuid.UUID] = None
    product_name: str
    sku: str
    quantity: Decimal = Field(..., decimal_places=4)
    unit_price: Decimal = Field(..., decimal_places=4)
    line_total: Decimal = Field(..., decimal_places=2)
    gst_rate: Decimal = Field(..., decimal_places=2)
    
    class Config:
        from_attributes = True

class FinalizedSaleDTO(BaseModel):
    """DTO representing a completed sale, suitable for generating a receipt."""
    transaction_id: uuid.UUID
    transaction_number: str
    transaction_date: datetime
    subtotal: Decimal = Field(..., decimal_places=2)
    tax_amount: Decimal = Field(..., decimal_places=2)
    discount_amount: Decimal = Field(..., decimal_places=2)
    rounding_adjustment: Decimal = Field(..., decimal_places=2)
    total_amount: Decimal = Field(..., decimal_places=2)
    amount_paid: Decimal = Field(..., decimal_places=2)
    change_due: Decimal = Field(..., decimal_places=2)
    customer_name: Optional[str] = None
    cashier_name: str
    items: List[SalesTransactionItemDTO]
