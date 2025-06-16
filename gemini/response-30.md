Of course. Building on the successful completion of the transactional core, we will now meticulously implement **Stage 4: Expanding Operations - Inventory & Advanced CRM**. This stage is crucial for transforming the application from a simple sales tool into a comprehensive retail management platform. My approach will remain rigorous, ensuring each file is production-worthy, architecturally sound, and directly follows our established execution plan.

---

### **Detailed Execution Plan: Stage 4 - Expanding Operations (Inventory & Advanced CRM)**

**Objective:** To build out the full inventory management and advanced customer relationship management modules. This includes purchase orders, stock adjustments, stock history, and customer loyalty functionality.

---

### **Phase 4.1: Data Transfer Objects (DTOs)**

This phase defines the data contracts for our new inventory and CRM workflows.

#### **1. `app/business_logic/dto/inventory_dto.py`**

*   **File Path:** `app/business_logic/dto/inventory_dto.py`
*   **Purpose & Goals:** Defines Pydantic models for all inventory-related operations, including suppliers, purchase orders, stock adjustments, stock movements, and inventory summaries.
*   **Interfaces:** `SupplierDTO`, `PurchaseOrderDTO`, `StockAdjustmentDTO`, `StockMovementDTO`, `InventorySummaryDTO`, and their related create/update/item DTOs.
*   **Interactions:** Used by `InventoryManager` and various UI components (`InventoryView`, `PurchaseOrderDialog`, `StockAdjustmentDialog`).
*   **Code Skeleton:**

```python
# File: app/business_logic/dto/inventory_dto.py
"""Data Transfer Objects for Inventory and Procurement operations."""
import uuid
from decimal import Decimal
from datetime import datetime
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
    variant_id: Optional[uuid.UUID] = None
    quantity_ordered: Decimal = Field(..., gt=Decimal("0.00"), decimal_places=4)
    unit_cost: Decimal = Field(..., ge=Decimal("0.00"), decimal_places=4)

class PurchaseOrderCreateDTO(BaseModel):
    company_id: uuid.UUID
    outlet_id: uuid.UUID
    supplier_id: uuid.UUID
    po_number: Optional[str] = None
    order_date: datetime = Field(default_factory=datetime.utcnow)
    expected_delivery_date: Optional[datetime] = None
    notes: Optional[str] = None
    items: List[PurchaseOrderItemCreateDTO] = Field(..., min_items=1)

class PurchaseOrderItemDTO(BaseModel):
    id: uuid.UUID
    product_id: uuid.UUID
    variant_id: Optional[uuid.UUID] = None
    product_name: str
    sku: str
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
    supplier_name: str
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
    variant_id: Optional[uuid.UUID] = None
    counted_quantity: Decimal = Field(..., ge=Decimal("0.00"), decimal_places=4)

class StockAdjustmentDTO(BaseModel):
    company_id: uuid.UUID
    outlet_id: uuid.UUID
    user_id: uuid.UUID
    notes: str = Field(..., min_length=1, description="Reason or notes for the adjustment")
    items: List[StockAdjustmentItemDTO] = Field(..., min_items=1)

# --- Stock Movement DTO (for display/reporting) ---
class StockMovementDTO(BaseModel):
    id: uuid.UUID
    product_id: uuid.UUID
    variant_id: Optional[uuid.UUID] = None
    product_name: str
    sku: str
    outlet_name: str
    movement_type: str
    quantity_change: Decimal = Field(..., decimal_places=4)
    reference_id: Optional[uuid.UUID]
    notes: Optional[str]
    created_by_user_name: Optional[str]
    created_at: datetime
    class Config:
        orm_mode = True

# --- Inventory Summary DTO (for InventoryView display) ---
class InventorySummaryDTO(BaseModel):
    product_id: uuid.UUID
    variant_id: Optional[uuid.UUID] = None
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

**Double-check and Validate `app/business_logic/dto/inventory_dto.py`:**
*   This is a new file. Its content is self-contained and accurate according to the plan.
*   **Key Consideration:** `variant_id` has been added to all relevant DTOs (`PurchaseOrderItemCreateDTO`, `PurchaseOrderItemDTO`, `StockAdjustmentItemDTO`, `StockMovementDTO`, `InventorySummaryDTO`) to fully support the database schema.
*   The DTOs are comprehensive and cover all necessary data contracts for Stage 4.

---

#### **2. `app/business_logic/dto/customer_dto.py` (Modified)**

*   **File Path:** `app/business_logic/dto/customer_dto.py`
*   **Purpose & Goals:** To add a DTO for loyalty point adjustments, enabling administrators to manually add or remove points.
*   **Interfaces:** Adds `LoyaltyPointAdjustmentDTO`.
*   **Interactions:** Will be used by the UI (in the customer management view, likely a dialog) and consumed by `CustomerManager`.
*   **Code Skeleton:**

```python
# File: app/business_logic/dto/customer_dto.py
"""Data Transfer Objects (DTOs) for the Customer entity."""
import uuid
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, EmailStr

class CustomerBaseDTO(BaseModel):
    """Base DTO with common customer fields."""
    customer_code: str = Field(..., min_length=1, max_length=50, description="Unique code for the customer")
    name: str = Field(..., min_length=1, max_length=255, description="Customer's full name")
    email: Optional[EmailStr] = Field(None, description="Customer's email address")
    phone: Optional[str] = Field(None, description="Customer's phone number")
    address: Optional[str] = Field(None, description="Customer's address")

class CustomerCreateDTO(CustomerBaseDTO):
    """DTO for creating a new customer."""
    credit_limit: Decimal = Field(Decimal("0.00"), ge=0, decimal_places=2, description="Credit limit extended to the customer")

class CustomerUpdateDTO(CustomerBaseDTO):
    """DTO for updating an existing customer."""
    credit_limit: Decimal = Field(Decimal("0.00"), ge=0, decimal_places=2, description="Credit limit extended to the customer")
    is_active: bool = True

class CustomerDTO(CustomerBaseDTO):
    """DTO representing a full customer record."""
    id: uuid.UUID = Field(..., description="Unique identifier for the customer")
    loyalty_points: int = Field(..., ge=0, description="Current loyalty points balance")
    credit_limit: Decimal = Field(..., ge=0, decimal_places=2, description="Credit limit extended to the customer")
    is_active: bool = True

    class Config:
        orm_mode = True

class LoyaltyPointAdjustmentDTO(BaseModel):
    """DTO for manually adjusting a customer's loyalty points."""
    customer_id: uuid.UUID
    points_change: int # Can be positive (add) or negative (deduct)
    reason: str = Field(..., min_length=1, description="Reason for the manual adjustment (e.g., 'Goodwill gesture', 'Point correction')")
    admin_user_id: uuid.UUID # User performing the adjustment
```

**Double-check and Validate `app/business_logic/dto/customer_dto.py`:**

```diff
--- a/app/business_logic/dto/customer_dto.py
+++ b/app/business_logic/dto/customer_dto.py
@@ -29,3 +29,8 @@
 
     class Config:
         orm_mode = True
+
+class LoyaltyPointAdjustmentDTO(BaseModel):
+    """DTO for manually adjusting a customer's loyalty points."""
+    customer_id: uuid.UUID
+    points_change: int # Can be positive (add) or negative (deduct)
+    reason: str = Field(..., min_length=1, description="Reason for the manual adjustment (e.g., 'Goodwill gesture', 'Point correction')")
+    admin_user_id: uuid.UUID # User performing the adjustment

```

**Review and Validation Summary:**
The `app/business_logic/dto/customer_dto.py` file is correctly updated with the new `LoyaltyPointAdjustmentDTO`, providing a clear data contract for this administrative function.

---

### **Phase 4.2: Data Access Layer (Services)**

This phase creates the services for suppliers and purchase orders.

#### **1. `app/services/supplier_service.py`**

*   **File Path:** `app/services/supplier_service.py`
*   **Purpose & Goals:** Handles persistence operations for `Supplier` entities.
*   **Interfaces:** `SupplierService(core: ApplicationCore)`. Inherits CRUD from `BaseService` and adds specific search methods.
*   **Interactions:** Used by `InventoryManager` and UI components.
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
from app.models.product import Supplier
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
    
    async def get_all_active_suppliers(self, company_id: UUID) -> Result[List[Supplier], str]:
        """Fetches all active suppliers for a given company."""
        try:
            async with self.core.get_session() as session:
                stmt = select(Supplier).where(
                    Supplier.company_id == company_id,
                    Supplier.is_active == True
                ).order_by(Supplier.name)
                result = await session.execute(stmt)
                suppliers = result.scalars().all()
                return Success(suppliers)
        except Exception as e:
            return Failure(f"Database error fetching active suppliers: {e}")

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

**Double-check and Validate `app/services/supplier_service.py`:**
*   This is a new file. Its content is self-contained and accurate.
*   It correctly inherits from `BaseService` and provides specific methods like `get_by_name`, `get_all_active_suppliers`, and `search`.

---

#### **2. `app/services/purchase_order_service.py`**

*   **File Path:** `app/services/purchase_order_service.py`
*   **Purpose & Goals:** Handles persistence operations for `PurchaseOrder` aggregates.
*   **Interfaces:** `PurchaseOrderService(core: ApplicationCore)`.
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
from sqlalchemy.orm import selectinload

from app.core.result import Result, Success, Failure
from app.models.inventory import PurchaseOrder
from app.services.base_service import BaseService

if TYPE_CHECKING:
    from app.core.application_core import ApplicationCore
    from sqlalchemy.ext.asyncio import AsyncSession

class PurchaseOrderService(BaseService):
    """
    Handles all database interactions for the PurchaseOrder model.
    Inherits generic CRUD from BaseService.
    """
    def __init__(self, core: "ApplicationCore"):
        super().__init__(core, PurchaseOrder)
        
    async def create_full_purchase_order(self, po: PurchaseOrder, session: AsyncSession) -> Result[PurchaseOrder, str]:
        """
        Saves a complete PurchaseOrder object, including its items, within a provided session.
        Args:
            po: The complete PurchaseOrder ORM instance to save.
            session: The active SQLAlchemy AsyncSession from the calling manager.
        Returns:
            A Success containing the saved PurchaseOrder, or a Failure with an error.
        """
        try:
            session.add(po)
            await session.flush()
            await session.refresh(po, attribute_names=['items']) # Refresh to load items
            return Success(po)
        except sa.exc.IntegrityError as e:
            return Failure(f"Data integrity error creating purchase order: {e.orig}")
        except Exception as e:
            return Failure(f"Database error saving full purchase order: {e}")

    async def get_open_purchase_orders(self, company_id: UUID, outlet_id: Optional[UUID] = None) -> Result[List[PurchaseOrder], str]:
        """
        Fetches open/pending purchase orders for a company, optionally filtered by outlet.
        """
        try:
            async with self.core.get_session() as session:
                stmt = select(PurchaseOrder).where(
                    PurchaseOrder.company_id == company_id,
                    PurchaseOrder.status.in_(['DRAFT', 'SENT', 'PARTIALLY_RECEIVED'])
                ).options(selectinload(PurchaseOrder.items))
                
                if outlet_id:
                    stmt = stmt.where(PurchaseOrder.outlet_id == outlet_id)
                
                result = await session.execute(stmt)
                pos = result.scalars().unique().all()
                return Success(pos)
        except Exception as e:
            return Failure(f"Database error fetching open purchase orders: {e}")
```

**Double-check and Validate `app/services/purchase_order_service.py`:**
*   This is a new file. Its content is self-contained and accurate.
*   The `create_full_purchase_order` correctly accepts a `session` argument for atomic transactions.
*   `get_open_purchase_orders` uses `selectinload` to efficiently pre-load related items, which is an important performance optimization.

---

This completes the first part of Stage 4. The DTOs and Services are now in place. The next response will provide the `InventoryManager`, `CustomerManager`, and the UI components for this stage.

---
https://drive.google.com/file/d/108RlhMVaufy_hYAq9aWl4fJT0Nc_LB2k/view?usp=sharing, https://drive.google.com/file/d/1DVVDdJPIYRsNjaL1TBK0pyivBT9T3KcR/view?usp=sharing, https://drive.google.com/file/d/1Dv92K22sZCR81fKux1KGaRKSj8Jv-Uyc/view?usp=sharing, https://aistudio.google.com/app/prompts?state=%7B%22ids%22:%5B%221HJO6Ey-cx-eWjXUJuYEitWEe9fWU1I7v%22%5D,%22action%22:%22open%22,%22userId%22:%22103961307342447084491%22,%22resourceKeys%22:%7B%7D%7D&usp=sharing, https://drive.google.com/file/d/1O8RKDf9T_KQwxh_rkPefDZVRvLlJpeOW/view?usp=sharing, https://drive.google.com/file/d/1SzHas3aRVlLw8XZ5_aNYK9dhML_2ea-b/view?usp=sharing, https://drive.google.com/file/d/1cshXJfKI6TJeVUZKw_xMxdF0Ly-V9Anu/view?usp=sharing, https://drive.google.com/file/d/1gTl2UasRWjqn51dY_Ouh_io0JM4zvxOj/view?usp=sharing, https://drive.google.com/file/d/1l2E0gN419jGB6-aopwZySbqPiKbZLfCf/view?usp=sharing, https://drive.google.com/file/d/1nrRKmVq24tyRexjTP6PcrDYAYdreLm4u/view?usp=sharing, https://drive.google.com/file/d/1qSk87Kr_yuVsvxJM8CMpbr8sfCVBtsP8/view?usp=sharing, https://drive.google.com/file/d/1wjCj8KX8Cs8MeVz0a4FWLB7hoeUhSJJe/view?usp=sharing, https://drive.google.com/file/d/1yf-0upWQE6xmB3LxWX6yCtOzUIRt-sDo/view?usp=sharing

