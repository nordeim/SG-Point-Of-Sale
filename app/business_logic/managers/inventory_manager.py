# File: app/business_logic/managers/inventory_manager.py
"""Business Logic Manager for orchestrating Inventory operations."""
# ... (imports from previous stages) ...
from app.models.inventory import StockMovement

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    # ... (other imports) ...

class InventoryManager(BaseManager):
    """Handles high-level inventory workflows like stock takes and adjustments."""
    
    @property
    def inventory_service(self) -> "InventoryService":
        return self.core.inventory_service

    # ... (existing methods like adjust_stock, create_purchase_order, etc.) ...
    
    async def deduct_stock_for_sale(self, company_id: UUID, outlet_id: UUID, sale_items: List[Dict[str, Any]], cashier_id: UUID, session: AsyncSession) -> Result[List[StockMovement], str]:
        """
        A dedicated method to deduct stock after a sale is finalized.
        Called by the SalesManager within its atomic transaction.
        Args:
            company_id: The UUID of the company.
            outlet_id: The UUID of the outlet where the sale occurred.
            sale_items: A list of dictionaries containing product_id, variant_id, sku, quantity.
            cashier_id: The UUID of the cashier.
            session: The SQLAlchemy AsyncSession for the current transaction.
        Returns:
            A Success containing the list of created StockMovement objects, or a Failure.
        """
        stock_movements = []
        for item_data in sale_items:
            product_id = item_data['product_id']
            variant_id = item_data.get('variant_id') # Handle optional variant
            quantity_to_deduct = item_data['quantity']
            
            # Check if this product's inventory is tracked
            # (In a real scenario, this info could be passed in sale_items)
            product_result = await self.core.product_service.get_by_id(product_id)
            if isinstance(product_result, Failure) or not product_result.value:
                return Failure(f"Could not find product {product_id} for stock deduction.")
            
            if not product_result.value.track_inventory:
                continue # Skip untracked items

            # 1. Adjust the stock level (deducting quantity)
            adjust_result = await self.inventory_service.adjust_stock_level(
                outlet_id=outlet_id,
                product_id=product_id,
                variant_id=variant_id,
                quantity_change=-quantity_to_deduct, # Negative for deduction
                session=session
            )
            if isinstance(adjust_result, Failure):
                return Failure(f"Insufficient stock for product {item_data['sku']}: {adjust_result.error}")

            # 2. Create the stock movement record for logging
            movement = StockMovement(
                company_id=company_id,
                outlet_id=outlet_id,
                product_id=product_id,
                variant_id=variant_id,
                movement_type='SALE',
                quantity_change=-quantity_to_deduct,
                notes=f"Sale processed by user {cashier_id}", # Reference to sales transaction will be added later
                created_by_user_id=cashier_id,
                reference_type="SALES_TRANSACTION"
                # reference_id will be set by SalesManager after the sales_transaction is saved.
            )
            stock_movements.append(movement)
            # Log the movement within the same session
            log_result = await self.inventory_service.log_movement(movement, session)
            if isinstance(log_result, Failure):
                return Failure(f"Failed to log sale stock movement for product {item_data['sku']}: {log_result.error}")
        
        return Success(stock_movements)
