# File: app/business_logic/managers/customer_manager.py
"""Business Logic Manager for Customer operations."""
from __future__ import annotations
from typing import TYPE_CHECKING, List, Optional
from uuid import UUID
from decimal import Decimal

from app.core.result import Result, Success, Failure
from app.business_logic.managers.base_manager import BaseManager
from app.business_logic.dto.customer_dto import CustomerDTO, CustomerCreateDTO, CustomerUpdateDTO
from app.models.customer import Customer

if TYPE_CHECKING:
    from app.core.application_core import ApplicationCore
    from app.services.customer_service import CustomerService
    from sqlalchemy.ext.asyncio import AsyncSession

class CustomerManager(BaseManager):
    """Orchestrates business logic for customers."""

    @property
    def customer_service(self) -> "CustomerService":
        return self.core.customer_service

    async def create_customer(self, company_id: UUID, dto: CustomerCreateDTO) -> Result[CustomerDTO, str]:
        """
        Creates a new customer.
        Business rule: Customer code and email must be unique for the company.
        """
        async with self.core.get_session() as session:
            existing_result = await self.customer_service.get_by_code(company_id, dto.customer_code, session)
            if isinstance(existing_result, Failure):
                return existing_result
            if existing_result.value is not None:
                return Failure(f"Business Rule Error: Customer with code '{dto.customer_code}' already exists.")

            if dto.email:
                email_check_result = await self.customer_service.get_by_email(company_id, dto.email, session)
                if isinstance(email_check_result, Failure):
                    return email_check_result
                if email_check_result.value is not None:
                    return Failure(f"Business Rule Error: Customer with email '{dto.email}' already exists.")

            new_customer = Customer(company_id=company_id, **dto.dict())
            
            create_result = await self.customer_service.create(new_customer, session)
            if isinstance(create_result, Failure):
                return create_result

            return Success(CustomerDTO.from_orm(create_result.value))

    async def update_customer(self, customer_id: UUID, dto: CustomerUpdateDTO) -> Result[CustomerDTO, str]:
        """Updates an existing customer."""
        async with self.core.get_session() as session:
            customer_result = await self.customer_service.get_by_id(customer_id, session)
            if isinstance(customer_result, Failure):
                return customer_result
            
            customer = customer_result.value
            if not customer:
                return Failure("Customer not found.")

            if dto.customer_code != customer.customer_code:
                existing_result = await self.customer_service.get_by_code(customer.company_id, dto.customer_code, session)
                if isinstance(existing_result, Failure):
                    return existing_result
                if existing_result.value is not None and existing_result.value.id != customer_id:
                    return Failure(f"Business Rule Error: New customer code '{dto.customer_code}' is already in use by another customer.")
            
            if dto.email and dto.email != customer.email:
                email_check_result = await self.customer_service.get_by_email(customer.company_id, dto.email, session)
                if isinstance(email_check_result, Failure):
                    return email_check_result
                if email_check_result.value is not None and email_check_result.value.id != customer_id:
                    return Failure(f"Business Rule Error: New email '{dto.email}' is already in use by another customer.")

            for field, value in dto.dict(exclude_unset=True).items():
                setattr(customer, field, value)

            update_result = await self.customer_service.update(customer, session)
            if isinstance(update_result, Failure):
                return update_result
            
            return Success(CustomerDTO.from_orm(update_result.value))

    async def get_customer(self, customer_id: UUID, session: Optional["AsyncSession"] = None) -> Result[CustomerDTO, str]:
        """Retrieves a single customer by ID."""
        # FIX: Pass the session down to the service layer.
        result = await self.customer_service.get_by_id(customer_id, session)
        if isinstance(result, Failure):
            return result
        
        customer = result.value
        if not customer:
            return Failure("Customer not found.")
            
        return Success(CustomerDTO.from_orm(customer))

    async def get_all_customers(self, company_id: UUID, limit: int = 100, offset: int = 0) -> Result[List[CustomerDTO], str]:
        """Retrieves all customers for a given company."""
        result = await self.customer_service.get_all(company_id, limit, offset)
        if isinstance(result, Failure):
            return result
        
        return Success([CustomerDTO.from_orm(c) for c in result.value])
    
    async def search_customers(self, company_id: UUID, term: str, limit: int = 100, offset: int = 0) -> Result[List[CustomerDTO], str]:
        """Searches for customers by code, name, email, or phone."""
        result = await self.customer_service.search(company_id, term, limit, offset)
        if isinstance(result, Failure):
            return result
        
        return Success([CustomerDTO.from_orm(c) for c in result.value])

    async def deactivate_customer(self, customer_id: UUID) -> Result[bool, str]:
        """Deactivates a customer (soft delete)."""
        async with self.core.get_session() as session:
            customer_result = await self.customer_service.get_by_id(customer_id, session)
            if isinstance(customer_result, Failure):
                return customer_result
            
            customer = customer_result.value
            if not customer:
                return Failure("Customer not found.")
            
            customer.is_active = False
            update_result = await self.customer_service.update(customer, session)
            if isinstance(update_result, Failure):
                return update_result
            
            return Success(True)

    async def add_loyalty_points_for_sale(self, customer_id: UUID, sale_total: Decimal, session: "AsyncSession") -> Result[int, str]:
        """
        Calculates and adds loyalty points for a completed sale.
        This method MUST be called with an existing session from a parent transaction.
        It modifies the customer object and relies on the calling transaction to commit the change.
        """
        loyalty_rate = Decimal("10.00")
        points_to_add = int(sale_total // loyalty_rate)
        
        if points_to_add <= 0:
            return Success(0)

        # FIX: Fetch the customer using the provided session.
        customer_result = await self.customer_service.get_by_id(customer_id, session)
        if isinstance(customer_result, Failure):
            return customer_result
        
        customer = customer_result.value
        if not customer:
            return Failure(f"Customer with ID {customer_id} not found.")
        
        # FIX: Modify the object. The Unit of Work in the parent session will detect
        # this change and include it in the final COMMIT. No explicit update call is needed.
        customer.loyalty_points += points_to_add
            
        return Success(customer.loyalty_points)
