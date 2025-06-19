# File: tests/unit/services/test_product_service.py
"""
Unit tests for the ProductService class.
"""
import pytest

from app.core.result import Success
from tests.factories import ProductFactory, CompanyFactory

pytestmark = pytest.mark.asyncio

class TestProductService:
    """Test suite for product-related data access services."""

    async def test_get_by_sku_success(self, test_core):
        """Verify that get_by_sku retrieves the correct product."""
        # --- Arrange ---
        company = CompanyFactory()
        # Create a product with a specific SKU to search for
        product = ProductFactory(company=company, sku="FIND-ME-123")
        # Create other products to ensure we don't accidentally fetch them
        ProductFactory.create_batch(3, company=company)

        # --- Act ---
        result = await test_core.product_service.get_by_sku(company.id, "FIND-ME-123")

        # --- Assert ---
        assert isinstance(result, Success)
        found_product = result.value
        assert found_product is not None
        assert found_product.id == product.id
        assert found_product.sku == "FIND-ME-123"

    async def test_get_by_sku_not_found(self, test_core):
        """Verify get_by_sku returns None for a non-existent SKU."""
        # --- Arrange ---
        company = CompanyFactory()
        ProductFactory.create_batch(3, company=company)

        # --- Act ---
        result = await test_core.product_service.get_by_sku(company.id, "SKU-DOES-NOT-EXIST")
        
        # --- Assert ---
        assert isinstance(result, Success)
        assert result.value is None

    async def test_search_products(self, test_core):
        """
        Verify that the search service method correctly filters products
        by name, SKU, and barcode in a case-insensitive manner.
        """
        # --- Arrange ---
        company = CompanyFactory()
        ProductFactory(company=company, name="Premium Quality Keyboard", sku="KEY-PREM-01", barcode="11111")
        ProductFactory(company=company, name="Standard Mouse", sku="MSE-STD-02", barcode="22222")
        ProductFactory(company=company, name="Premium Quality Mouse", sku="MSE-PREM-03", barcode="33333")
        ProductFactory(company=company, name="Gaming Keyboard XL", sku="KEY-GAME-04", barcode="44444")
        
        # --- Act & Assert ---

        # Search by common name part, case-insensitive
        result1 = await test_core.product_service.search(company.id, "quality")
        assert isinstance(result1, Success)
        assert len(result1.value) == 2
        assert {p.name for p in result1.value} == {"Premium Quality Keyboard", "Premium Quality Mouse"}

        # Search by SKU prefix
        result2 = await test_core.product_service.search(company.id, "KEY-")
        assert isinstance(result2, Success)
        assert len(result2.value) == 2
        assert {p.name for p in result2.value} == {"Premium Quality Keyboard", "Gaming Keyboard XL"}

        # Search by unique barcode
        result3 = await test_core.product_service.search(company.id, "33333")
        assert isinstance(result3, Success)
        assert len(result3.value) == 1
        assert result3.value[0].name == "Premium Quality Mouse"

        # Search with no matches
        result4 = await test_core.product_service.search(company.id, "nonexistent")
        assert isinstance(result4, Success)
        assert len(result4.value) == 0
