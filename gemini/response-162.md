You are right to demand the utmost care. The `pytest` output clearly indicates that every single test is failing during its setup phase with the exact same error. This points to a fundamental, shared problem in the test configuration, not a problem with the individual tests themselves. I will now perform an exhaustive analysis.

### **1. Systematic Diagnosis & Root Cause Analysis**

*   **The Error:** The log is filled with identical errors for every test function. The key traceback line is:
    ```
    E   ModuleNotFoundError: No module named 'aiosqlite'
    ```
    This error originates in `tests/conftest.py` at line 36, within the `db_engine` fixture, when `create_async_engine(test_db_url)` is called.

*   **Error Breakdown:**
    1.  The `db_engine` fixture in `conftest.py` is correctly configured to use an in-memory SQLite database via the URL `sqlite+aiosqlite:///:memory:`.
    2.  SQLAlchemy, upon receiving this URL, correctly determines that it needs the `aiosqlite` dialect to communicate with SQLite asynchronously.
    3.  The SQLAlchemy dialect code then tries to `__import__("aiosqlite")`.
    4.  This import fails, raising a `ModuleNotFoundError`.

*   **Root Cause:** The `aiosqlite` package, which is the necessary database driver for SQLAlchemy to interact with SQLite in an `async` context, **is not installed in the testing environment.** The project's dependencies are managed by `pyproject.toml`, and this package is missing from the list of development dependencies.

*   **The Pydantic Warnings:** The log also shows several `PydanticDeprecatedSince20` warnings. While not the cause of the failure, they represent technical debt that should be addressed to clean up the test output and ensure future compatibility. My plan from the previous step to fix these was correct, but it was preempted by the `ImportError`. I will now combine the fix for the critical error with the fix for these warnings.

### **2. Strategic Plan for Resolution**

This problem has two parts: the critical missing dependency and the technical debt from the warnings. I will address both in a single, comprehensive update.

**Phase 4, Sub-Task 4.7 (Revised): Fix Test Environment and Modernize DTOs**

1.  **Fix the Missing Dependency:** Add `aiosqlite` to the development dependencies in `pyproject.toml`. This is the root cause and the primary fix.
2.  **Modernize All Pydantic DTOs:** Proactively fix all the deprecation warnings by updating every DTO file to use modern Pydantic V2 syntax. This involves:
    *   Changing `class Config:` to `model_config = ConfigDict(...)`.
    *   Changing `Field(..., min_items=X)` to `Field(..., min_length=X)`.
    *   Changing `@validator(...)` to `@field_validator(...)`.

This combined approach will not only make the tests run but will also silence all warnings, resulting in a perfectly clean test output.

---

### **Generated and Updated Files**

Here are the complete updated replacement files required to fix all identified issues.

#### 1. Updated File: `pyproject.toml`
This change adds the missing `aiosqlite` package to the development dependencies, which will resolve the `ModuleNotFoundError`.

```toml
# pyproject.toml
[tool.poetry]
# --- Project Metadata ---
# This information is used for packaging the application and for display on
# package indexes like PyPI if the project is ever published.
name = "sg-pos-system"
version = "1.0.0"
description = "An enterprise-grade, open-source Point-of-Sale system, meticulously engineered for Singapore's SMB retail landscape."
authors = ["Your Name <you@example.com>"]
license = "MIT"
readme = "README.md"
homepage = "https://github.com/your-org/sg-pos-system"
repository = "https://github.com/your-org/sg-pos-system"
documentation = "https://github.com/your-org/sg-pos-system/blob/main/docs/index.md"
keywords = ["pos", "point-of-sale", "retail", "singapore", "gst", "pyside6", "qt6", "python"]

# --- Python Version Constraint ---
# Specifies that this project is compatible with Python 3.11 and any later minor versions,
# but not Python 4.0. This aligns with the PRD's technology stack choice.
[tool.poetry.dependencies]
python = ">=3.11,<3.14"

# --- Core Production Dependencies ---
# These are the essential packages required for the application to run in production.

# GUI Framework
PySide6 = "^6.9.0"         # The core Qt6 bindings for Python.

# Database & ORM
SQLAlchemy = {version = "^2.0.30", extras = ["asyncio"]} # The industry-standard ORM, with asyncio support.
alembic = "^1.13.1"        # For database schema migrations.
asyncpg = "^0.29.0"        # High-performance asyncio driver for PostgreSQL.

# Data Validation & Settings
pydantic = "^2.7.1"        # For Data Transfer Objects (DTOs) and core validation.
pydantic-settings = "^2.2.1" # FIX: Added for settings management with Pydantic v2.
python-dotenv = "^1.0.0"   # For loading environment variables from .env files.

# Security
bcrypt = "^4.1.2"          # For secure password hashing.
cryptography = "^42.0.7"   # For any custom encryption needs.

# Logging
structlog = "^24.2.0"       # For structured, context-aware logging.

# External Integrations & Utilities
aiohttp = "^3.9.5"         # Asynchronous HTTP client for API integrations.
reportlab = "^4.1.0"       # For generating PDF receipts and reports.
openpyxl = "^3.1.2"        # For exporting data to Excel (.xlsx) files.
qrcode = {version = "^7.4.2", extras = ["pil"]} # For generating QR codes (e.g., for PayNow).


# --- Development Group Dependencies ---
# These packages are only installed in development environments (`poetry install --with dev`).
# This keeps the production installation lean and clean.
[tool.poetry.group.dev.dependencies]
# NEW: Add psycopg2-binary for Alembic's synchronous connection to PostgreSQL
psycopg2-binary = "^2.9.10" # Or latest stable version

# FIX: Add aiosqlite, the async driver needed for the in-memory SQLite test database.
aiosqlite = "^0.20.0"

# Testing Framework
pytest = "^8.2.0"             # The primary testing framework.
pytest-qt = "^4.2.0"          # For testing PySide6 UI components.
pytest-asyncio = "^0.23.0"    # For testing asyncio code.
pytest-cov = "^5.0.0"         # For measuring test coverage.
factory-boy = "^3.3.0"        # For creating test data fixtures.

# Code Quality & Formatting
black = "^24.4.2"            # The uncompromising code formatter.
ruff = "^0.4.4"               # An extremely fast Python linter, replacing flake8, isort, etc.
mypy = "^1.10.0"              # Static type checker for Python.
pre-commit = "^3.7.0"         # For managing and maintaining pre-commit hooks.

# Documentation
Sphinx = "^7.3.1"             # The standard documentation generator for Python projects.
myst-parser = "^2.0.0"        # To write Sphinx documentation in Markdown.
sphinx-rtd-theme = "^2.0.0"   # A popular theme for Sphinx docs.

# Interactive Development
ipython = "^8.24.0"           # A better interactive Python shell.


# ==============================================================================
# Tool Configurations
# ------------------------------------------------------------------------------
# Centralizing tool configurations here makes the project easier to manage.
# ==============================================================================

# --- Black (Code Formatter) Configuration ---
[tool.black]
line-length = 88
target-version = ['py311']
include = '\.pyi?$'
exclude = '''
/(
    \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | _build
  | buck-out
  | build
  | dist
  | migrations
)/
'''

# --- Ruff (Linter) Configuration ---
# Ruff is configured to be strict and to replace multiple older tools.
[tool.ruff]
line-length = 88
target-version = "py311"

# Select a broad range of rules to enforce high code quality.
# See all rules here: https://docs.astral.sh/ruff/rules/
select = [
    "E",  # pycodestyle errors
    "W",  # pycodestyle warnings
    "F",  # pyflakes
    "I",  # isort (import sorting)
    "B",  # flake8-bugbear (finds likely bugs)
    "C4", # flake8-comprehensions
    "UP", # pyupgrade (modernizes syntax)
    "S",  # bandit (security linter)
    "SIM",# flake8-simplify
]
ignore = ["E501"] # Ignored by black formatter anyway.

[tool.ruff.mccabe]
max-complexity = 10 # Keep functions simple and readable.

# --- MyPy (Static Type Checker) Configuration ---
# Enforces strict type checking for robust code.
[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_calls = true
strict_optional = true
show_error_codes = true
exclude = ["migrations/"]


# --- Pytest Configuration ---
[tool.pytest.ini_options]
minversion = "7.0"
addopts = "-ra -q --cov=app --cov-report=term-missing"
testpaths = ["tests"]
python_files = "test_*.py"
asyncio_mode = "auto" # Automatically handle asyncio tests.
qt_api = "pyside6"    # Specify the Qt binding for pytest-qt.


# ==============================================================================
# Build System Configuration
# ------------------------------------------------------------------------------
# This section is required by PEP 517 and tells tools like pip how to build
# the project package. For Poetry, this is standard boilerplate.
# ==============================================================================

[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"

```

#### 2. Updated File: `app/business_logic/dto/company_dto.py`
Modernizes the Pydantic config.

```python
# File: app/business_logic/dto/company_dto.py
"""Data Transfer Objects for Company and Outlet operations."""
import uuid
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

class CompanyBaseDTO(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Legal name of the company")
    registration_number: str = Field(..., min_length=1, max_length=20, description="Singapore UEN (Unique Entity Number)")
    gst_registration_number: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None

class CompanyUpdateDTO(CompanyBaseDTO):
    """DTO for updating a company's information."""
    pass

class CompanyDTO(CompanyBaseDTO):
    """DTO representing a full company record."""
    id: uuid.UUID
    
    model_config = ConfigDict(from_attributes=True)

class OutletDTO(BaseModel):
    """DTO representing a retail outlet."""
    id: uuid.UUID
    name: str
    code: str
    is_active: bool
    
    model_config = ConfigDict(from_attributes=True)
```

#### 3. Updated File: `app/business_logic/dto/customer_dto.py`
Modernizes the Pydantic config.

```python
# File: app/business_logic/dto/customer_dto.py
"""Data Transfer Objects (DTOs) for the Customer entity."""
import uuid
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, EmailStr, ConfigDict

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

    model_config = ConfigDict(from_attributes=True)

class LoyaltyPointAdjustmentDTO(BaseModel):
    """DTO for manually adjusting a customer's loyalty points."""
    customer_id: uuid.UUID
    points_change: int # Can be positive (add) or negative (deduct)
    reason: str = Field(..., min_length=1, description="Reason for the manual adjustment (e.g., 'Goodwill gesture', 'Point correction')")
    admin_user_id: uuid.UUID # User performing the adjustment
```

#### 4. Updated File: `app/business_logic/dto/inventory_dto.py`
Modernizes all configs and replaces `min_items` with `min_length`.

```python
# File: app/business_logic/dto/inventory_dto.py
"""Data Transfer Objects for Inventory and Procurement operations."""
import uuid
from decimal import Decimal
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

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
    model_config = ConfigDict(from_attributes=True)

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
    items: List[PurchaseOrderItemCreateDTO] = Field(..., min_length=1)

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
    model_config = ConfigDict(from_attributes=True)

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
    model_config = ConfigDict(from_attributes=True)

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
    items: List[StockAdjustmentItemDTO] = Field(..., min_length=1)

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
    model_config = ConfigDict(from_attributes=True)

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
    
    model_config = ConfigDict(from_attributes=True)
```

#### 5. Updated File: `app/business_logic/dto/product_dto.py`
Modernizes the config and replaces the legacy `@validator` with the new `@field_validator`.

```python
# File: app/business_logic/dto/product_dto.py
"""
Data Transfer Objects (DTOs) for the Product entity.
"""
import uuid
from decimal import Decimal
from typing import Optional, Any
from pydantic import BaseModel, Field, field_validator, ConfigDict

class ProductBaseDTO(BaseModel):
    """Base DTO with common product fields."""
    sku: str = Field(..., min_length=1, max_length=100, description="Stock Keeping Unit")
    name: str = Field(..., min_length=1, max_length=255, description="Product name")
    description: Optional[str] = Field(None, description="Detailed description of the product")
    selling_price: Decimal = Field(..., gt=Decimal("0.00"), decimal_places=4, description="The retail price of the product")
    cost_price: Decimal = Field(..., ge=Decimal("0.00"), decimal_places=4, description="The cost of acquiring the product")
    gst_rate: Decimal = Field(Decimal("9.00"), ge=Decimal("0.00"), le=Decimal("100.00"), decimal_places=2, description="Goods and Services Tax rate (e.g., 9.00 for 9%)")
    track_inventory: bool = True
    is_active: bool = True
    category_id: Optional[uuid.UUID] = Field(None, description="UUID of the product's category")
    supplier_id: Optional[uuid.UUID] = Field(None, description="UUID of the product's primary supplier")
    barcode: Optional[str] = Field(None, max_length=100, description="Product barcode (EAN, UPC, etc.)")
    reorder_point: int = Field(0, ge=0, description="Threshold quantity for reordering suggestions")

    @field_validator('selling_price')
    @classmethod
    def check_selling_price_not_less_than_cost_price(cls, v: Decimal, values: Any) -> Decimal:
        if 'cost_price' in values.data and v < values.data['cost_price']:
            raise ValueError('Selling price cannot be less than cost price.')
        return v

class ProductCreateDTO(ProductBaseDTO):
    """DTO for creating a new product."""
    pass

class ProductUpdateDTO(ProductBaseDTO):
    """DTO for updating an existing product."""
    pass

class ProductDTO(ProductBaseDTO):
    """DTO representing a full product record, including its unique ID."""
    id: uuid.UUID = Field(..., description="Unique identifier for the product")

    model_config = ConfigDict(from_attributes=True)
```

#### 6. Updated File: `app/business_logic/dto/user_dto.py`
Modernizes the Pydantic config.

```python
# File: app/business_logic/dto/user_dto.py
"""Data Transfer Objects for User operations."""
import uuid
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr, ConfigDict

class UserBaseDTO(BaseModel):
    username: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool = True

class UserCreateDTO(UserBaseDTO):
    password: str = Field(..., min_length=8, description="User's initial password")
    roles: List[uuid.UUID]

class UserUpdateDTO(UserBaseDTO):
    password: Optional[str] = Field(None, min_length=8, description="New password (if changing)")
    roles: List[uuid.UUID]

class RoleDTO(BaseModel):
    id: uuid.UUID
    name: str
    model_config = ConfigDict(from_attributes=True)

class UserDTO(UserBaseDTO):
    id: uuid.UUID
    roles: List[RoleDTO]
    model_config = ConfigDict(from_attributes=True)
```

#### 7. Updated File: `app/business_logic/dto/sales_dto.py`
Modernizes all configs and replaces `min_items` with `min_length`.

```python
# File: app/business_logic/dto/sales_dto.py
"""Data Transfer Objects for Sales operations."""
import uuid
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

class CartItemDTO(BaseModel):
    """DTO representing an item to be added to a sales transaction."""
    product_id: uuid.UUID = Field(..., description="UUID of the product being sold")
    variant_id: Optional[uuid.UUID] = Field(None, description="UUID of the specific product variant, if any")
    quantity: Decimal = Field(..., gt=Decimal("0.00"), decimal_places=4, description="Quantity of the product sold")
    unit_price_override: Optional[Decimal] = Field(None, ge=Decimal("0.00"), decimal_places=4, description="Optional override for unit selling price")

class PaymentInfoDTO(BaseModel):
    """DTO representing a payment to be applied to a sale."""
    payment_method_id: uuid.UUID = Field(..., description="UUID of the payment method used")
    amount: Decimal = Field(..., gt=Decimal("0.00"), decimal_places=2, description="Amount paid using this method")
    reference_number: Optional[str] = Field(None, max_length=100, description="Reference number (e.g., card approval code)")

class SaleCreateDTO(BaseModel):
    """DTO for creating a new sales transaction."""
    company_id: uuid.UUID
    outlet_id: uuid.UUID
    cashier_id: uuid.UUID
    customer_id: Optional[uuid.UUID] = None
    cart_items: List[CartItemDTO] = Field(..., min_length=1)
    payments: List[PaymentInfoDTO] = Field(..., min_length=1)
    notes: Optional[str] = None

class SalesTransactionItemDTO(BaseModel):
    """DTO for a single item within a finalized sales transaction receipt."""
    product_id: uuid.UUID
    variant_id: Optional[uuid.UUID] = None
    product_name: str
    sku: str
    quantity: Decimal = Field(..., decimal_places=4)
    unit_price: Decimal = Field(..., decimal_places=4)
    line_total: Decimal = Field(..., decimal_places=2)
    gst_rate: Decimal = Field(..., decimal_places=2)
    
    model_config = ConfigDict(from_attributes=True)

class FinalizedSaleDTO(BaseModel):
    """DTO representing a completed sale, suitable for generating a receipt."""
    transaction_id: uuid.UUID
    transaction_number: str
    transaction_date: datetime
    subtotal: Decimal = Field(..., decimal_places=2)
    tax_amount: Decimal = Field(..., decimal_places=2)
    discount_amount: Decimal = Field(..., decimal_places=2)
    rounding_adjustment: Decimal = Field(..., decimal_places=2)
    total_amount: Decimal = Field(..., decimal_places=2)
    amount_paid: Decimal = Field(..., decimal_places=2)
    change_due: Decimal = Field(..., decimal_places=2)
    customer_name: Optional[str] = None
    cashier_name: str
    items: List[SalesTransactionItemDTO]
```

### **Summary & Conclusion**

This comprehensive update addresses all identified issues. The critical `ModuleNotFoundError` is resolved by adding the `aiosqlite` dependency, and the technical debt from Pydantic V1 syntax has been fully paid off by modernizing all DTOs.

After applying these changes, you will need to update your Poetry environment once:

```bash
poetry install
```

After the installation, running `pytest` should now proceed without the `ModuleNotFoundError` and without the Pydantic deprecation warnings. The test suite will now be able to run correctly.

---
https://drive.google.com/file/d/11EUoGcc2Ooz7rfBtNPup3kDYyQbLzGCY/view?usp=sharing, https://aistudio.google.com/app/prompts?state=%7B%22ids%22:%5B%2212VGvhlsO4bTWDpTQADljLQwnQ51SA7pp%22%5D,%22action%22:%22open%22,%22userId%22:%22103961307342447084491%22,%22resourceKeys%22:%7B%7D%7D&usp=sharing, https://drive.google.com/file/d/12acS5idyq3W95Z0Yg84jJ_IqSkr8n5Yl/view?usp=sharing, https://drive.google.com/file/d/1EjDki_AWi3zMDnZi1s3ok7W2K9dp-8sv/view?usp=sharing, https://drive.google.com/file/d/1HejEv1nlMxlOSzNkm4qHUdytCe9a0ISg/view?usp=sharing, https://drive.google.com/file/d/1pBPMY3TTXyX-bu7qSeEHZ3QqivmAujF9/view?usp=sharing

