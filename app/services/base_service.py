# File: app/services/base_service.py
"""
Abstract Base Class for all data services (Repositories).

This provides a consistent interface and reusable logic for common CRUD
operations, reducing boilerplate code in concrete service implementations.
"""
from __future__ import annotations
from typing import TYPE_CHECKING, Type, TypeVar
from uuid import UUID
import sqlalchemy as sa
from sqlalchemy.future import select

from app.core.result import Result, Success, Failure

if TYPE_CHECKING:
    from app.core.application_core import ApplicationCore
    from app.models.base import Base

ModelType = TypeVar("ModelType", bound="Base")

class BaseService:
    """
    Implements the Repository pattern for a given SQLAlchemy model.
    """
    def __init__(self, core: "ApplicationCore", model: Type[ModelType]):
        self.core = core
        self.model = model

    async def get_by_id(self, record_id: UUID) -> Result[ModelType | None, str]:
        """Fetches a single record by its primary key (ID)."""
        try:
            async with self.core.get_session() as session:
                stmt = select(self.model).where(self.model.id == record_id)
                result = await session.execute(stmt)
                record = result.scalar_one_or_none()
                return Success(record)
        except Exception as e:
            # In a real app, log the error `e`
            return Failure("A database error occurred.")

    async def get_all(self, limit: int = 100, offset: int = 0) -> Result[list[ModelType], str]:
        """Fetches all records for the model with pagination."""
        try:
            async with self.core.get_session() as session:
                stmt = select(self.model).offset(offset).limit(limit)
                result = await session.execute(stmt)
                records = result.scalars().all()
                return Success(records)
        except Exception as e:
            return Failure("A database error occurred.")
