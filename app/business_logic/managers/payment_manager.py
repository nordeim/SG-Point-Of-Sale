# File: app/business_logic/managers/payment_manager.py
"""Business Logic Manager for Payment Method operations."""
from __future__ import annotations
from typing import TYPE_CHECKING, List
from uuid import UUID

from app.core.result import Result, Success, Failure
from app.business_logic.managers.base_manager import BaseManager
from app.business_logic.dto.payment_dto import PaymentMethodDTO, PaymentMethodCreateDTO, PaymentMethodUpdateDTO
from app.models.sales import PaymentMethod

if TYPE_CHECKING:
    from app.core.application_core import ApplicationCore
    from app.services.payment_service import PaymentMethodService

class PaymentMethodManager(BaseManager):
    """Orchestrates business logic for payment methods."""

    @property
    def payment_method_service(self) -> "PaymentMethodService":
        return self.core.payment_method_service

    async def get_all_payment_methods(self, company_id: UUID) -> Result[List[PaymentMethodDTO], str]:
        """Retrieves all payment methods for a given company, sorted by name."""
        result = await self.payment_method_service.get_all(company_id, order_by_column='name')
        if isinstance(result, Failure):
            return result
        return Success([PaymentMethodDTO.from_orm(pm) for pm in result.value])

    async def create_payment_method(self, company_id: UUID, dto: PaymentMethodCreateDTO) -> Result[PaymentMethodDTO, str]:
        """Creates a new payment method after validating business rules."""
        # Business rule: Check for duplicate name
        existing_result = await self.payment_method_service.get_by_name(company_id, dto.name)
        if isinstance(existing_result, Failure):
            return existing_result
        if existing_result.value:
            return Failure(f"A payment method with the name '{dto.name}' already exists.")

        new_method = PaymentMethod(company_id=company_id, **dto.dict())
        
        create_result = await self.payment_method_service.create(new_method)
        if isinstance(create_result, Failure):
            return create_result

        return Success(PaymentMethodDTO.from_orm(create_result.value))

    async def update_payment_method(self, method_id: UUID, dto: PaymentMethodUpdateDTO) -> Result[PaymentMethodDTO, str]:
        """Updates an existing payment method."""
        method_result = await self.payment_method_service.get_by_id(method_id)
        if isinstance(method_result, Failure):
            return method_result
        
        method = method_result.value
        if not method:
            return Failure(f"Payment method with ID {method_id} not found.")

        # Business rule: If name is changed, check for duplication.
        if dto.name != method.name:
            existing_result = await self.payment_method_service.get_by_name(method.company_id, dto.name)
            if isinstance(existing_result, Failure):
                return existing_result
            if existing_result.value and existing_result.value.id != method_id:
                return Failure(f"Another payment method with the name '{dto.name}' already exists.")
        
        # Update fields from DTO
        for field, value in dto.dict(exclude_unset=True).items():
            setattr(method, field, value)

        update_result = await self.payment_method_service.update(method)
        if isinstance(update_result, Failure):
            return update_result
        
        return Success(PaymentMethodDTO.from_orm(update_result.value))

    async def deactivate_payment_method(self, method_id: UUID) -> Result[bool, str]:
        """Deactivates a payment method (soft delete)."""
        method_result = await self.payment_method_service.get_by_id(method_id)
        if isinstance(method_result, Failure):
            return method_result
        
        method = method_result.value
        if not method:
            return Failure("Payment method not found.")
        
        method.is_active = False
        update_result = await self.payment_method_service.update(method)
        if isinstance(update_result, Failure):
            return update_result
        
        return Success(True)
