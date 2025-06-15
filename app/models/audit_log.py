# File: app/models/audit_log.py
"""SQLAlchemy model for the Audit Logs."""
import uuid
from datetime import datetime
import sqlalchemy as sa
from sqlalchemy import Column, String, ForeignKey, DateTime, Text, BigInteger
from sqlalchemy.dialects.postgresql import UUID, INET, JSONB
from sqlalchemy.orm import relationship

from app.models.base import Base # Audit logs are immutable, typically don't have updated_at

class AuditLog(Base):
    """
    Immutable log of all significant changes or actions within the system.
    Populated by database triggers and/or application logic.
    """
    __tablename__ = "audit_logs"

    id = Column(BigInteger, primary_key=True, doc="Unique identifier for the audit log entry (auto-incrementing)") # Using BigInteger for sequence
    company_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.companies.id"), nullable=True, index=True, doc="ID of the company affected or context")
    user_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.users.id", ondelete="SET NULL"), nullable=True, index=True, doc="ID of the user who performed the action")
    action = Column(String(50), nullable=False, doc="Type of action (e.g., 'CREATE_PRODUCT', 'UPDATE_PRICE', 'LOGIN')")
    table_name = Column(String(100), nullable=False, doc="Name of the table affected") # Changed to NOT NULL as per schema.sql
    record_id = Column(UUID(as_uuid=True), nullable=False, doc="ID of the record affected") # Changed to NOT NULL as per schema.sql
    old_values = Column(JSONB, nullable=True, doc="JSONB snapshot of the record BEFORE the change")
    new_values = Column(JSONB, nullable=True, doc="JSONB snapshot of the record AFTER the change")
    ip_address = Column(INET, nullable=True, doc="IP address from where the action originated")
    # session_id UUID, # Not in current schema, but useful for grouping actions within a user session
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, doc="Timestamp when the audit log entry was created") # No updated_at for immutability

    # Relationships
    company = relationship("Company", back_populates="audit_logs", doc="The company associated with this audit log entry")
    user = relationship("User", back_populates="audit_logs", doc="The user associated with this audit log entry")

    # No `updated_at` as audit logs are immutable.
