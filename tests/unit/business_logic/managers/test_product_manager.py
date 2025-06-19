# File: tests/unit/business_logic/managers/test_product_manager.py
"""
Unit tests for the ProductManager class.
"""
import pytest
from decimal import Decimal

from app.core.result import Success, Failure
from app.business_logic.dto.product_dto import ProductCreateDTO, ProductUpdateDTO
from app.models import Product
from tests.factories import ProductFactory

pytestmark = pytest.mark.asyncio

class TestProductManager:
    """Test suite for product-related business logic."""

    async def test_create_product_success(self, test_core):
        """Verify successful creation of a new product."""
        # --- Arrange ---
        dto = ProductCreateDTO(
            sku="TEST-001",
            name="Test Product",
            selling_price=Decimal("99.99"),
            cost_price=Decimal("50.00")
        )
        
        # --- Act ---
        result = await test_core.product_manager.create_product(test_core.current_company_id, dto)

        # --- Assert ---
        assert isinstance(result, Success)
        assert result.value.sku == "TEST-001"
        assert result.value.name == "Test Product"

    async def test_create_product_duplicate_sku_fails(self, test_core):
        """Verify that creating a product with a duplicate SKU fails."""
        # --- Arrange ---
        ProductFactory(company_id=test_core.current_company_id, sku="EXISTING-SKU")
        dto = ProductCreateDTO(
            sku="EXISTING-SKU",
            name="Another Product",
            selling_price=Decimal("10.00"),
            cost_price=Decimal("5.00")
        )

        # --- Act ---
        result = await test_core.product_manager.create_product(test_core.current_company_id, dto)

        # --- Assert ---
        assert isinstance(result, Failure)
        assert "already exists" in result.error

    async def test_update_product_success(self, test_core):
        """Verify successful update of a product's details."""
        # --- Arrange ---
        product = ProductFactory(company_id=test_core.current_company_id, name="Original Name")
        update_dto = ProductUpdateDTO(
            sku=product.sku, # SKU is not changed
            name="Updated Name",
            selling_price=product.selling_price,
            cost_price=product.cost_price,
            is_active=False
        )

        # --- Act ---
        result = await test_core.product_manager.update_product(product.id, update_dto)

        # --- Assert ---
        assert isinstance(result, Success)
        assert result.value.name == "Updated Name"
        assert result.value.is_active is False

    async def test_deactivate_product_success(self, test_core, db_session):
        """Verify that deactivating a product sets its is_active flag to False."""
        # --- Arrange ---
        product = ProductFactory(company_id=test_core.current_company_id, is_active=True)

        # --- Act ---
        result = await test_core.product_manager.deactivate_product(product.id)
        
        # --- Assert ---
        assert isinstance(result, Success)
        
        updated_product = await db_session.get(Product, product.id)
        assert updated_product.is_active is False

    async def test_search_products(self, test_core):
        """Verify that searching returns the correct products."""
        # --- Arrange ---
        ProductFactory(company_id=test_core.current_company_id, name="Blue Widget", sku="WID-BLUE")
        ProductFactory(company_id=test_core.current_company_id, name="Red Widget", sku="WID-RED")
        ProductFactory(company_id=test_core.current_company_id, name="Green Gadget", sku="GAD-GRN")

        # --- Act & Assert ---
        # Search by name fragment
        result_widget = await test_core.product_manager.search_products(test_core.current_company_id, "Widget")
        assert isinstance(result_widget, Success)
        assert len(result_widget.value) == 2

        # Search by SKU fragment
        result_wid = await test_core.product_manager.search_products(test_core.current_company_id, "WID")
        assert isinstance(result_wid, Success)
        assert len(result_wid.value) == 2

        # Search for specific item
        result_red = await test_core.product_manager.search_products(test_core.current_company_id, "Red Widget")
        assert isinstance(result_red, Success)
        assert len(result_red.value) == 1
        assert result_red.value[0].name == "Red Widget"
