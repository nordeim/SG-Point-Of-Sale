# File: app/business_logic/dto/company_dto.py
"""Data Transfer Objects for Company and Outlet operations."""
import uuid
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

class CompanyBaseDTO(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Legal name of the company")
    registration_number: str = Field(..., min_length=1, max_length=20, description="Singapore UEN (Unique Entity Number)")
    gst_registration_number: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None

class CompanyUpdateDTO(CompanyBaseDTO):
    """DTO for updating a company's information."""
    pass

class CompanyDTO(CompanyBaseDTO):
    """DTO representing a full company record."""
    id: uuid.UUID
    
    model_config = ConfigDict(from_attributes=True)

class OutletDTO(BaseModel):
    """DTO representing a retail outlet."""
    id: uuid.UUID
    name: str
    code: str
    is_active: bool
    
    model_config = ConfigDict(from_attributes=True)
