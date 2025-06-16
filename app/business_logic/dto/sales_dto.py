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
    company_id: uuid.UUID = Field(..., description="UUID of the company making the sale")
    outlet_id: uuid.UUID = Field(..., description="UUID of the outlet where the sale occurred")
    cashier_id: uuid.UUID = Field(..., description="UUID of the cashier processing the sale")
    customer_id: Optional[uuid.UUID] = Field(None, description="UUID of the customer (optional)")
    cart_items: List[CartItemDTO] = Field(..., min_items=1, description="List of items in the cart")
    payments: List[PaymentInfoDTO] = Field(..., min_items=1, description="List of payments applied to the sale")
    notes: Optional[str] = Field(None, description="Any notes for the sales transaction")

class SalesTransactionItemDTO(BaseModel):
    """DTO for a single item within a finalized sales transaction receipt."""
    product_id: uuid.UUID
    variant_id: Optional[uuid.UUID] = None
    product_name: str
    sku: str
    quantity: Decimal = Field(..., decimal_places=4)
    unit_price: Decimal = Field(..., decimal_places=4)
    line_total: Decimal = Field(..., decimal_places=2)
    gst_rate: Decimal = Field(..., decimal_places=2) # GST rate at the time of sale
    
    class Config:
        orm_mode = True

class FinalizedSaleDTO(BaseModel):
    """DTO representing a completed sale, suitable for generating a receipt."""
    transaction_id: uuid.UUID = Field(..., description="UUID of the finalized sales transaction")
    transaction_number: str = Field(..., description="Unique transaction number")
    transaction_date: datetime = Field(..., description="Date and time of the transaction")
    
    # Financial summary
    subtotal: Decimal = Field(..., decimal_places=2, description="Subtotal before tax and discount")
    tax_amount: Decimal = Field(..., decimal_places=2, description="Total tax amount")
    discount_amount: Decimal = Field(..., decimal_places=2, description="Total discount amount")
    rounding_adjustment: Decimal = Field(..., decimal_places=2, description="Rounding adjustment for total")
    total_amount: Decimal = Field(..., decimal_places=2, description="Final total amount due")
    
    # Payment details
    amount_paid: Decimal = Field(..., decimal_places=2, description="Total amount paid by customer")
    change_due: Decimal = Field(..., decimal_places=2, description="Change given back to customer")

    # Customer and Cashier info (optional for receipt)
    customer_name: Optional[str] = Field(None, description="Name of the customer (if associated)")
    cashier_name: str = Field(..., description="Name of the cashier who processed the sale")

    # Line items for receipt
    items: List[SalesTransactionItemDTO] = Field(..., description="List of items in the transaction")
