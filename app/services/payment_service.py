# File: app/services/payment_service.py
"""Data Access Service (Repository) for Payment methods and Payments."""
from __future__ import annotations
from typing import TYPE_CHECKING, List
from uuid import UUID
import sqlalchemy as sa
from sqlalchemy.future import select

from app.core.result import Result, Success, Failure
from app.models.sales import PaymentMethod, Payment # Import ORM models from sales.py
from app.services.base_service import BaseService

if TYPE_CHECKING:
    from app.core.application_core import ApplicationCore

class PaymentMethodService(BaseService):
    """
    Handles database interactions for PaymentMethod models.
    Inherits generic CRUD from BaseService.
    """
    def __init__(self, core: "ApplicationCore"):
        super().__init__(core, PaymentMethod)

    async def get_by_name(self, company_id: UUID, name: str) -> Result[PaymentMethod | None, str]:
        """Fetches a payment method by its name for a given company."""
        try:
            async with self.core.get_session() as session:
                stmt = select(PaymentMethod).where(
                    PaymentMethod.company_id == company_id,
                    PaymentMethod.name == name
                )
                result = await session.execute(stmt)
                method = result.scalar_one_or_none()
                return Success(method)
        except Exception as e:
            return Failure(f"Database error fetching payment method by name '{name}': {e}")
    
    async def get_all_active_methods(self, company_id: UUID) -> Result[List[PaymentMethod], str]:
        """Fetches all active payment methods for a given company."""
        try:
            async with self.core.get_session() as session:
                stmt = select(PaymentMethod).where(
                    PaymentMethod.company_id == company_id,
                    PaymentMethod.is_active == True
                ).order_by(PaymentMethod.name)
                result = await session.execute(stmt)
                methods = result.scalars().all()
                return Success(methods)
        except Exception as e:
            return Failure(f"Database error fetching active payment methods: {e}")

class PaymentService(BaseService):
    """
    Handles database interactions for Payment models.
    For now, mostly used for retrieving, as creation is part of SalesService.
    """
    def __init__(self, core: "ApplicationCore"):
        super().__init__(core, Payment)

    # TODO: Add methods for retrieving payments, e.g., by sales_transaction_id
