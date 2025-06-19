# File: tests/unit/business_logic/managers/test_inventory_manager.py
"""
Unit tests for the InventoryManager class.
"""
import pytest
from decimal import Decimal
import uuid

from app.core.result import Success, Failure
from app.business_logic.dto.inventory_dto import StockAdjustmentDTO, StockAdjustmentItemDTO, PurchaseOrderCreateDTO, PurchaseOrderItemCreateDTO
from app.models import Inventory, StockMovement, PurchaseOrder, PurchaseOrderItem
from tests.factories import ProductFactory, UserFactory, SupplierFactory

pytestmark = pytest.mark.asyncio

class TestInventoryManager:
    """Test suite for inventory-related business logic."""

    async def test_adjust_stock_success(self, test_core, db_session):
        """Verify stock adjustment correctly updates inventory and logs movement."""
        # --- Arrange ---
        user = UserFactory(company_id=test_core.current_company_id)
        product = ProductFactory(company_id=test_core.current_company_id)
        
        initial_qty = Decimal("50")
        inventory = Inventory(
            outlet_id=test_core.current_outlet_id,
            product_id=product.id,
            quantity_on_hand=initial_qty
        )
        db_session.add(inventory)
        await db_session.commit()

        counted_qty = Decimal("55.5")
        adjustment_dto = StockAdjustmentDTO(
            company_id=test_core.current_company_id,
            outlet_id=test_core.current_outlet_id,
            user_id=user.id,
            notes="Annual stock take",
            items=[StockAdjustmentItemDTO(product_id=product.id, counted_quantity=counted_qty)]
        )

        # --- Act ---
        result = await test_core.inventory_manager.adjust_stock(adjustment_dto)

        # --- Assert ---
        assert isinstance(result, Success)
        
        await db_session.refresh(inventory)
        assert inventory.quantity_on_hand == counted_qty

        movement = await db_session.get(StockMovement, {"product_id": product.id, "notes": "Annual stock take"})
        assert movement is not None
        assert movement.movement_type == 'ADJUSTMENT_IN'
        assert movement.quantity_change == counted_qty - initial_qty

    async def test_create_purchase_order_success(self, test_core, db_session):
        """Verify that a purchase order and its items are created correctly."""
        # --- Arrange ---
        product1 = ProductFactory(company_id=test_core.current_company_id, cost_price=Decimal("10.00"))
        product2 = ProductFactory(company_id=test_core.current_company_id, cost_price=Decimal("5.50"))
        supplier = SupplierFactory(company_id=test_core.current_company_id)

        po_create_dto = PurchaseOrderCreateDTO(
            company_id=test_core.current_company_id,
            outlet_id=test_core.current_outlet_id,
            supplier_id=supplier.id,
            items=[
                PurchaseOrderItemCreateDTO(product_id=product1.id, quantity_ordered=Decimal("10"), unit_cost=Decimal("9.80")),
                PurchaseOrderItemCreateDTO(product_id=product2.id, quantity_ordered=Decimal("20"), unit_cost=Decimal("5.00")),
            ]
        )
        
        # --- Act ---
        result = await test_core.inventory_manager.create_purchase_order(po_create_dto)

        # --- Assert ---
        assert isinstance(result, Success)
        po_dto = result.value
        
        expected_total = (Decimal("10") * Decimal("9.80")) + (Decimal("20") * Decimal("5.00"))
        assert po_dto.total_amount == expected_total

        po_db = await db_session.get(PurchaseOrder, po_dto.id)
        assert po_db is not None
        assert po_db.total_amount == expected_total
        
        items_count = await db_session.scalar(PurchaseOrderItem.count().where(PurchaseOrderItem.purchase_order_id == po_db.id))
        assert items_count == 2

    async def test_receive_purchase_order_items_success(self, test_core, db_session):
        """Verify receiving PO items updates stock, PO status, and logs movement."""
        # --- Arrange ---
        user = UserFactory(company_id=test_core.current_company_id)
        product = ProductFactory(company_id=test_core.current_company_id)
        supplier = SupplierFactory(company_id=test_core.current_company_id)
        
        # Create the PO
        po = PurchaseOrder(
            company_id=test_core.current_company_id,
            outlet_id=test_core.current_outlet_id,
            supplier_id=supplier.id,
            po_number="PO-TEST-123",
            status="SENT", # Must be in a receivable state
            items=[PurchaseOrderItem(product_id=product.id, quantity_ordered=10, unit_cost=10)]
        )
        db_session.add(po)
        
        # Create inventory record with zero stock
        inventory = Inventory(outlet_id=test_core.current_outlet_id, product_id=product.id, quantity_on_hand=0)
        db_session.add(inventory)
        await db_session.commit()

        items_to_receive = [{"product_id": product.id, "quantity_received": Decimal("7")}]

        # --- Act ---
        result = await test_core.inventory_manager.receive_purchase_order_items(po.id, items_to_receive, user.id)

        # --- Assert ---
        assert isinstance(result, Success)

        await db_session.refresh(po)
        await db_session.refresh(inventory)
        po_item = po.items[0]

        assert po_item.quantity_received == 7
        assert po.status == "PARTIALLY_RECEIVED"
        assert inventory.quantity_on_hand == 7

        movement = await db_session.get(StockMovement, {"reference_id": po.id, "product_id": product.id})
        assert movement is not None
        assert movement.movement_type == 'PURCHASE'
        assert movement.quantity_change == 7
        
    async def test_receive_more_than_ordered_fails(self, test_core, db_session):
        """Verify that receiving more items than ordered fails and rolls back."""
        # --- Arrange ---
        user = UserFactory(company_id=test_core.current_company_id)
        product = ProductFactory(company_id=test_core.current_company_id)
        supplier = SupplierFactory(company_id=test_core.current_company_id)
        
        po = PurchaseOrder(
            company_id=test_core.current_company_id, outlet_id=test_core.current_outlet_id,
            supplier_id=supplier.id, po_number="PO-FAIL-456", status="SENT",
            items=[PurchaseOrderItem(product_id=product.id, quantity_ordered=10, unit_cost=10)]
        )
        db_session.add(po)
        await db_session.commit()
        
        items_to_receive = [{"product_id": product.id, "quantity_received": Decimal("11")}] # Attempt to receive too many

        # --- Act ---
        result = await test_core.inventory_manager.receive_purchase_order_items(po.id, items_to_receive, user.id)
        
        # --- Assert ---
        assert isinstance(result, Failure)
        assert "exceeds ordered quantity" in result.error
        
        # Verify state was not changed
        await db_session.refresh(po)
        assert po.items[0].quantity_received == 0
        assert po.status == "SENT"
        
        movement_count = await db_session.scalar(StockMovement.count().where(StockMovement.reference_id == po.id))
        assert movement_count == 0
