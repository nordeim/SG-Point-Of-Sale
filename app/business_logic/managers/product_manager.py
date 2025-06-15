# File: app/business_logic/managers/product_manager.py
"""
Business Logic Manager for Product operations.

This manager orchestrates product-related workflows, enforces business rules,
and coordinates with the data access layer (ProductService).
"""
from __future__ import annotations
from typing import TYPE_CHECKING
from uuid import UUID

from app.core.result import Result, Success, Failure
from app.business_logic.managers.base_manager import BaseManager
from app.business_logic.dto.product_dto import ProductDTO, ProductCreateDTO, ProductUpdateDTO
from app.models.product import Product

if TYPE_CHECKING:
    from app.core.application_core import ApplicationCore
    from app.services.product_service import ProductService

class ProductManager(BaseManager):
    """Orchestrates business logic for products."""

    @property
    def product_service(self) -> "ProductService":
        # Lazy-load the service from the core
        return self.core.product_service

    async def create_product(self, company_id: UUID, dto: ProductCreateDTO) -> Result[ProductDTO, str]:
        """
        Creates a new product after validating business rules.
        Rule: A product's selling price should not be less than its cost price.
        """
        if dto.selling_price < dto.cost_price:
            return Failure("Validation Error: Selling price cannot be less than cost price.")

        # Check for duplicate SKU
        existing_product_result = await self.product_service.get_by_sku(company_id, dto.sku)
        if isinstance(existing_product_result, Failure):
            return existing_product_result # Propagate database error
        if existing_product_result.value is not None:
            return Failure(f"Business Rule Error: Product with SKU '{dto.sku}' already exists.")

        new_product = Product(company_id=company_id, **dto.dict())
        
        create_result = await self.product_service.create_product(new_product)
        if isinstance(create_result, Failure):
            return create_result

        return Success(ProductDTO.from_orm(create_result.value))

    async def update_product(self, product_id: UUID, dto: ProductUpdateDTO) -> Result[ProductDTO, str]:
        """Updates an existing product."""
        if dto.selling_price < dto.cost_price:
            return Failure("Validation Error: Selling price cannot be less than cost price.")

        product_result = await self.product_service.get_by_id(product_id)
        if isinstance(product_result, Failure):
            return product_result
        
        product = product_result.value
        if not product:
            return Failure("Product not found.")

        # Update fields from DTO
        for field, value in dto.dict(exclude_unset=True).items():
            setattr(product, field, value)

        update_result = await self.product_service.update_product(product)
        if isinstance(update_result, Failure):
            return update_result
        
        return Success(ProductDTO.from_orm(update_result.value))

    async def get_product(self, product_id: UUID) -> Result[ProductDTO, str]:
        """Retrieves a single product by its ID."""
        result = await self.product_service.get_by_id(product_id)
        if isinstance(result, Failure):
            return result
        
        product = result.value
        if not product:
            return Failure("Product not found.")
            
        return Success(ProductDTO.from_orm(product))
