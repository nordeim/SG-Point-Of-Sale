# File: app/core/application_core.py
"""
The heart of the application's architecture: The Dependency Injection Container.
"""
from __future__ import annotations
from typing import TYPE_CHECKING, AsyncIterator, Dict, Any, Optional
from contextlib import asynccontextmanager
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession, AsyncEngine
import uuid

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
    from app.business_logic.managers.gst_manager import GstManager
    from app.business_logic.managers.reporting_manager import ReportingManager
    from app.business_logic.managers.user_manager import UserManager
    from app.business_logic.managers.company_manager import CompanyManager

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

            self.async_worker.run_task_and_wait(self._initialize_async_components())

            self._current_company_id = uuid.UUID(self.settings.CURRENT_COMPANY_ID)
            self._current_outlet_id = uuid.UUID(self.settings.CURRENT_OUTLET_ID)
            self._current_user_id = uuid.UUID(self.settings.CURRENT_USER_ID)
        except Exception as e:
            if self._async_worker_thread and self._async_worker_thread.isRunning():
                self.shutdown()
            raise CoreException(f"ApplicationCore initialization failed: {e}") from e

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
    def user_manager(self) -> "UserManager":
        if "user" not in self._managers:
            from app.business_logic.managers.user_manager import UserManager
            self._managers["user"] = UserManager(self)
        return self._managers["user"]

    @property
    def product_manager(self) -> "ProductManager":
        if "product" not in self._managers:
            from app.business_logic.managers.product_manager import ProductManager
            self._managers["product"] = ProductManager(self)
        return self._managers["product"]

    @property
    def customer_manager(self) -> "CustomerManager":
        if "customer" not in self._managers:
            from app.business_logic.managers.customer_manager import CustomerManager
            self._managers["customer"] = CustomerManager(self)
        return self._managers["customer"]

    @property
    def inventory_manager(self) -> "InventoryManager":
        if "inventory" not in self._managers:
            from app.business_logic.managers.inventory_manager import InventoryManager
            self._managers["inventory"] = InventoryManager(self)
        return self._managers["inventory"]

    @property
    def sales_manager(self) -> "SalesManager":
        if "sales" not in self._managers:
            from app.business_logic.managers.sales_manager import SalesManager
            self._managers["sales"] = SalesManager(self)
        return self._managers["sales"]

    @property
    def gst_manager(self) -> "GstManager":
        if "gst" not in self._managers:
            from app.business_logic.managers.gst_manager import GstManager
            self._managers["gst"] = GstManager(self)
        return self._managers["gst"]

    @property
    def reporting_manager(self) -> "ReportingManager":
        if "reporting" not in self._managers:
            from app.business_logic.managers.reporting_manager import ReportingManager
            self._managers["reporting"] = ReportingManager(self)
        return self._managers["reporting"]
