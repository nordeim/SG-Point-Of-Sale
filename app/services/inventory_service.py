# File: app/services/inventory_service.py
"""Data Access Service (Repository) for Inventory operations."""
from __future__ import annotations
from typing import TYPE_CHECKING, List, Optional
from uuid import UUID
from decimal import Decimal
import sqlalchemy as sa
from sqlalchemy.future import select

from app.core.result import Result, Success, Failure
from app.models.inventory import Inventory, StockMovement
from app.models.product import Product
from app.models.user import User
from app.models.company import Outlet # FIX: Import Outlet model for join
from app.services.base_service import BaseService

if TYPE_CHECKING:
    from app.core.application_core import ApplicationCore
    from sqlalchemy.ext.asyncio import AsyncSession

class InventoryService(BaseService):
    """
    Handles direct database interactions for inventory levels and stock movements.
    """
    def __init__(self, core: "ApplicationCore"):
        super().__init__(core, Inventory)

    async def get_stock_level(self, outlet_id: UUID, product_id: UUID, variant_id: Optional[UUID], session: Optional[AsyncSession] = None) -> Result[Decimal, str]:
        """Gets the current quantity_on_hand for a product/variant at an outlet."""
        db_session = session if session else self.core.get_session()
        try:
            async with db_session as session:
                stmt = select(Inventory.quantity_on_hand).where(
                    Inventory.outlet_id == outlet_id,
                    Inventory.product_id == product_id,
                    Inventory.variant_id == variant_id
                )
                result = await session.execute(stmt)
                quantity = result.scalar_one_or_none()
                return Success(quantity if quantity is not None else Decimal("0"))
        except Exception as e:
            return Failure(f"Database error getting stock level: {e}")

    async def adjust_stock_level(self, outlet_id: UUID, product_id: UUID, variant_id: Optional[UUID], quantity_change: Decimal, session: AsyncSession) -> Result[Decimal, str]:
        """Adjusts the stock level for a product. Must be called within an existing transaction."""
        try:
            stmt = select(Inventory).where(
                Inventory.outlet_id == outlet_id,
                Inventory.product_id == product_id,
                Inventory.variant_id == variant_id
            ).with_for_update()
            
            result = await session.execute(stmt)
            inventory_item = result.scalar_one_or_none()

            if inventory_item:
                inventory_item.quantity_on_hand += quantity_change
            else:
                inventory_item = Inventory(
                    outlet_id=outlet_id,
                    product_id=product_id,
                    variant_id=variant_id,
                    quantity_on_hand=quantity_change
                )
                session.add(inventory_item)
            
            if inventory_item.quantity_on_hand < 0:
                raise ValueError("Stock quantity cannot be negative.")

            await session.flush()
            return Success(inventory_item.quantity_on_hand)
        except ValueError as ve:
            return Failure(str(ve))
        except Exception as e:
            return Failure(f"Failed to adjust stock level: {e}")

    async def log_movement(self, movement: StockMovement, session: AsyncSession) -> Result[StockMovement, str]:
        """Logs a stock movement record within an existing transaction."""
        try:
            session.add(movement)
            await session.flush()
            return Success(movement)
        except Exception as e:
            return Failure(f"Failed to log stock movement: {e}")

    async def get_inventory_summary(self, company_id: UUID, outlet_id: Optional[UUID], limit: int, offset: int, search_term: Optional[str]) -> Result[List[dict], str]:
        """Retrieves a summary of inventory levels for display."""
        try:
            async with self.core.get_session() as session:
                stmt = select(
                    Product.id.label("product_id"),
                    Product.name.label("product_name"),
                    Product.sku,
                    Product.barcode,
                    Product.reorder_point,
                    Product.is_active,
                    Product.cost_price,
                    Product.selling_price,
                    sa.func.coalesce(Inventory.quantity_on_hand, Decimal('0.0')).label("quantity_on_hand"),
                    sa.text("(SELECT name FROM sgpos.categories WHERE id = products.category_id) AS category_name")
                ).select_from(Product).outerjoin(Inventory, sa.and_(
                    Inventory.product_id == Product.id,
                    Inventory.outlet_id == outlet_id
                )).where(Product.company_id == company_id)

                if search_term:
                    search_pattern = f"%{search_term}%"
                    stmt = stmt.where(sa.or_(
                        Product.sku.ilike(search_pattern),
                        Product.name.ilike(search_pattern)
                    ))
                
                stmt = stmt.order_by(Product.name).offset(offset).limit(limit)
                result = await session.execute(stmt)
                return Success([row._asdict() for row in result.all()])
        except Exception as e:
            return Failure(f"Database error getting inventory summary: {e}")

    async def get_movements_for_product(self, company_id: UUID, product_id: UUID) -> Result[List[dict], str]:
        """
        Retrieves the movement history for a specific product, enriched with user and product details.
        """
        try:
            async with self.core.get_session() as session:
                # FIX: Use explicit JOINs instead of a text-based subquery for better reliability.
                stmt = (
                    select(
                        StockMovement.id,
                        StockMovement.product_id,
                        StockMovement.variant_id,
                        Product.name.label("product_name"),
                        Product.sku,
                        Outlet.name.label("outlet_name"),
                        StockMovement.movement_type,
                        StockMovement.quantity_change,
                        StockMovement.reference_id,
                        StockMovement.notes,
                        User.full_name.label("created_by_user_name"),
                        StockMovement.created_at
                    )
                    .join(Product, StockMovement.product_id == Product.id)
                    .join(Outlet, StockMovement.outlet_id == Outlet.id)
                    .outerjoin(User, StockMovement.created_by_user_id == User.id)
                    .where(
                        StockMovement.company_id == company_id,
                        StockMovement.product_id == product_id
                    )
                    .order_by(StockMovement.created_at.desc())
                )
                result = await session.execute(stmt)
                return Success([row._asdict() for row in result.all()])
        except Exception as e:
            return Failure(f"Database error getting stock movements for product: {e}")
