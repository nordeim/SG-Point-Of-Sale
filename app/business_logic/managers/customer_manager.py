# File: app/business_logic/managers/customer_manager.py
"""Business Logic Manager for Customer operations."""
from __future__ import annotations
from typing import TYPE_CHECKING
from uuid import UUID

from app.core.result import Result, Success, Failure
from app.business_logic.managers.base_manager import BaseManager
from app.business_logic.dto.customer_dto import CustomerDTO, CustomerCreateDTO, CustomerUpdateDTO
from app.models.customer import Customer

if TYPE_CHECKING:
    from app.core.application_core import ApplicationCore
    from app.services.customer_service import CustomerService

class CustomerManager(BaseManager):
    """Orchestrates business logic for customers."""

    @property
    def customer_service(self) -> "CustomerService":
        return self.core.customer_service # Assuming core has a customer_service property

    async def create_customer(self, company_id: UUID, dto: CustomerCreateDTO) -> Result[CustomerDTO, str]:
        """Creates a new customer."""
        # Business rule: e.g., customer code must be unique
        existing_result = await self.customer_service.get_by_code(company_id, dto.customer_code)
        if isinstance(existing_result, Failure):
            return existing_result
        if existing_result.value is not None:
            return Failure(f"Customer code '{dto.customer_code}' is already in use.")

        new_customer = Customer(company_id=company_id, **dto.dict())
        
        create_result = await self.customer_service.create_customer(new_customer)
        if isinstance(create_result, Failure):
            return create_result

        return Success(CustomerDTO.from_orm(create_result.value))

    # ... similar methods for update, get, etc.
