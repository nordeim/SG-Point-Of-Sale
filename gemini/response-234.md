I understand. It appears my previous attempts, while well-intentioned, introduced a new regression. The `greenlet_spawn` error has been replaced by a more conventional `AttributeError`, but the core function remains broken. This is a clear failure on my part to fully validate the interconnectedness of my changes. I will redouble my efforts, analyze this new error with extreme thoroughness, and provide a definitive fix.

### **Phase 1: Deep Analysis of the `AttributeError`**

This new error is much more straightforward than the `greenlet_spawn` issue, which is a positive sign that we are moving away from deep runtime conflicts to more understandable code-level bugs.

1.  **Error Message Dissection:**
    *   `Could not finalize sale: A critical error occurred while finalizing the sale:`: The error is happening in the final, overarching `try...except` block of `SalesManager.finalize_sale`.
    *   `'SalesManager' object has no attribute 'customer_service'`: This is the **exact root cause**. The code is attempting to call `self.customer_service` from within an instance of `SalesManager`, but no such attribute or property exists on the `SalesManager` object.

2.  **Code Path and Root Cause Analysis:**
    I will trace the execution within the `SalesManager.finalize_sale` method I recently modified:
    1.  The code proceeds correctly until it needs to fetch the customer's name for the receipt DTO.
    2.  The relevant line is: `customer_res = await self.customer_service.get_by_id(dto.customer_id, session)`
    3.  This line directly causes the `AttributeError`.

    Now, I must ask *why* `SalesManager` does not have `customer_service`.
    *   Looking at `app/business_logic/managers/sales_manager.py`, I can see properties for `sales_service`, `product_service`, `user_service`, `inventory_manager`, and `customer_manager`.
    *   It **does not** have a property for `customer_service`. This is an architectural choice. Managers are intended to talk to *other managers* or their *own primary service*, not to the services of other domains.
    *   The `SalesManager` correctly has a `self.customer_manager` property. The correct way to get a customer's details would be to call a method on the `CustomerManager`, like `self.customer_manager.get_customer(...)`.
    *   My previous fix incorrectly made a direct call to `self.customer_service` from within `SalesManager`. This is both an architectural violation and the direct cause of the bug. I introduced this error in my last attempt to fix the `greenlet_spawn` problem.

### **Phase 2: The Definitive Remediation Plan**

The fix is now clear, simple, and architectural. I must correct the erroneous service call and adhere to the established manager-to-manager communication pattern.

1.  **Correct the Erroneous Call:** In `app/business_logic/managers/sales_manager.py`, I will replace the incorrect call:
    *   **From:** `customer_res = await self.customer_service.get_by_id(dto.customer_id, session)`
    *   **To:** `customer_res = await self.customer_manager.get_customer(dto.customer_id, session)`

2.  **Update the Called Method:** The `CustomerManager.get_customer` method must be updated to accept the optional `session` object to ensure it participates in the `SalesManager`'s transaction. This is a continuation of the architectural refactoring that I missed in the previous step.
    *   I will modify the signature of `get_customer` in `app/business_logic/managers/customer_manager.py`.
    *   I will then ensure that this `session` is passed down to the underlying `self.customer_service.get_by_id` call.

This two-part fix is surgically precise. It corrects the `AttributeError`, restores architectural integrity, and ensures the entire operation remains within a single atomic transaction, thereby preventing any resurgence of the `greenlet_spawn` error.

### **Phase 3: Code Implementation and Validation**

I will now provide the complete, updated replacement files for the two affected managers. I will perform a line-by-line validation myself to ensure these are the only changes and that they are correct.

---
### File: `app/business_logic/managers/customer_manager.py`

This file is updated to make its `get_customer` method transaction-aware, allowing it to be safely called from other managers like `SalesManager`.

```python
# File: app/business_logic/managers/customer_manager.py
"""Business Logic Manager for Customer operations."""
from __future__ import annotations
from typing import TYPE_CHECKING, List, Optional
from uuid import UUID
from decimal import Decimal

from app.core.result import Result, Success, Failure
from app.business_logic.managers.base_manager import BaseManager
from app.business_logic.dto.customer_dto import CustomerDTO, CustomerCreateDTO, CustomerUpdateDTO
from app.models.customer import Customer

if TYPE_CHECKING:
    from app.core.application_core import ApplicationCore
    from app.services.customer_service import CustomerService
    from sqlalchemy.ext.asyncio import AsyncSession

class CustomerManager(BaseManager):
    """Orchestrates business logic for customers."""

    @property
    def customer_service(self) -> "CustomerService":
        return self.core.customer_service

    async def create_customer(self, company_id: UUID, dto: CustomerCreateDTO) -> Result[CustomerDTO, str]:
        """
        Creates a new customer.
        Business rule: Customer code and email must be unique for the company.
        """
        async with self.core.get_session() as session:
            existing_result = await self.customer_service.get_by_code(company_id, dto.customer_code, session)
            if isinstance(existing_result, Failure):
                return existing_result
            if existing_result.value is not None:
                return Failure(f"Business Rule Error: Customer with code '{dto.customer_code}' already exists.")

            if dto.email:
                email_check_result = await self.customer_service.get_by_email(company_id, dto.email, session)
                if isinstance(email_check_result, Failure):
                    return email_check_result
                if email_check_result.value is not None:
                    return Failure(f"Business Rule Error: Customer with email '{dto.email}' already exists.")

            new_customer = Customer(company_id=company_id, **dto.dict())
            
            create_result = await self.customer_service.create(new_customer, session)
            if isinstance(create_result, Failure):
                return create_result

            return Success(CustomerDTO.from_orm(create_result.value))

    async def update_customer(self, customer_id: UUID, dto: CustomerUpdateDTO) -> Result[CustomerDTO, str]:
        """Updates an existing customer."""
        async with self.core.get_session() as session:
            customer_result = await self.customer_service.get_by_id(customer_id, session)
            if isinstance(customer_result, Failure):
                return customer_result
            
            customer = customer_result.value
            if not customer:
                return Failure("Customer not found.")

            if dto.customer_code != customer.customer_code:
                existing_result = await self.customer_service.get_by_code(customer.company_id, dto.customer_code, session)
                if isinstance(existing_result, Failure):
                    return existing_result
                if existing_result.value is not None and existing_result.value.id != customer_id:
                    return Failure(f"Business Rule Error: New customer code '{dto.customer_code}' is already in use by another customer.")
            
            if dto.email and dto.email != customer.email:
                email_check_result = await self.customer_service.get_by_email(customer.company_id, dto.email, session)
                if isinstance(email_check_result, Failure):
                    return email_check_result
                if email_check_result.value is not None and email_check_result.value.id != customer_id:
                    return Failure(f"Business Rule Error: New email '{dto.email}' is already in use by another customer.")

            for field, value in dto.dict(exclude_unset=True).items():
                setattr(customer, field, value)

            update_result = await self.customer_service.update(customer, session)
            if isinstance(update_result, Failure):
                return update_result
            
            return Success(CustomerDTO.from_orm(update_result.value))

    async def get_customer(self, customer_id: UUID, session: Optional["AsyncSession"] = None) -> Result[CustomerDTO, str]:
        """Retrieves a single customer by ID."""
        # FIX: Pass the session down to the service layer.
        result = await self.customer_service.get_by_id(customer_id, session)
        if isinstance(result, Failure):
            return result
        
        customer = result.value
        if not customer:
            return Failure("Customer not found.")
            
        return Success(CustomerDTO.from_orm(customer))

    async def get_all_customers(self, company_id: UUID, limit: int = 100, offset: int = 0) -> Result[List[CustomerDTO], str]:
        """Retrieves all customers for a given company."""
        result = await self.customer_service.get_all(company_id, limit, offset)
        if isinstance(result, Failure):
            return result
        
        return Success([CustomerDTO.from_orm(c) for c in result.value])
    
    async def search_customers(self, company_id: UUID, term: str, limit: int = 100, offset: int = 0) -> Result[List[CustomerDTO], str]:
        """Searches for customers by code, name, email, or phone."""
        result = await self.customer_service.search(company_id, term, limit, offset)
        if isinstance(result, Failure):
            return result
        
        return Success([CustomerDTO.from_orm(c) for c in result.value])

    async def deactivate_customer(self, customer_id: UUID) -> Result[bool, str]:
        """Deactivates a customer (soft delete)."""
        async with self.core.get_session() as session:
            customer_result = await self.customer_service.get_by_id(customer_id, session)
            if isinstance(customer_result, Failure):
                return customer_result
            
            customer = customer_result.value
            if not customer:
                return Failure("Customer not found.")
            
            customer.is_active = False
            update_result = await self.customer_service.update(customer, session)
            if isinstance(update_result, Failure):
                return update_result
            
            return Success(True)

    async def add_loyalty_points_for_sale(self, customer_id: UUID, sale_total: Decimal, session: "AsyncSession") -> Result[int, str]:
        """
        Calculates and adds loyalty points for a completed sale.
        This method MUST be called with an existing session from a parent transaction.
        It modifies the customer object and relies on the calling transaction to commit the change.
        """
        loyalty_rate = Decimal("10.00")
        points_to_add = int(sale_total // loyalty_rate)
        
        if points_to_add <= 0:
            return Success(0)

        # FIX: Fetch the customer using the provided session.
        customer_result = await self.customer_service.get_by_id(customer_id, session)
        if isinstance(customer_result, Failure):
            return customer_result
        
        customer = customer_result.value
        if not customer:
            return Failure(f"Customer with ID {customer_id} not found.")
        
        # FIX: Modify the object. The Unit of Work in the parent session will detect
        # this change and include it in the final COMMIT. No explicit update call is needed.
        customer.loyalty_points += points_to_add
            
        return Success(customer.loyalty_points)

```
---
### File: `app/business_logic/managers/sales_manager.py`

This file is updated to correctly call the `CustomerManager` instead of the non-existent `customer_service`.

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
            # --- 1. Pre-computation & Validation Phase (before database transaction) ---
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
            
            final_dto_data = {} # Dictionary to hold pure data for the DTO

            # --- 2. Orchestration within a single atomic transaction ---
            async with self.core.get_session() as session:
                # 2a. Deduct inventory and create stock movement objects
                inventory_deduction_result = await self.inventory_manager.deduct_stock_for_sale(
                    dto.company_id, dto.outlet_id, calculated_totals["items_with_details"], dto.cashier_id, session
                )
                if isinstance(inventory_deduction_result, Failure):
                    return inventory_deduction_result
                
                stock_movements: List[StockMovement] = inventory_deduction_result.value

                # 2b. Construct SalesTransaction ORM model
                transaction_number = f"SALE-{uuid.uuid4().hex[:8].upper()}"
                sale = SalesTransaction(
                    company_id=dto.company_id, outlet_id=dto.outlet_id, cashier_id=dto.cashier_id,
                    customer_id=dto.customer_id, transaction_number=transaction_number,
                    subtotal=calculated_totals["subtotal"], tax_amount=calculated_totals["tax_amount"],
                    total_amount=total_amount_due, notes=dto.notes, status="COMPLETED"
                )
                
                sale.items = [SalesTransactionItem(**{k: v for k, v in item_data.items() if k in SalesTransactionItem.__table__.columns}) for item_data in calculated_totals["items_with_details"]]
                sale.payments = [Payment(**p_info.dict()) for p_info in dto.payments]
                
                # 2c. Persist the entire transaction graph and get the generated ID
                saved_sale_result = await self.sales_service.create_full_transaction(sale, session)
                if isinstance(saved_sale_result, Failure):
                    return saved_sale_result
                
                saved_sale = saved_sale_result.value
                
                # 2d. Back-populate the reference ID on stock movements
                for movement in stock_movements:
                    movement.reference_id = saved_sale.id
                
                # 2e. Update loyalty points if applicable
                if dto.customer_id:
                    loyalty_result = await self.customer_manager.add_loyalty_points_for_sale(dto.customer_id, saved_sale.total_amount, session)
                    if isinstance(loyalty_result, Failure):
                        print(f"WARNING: Failed to update loyalty points for customer {dto.customer_id}: {loyalty_result.error}")

                # 2f. Eagerly fetch all data needed for the final DTO before the session closes
                customer_name = None
                if dto.customer_id:
                    # FIX: Correctly call the customer_manager, not a non-existent customer_service attribute.
                    # Pass the session to ensure the operation is part of the same transaction.
                    customer_res = await self.customer_manager.get_customer(dto.customer_id, session)
                    if isinstance(customer_res, Success) and customer_res.value:
                         customer_name = customer_res.value.name
                
                cashier_res = await self.user_service.get_by_id_with_roles(dto.cashier_id, session)
                cashier_name = cashier_res.value.full_name if isinstance(cashier_res, Success) and cashier_res.value else "Unknown"

                # 2g. Eagerly load the items again after they have been flushed to the DB
                await session.refresh(saved_sale, attribute_names=['items'])
                
                # 2h. Populate the data dictionary with pure data, not ORM objects
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
            # -- End of Transaction Block: `session.commit()` is called here --

            # 3. Construct the final DTO outside the session context from pure data
            finalized_dto = FinalizedSaleDTO(**final_dto_data)
            return Success(finalized_dto)

        except Exception as e:
            # This will catch any unexpected errors during the process
            return Failure(f"A critical error occurred while finalizing the sale: {e}")
```

---
### **Phase 4: Validation and Conclusion**

I have performed a meticulous review of the changes.

*   **`app/business_logic/managers/customer_manager.py`:**
    *   **Change:** The `get_customer` method signature was updated to accept an optional `session`, which is then passed to the service layer.
    *   **Validation:** This change is **correct**. It makes the method transaction-aware, allowing it to be safely called from within another manager's transaction block, which is exactly what `SalesManager` requires.

*   **`app/business_logic/managers/sales_manager.py`:**
    *   **Change:** The line `customer_res = await self.customer_service.get_by_id(...)` has been corrected to `customer_res = await self.customer_manager.get_customer(...)`.
    *   **Validation:** This change is **correct**. It fixes the `AttributeError` by calling the existing `customer_manager` property instead of a non-existent `customer_service`. This restores the correct architectural pattern of manager-to-manager communication.

**Final Conclusion:**
The `AttributeError` was a direct result of an incorrect method call I introduced during the previous complex refactoring. By correcting this call in `SalesManager` and ensuring the `CustomerManager.get_customer` method is transaction-aware, the bug is resolved. This fix is targeted, architecturally sound, and should restore the sales finalization functionality completely, without re-introducing the `greenlet_spawn` error.

---
https://aistudio.google.com/app/prompts?state=%7B%22ids%22:%5B%221-0cd2T3QCbEo9-BuF3E34Vxd5N1MyXxL%22%5D,%22action%22:%22open%22,%22userId%22:%22103961307342447084491%22,%22resourceKeys%22:%7B%7D%7D&usp=sharing, https://drive.google.com/file/d/16cdZU41g8TlnPThn56mUbSiy8Nj7T972/view?usp=sharing, https://drive.google.com/file/d/17U22MxkkxDFFwY8VKz3xfpp4h9NwhAzp/view?usp=sharing, https://drive.google.com/file/d/1AKSukVm2yPsovA_5UpTi-RJ1rzGfX0MV/view?usp=sharing, https://drive.google.com/file/d/1ODZeIijIR5kcbGqgNsqVmT-IOzGrsJ-k/view?usp=sharing, https://drive.google.com/file/d/1TVvj8eTWvXbeDJYzeaEPE1Djr08tT21H/view?usp=sharing, https://drive.google.com/file/d/1XgceuEUl5BjQA6MvvqtAJi_N12RRy9za/view?usp=sharing, https://drive.google.com/file/d/1_LwDASE6wayDCndst3vn09eiWjCExoCR/view?usp=sharing, https://drive.google.com/file/d/1gguoJbh_lGpUUGgcht9ysjD6caWMZUa7/view?usp=sharing, https://drive.google.com/file/d/1kh2PTBGt78KU0uwZdLHmBjRg2gMFB6pa/view?usp=sharing, https://drive.google.com/file/d/1vMzJ5FDqg18_TGMitmeskTQg1vvGChOk/view?usp=sharing, https://drive.google.com/file/d/1xj34_a4v8iKjBD5Yb4PHy057i_2yZuKy/view?usp=sharing

