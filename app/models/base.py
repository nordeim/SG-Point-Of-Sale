# File: app/models/base.py
"""
Defines the base for all SQLAlchemy ORM models.
Includes a mixin for common timestamp columns.
"""
import os
from datetime import datetime
from sqlalchemy import MetaData, Column, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

# It's good practice to use a naming convention for constraints.
# This helps in generating consistent constraint names in the database.
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

# FIX: Conditionally set the schema based on a test environment variable.
# This allows the same models to work with PostgreSQL (with schema) and
# SQLite (without schema) during tests.
schema = "sgpos"
if os.environ.get("SGPOS_TEST_MODE") == "1":
    schema = None

# IMPORTANT: Specify the schema here. All tables defined using this Base will
# automatically belong to the 'sgpos' schema in production.
metadata = MetaData(naming_convention=convention, schema=schema)
Base = declarative_base(metadata=metadata)

class TimestampMixin:
    """Mixin to add created_at and updated_at columns to a model."""
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        doc="Timestamp when the record was created (UTC)"
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(), # Automatically updates on record modification
        nullable=False,
        doc="Timestamp when the record was last updated (UTC)"
    )
