# File: app/business_logic/managers/company_manager.py
"""Business Logic Manager for Company and Outlet operations."""
from __future__ import annotations
from typing import TYPE_CHECKING
from uuid import UUID

from app.core.result import Result, Success, Failure
from app.business_logic.managers.base_manager import BaseManager
from app.business_logic.dto.company_dto import CompanyDTO, CompanyUpdateDTO

if TYPE_CHECKING:
    from app.core.application_core import ApplicationCore
    from app.services.company_service import CompanyService

class CompanyManager(BaseManager):
    """Orchestrates business logic for companies and outlets."""
    @property
    def company_service(self) -> "CompanyService":
        return self.core.company_service

    async def get_company(self, company_id: UUID) -> Result[CompanyDTO, str]:
        """Retrieves company details."""
        result = await self.company_service.get_by_id(company_id)
        if isinstance(result, Failure):
            return result
        
        company = result.value
        if not company:
            return Failure(f"Company with ID {company_id} not found.")

        return Success(CompanyDTO.from_orm(company))

    async def update_company(self, company_id: UUID, dto: CompanyUpdateDTO) -> Result[CompanyDTO, str]:
        """Updates a company's details after validation."""
        company_result = await self.company_service.get_by_id(company_id)
        if isinstance(company_result, Failure):
            return company_result
        
        company = company_result.value
        if not company:
            return Failure(f"Company with ID {company_id} not found.")

        # Business Rule: Check for uniqueness if registration number is changed.
        if dto.registration_number and dto.registration_number != company.registration_number:
            existing_res = await self.company_service.get_by_registration_number(dto.registration_number)
            if isinstance(existing_res, Failure):
                return existing_res
            if existing_res.value and existing_res.value.id != company_id:
                return Failure(f"Registration number '{dto.registration_number}' is already in use.")

        # Business Rule: Check for uniqueness if GST number is changed.
        if dto.gst_registration_number and dto.gst_registration_number != company.gst_registration_number:
            existing_res = await self.company_service.get_by_gst_number(dto.gst_registration_number)
            if isinstance(existing_res, Failure):
                return existing_res
            if existing_res.value and existing_res.value.id != company_id:
                return Failure(f"GST registration number '{dto.gst_registration_number}' is already in use.")
        
        # Update fields from DTO
        for field, value in dto.dict(exclude_unset=True).items():
            setattr(company, field, value)
        
        update_result = await self.company_service.update(company)
        if isinstance(update_result, Failure):
            return update_result
        
        return Success(CompanyDTO.from_orm(update_result.value))
