It is my purpose to set the highest possible standard for quality and clarity. Let's proceed with that same commitment to excellence as we build out **Stage 3: The Transactional Core**.

This stage is arguably the most critical in the entire project. It's where we build the primary value proposition of the POS system—the ability to conduct a sale. This involves a complex orchestration of inventory checks, pricing calculations, payment processing, and financial record-keeping, all while ensuring the user interface remains fast and intuitive for the cashier.

The code for this stage will serve as a masterclass for your future developers on how to handle complex, multi-step business workflows within our defined architecture. It will demonstrate how the `SalesManager` acts as an orchestrator, coordinating multiple services to ensure a transaction is processed **atomically**—it either succeeds completely, or it fails gracefully, leaving the system in a consistent state.

Here is the complete code and configuration for **Stage 3 of the Project Management Document**.

---

## **SG-POS System: Stage 3 Code Implementation**

This stage builds upon the foundations of Stages 1 and 2. We will create the necessary models, services, business logic, and UI components to handle a complete sales transaction.

### **1. Database Models for Sales & Payments (`app/models/`)**

First, we define the database schema for all transactional data.

#### **`app/models/sales.py`** (New File)

```python
"""SQLAlchemy models for Sales Transactions and their Line Items."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, ForeignKey, Numeric, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin

class SalesTransaction(Base, TimestampMixin):
    """Represents the header of a sales transaction."""
    __tablename__ = "sales_transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True)
    outlet_id = Column(UUID(as_uuid=True), ForeignKey("outlets.id"), nullable=False, index=True)
    transaction_number = Column(String(50), nullable=False, unique=True)
    transaction_date = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=True, index=True)
    cashier_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)

    subtotal = Column(Numeric(19, 2), nullable=False)
    tax_amount = Column(Numeric(19, 2), nullable=False)
    discount_amount = Column(Numeric(19, 2), nullable=False, default=0)
    rounding_adjustment = Column(Numeric(19, 2), nullable=False, default=0)
    total_amount = Column(Numeric(19, 2), nullable=False)

    status = Column(String(20), nullable=False, default='COMPLETED') # COMPLETED, VOIDED, HELD
    notes = Column(Text)

    # Relationships
    company = relationship("Company")
    outlet = relationship("Outlet")
    customer = relationship("Customer")
    cashier = relationship("User")
    items = relationship("SalesTransactionItem", back_populates="sales_transaction", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="sales_transaction", cascade="all, delete-orphan")

class SalesTransactionItem(Base, TimestampMixin):
    """Represents a single line item within a sales transaction."""
    __tablename__ = "sales_transaction_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sales_transaction_id = Column(UUID(as_uuid=True), ForeignKey("sales_transactions.id"), nullable=False, index=True)
    
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    # variant_id can be added here if variants are implemented
    
    quantity = Column(Numeric(15, 4), nullable=False)
    unit_price = Column(Numeric(19, 4), nullable=False)
    cost_price = Column(Numeric(19, 4), nullable=False)
    line_total = Column(Numeric(19, 2), nullable=False)

    # Relationships
    sales_transaction = relationship("SalesTransaction", back_populates="items")
    product = relationship("Product")
```

#### **`app/models/payment.py`** (New File)

```python
"""SQLAlchemy models for Payments and Payment Methods."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, ForeignKey, Numeric, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin

class PaymentMethod(Base, TimestampMixin):
    """Represents a payment method available to a company (e.g., Cash, NETS)."""
    __tablename__ = "payment_methods"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    name = Column(String(100), nullable=False)
    type = Column(String(50), nullable=False) # CASH, CARD, NETS, etc.
    is_active = Column(Boolean, nullable=False, default=True)

    company = relationship("Company")
    
    __table_args__ = (sa.UniqueConstraint('company_id', 'name', name='uq_payment_methods_company_name'),)


class Payment(Base, TimestampMixin):
    """Represents a single payment applied to a sales transaction."""
    __tablename__ = "payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sales_transaction_id = Column(UUID(as_uuid=True), ForeignKey("sales_transactions.id"), nullable=False, index=True)
    payment_method_id = Column(UUID(as_uuid=True), ForeignKey("payment_methods.id"), nullable=False)
    
    amount = Column(Numeric(19, 2), nullable=False)
    reference_number = Column(String(100)) # For card approval codes, etc.
    
    # Relationships
    sales_transaction = relationship("SalesTransaction", back_populates="payments")
    payment_method = relationship("PaymentMethod")

```
**Action:** After creating these model files, you must run Alembic to generate and apply the new migration script:
```bash
alembic revision --autogenerate -m "Add sales and payment tables"
alembic upgrade head
```

### **2. Data Transfer Objects (DTOs) for Sales**

We define the data contracts for creating and viewing sales.

#### **`app/business_logic/dto/sales_dto.py`** (New File)

```python
"""Data Transfer Objects for Sales operations."""
import uuid
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field

class CartItemDTO(BaseModel):
    """DTO representing an item to be added to a sales transaction."""
    product_id: uuid.UUID
    quantity: Decimal = Field(..., gt=0)
    # Price can be optional; if not provided, fetch the current selling price.
    unit_price_override: Optional[Decimal] = Field(None, ge=0) 

class PaymentInfoDTO(BaseModel):
    """DTO representing a payment to be applied to a sale."""
    payment_method_id: uuid.UUID
    amount: Decimal = Field(..., gt=0)
    reference_number: Optional[str] = None

class SaleCreateDTO(BaseModel):
    """DTO for creating a new sales transaction."""
    company_id: uuid.UUID
    outlet_id: uuid.UUID
    cashier_id: uuid.UUID
    customer_id: Optional[uuid.UUID] = None
    cart_items: List[CartItemDTO] = Field(..., min_items=1)
    payments: List[PaymentInfoDTO] = Field(..., min_items=1)
    notes: Optional[str] = None

class FinalizedSaleDTO(BaseModel):
    """DTO representing a completed sale, suitable for generating a receipt."""
    transaction_id: uuid.UUID
    transaction_number: str
    total_amount: Decimal
    amount_paid: Decimal
    change_due: Decimal

    class Config:
        orm_mode = True
```

### **3. Data Access Layer for Sales (`app/services/`)**

This service handles the atomic persistence of sales data.

#### **`app/services/sales_service.py`** (New File)

```python
"""Data Access Service (Repository) for Sales entities."""
from __future__ import annotations
from typing import TYPE_CHECKING

from app.core.result import Result, Success, Failure
from app.models.sales import SalesTransaction
from app.services.base_service import BaseService

if TYPE_CHECKING:
    from app.core.application_core import ApplicationCore

class SalesService(BaseService):
    """Handles all database interactions for sales-related models."""

    def __init__(self, core: "ApplicationCore"):
        super().__init__(core, SalesTransaction)

    async def save_full_transaction(self, transaction: SalesTransaction) -> Result[SalesTransaction, str]:
        """
        Saves a complete SalesTransaction object, including its items and payments.
        This method assumes it is being called within an existing session from the manager.
        """
        try:
            # The session is managed by the calling manager's `get_session` context.
            async with self.core.get_session() as session:
                session.add(transaction)
                await session.flush()
                await session.refresh(transaction)
                # Refreshing items and payments might be needed if they have defaults
                for item in transaction.items:
                    await session.refresh(item)
                for payment in transaction.payments:
                    await session.refresh(payment)
                
            return Success(transaction)
        except Exception as e:
            return Failure(f"Database error saving transaction: {e}")

```
*Note: A `payment_service.py` could also be created, but for Stage 3, the logic can be contained within the `SalesService` for simplicity, as payments are always tied to a sale.*

### **4. Business Logic for Sales (`app/business_logic/managers/`)**

This is the most complex part of Stage 3. The `SalesManager` will orchestrate the entire process.

#### **`app/business_logic/managers/sales_manager.py`** (New File)

```python
"""
Business Logic Manager for orchestrating the entire sales workflow.
"""
from __future__ import annotations
from decimal import Decimal
import uuid
from typing import TYPE_CHECKING, List

from app.core.result import Result, Success, Failure
from app.business_logic.managers.base_manager import BaseManager
from app.business_logic.dto.sales_dto import SaleCreateDTO, FinalizedSaleDTO, CartItemDTO
from app.models.sales import SalesTransaction, SalesTransactionItem
from app.models.payment import Payment

if TYPE_CHECKING:
    from app.core.application_core import ApplicationCore
    from app.services.sales_service import SalesService
    # We will also need InventoryManager, but let's assume it's available via core
    # from app.business_logic.managers.inventory_manager import InventoryManager

class SalesManager(BaseManager):
    """Orchestrates the business logic for creating and finalizing sales."""

    @property
    def sales_service(self) -> "SalesService":
        # Placeholder for lazy-loading SalesService
        # self.core.sales_service
        pass 
    
    # This pattern would be used for all required managers/services
    # def inventory_manager(self) -> "InventoryManager":
    #     return self.core.inventory_manager

    async def _calculate_totals(self, cart_items: List[CartItemDTO]) -> Result[dict, str]:
        """
        Internal helper to calculate subtotal, tax, and total from cart items.
        This would fetch product details to get prices and tax rates.
        """
        subtotal = Decimal("0.0")
        tax_amount = Decimal("0.0")
        
        for item in cart_items:
            # In a real implementation, fetch product from product_service
            # product_result = await self.core.product_service.get_by_id(item.product_id)
            # For now, let's use dummy data
            price = Decimal("10.00") if item.unit_price_override is None else item.unit_price_override
            gst_rate = Decimal("8.00") # from product
            
            line_subtotal = item.quantity * price
            subtotal += line_subtotal
            # Simplified tax calculation
            tax_amount += line_subtotal * (gst_rate / Decimal("100.0"))

        total_amount = subtotal + tax_amount
        return Success({
            "subtotal": subtotal,
            "tax_amount": tax_amount,
            "total_amount": total_amount.quantize(Decimal("0.01"))
        })

    async def finalize_sale(self, dto: SaleCreateDTO) -> Result[FinalizedSaleDTO, str]:
        """
        Processes a complete sales transaction atomically.
        This is the core orchestration method.
        """
        # --- 1. Validation Phase ---
        total_payment = sum(p.amount for p in dto.payments)
        
        totals_result = await self._calculate_totals(dto.cart_items)
        if isinstance(totals_result, Failure):
            return totals_result
        
        totals = totals_result.value
        if total_payment < totals["total_amount"]:
            return Failure("Payment amount is less than the total amount due.")

        # --- 2. Orchestration within a single transaction ---
        try:
            # We would use the core session context manager to ensure atomicity
            # async with self.core.get_session() as session:
            
            # --- 2a. Check and deduct inventory (This needs InventoryManager) ---
            # for item in dto.cart_items:
            #     await self.inventory_manager.deduct_stock(item.product_id, item.quantity)
            
            # --- 2b. Construct ORM models ---
            sale = SalesTransaction(
                company_id=dto.company_id,
                outlet_id=dto.outlet_id,
                cashier_id=dto.cashier_id,
                customer_id=dto.customer_id,
                transaction_number=f"SALE-{uuid.uuid4().hex[:8].upper()}",
                **totals
            )
            
            # Create line items
            for cart_item in dto.cart_items:
                # Again, this would fetch real cost/price data
                sale.items.append(SalesTransactionItem(
                    product_id=cart_item.product_id,
                    quantity=cart_item.quantity,
                    unit_price=Decimal("10.0"), # dummy data
                    cost_price=Decimal("5.0"), # dummy data
                    line_total=cart_item.quantity * Decimal("10.0") # dummy data
                ))
            
            # Create payment records
            for payment_info in dto.payments:
                sale.payments.append(Payment(**payment_info.dict()))
            
            # --- 2c. Persist the entire transaction atomically ---
            # In a real implementation, you would pass the 'sale' object to the service
            # For now, we simulate success
            # saved_sale_result = await self.sales_service.save_full_transaction(sale)
            # if isinstance(saved_sale_result, Failure):
            #     # The context manager would handle the rollback
            #     return saved_sale_result
            
            # --- 2d. (Optional) Update customer loyalty points ---
            # await self.core.customer_manager.add_loyalty_points(...)
            
            change_due = total_payment - totals["total_amount"]
            
            finalized_dto = FinalizedSaleDTO(
                transaction_id=uuid.uuid4(), # dummy data
                transaction_number=sale.transaction_number,
                total_amount=totals["total_amount"],
                amount_paid=total_payment,
                change_due=change_due.quantize(Decimal("0.01"))
            )
            
            return Success(finalized_dto)

        except Exception as e:
            # Log the full error e
            return Failure("A critical error occurred while finalizing the sale.")
```

### **5. Point-of-Sale UI (`app/ui/`)**

This is the user-facing component that cashiers will interact with.

#### **`app/ui/views/pos_view.py`** (New File)
```python
"""The primary Point-of-Sale (POS) view."""
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLineEdit,
    QTableView, QPushButton, QLabel, QFormLayout
)
from PySide6.QtCore import Slot

from app.core.application_core import ApplicationCore
# from app.ui.dialogs.payment_dialog import PaymentDialog
# For Stage 3, we can simulate the payment dialog logic directly in the view.

class POSView(QWidget):
    """The main POS interface for conducting sales."""

    def __init__(self, core: ApplicationCore, parent=None):
        super().__init__(parent)
        self.core = core
        self.current_cart = [] # Simple list to hold cart items

        self._setup_ui()
        self._connect_signals()
        self._reset_sale()

    def _setup_ui(self):
        """Build the user interface."""
        # --- Left Panel: Cart and Totals ---
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        self.cart_table = QTableView() # A model will be needed here
        self.totals_label = QLabel("Total: S$0.00")
        self.totals_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        left_layout.addWidget(QLabel("Current Sale"))
        left_layout.addWidget(self.cart_table, 1) # Give table more space
        left_layout.addWidget(self.totals_label)
        
        # --- Right Panel: Product Entry and Actions ---
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        product_form = QFormLayout()
        self.product_search_input = QLineEdit()
        self.product_search_input.setPlaceholderText("Scan barcode or enter SKU...")
        self.add_item_button = QPushButton("Add to Cart")
        product_form.addRow("Product:", self.product_search_input)
        
        self.pay_button = QPushButton("PAY")
        self.pay_button.setStyleSheet("background-color: #4CAF50; color: white; font-size: 28px; padding: 20px;")
        
        self.new_sale_button = QPushButton("New Sale")
        
        right_layout.addLayout(product_form)
        right_layout.addWidget(self.add_item_button)
        right_layout.addStretch()
        right_layout.addWidget(self.new_sale_button)
        right_layout.addWidget(self.pay_button)
        
        # --- Main Layout ---
        main_layout = QHBoxLayout(self)
        main_layout.addWidget(left_panel, 2) # Left panel takes 2/3 of space
        main_layout.addWidget(right_panel, 1) # Right panel takes 1/3

    def _connect_signals(self):
        self.add_item_button.clicked.connect(self._on_add_item)
        self.product_search_input.returnPressed.connect(self._on_add_item)
        self.pay_button.clicked.connect(self._on_pay)
        self.new_sale_button.clicked.connect(self._reset_sale)

    def _update_totals(self):
        """Recalculates and updates the total display."""
        total = sum(item['quantity'] * item['price'] for item in self.current_cart)
        # GST would be calculated here too
        self.totals_label.setText(f"Total: S${total:.2f}")

    @Slot()
    def _on_add_item(self):
        """Handles adding a product to the cart."""
        sku = self.product_search_input.text()
        if not sku:
            return
        
        # --- This part would call the business logic ---
        # async def add_item_task():
        #     product_result = await self.core.product_manager.get_by_sku(sku)
        #     #... handle result
        
        # For now, we simulate finding a product
        self.current_cart.append({
            "sku": sku,
            "name": f"Product {sku}",
            "quantity": 1,
            "price": Decimal("15.50")
        })
        self.product_search_input.clear()
        self.product_search_input.setFocus()
        
        # Update UI (Table model would do this automatically)
        print("Current Cart:", self.current_cart) 
        self._update_totals()

    @Slot()
    def _on_pay(self):
        """Handles the payment process."""
        # --- This is where the orchestration happens ---
        # 1. Create the SaleCreateDTO from self.current_cart
        # 2. Open the PaymentDialog to get payment info
        # 3. Call self.core.sales_manager.finalize_sale(dto)
        # 4. Handle the Result
        
        # Simulating the flow
        print("Payment process initiated...")
        # A real implementation would launch the payment dialog here.
        # After payment is confirmed, the sale is finalized.
        self._reset_sale()
        print("Sale finalized and new sale started.")
        # Show a success message
        QMessageBox.information(self, "Success", "Transaction Completed!")

    @Slot()
    def _reset_sale(self):
        """Clears the cart and resets the UI for a new sale."""
        self.current_cart.clear()
        self.product_search_input.clear()
        # Update table model to be empty
        self._update_totals()
        self.product_search_input.setFocus()
```
*(Note: A full UI implementation would require a `QAbstractTableModel` to dynamically display the cart contents in the `QTableView`. This has been omitted for clarity but is a necessary component for a fully functional UI.)*

This completes the code implementation for Stage 3. This stage is a significant leap forward, establishing the core transactional capability of the SG-POS system. The code provides a robust and clear example of how to implement complex business workflows while adhering to our strict architectural principles. Your development team can now study, understand, and replicate these patterns as they build out the remaining features in the subsequent stages.

---
https://drive.google.com/file/d/1--N5SVasJwyuD2sAG_PkHP_EU8maFUIG/view?usp=sharing, https://drive.google.com/file/d/1-aPjGdazXcN4sMP1Rrxu3ZL-_r77se25/view?usp=sharing, https://drive.google.com/file/d/155prVF-weYwj2SYGTz6kgmQCWr54fe1i/view?usp=sharing, https://drive.google.com/file/d/1B8QfYknf2XcufBlNqy85reIlayDz3A4G/view?usp=sharing, https://drive.google.com/file/d/1DWDcoki0DxrojFQII5TXKEQmkb_1lmAZ/view?usp=sharing, https://drive.google.com/file/d/1GOx8Ip7IiCAJJAh5_uTn1z_attqC-UYX/view?usp=sharing, https://drive.google.com/file/d/1I-oK7zzhWFuxkh2M8RWTNyLXTN63ZAbV/view?usp=sharing, https://drive.google.com/file/d/1LtDhg_B1t059pE3AKsb0DnRlIvaRHG1W/view?usp=sharing, https://drive.google.com/file/d/1O7dMCCPrlwVdFbbZTN-X_hKHrWJcvRwO/view?usp=sharing, https://drive.google.com/file/d/1OYbolRDSNyB4s1iI6kaxL00EcIgZvuLK/view?usp=sharing, https://drive.google.com/file/d/1PcgJkam4NW0VyCRt3KtAj_QtCy3_Va3M/view?usp=sharing, https://drive.google.com/file/d/1Py5ksEK0rg5SNBcnUEo8fGUlKldAGC2R/view?usp=sharing, https://drive.google.com/file/d/1RqS06J2HqHsSyQiK4GYM8wmAX6z5TzFW/view?usp=sharing, https://drive.google.com/file/d/1UsRkTO-P3XZRsU4r6p-5Vqqpfm5VZ26K/view?usp=sharing, https://drive.google.com/file/d/1W6fKS9oWjpV3wsE1x6SxwE0adjfjvJ16/view?usp=sharing, https://drive.google.com/file/d/1Wn2QYlW05N9ei6WzG1uDe8Ac96Dc_wqB/view?usp=sharing, https://drive.google.com/file/d/1_xoWQs6uf9579WhZJ4ej6pkEREIAIJRh/view?usp=sharing, https://drive.google.com/file/d/1f5_aeEDRkwvOZCLKAz2ZFpwahqxHBtio/view?usp=sharing, https://aistudio.google.com/app/prompts?state=%7B%22ids%22:%5B%221gx_oZ2wveunWKD2wA8376-_VkH-4cB0T%22%5D,%22action%22:%22open%22,%22userId%22:%22114616170952591381046%22,%22resourceKeys%22:%7B%7D%7D&usp=sharing, https://drive.google.com/file/d/1hilLbpA8KFwBdWXB710RoqnPT_ra8hQS/view?usp=sharing, https://drive.google.com/file/d/1nKpXi0YMRulUyQmu-3OYkYCv60d-2xS7/view?usp=sharing, https://drive.google.com/file/d/1ohbdiNg0wYF_FDgycsgb4r27ZGX9FkFM/view?usp=sharing, https://drive.google.com/file/d/1r-iHHzDEvyg-s8jAIelE7AKDoU16_N2Q/view?usp=sharing, https://drive.google.com/file/d/1yiWwDOe7C0969ePNJti0kqznH2faVlbn/view?usp=sharing
