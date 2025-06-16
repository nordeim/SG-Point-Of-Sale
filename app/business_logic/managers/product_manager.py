# File: app/business_logic/managers/product_manager.py
"""
Business Logic Manager for Product operations.

This manager orchestrates product-related workflows, enforces business rules,
and coordinates with the data access layer (ProductService).
"""
from __future__ import annotations
from typing import TYPE_CHECKING, List
from uuid import UUID

from app.core.result import Result, Success, Failure
from app.business_logic.managers.base_manager import BaseManager
from app.business_logic.dto.product_dto import ProductDTO, ProductCreateDTO, ProductUpdateDTO
from app.models.product import Product # Import the ORM model

if TYPE_CHECKING:
    from app.core.application_core import ApplicationCore
    from app.services.product_service import ProductService

class ProductManager(BaseManager):
    """Orchestrates business logic for products."""

    @property
    def product_service(self) -> "ProductService":
        """Lazy-loads the ProductService instance from the core."""
        return self.core.product_service

    async def create_product(self, company_id: UUID, dto: ProductCreateDTO) -> Result[ProductDTO, str]:
        """
        Creates a new product after validating business rules.
        Rule: SKU must be unique for the company.
        Args:
            company_id: The UUID of the company creating the product.
            dto: The ProductCreateDTO containing product data.
        Returns:
            A Success with the created ProductDTO, or a Failure with an error message.
        """
        # Business rule: Check for duplicate SKU
        existing_product_result = await self.product_service.get_by_sku(company_id, dto.sku)
        if isinstance(existing_product_result, Failure):
            return existing_product_result # Propagate database error
        if existing_product_result.value is not None:
            return Failure(f"Business Rule Error: Product with SKU '{dto.sku}' already exists.")

        # Convert DTO to ORM model instance
        new_product = Product(company_id=company_id, **dto.dict())
        
        # Persist via service
        create_result = await self.product_service.create(new_product)
        if isinstance(create_result, Failure):
            return create_result # Propagate database error from service

        return Success(ProductDTO.from_orm(create_result.value))

    async def update_product(self, product_id: UUID, dto: ProductUpdateDTO) -> Result[ProductDTO, str]:
        """
        Updates an existing product after validating business rules.
        Args:
            product_id: The UUID of the product to update.
            dto: The ProductUpdateDTO containing updated product data.
        Returns:
            A Success with the updated ProductDTO, or a Failure with an error message.
        """
        # Retrieve existing product
        product_result = await self.product_service.get_by_id(product_id)
        if isinstance(product_result, Failure):
            return product_result
        
        product = product_result.value
        if not product:
            return Failure("Product not found.")

        # Business rule: If SKU is changed, check for duplication
        if dto.sku != product.sku:
            existing_product_result = await self.product_service.get_by_sku(product.company_id, dto.sku)
            if isinstance(existing_product_result, Failure):
                return existing_product_result
            if existing_product_result.value is not None and existing_product_result.value.id != product_id:
                return Failure(f"Business Rule Error: New SKU '{dto.sku}' is already in use by another product.")

        # Update fields from DTO
        for field, value in dto.dict(exclude_unset=True).items(): # exclude_unset for partial updates
            setattr(product, field, value)

        # Persist update via service
        update_result = await self.product_service.update(product)
        if isinstance(update_result, Failure):
            return update_result # Propagate database error
        
        return Success(ProductDTO.from_orm(update_result.value))

    async def get_product(self, product_id: UUID) -> Result[ProductDTO, str]:
        """
        Retrieves a single product by its ID.
        Args:
            product_id: The UUID of the product.
        Returns:
            A Success with the ProductDTO, or a Failure if not found or a database error occurs.
        """
        result = await self.product_service.get_by_id(product_id)
        if isinstance(result, Failure):
            return result
        
        product = result.value
        if not product:
            return Failure("Product not found.")
            
        return Success(ProductDTO.from_orm(product))

    async def get_all_products(self, company_id: UUID, limit: int = 100, offset: int = 0) -> Result[List[ProductDTO], str]:
        """
        Retrieves all products for a given company.
        Args:
            company_id: The UUID of the company.
            limit: Max number of products to return.
            offset: Number of products to skip.
        Returns:
            A Success with a list of ProductDTOs, or a Failure.
        """
        result = await self.product_service.get_all(company_id, limit, offset)
        if isinstance(result, Failure):
            return result
        
        return Success([ProductDTO.from_orm(p) for p in result.value])
    
    async def search_products(self, company_id: UUID, term: str, limit: int = 100, offset: int = 0) -> Result[List[ProductDTO], str]:
        """
        Searches for products by SKU, barcode, or name for a given company.
        Args:
            company_id: The UUID of the company.
            term: The search term.
            limit: Max number of products to return.
            offset: Number of products to skip.
        Returns:
            A Success with a list of matching ProductDTOs, or a Failure.
        """
        result = await self.product_service.search(company_id, term, limit, offset)
        if isinstance(result, Failure):
            return result
        
        return Success([ProductDTO.from_orm(p) for p in result.value])

    async def deactivate_product(self, product_id: UUID) -> Result[bool, str]:
        """
        Deactivates a product (soft delete) by setting its is_active flag to False.
        Args:
            product_id: The UUID of the product to deactivate.
        Returns:
            A Success with True if deactivated, or a Failure.
        """
        product_result = await self.product_service.get_by_id(product_id)
        if isinstance(product_result, Failure):
            return product_result
        
        product = product_result.value
        if not product:
            return Failure("Product not found.")
        
        product.is_active = False # Set the flag
        update_result = await self.product_service.update(product)
        if isinstance(update_result, Failure):
            return update_result
        
        return Success(True)
