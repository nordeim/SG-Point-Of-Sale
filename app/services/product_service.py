# File: app/services/product_service.py
"""Data Access Service (Repository) for Product entities."""
from __future__ import annotations
from typing import TYPE_CHECKING, List, Optional
from uuid import UUID
import sqlalchemy as sa
from sqlalchemy.future import select
from sqlalchemy import or_

from app.core.result import Result, Success, Failure
from app.models.product import Product
from app.services.base_service import BaseService

if TYPE_CHECKING:
    from app.core.application_core import ApplicationCore
    from sqlalchemy.ext.asyncio import AsyncSession

class ProductService(BaseService):
    """Handles all database interactions for the Product model."""

    def __init__(self, core: "ApplicationCore"):
        super().__init__(core, Product)

    async def get_by_sku(self, company_id: UUID, sku: str, session: Optional[AsyncSession] = None) -> Result[Product | None, str]:
        """Fetches a product by its unique SKU for a given company."""
        try:
            async with self._get_session_context(session) as active_session:
                stmt = select(Product).where(
                    Product.company_id == company_id,
                    Product.sku == sku
                )
                result = await active_session.execute(stmt)
                product = result.scalar_one_or_none()
                return Success(product)
        except Exception as e:
            return Failure(f"Database error fetching product by SKU: {e}")

    async def search(self, company_id: UUID, term: str, limit: int = 100, offset: int = 0, session: Optional[AsyncSession] = None) -> Result[List[Product], str]:
        """Searches for active products by SKU, barcode, or name for a given company."""
        try:
            async with self._get_session_context(session) as active_session:
                search_pattern = f"%{term}%"
                stmt = select(self.model).where(
                    self.model.company_id == company_id,
                    self.model.is_active == True,
                    or_(
                        self.model.sku.ilike(search_pattern),
                        self.model.name.ilike(search_pattern),
                        self.model.barcode.ilike(search_pattern)
                    )
                ).offset(offset).limit(limit)
                
                result = await active_session.execute(stmt)
                records = result.scalars().all()
                return Success(records)
        except Exception as e:
            return Failure(f"Database error searching products: {e}")

    async def create_product(self, product: Product, session: Optional[AsyncSession] = None) -> Result[Product, str]:
        """Saves a new product instance to the database."""
        return await self.create(product, session)

    async def update_product(self, product: Product, session: Optional[AsyncSession] = None) -> Result[Product, str]:
        """Updates an existing product instance in the database."""
        return await self.update(product, session)
