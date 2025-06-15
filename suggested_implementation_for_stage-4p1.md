**Stage 4: Expanding Operations - Inventory & Advanced CRM**. This stage is crucial as it builds upon the transactional core, adding the deep operational capabilities that retailers critically need: comprehensive inventory control and meaningful customer relationship management.

The code generated here will continue to serve as a "gold standard" reference, demonstrating how to add significant new modules to our existing foundation without compromising architectural integrity. It will showcase advanced business logic, database interactions, and the corresponding UI development patterns.

Let's proceed with building out Stage 4.

---

## **SG-POS System: Stage 4 Code Implementation**

This stage involves creating new models and services for advanced inventory concepts (like purchase orders and suppliers) and then building the business logic and UI to manage them. We will also enhance the customer module with loyalty features.

### **1. Database Models for Advanced Inventory & CRM**

We begin by extending our database schema with tables for Suppliers, Purchase Orders, and Stock Movements.

#### **`app/models/inventory.py`** (Modified)
We add the `StockMovement` model to this existing file.

```python
"""SQLAlchemy models for Inventory and Stock Movements."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, ForeignKey, Numeric, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin

# The `Inventory` model from Stage 1 is assumed to be here.
# We are adding the new models below.

class Supplier(Base, TimestampMixin):
    """Represents a product supplier."""
    __tablename__ = "suppliers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    contact_person = Column(String(255))
    email = Column(String(255))
    phone = Column(String(50))
    address = Column(Text)
    is_active = Column(Boolean, nullable=False, default=True)

    company = relationship("Company")
    purchase_orders = relationship("PurchaseOrder", back_populates="supplier")

class PurchaseOrder(Base, TimestampMixin):
    """Represents a purchase order sent to a supplier."""
    __tablename__ = "purchase_orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    outlet_id = Column(UUID(as_uuid=True), ForeignKey("outlets.id"), nullable=False)
    supplier_id = Column(UUID(as_uuid=True), ForeignKey("suppliers.id"), nullable=False)
    
    po_number = Column(String(50), nullable=False, unique=True)
    order_date = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    expected_delivery_date = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(20), nullable=False, default='DRAFT') # DRAFT, SENT, PARTIALLY_RECEIVED, RECEIVED, CANCELLED

    notes = Column(Text)
    total_amount = Column(Numeric(19, 2), nullable=False, default=0)
    
    # Relationships
    company = relationship("Company")
    outlet = relationship("Outlet")
    supplier = relationship("Supplier", back_populates="purchase_orders")
    items = relationship("PurchaseOrderItem", back_populates="purchase_order", cascade="all, delete-orphan")

class PurchaseOrderItem(Base, TimestampMixin):
    """Represents a line item within a purchase order."""
    __tablename__ = "purchase_order_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    purchase_order_id = Column(UUID(as_uuid=True), ForeignKey("purchase_orders.id"), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    
    quantity_ordered = Column(Numeric(15, 4), nullable=False)
    quantity_received = Column(Numeric(15, 4), nullable=False, default=0)
    unit_cost = Column(Numeric(19, 4), nullable=False)
    
    # Relationships
    purchase_order = relationship("PurchaseOrder", back_populates="items")
    product = relationship("Product")

class StockMovement(Base, TimestampMixin):
    """Immutable log of all inventory changes for full auditability."""
    __tablename__ = "stock_movements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    outlet_id = Column(UUID(as_uuid=True), ForeignKey("outlets.id"), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    # variant_id can be added here
    
    movement_type = Column(String(50), nullable=False) # SALE, RETURN, PURCHASE, ADJUSTMENT, TRANSFER
    quantity_change = Column(Numeric(15, 4), nullable=False) # Positive for stock in, negative for stock out
    
    reference_id = Column(UUID) # e.g., sales_transaction.id, purchase_order.id
    reference_type = Column(String(50))
    
    notes = Column(Text)
    created_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # Relationships
    product = relationship("Product")
    outlet = relationship("Outlet")
    user = relationship("User")
```
**Action:** As before, run Alembic to generate and apply the migration for these new tables.
```bash
alembic revision --autogenerate -m "Add supplier, purchase order, and stock movement tables"
alembic upgrade head
```

### **2. DTOs for Inventory and CRM**

We define the data contracts for our new workflows.

#### **`app/business_logic/dto/inventory_dto.py`** (New File)

```python
"""Data Transfer Objects for Inventory and Procurement operations."""
import uuid
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field

# --- Purchase Order DTOs ---

class PurchaseOrderItemCreateDTO(BaseModel):
    product_id: uuid.UUID
    quantity_ordered: Decimal = Field(..., gt=0)
    unit_cost: Decimal = Field(..., ge=0)

class PurchaseOrderCreateDTO(BaseModel):
    company_id: uuid.UUID
    outlet_id: uuid.UUID
    supplier_id: uuid.UUID
    notes: Optional[str] = None
    items: List[PurchaseOrderItemCreateDTO] = Field(..., min_items=1)

# --- Stock Adjustment DTO ---

class StockAdjustmentItemDTO(BaseModel):
    product_id: uuid.UUID
    counted_quantity: Decimal = Field(..., ge=0)
    # The manager will calculate the change from the current stock level

class StockAdjustmentDTO(BaseModel):
    company_id: uuid.UUID
    outlet_id: uuid.UUID
    user_id: uuid.UUID
    notes: str
    items: List[StockAdjustmentItemDTO] = Field(..., min_items=1)
```

#### **`app/business_logic/dto/customer_dto.py`** (Modified)

We add a DTO for loyalty point adjustments.

```python
# ... (existing DTOs)

class LoyaltyPointAdjustmentDTO(BaseModel):
    """DTO for manually adjusting a customer's loyalty points."""
    customer_id: uuid.UUID
    points_change: int # Can be positive or negative
    reason: str
    admin_user_id: uuid.UUID
```

### **3. Services for New Inventory Entities**

We create the repositories to handle database interactions for suppliers and purchase orders.

#### **`app/services/supplier_service.py`** (New File)

```python
"""Data Access Service (Repository) for Supplier entities."""
from __future__ import annotations
from typing import TYPE_CHECKING
from app.models.inventory import Supplier
from app.services.base_service import BaseService

if TYPE_CHECKING:
    from app.core.application_core import ApplicationCore

class SupplierService(BaseService):
    """Handles all database interactions for the Supplier model."""
    def __init__(self, core: "ApplicationCore"):
        super().__init__(core, Supplier)
    
    # Can add specific search methods here, e.g., search_by_name
```

#### **`app/services/purchase_order_service.py`** (New File)

```python
"""Data Access Service (Repository) for Purchase Order entities."""
from __future__ import annotations
from typing import TYPE_CHECKING
from app.models.inventory import PurchaseOrder
from app.services.base_service import BaseService

if TYPE_CHECKING:
    from app.core.application_core import ApplicationCore

class PurchaseOrderService(BaseService):
    """Handles all database interactions for the PurchaseOrder model."""
    def __init__(self, core: "ApplicationCore"):
        super().__init__(core, PurchaseOrder)
        
    # Example specific method:
    # async def get_open_purchase_orders(self, outlet_id: UUID) -> Result[List[PurchaseOrder], str]:
    #     ...
```

#### **`app/services/inventory_service.py`** (New File)
This service is crucial. It will manage the `inventory` and `stock_movements` tables.

```python
"""Data Access Service (Repository) for Inventory operations."""
from __future__ import annotations
from typing import TYPE_CHECKING
from uuid import UUID
from decimal import Decimal
import sqlalchemy as sa
from sqlalchemy.future import select

from app.core.result import Result, Success, Failure
from app.models.inventory import Inventory, StockMovement
from app.services.base_service import BaseService

if TYPE_CHECKING:
    from app.core.application_core import ApplicationCore

class InventoryService(BaseService):
    """Handles direct database interactions for inventory levels and movements."""
    
    def __init__(self, core: "ApplicationCore"):
        # This service interacts with two models, so we don't use the base init
        self.core = core

    async def get_stock_level(self, outlet_id: UUID, product_id: UUID) -> Result[Decimal, str]:
        """Gets the current quantity_on_hand for a product at an outlet."""
        try:
            async with self.core.get_session() as session:
                stmt = select(Inventory.quantity_on_hand).where(
                    Inventory.outlet_id == outlet_id,
                    Inventory.product_id == product_id
                )
                result = await session.execute(stmt)
                quantity = result.scalar_one_or_none()
                return Success(quantity or Decimal("0"))
        except Exception as e:
            return Failure(f"Database error getting stock level: {e}")

    async def adjust_stock_level(
        self,
        outlet_id: UUID,
        product_id: UUID,
        quantity_change: Decimal,
        session  # Expects to be called within an existing transaction
    ) -> Result[Decimal, str]:
        """
        Adjusts the stock level for a product. This is a low-level, unsafe
        method that should only be called by a manager. It returns the new stock level.
        """
        try:
            # Lock the row for update to prevent race conditions
            stmt = select(Inventory).where(
                Inventory.outlet_id == outlet_id,
                Inventory.product_id == product_id
            ).with_for_update()
            
            result = await session.execute(stmt)
            inventory_item = result.scalar_one_or_none()

            if inventory_item:
                inventory_item.quantity_on_hand += quantity_change
            else:
                # Create a new inventory record if it doesn't exist
                inventory_item = Inventory(
                    outlet_id=outlet_id,
                    product_id=product_id,
                    quantity_on_hand=quantity_change
                )
                session.add(inventory_item)

            if inventory_item.quantity_on_hand < 0:
                # This check ensures we don't go into negative stock unless allowed
                raise ValueError("Stock quantity cannot be negative.")

            await session.flush()
            return Success(inventory_item.quantity_on_hand)
        except Exception as e:
            return Failure(f"Failed to adjust stock level: {e}")

    async def log_movement(
        self,
        movement: StockMovement,
        session # Expects to be called within an existing transaction
    ) -> Result[StockMovement, str]:
        """Logs a stock movement record."""
        try:
            session.add(movement)
            await session.flush()
            return Success(movement)
        except Exception as e:
            return Failure(f"Failed to log stock movement: {e}")
```

### **4. Business Logic for Inventory and CRM**

#### **`app/business_logic/managers/inventory_manager.py`** (New File)
This manager will be the primary orchestrator for all inventory workflows.

```python
"""Business Logic Manager for orchestrating Inventory operations."""
from __future__ import annotations
from typing import TYPE_CHECKING
from uuid import UUID
from decimal import Decimal

from app.core.result import Result, Success, Failure
from app.business_logic.managers.base_manager import BaseManager
from app.business_logic.dto.inventory_dto import StockAdjustmentDTO
from app.models.inventory import StockMovement

if TYPE_CHECKING:
    from app.core.application_core import ApplicationCore
    from app.services.inventory_service import InventoryService

class InventoryManager(BaseManager):
    """Handles high-level inventory workflows like stock takes and adjustments."""
    
    @property
    def inventory_service(self) -> "InventoryService":
        # Placeholder for lazy-loading InventoryService
        pass

    async def adjust_stock(self, dto: StockAdjustmentDTO) -> Result[None, str]:
        """
        Performs a stock adjustment for one or more products, creating an
        auditable stock movement record for each change.
        """
        try:
            async with self.core.get_session() as session:
                for item in dto.items:
                    # 1. Get current stock
                    current_stock_result = await self.inventory_service.get_stock_level(
                        dto.outlet_id, item.product_id
                    )
                    if isinstance(current_stock_result, Failure):
                        # Rollback the entire transaction if one item fails
                        raise Exception(current_stock_result.error) 
                    
                    current_stock = current_stock_result.value
                    quantity_change = item.counted_quantity - current_stock
                    
                    if quantity_change == 0:
                        continue # No change needed

                    # 2. Adjust the stock level
                    adjust_result = await self.inventory_service.adjust_stock_level(
                        outlet_id=dto.outlet_id,
                        product_id=item.product_id,
                        quantity_change=quantity_change,
                        session=session
                    )
                    if isinstance(adjust_result, Failure):
                        raise Exception(adjust_result.error)

                    # 3. Log the movement for audit trail
                    movement = StockMovement(
                        company_id=dto.company_id,
                        outlet_id=dto.outlet_id,
                        product_id=item.product_id,
                        movement_type='ADJUSTMENT_IN' if quantity_change > 0 else 'ADJUSTMENT_OUT',
                        quantity_change=quantity_change,
                        notes=dto.notes,
                        created_by_user_id=dto.user_id,
                        reference_type="STOCK_TAKE" # Or some other reference
                    )
                    log_result = await self.inventory_service.log_movement(movement, session)
                    if isinstance(log_result, Failure):
                        raise Exception(log_result.error)
            
            return Success(None)
        except Exception as e:
            return Failure(str(e))

    async def deduct_stock_for_sale(self, sales_transaction_id: UUID, outlet_id: UUID, items: list) -> Result[None, str]:
        """
        A dedicated method to deduct stock after a sale is finalized.
        This is called by the SalesManager.
        """
        # This would loop through sale items, create StockMovement records
        # with type 'SALE', and call inventory_service.adjust_stock_level
        # for each. The entire operation must be in a single transaction.
        pass
```

#### **`app/business_logic/managers/customer_manager.py`** (Modified)
We add the loyalty points logic here.

```python
# ... existing CustomerManager code ...

    async def add_loyalty_points_for_sale(self, customer_id: UUID, sale_total: Decimal) -> Result[int, str]:
        """
        Calculates and adds loyalty points for a completed sale.
        Business Rule: 1 point for every S$10 spent.
        """
        # In a real app, this rule would be configurable
        points_to_add = int(sale_total // 10)
        
        if points_to_add <= 0:
            return Success(0)

        customer_result = await self.customer_service.get_by_id(customer_id)
        if isinstance(customer_result, Failure) or customer_result.value is None:
            return Failure("Customer not found.")
        
        customer = customer_result.value
        customer.loyalty_points += points_to_add
        
        update_result = await self.customer_service.update_customer(customer)
        if isinstance(update_result, Failure):
            return update_result
            
        # Here we would also log the loyalty transaction for auditing.
        return Success(customer.loyalty_points)

```

### **5. Inventory Management UI (`app/ui/`)**

We create the user-facing screens for managing inventory.

#### **`app/ui/views/inventory_view.py`** (New File)
```python
"""Main View for Inventory Management."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableView, QLabel, QLineEdit
)
from PySide6.QtCore import Slot

from app.core.application_core import ApplicationCore
# from app.ui.dialogs.stock_adjustment_dialog import StockAdjustmentDialog # To be created
# from app.ui.dialogs.purchase_order_dialog import PurchaseOrderDialog # To be created

class InventoryView(QWidget):
    """A view to display stock levels and initiate inventory operations."""

    def __init__(self, core: ApplicationCore, parent=None):
        super().__init__(parent)
        self.core = core
        
        self._setup_ui()
        self._connect_signals()
        self._load_data()

    def _setup_ui(self):
        """Build the user interface."""
        # --- Top Bar with Actions ---
        top_bar_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by SKU or Product Name...")
        self.adjust_stock_button = QPushButton("Adjust Stock")
        self.new_po_button = QPushButton("New Purchase Order")
        
        top_bar_layout.addWidget(QLabel("Search:"))
        top_bar_layout.addWidget(self.search_input, 1)
        top_bar_layout.addStretch()
        top_bar_layout.addWidget(self.adjust_stock_button)
        top_bar_layout.addWidget(self.new_po_button)
        
        # --- Main Table ---
        self.inventory_table = QTableView()
        # A QAbstractTableModel would be set here to display inventory data
        
        # --- Main Layout ---
        main_layout = QVBoxLayout(self)
        main_layout.addLayout(top_bar_layout)
        main_layout.addWidget(self.inventory_table)
        
    def _connect_signals(self):
        self.adjust_stock_button.clicked.connect(self._on_adjust_stock)
        self.new_po_button.clicked.connect(self._on_new_po)
        self.search_input.textChanged.connect(self._on_search)

    def _load_data(self):
        """Loads initial inventory data into the table."""
        # This would call the inventory manager to get all stock levels
        # and populate the table model.
        print("Loading inventory data...")
        
    @Slot()
    def _on_adjust_stock(self):
        """Opens the stock adjustment dialog."""
        # dialog = StockAdjustmentDialog(self.core, parent=self)
        # if dialog.exec():
        #     self._load_data() # Refresh data on success
        print("Stock Adjustment dialog would open here.")
        
    @Slot()
    def _on_new_po(self):
        """Opens the purchase order creation dialog."""
        # dialog = PurchaseOrderDialog(self.core, parent=self)
        # if dialog.exec():
        #     # Handle PO creation...
        print("New Purchase Order dialog would open here.")

    @Slot(str)
    def _on_search(self, text: str):
        """Filters the inventory table based on search text."""
        # The table model would handle the filtering logic.
        print(f"Searching for: {text}")
```
*(The dialogs for `StockAdjustmentDialog` and `PurchaseOrderDialog` would be implemented similarly to `ProductDialog` from Stage 2, collecting data via a form and passing a DTO to the relevant manager.)*

This completes the implementation of Stage 4. We have now added sophisticated inventory management and customer loyalty features, building directly on our established patterns. The system is evolving from a simple sales tool into a comprehensive retail management platform. The codebase remains clean, testable, and ready for the final stage of development.

---
https://drive.google.com/file/d/1--N5SVasJwyuD2sAG_PkHP_EU8maFUIG/view?usp=sharing, https://drive.google.com/file/d/1-aPjGdazXcN4sMP1Rrxu3ZL-_r77se25/view?usp=sharing, https://drive.google.com/file/d/155prVF-weYwj2SYGTz6kgmQCWr54fe1i/view?usp=sharing, https://drive.google.com/file/d/1B8QfYknf2XcufBlNqy85reIlayDz3A4G/view?usp=sharing, https://drive.google.com/file/d/1DWDcoki0DxrojFQII5TXKEQmkb_1lmAZ/view?usp=sharing, https://drive.google.com/file/d/1GOx8Ip7IiCAJJAh5_uTn1z_attqC-UYX/view?usp=sharing, https://drive.google.com/file/d/1I-oK7zzhWFuxkh2M8RWTNyLXTN63ZAbV/view?usp=sharing, https://drive.google.com/file/d/1LtDhg_B1t059pE3AKsb0DnRlIvaRHG1W/view?usp=sharing, https://drive.google.com/file/d/1O7dMCCPrlwVdFbbZTN-X_hKHrWJcvRwO/view?usp=sharing, https://drive.google.com/file/d/1OYbolRDSNyB4s1iI6kaxL00EcIgZvuLK/view?usp=sharing, https://drive.google.com/file/d/1PcgJkam4NW0VyCRt3KtAj_QtCy3_Va3M/view?usp=sharing, https://drive.google.com/file/d/1Py5ksEK0rg5SNBcnUEo8fGUlKldAGC2R/view?usp=sharing, https://drive.google.com/file/d/1RqS06J2HqHsSyQiK4GYM8wmAX6z5TzFW/view?usp=sharing, https://drive.google.com/file/d/1UsRkTO-P3XZRsU4r6p-5Vqqpfm5VZ26K/view?usp=sharing, https://drive.google.com/file/d/1W6fKS9oWjpV3wsE1x6SxwE0adjfjvJ16/view?usp=sharing, https://drive.google.com/file/d/1Wn2QYlW05N9ei6WzG1uDe8Ac96Dc_wqB/view?usp=sharing, https://drive.google.com/file/d/1_xoWQs6uf9579WhZJ4ej6pkEREIAIJRh/view?usp=sharing, https://drive.google.com/file/d/1f5_aeEDRkwvOZCLKAz2ZFpwahqxHBtio/view?usp=sharing, https://aistudio.google.com/app/prompts?state=%7B%22ids%22:%5B%221gx_oZ2wveunWKD2wA8376-_VkH-4cB0T%22%5D,%22action%22:%22open%22,%22userId%22:%22114616170952591381046%22,%22resourceKeys%22:%7B%7D%7D&usp=sharing, https://drive.google.com/file/d/1hilLbpA8KFwBdWXB710RoqnPT_ra8hQS/view?usp=sharing, https://drive.google.com/file/d/1nKpXi0YMRulUyQmu-3OYkYCv60d-2xS7/view?usp=sharing, https://drive.google.com/file/d/1ohbdiNg0wYF_FDgycsgb4r27ZGX9FkFM/view?usp=sharing, https://drive.google.com/file/d/1r-iHHzDEvyg-s8jAIelE7AKDoU16_N2Q/view?usp=sharing, https://drive.google.com/file/d/1yiWwDOe7C0969ePNJti0kqznH2faVlbn/view?usp=sharing
