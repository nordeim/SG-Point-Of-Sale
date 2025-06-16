# File: app/services/base_service.py
"""
Abstract Base Class for all data services (Repositories).

This provides a consistent interface and reusable logic for common CRUD
operations, reducing boilerplate code in concrete service implementations.
"""
from __future__ import annotations
from typing import TYPE_CHECKING, Type, TypeVar, List
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
        Args:
            record_id: The UUID of the record to fetch.
        Returns:
            A Success containing the model instance or None if not found,
            or a Failure with an error message.
        """
        try:
            async with self.core.get_session() as session:
                stmt = select(self.model).where(self.model.id == record_id)
                result = await session.execute(stmt)
                record = result.scalar_one_or_none()
                return Success(record)
        except Exception as e:
            return Failure(f"Database error fetching {self.model.__tablename__} by ID: {e}")

    async def get_all(self, company_id: UUID, limit: int = 100, offset: int = 0) -> Result[List[ModelType], str]:
        """
        Fetches all records for the model with pagination, filtered by company_id.
        Args:
            company_id: The UUID of the company to filter by.
            limit: Maximum number of records to return.
            offset: Number of records to skip.
        Returns:
            A Success containing a list of model instances,
            or a Failure with an error message.
        """
        try:
            async with self.core.get_session() as session:
                stmt = select(self.model).where(self.model.company_id == company_id).offset(offset).limit(limit)
                result = await session.execute(stmt)
                records = result.scalars().all()
                return Success(records)
        except Exception as e:
            return Failure(f"Database error fetching all {self.model.__tablename__}: {e}")

    async def create(self, model_instance: ModelType) -> Result[ModelType, str]:
        """
        Saves a new model instance to the database.
        Args:
            model_instance: The ORM model instance to create.
        Returns:
            A Success containing the created model instance (with ID if newly generated),
            or a Failure with an error message.
        """
        try:
            async with self.core.get_session() as session:
                session.add(model_instance)
                await session.flush()  # Use flush to get generated IDs (e.g., UUID)
                await session.refresh(model_instance) # Refresh to load default values from DB
                return Success(model_instance)
        except sa.exc.IntegrityError as e:
            return Failure(f"Data integrity error creating {self.model.__tablename__}: Duplicate entry or missing reference. Details: {e.orig}")
        except Exception as e:
            return Failure(f"Database error creating {self.model.__tablename__}: {e}")

    async def update(self, model_instance: ModelType) -> Result[ModelType, str]:
        """
        Updates an existing model instance in the database.
        Args:
            model_instance: The ORM model instance to update (must have ID set).
        Returns:
            A Success containing the updated model instance,
            or a Failure with an error message.
        """
        try:
            async with self.core.get_session() as session:
                # Merge the detached instance into the current session if it's not already
                session.add(model_instance) 
                await session.flush()
                await session.refresh(model_instance)
                return Success(model_instance)
        except Exception as e:
            return Failure(f"Database error updating {self.model.__tablename__}: {e}")

    async def delete(self, record_id: UUID) -> Result[bool, str]:
        """
        Deletes a record by its ID.
        Args:
            record_id: The UUID of the record to delete.
        Returns:
            A Success indicating True if deleted, False if not found,
            or a Failure with an error message.
        """
        try:
            async with self.core.get_session() as session:
                stmt = select(self.model).where(self.model.id == record_id)
                result = await session.execute(stmt)
                record = result.scalar_one_or_none()
                if record:
                    await session.delete(record)
                    return Success(True)
                return Success(False) # Record not found
        except sa.exc.IntegrityError as e:
            return Failure(f"Cannot delete {self.model.__tablename__}: It is referenced by other records. (Integrity error: {e.orig})")
        except Exception as e:
            return Failure(f"Database error deleting {self.model.__tablename__}: {e}")
