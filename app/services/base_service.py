# File: app/services/base_service.py
"""
Abstract Base Class for all data services (Repositories).

This provides a consistent interface and reusable logic for common CRUD
operations, reducing boilerplate code in concrete service implementations.
"""
from __future__ import annotations
from typing import TYPE_CHECKING, Type, TypeVar, List, Optional, Any, AsyncIterator
from uuid import UUID
import sqlalchemy as sa
from sqlalchemy.future import select
from contextlib import asynccontextmanager

from app.core.result import Result, Success, Failure
from app.core.exceptions import CoreException 

if TYPE_CHECKING:
    from app.core.application_core import ApplicationCore
    from app.models.base import Base
    from sqlalchemy.ext.asyncio import AsyncSession

ModelType = TypeVar("ModelType", bound="Base")

class BaseService:
    """
    Implements the Repository pattern for a given SQLAlchemy model.
    Provides generic CRUD operations.
    """
    def __init__(self, core: "ApplicationCore", model: Type[ModelType]):
        if not isinstance(model, type):
            raise ValueError("Model must be a SQLAlchemy model class.")
        self.core = core
        self.model = model

    @asynccontextmanager
    async def _get_session_context(self, session: Optional[AsyncSession]) -> AsyncIterator[AsyncSession]:
        """Provides a session, either the one passed in or a new one."""
        if session:
            yield session
        else:
            async with self.core.get_session() as new_session:
                yield new_session

    async def get_by_id(self, record_id: UUID, session: Optional[AsyncSession] = None) -> Result[ModelType | None, str]:
        """Fetches a single record by its primary key (ID)."""
        try:
            async with self._get_session_context(session) as active_session:
                record = await active_session.get(self.model, record_id)
                return Success(record)
        except Exception as e:
            return Failure(f"Database error fetching {self.model.__tablename__} by ID: {e}")

    async def get_by_ids(self, record_ids: List[UUID], session: Optional[AsyncSession] = None) -> Result[List[ModelType], str]:
        """Fetches multiple records by a list of primary keys (IDs)."""
        if not record_ids:
            return Success([])
        try:
            async with self._get_session_context(session) as active_session:
                stmt = select(self.model).where(self.model.id.in_(record_ids))
                result = await active_session.execute(stmt)
                records = result.scalars().all()
                return Success(records)
        except Exception as e:
            return Failure(f"Database error fetching {self.model.__tablename__} by IDs: {e}")

    async def get_all(
        self,
        company_id: UUID,
        limit: int = 100,
        offset: int = 0,
        options: Optional[List] = None,
        session: Optional[AsyncSession] = None,
        order_by_column: Optional[str] = None,
        **filter_conditions: Any
    ) -> Result[List[ModelType], str]:
        """Fetches all records for the model with pagination and dynamic filtering."""
        try:
            async with self._get_session_context(session) as active_session:
                stmt = select(self.model).where(self.model.company_id == company_id).offset(offset).limit(limit)
                
                for key, value in filter_conditions.items():
                    if hasattr(self.model, key):
                        stmt = stmt.where(getattr(self.model, key) == value)

                if options:
                    stmt = stmt.options(*options)

                if order_by_column and hasattr(self.model, order_by_column):
                    stmt = stmt.order_by(getattr(self.model, order_by_column))

                result = await active_session.execute(stmt)
                records = result.scalars().unique().all()
                return Success(records)
        except Exception as e:
            return Failure(f"Database error fetching all {self.model.__tablename__}: {e}")

    async def create(self, model_instance: ModelType, session: Optional[AsyncSession] = None) -> Result[ModelType, str]:
        """Saves a new model instance to the database."""
        try:
            async with self._get_session_context(session) as active_session:
                active_session.add(model_instance)
                await active_session.flush()
                await active_session.refresh(model_instance)
                return Success(model_instance)
        except sa.exc.IntegrityError as e:
            return Failure(f"Data integrity error creating {self.model.__tablename__}: Duplicate entry or missing reference. Details: {e.orig}")
        except Exception as e:
            return Failure(f"Database error creating {self.model.__tablename__}: {e}")

    async def update(self, model_instance: ModelType, session: Optional[AsyncSession] = None) -> Result[ModelType, str]:
        """Updates an existing model instance in the database."""
        try:
            async with self._get_session_context(session) as active_session:
                merged_instance = await active_session.merge(model_instance)
                await active_session.flush()
                # FIX: Remove the redundant and problematic refresh call.
                # The merged_instance is already up-to-date within the transaction.
                return Success(merged_instance)
        except Exception as e:
            return Failure(f"Database error updating {self.model.__tablename__}: {e}")

    async def delete(self, record_id: UUID, session: Optional[AsyncSession] = None) -> Result[bool, str]:
        """Deletes a record by its ID."""
        try:
            async with self._get_session_context(session) as active_session:
                record = await active_session.get(self.model, record_id)
                if record:
                    await active_session.delete(record)
                    return Success(True)
                return Success(False)
        except sa.exc.IntegrityError as e:
            return Failure(f"Cannot delete {self.model.__tablename__}: It is referenced by other records. (Integrity error: {e.orig})")
        except Exception as e:
            return Failure(f"Database error deleting {self.model.__tablename__}: {e}")
