You have done an excellent job in providing this detailed `pytest` output. The error and the warnings are very clear and point to specific issues that need to be addressed. I will now proceed with a meticulous analysis and a plan to fix them.

### **1. Systematic Diagnosis & Root Cause Analysis**

The `pytest` output reveals two distinct types of issues: a single critical `ImportError` that stops the test run, and several `PydanticDeprecatedSince20` warnings that indicate technical debt.

#### **A. The Critical `ImportError`**

*   **Error Message:** `ImportError: cannot import name 'SupplierFactory' from 'tests.factories'`
*   **Location:** The error occurs in `tests/unit/business_logic/managers/test_inventory_manager.py` when it tries to import `SupplierFactory`.
*   **Root Cause:** A simple but critical omission. When I created the `tests/factories.py` file, I created factories for `Company`, `User`, `Product`, `Customer`, and `PaymentMethod`. However, the test for `InventoryManager` (specifically the part that tests creating a purchase order) requires a `Supplier` to be created. I **forgot to create the `SupplierFactory`** in `tests/factories.py`. The test file correctly tries to import it, but it doesn't exist, causing the import to fail and halting the entire test collection process.

#### **B. The Deprecation Warnings**

*   **Warning Type:** `PydanticDeprecatedSince20`
*   **Locations:**
    1.  `_config.py`: A general warning about using class-based `Config` in Pydantic models. All our DTOs use `class Config: from_attributes = True`. The modern approach is to use `model_config = ConfigDict(from_attributes=True)`.
    2.  `fields.py`: A warning about using `min_items` in a `Field`, stating it should be `min_length`. This points directly to our DTOs for `PurchaseOrderCreateDTO` and `StockAdjustmentDTO`.
    3.  `product_dto.py`: A warning about using the old `@validator` syntax. The new syntax is `@field_validator`.
*   **Root Cause:** The DTOs were written using Pydantic V1 syntax, but we are running on Pydantic V2. While V2 provides a compatibility layer (which is why these are warnings, not errors), it is best practice to migrate to the modern V2 syntax to ensure future compatibility and eliminate noisy warnings from the test output.

### **2. Strategic Plan for Resolution**

I will address these issues in two focused sub-tasks. Fixing the critical `ImportError` is the top priority to get the test suite running. Then, we will clean up the technical debt revealed by the warnings.

**Phase 4, Sub-Task 4.7: Fix Test Suite ImportError**
1.  **Modify `tests/factories.py`:** Add the missing `SupplierFactory`.
2.  **Modify `tests/unit/business_logic/managers/test_inventory_manager.py`:** No changes should be needed here, as it was already trying to import the factory correctly. This is just a validation step.

**Phase 4, Sub-Task 4.8: Modernize Pydantic DTOs**
1.  **Update All DTOs:** Go through every DTO file in `app/business_logic/dto/` and update them to Pydantic V2 syntax.
    *   Replace `class Config:` with `model_config = ConfigDict(...)`.
    *   Replace `min_items=...` with `min_length=...`.
    *   Update the `@validator` in `product_dto.py` to the modern `@field_validator` syntax.

I will begin immediately with **Sub-Task 4.7** to unblock the test suite.

---

### **Phase 4, Sub-Task 4.7: Fix Test Suite ImportError**

**Objective:** To resolve the `ImportError` by creating the missing `SupplierFactory`.

**Execution Plan & Checklist:**

1.  **Update `tests/factories.py`:**
    *   [x] Add `Supplier` to the import from `app.models`.
    *   [x] Create a new `SupplierFactory` class inheriting from `SQLAlchemyModelFactory`.
    *   [x] Define its `Meta` class, pointing to the `Supplier` model.
    *   [x] Define its fields (`id`, `company`, `name`, etc.) using `factory` helpers.
2.  **Update `tests/conftest.py`:**
    *   [x] Add the new `factories.SupplierFactory` to the list of factories that get the test session configured in the `db_session` fixture. This is a crucial step to prevent follow-on errors.

---

### **Generated and Updated Files for Sub-Task 4.7**

Here are the complete updated files to resolve the error.

#### 1. Updated File: `tests/factories.py`
This version adds the required `SupplierFactory`.

```python
# File: tests/factories.py
"""
factory-boy classes for creating test data.
"""
import factory
from factory.alchemy import SQLAlchemyModelFactory
from decimal import Decimal
import uuid

from app.models import (
    Company, Outlet, User, Role, Product, Customer, PaymentMethod, Supplier
)

# Note: The session is now configured and injected by the `db_session`
# fixture in `tests/conftest.py`.

class CompanyFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Company
        sqlalchemy_session_persistence = "flush"

    id = factory.LazyFunction(uuid.uuid4)
    name = factory.Faker('company')
    registration_number = factory.Sequence(lambda n: f"UEN{n:08d}")
    is_active = True

class OutletFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Outlet
        sqlalchemy_session_persistence = "flush"

    id = factory.LazyFunction(uuid.uuid4)
    company = factory.SubFactory(CompanyFactory)
    code = factory.Sequence(lambda n: f"OUTLET-{n}")
    name = factory.Faker('word')
    is_active = True

class UserFactory(SQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session_persistence = "flush"

    id = factory.LazyFunction(uuid.uuid4)
    company = factory.SubFactory(CompanyFactory)
    username = factory.Faker('user_name')
    email = factory.Faker('email')
    password_hash = "a_fake_hash"
    is_active = True

class RoleFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Role
        sqlalchemy_session_persistence = "flush"
    
    id = factory.LazyFunction(uuid.uuid4)
    company = factory.SubFactory(CompanyFactory)
    name = factory.Sequence(lambda n: f"Role {n}")
    is_system_role = False

class ProductFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Product
        sqlalchemy_session_persistence = "flush"

    id = factory.LazyFunction(uuid.uuid4)
    company = factory.SubFactory(CompanyFactory)
    sku = factory.Sequence(lambda n: f"SKU{n:04d}")
    name = factory.Faker('word')
    cost_price = Decimal("10.00")
    selling_price = Decimal("20.00")
    gst_rate = Decimal("9.00")
    track_inventory = True
    is_active = True

class CustomerFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Customer
        sqlalchemy_session_persistence = "flush"
    
    id = factory.LazyFunction(uuid.uuid4)
    company = factory.SubFactory(CompanyFactory)
    customer_code = factory.Sequence(lambda n: f"CUST-{n:04d}")
    name = factory.Faker('name')
    is_active = True

class PaymentMethodFactory(SQLAlchemyModelFactory):
    class Meta:
        model = PaymentMethod
        sqlalchemy_session_persistence = "flush"
    
    id = factory.LazyFunction(uuid.uuid4)
    company = factory.SubFactory(CompanyFactory)
    name = factory.Sequence(lambda n: f"Method {n}")
    type = "CASH"
    is_active = True

class SupplierFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Supplier
        sqlalchemy_session_persistence = "flush"
    
    id = factory.LazyFunction(uuid.uuid4)
    company = factory.SubFactory(CompanyFactory)
    name = factory.Faker('company')
    is_active = True
```

#### 2. Updated File: `tests/conftest.py`
This version adds the new `SupplierFactory` to the session configuration logic.

```python
# File: tests/conftest.py
"""
Pytest configuration and fixtures for the entire test suite.
"""
import pytest
import asyncio
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from alembic.config import Config
from alembic import command
import os

from app.core.config import settings
from app.core.application_core import ApplicationCore
from app.models.base import Base
from tests import factories # Import the entire factories module

# --- Test Database Setup ---

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def test_db_url() -> str:
    """Provides a URL for an in-memory SQLite database for testing."""
    return "sqlite+aiosqlite:///:memory:"

@pytest.fixture(scope="session")
async def db_engine(test_db_url: str):
    """Creates an async engine for the test database."""
    engine = create_async_engine(test_db_url)
    yield engine
    await engine.dispose()

@pytest.fixture(scope="session", autouse=True)
async def setup_database(db_engine):
    """
    Sets up the database schema for the entire test session.
    The autouse=True flag ensures this fixture runs for every test session.
    """
    alembic_cfg = Config("alembic.ini")
    Base.metadata.schema = None 
    alembic_cfg.set_main_option("sqlalchemy.url", str(db_engine.url))

    command.upgrade(alembic_cfg, "head")
    yield
    Base.metadata.schema = "sgpos" 


@pytest.fixture
async def db_session(setup_database, db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Provides a clean database session for each test function."""
    session_factory = async_sessionmaker(db_engine, expire_on_commit=False)

    async with session_factory() as session:
        # FIX: Associate the active test session with all factory_boy factories
        factories.CompanyFactory._meta.sqlalchemy_session = session
        factories.OutletFactory._meta.sqlalchemy_session = session
        factories.UserFactory._meta.sqlalchemy_session = session
        factories.RoleFactory._meta.sqlalchemy_session = session
        factories.ProductFactory._meta.sqlalchemy_session = session
        factories.CustomerFactory._meta.sqlalchemy_session = session
        factories.PaymentMethodFactory._meta.sqlalchemy_session = session
        factories.SupplierFactory._meta.sqlalchemy_session = session

        yield session
        
        # Clean up database state after the test
        await session.rollback()
        for table in reversed(Base.metadata.sorted_tables):
            await session.execute(table.delete())
        await session.commit()
        await session.close()


# --- Application Core Fixture ---

@pytest.fixture
def test_settings(test_db_url: str) -> settings:
    """Overrides production settings with test-specific ones."""
    settings.DATABASE_URL = test_db_url
    return settings

@pytest.fixture
async def test_core(test_settings, db_session, monkeypatch) -> ApplicationCore:
    """
    Provides a fully initialized ApplicationCore instance connected
    to the isolated in-memory test database, using monkeypatching for robustness.
    """
    core = ApplicationCore(test_settings)
    
    test_session_factory = async_sessionmaker(db_session.bind, expire_on_commit=False)
    monkeypatch.setattr(core, "_session_factory", test_session_factory)
    monkeypatch.setattr(core, "_engine", db_session.bind)
    
    yield core
```

---
https://drive.google.com/file/d/11EUoGcc2Ooz7rfBtNPup3kDYyQbLzGCY/view?usp=sharing, https://aistudio.google.com/app/prompts?state=%7B%22ids%22:%5B%2212VGvhlsO4bTWDpTQADljLQwnQ51SA7pp%22%5D,%22action%22:%22open%22,%22userId%22:%22103961307342447084491%22,%22resourceKeys%22:%7B%7D%7D&usp=sharing, https://drive.google.com/file/d/1EjDki_AWi3zMDnZi1s3ok7W2K9dp-8sv/view?usp=sharing, https://drive.google.com/file/d/1HejEv1nlMxlOSzNkm4qHUdytCe9a0ISg/view?usp=sharing, https://drive.google.com/file/d/1pBPMY3TTXyX-bu7qSeEHZ3QqivmAujF9/view?usp=sharing

