# File: app/services/company_service.py
"""Data Access Service (Repository) for Company and Outlet entities."""
from __future__ import annotations
from typing import TYPE_CHECKING, List, Optional
from uuid import UUID
import sqlalchemy as sa
from sqlalchemy.future import select

from app.core.result import Result, Success, Failure
from app.models import Company, Outlet
from app.services.base_service import BaseService

if TYPE_CHECKING:
    from app.core.application_core import ApplicationCore

class CompanyService(BaseService):
    """Handles database interactions for Company models."""
    def __init__(self, core: "ApplicationCore"):
        super().__init__(core, Company)

class OutletService(BaseService):
    """Handles database interactions for Outlet models."""
    def __init__(self, core: "ApplicationCore"):
        super().__init__(core, Outlet)

    async def get_all_by_company(self, company_id: UUID) -> Result[List[Outlet], str]:
        """Fetches all active outlets for a specific company."""
        try:
            async with self.core.get_session() as session:
                stmt = select(Outlet).where(Outlet.company_id == company_id, Outlet.is_active == True).order_by(Outlet.name)
                result = await session.execute(stmt)
                return Success(result.scalars().all())
        except Exception as e:
            return Failure(f"Database error fetching outlets for company {company_id}: {e}")
