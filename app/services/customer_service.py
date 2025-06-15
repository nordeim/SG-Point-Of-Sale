# File: app/services/customer_service.py
"""Data Access Service (Repository) for Customer entities."""
from __future__ import annotations
from typing import TYPE_CHECKING
from uuid import UUID
import sqlalchemy as sa
from sqlalchemy.future import select

from app.core.result import Result, Success, Failure
from app.models.customer import Customer
from app.services.base_service import BaseService

if TYPE_CHECKING:
    from app.core.application_core import ApplicationCore

class CustomerService(BaseService):
    """Handles all database interactions for the Customer model."""

    def __init__(self, core: "ApplicationCore"):
        super().__init__(core, Customer)

    async def get_by_code(self, company_id: UUID, code: str) -> Result[Customer | None, str]:
        """Fetches a customer by their unique code for a given company."""
        try:
            async with self.core.get_session() as session:
                stmt = select(Customer).where(
                    Customer.company_id == company_id,
                    Customer.customer_code == code
                )
                result = await session.execute(stmt)
                customer = result.scalar_one_or_none()
                return Success(customer)
        except Exception as e:
            return Failure(f"Database error fetching customer by code: {e}")

    async def create_customer(self, customer: Customer) -> Result[Customer, str]:
        """Saves a new customer instance to the database."""
        try:
            async with self.core.get_session() as session:
                session.add(customer)
                await session.flush()
                await session.refresh(customer)
                return Success(customer)
        except sa.exc.IntegrityError:
            return Failure("Customer with this code or email already exists.")
        except Exception as e:
            return Failure(f"Database error creating customer: {e}")

    async def update_customer(self, customer: Customer) -> Result[Customer, str]:
        """Updates an existing customer instance in the database."""
        try:
            async with self.core.get_session() as session:
                session.add(customer)
                await session.flush()
                await session.refresh(customer)
                return Success(customer)
        except Exception as e:
            return Failure(f"Database error updating customer: {e}")
