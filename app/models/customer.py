# File: app/models/customer.py
"""SQLAlchemy models for Customer entities."""
import uuid
from datetime import datetime
import sqlalchemy as sa
from sqlalchemy import Column, String, Boolean, ForeignKey, Numeric, DateTime, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin

class Customer(Base, TimestampMixin):
    """Represents a customer of the retail business."""
    __tablename__ = "customers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, doc="Unique identifier for the customer")
    company_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.companies.id", ondelete="RESTRICT"), nullable=False, index=True, doc="Foreign key to the owning company")
    customer_code = Column(String(50), nullable=False, doc="Unique identifier for the customer (e.g., loyalty card number)")
    name = Column(String(255), nullable=False, doc="Customer's full name")
    email = Column(String(255), doc="Customer's email address")
    phone = Column(String(50), doc="Customer's phone number")
    address = Column(Text, doc="Customer's address") # Added as per schema
    loyalty_points = Column(Integer, nullable=False, default=0, doc="Current loyalty points balance")
    credit_limit = Column(Numeric(19, 2), nullable=False, default=0, doc="Credit limit extended to the customer (if applicable)")
    is_active = Column(Boolean, nullable=False, default=True, doc="Indicates if the customer account is active")

    # Relationships
    company = relationship("Company", back_populates="customers", doc="The company this customer belongs to")
    sales_transactions = relationship("SalesTransaction", back_populates="customer", doc="Sales transactions made by this customer")

    __table_args__ = (
        sa.UniqueConstraint('company_id', 'customer_code', name='uq_customer_company_code'),
        sa.UniqueConstraint('company_id', 'email', name='uq_customer_company_email')
    )
