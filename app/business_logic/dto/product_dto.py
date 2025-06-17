# File: app/business_logic/dto/product_dto.py
"""
Data Transfer Objects (DTOs) for the Product entity.
"""
import uuid
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, validator

class ProductBaseDTO(BaseModel):
    """Base DTO with common product fields."""
    sku: str = Field(..., min_length=1, max_length=100, description="Stock Keeping Unit")
    name: str = Field(..., min_length=1, max_length=255, description="Product name")
    description: Optional[str] = Field(None, description="Detailed description of the product")
    selling_price: Decimal = Field(..., gt=Decimal("0.00"), decimal_places=4, description="The retail price of the product")
    cost_price: Decimal = Field(..., ge=Decimal("0.00"), decimal_places=4, description="The cost of acquiring the product")
    gst_rate: Decimal = Field(Decimal("9.00"), ge=Decimal("0.00"), le=Decimal("100.00"), decimal_places=2, description="Goods and Services Tax rate (e.g., 9.00 for 9%)") # FIX: Updated GST Rate
    track_inventory: bool = True
    is_active: bool = True
    category_id: Optional[uuid.UUID] = Field(None, description="UUID of the product's category")
    supplier_id: Optional[uuid.UUID] = Field(None, description="UUID of the product's primary supplier")
    barcode: Optional[str] = Field(None, max_length=100, description="Product barcode (EAN, UPC, etc.)")
    reorder_point: int = Field(0, ge=0, description="Threshold quantity for reordering suggestions")

    @validator('selling_price')
    def check_selling_price_not_less_than_cost_price(cls, v, values):
        if 'cost_price' in values and v < values['cost_price']:
            raise ValueError('Selling price cannot be less than cost price.')
        return v

class ProductCreateDTO(ProductBaseDTO):
    """DTO for creating a new product."""
    pass

class ProductUpdateDTO(ProductBaseDTO):
    """DTO for updating an existing product."""
    pass

class ProductDTO(ProductBaseDTO):
    """DTO representing a full product record, including its unique ID."""
    id: uuid.UUID = Field(..., description="Unique identifier for the product")

    class Config:
        from_attributes = True
