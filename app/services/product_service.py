# File: app/services/product_service.py
"""Data Access Service (Repository) for Product entities."""
from __future__ import annotations
from typing import TYPE_CHECKING
from uuid import UUID
import sqlalchemy as sa
from sqlalchemy.future import select

from app.core.result import Result, Success, Failure
from app.models.product import Product
from app.services.base_service import BaseService

if TYPE_CHECKING:
    from app.core.application_core import ApplicationCore

class ProductService(BaseService):
    """Handles all database interactions for the Product model."""

    def __init__(self, core: "ApplicationCore"):
        super().__init__(core, Product)

    async def get_by_sku(self, company_id: UUID, sku: str) -> Result[Product | None, str]:
        """Fetches a product by its unique SKU for a given company."""
        try:
            async with self.core.get_session() as session:
                stmt = select(Product).where(
                    Product.company_id == company_id,
                    Product.sku == sku
                )
                result = await session.execute(stmt)
                product = result.scalar_one_or_none()
                return Success(product)
        except Exception as e:
            return Failure(f"Database error fetching product by SKU: {e}")

    async def create_product(self, product: Product) -> Result[Product, str]:
        """Saves a new product instance to the database."""
        try:
            async with self.core.get_session() as session:
                session.add(product)
                await session.flush()  # Use flush to get the ID before commit
                await session.refresh(product)
                return Success(product)
        except sa.exc.IntegrityError:
            # Handles cases like duplicate SKU
            return Failure("Product with this SKU already exists.")
        except Exception as e:
            return Failure(f"Database error creating product: {e}")

    async def update_product(self, product: Product) -> Result[Product, str]:
        """Updates an existing product instance in the database."""
        try:
            async with self.core.get_session() as session:
                session.add(product) # Add to session to track changes
                await session.flush()
                await session.refresh(product)
                return Success(product)
        except Exception as e:
            return Failure(f"Database error updating product: {e}")
