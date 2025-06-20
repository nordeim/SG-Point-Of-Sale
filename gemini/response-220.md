This is an extremely perplexing situation. I acknowledge the `greenlet_spawn` error persists despite multiple, increasingly deep architectural fixes. The log is clean, the database transaction completes, yet the UI reports a failure. This points to a final, subtle interaction that I have missed. I will now perform the most exhaustive analysis possible, going beyond the code itself to consider the fundamental interactions between SQLAlchemy, `asyncpg`, and the `greenlet` library.

### **Final Exhaustive Analysis: The Last Resort**

1.  **Re-Confirmation of Facts:**
    *   The `greenlet_spawn` error means an `await` on a database operation is happening outside the greenlet that owns the database connection.
    *   My previous fixes have ensured that all explicit `await` calls and all implicit lazy-loads are happening inside the `async with` block.
    *   The database log shows a successful `COMMIT`.
    *   The error *only* appears in the UI, which means the `Failure` object is being correctly created and passed back through the `async_worker`.

2.  **The New Hypothesis: Post-Commit Session State**
    This leads me to a final, deep hypothesis about SQLAlchemy's internal state management. After `COMMIT`, the session is in a "closed" state. The ORM objects associated with it (`saved_sale`, `customer`, `cashier`) are "expired". It is possible that the mere act of constructing the `FinalizedSaleDTO` from these expired objects, even without accessing unloaded relationships, is somehow triggering an issue. The Pydantic `from_orm` method inspects the object's attributes, and this inspection itself might be what the `asyncpg` driver considers an invalid operation on an expired object's state.

3.  **Exploring the Ultimate Solution: Total Decoupling and Eager Loading**
    If even accessing attributes on an expired object is problematic, then the only remaining solution is to ensure the objects are not expired when we need them. How can we do this?
    *   **Option A (Flawed):** Don't close the session. This is not viable as it would lead to connection leaks and transactional ambiguity.
    *   **Option B (Complex):** Use `session.refresh()` on every object and every relationship right before exiting the `with` block. This would be a lot of manual work and still might not catch every case.
    *   **Option C (The Correct, Idiomatic SQLAlchemy Solution):** Use **eager loading options** when the objects are first loaded or created. When you have an object and you know you will need to access its relationships after the session is closed, you must tell SQLAlchemy to load that data *up front* within the transaction. For a new object like `saved_sale`, we can use `session.refresh()` with a specific load option. For existing objects like `customer` and `cashier`, we can add the option to the `get_by_id` query.

4.  **Pinpointing the Final Flaw:** The most likely source of the implicit I/O is `saved_sale.items`. Although we construct the `SalesTransactionItemDTO` list inside the `with` block, the `from_orm` call still needs to access the attributes of each `item` in the `saved_sale.items` collection. The `create_full_transaction` service method refreshes the `saved_sale` object, but it may not be refreshing the related items properly.

    Let's re-examine `sales_service.py`:
    ```python
    # sales_service.py
    async def create_full_transaction(..., session: AsyncSession):
        session.add(transaction)
        await session.flush()
        await session.refresh(transaction) # Refreshes 'transaction'
        for item in transaction.items:
            await session.refresh(item) # Refreshes each 'item'
        # ...
    ```
    This *should* work. My previous analysis concluded this was correct. If this is still failing, the problem is so deep within the async driver that a different approach is needed.

5.  **The Radical, but Definitive Plan: Pre-emptive Eager Loading.**
    Instead of relying on `refresh` after the fact, let's ensure the relationships are properly loaded from the start. For the `customer` and `cashier` objects, we can add `selectinload` options. For the `saved_sale` object, the relationships are added in memory, so they should be available. The most likely culprit remains accessing `saved_sale.items` after the `COMMIT`.

    Let's try the most robust pattern possible, which is a combination of my previous fix (extracting data to a dict) and being even more explicit about what data is being loaded. I suspect there's a subtle interaction with `customer.loyalty_points` being updated and then the `customer` object being used.

### **Final, Definitive, and Meticulous Execution Plan**

*   **Goal:** To eliminate the `greenlet_spawn` error by ensuring no part of the code, implicit or explicit, attempts I/O on an expired ORM object after its transaction has been committed. This requires a combination of eager loading and careful data extraction.
*   **Files to be Modified:**
    1.  `app/business_logic/managers/sales_manager.py` (Final structural change)
    2.  `app/services/user_service.py` (Add eager loading option)

#### **Step 1: Fortify `UserManager.get_by_id`**
*   **File:** `app/services/user_service.py`
*   **Action:** Although `BaseService.get_by_id` exists, `UserManager` sometimes needs the user's roles. We'll add a specific method in `UserService` to handle this with eager loading to prevent any possible lazy-load later.
*   **Checklist:**
    *   [ ] Open `app/services/user_service.py`.
    *   [ ] Add a new method: `async def get_by_id_with_roles(self, user_id: UUID, session: Optional[AsyncSession] = None) -> Result[Optional[User], str]:`.
    *   [ ] Inside, use `select(User).where(User.id == user_id).options(selectinload(User.user_roles).selectinload(UserRole.role))`. This will fetch the user and all their roles in a single query.
    *   [ ] Use the standard `_get_session_context` pattern.

#### **Step 2: Fortify `CustomerManager.get_by_id`**
*   **File:** `app/services/customer_service.py`
*   **Action:** Even though it has no relationships to load, we will ensure all custom methods use the session propagation pattern consistently. *Self-correction: I already did this in the last step. I will double-check that it is correct and complete.* I have re-validated my previous change to this file, and it is correct. No changes needed here.

#### **Step 3: Final Restructuring of `SalesManager.finalize_sale`**
*   **File:** `app/business_logic/managers/sales_manager.py`
*   **Action:** This is the final and most critical change. We will combine eager loading with data decoupling.
*   **Checklist:**
    *   [ ] Open `app/business_logic/managers/sales_manager.py`.
    *   [ ] Inside the `async with self.core.get_session() as session:` block:
    *   [ ] Change the call to `self.user_service.get_by_id` to the new `self.user_service.get_by_id_with_roles`. This ensures the cashier's roles are pre-loaded, even if not used, preventing any possible lazy load.
    *   [ ] After `saved_sale_result = await self.sales_service.create_full_transaction(...)`, explicitly load the items relationship using `await session.refresh(saved_sale, attribute_names=['items'])`. This forces the items to be loaded into the session *before* the commit.
    *   [ ] Immediately after refreshing, perform the data extraction into the `final_dto_data` dictionary as planned in the previous fix. This includes `[SalesTransactionItemDTO.from_orm(item) for item in saved_sale.items]`.
    *   [ ] **Crucially, after this point inside the `with` block, do not access any attributes on `saved_sale` or its related objects again.** All further logic should use the `final_dto_data` dictionary.
    *   [ ] The `return Success(finalized_dto)` statement remains *outside* the `with` block, constructed from the safe, decoupled `final_dto_data`.

This plan is my most thorough attempt. It addresses not just explicit `await`s but also the subtle, implicit `await`s that can be triggered by SQLAlchemy's lazy-loading mechanism on expired objects. It combines the best of all previous fixes.

***

### **Final Bug Fix Execution: Complete Updated Files**

#### 1. `app/services/user_service.py`

A new method is added to specifically load a user with their roles eagerly, preventing any possibility of lazy-loading later in the process.

```python
# File: app/services/user_service.py
"""Data Access Service for User and Role entities."""
from __future__ import annotations
from typing import TYPE_CHECKING, List, Optional
from uuid import UUID
import sqlalchemy as sa
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.core.result import Result, Success, Failure
from app.models import User, Role, UserRole, Permission, RolePermission
from app.services.base_service import BaseService

if TYPE_CHECKING:
    from app.core.application_core import ApplicationCore
    from sqlalchemy.ext.asyncio import AsyncSession

class UserService(BaseService):
    """Handles database interactions for the User model."""
    def __init__(self, core: "ApplicationCore"):
        super().__init__(core, User)

    async def get_by_username(self, company_id: UUID, username: str, session: Optional[AsyncSession] = None) -> Result[Optional[User], str]:
        try:
            async with self._get_session_context(session) as active_session:
                stmt = select(User).where(User.company_id == company_id, User.username == username).options(selectinload(User.user_roles).selectinload(UserRole.role))
                result = await active_session.execute(stmt)
                return Success(result.scalar_one_or_none())
        except Exception as e:
            return Failure(f"Database error fetching user by username: {e}")

    async def get_by_id_with_roles(self, user_id: UUID, session: Optional[AsyncSession] = None) -> Result[Optional[User], str]:
        """Gets a user by ID and eagerly loads their roles."""
        try:
            async with self._get_session_context(session) as active_session:
                stmt = select(User).where(User.id == user_id).options(selectinload(User.user_roles).selectinload(UserRole.role))
                result = await active_session.execute(stmt)
                return Success(result.scalar_one_or_none())
        except Exception as e:
            return Failure(f"Database error fetching user with roles: {e}")

class RoleService(BaseService):
    """Handles database interactions for the Role model."""
    def __init__(self, core: "ApplicationCore"):
        super().__init__(core, Role)
    
    async def get_all_with_permissions(self, company_id: UUID, session: Optional[AsyncSession] = None) -> Result[List[Role], str]:
        try:
            async with self._get_session_context(session) as active_session:
                stmt = select(Role).where(Role.company_id == company_id).options(selectinload(Role.role_permissions).selectinload(RolePermission.permission))
                result = await active_session.execute(stmt)
                return Success(result.scalars().unique().all())
        except Exception as e:
            return Failure(f"Database error fetching roles: {e}")
```

#### 2. `app/business_logic/managers/sales_manager.py`

The `finalize_sale` method is restructured for maximum safety. It now explicitly refreshes the newly created `sale` object to load its `items` relationship, extracts all needed data into a simple dictionary, and only constructs the final DTO *after* the transaction is safely committed.

```python
# File: app/business_logic/managers/sales_manager.py
"""
Business Logic Manager for orchestrating the entire sales workflow.
"""
from __future__ import annotations
from decimal import Decimal
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Dict, Any, Optional

from app.core.result import Result, Success, Failure
from app.business_logic.managers.base_manager import BaseManager
from app.business_logic.dto.sales_dto import SaleCreateDTO, FinalizedSaleDTO, SalesTransactionItemDTO
from app.models.sales import SalesTransaction, SalesTransactionItem, Payment
from app.models.inventory import StockMovement
from app.models.product import Product
from sqlalchemy.orm import selectinload

if TYPE_CHECKING:
    from app.core.application_core import ApplicationCore
    from app.services.sales_service import SalesService
    from app.services.product_service import ProductService
    from app.services.user_service import UserService
    from app.business_logic.managers.inventory_manager import InventoryManager
    from app.business_logic.managers.customer_manager import CustomerManager
    from sqlalchemy.ext.asyncio import AsyncSession


class SalesManager(BaseManager):
    """Orchestrates the business logic for creating and finalizing sales."""

    @property
    def sales_service(self) -> "SalesService":
        return self.core.sales_service

    @property
    def product_service(self) -> "ProductService":
        return self.core.product_service
    
    @property
    def user_service(self) -> "UserService":
        return self.core.user_service

    @property
    def inventory_manager(self) -> "InventoryManager":
        return self.core.inventory_manager

    @property
    def customer_manager(self) -> "CustomerManager":
        return self.core.customer_manager


    async def _calculate_totals(self, cart_items: List[Dict[str, Any]]) -> Result[Dict[str, Any], str]:
        """
        Internal helper to calculate subtotal, tax, and total from cart items with product details.
        """
        subtotal = Decimal("0.0")
        tax_amount = Decimal("0.0")
        items_with_details: List[Dict[str, Any]] = [] 
        
        for item_data in cart_items:
            product = item_data["product"]
            quantity = item_data["quantity"]
            unit_price = item_data["unit_price_override"] if item_data["unit_price_override"] is not None else product.selling_price
            
            line_subtotal = (quantity * unit_price).quantize(Decimal("0.01"))
            subtotal += line_subtotal
            
            item_tax = (line_subtotal * (product.gst_rate / Decimal("100.0"))).quantize(Decimal("0.01"))
            tax_amount += item_tax

            items_with_details.append({
                "product_id": product.id,
                "variant_id": item_data.get("variant_id"),
                "product_name": product.name,
                "sku": product.sku,
                "quantity": quantity,
                "unit_price": unit_price,
                "cost_price": product.cost_price,
                "line_total": line_subtotal,
                "gst_rate": product.gst_rate,
                "product": product
            })

        total_amount = subtotal + tax_amount
        return Success({
            "subtotal": subtotal.quantize(Decimal("0.01")),
            "tax_amount": tax_amount.quantize(Decimal("0.01")),
            "total_amount": total_amount.quantize(Decimal("0.01")),
            "items_with_details": items_with_details
        })

    async def finalize_sale(self, dto: SaleCreateDTO) -> Result[FinalizedSaleDTO, str]:
        """
        Processes a complete sales transaction atomically.
        """
        try:
            total_payment = sum(p.amount for p in dto.payments).quantize(Decimal("0.01"))
            
            product_ids = [item.product_id for item in dto.cart_items]
            fetched_products_result = await self.product_service.get_by_ids(product_ids)
            if isinstance(fetched_products_result, Failure):
                return fetched_products_result
            
            products_map = {p.id: p for p in fetched_products_result.value}
            if len(products_map) != len(product_ids):
                return Failure("One or more products in the cart could not be found.")

            detailed_cart_items = []
            for item_dto in dto.cart_items:
                detailed_cart_items.append({
                    "product": products_map[item_dto.product_id],
                    "quantity": item_dto.quantity,
                    "unit_price_override": item_dto.unit_price_override,
                    "variant_id": item_dto.variant_id
                })

            totals_result = await self._calculate_totals(detailed_cart_items)
            if isinstance(totals_result, Failure):
                return totals_result
            
            calculated_totals = totals_result.value
            total_amount_due = calculated_totals["total_amount"]

            if total_payment < total_amount_due:
                return Failure(f"Payment amount (S${total_payment:.2f}) is less than the total amount due (S${total_amount_due:.2f}).")

            change_due = (total_payment - total_amount_due).quantize(Decimal("0.01"))
            
            final_dto_data = {}

            async with self.core.get_session() as session:
                inventory_deduction_result = await self.inventory_manager.deduct_stock_for_sale(
                    dto.company_id, dto.outlet_id, calculated_totals["items_with_details"], dto.cashier_id, session
                )
                if isinstance(inventory_deduction_result, Failure):
                    return inventory_deduction_result
                
                stock_movements: List[StockMovement] = inventory_deduction_result.value

                transaction_number = f"SALE-{uuid.uuid4().hex[:8].upper()}"
                sale = SalesTransaction(
                    company_id=dto.company_id, outlet_id=dto.outlet_id, cashier_id=dto.cashier_id,
                    customer_id=dto.customer_id, transaction_number=transaction_number,
                    subtotal=calculated_totals["subtotal"], tax_amount=calculated_totals["tax_amount"],
                    total_amount=total_amount_due, notes=dto.notes, status="COMPLETED"
                )
                
                sale.items = [SalesTransactionItem(**{k: v for k, v in item_data.items() if k in SalesTransactionItem.__table__.columns}) for item_data in calculated_totals["items_with_details"]]
                sale.payments = [Payment(**p_info.dict()) for p_info in dto.payments]
                
                saved_sale_result = await self.sales_service.create_full_transaction(sale, session)
                if isinstance(saved_sale_result, Failure):
                    return saved_sale_result
                
                saved_sale = saved_sale_result.value
                
                for movement in stock_movements:
                    movement.reference_id = saved_sale.id
                
                if dto.customer_id:
                    loyalty_result = await self.customer_manager.add_loyalty_points_for_sale(dto.customer_id, saved_sale.total_amount, session)
                    if isinstance(loyalty_result, Failure):
                        print(f"WARNING: Failed to update loyalty points for customer {dto.customer_id}: {loyalty_result.error}")

                customer_name = None
                if dto.customer_id:
                    customer_res = await self.customer_service.get_by_id(dto.customer_id, session)
                    if isinstance(customer_res, Success) and customer_res.value:
                         customer_name = customer_res.value.name
                
                # FIX: Use the new eager-loading service method
                cashier_res = await self.user_service.get_by_id_with_roles(dto.cashier_id, session)
                cashier_name = cashier_res.value.full_name if isinstance(cashier_res, Success) and cashier_res.value else "Unknown"

                # FIX: Eagerly load the items before the session closes
                await session.refresh(saved_sale, attribute_names=['items'])
                
                final_dto_data = {
                    "transaction_id": saved_sale.id,
                    "transaction_number": saved_sale.transaction_number,
                    "transaction_date": saved_sale.transaction_date,
                    "subtotal": saved_sale.subtotal,
                    "tax_amount": saved_sale.tax_amount,
                    "discount_amount": saved_sale.discount_amount,
                    "rounding_adjustment": saved_sale.rounding_adjustment,
                    "total_amount": saved_sale.total_amount,
                    "amount_paid": total_payment,
                    "change_due": change_due,
                    "customer_name": customer_name,
                    "cashier_name": cashier_name,
                    "items": [SalesTransactionItemDTO.from_orm(item) for item in saved_sale.items]
                }

            finalized_dto = FinalizedSaleDTO(**final_dto_data)
            return Success(finalized_dto)

        except Exception as e:
            return Failure(f"A critical error occurred while finalizing the sale: {e}")
```

