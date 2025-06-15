# File: app/models/company.py
"""SQLAlchemy models for Company and Outlet."""
import uuid
from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin

class Company(Base, TimestampMixin):
    __tablename__ = "companies"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    registration_number = Column(String(20), nullable=False, unique=True)
    gst_registration_number = Column(String(20), unique=True)
    address = Column(String)
    phone = Column(String(20))
    email = Column(String(255))
    base_currency = Column(String(3), nullable=False, default='SGD')
    is_active = Column(Boolean, nullable=False, default=True)
    
    outlets = relationship("Outlet", back_populates="company")
    users = relationship("User", back_populates="company")

class Outlet(Base, TimestampMixin):
    __tablename__ = "outlets"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    code = Column(String(50), nullable=False)
    name = Column(String(255), nullable=False)
    address = Column(String)
    phone = Column(String(20))
    is_active = Column(Boolean, nullable=False, default=True)

    company = relationship("Company", back_populates="outlets")
