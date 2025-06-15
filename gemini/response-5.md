```markdown
# Detailed Execution Plan: Building the SG-POS System (Production-Worthy) - Continued

This document continues the detailed execution plan for building the SG Point-of-Sale (SG-POS) system, resuming from where the previous response left off. We will proceed with completing Stage 3, and then detail the plans for Stages 4 and 5.

---

## **Stage 3: The Transactional Core - The Sales Module**

**Objective:** To build the most critical feature of the POS system: the ability to conduct a complete sales transaction from start to finish. This includes atomicity, inventory deduction, and financial record-keeping.

### **Phase 3.1: Data Transfer Objects (DTOs) for Sales**

#### **1. `app/business_logic/dto/sales_dto.py`**

*   **File Path:** `app/business_logic/dto/sales_dto.py`
*   **Purpose & Goals:** Defines the data contracts for sales transactions, including cart items, payment information, and the structure of a finalized sale receipt.
*   **Interfaces:** `CartItemDTO`, `PaymentInfoDTO`, `SaleCreateDTO`, `FinalizedSaleDTO`. All are Pydantic `BaseModel`s.
*   **Interactions:**
    *   UI (`POSView`, `PaymentDialog`) constructs `SaleCreateDTO`.
    *   `SalesManager` consumes `SaleCreateDTO` and returns `FinalizedSaleDTO`.
    *   `SalesService` works with `SalesTransaction` ORM models derived from DTOs.
*   **Code Skeleton:**
    ```python
    # File: app/business_logic/dto/sales_dto.py
    """Data Transfer Objects for Sales operations."""
    import uuid
    from decimal import Decimal
    from typing import List, Optional
    from pydantic import BaseModel, Field

    class CartItemDTO(BaseModel):
        """DTO representing an item to be added to a sales transaction."""
        product_id: uuid.UUID = Field(..., description="UUID of the product being sold")
        quantity: Decimal = Field(..., gt=Decimal("0.00"), decimal_places=4, description="Quantity of the product sold")
        # Price can be optional; if not provided, fetch the current selling price from ProductManager.
        unit_price_override: Optional[Decimal] = Field(None, ge=Decimal("0.00"), decimal_places=4, description="Optional override for unit selling price")

    class PaymentInfoDTO(BaseModel):
        """DTO representing a payment to be applied to a sale."""
        payment_method_id: uuid.UUID = Field(..., description="UUID of the payment method used")
        amount: Decimal = Field(..., gt=Decimal("0.00"), decimal_places=2, description="Amount paid using this method")
        reference_number: Optional[str] = Field(None, max_length=100, description="Reference number (e.g., card approval code)")

    class SaleCreateDTO(BaseModel):
        """DTO for creating a new sales transaction."""
        company_id: uuid.UUID = Field(..., description="UUID of the company making the sale")
        outlet_id: uuid.UUID = Field(..., description="UUID of the outlet where the sale occurred")
        cashier_id: uuid.UUID = Field(..., description="UUID of the cashier processing the sale")
        customer_id: Optional[uuid.UUID] = Field(None, description="UUID of the customer (optional)")
        cart_items: List[CartItemDTO] = Field(..., min_items=1, description="List of items in the cart")
        payments: List[PaymentInfoDTO] = Field(..., min_items=1, description="List of payments applied to the sale")
        notes: Optional[str] = Field(None, description="Any notes for the sales transaction")

    class FinalizedSaleDTO(BaseModel):
        """DTO representing a completed sale, suitable for generating a receipt."""
        transaction_id: uuid.UUID = Field(..., description="UUID of the finalized sales transaction")
        transaction_number: str = Field(..., description="Unique transaction number")
        transaction_date: datetime.datetime = Field(..., description="Date and time of the transaction")
        
        # Financial summary
        subtotal: Decimal = Field(..., decimal_places=2, description="Subtotal before tax and discount")
        tax_amount: Decimal = Field(..., decimal_places=2, description="Total tax amount")
        discount_amount: Decimal = Field(..., decimal_places=2, description="Total discount amount")
        rounding_adjustment: Decimal = Field(..., decimal_places=2, description="Rounding adjustment for total")
        total_amount: Decimal = Field(..., decimal_places=2, description="Final total amount due")
        
        # Payment details
        amount_paid: Decimal = Field(..., decimal_places=2, description="Total amount paid by customer")
        change_due: Decimal = Field(..., decimal_places=2, description="Change given back to customer")

        # Customer and Cashier info (optional for receipt)
        customer_name: Optional[str] = Field(None, description="Name of the customer (if associated)")
        cashier_name: str = Field(..., description="Name of the cashier who processed the sale")

        # Line items for receipt
        items: List["SalesTransactionItemDTO"] = Field(..., description="List of items in the transaction")

    class SalesTransactionItemDTO(BaseModel):
        """DTO for a single item within a finalized sales transaction."""
        product_id: uuid.UUID
        product_name: str
        sku: str
        quantity: Decimal = Field(..., decimal_places=4)
        unit_price: Decimal = Field(..., decimal_places=4)
        line_total: Decimal = Field(..., decimal_places=2)
        gst_rate: Decimal = Field(..., decimal_places=2) # GST rate at the time of sale
        
        class Config:
            orm_mode = True

    # Forward references for Pydantic (if needed for recursive types, not strictly needed here for this example)
    FinalizedSaleDTO.update_forward_refs() # For Pydantic v1.x; v2+ handles this automatically
    ```
*   **Acceptance Checklist:**
    *   [ ] `CartItemDTO`, `PaymentInfoDTO`, `SaleCreateDTO`, `FinalizedSaleDTO`, `SalesTransactionItemDTO` are defined.
    *   [ ] All necessary fields for sales, payments, and receipt generation are included.
    *   [ ] Fields have correct Pydantic types, validation (e.g., `gt`, `ge`), and `decimal_places` for `Decimal` types.
    *   [ ] `FinalizedSaleDTO` includes `transaction_id`, `transaction_number`, `total_amount`, `amount_paid`, `change_due`, `customer_name`, `cashier_name`, and a list of `SalesTransactionItemDTO`.
    *   [ ] `SalesTransactionItemDTO` includes relevant product details and financial figures.
    *   [ ] Docstrings are clear and comprehensive.

### **Phase 3.2: Data Access Layer for Sales (`app/services/`)**

This phase creates services for sales transactions and payment methods.

#### **1. `app/services/sales_service.py`**

*   **File Path:** `app/services/sales_service.py`
*   **Purpose & Goals:** Handles the atomic persistence of sales data (SalesTransaction and its items).
*   **Interfaces:** `SalesService(core: ApplicationCore)`. Methods: `async create_full_transaction(transaction: SalesTransaction)`.
*   **Interactions:** Uses `self.core.get_session()` for database interaction. Called by `SalesManager`. Persists `SalesTransaction` ORM models.
*   **Code Skeleton:**
    ```python
    # File: app/services/sales_service.py
    """Data Access Service (Repository) for Sales entities."""
    from __future__ import annotations
    from typing import TYPE_CHECKING
    import sqlalchemy as sa # Import sa for specific exceptions

    from app.core.result import Result, Success, Failure
    from app.models.sales import SalesTransaction, SalesTransactionItem # Import ORM models
    from app.models.payment import Payment # Import Payment ORM model
    from app.services.base_service import BaseService # Inherit from BaseService for common CRUD

    if TYPE_CHECKING:
        from app.core.application_core import ApplicationCore

    class SalesService(BaseService):
        """
        Handles all database interactions for sales-related models.
        It encapsulates the atomic persistence of SalesTransaction and its related entities.
        """

        def __init__(self, core: "ApplicationCore"):
            super().__init__(core, SalesTransaction) # Initialize BaseService for SalesTransaction model

        async def create_full_transaction(self, transaction: SalesTransaction) -> Result[SalesTransaction, str]:
            """
            Saves a complete SalesTransaction object, including its items and payments,
            within the current session.
            This method assumes it is being called within an existing session context
            managed by the calling manager (e.g., SalesManager).
            Args:
                transaction: The complete SalesTransaction ORM instance to save.
            Returns:
                A Success containing the saved SalesTransaction, or a Failure with an error.
            """
            try:
                # The session is managed by the calling manager's `get_session` context,
                # ensuring atomicity of the entire operation.
                # `session.add(transaction)` automatically adds related objects (items, payments)
                # if relationships are configured with cascade="all, delete-orphan"
                async with self.core.get_session() as session: # Ensure the session is managed by the service
                    session.add(transaction)
                    await session.flush() # Flush to get any generated IDs (like transaction_id)
                    await session.refresh(transaction) # Refresh the transaction instance to get generated fields

                    # If related items/payments have defaults or triggers, they might need refreshing too
                    for item in transaction.items:
                        await session.refresh(item)
                    for payment in transaction.payments:
                        await session.refresh(payment)
                        
                    # All operations are part of this single session, which will be committed by the context manager.
                    return Success(transaction)
            except sa.exc.IntegrityError as e:
                return Failure(f"Data integrity error creating sales transaction: {e.orig}")
            except Exception as e:
                return Failure(f"Database error saving full transaction: {e}")

        # TODO: Add methods to retrieve sales transactions by various criteria (e.g., date range, customer, number)
        # async def get_transactions_by_date_range(self, company_id: uuid.UUID, start_date: datetime, end_date: datetime) -> Result[List[SalesTransaction], str]:
        #     # Example for reporting
        #     pass
    ```
*   **Acceptance Checklist:**
    *   [ ] `SalesService` inherits from `BaseService` (for `SalesTransaction` model).
    *   [ ] `create_full_transaction` method is implemented.
    *   [ ] `create_full_transaction` uses `async with self.core.get_session()` to manage the session atomically.
    *   [ ] It adds the `SalesTransaction` instance to the session and flushes/refreshes.
    *   [ ] Correctly handles `IntegrityError` and general exceptions, returning `Result`.
    *   [ ] Docstrings are clear.

#### **2. `app/services/payment_service.py`** (New File)

*   **File Path:** `app/services/payment_service.py`
*   **Purpose & Goals:** Handles persistence operations specifically for Payment Methods and Payments.
*   **Interfaces:** `PaymentService(core: ApplicationCore)`. Methods: `async get_payment_method_by_name(company_id, name)`, `async get_all_payment_methods(company_id)`.
*   **Interactions:** Inherits from `BaseService` (for `PaymentMethod` or `Payment`). Used by `SalesManager` to manage payment-related data.
*   **Code Skeleton:**
    ```python
    # File: app/services/payment_service.py
    """Data Access Service (Repository) for Payment methods and Payments."""
    from __future__ import annotations
    from typing import TYPE_CHECKING, List
    from uuid import UUID
    import sqlalchemy as sa
    from sqlalchemy.future import select

    from app.core.result import Result, Success, Failure
    from app.models.payment import PaymentMethod, Payment # Import ORM models
    from app.services.base_service import BaseService

    if TYPE_CHECKING:
        from app.core.application_core import ApplicationCore

    class PaymentMethodService(BaseService):
        """
        Handles database interactions for PaymentMethod models.
        Inherits generic CRUD from BaseService.
        """
        def __init__(self, core: "ApplicationCore"):
            super().__init__(core, PaymentMethod)

        async def get_by_name(self, company_id: UUID, name: str) -> Result[PaymentMethod | None, str]:
            """Fetches a payment method by its name for a given company."""
            try:
                async with self.core.get_session() as session:
                    stmt = select(PaymentMethod).where(
                        PaymentMethod.company_id == company_id,
                        PaymentMethod.name == name
                    )
                    result = await session.execute(stmt)
                    method = result.scalar_one_or_none()
                    return Success(method)
            except Exception as e:
                return Failure(f"Database error fetching payment method by name '{name}': {e}")
        
        async def get_all_active_methods(self, company_id: UUID) -> Result[List[PaymentMethod], str]:
            """Fetches all active payment methods for a given company."""
            try:
                async with self.core.get_session() as session:
                    stmt = select(PaymentMethod).where(
                        PaymentMethod.company_id == company_id,
                        PaymentMethod.is_active == True
                    )
                    result = await session.execute(stmt)
                    methods = result.scalars().all()
                    return Success(methods)
            except Exception as e:
                return Failure(f"Database error fetching active payment methods: {e}")

    # Although Payments are typically part of a SalesTransaction's lifecycle,
    # having a separate service for direct Payment operations (if any) can be useful.
    # For now, `SalesService` handles Payment persistence as part of `SalesTransaction`.
    # This class might be expanded if payments need to be managed independently later.
    class PaymentService(BaseService):
        """
        Handles database interactions for Payment models.
        For now, mostly used for retrieving, not creating, as creation is part of SalesService.
        """
        def __init__(self, core: "ApplicationCore"):
            super().__init__(core, Payment)

        # TODO: Add methods for retrieving payments, e.g., by sales_transaction_id
    ```
*   **Acceptance Checklist:**
    *   [ ] `PaymentMethodService` class is created, inheriting from `BaseService` for `PaymentMethod`.
    *   [ ] `get_by_name` and `get_all_active_methods` methods are implemented.
    *   [ ] A placeholder `PaymentService` for `Payment` model is defined, even if its main methods are for future use.
    *   [ ] All methods use `async with self.core.get_session()` and return `Result`.
    *   [ ] Type hinting is complete.

### **Phase 3.3: Business Logic for Sales (`app/business_logic/managers/`)**

This phase implements the complex orchestration logic for sales transactions.

#### **1. `app/business_logic/managers/sales_manager.py`**

*   **File Path:** `app/business_logic/managers/sales_manager.py`
*   **Purpose & Goals:** Orchestrates the entire sales workflow, from validating cart items and payments to atomically deducting inventory, creating transaction records, and updating loyalty points.
*   **Interfaces:** `SalesManager(core: ApplicationCore)`. Methods: `async finalize_sale(dto: SaleCreateDTO)`. Returns `Result[FinalizedSaleDTO, str]`.
*   **Interactions:**
    *   Lazy-loads `ProductService`, `SalesService`, `InventoryManager`, `CustomerManager`, `UserService` (for cashier name).
    *   Consumes `SaleCreateDTO`.
    *   Creates `SalesTransaction` and `Payment` ORM models.
    *   Calls `inventory_manager.deduct_stock_for_sale`, `customer_manager.add_loyalty_points_for_sale`, `sales_service.create_full_transaction`.
    *   **Ensures atomicity** using `async with self.core.get_session() as session:`.
*   **Code Skeleton:**
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
    from app.business_logic.dto.sales_dto import SaleCreateDTO, FinalizedSaleDTO, CartItemDTO, SalesTransactionItemDTO
    from app.models.sales import SalesTransaction, SalesTransactionItem
    from app.models.payment import Payment # Import Payment ORM model
    from app.models.product import Product # For fetching product data


    if TYPE_CHECKING:
        from app.core.application_core import ApplicationCore
        from app.services.sales_service import SalesService
        from app.services.product_service import ProductService
        from app.services.payment_service import PaymentMethodService
        from app.services.user_service import UserService
        from app.business_logic.managers.inventory_manager import InventoryManager
        from app.business_logic.managers.customer_manager import CustomerManager


    class SalesManager(BaseManager):
        """Orchestrates the business logic for creating and finalizing sales."""

        @property
        def sales_service(self) -> "SalesService":
            return self.core.sales_service

        @property
        def product_service(self) -> "ProductService":
            return self.core.product_service

        @property
        def payment_method_service(self) -> "PaymentMethodService":
            return self.core.payment_method_service
        
        @property
        def inventory_manager(self) -> "InventoryManager":
            return self.core.inventory_manager

        @property
        def customer_manager(self) -> "CustomerManager":
            return self.core.customer_manager

        @property
        def user_service(self) -> "UserService":
            return self.core.user_service


        async def _calculate_totals(self, company_id: uuid.UUID, cart_items: List[CartItemDTO]) -> Result[dict, str]:
            """
            Internal helper to calculate subtotal, tax, and total from cart items.
            This fetches real product details to get prices and tax rates.
            Args:
                company_id: The UUID of the company.
                cart_items: List of CartItemDTOs.
            Returns:
                A Success containing a dictionary with 'subtotal', 'tax_amount', 'total_amount', and 'items_with_details',
                or a Failure.
            """
            subtotal = Decimal("0.0")
            tax_amount = Decimal("0.0")
            # This list will hold product details needed for SalesTransactionItem creation
            items_with_details: List[Dict[str, Any]] = [] 
            
            for item_dto in cart_items:
                product_result = await self.product_service.get_by_id(item_dto.product_id)
                if isinstance(product_result, Failure):
                    return Failure(f"Product lookup error: {product_result.error}")
                if product_result.value is None:
                    return Failure(f"Product with ID '{item_dto.product_id}' not found.")
                
                product = product_result.value

                # Determine unit price: override if provided, else use product's selling price
                unit_price = item_dto.unit_price_override if item_dto.unit_price_override is not None else product.selling_price
                
                if unit_price <= 0: # Basic check for valid price
                    return Failure(f"Invalid unit price for product '{product.name}'.")

                line_subtotal = item_dto.quantity * unit_price
                subtotal += line_subtotal
                
                # Calculate tax for this item based on product's GST rate
                item_tax = line_subtotal * (product.gst_rate / Decimal("100.0"))
                tax_amount += item_tax

                items_with_details.append({
                    "product_id": product.id,
                    "product_name": product.name, # For receipt DTO
                    "sku": product.sku, # For receipt DTO
                    "quantity": item_dto.quantity,
                    "unit_price": unit_price,
                    "cost_price": product.cost_price, # Store cost price at time of sale
                    "line_total": line_subtotal.quantize(Decimal("0.01")), # Round to 2 decimal places
                    "gst_rate": product.gst_rate # Store GST rate at time of sale
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
            This is the core orchestration method.
            Args:
                dto: SaleCreateDTO containing all details for the sale.
            Returns:
                A Success with a FinalizedSaleDTO, or a Failure with an error message.
            """
            # --- 1. Initial Validation & Calculation Phase ---
            total_payment = sum(p.amount for p in dto.payments)
            
            totals_result = await self._calculate_totals(dto.company_id, dto.cart_items)
            if isinstance(totals_result, Failure):
                return totals_result # Propagate calculation/product lookup errors
            
            calculated_totals = totals_result.value
            total_amount_due = calculated_totals["total_amount"]

            if total_payment < total_amount_due:
                return Failure(f"Payment amount (S${total_payment:.2f}) is less than the total amount due (S${total_amount_due:.2f}).")

            change_due = total_payment - total_amount_due
            # Apply rounding adjustment for final amount due if needed (e.g., cash rounding)
            # For simplicity, we'll just round the change due
            change_due = change_due.quantize(Decimal("0.01"))


            # --- 2. Orchestration within a single atomic transaction ---
            # All critical operations must occur within one database session to ensure atomicity.
            try:
                # The session context manager provided by ApplicationCore ensures commit/rollback.
                async with self.core.get_session() as session:
                    # --- 2a. Check and deduct inventory ---
                    # This method must perform atomic checks and deductions for all items.
                    inventory_deduction_result = await self.inventory_manager.deduct_stock_for_sale(
                        company_id=dto.company_id,
                        outlet_id=dto.outlet_id,
                        sale_items=calculated_totals["items_with_details"], # Pass detailed items
                        cashier_id=dto.cashier_id,
                        session=session # Pass the current session for atomicity
                    )
                    if isinstance(inventory_deduction_result, Failure):
                        # If inventory fails, the session will be rolled back by `get_session` context manager
                        return Failure(f"Inventory deduction failed: {inventory_deduction_result.error}")
                    

                    # --- 2b. Construct SalesTransaction ORM model and related entities ---
                    # Generate a unique transaction number (a robust generation logic might be more complex)
                    transaction_number = f"SALE-{uuid.uuid4().hex[:8].upper()}"

                    sale = SalesTransaction(
                        company_id=dto.company_id,
                        outlet_id=dto.outlet_id,
                        cashier_id=dto.cashier_id,
                        customer_id=dto.customer_id,
                        transaction_number=transaction_number,
                        transaction_date=datetime.utcnow(),
                        subtotal=calculated_totals["subtotal"],
                        tax_amount=calculated_totals["tax_amount"],
                        discount_amount=Decimal("0.00"), # TODO: Implement discount logic
                        rounding_adjustment=Decimal("0.00"), # TODO: Implement rounding logic
                        total_amount=total_amount_due,
                        status='COMPLETED',
                        notes=dto.notes
                    )
                    
                    # Create SalesTransactionItem ORM instances
                    for item_data in calculated_totals["items_with_details"]:
                        sale.items.append(SalesTransactionItem(
                            product_id=item_data["product_id"],
                            quantity=item_data["quantity"],
                            unit_price=item_data["unit_price"],
                            cost_price=item_data["cost_price"],
                            line_total=item_data["line_total"],
                        ))
                    
                    # Create Payment ORM instances
                    for payment_info in dto.payments:
                        # Validate payment method exists and is active (optional, could be in UI or prior manager)
                        # payment_method_result = await self.payment_method_service.get_by_id(payment_info.payment_method_id)
                        # if isinstance(payment_method_result, Failure) or payment_method_result.value is None:
                        #     raise Exception(f"Payment method {payment_info.payment_method_id} not found.")

                        sale.payments.append(Payment(
                            payment_method_id=payment_info.payment_method_id,
                            amount=payment_info.amount,
                            reference_number=payment_info.reference_number
                        ))
                    
                    # --- 2c. Persist the entire transaction atomically via SalesService ---
                    # Pass the current session to the service to ensure it's part of the same transaction
                    saved_sale_result = await self.sales_service.create_full_transaction(sale)
                    if isinstance(saved_sale_result, Failure):
                        # The context manager handles rollback
                        return Failure(f"Failed to save transaction: {saved_sale_result.error}")
                    
                    saved_sale = saved_sale_result.value

                    # --- 2d. Update customer loyalty points (if customer exists) ---
                    if dto.customer_id:
                        loyalty_result = await self.customer_manager.add_loyalty_points_for_sale(
                            dto.customer_id, saved_sale.total_amount
                        )
                        if isinstance(loyalty_result, Failure):
                            # This is a non-critical failure, can log but not roll back whole sale.
                            # For strict atomicity, could raise, but loyalty can be reconciled later.
                            print(f"WARNING: Failed to update loyalty points for customer {dto.customer_id}: {loyalty_result.error}")
                            # For now, we will not return Failure for this.
                    
                    # --- 2e. Get cashier name for receipt DTO ---
                    cashier_user_result = await self.user_service.get_by_id(dto.cashier_id)
                    cashier_name = cashier_user_result.value.full_name if isinstance(cashier_user_result, Success) and cashier_user_result.value else "Unknown Cashier"

                    # --- 2f. Prepare FinalizedSaleDTO for receipt/UI feedback ---
                    finalized_dto_items = [
                        SalesTransactionItemDTO(
                            product_id=item.product_id,
                            product_name=item_data['product_name'], # From calculated_totals
                            sku=item_data['sku'],
                            quantity=item.quantity,
                            unit_price=item.unit_price,
                            line_total=item.line_total,
                            gst_rate=item_data['gst_rate'] # From calculated_totals
                        )
                        for item, item_data in zip(saved_sale.items, calculated_totals["items_with_details"])
                    ]

                    finalized_dto = FinalizedSaleDTO(
                        transaction_id=saved_sale.id,
                        transaction_number=saved_sale.transaction_number,
                        transaction_date=saved_sale.transaction_date,
                        subtotal=saved_sale.subtotal,
                        tax_amount=saved_sale.tax_amount,
                        discount_amount=saved_sale.discount_amount,
                        rounding_adjustment=saved_sale.rounding_adjustment,
                        total_amount=saved_sale.total_amount,
                        amount_paid=total_payment,
                        change_due=change_due,
                        customer_name= (await self.customer_manager.get_customer(dto.customer_id)).value.name if dto.customer_id else None,
                        cashier_name=cashier_name,
                        items=finalized_dto_items
                    )
                    
                    return Success(finalized_dto)

            except Exception as e:
                # Log the full error `e` for debugging
                print(f"CRITICAL ERROR in finalize_sale: {e}", file=sys.stderr)
                # The `get_session` context manager handles the rollback.
                return Failure(f"A critical error occurred while finalizing the sale: {e}")
    ```
*   **Acceptance Checklist:**
    *   [ ] `SalesManager` inherits from `BaseManager`.
    *   [ ] All necessary services and managers are lazy-loaded via `@property` decorators.
    *   [ ] `_calculate_totals` is fully implemented to fetch real product data, calculate subtotal, tax, and total, and store item details.
    *   [ ] `finalize_sale` method orchestrates the entire sales process.
    *   [ ] **Crucially**, `async with self.core.get_session() as session:` is used to ensure the entire operation is atomic.
    *   [ ] Calls `inventory_manager.deduct_stock_for_sale` (passing the session) and handles its `Result`.
    *   [ ] Calls `sales_service.create_full_transaction` (passing the ORM instance).
    *   [ ] Calls `customer_manager.add_loyalty_points_for_sale` (if customer exists).
    *   [ ] Fetches cashier name for `FinalizedSaleDTO`.
    *   [ ] Constructs `SalesTransaction`, `SalesTransactionItem`, and `Payment` ORM models from DTOs and calculated data.
    *   [ ] Correctly handles payment validation (total amount paid vs. total amount due).
    *   [ ] Returns `Result[FinalizedSaleDTO, str]` with all necessary details for a receipt.
    *   [ ] Comprehensive error handling and logging (even if print for now) are present.
    *   [ ] Type hinting is complete.

### **Phase 3.4: Point-of-Sale UI (`app/ui/`)**

This phase implements the main cashier-facing UI and the payment dialog.

#### **1. `app/ui/views/pos_view.py`**

*   **File Path:** `app/ui/views/pos_view.py`
*   **Purpose & Goals:** The primary Point-of-Sale (POS) view for cashiers. It allows scanning/searching products, adding them to a cart (dynamically displayed), calculating totals, and initiating the payment process.
*   **Interfaces:** `POSView(core: ApplicationCore)`.
*   **Interactions:**
    *   Receives `ApplicationCore`.
    *   Manages a `CartTableModel` (`QAbstractTableModel`).
    *   Calls `product_manager.search_products` for product lookup via `async_worker.run_task()`.
    *   Launches `PaymentDialog` for payment processing.
    *   Calls `sales_manager.finalize_sale` via `async_worker.run_task()`.
    *   Displays cart contents, totals, and feedback via `QMessageBox`.
*   **Code Skeleton:**
    ```python
    # File: app/ui/views/pos_view.py
    """The primary Point-of-Sale (POS) view."""
    from __future__ import annotations
    import uuid
    from decimal import Decimal
    from typing import List, Any, Optional, Dict, Tuple

    from PySide6.QtWidgets import (
        QWidget, QHBoxLayout, QVBoxLayout, QLineEdit,
        QTableView, QPushButton, QLabel, QFormLayout, QMessageBox, QHeaderView
    )
    from PySide6.QtCore import Slot, Signal, QAbstractTableModel, QModelIndex, Qt, QObject

    from app.core.application_core import ApplicationCore
    from app.core.result import Result, Success, Failure
    from app.business_logic.dto.sales_dto import CartItemDTO, FinalizedSaleDTO, SalesTransactionItemDTO # For DTOs
    from app.business_logic.dto.product_dto import ProductDTO # For product lookup
    from app.ui.dialogs.payment_dialog import PaymentDialog # Import the PaymentDialog
    from app.core.async_bridge import AsyncWorker

    class CartItemDisplay(QObject):
        """Helper class to hold and represent cart item data for the TableModel."""
        def __init__(self, product_id: uuid.UUID, sku: str, name: str, quantity: Decimal, unit_price: Decimal, gst_rate: Decimal, parent: Optional[QObject] = None):
            super().__init__(parent)
            self.product_id = product_id
            self.sku = sku
            self.name = name
            self.quantity = quantity
            self.unit_price = unit_price
            self.gst_rate = gst_rate # Store original GST rate
            self.line_subtotal = (quantity * unit_price).quantize(Decimal("0.01"))
            self.line_tax = (self.line_subtotal * (gst_rate / Decimal("100.0"))).quantize(Decimal("0.01"))
            self.line_total = (self.line_subtotal + self.line_tax).quantize(Decimal("0.01"))

        def to_cart_item_dto(self) -> CartItemDTO:
            """Converts to CartItemDTO for the manager."""
            return CartItemDTO(
                product_id=self.product_id,
                quantity=self.quantity,
                unit_price_override=self.unit_price # Use current unit price as override if changed
            )

    class CartTableModel(QAbstractTableModel):
        """A Qt Table Model for displaying items in the sales cart."""
        
        HEADERS = ["SKU", "Name", "Qty", "Unit Price", "GST", "Line Total"]
        COLUMN_QTY = 2 # Column index for Quantity

        def __init__(self, parent: Optional[QObject] = None):
            super().__init__(parent)
            self._items: List[CartItemDisplay] = []
            self.cart_changed = Signal() # Signal to notify POSView about cart changes

        def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
            return len(self._items)

        def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
            return len(self.HEADERS)

        def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
            if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
                return self.HEADERS[section]
            return None

        def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
            if not index.isValid():
                return None
            
            item = self._items[index.row()]
            col = index.column()

            if role == Qt.ItemDataRole.DisplayRole:
                if col == 0: return item.sku
                if col == 1: return item.name
                if col == 2: return str(item.quantity)
                if col == 3: return f"S${item.unit_price:.2f}"
                if col == 4: return f"{item.gst_rate:.2f}%"
                if col == 5: return f"S${item.line_total:.2f}"
            
            if role == Qt.ItemDataRole.EditRole and col == self.COLUMN_QTY:
                return str(item.quantity) # For editing quantity

            if role == Qt.ItemDataRole.TextAlignmentRole:
                if col in [2, 3, 4, 5]: # Qty, Price, GST, Line Total
                    return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            
            return None

        def setData(self, index: QModelIndex, value: Any, role: int = Qt.ItemDataRole.EditRole) -> bool:
            if role == Qt.ItemDataRole.EditRole and index.column() == self.COLUMN_QTY:
                try:
                    new_qty = Decimal(value)
                    if new_qty <= 0:
                        # Consider removing item if quantity is 0 or negative
                        self.remove_item_at_row(index.row())
                        return True
                    
                    item = self._items[index.row()]
                    if item.quantity != new_qty:
                        item.quantity = new_qty
                        # Recalculate derived properties
                        item.line_subtotal = (item.quantity * item.unit_price).quantize(Decimal("0.01"))
                        item.line_tax = (item.line_subtotal * (item.gst_rate / Decimal("100.0"))).quantize(Decimal("0.01"))
                        item.line_total = (item.line_subtotal + item.line_tax).quantize(Decimal("0.01"))
                        
                        self.dataChanged.emit(index, self.createIndex(index.row(), self.columnCount() - 1))
                        self.cart_changed.emit() # Notify view about total change
                        return True
                except (ValueError, TypeError):
                    return False
            return False

        def flags(self, index: QModelIndex) -> Qt.ItemFlag:
            flags = super().flags(index)
            if index.column() == self.COLUMN_QTY:
                flags |= Qt.ItemFlag.ItemIsEditable
            return flags

        def add_item(self, product_dto: ProductDTO, quantity: Decimal = Decimal("1")):
            # Check if item already exists in cart, then update quantity
            for item_display in self._items:
                if item_display.product_id == product_dto.id:
                    item_display.quantity += quantity
                    item_display.line_subtotal = (item_display.quantity * item_display.unit_price).quantize(Decimal("0.01"))
                    item_display.line_tax = (item_display.line_subtotal * (item_display.gst_rate / Decimal("100.0"))).quantize(Decimal("0.01"))
                    item_display.line_total = (item_display.line_subtotal + item_display.line_tax).quantize(Decimal("0.01"))
                    
                    idx = self._items.index(item_display)
                    self.dataChanged.emit(self.createIndex(idx, 0), self.createIndex(idx, self.columnCount() - 1))
                    self.cart_changed.emit()
                    return

            # Add new item
            self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
            self._items.append(CartItemDisplay(
                product_id=product_dto.id,
                sku=product_dto.sku,
                name=product_dto.name,
                quantity=quantity,
                unit_price=product_dto.selling_price,
                gst_rate=product_dto.gst_rate # Store current GST rate for line item
            ))
            self.endInsertRows()
            self.cart_changed.emit()

        def remove_item_at_row(self, row: int):
            if 0 <= row < len(self._items):
                self.beginRemoveRows(QModelIndex(), row, row)
                del self._items[row]
                self.endRemoveRows()
                self.cart_changed.emit()

        def clear_cart(self):
            self.beginResetModel()
            self._items.clear()
            self.endResetModel()
            self.cart_changed.emit()

        def get_cart_summary(self) -> Tuple[Decimal, Decimal, Decimal]:
            """Returns (subtotal, tax_amount, total_amount) for the current cart."""
            subtotal = sum(item.line_subtotal for item in self._items).quantize(Decimal("0.01"))
            tax_amount = sum(item.line_tax for item in self._items).quantize(Decimal("0.01"))
            total_amount = sum(item.line_total for item in self._items).quantize(Decimal("0.01"))
            return subtotal, tax_amount, total_amount
        
        def get_cart_items_dto(self) -> List[CartItemDTO]:
            """Returns a list of CartItemDTOs from the current cart."""
            return [item.to_cart_item_dto() for item in self._items]


    class POSView(QWidget):
        """The main POS interface for conducting sales."""

        def __init__(self, core: ApplicationCore, parent: Optional[QObject] = None):
            super().__init__(parent)
            self.core = core
            self.async_worker: AsyncWorker = core.async_worker

            self._setup_ui()
            self._connect_signals()
            self._reset_sale()

        def _setup_ui(self):
            """Build the user interface."""
            # --- Left Panel: Cart and Totals ---
            left_panel = QWidget()
            left_layout = QVBoxLayout(left_panel)
            
            self.cart_table = QTableView()
            self.cart_model = CartTableModel()
            self.cart_table.setModel(self.cart_model)
            self.cart_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            self.cart_table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
            self.cart_table.setSelectionMode(QTableView.SelectionMode.SingleSelection)
            self.cart_table.setEditTriggers(QTableView.EditTrigger.DoubleClicked | QTableView.EditTrigger.AnyKeyPressed)

            self.subtotal_label = QLabel("Subtotal: S$0.00")
            self.tax_label = QLabel("GST (8.00%): S$0.00")
            self.total_label = QLabel("Total: S$0.00")
            self.total_label.setStyleSheet("font-size: 28px; font-weight: bold; color: #333;")

            # Layout for totals
            totals_form_layout = QFormLayout()
            totals_form_layout.addRow(self.subtotal_label)
            totals_form_layout.addRow(self.tax_label)
            totals_form_layout.addRow(self.total_label)

            left_layout.addWidget(QLabel("Current Sale Items"))
            left_layout.addWidget(self.cart_table, 1) # Give table more space
            left_layout.addLayout(totals_form_layout)
            
            # --- Right Panel: Product Entry, Customer, and Actions ---
            right_panel = QWidget()
            right_layout = QVBoxLayout(right_panel)

            # Product Search
            product_search_form = QFormLayout()
            self.product_search_input = QLineEdit()
            self.product_search_input.setPlaceholderText("Scan barcode or enter SKU/name...")
            self.add_item_button = QPushButton("Add to Cart")
            product_search_form.addRow("Product:", self.product_search_input)
            right_layout.addLayout(product_search_form)
            right_layout.addWidget(self.add_item_button)

            # Customer Selection (Simplified for now)
            customer_form = QFormLayout()
            self.customer_search_input = QLineEdit()
            self.customer_search_input.setPlaceholderText("Search customer by code/name...")
            self.select_customer_button = QPushButton("Select Customer")
            self.clear_customer_button = QPushButton("Clear")
            self.selected_customer_label = QLabel("Customer: N/A")
            customer_actions_layout = QHBoxLayout()
            customer_actions_layout.addWidget(self.select_customer_button)
            customer_actions_layout.addWidget(self.clear_customer_button)
            customer_form.addRow(self.selected_customer_label)
            customer_form.addRow(self.customer_search_input)
            customer_form.addRow(customer_actions_layout)
            right_layout.addLayout(customer_form)
            self.selected_customer_id: Optional[uuid.UUID] = None # To store selected customer's ID

            right_layout.addStretch() # Pushes buttons to bottom

            # Action Buttons
            self.new_sale_button = QPushButton("New Sale")
            self.void_sale_button = QPushButton("Void Sale")
            self.pay_button = QPushButton("PAY")
            self.pay_button.setStyleSheet("background-color: #4CAF50; color: white; font-size: 28px; padding: 20px;")
            
            right_layout.addWidget(self.new_sale_button)
            right_layout.addWidget(self.void_sale_button)
            right_layout.addWidget(self.pay_button)
            
            # --- Main Layout ---
            main_layout = QHBoxLayout(self)
            main_layout.addWidget(left_panel, 2) # Left panel takes 2/3 of space
            main_layout.addWidget(right_panel, 1) # Right panel takes 1/3
            self.setLayout(main_layout)
            self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)


        def _connect_signals(self):
            """Connects UI signals to slots."""
            self.add_item_button.clicked.connect(self._on_add_item_clicked)
            self.product_search_input.returnPressed.connect(self._on_add_item_clicked)
            self.pay_button.clicked.connect(self._on_pay_clicked)
            self.new_sale_button.clicked.connect(self._reset_sale_clicked)
            self.void_sale_button.clicked.connect(self._void_sale_clicked)
            self.cart_model.cart_changed.connect(self._update_totals) # Connect cart model signal
            # Customer selection signals
            self.select_customer_button.clicked.connect(self._on_select_customer_clicked)
            self.clear_customer_button.clicked.connect(self._clear_customer_selection)


        @Slot()
        def _update_totals(self):
            """Recalculates and updates the total display based on cart model."""
            subtotal, tax_amount, total_amount = self.cart_model.get_cart_summary()
            self.subtotal_label.setText(f"Subtotal: S${subtotal:.2f}")
            self.tax_label.setText(f"GST ({Decimal('8.00'):.2f}%): S${tax_amount:.2f}") # Hardcoded GST rate for display
            self.total_label.setText(f"Total: S${total_amount:.2f}")


        @Slot()
        def _on_add_item_clicked(self):
            """Handles adding a product to the cart from search input."""
            search_term = self.product_search_input.text().strip()
            if not search_term:
                QMessageBox.warning(self, "Input Required", "Please enter a product SKU, barcode, or name.")
                return
            
            company_id = self.core.current_company_id

            def _on_done(result: Any, error: Optional[Exception]):
                if error:
                    QMessageBox.critical(self, "Error", f"Failed to search product: {error}")
                elif isinstance(result, Success):
                    products = result.value
                    if not products:
                        QMessageBox.warning(self, "Not Found", f"No product found for '{search_term}'.")
                        return

                    # For simplicity, if multiple products match, take the first one.
                    # A real app might show a selection dialog.
                    selected_product: ProductDTO = products[0] 
                    self.cart_model.add_item(selected_product)
                    self.product_search_input.clear()
                    self.product_search_input.setFocus()
                elif isinstance(result, Failure):
                    QMessageBox.warning(self, "Product Lookup Failed", f"Could not find product: {result.error}")
            
            coro = self.core.product_manager.search_products(company_id, search_term, limit=1) # Limit to 1 for simple selection
            self.async_worker.run_task(coro, on_done_callback=_on_done)


        @Slot()
        def _on_pay_clicked(self):
            """Initiates the payment process."""
            if not self.cart_model.rowCount():
                QMessageBox.warning(self, "Empty Cart", "Cannot process payment for an empty cart.")
                return

            # Get current company, outlet, cashier IDs from core (from settings for now)
            company_id = self.core.current_company_id
            outlet_id = self.core.current_outlet_id
            cashier_id = self.core.current_user_id # Assuming logged-in user is cashier

            # Construct preliminary SaleCreateDTO without payment info
            # PaymentDialog will collect payment info.
            temp_sale_dto = SaleCreateDTO(
                company_id=company_id,
                outlet_id=outlet_id,
                cashier_id=cashier_id,
                customer_id=self.selected_customer_id,
                cart_items=self.cart_model.get_cart_items_dto(),
                payments=[] # To be filled by dialog
            )
            
            # Get cart totals for payment dialog
            subtotal, tax_amount, total_amount = self.cart_model.get_cart_summary()

            # Open PaymentDialog
            payment_dialog = PaymentDialog(self.core, total_amount, parent=self)
            if payment_dialog.exec(): # This exec() call is blocking, but the dialog itself manages async operations
                payment_info_dtos = payment_dialog.get_payment_info()
                if not payment_info_dtos:
                    QMessageBox.critical(self, "Payment Error", "No payment information received from dialog.")
                    return

                # Update the temp DTO with actual payment info
                temp_sale_dto.payments = payment_info_dtos

                # Call SalesManager to finalize the sale asynchronously
                def _on_done(result: Any, error: Optional[Exception]):
                    if error:
                        QMessageBox.critical(self, "Error", f"Failed to finalize sale: {error}")
                    elif isinstance(result, Success):
                        finalized_sale_dto: FinalizedSaleDTO = result.value
                        QMessageBox.information(self, "Sale Completed", 
                                                f"Transaction {finalized_sale_dto.transaction_number} completed!\n"
                                                f"Total: S${finalized_sale_dto.total_amount:.2f}\n"
                                                f"Change Due: S${finalized_sale_dto.change_due:.2f}")
                        
                        # TODO: Trigger receipt printing/display (using FinalizedSaleDTO)
                        print(f"Finalized Sale DTO for Receipt: {finalized_sale_dto}")

                        self._reset_sale_clicked() # Reset UI for new sale
                    elif isinstance(result, Failure):
                        QMessageBox.warning(self, "Sale Failed", f"Could not finalize sale: {result.error}")
                
                coro = self.core.sales_manager.finalize_sale(temp_sale_dto)
                self.pay_button.setEnabled(False) # Disable button while processing
                self.async_worker.run_task(coro, on_done_callback=_on_done)
                self.pay_button.setEnabled(True) # Re-enable (will be done in callback for true async)
            else:
                QMessageBox.information(self, "Payment Cancelled", "Payment process cancelled.")


        @Slot()
        def _reset_sale_clicked(self):
            """Clears the cart and resets the UI for a new sale."""
            self.cart_model.clear_cart()
            self.product_search_input.clear()
            self._clear_customer_selection()
            self._update_totals() # Updates to S$0.00
            self.product_search_input.setFocus()
            QMessageBox.information(self, "New Sale", "Sale reset. Ready for new transaction.")


        @Slot()
        def _void_sale_clicked(self):
            """Voids the current sale (clears cart without processing)."""
            if self.cart_model.rowCount() == 0:
                QMessageBox.information(self, "No Sale", "There is no active sale to void.")
                return

            reply = QMessageBox.question(self, "Confirm Void",
                                        "Are you sure you want to void the current sale? This cannot be undone.",
                                        QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                self._reset_sale_clicked()
                QMessageBox.information(self, "Sale Voided", "Current sale has been voided.")

        @Slot()
        def _on_select_customer_clicked(self):
            """Opens a dialog to select a customer (simplified for now)."""
            customer_code = self.customer_search_input.text().strip()
            if not customer_code:
                QMessageBox.warning(self, "Input Required", "Please enter a customer code or name to search.")
                return
            
            company_id = self.core.current_company_id

            def _on_done(result: Any, error: Optional[Exception]):
                if error:
                    QMessageBox.critical(self, "Error", f"Failed to search customer: {error}")
                elif isinstance(result, Success):
                    customers = result.value
                    if not customers:
                        QMessageBox.warning(self, "Not Found", f"No customer found for '{customer_code}'.")
                        return
                    
                    selected_customer: CustomerDTO = customers[0] # Take first for simplicity
                    self.selected_customer_id = selected_customer.id
                    self.selected_customer_label.setText(f"Customer: {selected_customer.name} ({selected_customer.customer_code})")
                    QMessageBox.information(self, "Customer Selected", f"Customer '{selected_customer.name}' selected.")
                    self.customer_search_input.clear() # Clear search after selection
                elif isinstance(result, Failure):
                    QMessageBox.warning(self, "Customer Lookup Failed", f"Could not find customer: {result.error}")
            
            # Use customer_manager.search_customers
            coro = self.core.customer_manager.search_customers(company_id, customer_code, limit=1)
            self.async_worker.run_task(coro, on_done_callback=_on_done)


        @Slot()
        def _clear_customer_selection(self):
            """Clears the currently selected customer."""
            self.selected_customer_id = None
            self.selected_customer_label.setText("Customer: N/A")
            self.customer_search_input.clear()
            QMessageBox.information(self, "Customer Cleared", "Customer selection cleared.")
    ```
*   **Acceptance Checklist:**
    *   [ ] `POSView` inherits `QWidget`.
    *   [ ] `CartTableModel` is implemented as a `QAbstractTableModel` for displaying cart items.
    *   [ ] `cart_table` is set up with `cart_model` and `QHeaderView.ResizeMode.Stretch`.
    *   [ ] `CartTableModel` has `add_item`, `remove_item_at_row`, `clear_cart`, `get_cart_summary`, `get_cart_items_dto` methods.
    *   [ ] Quantity column is editable in `CartTableModel`.
    *   [ ] `subtotal_label`, `tax_label`, `total_label` are present and updated by `_update_totals` slot.
    *   [ ] `_on_add_item_clicked` calls `product_manager.search_products` via `async_worker.run_task()` and adds product to cart on success.
    *   [ ] `_on_pay_clicked` launches `PaymentDialog`, constructs `SaleCreateDTO`, and calls `sales_manager.finalize_sale` via `async_worker.run_task()`.
    *   [ ] `_on_pay_clicked` handles `Result` from `finalize_sale` with `QMessageBox` feedback, and calls `_reset_sale_clicked` on success.
    *   [ ] `_reset_sale_clicked` clears cart and UI.
    *   [ ] `_void_sale_clicked` confirms and clears cart.
    *   [ ] `_on_select_customer_clicked` uses `customer_manager.search_customers` to select a customer (simplified).
    *   [ ] `_clear_customer_selection` clears the customer selection.
    *   [ ] Type hinting is complete.

#### **2. `app/ui/dialogs/payment_dialog.py`**

*   **File Path:** `app/ui/dialogs/payment_dialog.py`
*   **Purpose & Goals:** A modal `QDialog` for handling payment collection in a sales transaction. It allows multiple payment methods (split tender) and calculates change due.
*   **Interfaces:** `PaymentDialog(core: ApplicationCore, total_due: Decimal)`. Method: `get_payment_info() -> List[PaymentInfoDTO]`.
*   **Interactions:** Launched by `POSView`. Collects payment details and returns them as `PaymentInfoDTO`s. Does not call backend managers directly.
*   **Code Skeleton:**
    ```python
    # File: app/ui/dialogs/payment_dialog.py
    """A QDialog for collecting payment for a sales transaction."""
    import uuid
    from decimal import Decimal
    from typing import List, Optional, Any
    
    from PySide6.QtWidgets import (
        QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit,
        QDoubleSpinBox, QComboBox, QPushButton, QLabel, QDialogButtonBox, QMessageBox,
        QTableWidget, QTableWidgetItem, QHeaderView
    )
    from PySide6.QtCore import Slot, Signal, Qt, QObject

    from app.core.application_core import ApplicationCore
    from app.core.result import Success, Failure
    from app.business_logic.dto.sales_dto import PaymentInfoDTO
    from app.models.payment import PaymentMethod # For type hinting

    class PaymentEntry:
        """Helper class to hold payment details entered by user."""
        def __init__(self, method_id: uuid.UUID, method_name: str, amount: Decimal):
            self.method_id = method_id
            self.method_name = method_name
            self.amount = amount

        def to_payment_info_dto(self) -> PaymentInfoDTO:
            """Converts to PaymentInfoDTO."""
            return PaymentInfoDTO(payment_method_id=self.method_id, amount=self.amount)

    class PaymentDialog(QDialog):
        """A dialog for collecting payment for a sales transaction, supporting split tender."""

        def __init__(self, core: ApplicationCore, total_due: Decimal, parent: Optional[QObject] = None):
            super().__init__(parent)
            self.core = core
            self.total_due = total_due.quantize(Decimal("0.01"))
            self.current_payments: List[PaymentEntry] = []
            self.available_payment_methods: List[PaymentMethod] = []

            self.setWindowTitle("Process Payment")
            self.setMinimumSize(500, 400) # Give more space

            self._setup_ui()
            self._connect_signals()
            self._load_payment_methods() # Load methods asynchronously

        def _setup_ui(self):
            """Build the user interface."""
            # --- Top: Totals Summary ---
            summary_layout = QFormLayout()
            self.total_due_label = QLabel(f"<b>Amount Due: S${self.total_due:.2f}</b>")
            self.total_paid_label = QLabel("Amount Paid: S$0.00")
            self.balance_label = QLabel("Balance: S$0.00")
            
            self.total_due_label.setStyleSheet("font-size: 20px;")
            self.total_paid_label.setStyleSheet("font-size: 16px; color: #555;")
            self.balance_label.setStyleSheet("font-size: 18px; font-weight: bold; color: red;")

            summary_layout.addRow("Total Due:", self.total_due_label)
            summary_layout.addRow("Amount Paid:", self.total_paid_label)
            summary_layout.addRow("Balance:", self.balance_label)

            # --- Middle: Payment Entry ---
            payment_entry_layout = QHBoxLayout()
            self.method_combo = QComboBox()
            self.amount_input = QDoubleSpinBox()
            self.amount_input.setRange(0, 999999.99)
            self.amount_input.setDecimals(2)
            self.add_payment_button = QPushButton("Add Payment")
            
            payment_entry_layout.addWidget(self.method_combo, 1)
            payment_entry_layout.addWidget(self.amount_input)
            payment_entry_layout.addWidget(self.add_payment_button)

            # --- Bottom: Payments Table ---
            self.payments_table = QTableWidget(0, 3) # Rows, Cols
            self.payments_table.setHorizontalHeaderLabels(["Method", "Amount", "Action"])
            self.payments_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            self.payments_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

            # --- Buttons ---
            self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            self.button_box.button(QDialogButtonBox.Ok).setText("Finalize Sale")
            self.button_box.button(QDialogButtonBox.Ok).setEnabled(False) # Enable only when balance is 0 or less

            # --- Main Layout ---
            main_layout = QVBoxLayout(self)
            main_layout.addLayout(summary_layout)
            main_layout.addStretch(1) # Push content apart
            main_layout.addLayout(payment_entry_layout)
            main_layout.addWidget(self.payments_table, 2) # Give table more space
            main_layout.addWidget(self.button_box)

            self._update_summary_labels() # Initial update


        def _connect_signals(self):
            """Connects UI signals to slots."""
            self.add_payment_button.clicked.connect(self._on_add_payment_clicked)
            self.button_box.accepted.connect(self._on_finalize_sale_clicked)
            self.button_box.rejected.connect(self.reject)


        def _load_payment_methods(self):
            """Loads available payment methods asynchronously and populates the combo box."""
            company_id = self.core.current_company_id

            def _on_done(result: Any, error: Optional[Exception]):
                if error:
                    QMessageBox.critical(self, "Load Error", f"Failed to load payment methods: {error}")
                    self.add_payment_button.setEnabled(False) # Disable payment entry
                elif isinstance(result, Success):
                    self.available_payment_methods = result.value
                    self.method_combo.clear()
                    for method in self.available_payment_methods:
                        self.method_combo.addItem(method.name, method.id)
                    
                    if self.method_combo.count() > 0:
                        self.amount_input.setValue(float(self.total_due)) # Pre-fill with remaining balance
                    else:
                        QMessageBox.warning(self, "No Payment Methods", "No active payment methods found. Please configure them in settings.")
                        self.add_payment_button.setEnabled(False)
                elif isinstance(result, Failure):
                    QMessageBox.warning(self, "Payment Methods Failed", f"Could not load payment methods: {result.error}")
                    self.add_payment_button.setEnabled(False)

            coro = self.core.payment_method_service.get_all_active_methods(company_id)
            self.core.async_worker.run_task(coro, on_done_callback=_on_done)


        @Slot()
        def _update_summary_labels(self):
            """Updates the amount paid and balance labels."""
            total_paid = sum(p.amount for p in self.current_payments).quantize(Decimal("0.01"))
            balance = (self.total_due - total_paid).quantize(Decimal("0.01"))

            self.total_paid_label.setText(f"Amount Paid: S${total_paid:.2f}")
            self.balance_label.setText(f"Balance: S${balance:.2f}")
            
            if balance <= 0:
                self.balance_label.setStyleSheet("font-size: 18px; font-weight: bold; color: green;")
                self.button_box.button(QDialogButtonBox.Ok).setEnabled(True) # Enable finalize button
            else:
                self.balance_label.setStyleSheet("font-size: 18px; font-weight: bold; color: red;")
                self.button_box.button(QDialogButtonBox.Ok).setEnabled(False)


        @Slot()
        def _on_add_payment_clicked(self):
            """Adds a new payment entry to the table."""
            selected_method_id = self.method_combo.currentData()
            selected_method_name = self.method_combo.currentText()
            amount = Decimal(str(self.amount_input.value()))

            if not selected_method_id:
                QMessageBox.warning(self, "No Method", "Please select a payment method.")
                return
            if amount <= 0:
                QMessageBox.warning(self, "Invalid Amount", "Payment amount must be greater than zero.")
                return
            
            # Optionally: Limit amount to remaining balance or allow overpayment
            current_total_paid = sum(p.amount for p in self.current_payments)
            remaining_balance = self.total_due - current_total_paid
            if amount > remaining_balance and remaining_balance > 0: # Allow overpayment
                reply = QMessageBox.question(self, "Overpayment?", f"Payment of S${amount:.2f} is more than remaining S${remaining_balance:.2f}. Continue?", QMessageBox.Yes | QMessageBox.No)
                if reply == QMessageBox.No:
                    return

            payment_entry = PaymentEntry(selected_method_id, selected_method_name, amount)
            self.current_payments.append(payment_entry)
            
            row_idx = self.payments_table.rowCount()
            self.payments_table.insertRow(row_idx)
            self.payments_table.setItem(row_idx, 0, QTableWidgetItem(selected_method_name))
            self.payments_table.setItem(row_idx, 1, QTableWidgetItem(f"S${amount:.2f}"))

            # Add remove button
            remove_button = QPushButton("Remove")
            remove_button.clicked.connect(lambda: self._on_remove_payment_clicked(row_idx))
            self.payments_table.setCellWidget(row_idx, 2, remove_button)

            self._update_summary_labels()
            self.amount_input.setValue(float(self.total_due - sum(p.amount for p in self.current_payments))) # Pre-fill remaining balance


        @Slot(int)
        def _on_remove_payment_clicked(self, row_idx: int):
            """Removes a payment entry from the table."""
            # Note: This slot needs to be careful with row_idx if rows are removed dynamically.
            # A common pattern is to connect to a lambda that captures the item itself.
            # For simplicity, we assume index stability or re-evaluate.
            button = self.sender()
            if button:
                row_idx = self.payments_table.indexAt(button.pos()).row()
                if 0 <= row_idx < len(self.current_payments):
                    self.payments_table.removeRow(row_idx)
                    del self.current_payments[row_idx]
                    self._update_summary_labels()
                    self.amount_input.setValue(float(self.total_due - sum(p.amount for p in self.current_payments)))
            

        @Slot()
        def _on_finalize_sale_clicked(self):
            """Finalizes the sale if all conditions are met."""
            if sum(p.amount for p in self.current_payments) < self.total_due:
                QMessageBox.warning(self, "Insufficient Payment", "Amount paid is less than total due. Cannot finalize sale.")
                return

            self.accept() # Accept the dialog, triggering POSView to process the sale


        def get_payment_info(self) -> List[PaymentInfoDTO]:
            """Returns the collected payment information as DTOs."""
            return [p.to_payment_info_dto() for p in self.current_payments]
    ```
*   **Acceptance Checklist:**
    *   [ ] `PaymentDialog` inherits `QDialog`.
    *   [ ] Constructor accepts `ApplicationCore` and `total_due`.
    *   [ ] UI elements (summary labels, method combo box, amount input, add button, payments table, OK/Cancel buttons) are created and laid out.
    *   [ ] `_update_summary_labels` correctly calculates and displays total paid and balance.
    *   [ ] `_load_payment_methods` loads active payment methods via `payment_method_service` using `async_worker.run_task()` and populates the combo box.
    *   [ ] `_on_add_payment_clicked` adds payment entries to `current_payments` list and `payments_table`.
    *   [ ] `_on_remove_payment_clicked` removes payment entries.
    *   [ ] `_on_finalize_sale_clicked` accepts the dialog if payment is sufficient, otherwise warns.
    *   [ ] `get_payment_info` returns a list of `PaymentInfoDTO`s.
    *   [ ] "Finalize Sale" button is enabled only when `balance <= 0`.
    *   [ ] `amount_input` auto-fills with remaining balance.
    *   [ ] Type hinting is complete.

### **Phase 3.5: Updates to Existing Stage 1/2 Files**

#### **1. `app/ui/main_window.py`** (Modified from Stage 2)

*   **File Path:** `app/ui/main_window.py`
*   **Purpose & Goals:** To integrate the new `POSView` into the main application window and provide a navigation option in the menu bar.
*   **Interactions:** Instantiates `POSView` and adds it to the `QStackedWidget`. Adds a "Sales" action under a "POS" menu.
*   **Code Skeleton:**
    ```python
    # File: app/ui/main_window.py
    """
    The main window of the SG-POS application.
    This QMainWindow acts as the shell, hosting different views like the POS screen,
    inventory management, etc., and providing navigation.
    """
    import asyncio
    import sys
    from typing import Optional, Any
    from PySide6.QtWidgets import (
        QMainWindow, QWidget, QVBoxLayout, QLabel,
        QStackedWidget, QMenuBar, QMenu, QMessageBox
    )
    from PySide6.QtCore import Slot, QEvent, QObject, QMetaObject, Qt, QGenericArgument as Q_ARG

    from app.core.application_core import ApplicationCore
    from app.core.async_bridge import AsyncWorker
    from app.core.exceptions import CoreException

    # Import all views that will be hosted
    from app.ui.views.product_view import ProductView
    from app.ui.views.customer_view import CustomerView
    from app.ui.views.pos_view import POSView # NEW: Import POSView
    # from app.ui.views.inventory_view import InventoryView # To be implemented in Stage 4
    # from app.ui.views.reports_view import ReportsView # To be implemented in Stage 5
    # from app.ui.views.settings_view import SettingsView # To be implemented in Stage 5


    class MainWindow(QMainWindow):
        """The main application window."""

        def __init__(self, core: ApplicationCore):
            """
            Initializes the main window.
            
            Args:
                core: The central ApplicationCore instance.
            """
            super().__init__()
            self.core = core
            self.async_worker: AsyncWorker = core.async_worker

            self.setWindowTitle("SG Point-of-Sale System")
            self.setGeometry(100, 100, 1280, 720)

            # Create a QStackedWidget to hold the different views
            self.stacked_widget = QStackedWidget()
            self.setCentralWidget(self.stacked_widget)

            # --- Initialize and add actual views ---
            self.product_view = ProductView(self.core)
            self.customer_view = CustomerView(self.core)
            self.pos_view = POSView(self.core) # NEW: Initialize POSView
            # TODO: Initialize other views as they are implemented in later stages
            # self.inventory_view = InventoryView(self.core)
            # self.reports_view = ReportsView(self.core)
            # self.settings_view = SettingsView(self.core)

            # Add views to the stack
            self.stacked_widget.addWidget(self.pos_view) # NEW: Add POSView first or as a main default
            self.stacked_widget.addWidget(self.product_view)
            self.stacked_widget.addWidget(self.customer_view)
            # TODO: Add other views here
            
            # Show the POS view by default
            self.stacked_widget.setCurrentWidget(self.pos_view) # NEW: Start on POS view

            # --- Connect the AsyncWorker's general task_finished signal ---
            self.async_worker.task_finished.connect(self._handle_async_task_result)

            # --- Create menu bar for navigation ---
            self._create_menu()

        def _create_menu(self):
            """Creates the main menu bar with navigation items."""
            menu_bar = self.menuBar()
            
            # File Menu
            file_menu = menu_bar.addMenu("&File")
            exit_action = file_menu.addAction("E&xit")
            exit_action.triggered.connect(self.close)

            # POS Menu (Populated in Stage 3)
            pos_menu = menu_bar.addMenu("&POS") # NEW
            pos_action = pos_menu.addAction("Sales") # NEW
            pos_action.triggered.connect(lambda: self.stacked_widget.setCurrentWidget(self.pos_view)) # NEW

            # Data Management Menu (Populated in Stage 2)
            data_menu = menu_bar.addMenu("&Data Management")
            product_action = data_menu.addAction("Products")
            product_action.triggered.connect(lambda: self.stacked_widget.setCurrentWidget(self.product_view))
            customer_action = data_menu.addAction("Customers")
            customer_action.triggered.connect(lambda: self.stacked_widget.setCurrentWidget(self.customer_view))

            # Inventory Menu (Populated in Stage 4)
            # inventory_menu = menu_bar.addMenu("&Inventory")
            # inventory_action = inventory_menu.addAction("Stock Management")
            # inventory_action.triggered.connect(lambda: self.stacked_widget.setCurrentWidget(self.inventory_view))

            # Reports Menu (Populated in Stage 5)
            # reports_menu = menu_bar.addMenu("&Reports")
            # reports_action = reports_menu.addAction("Business Reports")
            # reports_action.triggered.connect(lambda: self.stacked_widget.setCurrentWidget(self.reports_view))

            # Settings Menu (Populated in Stage 5)
            # settings_menu = menu_bar.addMenu("&Settings")
            # settings_action = settings_menu.addAction("Application Settings")
            # settings_action.triggered.connect(lambda: self.stacked_widget.setCurrentWidget(self.settings_view))


        @Slot(object, object)
        def _handle_async_task_result(self, result: Any, error: Optional[Exception]):
            """
            Global handler for results/errors from async tasks that didn't have
            a specific `on_done_callback`. This can be used for general error reporting.
            Individual UI components should still use specific callbacks where needed.
            """
            if error:
                print(f"Unhandled async error: {error}", file=sys.stderr)
                # TODO: Implement more sophisticated global error logging/display
                # QMessageBox.critical(self, "Error", f"An unexpected background error occurred: {error}")

        def closeEvent(self, event: QEvent) -> None:
            """
            Handle window close event to gracefully shut down the application core.
            This ensures database connections and async threads are properly terminated.
            """
            print("Main window closing. Initiating ApplicationCore shutdown...")
            
            async def shutdown_task():
                try:
                    await self.core.shutdown()
                    print("ApplicationCore shutdown complete.")
                except Exception as e:
                    print(f"Error during ApplicationCore shutdown: {e}", file=sys.stderr)
                    QMetaObject.invokeMethod(self, "show_shutdown_error",
                                            Qt.ConnectionType.QueuedConnection,
                                            Q_ARG(str, str(e)))
                QMetaObject.invokeMethod(self, "accept_close_event",
                                         Qt.ConnectionType.QueuedConnection)

            self.async_worker.run_task(shutdown_task())
            
            event.ignore()

        @Slot()
        def accept_close_event(self) -> None:
            """Slot to finally accept the close event after async shutdown completes."""
            QApplication.instance().quit()

        @Slot(str)
        def show_shutdown_error(self, error_message: str) -> None:
            """Displays a critical error message if shutdown fails."""
            QMessageBox.critical(self, "Shutdown Error", f"Failed to gracefully shut down application:\n{error_message}")
    ```
*   **Acceptance Checklist:**
    *   [ ] `POSView` is imported and instantiated.
    *   [ ] `POSView` is added to the `stacked_widget`.
    *   [ ] "POS" menu is created in the menu bar.
    *   [ ] "Sales" action is added to the "POS" menu and correctly switches the `stacked_widget` to `pos_view`.
    *   [ ] The initial view displayed is `pos_view`.

---

This completes the detailed execution plan for Stage 3. The core transactional capabilities are now defined, with full atomicity and proper asynchronous integration.

---

## **Stage 4: Expanding Operations - Inventory & Advanced CRM**

**Objective:** To build out the full inventory management and advanced customer relationship management modules.

### **Phase 4.1: Data Transfer Objects (DTOs) for Inventory**

#### **1. `app/business_logic/dto/inventory_dto.py`**

*   **File Path:** `app/business_logic/dto/inventory_dto.py`
*   **Purpose & Goals:** Defines data contracts for inventory-related operations, including purchase orders, stock adjustments, and stock movements.
*   **Interfaces:** `PurchaseOrderItemCreateDTO`, `PurchaseOrderCreateDTO`, `StockAdjustmentItemDTO`, `StockAdjustmentDTO`, `PurchaseOrderDTO`, `StockMovementDTO`, `SupplierDTO`.
*   **Interactions:** Used by `InventoryManager`, `PurchaseOrderService`, `SupplierService`, `InventoryService`, and UI dialogs/views.
*   **Code Skeleton:**
    ```python
    # File: app/business_logic/dto/inventory_dto.py
    """Data Transfer Objects for Inventory and Procurement operations."""
    import uuid
    from decimal import Decimal
    from datetime import datetime, date
    from typing import List, Optional
    from pydantic import BaseModel, Field

    # --- Supplier DTOs ---
    class SupplierBaseDTO(BaseModel):
        name: str = Field(..., min_length=1, max_length=255)
        contact_person: Optional[str] = None
        email: Optional[str] = None
        phone: Optional[str] = None
        address: Optional[str] = None
        is_active: bool = True

    class SupplierCreateDTO(SupplierBaseDTO):
        pass

    class SupplierUpdateDTO(SupplierBaseDTO):
        pass

    class SupplierDTO(SupplierBaseDTO):
        id: uuid.UUID
        class Config:
            orm_mode = True

    # --- Purchase Order DTOs ---
    class PurchaseOrderItemCreateDTO(BaseModel):
        product_id: uuid.UUID
        quantity_ordered: Decimal = Field(..., gt=Decimal("0.00"))
        unit_cost: Decimal = Field(..., ge=Decimal("0.00"), decimal_places=4)

    class PurchaseOrderCreateDTO(BaseModel):
        company_id: uuid.UUID
        outlet_id: uuid.UUID
        supplier_id: uuid.UUID
        po_number: Optional[str] = None # Will be generated if not provided
        order_date: datetime = Field(default_factory=datetime.utcnow)
        expected_delivery_date: Optional[datetime] = None
        notes: Optional[str] = None
        items: List[PurchaseOrderItemCreateDTO] = Field(..., min_items=1)

    class PurchaseOrderItemDTO(BaseModel):
        id: uuid.UUID
        product_id: uuid.UUID
        product_name: str # For display
        sku: str # For display
        quantity_ordered: Decimal = Field(..., decimal_places=4)
        quantity_received: Decimal = Field(..., decimal_places=4)
        unit_cost: Decimal = Field(..., decimal_places=4)
        line_total: Decimal = Field(..., decimal_places=2)
        class Config:
            orm_mode = True

    class PurchaseOrderDTO(BaseModel):
        id: uuid.UUID
        company_id: uuid.UUID
        outlet_id: uuid.UUID
        supplier_id: uuid.UUID
        supplier_name: str # For display
        po_number: str
        order_date: datetime
        expected_delivery_date: Optional[datetime]
        status: str
        notes: Optional[str]
        total_amount: Decimal = Field(..., decimal_places=2)
        items: List[PurchaseOrderItemDTO]
        class Config:
            orm_mode = True

    # --- Stock Adjustment DTO ---
    class StockAdjustmentItemDTO(BaseModel):
        product_id: uuid.UUID
        counted_quantity: Decimal = Field(..., ge=Decimal("0.00"), decimal_places=4)
        # The manager will calculate the change from the current stock level

    class StockAdjustmentDTO(BaseModel):
        company_id: uuid.UUID
        outlet_id: uuid.UUID
        user_id: uuid.UUID # User performing the adjustment
        notes: str = Field(..., min_length=1, description="Reason or notes for the adjustment")
        items: List[StockAdjustmentItemDTO] = Field(..., min_items=1)

    # --- Stock Movement DTO (for display/reporting) ---
    class StockMovementDTO(BaseModel):
        id: uuid.UUID
        product_id: uuid.UUID
        product_name: str
        sku: str
        outlet_name: str
        movement_type: str
        quantity_change: Decimal = Field(..., decimal_places=4)
        reference_id: Optional[uuid.UUID]
        reference_type: Optional[str]
        notes: Optional[str]
        created_by_user_name: Optional[str]
        created_at: datetime
        class Config:
            orm_mode = True

    # --- Inventory Summary DTO (for InventoryView display) ---
    class InventorySummaryDTO(BaseModel):
        product_id: uuid.UUID
        product_name: str
        sku: str
        barcode: Optional[str]
        category_name: Optional[str]
        quantity_on_hand: Decimal = Field(..., decimal_places=4)
        reorder_point: int
        is_active: bool
        cost_price: Decimal = Field(..., decimal_places=4)
        selling_price: Decimal = Field(..., decimal_places=4)
        
        class Config:
            orm_mode = True
    ```
*   **Acceptance Checklist:**
    *   [ ] DTOs for `Supplier`, `PurchaseOrder`, `PurchaseOrderItem`, `StockAdjustment`, `StockMovement`, and `InventorySummary` are defined.
    *   [ ] All necessary fields are included with correct Pydantic types, validation, and `decimal_places`.
    *   [ ] `Create`, `Update`, and `Full` DTO patterns are used where appropriate.
    *   [ ] `Config.orm_mode` is set for DTOs that map directly from ORM models.
    *   [ ] Docstrings are clear.

### **Phase 4.2: Data Access Layer for Inventory & CRM**

#### **1. `app/services/supplier_service.py`**

*   **File Path:** `app/services/supplier_service.py`
*   **Purpose & Goals:** Handles persistence operations for supplier entities.
*   **Interfaces:** `SupplierService(core: ApplicationCore)`. Methods: `async get_by_name(company_id, name)`. Inherits CRUD from `BaseService`.
*   **Interactions:** Used by `InventoryManager` and UI.
*   **Code Skeleton:**
    ```python
    # File: app/services/supplier_service.py
    """Data Access Service (Repository) for Supplier entities."""
    from __future__ import annotations
    from typing import TYPE_CHECKING, List
    from uuid import UUID
    import sqlalchemy as sa
    from sqlalchemy.future import select

    from app.core.result import Result, Success, Failure
    from app.models.inventory import Supplier
    from app.services.base_service import BaseService

    if TYPE_CHECKING:
        from app.core.application_core import ApplicationCore

    class SupplierService(BaseService):
        """
        Handles all database interactions for the Supplier model.
        Inherits generic CRUD from BaseService.
        """
        def __init__(self, core: "ApplicationCore"):
            super().__init__(core, Supplier)
        
        async def get_by_name(self, company_id: UUID, name: str) -> Result[Supplier | None, str]:
            """Fetches a supplier by its unique name for a given company."""
            try:
                async with self.core.get_session() as session:
                    stmt = select(Supplier).where(
                        Supplier.company_id == company_id,
                        Supplier.name == name
                    )
                    result = await session.execute(stmt)
                    supplier = result.scalar_one_or_none()
                    return Success(supplier)
            except Exception as e:
                return Failure(f"Database error fetching supplier by name '{name}': {e}")
        
        async def search(self, company_id: UUID, term: str, limit: int = 100, offset: int = 0) -> Result[List[Supplier], str]:
            """
            Searches for suppliers by name, contact person, email, or phone.
            """
            try:
                async with self.core.get_session() as session:
                    search_pattern = f"%{term}%"
                    stmt = select(Supplier).where(
                        Supplier.company_id == company_id,
                        Supplier.is_active == True,
                        sa.or_(
                            Supplier.name.ilike(search_pattern),
                            Supplier.contact_person.ilike(search_pattern),
                            Supplier.email.ilike(search_pattern),
                            Supplier.phone.ilike(search_pattern)
                        )
                    ).offset(offset).limit(limit)
                    result = await session.execute(stmt)
                    suppliers = result.scalars().all()
                    return Success(suppliers)
            except Exception as e:
                return Failure(f"Database error searching suppliers: {e}")
    ```
*   **Acceptance Checklist:**
    *   [ ] `SupplierService` inherits from `BaseService` for `Supplier`.
    *   [ ] `get_by_name` and `search` methods are implemented.
    *   [ ] All methods return `Result` and use `async with self.core.get_session()`.

#### **2. `app/services/purchase_order_service.py`**

*   **File Path:** `app/services/purchase_order_service.py`
*   **Purpose & Goals:** Handles persistence operations for Purchase Orders and their items.
*   **Interfaces:** `PurchaseOrderService(core: ApplicationCore)`. Methods: `async create_full_purchase_order(po: PurchaseOrder)`.
*   **Interactions:** Used by `InventoryManager`.
*   **Code Skeleton:**
    ```python
    # File: app/services/purchase_order_service.py
    """Data Access Service (Repository) for Purchase Order entities."""
    from __future__ import annotations
    from typing import TYPE_CHECKING, List
    from uuid import UUID
    import sqlalchemy as sa
    from sqlalchemy.future import select

    from app.core.result import Result, Success, Failure
    from app.models.inventory import PurchaseOrder, PurchaseOrderItem
    from app.services.base_service import BaseService

    if TYPE_CHECKING:
        from app.core.application_core import ApplicationCore

    class PurchaseOrderService(BaseService):
        """
        Handles all database interactions for the PurchaseOrder model.
        Inherits generic CRUD from BaseService.
        """
        def __init__(self, core: "ApplicationCore"):
            super().__init__(core, PurchaseOrder)
            
        async def create_full_purchase_order(self, po: PurchaseOrder) -> Result[PurchaseOrder, str]:
            """
            Saves a complete PurchaseOrder object, including its items, within the current session.
            Args:
                po: The complete PurchaseOrder ORM instance to save.
            Returns:
                A Success containing the saved PurchaseOrder, or a Failure with an error.
            """
            try:
                async with self.core.get_session() as session:
                    session.add(po)
                    await session.flush()
                    await session.refresh(po)
                    for item in po.items:
                        await session.refresh(item)
                    return Success(po)
            except sa.exc.IntegrityError as e:
                return Failure(f"Data integrity error creating purchase order: {e.orig}")
            except Exception as e:
                return Failure(f"Database error saving full purchase order: {e}")

        async def get_open_purchase_orders(self, company_id: UUID, outlet_id: UUID | None = None) -> Result[List[PurchaseOrder], str]:
            """
            Fetches open/pending purchase orders for a company, optionally filtered by outlet.
            """
            try:
                async with self.core.get_session() as session:
                    stmt = select(PurchaseOrder).where(
                        PurchaseOrder.company_id == company_id,
                        PurchaseOrder.status.in_(['DRAFT', 'SENT', 'PARTIALLY_RECEIVED'])
                    )
                    if outlet_id:
                        stmt = stmt.where(PurchaseOrder.outlet_id == outlet_id)
                    result = await session.execute(stmt)
                    pos = result.scalars().all()
                    return Success(pos)
            except Exception as e:
                return Failure(f"Database error fetching open purchase orders: {e}")

        # TODO: Add methods for receiving items against a PO, updating PO status, etc.
    ```
*   **Acceptance Checklist:**
    *   [ ] `PurchaseOrderService` inherits from `BaseService` for `PurchaseOrder`.
    *   [ ] `create_full_purchase_order` is implemented to save a PO and its items atomically.
    *   [ ] `get_open_purchase_orders` is implemented.
    *   [ ] All methods return `Result` and use `async with self.core.get_session()`.

#### **3. `app/services/inventory_service.py`**

*   **File Path:** `app/services/inventory_service.py`
*   **Purpose & Goals:** Manages `Inventory` and `StockMovement` tables. Provides low-level atomic stock adjustment and movement logging.
*   **Interfaces:** `InventoryService(core: ApplicationCore)`. Methods: `async get_stock_level(outlet_id, product_id)`, `async adjust_stock_level(outlet_id, product_id, quantity_change, session)`, `async log_movement(movement, session)`.
*   **Interactions:** Used by `InventoryManager` and `SalesManager` (for `deduct_stock_for_sale`). Its `adjust_stock_level` and `log_movement` methods are designed to be called within an existing database session passed by the calling manager to ensure atomicity across multiple operations.
*   **Code Skeleton:**
    ```python
    # File: app/services/inventory_service.py
    """Data Access Service (Repository) for Inventory operations."""
    from __future__ import annotations
    from typing import TYPE_CHECKING, List
    from uuid import UUID
    from decimal import Decimal
    import sqlalchemy as sa
    from sqlalchemy.future import select

    from app.core.result import Result, Success, Failure
    from app.models.inventory import Inventory, StockMovement # Import ORM models
    from app.models.product import Product # For fetching product details in summary
    from app.models.company import Outlet # For fetching outlet details in summary
    from app.models.user import User # For fetching user details in summary
    from app.services.base_service import BaseService

    if TYPE_CHECKING:
        from app.core.application_core import ApplicationCore
        from sqlalchemy.ext.asyncio import AsyncSession # For type hinting session argument


    class InventoryService: # Does NOT inherit from BaseService as it manages multiple models
        """
        Handles direct database interactions for inventory levels and stock movements.
        Low-level operations, usually called by InventoryManager.
        """
        def __init__(self, core: "ApplicationCore"):
            self.core = core

        async def get_stock_level(self, outlet_id: UUID, product_id: UUID, session: Optional[AsyncSession] = None) -> Result[Decimal, str]:
            """
            Gets the current quantity_on_hand for a product at an outlet.
            Can operate within an existing session or create a new one.
            Args:
                outlet_id: The UUID of the outlet.
                product_id: The UUID of the product.
                session: An optional existing SQLAlchemy AsyncSession.
            Returns:
                A Success containing the current quantity or Decimal("0"), or a Failure.
            """
            try:
                # Use provided session or create a new one for read-only operation
                async with self.core.get_session() as new_session if session is None else session:
                    stmt = select(Inventory.quantity_on_hand).where(
                        Inventory.outlet_id == outlet_id,
                        Inventory.product_id == product_id
                    )
                    result = await new_session.execute(stmt)
                    quantity = result.scalar_one_or_none()
                    return Success(quantity or Decimal("0"))
            except Exception as e:
                return Failure(f"Database error getting stock level for product {product_id} at outlet {outlet_id}: {e}")

        async def adjust_stock_level(
            self,
            outlet_id: UUID,
            product_id: UUID,
            quantity_change: Decimal,
            session: AsyncSession # MUST be called within an existing transaction session
        ) -> Result[Decimal, str]:
            """
            Adjusts the stock level for a product at a given outlet.
            This is a low-level method that modifies the `inventory` table.
            It must be called within an existing transactional session (passed in).
            Args:
                outlet_id: The UUID of the outlet.
                product_id: The UUID of the product.
                quantity_change: The amount to change (+ for increase, - for decrease).
                session: The SQLAlchemy AsyncSession to use (from the calling manager's UoW).
            Returns:
                A Success containing the new quantity_on_hand, or a Failure.
            """
            try:
                # Lock the row for update to prevent race conditions during concurrent adjustments
                stmt = select(Inventory).where(
                    Inventory.outlet_id == outlet_id,
                    Inventory.product_id == product_id
                ).with_for_update() # IMPORTANT: Row-level lock

                result = await session.execute(stmt)
                inventory_item = result.scalar_one_or_none()

                if inventory_item:
                    inventory_item.quantity_on_hand += quantity_change
                else:
                    # Create a new inventory record if it doesn't exist for this product/outlet
                    inventory_item = Inventory(
                        company_id=self.core.current_company_id, # Assume current company
                        outlet_id=outlet_id,
                        product_id=product_id,
                        quantity_on_hand=quantity_change
                    )
                    session.add(inventory_item)

                # Business rule validation: Prevent negative stock unless explicitly allowed by system config
                if inventory_item.quantity_on_hand < 0:
                    raise ValueError(f"Stock quantity for product {product_id} cannot be negative. Current: {inventory_item.quantity_on_hand - quantity_change}, Change: {quantity_change}")

                await session.flush() # Flush to ensure changes are seen within the transaction
                return Success(inventory_item.quantity_on_hand)
            except ValueError as ve: # Catch specific validation error
                return Failure(f"Stock adjustment validation error: {ve}")
            except Exception as e:
                return Failure(f"Failed to adjust stock level for product {product_id}: {e}")

        async def log_movement(
            self,
            movement: StockMovement,
            session: AsyncSession # MUST be called within an existing transaction session
        ) -> Result[StockMovement, str]:
            """
            Logs a stock movement record. This is an immutable record for auditing.
            It must be called within an existing transactional session.
            Args:
                movement: The StockMovement ORM instance to log.
                session: The SQLAlchemy AsyncSession to use.
            Returns:
                A Success containing the logged StockMovement, or a Failure.
            """
            try:
                session.add(movement)
                await session.flush()
                return Success(movement)
            except Exception as e:
                return Failure(f"Failed to log stock movement: {e}")
        
        async def get_inventory_summary(self, company_id: UUID, outlet_id: UUID | None = None, limit: int = 100, offset: int = 0, search_term: str | None = None) -> Result[List[Dict[str, Any]], str]:
            """
            Retrieves a summary of inventory levels, suitable for the InventoryView.
            Includes product details for display.
            """
            try:
                async with self.core.get_session() as session:
                    stmt = select(
                        Product.id,
                        Product.name,
                        Product.sku,
                        Product.barcode,
                        Product.reorder_point,
                        Product.is_active,
                        Product.cost_price,
                        Product.selling_price,
                        sa.func.coalesce(Inventory.quantity_on_hand, Decimal('0.0')).label("quantity_on_hand"),
                        sa.text("categories.name AS category_name") # Direct join and label for category name
                    ).join(Inventory, Inventory.product_id == Product.id, isouter=True) \
                    .outerjoin(Product.category) \
                    .where(Product.company_id == company_id)

                    if outlet_id:
                        stmt = stmt.where(Inventory.outlet_id == outlet_id)
                    
                    if search_term:
                        search_pattern = f"%{search_term}%"
                        stmt = stmt.where(sa.or_(
                            Product.sku.ilike(search_pattern),
                            Product.barcode.ilike(search_pattern),
                            Product.name.ilike(search_pattern)
                        ))

                    stmt = stmt.offset(offset).limit(limit)
                    
                    result = await session.execute(stmt)
                    # Convert to list of dictionaries, handling aliased category name
                    rows = [
                        {k: v for k, v in row._asdict().items()}
                        for row in result.all()
                    ]
                    return Success(rows)
            except Exception as e:
                return Failure(f"Database error getting inventory summary: {e}")
        
        async def get_stock_movements_for_product(self, company_id: UUID, product_id: UUID, limit: int = 100, offset: int = 0) -> Result[List[StockMovement], str]:
            """Retrieves stock movement history for a specific product."""
            try:
                async with self.core.get_session() as session:
                    stmt = select(StockMovement).where(
                        StockMovement.company_id == company_id,
                        StockMovement.product_id == product_id
                    ).order_by(StockMovement.created_at.desc()).offset(offset).limit(limit)
                    result = await session.execute(stmt)
                    movements = result.scalars().all()
                    return Success(movements)
            except Exception as e:
                return Failure(f"Database error fetching stock movements for product {product_id}: {e}")
    ```
*   **Acceptance Checklist:**
    *   [ ] `InventoryService` is defined (does not inherit `BaseService`).
    *   [ ] `get_stock_level` method is implemented, handling optional session.
    *   [ ] `adjust_stock_level` method is implemented, accepts a required `session` argument, uses `with_for_update()`, handles creating new `Inventory` records, and prevents negative stock.
    *   [ ] `log_movement` method is implemented, accepts a required `session` argument.
    *   [ ] `get_inventory_summary` method is implemented, using joins to get product and category details, and handles search/pagination.
    *   [ ] `get_stock_movements_for_product` is implemented.
    *   [ ] All methods return `Result` and handle exceptions.
    *   [ ] Type hinting is complete.

### **Phase 4.3: Business Logic for Inventory and CRM**

#### **1. `app/business_logic/managers/inventory_manager.py`**

*   **File Path:** `app/business_logic/managers/inventory_manager.py`
*   **Purpose & Goals:** Orchestrates all high-level inventory workflows, including stock adjustments, purchase order creation/receipt, and stock deduction during sales. Ensures atomic operations across multiple services.
*   **Interfaces:** `InventoryManager(core: ApplicationCore)`. Methods: `async adjust_stock(dto: StockAdjustmentDTO)`, `async create_purchase_order(dto: PurchaseOrderCreateDTO)`, `async deduct_stock_for_sale(...)`, `async get_inventory_summary(...)`, `async get_stock_movements_for_product(...)`, `async get_open_purchase_orders(...)`.
*   **Interactions:** Lazy-loads `InventoryService`, `ProductService`, `SupplierService`, `PurchaseOrderService`, `UserService`. Orchestrates operations via `self.core.get_session()`.
*   **Code Skeleton:**
    ```python
    # File: app/business_logic/managers/inventory_manager.py
    """Business Logic Manager for orchestrating Inventory operations."""
    from __future__ import annotations
    from typing import TYPE_CHECKING, List, Dict, Any
    from uuid import UUID
    from decimal import Decimal
    import uuid # For generating PO numbers

    from app.core.result import Result, Success, Failure
    from app.business_logic.managers.base_manager import BaseManager
    from app.business_logic.dto.inventory_dto import (
        StockAdjustmentDTO, PurchaseOrderCreateDTO, PurchaseOrderDTO,
        InventorySummaryDTO, StockMovementDTO, SupplierDTO, PurchaseOrderItemDTO
    )
    from app.models.inventory import StockMovement, PurchaseOrder, PurchaseOrderItem # Import ORM models
    from app.models.product import Product # For getting product cost/details


    if TYPE_CHECKING:
        from app.core.application_core import ApplicationCore
        from app.services.inventory_service import InventoryService
        from app.services.product_service import ProductService
        from app.services.supplier_service import SupplierService
        from app.services.purchase_order_service import PurchaseOrderService
        from app.services.user_service import UserService
        from sqlalchemy.ext.asyncio import AsyncSession


    class InventoryManager(BaseManager):
        """Handles high-level inventory workflows like stock takes, adjustments, and purchase orders."""
        
        @property
        def inventory_service(self) -> "InventoryService":
            return self.core.inventory_service

        @property
        def product_service(self) -> "ProductService":
            return self.core.product_service

        @property
        def supplier_service(self) -> "SupplierService":
            return self.core.supplier_service

        @property
        def purchase_order_service(self) -> "PurchaseOrderService":
            return self.core.purchase_order_service

        @property
        def user_service(self) -> "UserService":
            return self.core.user_service


        async def adjust_stock(self, dto: StockAdjustmentDTO) -> Result[None, str]:
            """
            Performs a stock adjustment for one or more products, creating an
            auditable stock movement record for each change.
            Args:
                dto: StockAdjustmentDTO containing details of the adjustment.
            Returns:
                A Success(None) on successful adjustment, or a Failure.
            """
            if not dto.items:
                return Failure("No items provided for stock adjustment.")
            if not dto.notes:
                return Failure("Adjustment notes/reason is required.")

            try:
                # All adjustments in this DTO must be atomic
                async with self.core.get_session() as session:
                    for item_dto in dto.items:
                        # 1. Get current stock
                        current_stock_result = await self.inventory_service.get_stock_level(
                            dto.outlet_id, item_dto.product_id, session=session # Pass session
                        )
                        if isinstance(current_stock_result, Failure):
                            raise Exception(f"Failed to get current stock for {item_dto.product_id}: {current_stock_result.error}")
                        
                        current_stock = current_stock_result.value
                        quantity_change = item_dto.counted_quantity - current_stock
                        
                        if quantity_change == 0:
                            continue # No change needed

                        # 2. Adjust the stock level in the Inventory table
                        adjust_result = await self.inventory_service.adjust_stock_level(
                            outlet_id=dto.outlet_id,
                            product_id=item_dto.product_id,
                            quantity_change=quantity_change,
                            session=session # Pass the current session
                        )
                        if isinstance(adjust_result, Failure):
                            raise Exception(f"Failed to update inventory for {item_dto.product_id}: {adjust_result.error}")

                        # 3. Log the movement for audit trail
                        movement_type = 'ADJUSTMENT_IN' if quantity_change > 0 else 'ADJUSTMENT_OUT'
                        movement = StockMovement(
                            company_id=dto.company_id,
                            outlet_id=dto.outlet_id,
                            product_id=item_dto.product_id,
                            movement_type=movement_type,
                            quantity_change=quantity_change,
                            notes=dto.notes,
                            created_by_user_id=dto.user_id,
                            reference_type="STOCK_ADJUSTMENT",
                            reference_id=None # Can link to a specific adjustment ID if we had one
                        )
                        log_result = await self.inventory_service.log_movement(movement, session)
                        if isinstance(log_result, Failure):
                            raise Exception(f"Failed to log stock movement for {item_dto.product_id}: {log_result.error}")
                
                return Success(None)
            except Exception as e:
                # The `get_session` context manager will handle the rollback if an exception is raised.
                return Failure(f"Stock adjustment failed: {e}")

        async def deduct_stock_for_sale(self, company_id: UUID, outlet_id: UUID, sale_items: List[Dict[str, Any]], cashier_id: UUID, session: AsyncSession) -> Result[None, str]:
            """
            A dedicated method to deduct stock after a sale is finalized.
            Called by the SalesManager within its atomic transaction.
            Args:
                company_id: The UUID of the company.
                outlet_id: The UUID of the outlet where the sale occurred.
                sale_items: A list of dictionaries containing product_id, quantity.
                cashier_id: The UUID of the cashier.
                session: The SQLAlchemy AsyncSession for the current transaction.
            Returns:
                A Success(None) if stock is successfully deducted, or a Failure.
            """
            for item_data in sale_items:
                product_id = item_data['product_id']
                quantity = item_data['quantity']

                # 1. Adjust the stock level (deducting quantity)
                adjust_result = await self.inventory_service.adjust_stock_level(
                    outlet_id=outlet_id,
                    product_id=product_id,
                    quantity_change=-quantity, # Negative for deduction
                    session=session
                )
                if isinstance(adjust_result, Failure):
                    return Failure(f"Insufficient stock for product {item_data['sku']}: {adjust_result.error}")

                # 2. Log the stock movement
                movement = StockMovement(
                    company_id=company_id,
                    outlet_id=outlet_id,
                    product_id=product_id,
                    movement_type='SALE',
                    quantity_change=-quantity,
                    notes=f"Sale transaction by {cashier_id}", # Or link to sales_transaction_id later
                    created_by_user_id=cashier_id,
                    reference_type="SALES_TRANSACTION"
                    # reference_id will be set by SalesManager when the sales_transaction is available
                )
                log_result = await self.inventory_service.log_movement(movement, session)
                if isinstance(log_result, Failure):
                    return Failure(f"Failed to log sale stock movement for product {item_data['sku']}: {log_result.error}")
            
            return Success(None)
        
        async def create_purchase_order(self, dto: PurchaseOrderCreateDTO) -> Result[PurchaseOrderDTO, str]:
            """
            Creates a new purchase order, including its line items.
            Args:
                dto: PurchaseOrderCreateDTO containing PO details.
            Returns:
                A Success with the created PurchaseOrderDTO, or a Failure.
            """
            try:
                async with self.core.get_session() as session:
                    # 1. Validate supplier exists
                    supplier_result = await self.supplier_service.get_by_id(dto.supplier_id)
                    if isinstance(supplier_result, Failure) or supplier_result.value is None:
                        raise Exception(f"Supplier with ID '{dto.supplier_id}' not found.")

                    # 2. Validate products exist and calculate total amount
                    po_total_amount = Decimal("0.0")
                    po_items: List[PurchaseOrderItem] = []
                    for item_dto in dto.items:
                        product_result = await self.product_service.get_by_id(item_dto.product_id)
                        if isinstance(product_result, Failure) or product_result.value is None:
                            raise Exception(f"Product with ID '{item_dto.product_id}' not found for PO item.")
                        
                        po_item = PurchaseOrderItem(
                            product_id=item_dto.product_id,
                            quantity_ordered=item_dto.quantity_ordered,
                            unit_cost=item_dto.unit_cost
                        )
                        po_items.append(po_item)
                        po_total_amount += item_dto.quantity_ordered * item_dto.unit_cost

                    # 3. Create PurchaseOrder ORM model
                    po_number = dto.po_number if dto.po_number else f"PO-{uuid.uuid4().hex[:8].upper()}"
                    new_po = PurchaseOrder(
                        company_id=dto.company_id,
                        outlet_id=dto.outlet_id,
                        supplier_id=dto.supplier_id,
                        po_number=po_number,
                        order_date=dto.order_date,
                        expected_delivery_date=dto.expected_delivery_date,
                        notes=dto.notes,
                        total_amount=po_total_amount.quantize(Decimal("0.01")),
                        items=po_items
                    )

                    # 4. Save the full purchase order via service
                    save_po_result = await self.purchase_order_service.create_full_purchase_order(new_po)
                    if isinstance(save_po_result, Failure):
                        raise Exception(f"Failed to save purchase order: {save_po_result.error}")

                    # TODO: Optional: Log an audit event for PO creation

                    # 5. Prepare DTO for return
                    supplier_name = supplier_result.value.name
                    po_items_dto = [PurchaseOrderItemDTO.from_orm(item) for item in save_po_result.value.items]
                    po_dto_for_return = PurchaseOrderDTO(
                        id=save_po_result.value.id,
                        company_id=save_po_result.value.company_id,
                        outlet_id=save_po_result.value.outlet_id,
                        supplier_id=save_po_result.value.supplier_id,
                        supplier_name=supplier_name,
                        po_number=save_po_result.value.po_number,
                        order_date=save_po_result.value.order_date,
                        expected_delivery_date=save_po_result.value.expected_delivery_date,
                        status=save_po_result.value.status,
                        notes=save_po_result.value.notes,
                        total_amount=save_po_result.value.total_amount,
                        items=po_items_dto
                    )
                    return Success(po_dto_for_return)

            except Exception as e:
                return Failure(f"Failed to create purchase order: {e}")

        async def receive_purchase_order_items(self, po_id: UUID, items_received: List[Dict[str, Any]], user_id: UUID) -> Result[None, str]:
            """
            Records the receipt of items against a purchase order.
            Updates inventory and logs stock movements.
            Args:
                po_id: The UUID of the purchase order.
                items_received: List of dicts: {'product_id': UUID, 'quantity_received': Decimal}
                user_id: The UUID of the user receiving the items.
            Returns:
                A Success(None) on successful receipt, or a Failure.
            """
            if not items_received:
                return Failure("No items specified for receipt.")
            
            try:
                async with self.core.get_session() as session:
                    # 1. Get PO and lock it
                    po_result = await self.purchase_order_service.get_by_id(po_id)
                    if isinstance(po_result, Failure) or po_result.value is None:
                        raise Exception(f"Purchase Order {po_id} not found.")
                    
                    po = po_result.value
                    if po.status not in ['SENT', 'PARTIALLY_RECEIVED']:
                        raise Exception(f"Cannot receive items for PO in '{po.status}' status. Must be 'SENT' or 'PARTIALLY_RECEIVED'.")

                    for received_item_data in items_received:
                        product_id = received_item_data['product_id']
                        quantity_received = received_item_data['quantity_received']

                        # Find the corresponding PO item
                        po_item: Optional[PurchaseOrderItem] = None
                        for item in po.items:
                            if item.product_id == product_id:
                                po_item = item
                                break
                        
                        if not po_item:
                            raise Exception(f"Product {product_id} not found in Purchase Order {po_id}.")
                        
                        if po_item.quantity_received + quantity_received > po_item.quantity_ordered:
                            raise Exception(f"Received quantity for product {po_item.product.sku} exceeds quantity ordered.")

                        # Update quantity received on PO item
                        po_item.quantity_received += quantity_received
                        await session.flush() # Flush to reflect changes on PO item

                        # Adjust inventory levels
                        adjust_result = await self.inventory_service.adjust_stock_level(
                            outlet_id=po.outlet_id,
                            product_id=product_id,
                            quantity_change=quantity_received,
                            session=session
                        )
                        if isinstance(adjust_result, Failure):
                            raise Exception(f"Failed to adjust inventory for {po_item.product.sku}: {adjust_result.error}")

                        # Log stock movement
                        movement = StockMovement(
                            company_id=po.company_id,
                            outlet_id=po.outlet_id,
                            product_id=product_id,
                            movement_type='PURCHASE_RECEIPT',
                            quantity_change=quantity_received,
                            notes=f"Received via PO {po.po_number}",
                            created_by_user_id=user_id,
                            reference_type="PURCHASE_ORDER",
                            reference_id=po.id
                        )
                        log_result = await self.inventory_service.log_movement(movement, session)
                        if isinstance(log_result, Failure):
                            raise Exception(f"Failed to log PO receipt movement for {po_item.product.sku}: {log_result.error}")
                    
                    # Update PO status if fully received
                    all_items_received = all(item.quantity_ordered == item.quantity_received for item in po.items)
                    if all_items_received:
                        po.status = 'RECEIVED'
                    elif any(item.quantity_received > 0 for item in po.items):
                        po.status = 'PARTIALLY_RECEIVED'
                    
                    await session.flush() # Flush PO status change
                    await session.refresh(po) # Refresh to get updated status
                    
                    return Success(None)
            except Exception as e:
                return Failure(f"Failed to receive purchase order items: {e}")

        async def get_inventory_summary(self, company_id: UUID, outlet_id: UUID | None = None, limit: int = 100, offset: int = 0, search_term: str | None = None) -> Result[List[InventorySummaryDTO], str]:
            """
            Retrieves a summary of inventory levels for display in the InventoryView.
            Args:
                company_id: The UUID of the company.
                outlet_id: Optional UUID of the outlet to filter by.
                limit: Pagination limit.
                offset: Pagination offset.
                search_term: Optional search term for products.
            Returns:
                A Success with a list of InventorySummaryDTOs, or a Failure.
            """
            summary_result = await self.inventory_service.get_inventory_summary(company_id, outlet_id, limit, offset, search_term)
            if isinstance(summary_result, Failure):
                return summary_result
            
            # Map raw dict results to DTOs
            summary_dtos = [InventorySummaryDTO(**row) for row in summary_result.value]
            return Success(summary_dtos)

        async def get_stock_movements_for_product(self, company_id: UUID, product_id: UUID, limit: int = 100, offset: int = 0) -> Result[List[StockMovementDTO], str]:
            """
            Retrieves detailed stock movement history for a specific product.
            Args:
                company_id: The UUID of the company.
                product_id: The UUID of the product.
                limit: Pagination limit.
                offset: Pagination offset.
            Returns:
                A Success with a list of StockMovementDTOs, or a Failure.
            """
            movements_result = await self.inventory_service.get_stock_movements_for_product(company_id, product_id, limit, offset)
            if isinstance(movements_result, Failure):
                return movements_result

            movements_with_details: List[StockMovementDTO] = []
            for movement in movements_result.value:
                product_name_res = await self.product_service.get_by_id(movement.product_id)
                product_name = product_name_res.value.name if isinstance(product_name_res, Success) and product_name_res.value else "Unknown Product"
                product_sku = product_name_res.value.sku if isinstance(product_name_res, Success) and product_name_res.value else "Unknown SKU"

                outlet_name_res = await self.core.outlet_service.get_by_id(movement.outlet_id) # Assume outlet_service exists
                outlet_name = outlet_name_res.value.name if isinstance(outlet_name_res, Success) and outlet_name_res.value else "Unknown Outlet"

                user_name_res = await self.user_service.get_by_id(movement.created_by_user_id) if movement.created_by_user_id else Success(None)
                user_name = user_name_res.value.full_name if isinstance(user_name_res, Success) and user_name_res.value else "N/A"

                movements_with_details.append(StockMovementDTO(
                    id=movement.id,
                    product_id=movement.product_id,
                    product_name=product_name,
                    sku=product_sku,
                    outlet_name=outlet_name,
                    movement_type=movement.movement_type,
                    quantity_change=movement.quantity_change,
                    reference_id=movement.reference_id,
                    reference_type=movement.reference_type,
                    notes=movement.notes,
                    created_by_user_name=user_name,
                    created_at=movement.created_at
                ))
            
            return Success(movements_with_details)
        
        async def get_all_suppliers(self, company_id: UUID, limit: int = 100, offset: int = 0) -> Result[List[SupplierDTO], str]:
            """Retrieves all suppliers for a given company."""
            result = await self.supplier_service.get_all(company_id, limit, offset)
            if isinstance(result, Failure):
                return result
            return Success([SupplierDTO.from_orm(s) for s in result.value])
        
        async def search_suppliers(self, company_id: UUID, term: str, limit: int = 100, offset: int = 0) -> Result[List[SupplierDTO], str]:
            """Searches for suppliers."""
            result = await self.supplier_service.search(company_id, term, limit, offset)
            if isinstance(result, Failure):
                return result
            return Success([SupplierDTO.from_orm(s) for s in result.value])

        async def get_all_purchase_orders(self, company_id: UUID, limit: int = 100, offset: int = 0) -> Result[List[PurchaseOrderDTO], str]:
            """Retrieves all purchase orders for a given company."""
            result = await self.purchase_order_service.get_all(company_id, limit, offset)
            if isinstance(result, Failure):
                return result
            
            po_dtos: List[PurchaseOrderDTO] = []
            for po in result.value:
                supplier_res = await self.supplier_service.get_by_id(po.supplier_id)
                supplier_name = supplier_res.value.name if isinstance(supplier_res, Success) and supplier_res.value else "Unknown Supplier"
                po_items_dto = [PurchaseOrderItemDTO.from_orm(item) for item in po.items]
                po_dtos.append(PurchaseOrderDTO(
                    id=po.id,
                    company_id=po.company_id,
                    outlet_id=po.outlet_id,
                    supplier_id=po.supplier_id,
                    supplier_name=supplier_name,
                    po_number=po.po_number,
                    order_date=po.order_date,
                    expected_delivery_date=po.expected_delivery_date,
                    status=po.status,
                    notes=po.notes,
                    total_amount=po.total_amount,
                    items=po_items_dto
                ))
            return Success(po_dtos)
        
        async def get_purchase_order_by_id(self, po_id: UUID) -> Result[PurchaseOrderDTO, str]:
            """Retrieves a single purchase order by ID."""
            po_result = await self.purchase_order_service.get_by_id(po_id)
            if isinstance(po_result, Failure) or po_result.value is None:
                return Failure("Purchase order not found.")
            
            po = po_result.value
            supplier_res = await self.supplier_service.get_by_id(po.supplier_id)
            supplier_name = supplier_res.value.name if isinstance(supplier_res, Success) and supplier_res.value else "Unknown Supplier"
            po_items_dto = [PurchaseOrderItemDTO.from_orm(item) for item in po.items]
            
            return Success(PurchaseOrderDTO(
                id=po.id,
                company_id=po.company_id,
                outlet_id=po.outlet_id,
                supplier_id=po.supplier_id,
                supplier_name=supplier_name,
                po_number=po.po_number,
                order_date=po.order_date,
                expected_delivery_date=po.expected_delivery_date,
                status=po.status,
                notes=po.notes,
                total_amount=po.total_amount,
                items=po_items_dto
            ))
        
        # TODO: Add logic for reorder point alerts
        # TODO: Add logic for inter-outlet transfers
        # TODO: Add specific methods for managing Product Categories
    ```
*   **Acceptance Checklist:**
    *   [ ] `InventoryManager` inherits `BaseManager`.
    *   [ ] All necessary services (`inventory_service`, `product_service`, `supplier_service`, `purchase_order_service`, `user_service`, `outlet_service` - assuming `outlet_service` will be created later) are lazy-loaded.
    *   [ ] `adjust_stock` method is fully implemented, uses `async with self.core.get_session()`, calls `inventory_service.adjust_stock_level` and `log_movement` with the session.
    *   [ ] `deduct_stock_for_sale` is fully implemented, accepts `session`, calls `inventory_service.adjust_stock_level` and `log_movement`.
    *   [ ] `create_purchase_order` is fully implemented, validates supplier/products, calculates total, creates `PurchaseOrder` ORM with items, and calls `purchase_order_service.create_full_purchase_order`.
    *   [ ] `receive_purchase_order_items` is implemented, updates PO item quantities, calls `inventory_service.adjust_stock_level` and `log_movement`, and updates PO status.
    *   [ ] `get_inventory_summary` maps raw data from `inventory_service` to `InventorySummaryDTO`s.
    *   [ ] `get_stock_movements_for_product` fetches movements and enriches with product/outlet/user names, returning `StockMovementDTO`s.
    *   [ ] `get_all_suppliers`, `search_suppliers`, `get_all_purchase_orders`, `get_purchase_order_by_id` are implemented, returning DTOs.
    *   [ ] All methods return `Result` and handle exceptions.
    *   [ ] Type hinting is complete.

#### **2. `app/business_logic/managers/customer_manager.py`** (Modified from Stage 2)

*   **File Path:** `app/business_logic/managers/customer_manager.py`
*   **Purpose & Goals:** Adds loyalty points calculation and adjustment logic.
*   **Interfaces:** `async add_loyalty_points_for_sale(customer_id, sale_total)`.
*   **Interactions:** Used by `SalesManager` (for `add_loyalty_points_for_sale`).
*   **Code Skeleton:**
    ```python
    # File: app/business_logic/managers/customer_manager.py
    """Business Logic Manager for Customer operations."""
    from __future__ import annotations
    from typing import TYPE_CHECKING, List
    from uuid import UUID
    from decimal import Decimal

    from app.core.result import Result, Success, Failure
    from app.business_logic.managers.base_manager import BaseManager
    from app.business_logic.dto.customer_dto import CustomerDTO, CustomerCreateDTO, CustomerUpdateDTO
    # TODO: from app.business_logic.dto.inventory_dto import LoyaltyPointAdjustmentDTO # If using DTO for manual adjustment
    # TODO: from app.models.accounting import LoyaltyTransaction # If separate model for loyalty transactions

    if TYPE_CHECKING:
        from app.core.application_core import ApplicationCore
        from app.services.customer_service import CustomerService

    class CustomerManager(BaseManager):
        """Orchestrates business logic for customers."""

        @property
        def customer_service(self) -> "CustomerService":
            """Lazy-loads the CustomerService instance from the core."""
            return self.core.customer_service

        async def create_customer(self, company_id: UUID, dto: CustomerCreateDTO) -> Result[CustomerDTO, str]:
            # ... (existing code for create_customer) ...
            # Business rule: Check for duplicate customer code
            existing_result = await self.customer_service.get_by_code(company_id, dto.customer_code)
            if isinstance(existing_result, Failure):
                return existing_result # Propagate database error
            if existing_result.value is not None:
                return Failure(f"Business Rule Error: Customer with code '{dto.customer_code}' already exists.")

            # TODO: Consider checking for duplicate email if emails are meant to be unique.

            from app.models.customer import Customer # Import ORM model locally
            new_customer = Customer(company_id=company_id, **dto.dict())
            
            create_result = await self.customer_service.create(new_customer)
            if isinstance(create_result, Failure):
                return create_result

            return Success(CustomerDTO.from_orm(create_result.value))

        async def update_customer(self, customer_id: UUID, dto: CustomerUpdateDTO) -> Result[CustomerDTO, str]:
            # ... (existing code for update_customer) ...
            customer_result = await self.customer_service.get_by_id(customer_id)
            if isinstance(customer_result, Failure):
                return customer_result
            
            customer = customer_result.value
            if not customer:
                return Failure("Customer not found.")

            # Business rule: If customer code is changed, check for duplication
            if dto.customer_code != customer.customer_code:
                existing_result = await self.customer_service.get_by_code(customer.company_id, dto.customer_code)
                if isinstance(existing_result, Failure):
                    return existing_result
                if existing_result.value is not None and existing_result.value.id != customer_id:
                    return Failure(f"Business Rule Error: New customer code '{dto.customer_code}' is already in use by another customer.")

            # Update fields from DTO
            for field, value in dto.dict().items():
                setattr(customer, field, value)

            update_result = await self.customer_service.update(customer)
            if isinstance(update_result, Failure):
                return update_result
            
            return Success(CustomerDTO.from_orm(update_result.value))

        async def get_customer(self, customer_id: UUID) -> Result[CustomerDTO, str]:
            # ... (existing code for get_customer) ...
            result = await self.customer_service.get_by_id(customer_id)
            if isinstance(result, Failure):
                return result
            
            customer = result.value
            if not customer:
                return Failure("Customer not found.")
                
            return Success(CustomerDTO.from_orm(customer))

        async def get_all_customers(self, company_id: UUID, limit: int = 100, offset: int = 0) -> Result[List[CustomerDTO], str]:
            # ... (existing code for get_all_customers) ...
            result = await self.customer_service.get_all(company_id, limit, offset)
            if isinstance(result, Failure):
                return result
            
            return Success([CustomerDTO.from_orm(c) for c in result.value])
        
        async def search_customers(self, company_id: UUID, term: str, limit: int = 100, offset: int = 0) -> Result[List[CustomerDTO], str]:
            # ... (existing code for search_customers) ...
            result = await self.customer_service.search(company_id, term, limit, offset)
            if isinstance(result, Failure):
                return result
            
            return Success([CustomerDTO.from_orm(c) for c in result.value])

        async def deactivate_customer(self, customer_id: UUID) -> Result[bool, str]:
            # ... (existing code for deactivate_customer) ...
            customer_result = await self.customer_service.get_by_id(customer_id)
            if isinstance(customer_result, Failure):
                return customer_result
            
            customer = customer_result.value
            if not customer:
                return Failure("Customer not found.")
            
            customer.is_active = False
            update_result = await self.customer_service.update(customer)
            if isinstance(update_result, Failure):
                return update_result
            
            return Success(True)

        async def add_loyalty_points_for_sale(self, customer_id: UUID, sale_total: Decimal) -> Result[int, str]:
            """
            Calculates and adds loyalty points for a completed sale.
            Business Rule: 1 point for every S$10 spent (configurable).
            Args:
                customer_id: The UUID of the customer.
                sale_total: The total amount of the sale.
            Returns:
                A Success with the new loyalty point total, or a Failure.
            """
            points_to_add = int(sale_total // Decimal("10.00")) # Calculate points based on rule
            
            if points_to_add <= 0:
                return Success(0) # No points to add

            customer_result = await self.customer_service.get_by_id(customer_id)
            if isinstance(customer_result, Failure):
                return customer_result
            
            customer = customer_result.value
            if not customer:
                return Failure(f"Customer with ID {customer_id} not found.")
            
            # Ensure operation is within an existing transaction if called by SalesManager
            # Since customer_service.update uses its own session, this will be a separate transaction for loyalty.
            # For strict atomicity, customer_service.update would need a `session` argument.
            customer.loyalty_points += points_to_add
            
            update_result = await self.customer_service.update(customer)
            if isinstance(update_result, Failure):
                return update_result
                
            # TODO: Log the loyalty transaction for auditing (separate LoyaltyTransaction model or audit_log entry)
            # await self.core.audit_manager.log_loyalty_change(...)

            return Success(customer.loyalty_points)
        
        # TODO: Implement redeem_loyalty_points(customer_id, points_to_redeem) -> Result[discount_value, Error]
        # This would be used in the POSView when applying discounts.
        # TODO: Implement manual_adjust_loyalty_points (for admin adjustments)
    ```
*   **Acceptance Checklist:**
    *   [ ] `add_loyalty_points_for_sale` is fully implemented.
    *   [ ] It calculates points based on sale total (configurable rule).
    *   [ ] It fetches the customer, updates `loyalty_points`, and persists via `customer_service.update`.
    *   [ ] It returns `Result` object.
    *   [ ] Type hinting is complete.

### **Phase 4.4: UI for Inventory Management (`app/ui/`)**

#### **1. `app/ui/views/inventory_view.py`**

*   **File Path:** `app/ui/views/inventory_view.py`
*   **Purpose & Goals:** Main view for inventory management. Displays current stock levels, allows searching, and provides buttons to trigger stock adjustments and purchase order creation.
*   **Interfaces:** `InventoryView(core: ApplicationCore)`.
*   **Interactions:**
    *   Manages an `InventoryTableModel`.
    *   Calls `inventory_manager.get_inventory_summary` and `search_products` via `async_worker.run_task()`.
    *   Launches `StockAdjustmentDialog` and `PurchaseOrderDialog`.
    *   Provides user context (`company_id`, `outlet_id`).
*   **Code Skeleton:**
    ```python
    # File: app/ui/views/inventory_view.py
    """Main View for Inventory Management."""
    from __future__ import annotations
    from decimal import Decimal
    from typing import List, Any, Optional
    
    from PySide6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
        QTableView, QLabel, QLineEdit, QHeaderView, QSizePolicy, QMessageBox,
        QTabWidget # For tabs like Inventory, Purchase Orders, Stock Movements
    )
    from PySide6.QtCore import Slot, Signal, QAbstractTableModel, QModelIndex, Qt, QObject

    from app.core.application_core import ApplicationCore
    from app.core.result import Success, Failure
    from app.business_logic.dto.inventory_dto import InventorySummaryDTO, PurchaseOrderDTO, StockMovementDTO
    from app.ui.dialogs.stock_adjustment_dialog import StockAdjustmentDialog # Import
    from app.ui.dialogs.purchase_order_dialog import PurchaseOrderDialog # Import
    from app.core.async_bridge import AsyncWorker

    class InventoryTableModel(QAbstractTableModel):
        """A Qt Table Model for displaying InventorySummaryDTOs."""
        
        HEADERS = ["SKU", "Name", "Category", "On Hand", "Reorder Pt.", "Cost", "Selling Price", "Active"]

        def __init__(self, items: List[InventorySummaryDTO], parent: Optional[QObject] = None):
            super().__init__(parent)
            self._items = items

        def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
            return len(self._items)

        def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
            return len(self.HEADERS)

        def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
            if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
                return self.HEADERS[section]
            return None

        def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
            if not index.isValid():
                return None
            
            item = self._items[index.row()]
            col = index.column()

            if role == Qt.ItemDataRole.DisplayRole:
                if col == 0: return item.sku
                if col == 1: return item.name
                if col == 2: return item.category_name or "N/A"
                if col == 3: return str(item.quantity_on_hand)
                if col == 4: return str(item.reorder_point)
                if col == 5: return f"S${item.cost_price:.2f}"
                if col == 6: return f"S${item.selling_price:.2f}"
                if col == 7: return "Yes" if item.is_active else "No"
            
            if role == Qt.ItemDataRole.TextAlignmentRole:
                if col in [3, 4, 5, 6]:
                    return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
                if col == 7:
                    return Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter
            
            return None

        def get_item_at_row(self, row: int) -> Optional[InventorySummaryDTO]:
            """Returns the InventorySummaryDTO at the given row index."""
            if 0 <= row < len(self._items):
                return self._items[row]
            return None

        def refresh_data(self, new_items: List[InventorySummaryDTO]):
            """Updates the model with new data and notifies views."""
            self.beginResetModel()
            self._items = new_items
            self.endResetModel()

    class PurchaseOrderTableModel(QAbstractTableModel):
        """A Qt Table Model for displaying PurchaseOrderDTOs."""
        HEADERS = ["PO Number", "Supplier", "Order Date", "Expected Delivery", "Total Amount", "Status"]

        def __init__(self, pos: List[PurchaseOrderDTO], parent: Optional[QObject] = None):
            super().__init__(parent)
            self._pos = pos

        def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
            return len(self._pos)

        def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
            return len(self.HEADERS)
        
        def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
            if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
                return self.HEADERS[section]
            return None

        def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
            if not index.isValid(): return None
            po = self._pos[index.row()]
            col = index.column()

            if role == Qt.ItemDataRole.DisplayRole:
                if col == 0: return po.po_number
                if col == 1: return po.supplier_name
                if col == 2: return po.order_date.strftime("%Y-%m-%d")
                if col == 3: return po.expected_delivery_date.strftime("%Y-%m-%d") if po.expected_delivery_date else "N/A"
                if col == 4: return f"S${po.total_amount:.2f}"
                if col == 5: return po.status.capitalize()
            
            if role == Qt.ItemDataRole.TextAlignmentRole:
                if col == 4: return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
                if col == 5: return Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter
            return None
        
        def get_po_at_row(self, row: int) -> Optional[PurchaseOrderDTO]:
            if 0 <= row < len(self._pos):
                return self._pos[row]
            return None

        def refresh_data(self, new_pos: List[PurchaseOrderDTO]):
            self.beginResetModel()
            self._pos = new_pos
            self.endResetModel()

    class StockMovementTableModel(QAbstractTableModel):
        """A Qt Table Model for displaying StockMovementDTOs."""
        HEADERS = ["Date", "Product", "SKU", "Outlet", "Type", "Change", "User", "Notes"]

        def __init__(self, movements: List[StockMovementDTO], parent: Optional[QObject] = None):
            super().__init__(parent)
            self._movements = movements

        def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
            return len(self._movements)

        def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
            return len(self.HEADERS)
        
        def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
            if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
                return self.HEADERS[section]
            return None

        def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
            if not index.isValid(): return None
            movement = self._movements[index.row()]
            col = index.column()

            if role == Qt.ItemDataRole.DisplayRole:
                if col == 0: return movement.created_at.strftime("%Y-%m-%d %H:%M")
                if col == 1: return movement.product_name
                if col == 2: return movement.sku
                if col == 3: return movement.outlet_name
                if col == 4: return movement.movement_type.replace('_', ' ').title()
                if col == 5: 
                    change_str = str(movement.quantity_change)
                    return f"+{change_str}" if movement.quantity_change > 0 else change_str
                if col == 6: return movement.created_by_user_name or "System"
                if col == 7: return movement.notes or "N/A"
            
            if role == Qt.ItemDataRole.TextAlignmentRole:
                if col == 5: return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            return None
        
        def refresh_data(self, new_movements: List[StockMovementDTO]):
            self.beginResetModel()
            self._movements = new_movements
            self.endResetModel()


    class InventoryView(QWidget):
        """A view to display stock levels and initiate inventory operations."""

        def __init__(self, core: ApplicationCore, parent: Optional[QObject] = None):
            super().__init__(parent)
            self.core = core
            self.async_worker: AsyncWorker = core.async_worker
            
            # Get current context IDs
            self.company_id = self.core.current_company_id
            self.outlet_id = self.core.current_outlet_id
            self.user_id = self.core.current_user_id


            self._setup_ui()
            self._connect_signals()
            self._load_inventory_summary() # Load initial data for current tab


        def _setup_ui(self):
            """Build the user interface with tabs for different inventory aspects."""
            self.tab_widget = QTabWidget()
            
            # --- Inventory Summary Tab ---
            self.inventory_summary_tab = QWidget()
            inventory_summary_layout = QVBoxLayout(self.inventory_summary_tab)
            
            # Top bar for Inventory Summary
            summary_top_layout = QHBoxLayout()
            self.inventory_search_input = QLineEdit()
            self.inventory_search_input.setPlaceholderText("Search product by SKU, name, barcode...")
            self.adjust_stock_button = QPushButton("Adjust Stock")
            summary_top_layout.addWidget(self.inventory_search_input, 1)
            summary_top_layout.addStretch()
            summary_top_layout.addWidget(self.adjust_stock_button)
            
            self.inventory_table = QTableView()
            self.inventory_model = InventoryTableModel([])
            self.inventory_table.setModel(self.inventory_model)
            self.inventory_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            self.inventory_table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
            self.inventory_table.setSelectionMode(QTableView.SelectionMode.SingleSelection)
            self.inventory_table.doubleClicked.connect(self._on_view_product_stock_history) # Double click to view history

            inventory_summary_layout.addLayout(summary_top_layout)
            inventory_summary_layout.addWidget(self.inventory_table)
            self.tab_widget.addTab(self.inventory_summary_tab, "Current Stock")

            # --- Purchase Orders Tab ---
            self.purchase_orders_tab = QWidget()
            po_layout = QVBoxLayout(self.purchase_orders_tab)
            
            po_top_layout = QHBoxLayout()
            self.new_po_button = QPushButton("New Purchase Order")
            self.receive_po_button = QPushButton("Receive Items on PO")
            po_top_layout.addStretch()
            po_top_layout.addWidget(self.new_po_button)
            po_top_layout.addWidget(self.receive_po_button)

            self.po_table = QTableView()
            self.po_model = PurchaseOrderTableModel([])
            self.po_table.setModel(self.po_model)
            self.po_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            self.po_table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
            self.po_table.setSelectionMode(QTableView.SelectionMode.SingleSelection)
            self.po_table.doubleClicked.connect(self._on_view_purchase_order_details)

            po_layout.addLayout(po_top_layout)
            po_layout.addWidget(self.po_table)
            self.tab_widget.addTab(self.purchase_orders_tab, "Purchase Orders")

            # --- Stock Movements Tab ---
            self.stock_movements_tab = QWidget()
            movements_layout = QVBoxLayout(self.stock_movements_tab)
            self.movements_table = QTableView()
            self.movements_model = StockMovementTableModel([])
            self.movements_table.setModel(self.movements_model)
            self.movements_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

            movements_layout.addWidget(QLabel("All Stock Movements (for selected product if any)"))
            movements_layout.addWidget(self.movements_table)
            self.tab_widget.addTab(self.stock_movements_tab, "Stock Movements")


            # --- Main Layout ---
            main_layout = QVBoxLayout(self)
            main_layout.addWidget(self.tab_widget)
            self.setLayout(main_layout)
            self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)


        def _connect_signals(self):
            """Connects UI signals to slots."""
            self.tab_widget.currentChanged.connect(self._on_tab_changed)

            # Inventory Summary Tab
            self.inventory_search_input.textChanged.connect(self._on_inventory_search)
            self.adjust_stock_button.clicked.connect(self._on_adjust_stock)

            # Purchase Orders Tab
            self.new_po_button.clicked.connect(self._on_new_po)
            self.receive_po_button.clicked.connect(self._on_receive_po_items)

            # TODO: Add search/filter for POs and Stock Movements
        
        @Slot(int)
        def _on_tab_changed(self, index: int):
            """Loads data relevant to the newly selected tab."""
            if index == self.tab_widget.indexOf(self.inventory_summary_tab):
                self._load_inventory_summary(search_term=self.inventory_search_input.text())
            elif index == self.tab_widget.indexOf(self.purchase_orders_tab):
                self._load_purchase_orders()
            elif index == self.tab_widget.indexOf(self.stock_movements_tab):
                # By default load all recent, or filter by a specific product if selected in inventory tab
                self._load_stock_movements()


        @Slot()
        def _load_inventory_summary(self, search_term: str = ""):
            """Loads inventory summary data asynchronously into the table model."""
            def _on_done(result: Any, error: Optional[Exception]):
                if error:
                    QMessageBox.critical(self, "Load Error", f"Failed to load inventory: {error}")
                elif isinstance(result, Success):
                    self.inventory_model.refresh_data(result.value)
                elif isinstance(result, Failure):
                    QMessageBox.warning(self, "Load Failed", f"Could not load inventory: {result.error}")
            
            coro = self.core.inventory_manager.get_inventory_summary(self.company_id, self.outlet_id, search_term=search_term)
            self.async_worker.run_task(coro, on_done_callback=_on_done)
        
        @Slot(str)
        def _on_inventory_search(self, text: str):
            """Triggers inventory search."""
            self._load_inventory_summary(search_term=text)


        @Slot()
        def _on_adjust_stock(self):
            """Opens the stock adjustment dialog."""
            dialog = StockAdjustmentDialog(self.core, self.outlet_id, self.user_id, parent=self)
            if dialog.exec():
                self._load_inventory_summary(search_term=self.inventory_search_input.text()) # Refresh summary


        @Slot()
        def _on_view_product_stock_history(self):
            """Opens stock movements tab for the selected product."""
            selected_item = self.inventory_model.get_item_at_row(self.inventory_table.currentIndex().row())
            if not selected_item: return

            self.tab_widget.setCurrentWidget(self.stock_movements_tab)
            # Now load movements for this specific product
            self._load_stock_movements(product_id=selected_item.product_id)


        @Slot()
        def _load_purchase_orders(self):
            """Loads purchase order data asynchronously into the table model."""
            def _on_done(result: Any, error: Optional[Exception]):
                if error:
                    QMessageBox.critical(self, "Load Error", f"Failed to load purchase orders: {error}")
                elif isinstance(result, Success):
                    self.po_model.refresh_data(result.value)
                elif isinstance(result, Failure):
                    QMessageBox.warning(self, "Load Failed", f"Could not load purchase orders: {result.error}")
            
            coro = self.core.inventory_manager.get_all_purchase_orders(self.company_id) # Can filter by outlet if needed
            self.async_worker.run_task(coro, on_done_callback=_on_done)

        @Slot()
        def _on_new_po(self):
            """Opens the purchase order creation dialog."""
            dialog = PurchaseOrderDialog(self.core, self.outlet_id, parent=self)
            if dialog.exec():
                self._load_purchase_orders() # Refresh PO list

        @Slot()
        def _on_receive_po_items(self):
            """Opens a dialog to receive items against a selected Purchase Order."""
            selected_po = self.po_model.get_po_at_row(self.po_table.currentIndex().row())
            if not selected_po:
                QMessageBox.information(self, "No Selection", "Please select a Purchase Order to receive items for.")
                return
            
            # TODO: Create a dedicated dialog for receiving items on a PO.
            # This dialog would display PO items, allow entering received quantities,
            # and then call inventory_manager.receive_purchase_order_items.
            QMessageBox.information(self, "Receive PO", f"Functionality to receive items for PO {selected_po.po_number} is not yet implemented.")


        @Slot()
        def _on_view_purchase_order_details(self):
            """Opens a dialog to view details of the selected Purchase Order."""
            selected_po = self.po_model.get_po_at_row(self.po_table.currentIndex().row())
            if not selected_po: return # Should not happen with double-click, but safety.
            
            # TODO: Implement a PurchaseOrderDetailDialog to show a PO and its items.
            QMessageBox.information(self, "PO Details", f"Details for PO {selected_po.po_number} would be shown here.")


        @Slot()
        def _load_stock_movements(self, product_id: Optional[uuid.UUID] = None):
            """Loads stock movements data asynchronously into the table model."""
            def _on_done(result: Any, error: Optional[Exception]):
                if error:
                    QMessageBox.critical(self, "Load Error", f"Failed to load stock movements: {error}")
                elif isinstance(result, Success):
                    self.movements_model.refresh_data(result.value)
                elif isinstance(result, Failure):
                    QMessageBox.warning(self, "Load Failed", f"Could not load stock movements: {result.error}")
            
            if product_id:
                coro = self.core.inventory_manager.get_stock_movements_for_product(self.company_id, product_id)
            else:
                # TODO: Implement a get_all_stock_movements in manager if needed for general view
                # For now, if no product_id, just clear or show empty.
                self.movements_model.refresh_data([])
                return
            self.async_worker.run_task(coro, on_done_callback=_on_done)
    ```
*   **Acceptance Checklist:**
    *   [ ] `InventoryView` inherits `QWidget`.
    *   [ ] `tab_widget` is used to organize tabs for "Current Stock", "Purchase Orders", "Stock Movements".
    *   [ ] `InventoryTableModel`, `PurchaseOrderTableModel`, `StockMovementTableModel` are implemented as `QAbstractTableModel`s.
    *   [ ] `inventory_table`, `po_table`, `movements_table` are set up with their respective models.
    *   [ ] UI elements (search input, buttons, tables) are created and laid out for each tab.
    *   [ ] `_connect_signals` connects tab changes to `_on_tab_changed`, and buttons/search to their slots.
    *   [ ] `_load_inventory_summary`, `_load_purchase_orders`, `_load_stock_movements` load data via `inventory_manager` using `async_worker.run_task()`.
    *   [ ] `_on_adjust_stock` launches `StockAdjustmentDialog`.
    *   [ ] `_on_new_po` launches `PurchaseOrderDialog`.
    *   [ ] `_on_receive_po_items` and `_on_view_purchase_order_details` are present as placeholders.
    *   [ ] `_on_view_product_stock_history` switches to the `Stock Movements` tab and loads specific product movements.
    *   [ ] `_on_inventory_search` filters the inventory summary.
    *   [ ] All methods handle `Result` objects and provide user feedback.
    *   [ ] Type hinting is complete.

#### **2. `app/ui/dialogs/stock_adjustment_dialog.py`**

*   **File Path:** `app/ui/dialogs/stock_adjustment_dialog.py`
*   **Purpose & Goals:** A `QDialog` for performing stock adjustments. It allows users to add products, input counted quantities, and submit the adjustment, creating an audit trail.
*   **Interfaces:** `StockAdjustmentDialog(core: ApplicationCore, outlet_id: UUID, user_id: UUID)`. Method: `exec()`.
*   **Interactions:** Calls `product_manager.search_products` to find products. Calls `inventory_manager.adjust_stock` via `async_worker.run_task()`.
*   **Code Skeleton:**
    ```python
    # File: app/ui/dialogs/stock_adjustment_dialog.py
    """
    A QDialog for performing stock adjustments.

    This dialog allows users to add products, input their physically counted quantities,
    and submit the adjustment. It orchestrates the process by:
    1. Fetching current stock levels for selected products.
    2. Collecting user input for new quantities and adjustment notes.
    3. Creating a StockAdjustmentDTO.
    4. Calling the InventoryManager to process the adjustment.
    5. Handling the success or failure result from the business logic layer.
    """
    from __future__ import annotations
    from decimal import Decimal
    from typing import List, Optional, Any, Tuple
    import uuid

    from PySide6.QtCore import (
        Qt, QAbstractTableModel, QModelIndex, Slot, Signal, QObject
    )
    from PySide6.QtWidgets import (
        QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit,
        QTableView, QPushButton, QDialogButtonBox, QTextEdit, QMessageBox,
        QHeaderView
    )

    from app.business_logic.dto.inventory_dto import StockAdjustmentDTO, StockAdjustmentItemDTO
    from app.business_logic.dto.product_dto import ProductDTO # For product details
    from app.core.result import Success, Failure
    from app.core.async_bridge import AsyncWorker

    class AdjustmentLineItem(QObject): # Inherit QObject for potential future signals if needed
        def __init__(self, product_id: uuid.UUID, sku: str, name: str, system_qty: Decimal, parent: Optional[QObject] = None):
            super().__init__(parent)
            self.product_id = product_id
            self.sku = sku
            self.name = name
            self.system_qty = system_qty
            self.counted_qty: Optional[Decimal] = None # User input
            
        @property
        def variance(self) -> Decimal:
            if self.counted_qty is None:
                return Decimal("0")
            return (self.counted_qty - self.system_qty).quantize(Decimal("0.0001"))

        def to_stock_adjustment_item_dto(self) -> StockAdjustmentItemDTO:
            return StockAdjustmentItemDTO(product_id=self.product_id, counted_quantity=self.counted_qty if self.counted_qty is not None else Decimal("0"))


    class StockAdjustmentTableModel(QAbstractTableModel):
        """A Qt Table Model for managing items in the stock adjustment dialog."""
        
        HEADERS = ["SKU", "Product Name", "System Quantity", "Counted Quantity", "Variance", "Action"]
        COLUMN_COUNTED_QTY = 3

        def __init__(self, parent: Optional[QObject] = None):
            super().__init__(parent)
            self._items: List[AdjustmentLineItem] = []
            self.data_changed_signal = Signal() # Custom signal for dialog to listen to

        def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
            return len(self._items)

        def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
            return len(self.HEADERS)

        def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
            if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
                return self.HEADERS[section]
            return None

        def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
            if not index.isValid():
                return None
                
            item = self._items[index.row()]
            col = index.column()

            if role == Qt.ItemDataRole.DisplayRole:
                if col == 0: return item.sku
                if col == 1: return item.name
                if col == 2: return str(item.system_qty)
                if col == 3: return str(item.counted_qty) if item.counted_qty is not None else ""
                if col == 4:
                    variance = item.variance
                    return f"+{variance}" if variance > 0 else str(variance)
            
            if role == Qt.ItemDataRole.EditRole and col == self.COLUMN_COUNTED_QTY:
                return str(item.counted_qty) if item.counted_qty is not None else ""

            if role == Qt.ItemDataRole.TextAlignmentRole:
                if col in [2, 3, 4]:
                    return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            
            return None

        def setData(self, index: QModelIndex, value: Any, role: int = Qt.ItemDataRole.EditRole) -> bool:
            if role == Qt.ItemDataRole.EditRole and index.column() == self.COLUMN_COUNTED_QTY:
                try:
                    # Allow empty string to represent None/uncounted
                    if not value.strip():
                        counted_qty = None
                    else:
                        counted_qty = Decimal(value)
                        if counted_qty < 0: # Cannot count negative quantity
                            QMessageBox.warning(self.parent(), "Invalid Quantity", "Counted quantity cannot be negative.")
                            return False

                    self._items[index.row()].counted_qty = counted_qty
                    # Emit dataChanged for both the edited cell and the variance cell
                    self.dataChanged.emit(index, self.createIndex(index.row(), self.columnCount() - 1))
                    self.data_changed_signal.emit() # Notify parent dialog for overall state checks
                    return True
                except (ValueError, TypeError):
                    QMessageBox.warning(self.parent(), "Invalid Input", "Please enter a valid number for quantity.")
                    return False
            return False

        def flags(self, index: QModelIndex) -> Qt.ItemFlag:
            flags = super().flags(index)
            if index.column() == self.COLUMN_COUNTED_QTY: # "Counted Quantity" column is editable
                flags |= Qt.ItemFlag.ItemIsEditable
            return flags

        def add_item(self, item: AdjustmentLineItem):
            # Check if item is already in the list
            for existing_item in self._items:
                if existing_item.product_id == item.product_id:
                    QMessageBox.information(self.parent(), "Duplicate Item", f"Product '{item.name}' (SKU: {item.sku}) is already in the adjustment list.")
                    return
            
            self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
            self._items.append(item)
            self.endInsertRows()
            self.data_changed_signal.emit() # Notify parent dialog

        def remove_item_at_row(self, row_idx: int):
            if 0 <= row_idx < len(self._items):
                self.beginRemoveRows(QModelIndex(), row_idx, row_idx)
                del self._items[row_idx]
                self.endRemoveRows()
                self.data_changed_signal.emit() # Notify parent dialog

        def get_adjustment_items(self) -> List[StockAdjustmentItemDTO]:
            """Returns a list of DTOs for items that have been counted (i.e., counted_qty is not None)."""
            return [
                item.to_stock_adjustment_item_dto()
                for item in self._items if item.counted_qty is not None
            ]

    class StockAdjustmentDialog(QDialog):
        """A dialog for creating and submitting a stock adjustment."""

        def __init__(self, core: ApplicationCore, outlet_id: uuid.UUID, user_id: uuid.UUID, parent: Optional[QObject] = None):
            super().__init__(parent)
            self.core = core
            self.async_worker: AsyncWorker = core.async_worker
            self.company_id = self.core.current_company_id # From core context
            self.outlet_id = outlet_id
            self.user_id = user_id

            self.setWindowTitle("Perform Stock Adjustment")
            self.setMinimumSize(800, 600)

            self._setup_ui()
            self._connect_signals()
            self._on_data_changed() # Initial state check

        def _setup_ui(self):
            """Initializes the UI widgets and layout."""
            # --- Product Search & Add ---
            self.product_search_input = QLineEdit()
            self.product_search_input.setPlaceholderText("Enter Product SKU, Barcode or Name to add...")
            self.add_product_button = QPushButton("Add Product")
            
            search_layout = QHBoxLayout()
            search_layout.addWidget(self.product_search_input, 1)
            search_layout.addWidget(self.add_product_button)
            
            # --- Adjustment Table ---
            self.adjustment_table = QTableView()
            self.table_model = StockAdjustmentTableModel(parent=self)
            self.adjustment_table.setModel(self.table_model)
            self.adjustment_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            self.adjustment_table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
            self.adjustment_table.setSelectionMode(QTableView.SelectionMode.SingleSelection)
            self.adjustment_table.setEditTriggers(QTableView.EditTrigger.DoubleClicked | QTableView.EditTrigger.AnyKeyPressed)
            self.adjustment_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu) # For right-click menu

            # --- Notes & Buttons ---
            self.notes_input = QTextEdit()
            self.notes_input.setPlaceholderText("Provide a reason or notes for this adjustment (e.g., 'Annual stock count', 'Wastage', 'Found items').")
            self.button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
            self.button_box.button(QDialogButtonBox.Save).setText("Submit Adjustment")
            # Disabled initially, enabled when items are counted and notes provided

            # --- Main Layout ---
            main_layout = QVBoxLayout(self)
            main_layout.addLayout(search_layout)
            main_layout.addWidget(self.adjustment_table)
            main_layout.addWidget(QLabel("Adjustment Notes/Reason:"))
            main_layout.addWidget(self.notes_input, 1) # Give notes area more vertical space
            main_layout.addWidget(self.button_box)

        def _connect_signals(self):
            """Connects UI signals to slots."""
            self.add_product_button.clicked.connect(self._on_add_product_clicked)
            self.product_search_input.returnPressed.connect(self._on_add_product_clicked)
            self.button_box.accepted.connect(self._on_submit_adjustment_clicked)
            self.button_box.rejected.connect(self.reject)
            self.table_model.data_changed_signal.connect(self._on_data_changed) # Connect custom signal
            self.notes_input.textChanged.connect(self._on_data_changed) # Also re-check on notes change
            self.adjustment_table.customContextMenuRequested.connect(self._on_table_context_menu)


        @Slot()
        def _on_data_changed(self):
            """Enables/disables the save button based on input validity."""
            has_notes = bool(self.notes_input.toPlainText().strip())
            has_counted_items = bool(self.table_model.get_adjustment_items()) # Only items with counted_qty != None
            
            self.button_box.button(QDialogButtonBox.Save).setEnabled(has_notes and has_counted_items)


        @Slot()
        def _on_add_product_clicked(self):
            """Fetches a product and its stock level and adds it to the table."""
            search_term = self.product_search_input.text().strip()
            if not search_term:
                QMessageBox.warning(self, "Input Required", "Please enter a product SKU, barcode, or name.")
                return

            def _on_done(result: Any, error: Optional[Exception]):
                if error:
                    QMessageBox.critical(self, "Error", f"Failed to search product: {error}")
                elif isinstance(result, Success):
                    products: List[ProductDTO] = result.value
                    if not products:
                        QMessageBox.warning(self, "Not Found", f"No product found for '{search_term}'.")
                        return

                    selected_product = products[0] # Take the first matching product

                    # Now get its current stock level
                    def _on_stock_done(stock_result: Any, stock_error: Optional[Exception]):
                        if stock_error:
                            QMessageBox.critical(self, "Error", f"Failed to get stock level: {stock_error}")
                        elif isinstance(stock_result, Success):
                            system_qty: Decimal = stock_result.value
                            item = AdjustmentLineItem(
                                product_id=selected_product.id,
                                sku=selected_product.sku,
                                name=selected_product.name,
                                system_qty=system_qty
                            )
                            self.table_model.add_item(item)
                            self.product_search_input.clear()
                            self.product_search_input.setFocus()
                        elif isinstance(stock_result, Failure):
                            QMessageBox.warning(self, "Stock Level Failed", f"Could not get stock level: {stock_result.error}")
                    
                    stock_coro = self.core.inventory_service.get_stock_level(self.outlet_id, selected_product.id)
                    self.async_worker.run_task(stock_coro, on_done_callback=_on_stock_done)

                elif isinstance(result, Failure):
                    QMessageBox.warning(self, "Product Lookup Failed", f"Could not find product: {result.error}")
            
            product_search_coro = self.core.product_manager.search_products(self.company_id, search_term, limit=1)
            self.async_worker.run_task(product_search_coro, on_done_callback=_on_done)


        @Slot()
        def _on_submit_adjustment_clicked(self):
            """Gathers data, creates a DTO, and calls the manager to process the adjustment."""
            notes = self.notes_input.toPlainText().strip()
            items_to_adjust = self.table_model.get_adjustment_items()

            # Input validation (also handled by _on_data_changed, but good to re-check)
            if not notes:
                QMessageBox.warning(self, "Notes Required", "Please provide a reason or note for this adjustment.")
                return
            if not items_to_adjust:
                QMessageBox.warning(self, "No Items", "Please enter a counted quantity for at least one item.")
                return

            adjustment_dto = StockAdjustmentDTO(
                company_id=self.company_id,
                outlet_id=self.outlet_id,
                user_id=self.user_id,
                notes=notes,
                items=items_to_adjust
            )
            
            def _on_done(result: Any, error: Optional[Exception]):
                self.button_box.button(QDialogButtonBox.Save).setEnabled(True) # Re-enable button
                if error:
                    QMessageBox.critical(self, "Submission Failed", f"An error occurred: {error}")
                elif isinstance(result, Success):
                    QMessageBox.information(self, "Success", "Stock adjustment submitted successfully.")
                    self.accept() # Closes the dialog with an OK status
                elif isinstance(result, Failure):
                    QMessageBox.warning(self, "Submission Failed", f"Could not submit adjustment: {result.error}")

            # Disable button to prevent double submission
            self.button_box.button(QDialogButtonBox.Save).setEnabled(False)
            coro = self.core.inventory_manager.adjust_stock(adjustment_dto)
            self.async_worker.run_task(coro, on_done_callback=_on_done)

        @Slot(QPoint)
        def _on_table_context_menu(self, pos: QPoint):
            """Shows context menu for the table."""
            index = self.adjustment_table.indexAt(pos)
            if not index.isValid():
                return

            menu = QMenu(self)
            remove_action = menu.addAction("Remove Item")
            
            action = menu.exec(self.adjustment_table.mapToGlobal(pos))
            if action == remove_action:
                self.table_model.remove_item_at_row(index.row())
    ```
*   **Acceptance Checklist:**
    *   [ ] `StockAdjustmentDialog` inherits `QDialog`.
    *   [ ] Constructor accepts `ApplicationCore`, `outlet_id`, `user_id`.
    *   [ ] `AdjustmentLineItem` and `StockAdjustmentTableModel` (using `QAbstractTableModel`) are implemented correctly, with editable quantity and variance display.
    *   [ ] UI elements (search, table, notes, buttons) are created and laid out.
    *   [ ] `_on_data_changed` enables/disables submit button based on notes and counted items.
    *   [ ] `_on_add_product_clicked` calls `product_manager.search_products` and `inventory_service.get_stock_level` via `async_worker.run_task()` to populate the table.
    *   [ ] `_on_submit_adjustment_clicked` constructs `StockAdjustmentDTO` and calls `inventory_manager.adjust_stock` via `async_worker.run_task()`.
    *   [ ] Async operations have `on_done_callback`s that provide `QMessageBox` feedback.
    *   [ ] Context menu (`_on_table_context_menu`) allows removing items.
    *   [ ] Dialog closes on successful submission.

#### **3. `app/ui/dialogs/purchase_order_dialog.py`**

*   **File Path:** `app/ui/dialogs/purchase_order_dialog.py`
*   **Purpose & Goals:** A `QDialog` for creating new Purchase Orders. It allows selecting a supplier, adding products with quantities and costs, and submitting the PO to the `InventoryManager`.
*   **Interfaces:** `PurchaseOrderDialog(core: ApplicationCore, outlet_id: UUID)`. Method: `exec()`.
*   **Interactions:** Calls `supplier_service.get_all_active_methods` (or `get_all` from BaseService), `product_manager.search_products` to populate data. Calls `inventory_manager.create_purchase_order` via `async_worker.run_task()`.
*   **Code Skeleton:**
    ```python
    # File: app/ui/dialogs/purchase_order_dialog.py
    """A QDialog for creating and managing Purchase Orders (POs)."""
    from __future__ import annotations
    from decimal import Decimal
    from typing import List, Optional, Any, Tuple
    import uuid

    from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex, Slot, Signal, QObject, QDate, QPoint
    from PySide6.QtWidgets import (
        QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit,
        QTableView, QPushButton, QDialogButtonBox, QTextEdit, QMessageBox,
        QComboBox, QDateEdit, QHeaderView, QMenu
    )

    from app.business_logic.dto.inventory_dto import PurchaseOrderCreateDTO, PurchaseOrderItemCreateDTO, SupplierDTO
    from app.business_logic.dto.product_dto import ProductDTO # For product search
    from app.core.application_core import ApplicationCore
    from app.core.result import Success, Failure
    from app.core.async_bridge import AsyncWorker

    class POLineItem(QObject): # Inherit QObject
        def __init__(self, product_id: uuid.UUID, sku: str, name: str, unit_cost: Decimal, parent: Optional[QObject] = None):
            super().__init__(parent)
            self.product_id = product_id
            self.sku = sku
            self.name = name
            self.quantity: Decimal = Decimal("1") # Default quantity
            self.unit_cost: Decimal = unit_cost # Default from product, can be edited

        @property
        def total_cost(self) -> Decimal:
            return (self.quantity * self.unit_cost).quantize(Decimal("0.01"))


    class PurchaseOrderTableModel(QAbstractTableModel):
        """A Qt Table Model for managing items in a Purchase Order."""
        
        HEADERS = ["SKU", "Product Name", "Quantity", "Unit Cost", "Total Cost", "Action"]
        COLUMN_QTY = 2
        COLUMN_UNIT_COST = 3

        def __init__(self, parent: Optional[QObject] = None):
            super().__init__(parent)
            self._items: List[POLineItem] = []
            self.total_cost_changed = Signal() # Custom signal for dialog to listen to

        def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
            return len(self._items)

        def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
            return len(self.HEADERS)

        def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
            if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
                return self.HEADERS[section]
            return None

        def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
            if not index.isValid(): return None
            item = self._items[index.row()]
            col = index.column()

            if role == Qt.ItemDataRole.DisplayRole:
                if col == 0: return item.sku
                if col == 1: return item.name
                if col == 2: return str(item.quantity)
                if col == 3: return f"S${item.unit_cost:.2f}"
                if col == 4: return f"S${item.total_cost:.2f}"
            
            if role == Qt.ItemDataRole.EditRole:
                if col == self.COLUMN_QTY: return str(item.quantity)
                if col == self.COLUMN_UNIT_COST: return str(item.unit_cost)
                
            if role == Qt.ItemDataRole.TextAlignmentRole:
                if col in [2, 3, 4]:
                    return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            
            return None

        def setData(self, index: QModelIndex, value: Any, role: int = Qt.ItemDataRole.EditRole) -> bool:
            if role == Qt.ItemDataRole.EditRole:
                item = self._items[index.row()]
                col = index.column()
                try:
                    if col == self.COLUMN_QTY: # Quantity
                        new_qty = Decimal(value)
                        if new_qty <= 0:
                            QMessageBox.warning(self.parent(), "Invalid Quantity", "Quantity must be greater than zero. To remove, use 'Remove Item' option.")
                            return False
                        item.quantity = new_qty
                    elif col == self.COLUMN_UNIT_COST: # Unit Cost
                        new_cost = Decimal(value)
                        if new_cost < 0:
                            QMessageBox.warning(self.parent(), "Invalid Cost", "Unit cost cannot be negative.")
                            return False
                        item.unit_cost = new_cost
                    else:
                        return False
                    
                    # Emit data changed for the row to update total cost and other calculated fields
                    self.dataChanged.emit(self.createIndex(index.row(), 0), self.createIndex(index.row(), self.columnCount() - 1))
                    self.total_cost_changed.emit() # Notify dialog about total cost change
                    return True
                except (ValueError, TypeError):
                    QMessageBox.warning(self.parent(), "Invalid Input", "Please enter a valid number.")
                    return False
            return False

        def flags(self, index: QModelIndex) -> Qt.ItemFlag:
            flags = super().flags(index)
            if index.column() in [self.COLUMN_QTY, self.COLUMN_UNIT_COST]: # Quantity and Unit Cost are editable
                flags |= Qt.ItemFlag.ItemIsEditable
            return flags

        def add_item(self, item: POLineItem):
            # Check for duplicate product
            for existing_item in self._items:
                if existing_item.product_id == item.product_id:
                    QMessageBox.information(self.parent(), "Duplicate Item", f"Product '{item.name}' (SKU: {item.sku}) is already in the PO list. Adjust quantity instead.")
                    return

            self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
            self._items.append(item)
            self.endInsertRows()
            self.total_cost_changed.emit()

        def remove_item_at_row(self, row_idx: int):
            if 0 <= row_idx < len(self._items):
                self.beginRemoveRows(QModelIndex(), row_idx, row_idx)
                del self._items[row_idx]
                self.endRemoveRows()
                self.total_cost_changed.emit()

        def get_total_cost(self) -> Decimal:
            return sum(item.total_cost for item in self._items).quantize(Decimal("0.01"))
        
        def get_po_items_dto(self) -> List[PurchaseOrderItemCreateDTO]:
            return [
                item.to_purchase_order_item_create_dto() # Assuming POLineItem has this method
                for item in self._items
            ]
        
        def has_items(self) -> bool:
            return len(self._items) > 0


    class PurchaseOrderDialog(QDialog):
        """A dialog for creating a new Purchase Order."""

        po_operation_completed = Signal(bool, str) # Signal for InventoryView to refresh

        def __init__(self, core: ApplicationCore, outlet_id: uuid.UUID, parent: Optional[QObject] = None):
            super().__init__(parent)
            self.core = core
            self.async_worker: AsyncWorker = core.async_worker
            self.company_id = self.core.current_company_id
            self.outlet_id = outlet_id

            self.setWindowTitle("Create New Purchase Order")
            self.setMinimumSize(900, 700)

            self._setup_ui()
            self._connect_signals()
            self._load_initial_data() # Load suppliers


        def _setup_ui(self):
            """Initializes the UI widgets and layout."""
            # --- PO Header Form ---
            self.supplier_combo = QComboBox()
            self.po_number_input = QLineEdit() # Optional, can be auto-generated
            self.order_date_edit = QDateEdit(QDate.currentDate())
            self.order_date_edit.setCalendarPopup(True)
            self.expected_delivery_date_edit = QDateEdit(QDate.currentDate().addDays(7)) # Default 7 days
            self.expected_delivery_date_edit.setCalendarPopup(True)
            self.notes_input = QTextEdit()
            
            po_form_layout = QFormLayout()
            po_form_layout.addRow("Supplier:", self.supplier_combo)
            po_form_layout.addRow("PO Number (Optional):", self.po_number_input)
            po_form_layout.addRow("Order Date:", self.order_date_edit)
            po_form_layout.addRow("Expected Delivery:", self.expected_delivery_date_edit)
            po_form_layout.addRow("Notes:", self.notes_input)
            
            # --- Product Search & Add to PO ---
            self.product_search_input = QLineEdit()
            self.product_search_input.setPlaceholderText("Enter Product SKU, Barcode or Name to add to PO...")
            self.add_product_button = QPushButton("Add Item to PO")

            product_search_layout = QHBoxLayout()
            product_search_layout.addWidget(self.product_search_input, 1)
            product_search_layout.addWidget(self.add_product_button)

            # --- PO Items Table ---
            self.po_table = QTableView()
            self.table_model = PurchaseOrderTableModel(parent=self)
            self.po_table.setModel(self.table_model)
            self.po_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            self.po_table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
            self.po_table.setSelectionMode(QTableView.SelectionMode.SingleSelection)
            self.po_table.setEditTriggers(QTableView.EditTrigger.DoubleClicked | QTableView.EditTrigger.AnyKeyPressed)
            self.po_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

            self.total_cost_label = QLabel("<b>Total PO Cost: S$0.00</b>")
            self.total_cost_label.setStyleSheet("font-size: 18px;")
            
            # --- Buttons ---
            self.button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
            self.button_box.button(QDialogButtonBox.Save).setText("Create Purchase Order")
            self.button_box.button(QDialogButtonBox.Save).setEnabled(False) # Disable until items are added

            # --- Main Layout ---
            main_layout = QVBoxLayout(self)
            main_layout.addLayout(po_form_layout)
            main_layout.addLayout(product_search_layout)
            main_layout.addWidget(self.po_table, 1) # Give table space
            main_layout.addWidget(self.total_cost_label, alignment=Qt.AlignmentFlag.AlignRight)
            main_layout.addWidget(self.button_box)


        def _connect_signals(self):
            """Connects UI signals to slots."""
            self.add_product_button.clicked.connect(self._on_add_product_to_po_clicked)
            self.product_search_input.returnPressed.connect(self._on_add_product_to_po_clicked)
            self.button_box.accepted.connect(self._on_submit_po_clicked)
            self.button_box.rejected.connect(self.reject)
            self.table_model.total_cost_changed.connect(self._update_total_cost_label) # Update total label from model
            self.table_model.dataChanged.connect(self._on_table_data_changed) # For checking if items are present
            self.po_table.customContextMenuRequested.connect(self._on_table_context_menu)
            self.supplier_combo.currentIndexChanged.connect(self._on_form_data_changed) # Also check form validity
            self.notes_input.textChanged.connect(self._on_form_data_changed)


        @Slot()
        def _on_form_data_changed(self):
            """Checks form validity to enable/disable save button."""
            has_supplier = self.supplier_combo.currentData() is not None
            has_items = self.table_model.has_items()
            self.button_box.button(QDialogButtonBox.Save).setEnabled(has_supplier and has_items)

        @Slot()
        def _on_table_data_changed(self):
            """Re-checks form validity when table data changes (e.g. last item removed)."""
            self._on_form_data_changed()


        def _load_initial_data(self):
            """Asynchronously loads suppliers to populate the combo box."""
            def _on_done(result: Any, error: Optional[Exception]):
                if error:
                    QMessageBox.critical(self, "Load Error", f"Failed to load suppliers: {error}")
                    self.supplier_combo.setEnabled(False)
                    self.add_product_button.setEnabled(False)
                elif isinstance(result, Success):
                    suppliers: List[SupplierDTO] = result.value
                    self.supplier_combo.clear()
                    if not suppliers:
                        self.supplier_combo.addItem("No Suppliers Available")
                        self.supplier_combo.setEnabled(False)
                        self.add_product_button.setEnabled(False)
                        QMessageBox.warning(self, "No Suppliers", "No active suppliers found. Please add suppliers in settings before creating a PO.")
                        return
                    
                    self.supplier_combo.addItem("-- Select Supplier --", userData=None)
                    for supplier in suppliers:
                        self.supplier_combo.addItem(supplier.name, userData=supplier.id)
                elif isinstance(result, Failure):
                    QMessageBox.warning(self, "Supplier Load Failed", f"Could not load suppliers: {result.error}")
                    self.supplier_combo.setEnabled(False)
                    self.add_product_button.setEnabled(False)

            coro = self.core.inventory_manager.get_all_suppliers(self.company_id) # Or get_all_active_suppliers
            self.async_worker.run_task(coro, on_done_callback=_on_done)


        @Slot()
        def _on_add_product_to_po_clicked(self):
            """Fetches a product and adds it to the PO table."""
            search_term = self.product_search_input.text().strip()
            if not search_term:
                QMessageBox.warning(self, "Input Required", "Please enter a product SKU, barcode or name.")
                return
            
            def _on_done(result: Any, error: Optional[Exception]):
                if error:
                    QMessageBox.critical(self, "Error", f"Failed to search product: {error}")
                elif isinstance(result, Success):
                    products: List[ProductDTO] = result.value
                    if not products:
                        QMessageBox.warning(self, "Not Found", f"No product found for '{search_term}'.")
                        return

                    selected_product: ProductDTO = products[0] # Take the first matching product
                    item = POLineItem(
                        product_id=selected_product.id,
                        sku=selected_product.sku,
                        name=selected_product.name,
                        unit_cost=selected_product.cost_price # Default to product's cost price
                    )
                    self.table_model.add_item(item)
                    self.product_search_input.clear()
                    self.product_search_input.setFocus()
                    self._on_form_data_changed() # Re-evaluate button state
                elif isinstance(result, Failure):
                    QMessageBox.warning(self, "Product Lookup Failed", f"Could not find product: {result.error}")
            
            product_search_coro = self.core.product_manager.search_products(self.company_id, search_term, limit=1)
            self.async_worker.run_task(product_search_coro, on_done_callback=_on_done)


        @Slot()
        def _update_total_cost_label(self):
            """Updates the total PO cost label based on the table model."""
            total_cost = self.table_model.get_total_cost()
            self.total_cost_label.setText(f"<b>Total PO Cost: S${total_cost:.2f}</b>")
            self._on_form_data_changed() # Re-evaluate button state

        @Slot()
        def _on_submit_po_clicked(self):
            """Gathers data, creates a DTO, and calls the manager to create the PO."""
            supplier_id = self.supplier_combo.currentData()
            if not supplier_id:
                QMessageBox.warning(self, "Supplier Required", "Please select a supplier.")
                return

            items_dto = self.table_model.get_po_items_dto()
            if not items_dto:
                QMessageBox.warning(self, "No Items", "Please add at least one item to the purchase order.")
                return
            
            po_number = self.po_number_input.text().strip() or None
            notes = self.notes_input.toPlainText().strip() or None

            po_dto = PurchaseOrderCreateDTO(
                company_id=self.company_id,
                outlet_id=self.outlet_id,
                supplier_id=supplier_id,
                po_number=po_number,
                order_date=self.order_date_edit.date().toPython(),
                expected_delivery_date=self.expected_delivery_date_edit.date().toPython(),
                notes=notes,
                items=items_dto
            )

            def _on_done(result: Any, error: Optional[Exception]):
                self.button_box.button(QDialogButtonBox.Save).setEnabled(True)
                if error:
                    QMessageBox.critical(self, "Creation Failed", f"An error occurred: {error}")
                elif isinstance(result, Success):
                    created_po: PurchaseOrderDTO = result.value
                    QMessageBox.information(self, "Success", f"Purchase Order '{created_po.po_number}' created successfully!")
                    self.po_operation_completed.emit(True, f"PO {created_po.po_number} created.")
                    self.accept()
                elif isinstance(result, Failure):
                    QMessageBox.warning(self, "Creation Failed", f"Could not create Purchase Order: {result.error}")

            self.button_box.button(QDialogButtonBox.Save).setEnabled(False) # Disable to prevent double submission
            coro = self.core.inventory_manager.create_purchase_order(po_dto)
            self.async_worker.run_task(coro, on_done_callback=_on_done)

        @Slot(QPoint)
        def _on_table_context_menu(self, pos: QPoint):
            """Shows context menu for the table."""
            index = self.po_table.indexAt(pos)
            if not index.isValid():
                return

            menu = QMenu(self)
            remove_action = menu.addAction("Remove Item")
            
            action = menu.exec(self.po_table.mapToGlobal(pos))
            if action == remove_action:
                self.table_model.remove_item_at_row(index.row())
    ```
*   **Acceptance Checklist:**
    *   [ ] `PurchaseOrderDialog` inherits `QDialog`.
    *   [ ] Constructor accepts `ApplicationCore` and `outlet_id`.
    *   [ ] `POLineItem` and `PurchaseOrderTableModel` (using `QAbstractTableModel`) are implemented, with editable quantity and unit cost.
    *   [ ] UI elements (supplier combo, date edits, notes, product search, table, total label, buttons) are created.
    *   [ ] `_connect_signals` connects all UI elements.
    *   [ ] `_load_initial_data` loads suppliers via `inventory_manager.get_all_suppliers` using `async_worker.run_task()` and populates `supplier_combo`.
    *   [ ] `_on_add_product_to_po_clicked` calls `product_manager.search_products` to find products and adds them to the table.
    *   [ ] `_update_total_cost_label` correctly updates the total cost.
    *   [ ] `_on_submit_po_clicked` constructs `PurchaseOrderCreateDTO` and calls `inventory_manager.create_purchase_order` via `async_worker.run_task()`.
    *   [ ] Async operations have `on_done_callback`s that provide `QMessageBox` feedback.
    *   [ ] "Create Purchase Order" button is enabled only when a supplier is selected and items are added.
    *   [ ] Context menu allows removing items.

### **Phase 4.5: Update Existing Files**

#### **1. `app/ui/main_window.py`** (Modified from Stage 3)

*   **File Path:** `app/ui/main_window.py`
*   **Purpose & Goals:** Integrate the new `InventoryView` into the main application window and add a navigation option.
*   **Interactions:** Instantiates `InventoryView`, adds it to `QStackedWidget`, and adds "Inventory" action to the menu.
*   **Code Skeleton:**
    ```python
    # File: app/ui/main_window.py
    """
    The main window of the SG-POS application.
    This QMainWindow acts as the shell, hosting different views like the POS screen,
    inventory management, etc., and providing navigation.
    """
    import asyncio
    import sys
    from typing import Optional, Any
    from PySide6.QtWidgets import (
        QMainWindow, QWidget, QVBoxLayout, QLabel,
        QStackedWidget, QMenuBar, QMenu, QMessageBox
    )
    from PySide6.QtCore import Slot, QEvent, QObject, QMetaObject, Qt, QGenericArgument as Q_ARG

    from app.core.application_core import ApplicationCore
    from app.core.async_bridge import AsyncWorker
    from app.core.exceptions import CoreException

    # Import all views that will be hosted
    from app.ui.views.product_view import ProductView
    from app.ui.views.customer_view import CustomerView
    from app.ui.views.pos_view import POSView
    from app.ui.views.inventory_view import InventoryView # NEW: Import InventoryView
    # from app.ui.views.reports_view import ReportsView # To be implemented in Stage 5
    # from app.ui.views.settings_view import SettingsView # To be implemented in Stage 5


    class MainWindow(QMainWindow):
        """The main application window."""

        def __init__(self, core: ApplicationCore):
            """
            Initializes the main window.
            
            Args:
                core: The central ApplicationCore instance.
            """
            super().__init__()
            self.core = core
            self.async_worker: AsyncWorker = core.async_worker

            self.setWindowTitle("SG Point-of-Sale System")
            self.setGeometry(100, 100, 1280, 720)

            # Create a QStackedWidget to hold the different views
            self.stacked_widget = QStackedWidget()
            self.setCentralWidget(self.stacked_widget)

            # --- Initialize and add actual views ---
            self.product_view = ProductView(self.core)
            self.customer_view = CustomerView(self.core)
            self.pos_view = POSView(self.core)
            self.inventory_view = InventoryView(self.core) # NEW: Initialize InventoryView
            # TODO: Initialize other views as they are implemented in later stages
            # self.reports_view = ReportsView(self.core)
            # self.settings_view = SettingsView(self.core)

            # Add views to the stack
            self.stacked_widget.addWidget(self.pos_view)
            self.stacked_widget.addWidget(self.product_view)
            self.stacked_widget.addWidget(self.customer_view)
            self.stacked_widget.addWidget(self.inventory_view) # NEW: Add InventoryView
            # TODO: Add other views here
            
            # Show the POS view by default
            self.stacked_widget.setCurrentWidget(self.pos_view)

            # --- Connect the AsyncWorker's general task_finished signal ---
            self.async_worker.task_finished.connect(self._handle_async_task_result)

            # --- Create menu bar for navigation ---
            self._create_menu()

        def _create_menu(self):
            """Creates the main menu bar with navigation items."""
            menu_bar = self.menuBar()
            
            # File Menu
            file_menu = menu_bar.addMenu("&File")
            exit_action = file_menu.addAction("E&xit")
            exit_action.triggered.connect(self.close)

            # POS Menu
            pos_menu = menu_bar.addMenu("&POS")
            pos_action = pos_menu.addAction("Sales")
            pos_action.triggered.connect(lambda: self.stacked_widget.setCurrentWidget(self.pos_view))

            # Data Management Menu
            data_menu = menu_bar.addMenu("&Data Management")
            product_action = data_menu.addAction("Products")
            product_action.triggered.connect(lambda: self.stacked_widget.setCurrentWidget(self.product_view))
            customer_action = data_menu.addAction("Customers")
            customer_action.triggered.connect(lambda: self.stacked_widget.setCurrentWidget(self.customer_view))

            # Inventory Menu (Populated in Stage 4)
            inventory_menu = menu_bar.addMenu("&Inventory") # NEW
            inventory_action = inventory_menu.addAction("Stock Management") # NEW
            inventory_action.triggered.connect(lambda: self.stacked_widget.setCurrentWidget(self.inventory_view)) # NEW

            # Reports Menu (Populated in Stage 5)
            # reports_menu = menu_bar.addMenu("&Reports")
            # reports_action = reports_menu.addAction("Business Reports")
            # reports_action.triggered.connect(lambda: self.stacked_widget.setCurrentWidget(self.reports_view))

            # Settings Menu (Populated in Stage 5)
            # settings_menu = menu_bar.addMenu("&Settings")
            # settings_action = settings_menu.addAction("Application Settings")
            # settings_action.triggered.connect(lambda: self.stacked_widget.setCurrentWidget(self.settings_view))


        @Slot(object, object)
        def _handle_async_task_result(self, result: Any, error: Optional[Exception]):
            """
            Global handler for results/errors from async tasks that didn't have
            a specific `on_done_callback`. This can be used for general error reporting.
            Individual UI components should still use specific callbacks where needed.
            """
            if error:
                print(f"Unhandled async error: {error}", file=sys.stderr)
                # TODO: Implement more sophisticated global error logging/display
                # QMessageBox.critical(self, "Error", f"An unexpected background error occurred: {error}")

        def closeEvent(self, event: QEvent) -> None:
            """
            Handle window close event to gracefully shut down the application core.
            This ensures database connections and async threads are properly terminated.
            """
            print("Main window closing. Initiating ApplicationCore shutdown...")
            
            async def shutdown_task():
                try:
                    await self.core.shutdown()
                    print("ApplicationCore shutdown complete.")
                except Exception as e:
                    print(f"Error during ApplicationCore shutdown: {e}", file=sys.stderr)
                    QMetaObject.invokeMethod(self, "show_shutdown_error",
                                            Qt.ConnectionType.QueuedConnection,
                                            Q_ARG(str, str(e)))
                QMetaObject.invokeMethod(self, "accept_close_event",
                                         Qt.ConnectionType.QueuedConnection)

            self.async_worker.run_task(shutdown_task())
            
            event.ignore()

        @Slot()
        def accept_close_event(self) -> None:
            """Slot to finally accept the close event after async shutdown completes."""
            QApplication.instance().quit()

        @Slot(str)
        def show_shutdown_error(self, error_message: str) -> None:
            """Displays a critical error message if shutdown fails."""
            QMessageBox.critical(self, "Shutdown Error", f"Failed to gracefully shut down application:\n{error_message}")
    ```
*   **Acceptance Checklist:**
    *   [ ] `InventoryView` is imported and instantiated.
    *   [ ] `InventoryView` is added to the `stacked_widget`.
    *   [ ] "Inventory" menu is created in the menu bar.
    *   [ ] "Stock Management" action is added to the "Inventory" menu and correctly switches the `stacked_widget` to `inventory_view`.

---

This completes the detailed execution plan for Stage 4. The system now has robust inventory and customer relationship management capabilities, built on the solid foundation established in previous stages.

---

## **Stage 5: Business Intelligence & Final Polish - Reporting, GST & Settings**

**Objective:** To build the reporting and analytics features that provide business insights, ensure full regulatory compliance, and add the final layer of professional polish to the application.

### **Phase 5.1: Data Transfer Objects (DTOs) for Reporting & GST**

#### **1. `app/business_logic/dto/reporting_dto.py`**

*   **File Path:** `app/business_logic/dto/reporting_dto.py`
*   **Purpose & Goals:** Defines the data contracts for various business reports (Sales Summary, Inventory Valuation, GST Form 5). These DTOs are read-only and designed for presentation.
*   **Interfaces:** `SalesByPeriodDTO`, `ProductPerformanceDTO`, `SalesSummaryReportDTO`, `InventoryValuationItemDTO`, `InventoryValuationReportDTO`, `GstReportDTO`.
*   **Interactions:** `ReportService` provides raw data to `ReportingManager` and `GstManager`, which then transform it into these DTOs. UI views consume these DTOs for display and export.
*   **Code Skeleton:**
    ```python
    # File: app/business_logic/dto/reporting_dto.py
    """
    Data Transfer Objects (DTOs) for Reporting and Analytics.

    These models define the structure of the data returned by the reporting engine.
    They are read-only and designed for clear presentation in the UI or for export.
    """
    import uuid
    from decimal import Decimal
    from datetime import date, datetime
    from typing import List, Dict, Optional
    from pydantic import BaseModel, Field

    # --- Sales Report DTOs ---

    class SalesByPeriodDTO(BaseModel):
        """Aggregated sales data for a specific period (e.g., a day or month)."""
        period: date = Field(..., description="Date of the period (e.g., day, start of month)")
        total_sales: Decimal = Field(..., decimal_places=2, description="Total sales amount for the period")
        transaction_count: int = Field(..., ge=0, description="Number of transactions in the period")
        average_transaction_value: Decimal = Field(..., decimal_places=2, description="Average value of transactions in the period")

    class ProductPerformanceDTO(BaseModel):
        """Performance metrics for a single product."""
        product_id: uuid.UUID
        sku: str
        name: str
        quantity_sold: Decimal = Field(..., decimal_places=4, description="Total quantity of product sold")
        total_revenue: Decimal = Field(..., decimal_places=2, description="Total revenue generated by the product")
        total_cost: Decimal = Field(..., decimal_places=2, description="Total cost of goods sold for this product")
        gross_margin: Decimal = Field(..., decimal_places=2, description="Gross margin (revenue - cost) for the product")
        gross_margin_percentage: Decimal = Field(..., decimal_places=2, description="Gross margin as a percentage of revenue")


    class SalesSummaryReportDTO(BaseModel):
        """Complete DTO for a comprehensive sales summary report."""
        start_date: date
        end_date: date
        total_revenue: Decimal = Field(..., decimal_places=2, description="Overall total revenue for the report period")
        total_transactions: int = Field(..., ge=0, description="Overall total number of transactions")
        total_discount_amount: Decimal = Field(..., decimal_places=2, description="Overall total discount amount applied")
        total_tax_collected: Decimal = Field(..., decimal_places=2, description="Overall total tax collected")
        
        sales_by_period: List[SalesByPeriodDTO] = Field(..., description="Sales data aggregated by period (e.g., daily)")
        top_performing_products: List[ProductPerformanceDTO] = Field(..., description="List of top-performing products (e.g., top 10 by revenue)")
        # TODO: Add other sections like sales by payment method, sales by cashier, etc.


    # --- Inventory Report DTOs ---

    class InventoryValuationItemDTO(BaseModel):
        product_id: uuid.UUID
        sku: str
        name: str
        quantity_on_hand: Decimal = Field(..., decimal_places=4)
        cost_price: Decimal = Field(..., decimal_places=4)
        total_value: Decimal = Field(..., decimal_places=2) # quantity_on_hand * cost_price

    class InventoryValuationReportDTO(BaseModel):
        """DTO for the inventory valuation report."""
        as_of_date: date
        outlet_id: uuid.UUID
        outlet_name: str # For display
        total_inventory_value: Decimal = Field(..., decimal_places=2)
        total_item_count: int = Field(..., ge=0)
        items: List[InventoryValuationItemDTO]

    # --- GST Report DTOs (IRAS Form 5 Structure) ---

    class GstReportDTO(BaseModel):
        """
        DTO structured to match the fields of the Singapore IRAS GST Form 5.
        This ensures effortless compliance and tax filing.
        All amounts are in SGD.
        """
        company_id: uuid.UUID
        company_name: str # For display on report
        company_gst_reg_no: Optional[str] # For display on report
        start_date: date
        end_date: date
        
        # Box 1: Total value of standard-rated supplies
        box_1_standard_rated_supplies: Decimal = Field(..., decimal_places=2)
        # Box 2: Total value of zero-rated supplies
        box_2_zero_rated_supplies: Decimal = Field(..., decimal_places=2)
        # Box 3: Total value of exempt supplies
        box_3_exempt_supplies: Decimal = Field(..., decimal_places=2)
        # Box 4: Total supplies (Sum of Box 1, 2, 3)
        box_4_total_supplies: Decimal = Field(..., decimal_places=2)
        # Box 5: Total value of taxable purchases (incl. imports)
        box_5_taxable_purchases: Decimal = Field(..., decimal_places=2)
        # Box 6: Output tax due (GST collected on sales)
        box_6_output_tax_due: Decimal = Field(..., decimal_places=2)
        # Box 7: Input tax claimed (GST paid on purchases)
        box_7_input_tax_claimed: Decimal = Field(..., decimal_places=2)
        # Box 8: Adjustments to output tax
        box_8_adjustments_output_tax: Decimal = Field(Decimal("0.00"), decimal_places=2)
        # Box 9: Adjustments to input tax
        box_9_adjustments_input_tax: Decimal = Field(Decimal("0.00"), decimal_places=2)
        # Box 10: (Ignored for this project's scope, for import GST)
        box_10_gst_on_imports: Decimal = Field(Decimal("0.00"), decimal_places=2)
        # Box 11: Refund of GST from customs (Ignored)
        box_11_refund_gst_customs: Decimal = Field(Decimal("0.00"), decimal_places=2)
        # Box 12: (Ignored for this project's scope, for GST payable in suspense account)
        box_12_gst_payable_suspense: Decimal = Field(Decimal("0.00"), decimal_places=2)
        # Box 13: Net GST payable / reclaimable (Box 6 + Box 8 - Box 7 - Box 9 - Box 10 - Box 11 + Box 12)
        box_13_net_gst_payable: Decimal = Field(..., decimal_places=2)
    ```
*   **Acceptance Checklist:**
    *   [ ] All listed DTOs are defined with appropriate fields.
    *   [ ] `Decimal` fields use `decimal_places` for precision.
    *   [ ] `GstReportDTO` accurately reflects the IRAS GST Form 5 structure, including all relevant boxes.
    *   [ ] `ProductPerformanceDTO` includes all necessary performance metrics.
    *   [ ] Docstrings are comprehensive.

### **Phase 5.2: Data Access Layer for Reporting & GST**

#### **1. `app/services/report_service.py`**

*   **File Path:** `app/services/report_service.py`
*   **Purpose & Goals:** Responsible for running complex, efficient data aggregation queries against the database to generate raw data for business reports. This layer uses SQLAlchemy Core or raw SQL for performance.
*   **Interfaces:** `ReportService(core: ApplicationCore)`. Methods: `async get_sales_summary_raw_data(...)`, `async get_product_performance_raw_data(...)`, `async get_inventory_valuation_raw_data(...)`, `async get_gst_f5_raw_data(...)`. All return `Result[List[dict], str]`.
*   **Interactions:** Used by `ReportingManager` and `GstManager`.
*   **Code Skeleton:**
    ```python
    # File: app/services/report_service.py
    """
    Data Access Service for complex reporting queries.

    This service is responsible for running efficient data aggregation queries
    directly against the database to generate the raw data needed for business reports.
    It primarily uses SQLAlchemy Core for performance-critical aggregation.
    """
    from __future__ import annotations
    from typing import TYPE_CHECKING, List, Dict, Any
    from datetime import date, datetime
    from decimal import Decimal
    import sqlalchemy as sa
    from sqlalchemy.future import select
    from sqlalchemy.sql import func, cast

    from app.core.result import Result, Success, Failure
    from app.models.sales import SalesTransaction, SalesTransactionItem
    from app.models.product import Product, Category
    from app.models.inventory import Inventory
    from app.models.payment import Payment # For payment method breakdown if needed
    from app.models.company import Outlet # For outlet names
    # TODO: Import JournalEntry if used for accounting reports

    if TYPE_CHECKING:
        from app.core.application_core import ApplicationCore

    class ReportService:
        """Handles all database aggregation queries for reporting."""

        def __init__(self, core: "ApplicationCore"):
            self.core = core

        async def get_sales_summary_raw_data(self, company_id: uuid.UUID, start_date: date, end_date: date) -> Result[List[Dict[str, Any]], str]:
            """
            Fetches aggregated sales data for a summary report, grouped by day.
            Includes total sales, transaction count, discount, and tax collected.
            Args:
                company_id: The UUID of the company.
                start_date: Start date of the report period (inclusive).
                end_date: End date of the report period (inclusive).
            Returns:
                A Success containing a list of dictionaries with aggregated data, or a Failure.
            """
            try:
                async with self.core.get_session() as session:
                    stmt = (
                        sa.select(
                            func.date(SalesTransaction.transaction_date).label("period"),
                            func.sum(SalesTransaction.total_amount).label("total_sales"),
                            func.count(SalesTransaction.id).label("transaction_count"),
                            func.sum(SalesTransaction.discount_amount).label("total_discount_amount"),
                            func.sum(SalesTransaction.tax_amount).label("total_tax_collected")
                        )
                        .where(
                            SalesTransaction.company_id == company_id,
                            SalesTransaction.transaction_date >= start_date, # Use >= for start
                            SalesTransaction.transaction_date < (end_date + timedelta(days=1)), # Use < for end of day
                            SalesTransaction.status == 'COMPLETED'
                        )
                        .group_by("period")
                        .order_by("period")
                    )
                    
                    result = await session.execute(stmt)
                    rows = [row._asdict() for row in result.all()]
                    return Success(rows)
            except Exception as e:
                return Failure(f"Database error generating sales summary raw data: {e}")

        async def get_product_performance_raw_data(self, company_id: uuid.UUID, start_date: date, end_date: date, limit: int = 10) -> Result[List[Dict[str, Any]], str]:
            """
            Fetches product performance data (quantity sold, revenue, cost, margin).
            Args:
                company_id: The UUID of the company.
                start_date: Start date of the report period.
                end_date: End date of the report period.
                limit: Number of top products to return.
            Returns:
                A Success containing a list of dictionaries with product performance, or a Failure.
            """
            try:
                async with self.core.get_session() as session:
                    stmt = (
                        sa.select(
                            Product.id.label("product_id"),
                            Product.sku.label("sku"),
                            Product.name.label("name"),
                            func.sum(SalesTransactionItem.quantity).label("quantity_sold"),
                            func.sum(SalesTransactionItem.line_total).label("total_revenue"),
                            func.sum(SalesTransactionItem.quantity * SalesTransactionItem.cost_price).label("total_cost")
                        )
                        .join(SalesTransactionItem, SalesTransactionItem.product_id == Product.id)
                        .join(SalesTransaction, SalesTransactionItem.sales_transaction_id == SalesTransaction.id)
                        .where(
                            SalesTransaction.company_id == company_id,
                            SalesTransaction.transaction_date >= start_date,
                            SalesTransaction.transaction_date < (end_date + timedelta(days=1)),
                            SalesTransaction.status == 'COMPLETED'
                        )
                        .group_by(Product.id, Product.sku, Product.name)
                        .order_by(func.sum(SalesTransactionItem.line_total).desc()) # Order by revenue descending
                        .limit(limit)
                    )
                    result = await session.execute(stmt)
                    rows = [row._asdict() for row in result.all()]
                    return Success(rows)
            except Exception as e:
                return Failure(f"Database error generating product performance raw data: {e}")

        async def get_inventory_valuation_raw_data(self, company_id: uuid.UUID, outlet_id: uuid.UUID | None = None) -> Result[List[Dict[str, Any]], str]:
            """
            Fetches raw data for inventory valuation report.
            Args:
                company_id: The UUID of the company.
                outlet_id: Optional UUID of the outlet to filter by.
            Returns:
                A Success containing a list of dictionaries with inventory valuation, or a Failure.
            """
            try:
                async with self.core.get_session() as session:
                    stmt = (
                        sa.select(
                            Product.id.label("product_id"),
                            Product.sku.label("sku"),
                            Product.name.label("name"),
                            Product.cost_price.label("cost_price"),
                            func.coalesce(Inventory.quantity_on_hand, Decimal('0.0')).label("quantity_on_hand")
                        )
                        .join(Inventory, Inventory.product_id == Product.id, isouter=True)
                        .where(Product.company_id == company_id)
                    )
                    if outlet_id:
                        stmt = stmt.where(Inventory.outlet_id == outlet_id)
                    
                    result = await session.execute(stmt)
                    rows = [row._asdict() for row in result.all()]
                    return Success(rows)
            except Exception as e:
                return Failure(f"Database error generating inventory valuation raw data: {e}")

        async def get_gst_f5_raw_data(self, company_id: uuid.UUID, start_date: date, end_date: date) -> Result[Dict[str, Any], str]:
            """
            Fetches all necessary data points for the IRAS GST F5 form.
            This query involves aggregating sales and purchase data based on GST categories.
            Args:
                company_id: The UUID of the company.
                start_date: Start date of the GST period.
                end_date: End date of the GST period.
            Returns:
                A Success containing a dictionary of raw GST data, or a Failure.
            """
            try:
                async with self.core.get_session() as session:
                    # Time delta for inclusive end date
                    from datetime import timedelta
                    report_end_datetime = end_date + timedelta(days=1)

                    # Query for Box 1 (Standard-Rated Supplies) and Box 6 (Output Tax Due)
                    # Assumes product.gst_rate > 0 is standard-rated.
                    sales_data_stmt = (
                        sa.select(
                            func.sum(SalesTransactionItem.line_total).filter(Product.gst_rate > 0).label("standard_rated_sales"),
                            func.sum(SalesTransactionItem.line_total).filter(Product.gst_rate == 0).label("zero_rated_sales"), # For Box 2
                            func.sum(SalesTransaction.tax_amount).label("output_tax_due")
                        )
                        .join(SalesTransactionItem, SalesTransaction.id == SalesTransactionItem.sales_transaction_id)
                        .join(Product, SalesTransactionItem.product_id == Product.id)
                        .where(
                            SalesTransaction.company_id == company_id,
                            SalesTransaction.transaction_date >= start_date,
                            SalesTransaction.transaction_date < report_end_datetime,
                            SalesTransaction.status == 'COMPLETED'
                        )
                    )
                    sales_data_res = (await session.execute(sales_data_stmt)).scalar_one()
                    standard_rated_sales = sales_data_res.standard_rated_sales or Decimal('0.00')
                    zero_rated_sales = sales_data_res.zero_rated_sales or Decimal('0.00')
                    output_tax_due = sales_data_res.output_tax_due or Decimal('0.00')

                    # TODO: Implement query for Box 3 (Exempt Supplies) if applicable.
                    # This would require explicit flagging of products/transactions as exempt.
                    exempt_supplies = Decimal('0.00') # Placeholder

                    # Query for Box 5 (Taxable Purchases) and Box 7 (Input Tax Claimed)
                    # Assumes unit_cost from PurchaseOrderItem is the taxable purchase value.
                    # This is a simplification; actual logic may involve payment method tax status, etc.
                    purchase_data_stmt = (
                        sa.select(
                            func.sum(PurchaseOrderItem.quantity_received * PurchaseOrderItem.unit_cost).label("taxable_purchases"),
                            # Assuming GST is included in unit_cost and needs to be extracted, or tracked separately.
                            # For simplicity, assuming a flat input tax rate for now or that it's embedded.
                            # A real system would need `input_tax_amount` column on PO items or similar.
                            (func.sum(PurchaseOrderItem.quantity_received * PurchaseOrderItem.unit_cost) * Decimal('0.08')).label("input_tax_claimed") # Assuming 8% for demo
                        )
                        .join(PurchaseOrder, PurchaseOrderItem.purchase_order_id == PurchaseOrder.id)
                        .where(
                            PurchaseOrder.company_id == company_id,
                            PurchaseOrder.order_date >= start_date,
                            PurchaseOrder.order_date < report_end_datetime,
                            PurchaseOrder.status.in_(['RECEIVED', 'PARTIALLY_RECEIVED']) # Only received items count
                        )
                    )
                    purchase_data_res = (await session.execute(purchase_data_stmt)).scalar_one()
                    taxable_purchases = purchase_data_res.taxable_purchases or Decimal('0.00')
                    input_tax_claimed = purchase_data_res.input_tax_claimed or Decimal('0.00')


                    data = {
                        "box_1_standard_rated_supplies": standard_rated_sales,
                        "box_2_zero_rated_supplies": zero_rated_sales,
                        "box_3_exempt_supplies": exempt_supplies,
                        "box_6_output_tax_due": output_tax_due,
                        "box_5_taxable_purchases": taxable_purchases,
                        "box_7_input_tax_claimed": input_tax_claimed,
                        # Other boxes are zero for now based on project scope
                    }
                    return Success(data)
            except Exception as e:
                return Failure(f"Database error generating GST F5 raw data: {e}")
    ```
*   **Acceptance Checklist:**
    *   [ ] `ReportService` class is defined.
    *   [ ] `get_sales_summary_raw_data` correctly aggregates sales data by period, including total sales, transaction count, discount, and tax.
    *   [ ] `get_product_performance_raw_data` correctly aggregates product performance data (quantity, revenue, cost) and orders by revenue.
    *   [ ] `get_inventory_valuation_raw_data` correctly fetches product cost and quantity on hand.
    *   [ ] `get_gst_f5_raw_data` implements queries to fetch data for relevant GST boxes (1, 2, 3, 5, 6, 7), joining across `SalesTransaction`, `SalesTransactionItem`, `Product`, `PurchaseOrder`, `PurchaseOrderItem`.
    *   [ ] All aggregation queries use `func.sum()` and handle `None` with `coalesce()`.
    *   [ ] All methods return `Result` and handle exceptions.
    *   [ ] Type hinting is complete.

### **Phase 5.3: Business Logic for Reporting and GST**

#### **1. `app/business_logic/managers/reporting_manager.py`**

*   **File Path:** `app/business_logic/managers/reporting_manager.py`
*   **Purpose & Goals:** Orchestrates the creation of various business reports by fetching raw data from `ReportService` and transforming it into presentable DTOs.
*   **Interfaces:** `ReportingManager(core: ApplicationCore)`. Methods: `async generate_sales_summary_report(...)`, `async generate_inventory_valuation_report(...)`.
*   **Interactions:** Lazy-loads `ReportService`, `ProductService`, `OutletService` (assuming it exists for outlet names). Consumes raw data (List[dict]) and returns structured DTOs.
*   **Code Skeleton:**
    ```python
    # File: app/business_logic/managers/reporting_manager.py
    """Business Logic Manager for generating business reports and analytics."""
    from __future__ import annotations
    from typing import TYPE_CHECKING, List, Dict, Any
    from datetime import date, datetime, timedelta
    from decimal import Decimal
    import uuid

    from app.core.result import Result, Success, Failure
    from app.business_logic.managers.base_manager import BaseManager
    from app.business_logic.dto.reporting_dto import (
        SalesSummaryReportDTO, SalesByPeriodDTO, ProductPerformanceDTO,
        InventoryValuationReportDTO, InventoryValuationItemDTO
    )
    # TODO: Import DTOs for other reports as needed (e.g., Staff Performance)

    if TYPE_CHECKING:
        from app.core.application_core import ApplicationCore
        from app.services.report_service import ReportService
        from app.services.product_service import ProductService
        from app.services.company_service import CompanyService # Assuming a service for Company/Outlet models


    class ReportingManager(BaseManager):
        """Orchestrates the creation of business intelligence reports."""

        @property
        def report_service(self) -> "ReportService":
            return self.core.report_service
        
        @property
        def product_service(self) -> "ProductService":
            return self.core.product_service

        # Assuming a CompanyService exists for fetching Outlet names
        @property
        def outlet_service(self) -> "CompanyService": # CompanyService would handle Outlet as well
            return self.core.company_service # Placeholder, needs a proper OutletService


        async def generate_sales_summary_report(self, company_id: uuid.UUID, start_date: date, end_date: date) -> Result[SalesSummaryReportDTO, str]:
            """
            Generates a comprehensive sales summary report.
            Combines sales data and top product performance.
            Args:
                company_id: The UUID of the company.
                start_date: Start date of the report period.
                end_date: End date of the report period.
            Returns:
                A Success with a SalesSummaryReportDTO, or a Failure.
            """
            # Get sales data aggregated by period
            sales_data_result = await self.report_service.get_sales_summary_raw_data(company_id, start_date, end_date)
            if isinstance(sales_data_result, Failure):
                return sales_data_result
            
            raw_sales_data = sales_data_result.value

            sales_by_period: List[SalesByPeriodDTO] = []
            total_revenue = Decimal("0.00")
            total_transactions = 0
            total_discount_amount = Decimal("0.00")
            total_tax_collected = Decimal("0.00")


            for row in raw_sales_data:
                period_date = row["period"]
                period_sales = row["total_sales"] or Decimal("0.00")
                period_tx_count = row["transaction_count"] or 0
                period_discount = row["total_discount_amount"] or Decimal("0.00")
                period_tax = row["total_tax_collected"] or Decimal("0.00")

                total_revenue += period_sales
                total_transactions += period_tx_count
                total_discount_amount += period_discount
                total_tax_collected += period_tax

                avg_tx_value = period_sales / period_tx_count if period_tx_count > 0 else Decimal("0.00")
                sales_by_period.append(SalesByPeriodDTO(
                    period=period_date,
                    total_sales=period_sales,
                    transaction_count=period_tx_count,
                    average_transaction_value=avg_tx_value
                ))
            
            # Get top performing products
            product_performance_result = await self.report_service.get_product_performance_raw_data(company_id, start_date, end_date, limit=10)
            if isinstance(product_performance_result, Failure):
                # This is an optional part of the report; log error but don't fail entire report generation
                print(f"Warning: Could not fetch top products: {product_performance_result.error}", file=sys.stderr)
                top_products: List[ProductPerformanceDTO] = []
            else:
                top_products = []
                for p_data in product_performance_result.value:
                    total_revenue_prod = p_data['total_revenue'] or Decimal('0.00')
                    total_cost_prod = p_data['total_cost'] or Decimal('0.00')
                    gross_margin_prod = (total_revenue_prod - total_cost_prod).quantize(Decimal("0.01"))
                    gross_margin_pct = (gross_margin_prod / total_revenue_prod * Decimal('100.00')).quantize(Decimal("0.01")) if total_revenue_prod > 0 else Decimal('0.00')
                    top_products.append(ProductPerformanceDTO(
                        product_id=p_data['product_id'],
                        sku=p_data['sku'],
                        name=p_data['name'],
                        quantity_sold=p_data['quantity_sold'] or Decimal('0.00'),
                        total_revenue=total_revenue_prod,
                        total_cost=total_cost_prod,
                        gross_margin=gross_margin_prod,
                        gross_margin_percentage=gross_margin_pct
                    ))

            report_dto = SalesSummaryReportDTO(
                start_date=start_date,
                end_date=end_date,
                total_revenue=total_revenue.quantize(Decimal("0.01")),
                total_transactions=total_transactions,
                total_discount_amount=total_discount_amount.quantize(Decimal("0.01")),
                total_tax_collected=total_tax_collected.quantize(Decimal("0.01")),
                sales_by_period=sales_by_period,
                top_performing_products=top_products
            )
            
            return Success(report_dto)

        async def generate_inventory_valuation_report(self, company_id: uuid.UUID, outlet_id: uuid.UUID | None = None) -> Result[InventoryValuationReportDTO, str]:
            """
            Generates a report showing the current value of inventory.
            Args:
                company_id: The UUID of the company.
                outlet_id: Optional UUID of the outlet to filter by.
            Returns:
                A Success with an InventoryValuationReportDTO, or a Failure.
            """
            raw_data_result = await self.report_service.get_inventory_valuation_raw_data(company_id, outlet_id)
            if isinstance(raw_data_result, Failure):
                return raw_data_result
            
            items_data = raw_data_result.value
            
            total_inventory_value = Decimal('0.00')
            total_item_count = 0
            valuation_items: List[InventoryValuationItemDTO] = []

            for item_data in items_data:
                qty_on_hand = item_data['quantity_on_hand'] or Decimal('0.00')
                cost_price = item_data['cost_price'] or Decimal('0.00')
                total_value_item = (qty_on_hand * cost_price).quantize(Decimal('0.01'))
                
                total_inventory_value += total_value_item
                total_item_count += 1 # Counts distinct products with inventory records

                valuation_items.append(InventoryValuationItemDTO(
                    product_id=item_data['product_id'],
                    sku=item_data['sku'],
                    name=item_data['name'],
                    quantity_on_hand=qty_on_hand,
                    cost_price=cost_price,
                    total_value=total_value_item
                ))
            
            # Get outlet name for report header if filtered by outlet
            outlet_name: Optional[str] = None
            if outlet_id:
                # TODO: Needs an OutletService to fetch outlet name
                # outlet_result = await self.core.outlet_service.get_by_id(outlet_id)
                # if isinstance(outlet_result, Success) and outlet_result.value:
                #     outlet_name = outlet_result.value.name
                outlet_name = "Selected Outlet" # Placeholder

            report_dto = InventoryValuationReportDTO(
                as_of_date=date.today(),
                outlet_id=outlet_id if outlet_id else uuid.UUID('00000000-0000-0000-0000-000000000000'), # Placeholder for "all outlets" ID
                outlet_name=outlet_name or "All Outlets",
                total_inventory_value=total_inventory_value.quantize(Decimal('0.01')),
                total_item_count=total_item_count,
                items=valuation_items
            )
            return Success(report_dto)
        
        # TODO: Add generate_staff_performance_report
        # TODO: Add generate_sales_by_payment_method_report
    ```
*   **Acceptance Checklist:**
    *   [ ] `ReportingManager` inherits `BaseManager`.
    *   [ ] `report_service` and `product_service` (and other services needed) are lazy-loaded.
    *   [ ] `generate_sales_summary_report` calls `report_service.get_sales_summary_raw_data` and `get_product_performance_raw_data`.
    *   [ ] It correctly aggregates the raw data and transforms it into `SalesSummaryReportDTO` and `ProductPerformanceDTO` (including margin calculations).
    *   [ ] `generate_inventory_valuation_report` calls `report_service.get_inventory_valuation_raw_data`.
    *   [ ] It calculates total inventory value and populates `InventoryValuationReportDTO`.
    *   [ ] All methods return `Result` and handle errors.
    *   [ ] Type hinting is complete.

#### **2. `app/business_logic/managers/gst_manager.py`**

*   **File Path:** `app/business_logic/managers/gst_manager.py`
*   **Purpose & Goals:** Handles all Singapore GST compliance logic and reporting, specifically for the IRAS GST Form 5.
*   **Interfaces:** `GstManager(core: ApplicationCore)`. Methods: `async generate_gst_f5_report(...)`.
*   **Interactions:** Lazy-loads `ReportService` and `CompanyService` (for company details). Consumes raw data from `ReportService` and transforms into `GstReportDTO`.
*   **Code Skeleton:**
    ```python
    # File: app/business_logic/managers/gst_manager.py
    """Business Logic Manager for GST compliance and reporting."""
    from __future__ import annotations
    from typing import TYPE_CHECKING
    from datetime import date
    from decimal import Decimal
    import uuid

    from app.core.result import Result, Success, Failure
    from app.business_logic.managers.base_manager import BaseManager
    from app.business_logic.dto.reporting_dto import GstReportDTO

    if TYPE_CHECKING:
        from app.core.application_core import ApplicationCore
        from app.services.report_service import ReportService
        from app.services.company_service import CompanyService # Assuming a CompanyService exists


    class GstManager(BaseManager):
        """Handles logic related to Singapore GST compliance."""

        @property
        def report_service(self) -> "ReportService":
            return self.core.report_service

        @property
        def company_service(self) -> "CompanyService":
            return self.core.company_service # Placeholder, needs a proper CompanyService


        async def generate_gst_f5_report(self, company_id: uuid.UUID, start_date: date, end_date: date) -> Result[GstReportDTO, str]:
            """
            Generates the data needed for an IRAS GST Form 5.
            Args:
                company_id: The UUID of the company.
                start_date: Start date of the GST period.
                end_date: End date of the GST period.
            Returns:
                A Success with a GstReportDTO, or a Failure.
            """
            company_result = await self.company_service.get_by_id(company_id)
            if isinstance(company_result, Failure) or company_result.value is None:
                return Failure(f"Company with ID {company_id} not found.")
            company = company_result.value

            data_result = await self.report_service.get_gst_f5_raw_data(company_id, start_date, end_date)
            if isinstance(data_result, Failure):
                return data_result
                
            data = data_result.value
            
            # Retrieve values from raw data, defaulting to 0 if not present
            box_1 = data.get("box_1_standard_rated_supplies", Decimal("0.00"))
            box_2 = data.get("box_2_zero_rated_supplies", Decimal("0.00"))
            box_3 = data.get("box_3_exempt_supplies", Decimal("0.00"))
            box_5 = data.get("box_5_taxable_purchases", Decimal("0.00"))
            box_6 = data.get("box_6_output_tax_due", Decimal("0.00"))
            box_7 = data.get("box_7_input_tax_claimed", Decimal("0.00"))

            # Perform final calculations as per IRAS Form 5 logic
            box_4 = (box_1 + box_2 + box_3).quantize(Decimal("0.01"))
            # Box 8, 9, 10, 11, 12 are assumed zero for MVP scope
            box_8 = Decimal("0.00")
            box_9 = Decimal("0.00")
            box_10 = Decimal("0.00")
            box_11 = Decimal("0.00")
            box_12 = Decimal("0.00")

            box_13_net_gst_payable = (box_6 + box_8 - box_7 - box_9 - box_10 - box_11 + box_12).quantize(Decimal("0.01"))
            
            report_dto = GstReportDTO(
                company_id=company_id,
                company_name=company.name,
                company_gst_reg_no=company.gst_registration_number,
                start_date=start_date,
                end_date=end_date,
                box_1_standard_rated_supplies=box_1,
                box_2_zero_rated_supplies=box_2,
                box_3_exempt_supplies=box_3,
                box_4_total_supplies=box_4,
                box_5_taxable_purchases=box_5,
                box_6_output_tax_due=box_6,
                box_7_input_tax_claimed=box_7,
                box_8_adjustments_output_tax=box_8,
                box_9_adjustments_input_tax=box_9,
                box_10_gst_on_imports=box_10,
                box_11_refund_gst_customs=box_11,
                box_12_gst_payable_suspense=box_12,
                box_13_net_gst_payable=box_13_net_gst_payable
            )
            
            return Success(report_dto)
        
        # TODO: Add generate_iras_audit_file (IAF) logic
    ```
*   **Acceptance Checklist:**
    *   [ ] `GstManager` inherits `BaseManager`.
    *   [ ] `report_service` and `company_service` (or equivalent) are lazy-loaded.
    *   [ ] `generate_gst_f5_report` calls `report_service.get_gst_f5_raw_data`.
    *   [ ] It correctly calculates all GST Form 5 boxes, including the net GST payable/reclaimable.
    *   [ ] It includes company name and GST reg no in the DTO.
    *   [ ] All methods return `Result` and handle errors.
    *   [ ] Type hinting is complete.

#### **3. (Optional, but recommended for full scope) `app/services/company_service.py`**

*   **File Path:** `app/services/company_service.py`
*   **Purpose & Goals:** Provides data access for `Company` and `Outlet` models.
*   **Interfaces:** `CompanyService(core: ApplicationCore)`. Inherits from `BaseService` for `Company` and provides specific methods for `Outlet`.
*   **Interactions:** Used by `GstManager`, `ReportingManager`, `InventoryManager`, etc.
*   **Code Skeleton:**
    ```python
    # File: app/services/company_service.py
    """Data Access Service (Repository) for Company and Outlet entities."""
    from __future__ import annotations
    from typing import TYPE_CHECKING, List
    from uuid import UUID
    import sqlalchemy as sa
    from sqlalchemy.future import select

    from app.core.result import Result, Success, Failure
    from app.models.company import Company, Outlet # Import ORM models
    from app.services.base_service import BaseService

    if TYPE_CHECKING:
        from app.core.application_core import ApplicationCore

    class CompanyService(BaseService):
        """
        Handles database interactions for Company models.
        Inherits generic CRUD from BaseService for Company.
        """
        def __init__(self, core: "ApplicationCore"):
            super().__init__(core, Company)

        # You can add specific methods here for Company if needed, e.g., get_by_registration_number

    class OutletService(BaseService):
        """
        Handles database interactions for Outlet models.
        Inherits generic CRUD from BaseService for Outlet.
        """
        def __init__(self, core: "ApplicationCore"):
            super().__init__(core, Outlet)

        async def get_by_code(self, company_id: UUID, code: str) -> Result[Outlet | None, str]:
            """Fetches an outlet by its unique code for a given company."""
            try:
                async with self.core.get_session() as session:
                    stmt = select(Outlet).where(
                        Outlet.company_id == company_id,
                        Outlet.code == code
                    )
                    result = await session.execute(stmt)
                    outlet = result.scalar_one_or_none()
                    return Success(outlet)
            except Exception as e:
                return Failure(f"Database error fetching outlet by code '{code}': {e}")
        
        async def get_all_by_company(self, company_id: UUID) -> Result[List[Outlet], str]:
            """Fetches all outlets for a specific company."""
            try:
                async with self.core.get_session() as session:
                    stmt = select(Outlet).where(Outlet.company_id == company_id, Outlet.is_active == True)
                    result = await session.execute(stmt)
                    outlets = result.scalars().all()
                    return Success(outlets)
            except Exception as e:
                return Failure(f"Database error fetching outlets for company {company_id}: {e}")
    ```
*   **Acceptance Checklist:**
    *   [ ] `CompanyService` (inheriting from `BaseService` for `Company`) is defined.
    *   [ ] `OutletService` (inheriting from `BaseService` for `Outlet`) is defined.
    *   [ ] `OutletService.get_by_code` and `get_all_by_company` methods are implemented.
    *   [ ] All methods return `Result` and use `async with self.core.get_session()`.

### **Phase 5.4: UI for Reporting and Settings**

#### **1. `app/ui/views/reports_view.py`**

*   **File Path:** `app/ui/views/reports_view.py`
*   **Purpose & Goals:** Provides the UI for generating and displaying various business reports (Sales Summary, Inventory Valuation, GST Form 5). It also offers export options.
*   **Interfaces:** `ReportsView(core: ApplicationCore)`.
*   **Interactions:** Calls `reporting_manager.generate_sales_summary_report`, `inventory_manager.generate_inventory_valuation_report`, `gst_manager.generate_gst_f5_report` via `async_worker.run_task()`. Uses `reportlab` and `openpyxl` for export (these are separate utility functions, not directly part of the view logic).
*   **Code Skeleton:**
    ```python
    # File: app/ui/views/reports_view.py
    """The main view for generating and displaying reports."""
    from __future__ import annotations
    from typing import List, Any, Optional
    from datetime import date, timedelta
    from decimal import Decimal

    from PySide6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QComboBox,
        QPushButton, QDateEdit, QTableWidget, QTableWidgetItem, QLabel,
        QHeaderView, QSizePolicy, QMessageBox, QScrollArea
    )
    from PySide6.QtCore import Slot, QDate, QAbstractTableModel, QModelIndex, Qt, QObject

    from app.core.application_core import ApplicationCore
    from app.core.result import Success, Failure
    from app.business_logic.dto.reporting_dto import (
        SalesSummaryReportDTO, GstReportDTO, InventoryValuationReportDTO,
        SalesByPeriodDTO, ProductPerformanceDTO, InventoryValuationItemDTO
    )
    from app.core.async_bridge import AsyncWorker
    # TODO: Import report generation utilities (e.g., pdf_exporter, excel_exporter)

    # --- Reusable Table Models for Reports ---
    class SalesByPeriodTableModel(QAbstractTableModel):
        HEADERS = ["Date", "Total Sales (S$)", "Transactions", "Avg. Tx Value (S$)"]
        def __init__(self, data: List[SalesByPeriodDTO], parent: Optional[QObject] = None):
            super().__init__(parent)
            self._data = data
        def rowCount(self, parent: QModelIndex = QModelIndex()) -> int: return len(self._data)
        def columnCount(self, parent: QModelIndex = QModelIndex()) -> int: return len(self.HEADERS)
        def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
            if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal: return self.HEADERS[section]
            return None
        def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
            if not index.isValid(): return None
            item = self._data[index.row()]
            col = index.column()
            if role == Qt.ItemDataRole.DisplayRole:
                if col == 0: return item.period.strftime("%Y-%m-%d")
                if col == 1: return f"{item.total_sales:.2f}"
                if col == 2: return str(item.transaction_count)
                if col == 3: return f"{item.average_transaction_value:.2f}"
            if role == Qt.ItemDataRole.TextAlignmentRole and col in [1,2,3]: return Qt.AlignRight | Qt.AlignVCenter
            return None
        def refresh_data(self, new_data: List[SalesByPeriodDTO]): self.beginResetModel(); self._data = new_data; self.endResetModel()

    class ProductPerformanceTableModel(QAbstractTableModel):
        HEADERS = ["SKU", "Product Name", "Qty Sold", "Revenue (S$)", "Margin (S$)", "Margin (%)"]
        def __init__(self, data: List[ProductPerformanceDTO], parent: Optional[QObject] = None):
            super().__init__(parent)
            self._data = data
        def rowCount(self, parent: QModelIndex = QModelIndex()) -> int: return len(self._data)
        def columnCount(self, parent: QModelIndex = QModelIndex()) -> int: return len(self.HEADERS)
        def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
            if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal: return self.HEADERS[section]
            return None
        def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
            if not index.isValid(): return None
            item = self._data[index.row()]
            col = index.column()
            if role == Qt.ItemDataRole.DisplayRole:
                if col == 0: return item.sku
                if col == 1: return item.name
                if col == 2: return str(item.quantity_sold)
                if col == 3: return f"{item.total_revenue:.2f}"
                if col == 4: return f"{item.gross_margin:.2f}"
                if col == 5: return f"{item.gross_margin_percentage:.2f}%"
            if role == Qt.ItemDataRole.TextAlignmentRole and col in [2,3,4,5]: return Qt.AlignRight | Qt.AlignVCenter
            return None
        def refresh_data(self, new_data: List[ProductPerformanceDTO]): self.beginResetModel(); self._data = new_data; self.endResetModel()

    class InventoryValuationTableModel(QAbstractTableModel):
        HEADERS = ["SKU", "Product Name", "Qty On Hand", "Cost Price (S$)", "Total Value (S$)"]
        def __init__(self, data: List[InventoryValuationItemDTO], parent: Optional[QObject] = None):
            super().__init__(parent)
            self._data = data
        def rowCount(self, parent: QModelIndex = QModelIndex()) -> int: return len(self._data)
        def columnCount(self, parent: QModelIndex = QModelIndex()) -> int: return len(self.HEADERS)
        def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
            if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal: return self.HEADERS[section]
            return None
        def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
            if not index.isValid(): return None
            item = self._data[index.row()]
            col = index.column()
            if role == Qt.ItemDataRole.DisplayRole:
                if col == 0: return item.sku
                if col == 1: return item.name
                if col == 2: return str(item.quantity_on_hand)
                if col == 3: return f"{item.cost_price:.2f}"
                if col == 4: return f"{item.total_value:.2f}"
            if role == Qt.ItemDataRole.TextAlignmentRole and col in [2,3,4]: return Qt.AlignRight | Qt.AlignVCenter
            return None
        def refresh_data(self, new_data: List[InventoryValuationItemDTO]): self.beginResetModel(); self._data = new_data; self.endResetModel()


    class ReportsView(QWidget):
        """UI for generating and viewing business reports."""

        def __init__(self, core: ApplicationCore, parent: Optional[QObject] = None):
            super().__init__(parent)
            self.core = core
            self.async_worker: AsyncWorker = core.async_worker
            self.company_id = self.core.current_company_id # From core context
            self.outlet_id = self.core.current_outlet_id # For inventory report filtering if needed

            self._setup_ui()
            self._connect_signals()
            self._set_default_dates()

        def _setup_ui(self):
            """Build the user interface."""
            # --- Controls ---
            controls_layout = QHBoxLayout()
            self.report_selector = QComboBox()
            self.report_selector.addItems(["Sales Summary Report", "Inventory Valuation Report", "GST Form 5"])
            
            self.start_date_edit = QDateEdit()
            self.start_date_edit.setCalendarPopup(True)
            self.end_date_edit = QDateEdit()
            self.end_date_edit.setCalendarPopup(True)
            
            self.generate_button = QPushButton("Generate Report")
            self.export_pdf_button = QPushButton("Export PDF")
            self.export_csv_button = QPushButton("Export CSV")

            controls_layout.addWidget(QLabel("Report:"))
            controls_layout.addWidget(self.report_selector)
            controls_layout.addWidget(QLabel("From:"))
            controls_layout.addWidget(self.start_date_edit)
            controls_layout.addWidget(QLabel("To:"))
            controls_layout.addWidget(self.end_date_edit)
            controls_layout.addStretch()
            controls_layout.addWidget(self.generate_button)
            controls_layout.addWidget(self.export_pdf_button)
            controls_layout.addWidget(self.export_csv_button)

            # --- Display Area (using QScrollArea for flexibility) ---
            self.report_content_widget = QWidget()
            self.report_content_layout = QVBoxLayout(self.report_content_widget)
            self.report_content_layout.addWidget(QLabel("Select a report and date range, then click 'Generate Report'."))
            self.report_content_layout.addStretch() # Push content to top

            self.report_scroll_area = QScrollArea()
            self.report_scroll_area.setWidgetResizable(True)
            self.report_scroll_area.setWidget(self.report_content_widget)

            # --- Main Layout ---
            main_layout = QVBoxLayout(self)
            main_layout.addLayout(controls_layout)
            main_layout.addWidget(self.report_scroll_area) # Add scroll area
            self.setLayout(main_layout)
            self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        def _set_default_dates(self):
            """Sets default date ranges for reports (e.g., last month or current quarter)."""
            today = QDate.currentDate()
            # Default to last month
            self.end_date_edit.setDate(today)
            self.start_date_edit.setDate(today.addMonths(-1).day(1)) # First day of previous month

            # For GST, set to last quarter
            # current_month = today.month()
            # if current_month <= 3: # Q1 ends in March, use previous year Q4
            #     self.start_date_edit.setDate(QDate(today.year() - 1, 10, 1))
            #     self.end_date_edit.setDate(QDate(today.year() - 1, 12, 31))
            # elif current_month <= 6: # Q2 ends in June
            #     self.start_date_edit.setDate(QDate(today.year(), 4, 1))
            #     self.end_date_edit.setDate(QDate(today.year(), 6, 30))
            # elif current_month <= 9: # Q3 ends in Sept
            #     self.start_date_edit.setDate(QDate(today.year(), 7, 1))
            #     self.end_date_edit.setDate(QDate(today.year(), 9, 30))
            # else: # Q4 ends in Dec
            #     self.start_date_edit.setDate(QDate(today.year(), 10, 1))
            #     self.end_date_edit.setDate(QDate(today.year(), 12, 31))

        def _connect_signals(self):
            """Connects UI signals to slots."""
            self.generate_button.clicked.connect(self._on_generate_report_clicked)
            self.export_pdf_button.clicked.connect(self._on_export_pdf_clicked)
            self.export_csv_button.clicked.connect(self._on_export_csv_clicked)

        def _clear_display_area(self):
            """Helper to clear the previous report content."""
            while self.report_content_layout.count() > 0:
                item = self.report_content_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
                elif item.layout():
                    self._clear_layout(item.layout())
            self.report_content_layout.addStretch() # Add stretch back after clearing

        def _clear_layout(self, layout: QVBoxLayout | QHBoxLayout | QFormLayout):
            """Recursively clears a layout."""
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
                elif item.layout():
                    self._clear_layout(item.layout())


        @Slot()
        def _on_generate_report_clicked(self):
            """Generates the selected report asynchronously."""
            report_name = self.report_selector.currentText()
            start_date_py = self.start_date_edit.date().toPython()
            end_date_py = self.end_date_edit.date().toPython()
            
            if start_date_py > end_date_py:
                QMessageBox.warning(self, "Invalid Date Range", "Start date cannot be after end date.")
                return

            self._clear_display_area()
            self.generate_button.setEnabled(False) # Disable button during generation
            self.export_pdf_button.setEnabled(False)
            self.export_csv_button.setEnabled(False)
            self.report_content_layout.addWidget(QLabel("Generating report... Please wait."))


            def _on_done(result: Any, error: Optional[Exception]):
                self.generate_button.setEnabled(True)
                self._clear_display_area() # Clear "generating" message

                if error:
                    QMessageBox.critical(self, "Report Error", f"An error occurred during report generation: {error}")
                    self.report_content_layout.addWidget(QLabel(f"Error generating report: {error}"))
                    self.report_content_layout.addStretch()
                elif isinstance(result, Success):
                    self.report_content_layout.addWidget(QLabel(f"<h3>{report_name} ({start_date_py.strftime('%Y-%m-%d')} to {end_date_py.strftime('%Y-%m-%d')})</h3>"))
                    
                    if report_name == "Sales Summary Report":
                        self._display_sales_summary_report(result.value)
                    elif report_name == "Inventory Valuation Report":
                        self._display_inventory_valuation_report(result.value)
                    elif report_name == "GST Form 5":
                        self._display_gst_report(result.value)

                    self.report_content_layout.addStretch()
                    self.export_pdf_button.setEnabled(True)
                    self.export_csv_button.setEnabled(True)

                elif isinstance(result, Failure):
                    QMessageBox.warning(self, "Report Failed", f"Could not generate report: {result.error}")
                    self.report_content_layout.addWidget(QLabel(f"Failed to generate report: {result.error}"))
                    self.report_content_layout.addStretch()
                
            coro = None
            if report_name == "Sales Summary Report":
                coro = self.core.reporting_manager.generate_sales_summary_report(self.company_id, start_date_py, end_date_py)
            elif report_name == "Inventory Valuation Report":
                coro = self.core.reporting_manager.generate_inventory_valuation_report(self.company_id, self.outlet_id) # Can filter by outlet
            elif report_name == "GST Form 5":
                coro = self.core.gst_manager.generate_gst_f5_report(self.company_id, start_date_py, end_date_py)
            
            if coro:
                self.async_worker.run_task(coro, on_done_callback=_on_done)
            else:
                QMessageBox.warning(self, "Not Implemented", "Selected report type is not yet implemented.")
                self.generate_button.setEnabled(True)
                self.report_content_layout.addWidget(QLabel("Selected report type is not yet implemented."))
                self.report_content_layout.addStretch()


        def _display_sales_summary_report(self, report_dto: SalesSummaryReportDTO):
            """Renders the Sales Summary Report DTO in the UI."""
            self.report_content_layout.addWidget(QLabel(f"<b>Overall Revenue: S${report_dto.total_revenue:.2f}</b>"))
            self.report_content_layout.addWidget(QLabel(f"<b>Total Transactions: {report_dto.total_transactions}</b>"))
            self.report_content_layout.addWidget(QLabel(f"Total Discount: S${report_dto.total_discount_amount:.2f}"))
            self.report_content_layout.addWidget(QLabel(f"Total GST Collected: S${report_dto.total_tax_collected:.2f}"))

            self.report_content_layout.addWidget(QLabel("<br><b>Sales by Period:</b>"))
            sales_by_period_table = QTableView()
            sales_by_period_table.setModel(SalesByPeriodTableModel(report_dto.sales_by_period))
            sales_by_period_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            self.report_content_layout.addWidget(sales_by_period_table)

            self.report_content_layout.addWidget(QLabel("<br><b>Top Performing Products:</b>"))
            product_performance_table = QTableView()
            product_performance_table.setModel(ProductPerformanceTableModel(report_dto.top_performing_products))
            product_performance_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            self.report_content_layout.addWidget(product_performance_table)


        def _display_inventory_valuation_report(self, report_dto: InventoryValuationReportDTO):
            """Renders the Inventory Valuation Report DTO in the UI."""
            self.report_content_layout.addWidget(QLabel(f"<b>Inventory Valuation as of {report_dto.as_of_date.strftime('%Y-%m-%d')} for {report_dto.outlet_name}</b>"))
            self.report_content_layout.addWidget(QLabel(f"<b>Total Inventory Value: S${report_dto.total_inventory_value:.2f}</b>"))
            self.report_content_layout.addWidget(QLabel(f

---
https://drive.google.com/file/d/108RlhMVaufy_hYAq9aWl4fJT0Nc_LB2k/view?usp=sharing, https://drive.google.com/file/d/1DVVDdJPIYRsNjaL1TBK0pyivBT9T3KcR/view?usp=sharing, https://drive.google.com/file/d/1Dv92K22sZCR81fKux1KGaRKSj8Jv-Uyc/view?usp=sharing, https://aistudio.google.com/app/prompts?state=%7B%22ids%22:%5B%221HJO6Ey-cx-eWjXUJuYEitWEe9fWU1I7v%22%5D,%22action%22:%22open%22,%22userId%22:%22103961307342447084491%22,%22resourceKeys%22:%7B%7D%7D&usp=sharing, https://drive.google.com/file/d/1O8RKDf9T_KQwxh_rkPefDZVRvLlJpeOW/view?usp=sharing, https://drive.google.com/file/d/1SzHas3aRVlLw8XZ5_aNYK9dhML_2ea-b/view?usp=sharing, https://drive.google.com/file/d/1cshXJfKI6TJeVUZKw_xMxdF0Ly-V9Anu/view?usp=sharing, https://drive.google.com/file/d/1gTl2UasRWjqn51dY_Ouh_io0JM4zvxOj/view?usp=sharing, https://drive.google.com/file/d/1l2E0gN419jGB6-aopwZySbqPiKbZLfCf/view?usp=sharing, https://drive.google.com/file/d/1nrRKmVq24tyRexjTP6PcrDYAYdreLm4u/view?usp=sharing, https://drive.google.com/file/d/1wjCj8KX8Cs8MeVz0a4FWLB7hoeUhSJJe/view?usp=sharing, https://drive.google.com/file/d/1yf-0upWQE6xmB3LxWX6yCtOzUIRt-sDo/view?usp=sharing

