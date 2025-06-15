# File: app/business_logic/dto/product_dto.py
"""
Data Transfer Objects (DTOs) for the Product entity.

These models define the data structure for passing product information between
the different layers of the application, ensuring a clear and validated contract.
"""
import uuid
from decimal import Decimal
from pydantic import BaseModel, Field, validator

class ProductBaseDTO(BaseModel):
    """Base DTO with common product fields."""
    sku: str = Field(..., min_length=1, max_length=100, description="Stock Keeping Unit")
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    selling_price: Decimal = Field(..., gt=0, description="The retail price of the product")
    cost_price: Decimal = Field(..., ge=0, description="The cost of acquiring the product")
    gst_rate: Decimal = Field(8.00, ge=0, le=100, description="Goods and Services Tax rate")
    track_inventory: bool = True
    is_active: bool = True
    category_id: uuid.UUID | None = None
    supplier_id: uuid.UUID | None = None
    barcode: str | None = None
    reorder_point: int = Field(0, ge=0)

class ProductCreateDTO(ProductBaseDTO):
    """DTO for creating a new product."""
    pass

class ProductUpdateDTO(ProductBaseDTO):
    """DTO for updating an existing product."""
    pass

class ProductDTO(ProductBaseDTO):
    """DTO representing a full product record, including its unique ID."""
    id: uuid.UUID

    class Config:
        orm_mode = True # Allows creating DTO from a SQLAlchemy ORM model instance
