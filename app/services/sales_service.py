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
        within a provided session. This method only adds to the session and flushes;
        it does not commit or refresh, leaving that to the calling manager's Unit of Work.
        Args:
            transaction: The complete SalesTransaction ORM instance to save.
            session: The active SQLAlchemy AsyncSession from the calling manager.
        Returns:
            A Success containing the stateful SalesTransaction object, or a Failure.
        """
        try:
            # Add the entire object graph to the session.
            # Cascades will handle adding items and payments.
            session.add(transaction)
            
            # Flush the session to send the INSERT statements to the DB.
            # This generates primary keys and validates constraints without committing.
            await session.flush() 
            
            # Return the instance. It is now persistent within the session's context.
            return Success(transaction)
        except sa.exc.IntegrityError as e:
            # The transaction will be rolled back by the manager's context.
            return Failure(f"Data integrity error creating sales transaction: {e.orig}")
        except Exception as e:
            # The transaction will be rolled back by the manager's context.
            return Failure(f"Database error saving full transaction: {e}")
