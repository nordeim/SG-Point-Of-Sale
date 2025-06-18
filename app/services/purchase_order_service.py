# File: app/services/purchase_order_service.py
"""Data Access Service (Repository) for Purchase Order entities."""
from __future__ import annotations
from typing import TYPE_CHECKING, List, Optional
from uuid import UUID
import sqlalchemy as sa
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload, joinedload

from app.core.result import Result, Success, Failure
from app.models.inventory import PurchaseOrder
from app.models.product import Supplier # Import Supplier for type hinting if needed
from app.services.base_service import BaseService

if TYPE_CHECKING:
    from app.core.application_core import ApplicationCore
    from sqlalchemy.ext.asyncio import AsyncSession

class PurchaseOrderService(BaseService):
    """
    Handles all database interactions for the PurchaseOrder model.
    Inherits generic CRUD from BaseService.
    """
    def __init__(self, core: "ApplicationCore"):
        super().__init__(core, PurchaseOrder)
        
    async def create_full_purchase_order(self, po: PurchaseOrder, session: AsyncSession) -> Result[PurchaseOrder, str]:
        """
        Saves a complete PurchaseOrder object, including its items, within a provided session.
        Args:
            po: The complete PurchaseOrder ORM instance to save.
            session: The active SQLAlchemy AsyncSession from the calling manager.
        Returns:
            A Success containing the saved PurchaseOrder, or a Failure with an error.
        """
        try:
            session.add(po)
            await session.flush()
            await session.refresh(po, attribute_names=['items']) # Refresh to load items
            return Success(po)
        except sa.exc.IntegrityError as e:
            return Failure(f"Data integrity error creating purchase order: {e.orig}")
        except Exception as e:
            return Failure(f"Database error saving full purchase order: {e}")

    async def get_all_with_supplier(self, company_id: UUID, outlet_id: Optional[UUID] = None, limit: int = 100, offset: int = 0) -> Result[List[PurchaseOrder], str]:
        """
        Fetches all purchase orders with their supplier information eagerly loaded
        using a JOIN for optimal performance.
        
        Args:
            company_id: The UUID of the company to filter by.
            outlet_id: Optional UUID of the outlet to filter by.
            limit: Maximum number of records to return.
            offset: Number of records to skip.
        
        Returns:
            A Success containing a list of PurchaseOrder model instances, or a Failure.
        """
        try:
            async with self.core.get_session() as session:
                stmt = select(self.model).where(
                    self.model.company_id == company_id
                ).options(
                    joinedload(self.model.supplier) # Use joinedload for a single SQL query
                ).order_by(
                    self.model.order_date.desc()
                ).offset(offset).limit(limit)

                if outlet_id:
                    stmt = stmt.where(self.model.outlet_id == outlet_id)

                result = await session.execute(stmt)
                records = result.scalars().unique().all()
                return Success(records)
        except Exception as e:
            return Failure(f"Database error fetching purchase orders with supplier: {e}")

    async def get_open_purchase_orders(self, company_id: UUID, outlet_id: Optional[UUID] = None) -> Result[List[PurchaseOrder], str]:
        """
        Fetches open/pending purchase orders for a company, optionally filtered by outlet.
        """
        try:
            async with self.core.get_session() as session:
                stmt = select(PurchaseOrder).where(
                    PurchaseOrder.company_id == company_id,
                    PurchaseOrder.status.in_(['DRAFT', 'SENT', 'PARTIALLY_RECEIVED'])
                ).options(selectinload(PurchaseOrder.items))
                
                if outlet_id:
                    stmt = stmt.where(PurchaseOrder.outlet_id == outlet_id)
                
                result = await session.execute(stmt)
                pos = result.scalars().unique().all()
                return Success(pos)
        except Exception as e:
            return Failure(f"Database error fetching open purchase orders: {e}")
