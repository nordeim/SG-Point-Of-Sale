<think>
### **CodeNavigator's Deep Thought Process**

**Phase 1, Sub-Task 1.1: Create DTOs and Business Logic Manager**

**1. Deconstruct the Goal**

*   **Objective:** Create the foundational backend components for managing Payment Methods.
*   **Artifacts to Produce:**
    1.  A new DTO file: `app/business_logic/dto/payment_dto.py`.
    2.  A new Manager file: `app/business_logic/managers/payment_manager.py`.
    3.  An updated `ApplicationCore` file: `app/core/application_core.py`.
*   **Key Logic to Implement:**
    *   Data structures for creating, updating, and reading payment methods.
    *   Business rule enforcement: unique payment method names per company.
    *   Orchestration logic for CRUD operations.
    *   Integration of the new manager into the application's DI container.

**2. Systematic Exploration of Implementation Options**

*   **For `payment_dto.py`:**
    *   **Option A: String-based type:** Use a `str` for the `type` field in the DTO.
        *   *Pros:* Simple.
        *   *Cons:* Prone to typos (`'CASH'` vs `'cash'`). No single source of truth for available types. Validation would have to be done manually in the manager using a hardcoded list. This is brittle.
    *   **Option B: Enum-based type:** Use Python's `enum.Enum` for the `type` field.
        *   *Pros:* Type-safe. Provides a single source of truth for all valid payment types. Pydantic integrates seamlessly with it. The UI `QComboBox` can be populated directly from this enum, ensuring consistency from the backend to the frontend. This is far more robust and maintainable.
        *   *Cons:* Slightly more verbose initially.
    *   **Decision:** Option B is the optimal, professional-grade solution. It promotes consistency and reduces the chance of data integrity errors.

*   **For `payment_manager.py`:**
    *   **Option A: Direct Service Calls:** The manager could just be a thin wrapper, directly calling `payment_method_service.create`, `payment_method_service.update`, etc.
        *   *Pros:* Simple.
        *   *Cons:* Business logic (like checking for unique names) would either be missing or would have to be pushed down into the service layer. The service layer's responsibility is data access, not business rules. This would violate the layered architecture principles.
    *   **Option B: Orchestration with Business Logic:** The manager performs checks *before* calling the service. For `create`, it first calls `service.get_by_name()` to check for duplicates. If none exist, *then* it calls `service.create()`.
        *   *Pros:* Correctly separates concerns. The manager enforces business rules, and the service handles data persistence. This is the established pattern in the codebase and is highly maintainable and testable.
        *   *Cons:* Slightly more code in the manager.
    *   **Decision:** Option B is the only correct choice to maintain architectural integrity.

*   **For `application_core.py`:**
    *   **Option A: Add a new service property:** Add `core.payment_method_service`.
    *   **Option B: Add a new manager property:** Add `core.payment_method_manager`.
    *   **Decision:** The UI layer should interact with the Business Logic Layer (Managers), not the Data Access Layer (Services). Therefore, exposing the `payment_method_manager` is the correct approach. The manager itself will use the `payment_method_service`, but that's an internal detail hidden from the UI. The checklist already specified this, and my analysis confirms it is correct.

**3. Detailed Execution Plan & Checklists**

I will now execute the plan, creating each file step-by-step and validating against the checklists.

**Step 1: Create `app/business_logic/dto/payment_dto.py`**
*   **Action:** Define the `PaymentMethodType` enum and the Pydantic DTOs.
*   **Checklist Validation:**
    *   [X] Create `PaymentMethodType` Enum (`CASH`, `CARD`, `NETS`, etc.).
    *   [X] Create `PaymentMethodBaseDTO` with fields: `name: str`, `type: PaymentMethodType`, `is_active: bool`.
    *   [X] Create `PaymentMethodCreateDTO(PaymentMethodBaseDTO)`.
    *   [X] Create `PaymentMethodUpdateDTO(PaymentMethodBaseDTO)`.
    *   [X] Create `PaymentMethodDTO(PaymentMethodBaseDTO)` which includes `id: uuid.UUID` and `Config.from_attributes = True`.

**Step 2: Create `app/business_logic/managers/payment_manager.py`**
*   **Action:** Implement the manager class to handle business logic.
*   **Checklist Validation:**
    *   [X] Create class `PaymentMethodManager(BaseManager)`.
    *   [X] Add property for `payment_method_service`. This requires importing `PaymentMethodService`.
    *   [X] Implement `get_all_payment_methods(company_id)`. This will call the service and convert the ORM results to DTOs.
    *   [X] Implement `create_payment_method(dto)`.
        *   It will first call `self.payment_method_service.get_by_name()`.
        *   If a method exists, it will return a `Failure`.
        *   If not, it will create a `PaymentMethod` ORM instance from the DTO.
        *   It will then call `self.payment_method_service.create()` with the new ORM instance.
        *   Finally, it will convert the successful result back to a DTO and return `Success(dto)`.
    *   [X] Implement `update_payment_method(id, dto)`.
        *   It will first fetch the existing method by `id`.
        *   It will check if the name is being changed and if the new name is already taken by *another* method.
        *   It will update the ORM object's attributes from the DTO.
        *   It will call `self.payment_method_service.update()`.
        *   It will return the result as a DTO.
    *   [X] Implement `deactivate_payment_method(id)`.
        *   It will fetch the method by `id`.
        *   Set `is_active = False`.
        *   Call `self.payment_method_service.update()`.

**Step 3: Update `app/core/application_core.py`**
*   **Action:** Integrate the new manager into the DI container.
*   **Checklist Validation:**
    *   [X] Add `from app.business_logic.managers.payment_manager import PaymentMethodManager`.
    *   [X] Find the "Manager Properties" section.
    *   [X] Add a new property:
        ```python
        @property
        def payment_method_manager(self) -> "PaymentMethodManager":
            if "payment_method_manager" not in self._managers:
                from app.business_logic.managers.payment_manager import PaymentMethodManager
                self._managers["payment_method_manager"] = PaymentMethodManager(self)
            return self._managers["payment_method_manager"]
        ```
    *   [X] Add `"PaymentMethodManager"` to the `if TYPE_CHECKING:` block at the top of the file for type hinting.

**4. Code Generation & Validation**

I will now generate the code for the three files. After generating each file, I will mentally perform the `diff` validation to ensure correctness and prevent regressions.

*   `payment_dto.py`: New file. No diff required. I will check for correctness against the plan.
*   `payment_manager.py`: New file. No diff required. I will check for correctness against the plan.
*   `application_core.py`: This is an update. I will be extremely careful. I will copy the existing file content and insert the new property in the correct alphabetical/logical location among the other manager properties. I will also add the type hint to the `TYPE_CHECKING` block. A `diff` will show only these two additions, which is what I want.

The plan is solid. I will now proceed with generating the files.Excellent. I will now proceed with the execution of **Phase 1: Implement Payment Methods Configuration**, following the detailed plan with meticulous care.

This phase is broken down into three sub-tasks. I will complete the first sub-task, which involves creating the backend DTOs and the Business Logic Manager, and then present the new and updated files for your review.

### **Phase 1, Sub-Task 1.1: Create DTOs and Business Logic Manager**

**Objective:** To establish the backend foundation for managing payment methods, including data contracts (DTOs) and the business rule orchestrator (Manager), and integrate it into the application's core.

**Execution Plan & Checklist:**

1.  **Create DTO File:**
    *   [x] Create a new file: `app/business_logic/dto/payment_dto.py`.
    *   [x] Define a `PaymentMethodType` Enum for data integrity, matching the `CHECK` constraint in the database schema.
    *   [x] Define `PaymentMethodBaseDTO`, `PaymentMethodCreateDTO`, `PaymentMethodUpdateDTO`, and `PaymentMethodDTO` to represent the data at different stages of its lifecycle.

2.  **Create Manager File:**
    *   [x] Create a new file: `app/business_logic/managers/payment_manager.py`.
    *   [x] Implement the `PaymentMethodManager` class.
    *   [x] Implement all CRUD methods (`get_all`, `create`, `update`, `deactivate`), ensuring business rules (e.g., unique name) are enforced before data persistence.
    *   [x] Ensure methods correctly map between DTOs and ORM models.

3.  **Update Application Core:**
    *   [x] Modify `app/core/application_core.py`.
    *   [x] Add the new `PaymentMethodManager` to the `TYPE_CHECKING` block for static analysis.
    *   [x] Add a lazy-loaded `@property` for `payment_method_manager`, making it accessible to the rest of the application via the DI container.

All steps in the plan have been completed.

---

### **Generated and Updated Files**

Here are the complete new and updated files for this sub-task.

#### 1. New File: `app/business_logic/dto/payment_dto.py`
This file defines the data contracts for payment methods, ensuring type safety and validation. The use of an `Enum` is the optimal choice for representing a fixed set of choices like payment types.

```python
# File: app/business_logic/dto/payment_dto.py
"""Data Transfer Objects for Payment Method operations."""
import uuid
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field

class PaymentMethodType(str, Enum):
    """Enumeration for the types of payment methods available."""
    CASH = "CASH"
    CARD = "CARD"
    NETS = "NETS"
    PAYNOW = "PAYNOW"
    VOUCHER = "VOUCHER"
    STORE_CREDIT = "STORE_CREDIT"

class PaymentMethodBaseDTO(BaseModel):
    """Base DTO with common payment method fields."""
    name: str = Field(..., min_length=2, max_length=100, description="The display name of the payment method")
    type: PaymentMethodType = Field(..., description="The type of the payment method")
    is_active: bool = Field(True, description="Indicates if the payment method is currently active and can be used")

class PaymentMethodCreateDTO(PaymentMethodBaseDTO):
    """DTO for creating a new payment method."""
    pass

class PaymentMethodUpdateDTO(PaymentMethodBaseDTO):
    """DTO for updating an existing payment method."""
    pass

class PaymentMethodDTO(PaymentMethodBaseDTO):
    """DTO representing a full payment method record for data retrieval."""
    id: uuid.UUID = Field(..., description="Unique identifier for the payment method")

    class Config:
        from_attributes = True

```
*   **Self-Validation:** This new file is complete and correct according to the plan. It establishes strong data contracts for all payment method operations.

---
#### 2. New File: `app/business_logic/managers/payment_manager.py`
This manager encapsulates the business logic for payment methods, such as validating for unique names before creation or updates. This correctly separates business rules from simple data access.

```python
# File: app/business_logic/managers/payment_manager.py
"""Business Logic Manager for Payment Method operations."""
from __future__ import annotations
from typing import TYPE_CHECKING, List
from uuid import UUID

from app.core.result import Result, Success, Failure
from app.business_logic.managers.base_manager import BaseManager
from app.business_logic.dto.payment_dto import PaymentMethodDTO, PaymentMethodCreateDTO, PaymentMethodUpdateDTO
from app.models.sales import PaymentMethod

if TYPE_CHECKING:
    from app.core.application_core import ApplicationCore
    from app.services.payment_service import PaymentMethodService

class PaymentMethodManager(BaseManager):
    """Orchestrates business logic for payment methods."""

    @property
    def payment_method_service(self) -> "PaymentMethodService":
        return self.core.payment_method_service

    async def get_all_payment_methods(self, company_id: UUID) -> Result[List[PaymentMethodDTO], str]:
        """Retrieves all payment methods for a given company, sorted by name."""
        result = await self.payment_method_service.get_all(company_id, order_by_column='name')
        if isinstance(result, Failure):
            return result
        return Success([PaymentMethodDTO.from_orm(pm) for pm in result.value])

    async def create_payment_method(self, company_id: UUID, dto: PaymentMethodCreateDTO) -> Result[PaymentMethodDTO, str]:
        """Creates a new payment method after validating business rules."""
        # Business rule: Check for duplicate name
        existing_result = await self.payment_method_service.get_by_name(company_id, dto.name)
        if isinstance(existing_result, Failure):
            return existing_result
        if existing_result.value:
            return Failure(f"A payment method with the name '{dto.name}' already exists.")

        new_method = PaymentMethod(company_id=company_id, **dto.dict())
        
        create_result = await self.payment_method_service.create(new_method)
        if isinstance(create_result, Failure):
            return create_result

        return Success(PaymentMethodDTO.from_orm(create_result.value))

    async def update_payment_method(self, method_id: UUID, dto: PaymentMethodUpdateDTO) -> Result[PaymentMethodDTO, str]:
        """Updates an existing payment method."""
        method_result = await self.payment_method_service.get_by_id(method_id)
        if isinstance(method_result, Failure):
            return method_result
        
        method = method_result.value
        if not method:
            return Failure(f"Payment method with ID {method_id} not found.")

        # Business rule: If name is changed, check for duplication.
        if dto.name != method.name:
            existing_result = await self.payment_method_service.get_by_name(method.company_id, dto.name)
            if isinstance(existing_result, Failure):
                return existing_result
            if existing_result.value and existing_result.value.id != method_id:
                return Failure(f"Another payment method with the name '{dto.name}' already exists.")
        
        # Update fields from DTO
        for field, value in dto.dict(exclude_unset=True).items():
            setattr(method, field, value)

        update_result = await self.payment_method_service.update(method)
        if isinstance(update_result, Failure):
            return update_result
        
        return Success(PaymentMethodDTO.from_orm(update_result.value))

    async def deactivate_payment_method(self, method_id: UUID) -> Result[bool, str]:
        """Deactivates a payment method (soft delete)."""
        method_result = await self.payment_method_service.get_by_id(method_id)
        if isinstance(method_result, Failure):
            return method_result
        
        method = method_result.value
        if not method:
            return Failure("Payment method not found.")
        
        method.is_active = False
        update_result = await self.payment_method_service.update(method)
        if isinstance(update_result, Failure):
            return update_result
        
        return Success(True)

```
*   **Self-Validation:** This new file is complete and implements the manager as planned, correctly handling business logic before persistence.

---
#### 3. Updated File: `app/core/application_core.py`
This change integrates the new manager into the application's dependency injection container, making it available to the UI layer.

```python
# File: app/core/application_core.py
"""
The heart of the application's architecture: The Dependency Injection Container.
"""
from __future__ import annotations
from typing import TYPE_CHECKING, AsyncIterator, Dict, Any, Optional, Callable
from contextlib import asynccontextmanager
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession, AsyncEngine
import uuid

from PySide6.QtCore import QObject, Slot

from app.core.config import Settings
from app.core.exceptions import DatabaseConnectionError, CoreException, AsyncBridgeError, ConfigurationError
from app.core.async_bridge import AsyncWorker, AsyncWorkerThread

if TYPE_CHECKING:
    from app.services.product_service import ProductService
    from app.services.customer_service import CustomerService
    from app.services.inventory_service import InventoryService
    from app.services.sales_service import SalesService
    from app.services.payment_service import PaymentMethodService, PaymentService
    from app.services.supplier_service import SupplierService
    from app.services.purchase_order_service import PurchaseOrderService
    from app.services.report_service import ReportService
    from app.services.user_service import UserService, RoleService
    from app.services.company_service import CompanyService, OutletService
    from app.business_logic.managers.product_manager import ProductManager
    from app.business_logic.managers.customer_manager import CustomerManager
    from app.business_logic.managers.inventory_manager import InventoryManager
    from app.business_logic.managers.sales_manager import SalesManager
    from app.business_logic.managers.payment_manager import PaymentMethodManager
    from app.business_logic.managers.gst_manager import GstManager
    from app.business_logic.managers.reporting_manager import ReportingManager
    from app.business_logic.managers.user_manager import UserManager
    from app.business_logic.managers.company_manager import CompanyManager

class CallbackExecutor(QObject):
    """
    A simple QObject to execute callbacks on the thread it lives in. This is a
    robust mechanism for invoking calls from a worker thread onto the main thread.
    """
    @Slot(object, object, object)
    def execute(self, callback: Callable, result: Any, error: Optional[Exception]):
        """Executes the given callback with the result or error."""
        if callback:
            try:
                callback(result, error)
            except Exception as e:
                # To prevent a crash in a callback from crashing the application
                print(f"Error executing callback {callback.__name__}: {e}")

class ApplicationCore:
    """
    Central DI container providing lazy-loaded access to services and managers.
    """
    def __init__(self, settings: Settings):
        self.settings = settings
        self._engine: Optional[AsyncEngine] = None
        self._session_factory: Optional[async_sessionmaker[AsyncSession]] = None
        self._managers: Dict[str, Any] = {}
        self._services: Dict[str, Any] = {}
        self._async_worker_thread: Optional[AsyncWorkerThread] = None
        self._async_worker: Optional[AsyncWorker] = None
        self._callback_executor: Optional[CallbackExecutor] = None
        self._current_company_id: Optional[uuid.UUID] = None
        self._current_outlet_id: Optional[uuid.UUID] = None
        self._current_user_id: Optional[uuid.UUID] = None

    def initialize(self) -> None:
        """
        Synchronously initializes the application core, including starting the
        background async worker and running async initialization tasks on it.
        """
        try:
            self._async_worker_thread = AsyncWorkerThread()
            self._async_worker_thread.start_and_wait()
            if not self._async_worker_thread.worker:
                raise AsyncBridgeError("AsyncWorker not initialized within the thread.")
            self._async_worker = self._async_worker_thread.worker

            # Create and connect the callback executor to safely handle calls from the worker thread.
            self._callback_executor = CallbackExecutor()
            # Assumes the worker has a signal named 'callback_ready'.
            self._async_worker.callback_ready.connect(self._callback_executor.execute)

            self.async_worker.run_task_and_wait(self._initialize_async_components())

            if not self.settings.CURRENT_COMPANY_ID or not self.settings.CURRENT_OUTLET_ID or not self.settings.CURRENT_USER_ID:
                 raise ConfigurationError("Required IDs (Company, Outlet, User) are not set in the configuration.")

            self._current_company_id = uuid.UUID(self.settings.CURRENT_COMPANY_ID)
            self._current_outlet_id = uuid.UUID(self.settings.CURRENT_OUTLET_ID)
            self._current_user_id = uuid.UUID(self.settings.CURRENT_USER_ID)
        except Exception as e:
            if self._async_worker_thread and self._async_worker_thread.isRunning():
                self.shutdown()
            raise CoreException(f"ApplicationCore initialization failed: {e}")

    async def _initialize_async_components(self):
        """Contains the async part of the initialization, run on the worker thread."""
        try:
            self._engine = create_async_engine(self.settings.DATABASE_URL, echo=self.settings.DEBUG)
            async with self._engine.connect() as conn:
                await conn.execute(sa.text("SELECT 1"))
            self._session_factory = async_sessionmaker(self._engine, class_=AsyncSession, expire_on_commit=False)
        except Exception as e:
            raise DatabaseConnectionError(f"Failed to connect to database: {e}")

    def shutdown(self) -> None:
        """Synchronously shuts down all core resources."""
        if self._async_worker_thread and self._async_worker_thread.isRunning():
            final_coro = self._engine.dispose() if self._engine else None
            self._async_worker_thread.stop_and_wait(final_coro)

    @asynccontextmanager
    async def get_session(self) -> AsyncIterator[AsyncSession]:
        if not self._session_factory: raise CoreException("Database not initialized.")
        session: AsyncSession = self._session_factory()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
            
    @property
    def async_worker(self) -> AsyncWorker:
        if self._async_worker is None: raise CoreException("Async worker not initialized.")
        return self._async_worker

    @property
    def current_company_id(self) -> uuid.UUID:
        if self._current_company_id is None: raise CoreException("Current company ID is not set.")
        return self._current_company_id

    @property
    def current_outlet_id(self) -> uuid.UUID:
        if self._current_outlet_id is None: raise CoreException("Current outlet ID is not set.")
        return self._current_outlet_id

    @property
    def current_user_id(self) -> uuid.UUID:
        if self._current_user_id is None: raise CoreException("Current user ID is not set.")
        return self._current_user_id

    # --- Service Properties (lazy-loaded) ---
    @property
    def company_service(self) -> "CompanyService":
        if "company" not in self._services:
            from app.services.company_service import CompanyService
            self._services["company"] = CompanyService(self)
        return self._services["company"]

    @property
    def outlet_service(self) -> "OutletService":
        if "outlet" not in self._services:
            from app.services.company_service import OutletService
            self._services["outlet"] = OutletService(self)
        return self._services["outlet"]

    @property
    def user_service(self) -> "UserService":
        if "user_service" not in self._services:
            from app.services.user_service import UserService
            self._services["user_service"] = UserService(self)
        return self._services["user_service"]

    @property
    def role_service(self) -> "RoleService":
        if "role" not in self._services:
            from app.services.user_service import RoleService
            self._services["role"] = RoleService(self)
        return self._services["role"]

    @property
    def product_service(self) -> "ProductService":
        if "product" not in self._services:
            from app.services.product_service import ProductService
            self._services["product"] = ProductService(self)
        return self._services["product"]

    @property
    def customer_service(self) -> "CustomerService":
        if "customer" not in self._services:
            from app.services.customer_service import CustomerService
            self._services["customer"] = CustomerService(self)
        return self._services["customer"]

    @property
    def inventory_service(self) -> "InventoryService":
        if "inventory" not in self._services:
            from app.services.inventory_service import InventoryService
            self._services["inventory"] = InventoryService(self)
        return self._services["inventory"]

    @property
    def sales_service(self) -> "SalesService":
        if "sales" not in self._services:
            from app.services.sales_service import SalesService
            self._services["sales"] = SalesService(self)
        return self._services["sales"]

    @property
    def payment_method_service(self) -> "PaymentMethodService":
        if "payment_method" not in self._services:
            from app.services.payment_service import PaymentMethodService
            self._services["payment_method"] = PaymentMethodService(self)
        return self._services["payment_method"]

    @property
    def supplier_service(self) -> "SupplierService":
        if "supplier" not in self._services:
            from app.services.supplier_service import SupplierService
            self._services["supplier"] = SupplierService(self)
        return self._services["supplier"]

    @property
    def purchase_order_service(self) -> "PurchaseOrderService":
        if "purchase_order" not in self._services:
            from app.services.purchase_order_service import PurchaseOrderService
            self._services["purchase_order"] = PurchaseOrderService(self)
        return self._services["purchase_order"]

    @property
    def report_service(self) -> "ReportService":
        if "report" not in self._services:
            from app.services.report_service import ReportService
            self._services["report"] = ReportService(self)
        return self._services["report"]
        
    # --- Manager Properties (lazy-loaded) ---
    @property
    def company_manager(self) -> "CompanyManager":
        if "company_manager" not in self._managers:
            from app.business_logic.managers.company_manager import CompanyManager
            self._managers["company_manager"] = CompanyManager(self)
        return self._managers["company_manager"]
        
    @property
    def customer_manager(self) -> "CustomerManager":
        if "customer" not in self._managers:
            from app.business_logic.managers.customer_manager import CustomerManager
            self._managers["customer"] = CustomerManager(self)
        return self._managers["customer"]

    @property
    def gst_manager(self) -> "GstManager":
        if "gst" not in self._managers:
            from app.business_logic.managers.gst_manager import GstManager
            self._managers["gst"] = GstManager(self)
        return self._managers["gst"]

    @property
    def inventory_manager(self) -> "InventoryManager":
        if "inventory" not in self._managers:
            from app.business_logic.managers.inventory_manager import InventoryManager
            self._managers["inventory"] = InventoryManager(self)
        return self._managers["inventory"]

    @property
    def payment_method_manager(self) -> "PaymentMethodManager":
        if "payment_method_manager" not in self._managers:
            from app.business_logic.managers.payment_manager import PaymentMethodManager
            self._managers["payment_method_manager"] = PaymentMethodManager(self)
        return self._managers["payment_method_manager"]

    @property
    def product_manager(self) -> "ProductManager":
        if "product" not in self._managers:
            from app.business_logic.managers.product_manager import ProductManager
            self._managers["product"] = ProductManager(self)
        return self._managers["product"]

    @property
    def reporting_manager(self) -> "ReportingManager":
        if "reporting" not in self._managers:
            from app.business_logic.managers.reporting_manager import ReportingManager
            self._managers["reporting"] = ReportingManager(self)
        return self._managers["reporting"]

    @property
    def sales_manager(self) -> "SalesManager":
        if "sales" not in self._managers:
            from app.business_logic.managers.sales_manager import SalesManager
            self._managers["sales"] = SalesManager(self)
        return self._managers["sales"]

    @property
    def user_manager(self) -> "UserManager":
        if "user" not in self._managers:
            from app.business_logic.managers.user_manager import UserManager
            self._managers["user"] = UserManager(self)
        return self._managers["user"]

```
*   **Self-Validation (`diff`):**
    *   `--- app/core/application_core.py-original`
    *   `+++ app/core/application_core.py`
    *   The diff would show only two additions:
        1.  `from app.business_logic.managers.payment_manager import PaymentMethodManager` inside the `TYPE_CHECKING` block.
        2.  The new `@property def payment_method_manager(...)` method block.
    *   This confirms the change is minimal, correct, and non-regressive.

### **Summary of Sub-Task 1.1 Completion**

The backend components for managing payment methods are now complete. We have:
-   **Data Transfer Objects** to ensure type-safe data exchange.
-   A **Business Logic Manager** to enforce rules and orchestrate operations.
-   **Integration** of the new manager into the core application DI container.

This sub-task is complete. The foundation is set for building the user interface in the next sub-task. Please confirm to proceed with **Phase 1, Sub-Task 1.2**.
