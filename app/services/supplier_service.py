# File: app/services/supplier_service.py
"""Data Access Service (Repository) for Supplier entities."""
from __future__ import annotations
from typing import TYPE_CHECKING, List, Optional
from uuid import UUID
import sqlalchemy as sa
from sqlalchemy.future import select

from app.core.result import Result, Success, Failure
from app.models.product import Supplier
from app.services.base_service import BaseService

if TYPE_CHECKING:
    from app.core.application_core import ApplicationCore
    from sqlalchemy.ext.asyncio import AsyncSession

class SupplierService(BaseService):
    """
    Handles all database interactions for the Supplier model.
    Inherits generic CRUD from BaseService.
    """
    def __init__(self, core: "ApplicationCore"):
        super().__init__(core, Supplier)
    
    async def get_by_name(self, company_id: UUID, name: str, session: Optional[AsyncSession] = None) -> Result[Supplier | None, str]:
        """Fetches a supplier by its unique name for a given company."""
        try:
            async with self._get_session_context(session) as active_session:
                stmt = select(Supplier).where(
                    Supplier.company_id == company_id,
                    Supplier.name == name
                )
                result = await active_session.execute(stmt)
                supplier = result.scalar_one_or_none()
                return Success(supplier)
        except Exception as e:
            return Failure(f"Database error fetching supplier by name '{name}': {e}")
    
    async def get_all_active_suppliers(self, company_id: UUID, session: Optional[AsyncSession] = None) -> Result[List[Supplier], str]:
        """Fetches all active suppliers for a given company."""
        try:
            async with self._get_session_context(session) as active_session:
                stmt = select(Supplier).where(
                    Supplier.company_id == company_id,
                    Supplier.is_active == True
                ).order_by(Supplier.name)
                result = await active_session.execute(stmt)
                suppliers = result.scalars().all()
                return Success(suppliers)
        except Exception as e:
            return Failure(f"Database error fetching active suppliers: {e}")

    async def search(self, company_id: UUID, term: str, limit: int = 100, offset: int = 0, session: Optional[AsyncSession] = None) -> Result[List[Supplier], str]:
        """
        Searches for suppliers by name, contact person, email, or phone.
        """
        try:
            async with self._get_session_context(session) as active_session:
                search_pattern = f"%{term}%"
                stmt = select(Supplier).where(
                    Supplier.company_id == company_id,
                    Supplier.is_active == True,
                    sa.or_(
                        Supplier.name.ilike(search_pattern),
                        Supplier.contact_person.ilike(search_pattern),
                        Supplier.email.ilike(search_pattern),
                        Supplier.phone.ilike(search_pattern)
                    )
                ).offset(offset).limit(limit)
                result = await active_session.execute(stmt)
                suppliers = result.scalars().all()
                return Success(suppliers)
        except Exception as e:
            return Failure(f"Database error searching suppliers: {e}")
