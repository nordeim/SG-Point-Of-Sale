# File: tests/unit/business_logic/managers/test_sales_manager.py
"""
Unit tests for the SalesManager class.
"""
import pytest
from decimal import Decimal
import uuid

from app.core.result import Success, Failure
from app.business_logic.dto.sales_dto import SaleCreateDTO, CartItemDTO, PaymentInfoDTO
from app.models import SalesTransaction, StockMovement, Inventory, Product
from tests.factories import ProductFactory, UserFactory, PaymentMethodFactory

pytestmark = pytest.mark.asyncio

class TestSalesManager:
    """Test suite for sales-related business logic."""

    async def test_finalize_sale_success(self, test_core, db_session):
        """
        Verify that a successful sale:
        1. Returns a Success result with a FinalizedSaleDTO.
        2. Creates a SalesTransaction, items, and payments.
        3. Correctly deducts stock from inventory.
        4. Logs a stock movement.
        """
        # --- Arrange ---
        # 1. Create prerequisite data using factories
        cashier = UserFactory(company=None, company_id=test_core.current_company_id)
        product = ProductFactory(company=None, company_id=test_core.current_company_id)
        payment_method = PaymentMethodFactory(company=None, company_id=test_core.current_company_id)
        
        # 2. Manually create the initial inventory record
        initial_stock = 100
        inventory_item = Inventory(
            outlet_id=test_core.current_outlet_id,
            product_id=product.id,
            quantity_on_hand=Decimal(initial_stock)
        )
        db_session.add(inventory_item)
        await db_session.commit()

        # 3. Construct the DTO for the sale
        sale_dto = SaleCreateDTO(
            company_id=test_core.current_company_id,
            outlet_id=test_core.current_outlet_id,
            cashier_id=cashier.id,
            cart_items=[
                CartItemDTO(product_id=product.id, quantity=Decimal("2"))
            ],
            payments=[
                PaymentInfoDTO(payment_method_id=payment_method.id, amount=Decimal("100.00"))
            ]
        )

        # --- Act ---
        result = await test_core.sales_manager.finalize_sale(sale_dto)

        # --- Assert ---
        # 1. Check the result and its type/data
        assert isinstance(result, Success)
        finalized_sale = result.value
        assert finalized_sale.total_amount == (product.selling_price * 2) * (Decimal("1") + product.gst_rate / 100)
        assert finalized_sale.change_due >= 0

        # 2. Verify database state changes
        await db_session.refresh(inventory_item)
        assert inventory_item.quantity_on_hand == initial_stock - 2

        tx_count = await db_session.scalar(SalesTransaction.count().where(SalesTransaction.id == finalized_sale.transaction_id))
        assert tx_count == 1
        
        movement = await db_session.get(StockMovement, {"reference_id": finalized_sale.transaction_id, "product_id": product.id})
        assert movement is not None
        assert movement.movement_type == 'SALE'
        assert movement.quantity_change == -2

    async def test_finalize_sale_insufficient_payment(self, test_core, db_session):
        """Verify that a sale fails if payment is less than the total amount."""
        # --- Arrange ---
        cashier = UserFactory(company_id=test_core.current_company_id)
        product = ProductFactory(company_id=test_core.current_company_id, selling_price=Decimal("50.00"))
        payment_method = PaymentMethodFactory(company_id=test_core.current_company_id)
        
        sale_dto = SaleCreateDTO(
            company_id=test_core.current_company_id,
            outlet_id=test_core.current_outlet_id,
            cashier_id=cashier.id,
            cart_items=[CartItemDTO(product_id=product.id, quantity=1)],
            payments=[PaymentInfoDTO(payment_method_id=payment_method.id, amount=Decimal("10.00"))] # Price is >50, payment is 10
        )

        # --- Act ---
        result = await test_core.sales_manager.finalize_sale(sale_dto)
        
        # --- Assert ---
        assert isinstance(result, Failure)
        assert "less than the total amount due" in result.error

        # Verify no records were created
        tx_count = await db_session.scalar(SalesTransaction.count())
        assert tx_count == 0

    async def test_finalize_sale_insufficient_stock(self, test_core, db_session):
        """Verify that a sale fails if there is not enough stock."""
        # --- Arrange ---
        cashier = UserFactory(company_id=test_core.current_company_id)
        product = ProductFactory(company_id=test_core.current_company_id)
        payment_method = PaymentMethodFactory(company_id=test_core.current_company_id)
        
        initial_stock = 5
        inventory_item = Inventory(
            outlet_id=test_core.current_outlet_id,
            product_id=product.id,
            quantity_on_hand=Decimal(initial_stock)
        )
        db_session.add(inventory_item)
        await db_session.commit()

        sale_dto = SaleCreateDTO(
            company_id=test_core.current_company_id,
            outlet_id=test_core.current_outlet_id,
            cashier_id=cashier.id,
            cart_items=[CartItemDTO(product_id=product.id, quantity=10)], # Try to sell 10
            payments=[PaymentInfoDTO(payment_method_id=payment_method.id, amount=Decimal("1000.00"))]
        )

        # --- Act ---
        result = await test_core.sales_manager.finalize_sale(sale_dto)

        # --- Assert ---
        assert isinstance(result, Failure)
        assert "Insufficient stock" in result.error

        # Verify stock level was not changed and no transaction was created
        await db_session.refresh(inventory_item)
        assert inventory_item.quantity_on_hand == initial_stock
        
        tx_count = await db_session.scalar(SalesTransaction.count())
        assert tx_count == 0
