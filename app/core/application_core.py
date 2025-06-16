# File: app/core/application_core.py
"""
The heart of the application's architecture: The Dependency Injection Container.

The ApplicationCore class is a singleton-like object responsible for creating,
managing, and providing access to all major application services and managers.
It uses a lazy-initialization pattern to ensure resources are only created when
they are first needed.
"""
from __future__ import annotations
from typing import TYPE_CHECKING, AsyncIterator, Dict, Any, Optional
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession, AsyncEngine
import sqlalchemy as sa # Import sa for sa.text

from app.core.config import Settings
from app.core.exceptions import DatabaseConnectionError, CoreException, AsyncBridgeError, ConfigurationError
from app.core.async_bridge import AsyncWorker, AsyncWorkerThread

import uuid # Import uuid for UUID type conversion

# Type checking block to avoid circular imports at runtime
if TYPE_CHECKING:
    # Import all services and managers that will be lazy-loaded
    # This helps mypy and IDEs, but avoids runtime circular imports.
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
    # TODO: Add AccountingManager if it will be a separate entity


class ApplicationCore:
    """
    Central DI container providing lazy-loaded access to services and managers.
    This class is the glue that holds the decoupled components of the system together.
    """

    def __init__(self, settings: Settings):
        """Initializes the core with application settings."""
        self.settings = settings
        self._engine: Optional[AsyncEngine] = None
        self._session_factory: Optional[async_sessionmaker[AsyncSession]] = None
        
        self._managers: Dict[str, Any] = {}
        self._services: Dict[str, Any] = {}

        # Asynchronous Worker Setup
        self._async_worker_thread: Optional[AsyncWorkerThread] = None
        self._async_worker: Optional[AsyncWorker] = None

        # Store current user/company/outlet context (for simplicity in dev)
        # These will be initialized in `initialize()` from settings, or dynamically after login.
        self._current_company_id: Optional[uuid.UUID] = None
        self._current_outlet_id: Optional[uuid.UUID] = None
        self._current_user_id: Optional[uuid.UUID] = None


    async def initialize(self) -> None:
        """
        Initializes essential resources like the database connection pool and async worker.
        This method must be called once at application startup.
        """
        # 1. Initialize database
        try:
            self._engine = create_async_engine(
                self.settings.DATABASE_URL,
                echo=self.settings.DEBUG, # Log SQL statements in debug mode
                pool_size=10, # Max connections in pool
                max_overflow=20, # Max connections above pool_size
            )
            # Verify connection by executing a simple query
            async with self._engine.connect() as conn:
                await conn.execute(sa.text("SELECT 1")) # Use sa.text for literal SQL
                # Ensure the search_path is set correctly for models that don't specify schema
                await conn.execute(sa.text(f"SET search_path TO {self.settings.model_config.get('schema', 'public')}"))


            self._session_factory = async_sessionmaker(
                self._engine, class_=AsyncSession, expire_on_commit=False
            )
        except Exception as e:
            raise DatabaseConnectionError(f"Failed to connect to database: {e}")

        # 2. Start the AsyncWorker thread
        try:
            self._async_worker_thread = AsyncWorkerThread()
            # It's good practice to give threads unique names for debugging
            self._async_worker_thread.setObjectName("AsyncWorkerThread_SG_POS") 
            self._async_worker_thread.start_and_wait() # Blocks until thread is ready
            
            if self._async_worker_thread.worker is None:
                raise AsyncBridgeError("AsyncWorker not initialized within the thread after startup.")
            self._async_worker = self._async_worker_thread.worker
        except Exception as e:
            raise AsyncBridgeError(f"Failed to start async worker thread: {e}")

        # 3. Populate initial context IDs from settings (for development)
        # In a real app, these would be set dynamically after user authentication/login.
        try:
            self._current_company_id = uuid.UUID(self.settings.CURRENT_COMPANY_ID)
            self._current_outlet_id = uuid.UUID(self.settings.CURRENT_OUTLET_ID)
            self._current_user_id = uuid.UUID(self.settings.CURRENT_USER_ID)
        except ValueError as e:
            raise ConfigurationError(f"Invalid UUID format in settings for current context IDs. Please check .env.dev: {e}")


    async def shutdown(self) -> None:
        """Gracefully disposes of resources, like the database connection pool and async worker."""
        print("Shutting down ApplicationCore resources...")
        if self._async_worker_thread:
            print("Stopping async worker thread...")
            self._async_worker_thread.stop_and_wait()
            print("Async worker thread stopped.")
        if self._engine:
            print("Disposing database engine...")
            await self._engine.dispose()
            print("Database engine disposed.")

    @asynccontextmanager
    async def get_session(self) -> AsyncIterator[AsyncSession]:
        """
        Provides a database session for a single unit of work.
        Handles session lifecycle including commit, rollback, and closing.
        """
        if not self._session_factory:
            raise CoreException("Database session factory not initialized. Call core.initialize() first.")
            
        session: AsyncSession = self._session_factory()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise # Re-raise the exception after rollback
        finally:
            await session.close()
            
    @property
    def async_worker(self) -> AsyncWorker:
        """Provides access to the AsyncWorker instance for submitting tasks."""
        if self._async_worker is None:
            raise CoreException("Async worker not initialized. Call core.initialize() first.")
        return self._async_worker

    # --- Context Properties (for use by Managers/Services) ---
    # These provide context (e.g., for multi-tenancy or current user)
    # and should be considered read-only by consuming components.
    @property
    def current_company_id(self) -> uuid.UUID:
        """Returns the UUID of the currently active company, typically from login session."""
        if self._current_company_id is None:
            # In a production app, this would indicate an unauthenticated state
            raise CoreException("Current company ID is not set. User might not be authenticated or session invalid.")
        return self._current_company_id

    @property
    def current_outlet_id(self) -> uuid.UUID:
        """Returns the UUID of the currently active outlet, typically selected by user."""
        if self._current_outlet_id is None:
            raise CoreException("Current outlet ID is not set. User might need to select an outlet.")
        return self._current_outlet_id

    @property
    def current_user_id(self) -> uuid.UUID:
        """Returns the UUID of the currently logged-in user."""
        if self._current_user_id is None:
            raise CoreException("Current user ID is not set. User might not be authenticated.")
        return self._current_user_id

    # --- Service Properties (lazy-loaded) ---
    # These properties provide access to the Data Access Layer services.
    @property
    def company_service(self) -> "CompanyService":
        """Lazy-loaded singleton for CompanyService."""
        if "company" not in self._services:
            from app.services.company_service import CompanyService # Local import
            self._services["company"] = CompanyService(self)
        return self._services["company"]

    @property
    def outlet_service(self) -> "OutletService":
        """Lazy-loaded singleton for OutletService."""
        if "outlet" not in self._services:
            from app.services.company_service import OutletService # OutletService might be in company_service.py
            self._services["outlet"] = OutletService(self)
        return self._services["outlet"]

    @property
    def product_service(self) -> "ProductService":
        """Lazy-loaded singleton for ProductService."""
        if "product" not in self._services:
            from app.services.product_service import ProductService # Local import
            self._services["product"] = ProductService(self)
        return self._services["product"]

    @property
    def customer_service(self) -> "CustomerService":
        """Lazy-loaded singleton for CustomerService."""
        if "customer" not in self._services:
            from app.services.customer_service import CustomerService # Local import
            self._services["customer"] = CustomerService(self)
        return self._services["customer"]

    @property
    def inventory_service(self) -> "InventoryService":
        """Lazy-loaded singleton for InventoryService."""
        if "inventory" not in self._services:
            from app.services.inventory_service import InventoryService # Local import
            self._services["inventory"] = InventoryService(self)
        return self._services["inventory"]

    @property
    def sales_service(self) -> "SalesService":
        """Lazy-loaded singleton for SalesService."""
        if "sales" not in self._services:
            from app.services.sales_service import SalesService # Local import
            self._services["sales"] = SalesService(self)
        return self._services["sales"]

    @property
    def payment_method_service(self) -> "PaymentMethodService": # Use PaymentMethodService as the main
        """Lazy-loaded singleton for PaymentMethodService."""
        if "payment_method" not in self._services:
            from app.services.payment_service import PaymentMethodService # Local import
            self._services["payment_method"] = PaymentMethodService(self)
        return self._services["payment_method"]

    @property
    def payment_service(self) -> "PaymentService": # For general Payment model operations if needed
        """Lazy-loaded singleton for PaymentService (for Payment model)."""
        if "payment" not in self._services:
            from app.services.payment_service import PaymentService # Local import
            self._services["payment"] = PaymentService(self)
        return self._services["payment"]
        
    @property
    def supplier_service(self) -> "SupplierService":
        """Lazy-loaded singleton for SupplierService."""
        if "supplier" not in self._services:
            from app.services.supplier_service import SupplierService # Local import
            self._services["supplier"] = SupplierService(self)
        return self._services["supplier"]

    @property
    def purchase_order_service(self) -> "PurchaseOrderService":
        """Lazy-loaded singleton for PurchaseOrderService."""
        if "purchase_order" not in self._services:
            from app.services.purchase_order_service import PurchaseOrderService # Local import
            self._services["purchase_order"] = PurchaseOrderService(self)
        return self._services["purchase_order"]

    @property
    def report_service(self) -> "ReportService":
        """Lazy-loaded singleton for ReportService."""
        if "report" not in self._services:
            from app.services.report_service import ReportService # Local import
            self._services["report"] = ReportService(self)
        return self._services["report"]

    @property
    def user_service(self) -> "UserService":
        """Lazy-loaded singleton for UserService."""
        if "user" not in self._services:
            from app.services.user_service import UserService # Local import
            self._services["user"] = UserService(self)
        return self._services["user"]

    @property
    def role_service(self) -> "RoleService":
        """Lazy-loaded singleton for RoleService."""
        if "role" not in self._services:
            from app.services.user_service import RoleService # Local import
            self._services["role"] = RoleService(self)
        return self._services["role"]

    # --- Manager Properties (lazy-loaded) ---
    # These properties provide access to the Business Logic Layer managers.
    @property
    def company_manager(self) -> "CompanyManager":
        """Lazy-loaded singleton for CompanyManager."""
        if "company" not in self._managers:
            from app.business_logic.managers.company_manager import CompanyManager # Local import
            self._managers["company"] = CompanyManager(self)
        return self._managers["company"]
        
    @property
    def product_manager(self) -> "ProductManager":
        """Lazy-loaded singleton for ProductManager."""
        if "product" not in self._managers:
            from app.business_logic.managers.product_manager import ProductManager # Local import
            self._managers["product"] = ProductManager(self)
        return self._managers["product"]

    @property
    def customer_manager(self) -> "CustomerManager":
        """Lazy-loaded singleton for CustomerManager."""
        if "customer" not in self._managers:
            from app.business_logic.managers.customer_manager import CustomerManager # Local import
            self._managers["customer"] = CustomerManager(self)
        return self._managers["customer"]

    @property
    def inventory_manager(self) -> "InventoryManager":
        """Lazy-loaded singleton for InventoryManager."""
        if "inventory" not in self._managers:
            from app.business_logic.managers.inventory_manager import InventoryManager # Local import
            self._managers["inventory"] = InventoryManager(self)
        return self._managers["inventory"]

    @property
    def sales_manager(self) -> "SalesManager":
        """Lazy-loaded singleton for SalesManager."""
        if "sales" not in self._managers:
            from app.business_logic.managers.sales_manager import SalesManager # Local import
            self._managers["sales"] = SalesManager(self)
        return self._managers["sales"]

    @property
    def gst_manager(self) -> "GstManager":
        """Lazy-loaded singleton for GstManager."""
        if "gst" not in self._managers:
            from app.business_logic.managers.gst_manager import GstManager # Local import
            self._managers["gst"] = GstManager(self)
        return self._managers["gst"]

    @property
    def reporting_manager(self) -> "ReportingManager":
        """Lazy-loaded singleton for ReportingManager."""
        if "reporting" not in self._managers:
            from app.business_logic.managers.reporting_manager import ReportingManager # Local import
            self._managers["reporting"] = ReportingManager(self)
        return self._managers["reporting"]

    @property
    def user_manager(self) -> "UserManager":
        """Lazy-loaded singleton for UserManager."""
        if "user" not in self._managers:
            from app.business_logic.managers.user_manager import UserManager # Local import
            self._managers["user"] = UserManager(self)
        return self._managers["user"]
    # TODO: Add more managers here as needed (e.g., AccountingManager)
