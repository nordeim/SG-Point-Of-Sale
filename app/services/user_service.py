# File: app/services/user_service.py
"""Data Access Service for User and Role entities."""
from __future__ import annotations
from typing import TYPE_CHECKING, List, Optional
from uuid import UUID
import sqlalchemy as sa
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.core.result import Result, Success, Failure
from app.models import User, Role, UserRole, Permission, RolePermission
from app.services.base_service import BaseService

if TYPE_CHECKING:
    from app.core.application_core import ApplicationCore
    from sqlalchemy.ext.asyncio import AsyncSession

class UserService(BaseService):
    """Handles database interactions for the User model."""
    def __init__(self, core: "ApplicationCore"):
        super().__init__(core, User)

    async def get_by_username(self, company_id: UUID, username: str, session: Optional[AsyncSession] = None) -> Result[Optional[User], str]:
        try:
            async with self._get_session_context(session) as active_session:
                stmt = select(User).where(User.company_id == company_id, User.username == username).options(selectinload(User.user_roles).selectinload(UserRole.role))
                result = await active_session.execute(stmt)
                return Success(result.scalar_one_or_none())
        except Exception as e:
            return Failure(f"Database error fetching user by username: {e}")

    async def get_by_id_with_roles(self, user_id: UUID, session: Optional[AsyncSession] = None) -> Result[Optional[User], str]:
        """Gets a user by ID and eagerly loads their roles."""
        try:
            async with self._get_session_context(session) as active_session:
                stmt = select(User).where(User.id == user_id).options(selectinload(User.user_roles).selectinload(UserRole.role))
                result = await active_session.execute(stmt)
                return Success(result.scalar_one_or_none())
        except Exception as e:
            return Failure(f"Database error fetching user with roles: {e}")

    # NEW METHOD: Eagerly loads roles for a list of users.
    async def get_all_with_roles(self, company_id: UUID, limit: int = 100, offset: int = 0, session: Optional[AsyncSession] = None) -> Result[List[User], str]:
        """
        Fetches all users for a company with their roles eagerly loaded to prevent
        N+1 query problems and lazy-loading errors.
        """
        try:
            async with self._get_session_context(session) as active_session:
                stmt = (
                    select(self.model)
                    .where(self.model.company_id == company_id)
                    .options(selectinload(User.user_roles).selectinload(UserRole.role))
                    .order_by(self.model.username)
                    .offset(offset)
                    .limit(limit)
                )
                result = await active_session.execute(stmt)
                records = result.scalars().unique().all()
                return Success(records)
        except Exception as e:
            return Failure(f"Database error fetching all users with roles: {e}")


class RoleService(BaseService):
    """Handles database interactions for the Role model."""
    def __init__(self, core: "ApplicationCore"):
        super().__init__(core, Role)
    
    async def get_all_with_permissions(self, company_id: UUID, session: Optional[AsyncSession] = None) -> Result[List[Role], str]:
        try:
            async with self._get_session_context(session) as active_session:
                stmt = select(Role).where(Role.company_id == company_id).options(selectinload(Role.role_permissions).selectinload(RolePermission.permission))
                result = await active_session.execute(stmt)
                return Success(result.scalars().unique().all())
        except Exception as e:
            return Failure(f"Database error fetching roles: {e}")
