# File: tests/unit/business_logic/managers/test_customer_manager.py
"""
Unit tests for the CustomerManager class.
"""
import pytest
from decimal import Decimal

from app.core.result import Success, Failure
from app.business_logic.dto.customer_dto import CustomerCreateDTO
from app.models import Customer
from tests.factories import CustomerFactory

pytestmark = pytest.mark.asyncio

class TestCustomerManager:
    """Test suite for customer-related business logic."""

    async def test_create_customer_success(self, test_core):
        """Verify successful creation of a new customer."""
        # --- Arrange ---
        dto = CustomerCreateDTO(
            customer_code="CUST-001",
            name="John Doe",
            email="john.doe@example.com"
        )
        
        # --- Act ---
        result = await test_core.customer_manager.create_customer(test_core.current_company_id, dto)

        # --- Assert ---
        assert isinstance(result, Success)
        assert result.value.customer_code == "CUST-001"
        assert result.value.name == "John Doe"

    async def test_create_customer_duplicate_code_fails(self, test_core):
        """Verify that creating a customer with a duplicate code fails."""
        # --- Arrange ---
        CustomerFactory(company_id=test_core.current_company_id, customer_code="EXISTING-CODE")
        dto = CustomerCreateDTO(customer_code="EXISTING-CODE", name="Jane Doe")

        # --- Act ---
        result = await test_core.customer_manager.create_customer(test_core.current_company_id, dto)

        # --- Assert ---
        assert isinstance(result, Failure)
        assert "already exists" in result.error

    async def test_add_loyalty_points_for_sale(self, test_core, db_session):
        """
        Verify that loyalty points are correctly calculated and added to a customer.
        Rule: 1 point per S$10 spent.
        """
        # --- Arrange ---
        customer = CustomerFactory(company_id=test_core.current_company_id, loyalty_points=50)
        sale_total = Decimal("125.50") # Should yield 12 points

        # --- Act ---
        result = await test_core.customer_manager.add_loyalty_points_for_sale(customer.id, sale_total)

        # --- Assert ---
        assert isinstance(result, Success)
        
        await db_session.refresh(customer)
        assert customer.loyalty_points == 50 + 12 # 50 initial + 12 from sale

    async def test_search_customers(self, test_core):
        """Verify that searching returns the correct customers."""
        # --- Arrange ---
        CustomerFactory(company_id=test_core.current_company_id, name="Alice Smith", email="alice@test.com")
        CustomerFactory(company_id=test_core.current_company_id, name="Bob Smith", phone="91234567")
        CustomerFactory(company_id=test_core.current_company_id, name="Charlie Brown", customer_code="CB-01")

        # --- Act & Assert ---
        # Search by common name
        result_smith = await test_core.customer_manager.search_customers(test_core.current_company_id, "Smith")
        assert isinstance(result_smith, Success)
        assert len(result_smith.value) == 2

        # Search by unique email
        result_alice = await test_core.customer_manager.search_customers(test_core.current_company_id, "alice@test.com")
        assert isinstance(result_alice, Success)
        assert len(result_alice.value) == 1
        assert result_alice.value[0].name == "Alice Smith"
