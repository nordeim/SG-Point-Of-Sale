# File: tests/unit/business_logic/managers/test_company_manager.py
"""
Unit tests for the CompanyManager class.
"""
import pytest

from app.core.result import Success, Failure
from app.business_logic.dto.company_dto import CompanyUpdateDTO
from tests.factories import CompanyFactory

pytestmark = pytest.mark.asyncio

class TestCompanyManager:
    """Test suite for company-related business logic."""

    async def test_get_company_success(self, test_core):
        """Verify that company details can be successfully retrieved."""
        # --- Arrange ---
        company = CompanyFactory()

        # --- Act ---
        result = await test_core.company_manager.get_company(company.id)

        # --- Assert ---
        assert isinstance(result, Success)
        assert result.value.id == company.id
        assert result.value.name == company.name

    async def test_update_company_success(self, test_core):
        """Verify that updating a company's information is successful."""
        # --- Arrange ---
        company = CompanyFactory(name="Old Company Name")
        update_dto = CompanyUpdateDTO(
            name="New Company Name",
            registration_number=company.registration_number, # Not changing
            address="123 New Address, Singapore"
        )

        # --- Act ---
        result = await test_core.company_manager.update_company(company.id, update_dto)

        # --- Assert ---
        assert isinstance(result, Success)
        assert result.value.id == company.id
        assert result.value.name == "New Company Name"
        assert result.value.address == "123 New Address, Singapore"

    async def test_update_company_duplicate_reg_no_fails(self, test_core):
        """Verify failure when trying to update to a registration number that already exists."""
        # --- Arrange ---
        company1 = CompanyFactory(registration_number="REG123")
        company2 = CompanyFactory(registration_number="REG456")

        update_dto = CompanyUpdateDTO(
            name=company2.name,
            registration_number=company1.registration_number # Attempt to use company1's reg number
        )

        # --- Act ---
        result = await test_core.company_manager.update_company(company2.id, update_dto)

        # --- Assert ---
        assert isinstance(result, Failure)
        assert "is already in use" in result.error
