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
    from sqlalchemy.ext.asyncio import AsyncSession

class CompanyService(BaseService):
    """Handles database interactions for Company models."""
    def __init__(self, core: "ApplicationCore"):
        super().__init__(core, Company)

    async def get_by_registration_number(self, registration_number: str, session: Optional[AsyncSession] = None) -> Result[Company | None, str]:
        """Fetches a company by its unique registration number."""
        try:
            async with self._get_session_context(session) as active_session:
                stmt = select(self.model).where(self.model.registration_number == registration_number)
                result = await active_session.execute(stmt)
                return Success(result.scalar_one_or_none())
        except Exception as e:
            return Failure(f"Database error fetching company by registration number: {e}")

    async def get_by_gst_number(self, gst_number: str, session: Optional[AsyncSession] = None) -> Result[Company | None, str]:
        """Fetches a company by its unique GST registration number."""
        try:
            async with self._get_session_context(session) as active_session:
                stmt = select(self.model).where(self.model.gst_registration_number == gst_number)
                result = await active_session.execute(stmt)
                return Success(result.scalar_one_or_none())
        except Exception as e:
            return Failure(f"Database error fetching company by GST number: {e}")


class OutletService(BaseService):
    """Handles database interactions for Outlet models."""
    def __init__(self, core: "ApplicationCore"):
        super().__init__(core, Outlet)

    async def get_all_by_company(self, company_id: UUID, session: Optional[AsyncSession] = None) -> Result[List[Outlet], str]:
        """Fetches all active outlets for a specific company."""
        try:
            async with self._get_session_context(session) as active_session:
                stmt = select(Outlet).where(Outlet.company_id == company_id, Outlet.is_active == True).order_by(Outlet.name)
                result = await active_session.execute(stmt)
                return Success(result.scalars().all())
        except Exception as e:
            return Failure(f"Database error fetching outlets for company {company_id}: {e}")
