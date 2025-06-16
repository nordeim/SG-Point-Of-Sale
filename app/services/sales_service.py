# File: app/services/sales_service.py
"""Data Access Service (Repository) for Sales entities."""
from __future__ import annotations
from typing import TYPE_CHECKING
import sqlalchemy as sa

from app.core.result import Result, Success, Failure
from app.models.sales import SalesTransaction
from app.services.base_service import BaseService

if TYPE_CHECKING:
    from app.core.application_core import ApplicationCore
    from sqlalchemy.ext.asyncio import AsyncSession

class SalesService(BaseService):
    """
    Handles all database interactions for sales-related models.
    It encapsulates the atomic persistence of SalesTransaction and its related entities.
    """

    def __init__(self, core: "ApplicationCore"):
        super().__init__(core, SalesTransaction)

    async def create_full_transaction(self, transaction: SalesTransaction, session: AsyncSession) -> Result[SalesTransaction, str]:
        """
        Saves a complete SalesTransaction object, including its items and payments,
        within a provided session. This ensures the operation is part of a larger, atomic transaction.
        Args:
            transaction: The complete SalesTransaction ORM instance to save.
            session: The active SQLAlchemy AsyncSession from the calling manager.
        Returns:
            A Success containing the saved SalesTransaction, or a Failure with an error.
        """
        try:
            # The session is managed by the calling manager's `get_session` context.
            # `session.add(transaction)` automatically adds related objects (items, payments)
            # if relationships are configured with cascade="all, delete-orphan"
            session.add(transaction)
            await session.flush() # Flush to get any generated IDs (like transaction_id)
            await session.refresh(transaction) # Refresh the transaction instance to get generated fields

            # If related items/payments have defaults or triggers, they might need refreshing too
            for item in transaction.items:
                await session.refresh(item)
            for payment in transaction.payments:
                await session.refresh(payment)
                
            return Success(transaction)
        except sa.exc.IntegrityError as e:
            return Failure(f"Data integrity error creating sales transaction: {e.orig}")
        except Exception as e:
            return Failure(f"Database error saving full transaction: {e}")

    # TODO: Add methods to retrieve sales transactions by various criteria (e.g., date range, customer, number)
