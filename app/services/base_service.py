# File: app/services/base_service.py
"""
Abstract Base Class for all data services (Repositories).

This provides a consistent interface and reusable logic for common CRUD
operations, reducing boilerplate code in concrete service implementations.
"""
from __future__ import annotations
from typing import TYPE_CHECKING, Type, TypeVar, List, Optional, Any
from uuid import UUID
import sqlalchemy as sa
from sqlalchemy.future import select

from app.core.result import Result, Success, Failure
from app.core.exceptions import CoreException 

if TYPE_CHECKING:
    from app.core.application_core import ApplicationCore
    from app.models.base import Base 

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

    async def get_by_id(self, record_id: UUID) -> Result[ModelType | None, str]:
        """
        Fetches a single record by its primary key (ID).
        """
        try:
            async with self.core.get_session() as session:
                stmt = select(self.model).where(self.model.id == record_id)
                result = await session.execute(stmt)
                record = result.scalar_one_or_none()
                return Success(record)
        except Exception as e:
            return Failure(f"Database error fetching {self.model.__tablename__} by ID: {e}")

    async def get_by_ids(self, record_ids: List[UUID]) -> Result[List[ModelType], str]:
        """
        Fetches multiple records by a list of primary keys (IDs).
        
        Args:
            record_ids: A list of UUIDs to fetch.
        
        Returns:
            A Success containing a list of model instances, or a Failure.
        """
        if not record_ids:
            return Success([])
        try:
            async with self.core.get_session() as session:
                stmt = select(self.model).where(self.model.id.in_(record_ids))
                result = await session.execute(stmt)
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
        **kwargs: Any
    ) -> Result[List[ModelType], str]:
        """
        Fetches all records for the model with pagination and dynamic filtering.
        
        Args:
            company_id: The UUID of the company to filter by.
            limit: Maximum number of records to return.
            offset: Number of records to skip.
            options: A list of SQLAlchemy loader options (e.g., for eager loading).
            **kwargs: Additional filter conditions where key is a column name.
        
        Returns:
            A Success containing a list of model instances, or a Failure.
        """
        try:
            async with self.core.get_session() as session:
                stmt = select(self.model).where(self.model.company_id == company_id).offset(offset).limit(limit)
                
                # FIX: Dynamically apply filters from kwargs
                for key, value in kwargs.items():
                    if hasattr(self.model, key) and value is not None:
                        stmt = stmt.where(getattr(self.model, key) == value)

                if options:
                    stmt = stmt.options(*options)

                result = await session.execute(stmt)
                records = result.scalars().unique().all()
                return Success(records)
        except Exception as e:
            return Failure(f"Database error fetching all {self.model.__tablename__}: {e}")

    async def create(self, model_instance: ModelType) -> Result[ModelType, str]:
        """
        Saves a new model instance to the database.
        """
        try:
            async with self.core.get_session() as session:
                session.add(model_instance)
                await session.flush()
                await session.refresh(model_instance)
                return Success(model_instance)
        except sa.exc.IntegrityError as e:
            return Failure(f"Data integrity error creating {self.model.__tablename__}: Duplicate entry or missing reference. Details: {e.orig}")
        except Exception as e:
            return Failure(f"Database error creating {self.model.__tablename__}: {e}")

    async def update(self, model_instance: ModelType) -> Result[ModelType, str]:
        """
        Updates an existing model instance in the database.
        """
        try:
            async with self.core.get_session() as session:
                session.add(model_instance) 
                await session.flush()
                await session.refresh(model_instance)
                return Success(model_instance)
        except Exception as e:
            return Failure(f"Database error updating {self.model.__tablename__}: {e}")

    async def delete(self, record_id: UUID) -> Result[bool, str]:
        """
        Deletes a record by its ID.
        """
        try:
            async with self.core.get_session() as session:
                stmt = select(self.model).where(self.model.id == record_id)
                result = await session.execute(stmt)
                record = result.scalar_one_or_none()
                if record:
                    await session.delete(record)
                    return Success(True)
                return Success(False)
        except sa.exc.IntegrityError as e:
            return Failure(f"Cannot delete {self.model.__tablename__}: It is referenced by other records. (Integrity error: {e.orig})")
        except Exception as e:
            return Failure(f"Database error deleting {self.model.__tablename__}: {e}")
