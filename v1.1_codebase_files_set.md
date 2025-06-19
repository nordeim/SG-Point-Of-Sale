# pyproject.toml
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

# .env.example
```example
# SG-POS Development Environment Configuration
# Copy this file to .env.dev and fill in the values.
# IMPORTANT: Ensure .env.dev is NOT committed to version control in production!

# --- PostgreSQL Database Configuration ---
# These are used by both Docker Compose to initialize the DB
# and by the application to connect to it.
POSTGRES_USER=sgpos_dev_user
POSTGRES_PASSWORD=a_very_secure_password_for_dev # *** REPLACE WITH A STRONG PASSWORD ***
POSTGRES_DB=sgpos_dev

# --- Application Configuration ---
# The natively-run Python app will read this file via app/core/config.py.
DATABASE_URL="postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@localhost:5432/${POSTGRES_DB}"

# Application-level settings
APP_ENV=development
DEBUG=True
LOG_LEVEL=DEBUG # DEBUG, INFO, WARNING, ERROR, CRITICAL
SECRET_KEY=a_super_secret_dev_key_that_is_not_for_production # *** REPLACE WITH A STRONG, UNIQUE KEY ***

# --- Example: For stage 4 to simulate current user/company/outlet context ---
# In a real app, these would come from authentication/session management
CURRENT_COMPANY_ID=00000000-0000-0000-0000-000000000001
CURRENT_OUTLET_ID=00000000-0000-0000-0000-000000000002
CURRENT_USER_ID=00000000-0000-0000-0000-000000000003


```

# .gitignore
```txt
# Byte-code files
*.pyc
__pycache__/

# Virtual environment directories (commonly used by Poetry or custom setups)
bin/
include/
lib/
lib64
.venv/
env/
venv/

# Environment variables
.env
.env.dev
.env.production
*.env # General ignore for .env files

# Poetry specific
.venv/
poetry.lock

# Database specific
*.db
*.sqlite
data/

# PySide6/Qt specific
*.ui
*.qrc
*.moc
*.qmlc
*.pyi
debug/
release/

# Build artifacts
build/
dist/
*.egg-info/

# Test coverage
.coverage
.pytest_cache/
htmlcov/

# MyPy cache
.mypy_cache/

# Editors & IDEs
.vscode/
.idea/
*.sublime-project
*.sublime-workspace

# Logs
*.log
logs/

# OS generated files
.DS_Store
Thumbs.db

```

# docker-compose.dev.yml
```yml
version: '3.8'

services:
  db:
    image: postgres:16-alpine
    container_name: sgpos_dev_db
    env_file:
      - .env.dev
    ports:
      - "5432:5432"
    volumes:
      - postgres_dev_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 10s
    restart: unless-stopped

volumes:
  postgres_dev_data:
    driver: local


```

# alembic.ini
```ini
# alembic.ini
# This is the Alembic configuration file.

[alembic]
script_location = migrations
# IMPORTANT: This connects to the DATABASE_URL defined in your .env.dev file
sqlalchemy.url = ${DATABASE_URL}
revision_table_name = alembic_version

# Logging configuration
# For more information about the Python standard library's logging configuration:
# https://docs.python.org/3/library/logging.config.html#logging-config-fileformat

[loggers]
keys = root, alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = INFO
handlers = console
qualname =

[logger_alembic]
level = INFO
handlers = console
qualname = alembic

[handler_console]
class = StreamHandler
formatter = generic
args = (sys.stderr,)

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S


```

# app/main.py
```py
# File: app/main.py
"""
SG-POS Application Entry Point.

This script initializes the core application components, sets up the asynchronous
bridge, creates the main UI window, and starts the Qt event loop.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from typing import Optional
from PySide6.QtWidgets import QApplication, QMessageBox

from app.core.application_core import ApplicationCore
from app.core.config import settings
from app.core.exceptions import CoreException
from app.ui.main_window import MainWindow

def main():
    """Initializes and runs the SG-POS application."""
    app = QApplication(sys.argv)
    
    # The previous call to qRegisterMetaType(object) has been removed because
    # the newer versions of PySide6 handle type registration automatically.

    core: Optional[ApplicationCore] = None
    exit_code = 0

    try:
        core = ApplicationCore(settings)
        core.initialize()

        main_window = MainWindow(core)
        main_window.show()

        exit_code = app.exec()

    except CoreException as e:
        QMessageBox.critical(
            None,
            "SG-POS Startup Error",
            f"A critical error occurred during startup:\n\n{e}\n\nThe application will now exit."
        )
        print(f"FATAL: {e}", file=sys.stderr)
        exit_code = 1
    except Exception as e:
        QMessageBox.critical(
            None,
            "SG-POS Unexpected Error",
            f"An unexpected error occurred:\n\n{e}\n\nThe application will now exit."
        )
        print(f"FATAL: Unexpected error: {e}", file=sys.stderr)
        exit_code = 1
    finally:
        if core:
            print("Shutting down core resources...")
            core.shutdown()
            print("Shutdown complete.")

    return exit_code

if __name__ == "__main__":
    sys.exit(main())


```

# app/integrations/__init__.py
```py

```

# app/__init__.py
```py

```

# app/ui/__init__.py
```py

```

# app/ui/dialogs/stock_adjustment_dialog.py
```py
# File: app/ui/dialogs/stock_adjustment_dialog.py
"""
A QDialog for performing stock adjustments.

This dialog allows users to add products, input their physically counted quantities,
and submit the adjustment. It orchestrates the process by:
1. Fetching product and current stock level data asynchronously.
2. Collecting user input for new quantities and adjustment notes.
3. Creating a StockAdjustmentDTO.
4. Calling the InventoryManager to process the adjustment asynchronously.
5. Handling the success or failure result to provide user feedback.
"""
from __future__ import annotations
from decimal import Decimal
from typing import List, Optional, Any
import uuid

from PySide6.QtCore import (
    Qt, QAbstractTableModel, QModelIndex, Slot, Signal, QObject, QPoint
)
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit,
    QTableView, QPushButton, QDialogButtonBox, QTextEdit, QMessageBox,
    QHeaderView, QMenu
)

from app.business_logic.dto.inventory_dto import StockAdjustmentDTO, StockAdjustmentItemDTO
from app.business_logic.dto.product_dto import ProductDTO
from app.core.application_core import ApplicationCore
from app.core.result import Success, Failure
from app.core.async_bridge import AsyncWorker

class AdjustmentLineItem(QObject):
    """Helper class to hold and represent adjustment line item data for the TableModel."""
    def __init__(self, product: ProductDTO, system_qty: Decimal, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.product = product
        self.system_qty = system_qty
        self.counted_qty: Optional[Decimal] = None

    @property
    def variance(self) -> Decimal:
        if self.counted_qty is None: return Decimal("0")
        return (self.counted_qty - self.system_qty).quantize(Decimal("0.0001"))

    def to_stock_adjustment_item_dto(self) -> StockAdjustmentItemDTO:
        return StockAdjustmentItemDTO(product_id=self.product.id, variant_id=None, counted_quantity=self.counted_qty) # TODO: Handle variant_id


class StockAdjustmentTableModel(QAbstractTableModel):
    """A Qt Table Model for managing items in the stock adjustment dialog."""
    HEADERS = ["SKU", "Product Name", "System Quantity", "Counted Quantity", "Variance"]
    COLUMN_COUNTED_QTY = 3

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._items: List[AdjustmentLineItem] = []
        self.data_changed_signal = Signal()

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int: return len(self._items)
    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int: return len(self.HEADERS)
    def headerData(self, s, o, r=Qt.DisplayRole):
        if r == Qt.DisplayRole and o == Qt.Horizontal: return self.HEADERS[s]
    def data(self, i, r=Qt.DisplayRole):
        if not i.isValid(): return None
        item = self._items[i.row()]
        col = i.column()
        if r == Qt.DisplayRole:
            if col == 0: return item.product.sku
            if col == 1: return item.product.name
            if col == 2: return str(item.system_qty)
            if col == 3: return str(item.counted_qty) if item.counted_qty is not None else ""
            if col == 4: v = item.variance; return f"+{v}" if v > 0 else str(v)
        if r == Qt.EditRole and col == self.COLUMN_COUNTED_QTY: return str(item.counted_qty or "")
        if r == Qt.TextAlignmentRole and col in [2, 3, 4]: return Qt.AlignRight | Qt.AlignVCenter
    def setData(self, i, v, r=Qt.EditRole):
        if r == Qt.EditRole and i.column() == self.COLUMN_COUNTED_QTY:
            try:
                self._items[i.row()].counted_qty = Decimal(v) if str(v).strip() else None
                self.dataChanged.emit(i, self.createIndex(i.row(), self.columnCount() - 1))
                self.data_changed_signal.emit()
                return True
            except: return False
        return False
    def flags(self, i):
        flags = super().flags(i)
        if i.column() == self.COLUMN_COUNTED_QTY: flags |= Qt.ItemIsEditable
        return flags
    def add_item(self, item: AdjustmentLineItem):
        if any(i.product.id == item.product.id for i in self._items):
            QMessageBox.information(self.parent(), "Duplicate Item", f"Product '{item.product.name}' is already in the list.")
            return
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount()); self._items.append(item); self.endInsertRows()
        self.data_changed_signal.emit()
    def remove_item_at_row(self, r):
        if 0 <= r < len(self._items):
            self.beginRemoveRows(QModelIndex(), r, r); del self._items[r]; self.endRemoveRows()
            self.data_changed_signal.emit()
    def get_adjustment_items(self): return [i.to_stock_adjustment_item_dto() for i in self._items if i.counted_qty is not None]

class StockAdjustmentDialog(QDialog):
    """A dialog for creating and submitting a stock adjustment."""
    operation_completed = Signal()

    def __init__(self, core: ApplicationCore, outlet_id: uuid.UUID, user_id: uuid.UUID, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.core = core
        self.async_worker: AsyncWorker = core.async_worker
        self.company_id = self.core.current_company_id
        self.outlet_id = outlet_id
        self.user_id = user_id
        self.setWindowTitle("Perform Stock Adjustment")
        self.setMinimumSize(800, 600)
        self._setup_ui()
        self._connect_signals()
        self._on_data_changed()

    def _setup_ui(self):
        self.product_search_input = QLineEdit(); self.product_search_input.setPlaceholderText("Enter Product SKU or Name to add...")
        self.add_product_button = QPushButton("Add Product"); search_layout = QHBoxLayout()
        search_layout.addWidget(self.product_search_input, 1); search_layout.addWidget(self.add_product_button)
        self.adjustment_table = QTableView(); self.table_model = StockAdjustmentTableModel(parent=self)
        self.adjustment_table.setModel(self.table_model); self.adjustment_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.adjustment_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.notes_input = QTextEdit(); self.notes_input.setPlaceholderText("Provide a reason (e.g., 'Annual stock count', 'Wastage')...")
        self.button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel); self.button_box.button(QDialogButtonBox.Save).setText("Submit Adjustment")
        main_layout = QVBoxLayout(self); main_layout.addLayout(search_layout); main_layout.addWidget(self.adjustment_table)
        main_layout.addWidget(QLabel("Adjustment Notes/Reason:")); main_layout.addWidget(self.notes_input, 1); main_layout.addWidget(self.button_box)

    def _connect_signals(self):
        self.add_product_button.clicked.connect(self._on_add_product_clicked)
        self.product_search_input.returnPressed.connect(self._on_add_product_clicked)
        self.button_box.accepted.connect(self._on_submit_adjustment_clicked)
        self.button_box.rejected.connect(self.reject)
        self.table_model.data_changed_signal.connect(self._on_data_changed)
        self.notes_input.textChanged.connect(self._on_data_changed)
        self.adjustment_table.customContextMenuRequested.connect(self._on_table_context_menu)

    @Slot()
    def _on_data_changed(self):
        self.button_box.button(QDialogButtonBox.Save).setEnabled(bool(self.notes_input.toPlainText().strip()) and bool(self.table_model.get_adjustment_items()))

    @Slot()
    def _on_add_product_clicked(self):
        search_term = self.product_search_input.text().strip()
        if not search_term: return
        def _on_product_search_done(result: Any, error: Optional[Exception]):
            if error or isinstance(result, Failure): QMessageBox.warning(self, "Product Lookup Failed", f"Could not find product: {error or result.error}"); return
            if isinstance(result, Success):
                products: List[ProductDTO] = result.value
                if not products: QMessageBox.warning(self, "Not Found", f"No product found for '{search_term}'."); return
                p = products[0]
                def _on_stock_fetch_done(stock_res, stock_err):
                    if stock_err or isinstance(stock_res, Failure): QMessageBox.critical(self, "Error", f"Failed to get stock level: {stock_err or stock_res.error}"); return
                    if isinstance(stock_res, Success):
                        self.table_model.add_item(AdjustmentLineItem(p, stock_res.value))
                        self.product_search_input.clear(); self.product_search_input.setFocus()
                self.async_worker.run_task(self.core.inventory_service.get_stock_level(self.outlet_id, p.id, None), _on_stock_fetch_done)
        self.async_worker.run_task(self.core.product_manager.search_products(self.company_id, search_term, limit=1), _on_product_search_done)

    @Slot()
    def _on_submit_adjustment_clicked(self):
        dto = StockAdjustmentDTO(company_id=self.company_id, outlet_id=self.outlet_id, user_id=self.user_id,
                                 notes=self.notes_input.toPlainText().strip(), items=self.table_model.get_adjustment_items())
        self.button_box.button(QDialogButtonBox.Save).setEnabled(False)
        def _on_done(r, e):
            self.button_box.button(QDialogButtonBox.Save).setEnabled(True)
            if e or isinstance(r, Failure): QMessageBox.critical(self, "Submission Failed", f"Could not submit adjustment: {e or r.error}")
            elif isinstance(r, Success):
                QMessageBox.information(self, "Success", "Stock adjustment submitted successfully."); self.operation_completed.emit(); self.accept()
        self.async_worker.run_task(self.core.inventory_manager.adjust_stock(dto), _on_done)

    @Slot(QPoint)
    def _on_table_context_menu(self, pos: QPoint):
        index = self.adjustment_table.indexAt(pos)
        if not index.isValid(): return
        menu = QMenu(self)
        remove_action = menu.addAction("Remove Item")
        if menu.exec(self.adjustment_table.mapToGlobal(pos)) == remove_action:
            self.table_model.remove_item_at_row(index.row())

```

# app/ui/dialogs/__init__.py
```py

```

# app/ui/dialogs/customer_dialog.py
```py
# File: app/ui/dialogs/customer_dialog.py
"""A QDialog for creating and editing Customer entities."""
from decimal import Decimal
from typing import Optional, Any, Union
import uuid

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit,
    QDoubleSpinBox, QCheckBox, QDialogButtonBox, QMessageBox, QTextEdit
)
from PySide6.QtCore import Slot, Signal, QObject

from app.business_logic.dto.customer_dto import CustomerCreateDTO, CustomerUpdateDTO, CustomerDTO
from app.core.application_core import ApplicationCore
from app.core.result import Success, Failure
from app.core.async_bridge import AsyncWorker

class CustomerDialog(QDialog):
    """A dialog for creating or editing a customer."""

    customer_operation_completed = Signal(bool, str) # Signal for CustomerView to refresh

    def __init__(self, core: ApplicationCore, customer: Optional[CustomerDTO] = None, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.core = core
        self.async_worker: AsyncWorker = core.async_worker
        self.customer = customer
        self.is_edit_mode = customer is not None

        self.setWindowTitle("Edit Customer" if self.is_edit_mode else "Add New Customer")
        self.setMinimumWidth(400)

        self._setup_ui()
        self._connect_signals()

        if self.is_edit_mode:
            self._populate_form()

    def _setup_ui(self):
        """Initializes the UI widgets and layout."""
        # --- Create Widgets ---
        self.customer_code_input = QLineEdit()
        self.name_input = QLineEdit()
        self.email_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.address_input = QTextEdit()
        self.credit_limit_input = QDoubleSpinBox()
        self.credit_limit_input.setRange(0, 9999999.99)
        self.credit_limit_input.setDecimals(2)
        self.is_active_checkbox = QCheckBox("Is Active")

        # --- Layout ---
        form_layout = QFormLayout()
        form_layout.addRow("Customer Code:", self.customer_code_input)
        form_layout.addRow("Name:", self.name_input)
        form_layout.addRow("Email:", self.email_input)
        form_layout.addRow("Phone:", self.phone_input)
        form_layout.addRow("Address:", self.address_input)
        form_layout.addRow("Credit Limit (S$):", self.credit_limit_input)
        form_layout.addRow(self.is_active_checkbox)
        
        self.button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        self.button_box.button(QDialogButtonBox.Save).setText("Save Customer")
        
        main_layout = QVBoxLayout(self)
        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.button_box)

        # Set defaults for new customer
        if not self.is_edit_mode:
            self.is_active_checkbox.setChecked(True)

    def _connect_signals(self):
        """Connects UI signals to slots."""
        self.button_box.accepted.connect(self._on_save_accepted)
        self.button_box.rejected.connect(self.reject)

    def _populate_form(self):
        """Populates the form fields with existing customer data in edit mode."""
        if self.customer:
            self.customer_code_input.setText(self.customer.customer_code)
            self.name_input.setText(self.customer.name)
            self.email_input.setText(self.customer.email or "")
            self.phone_input.setText(self.customer.phone or "")
            self.address_input.setPlainText(self.customer.address or "")
            self.credit_limit_input.setValue(float(self.customer.credit_limit))
            self.is_active_checkbox.setChecked(self.customer.is_active)

    def _get_dto(self) -> Union[CustomerCreateDTO, CustomerUpdateDTO]:
        """Constructs a DTO from the current form data."""
        common_data = {
            "customer_code": self.customer_code_input.text().strip(),
            "name": self.name_input.text().strip(),
            "email": self.email_input.text().strip() or None,
            "phone": self.phone_input.text().strip() or None,
            "address": self.address_input.toPlainText().strip() or None,
            "credit_limit": Decimal(str(self.credit_limit_input.value())),
        }
        if self.is_edit_mode:
            return CustomerUpdateDTO(**common_data, is_active=self.is_active_checkbox.isChecked())
        else:
            return CustomerCreateDTO(**common_data)

    @Slot()
    def _on_save_accepted(self):
        """Handles the save action, triggering the async operation."""
        dto = self._get_dto()
        company_id = self.core.current_company_id

        try:
            if self.is_edit_mode:
                coro = self.core.customer_manager.update_customer(self.customer.id, dto)
                success_msg = f"Customer '{dto.name}' updated successfully!"
                error_prefix = "Failed to update customer:"
            else:
                coro = self.core.customer_manager.create_customer(company_id, dto)
                success_msg = f"Customer '{dto.name}' created successfully!"
                error_prefix = "Failed to create customer:"

            self.button_box.button(QDialogButtonBox.Save).setEnabled(False)
            
            def _on_done(result: Any, error: Optional[Exception]):
                self.button_box.button(QDialogButtonBox.Save).setEnabled(True)
                if error:
                    QMessageBox.critical(self, "Error", f"{error_prefix}\n{error}")
                    self.customer_operation_completed.emit(False, str(error))
                elif isinstance(result, Success):
                    QMessageBox.information(self, "Success", success_msg)
                    self.customer_operation_completed.emit(True, success_msg)
                    self.accept()
                elif isinstance(result, Failure):
                    QMessageBox.warning(self, "Validation Error", f"{error_prefix}\n{result.error}")
                    self.customer_operation_completed.emit(False, result.error)
                else:
                    QMessageBox.critical(self, "Internal Error", f"Unexpected result type from manager: {type(result)}")
                    self.customer_operation_completed.emit(False, "An unexpected internal error occurred.")

            self.async_worker.run_task(coro, on_done_callback=_on_done)

        except Exception as e:
            QMessageBox.critical(self, "Application Error", f"An internal error prevented the operation:\n{e}")
            self.customer_operation_completed.emit(False, f"Internal error: {e}")
            self.button_box.button(QDialogButtonBox.Save).setEnabled(True)

```

# app/ui/dialogs/product_dialog.py
```py
# File: app/ui/dialogs/product_dialog.py
"""A QDialog for creating and editing Product entities."""
from __future__ import annotations
from decimal import Decimal
from typing import Optional, Any, Union
import uuid

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit,
    QDoubleSpinBox, QCheckBox, QDialogButtonBox, QMessageBox, QTextEdit
)
from PySide6.QtCore import Slot, Signal, QObject

from app.business_logic.dto.product_dto import ProductCreateDTO, ProductUpdateDTO, ProductDTO
from app.core.application_core import ApplicationCore
from app.core.result import Success, Failure
from app.core.async_bridge import AsyncWorker

class ProductDialog(QDialog):
    """A dialog for creating or editing a product."""
    product_operation_completed = Signal(bool, str)

    def __init__(self, core: ApplicationCore, product: Optional[ProductDTO] = None, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.core = core
        self.async_worker: AsyncWorker = core.async_worker
        self.product = product
        self.is_edit_mode = product is not None

        self.setWindowTitle("Edit Product" if self.is_edit_mode else "Add New Product")
        self.setMinimumWidth(400)

        self._setup_ui()
        self._connect_signals()

        if self.is_edit_mode:
            self._populate_form()

    def _setup_ui(self):
        self.sku_input = QLineEdit()
        self.name_input = QLineEdit()
        self.description_input = QTextEdit()
        self.selling_price_input = QDoubleSpinBox()
        self.selling_price_input.setRange(0, 999999.99); self.selling_price_input.setDecimals(2)
        self.cost_price_input = QDoubleSpinBox()
        self.cost_price_input.setRange(0, 999999.99); self.cost_price_input.setDecimals(2)
        self.is_active_checkbox = QCheckBox("Is Active")

        form_layout = QFormLayout()
        form_layout.addRow("SKU:", self.sku_input)
        form_layout.addRow("Name:", self.name_input)
        form_layout.addRow("Description:", self.description_input)
        form_layout.addRow("Selling Price (S$):", self.selling_price_input)
        form_layout.addRow("Cost Price (S$):", self.cost_price_input)
        form_layout.addRow(self.is_active_checkbox)
        
        self.button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        main_layout = QVBoxLayout(self)
        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.button_box)

        if not self.is_edit_mode: self.is_active_checkbox.setChecked(True)

    def _connect_signals(self):
        self.button_box.accepted.connect(self._on_save_accepted)
        self.button_box.rejected.connect(self.reject)

    def _populate_form(self):
        if self.product:
            self.sku_input.setText(self.product.sku)
            self.name_input.setText(self.product.name)
            self.description_input.setPlainText(self.product.description or "")
            self.selling_price_input.setValue(float(self.product.selling_price))
            self.cost_price_input.setValue(float(self.product.cost_price))
            self.is_active_checkbox.setChecked(self.product.is_active)

    def _get_dto(self) -> Union[ProductCreateDTO, ProductUpdateDTO, None]:
        try:
            common_data = {
                "sku": self.sku_input.text().strip(),
                "name": self.name_input.text().strip(),
                "description": self.description_input.toPlainText().strip() or None,
                "selling_price": Decimal(str(self.selling_price_input.value())),
                "cost_price": Decimal(str(self.cost_price_input.value())),
                "is_active": self.is_active_checkbox.isChecked(),
            }
            if self.is_edit_mode:
                return ProductUpdateDTO(**common_data)
            else:
                return ProductCreateDTO(**common_data)
        except Exception as e:
            QMessageBox.warning(self, "Invalid Input", f"Please check your inputs: {e}")
            return None

    @Slot()
    def _on_save_accepted(self):
        dto = self._get_dto()
        if not dto: return

        company_id = self.core.current_company_id
        if self.is_edit_mode:
            coro = self.core.product_manager.update_product(self.product.id, dto)
            success_msg, error_prefix = f"Product '{dto.name}' updated successfully!", "Failed to update product:"
        else:
            coro = self.core.product_manager.create_product(company_id, dto)
            success_msg, error_prefix = f"Product '{dto.name}' created successfully!", "Failed to create product:"

        self.button_box.button(QDialogButtonBox.Save).setEnabled(False)
        def _on_done(result: Any, error: Optional[Exception]):
            self.button_box.button(QDialogButtonBox.Save).setEnabled(True)
            if error:
                QMessageBox.critical(self, "Error", f"{error_prefix}\n{error}")
                self.product_operation_completed.emit(False, str(error))
            elif isinstance(result, Success):
                QMessageBox.information(self, "Success", success_msg)
                self.product_operation_completed.emit(True, success_msg)
                self.accept()
            elif isinstance(result, Failure):
                QMessageBox.warning(self, "Validation Error", f"{error_prefix}\n{result.error}")
                self.product_operation_completed.emit(False, result.error)

        self.async_worker.run_task(coro, on_done_callback=_on_done)

```

# app/ui/dialogs/purchase_order_dialog.py
```py
# File: app/ui/dialogs/purchase_order_dialog.py
"""A QDialog for creating and managing Purchase Orders (POs)."""
from __future__ import annotations
from decimal import Decimal
from typing import List, Optional, Any
import uuid
from datetime import datetime

from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex, Slot, Signal, QObject, QDate, QPoint
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit,
    QTableView, QPushButton, QDialogButtonBox, QTextEdit, QMessageBox,
    QComboBox, QDateEdit, QHeaderView, QMenu
)

from app.business_logic.dto.inventory_dto import PurchaseOrderCreateDTO, PurchaseOrderItemCreateDTO, SupplierDTO
from app.business_logic.dto.product_dto import ProductDTO
from app.core.application_core import ApplicationCore
from app.core.result import Success, Failure
from app.core.async_bridge import AsyncWorker

class POLineItem(QObject):
    """Helper class to hold and represent PO line item data for the TableModel."""
    def __init__(self, product: ProductDTO, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.product = product
        self.quantity: Decimal = Decimal("1.0000")
        self.unit_cost: Decimal = product.cost_price

    @property
    def total_cost(self) -> Decimal:
        return (self.quantity * self.unit_cost).quantize(Decimal("0.01"))

    def to_create_dto(self) -> PurchaseOrderItemCreateDTO:
        return PurchaseOrderItemCreateDTO(
            product_id=self.product.id,
            variant_id=None, # TODO: Handle variants
            quantity_ordered=self.quantity,
            unit_cost=self.unit_cost
        )

class PurchaseOrderTableModel(QAbstractTableModel):
    """A Qt Table Model for managing items in a Purchase Order."""
    HEADERS = ["SKU", "Product Name", "Quantity", "Unit Cost (S$)", "Total Cost (S$)"]
    COLUMN_QTY, COLUMN_UNIT_COST = 2, 3
    total_cost_changed = Signal()

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._items: List[POLineItem] = []

    def rowCount(self, p=QModelIndex()): return len(self._items)
    def columnCount(self, p=QModelIndex()): return len(self.HEADERS)
    def headerData(self, s, o, r=Qt.DisplayRole):
        if r == Qt.DisplayRole and o == Qt.Horizontal: return self.HEADERS[s]
    def data(self, i, r=Qt.DisplayRole):
        if not i.isValid(): return
        item, col = self._items[i.row()], i.column()
        if r == Qt.DisplayRole:
            if col == 0: return item.product.sku
            if col == 1: return item.product.name
            if col == 2: return f"{item.quantity:.4f}"
            if col == 3: return f"{item.unit_cost:.4f}"
            if col == 4: return f"{item.total_cost:.2f}"
        if r == Qt.EditRole:
            if col == self.COLUMN_QTY: return str(item.quantity)
            if col == self.COLUMN_UNIT_COST: return str(item.unit_cost)
        if r == Qt.TextAlignmentRole and col in [2, 3, 4]: return Qt.AlignRight | Qt.AlignVCenter
    def setData(self, i, v, r=Qt.EditRole):
        if r != Qt.EditRole: return False
        item, col = self._items[i.row()], i.column()
        try:
            if col == self.COLUMN_QTY:
                new_qty = Decimal(v)
                if new_qty <= 0: QMessageBox.warning(self.parent(), "Invalid Quantity", "Quantity must be greater than zero."); return False
                item.quantity = new_qty
            elif col == self.COLUMN_UNIT_COST:
                new_cost = Decimal(v)
                if new_cost < 0: QMessageBox.warning(self.parent(), "Invalid Cost", "Unit cost cannot be negative."); return False
                item.unit_cost = new_cost
            else: return False
            self.dataChanged.emit(self.createIndex(i.row(), 0), self.createIndex(i.row(), self.columnCount() - 1))
            self.total_cost_changed.emit()
            return True
        except: QMessageBox.warning(self.parent(), "Invalid Input", "Please enter a valid number."); return False
    def flags(self, i):
        flags = super().flags(i)
        if i.column() in [self.COLUMN_QTY, self.COLUMN_UNIT_COST]: flags |= Qt.ItemIsEditable
        return flags
    def add_item(self, item: POLineItem):
        if any(i.product.id == item.product.id for i in self._items):
            QMessageBox.information(self.parent(), "Duplicate Item", f"Product '{item.product.name}' is already in the PO list.")
            return
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount()); self._items.append(item); self.endInsertRows()
        self.total_cost_changed.emit()
    def remove_item_at_row(self, r):
        if 0 <= r < len(self._items): self.beginRemoveRows(QModelIndex(), r, r); del self._items[r]; self.endRemoveRows(); self.total_cost_changed.emit()
    def get_total_cost(self): return sum(item.total_cost for item in self._items).quantize(Decimal("0.01"))
    def get_po_items_dto(self): return [item.to_create_dto() for item in self._items]
    def has_items(self): return bool(self._items)

class PurchaseOrderDialog(QDialog):
    """A dialog for creating a new Purchase Order."""
    po_operation_completed = Signal()

    def __init__(self, core: ApplicationCore, outlet_id: uuid.UUID, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.core = core
        self.async_worker: AsyncWorker = core.async_worker
        self.company_id = self.core.current_company_id
        self.outlet_id = outlet_id
        self.setWindowTitle("Create New Purchase Order"); self.setMinimumSize(900, 700)
        self._setup_ui(); self._connect_signals(); self._load_initial_data()

    def _setup_ui(self):
        self.supplier_combo = QComboBox(); self.expected_delivery_date_edit = QDateEdit(QDate.currentDate().addDays(7)); self.expected_delivery_date_edit.setCalendarPopup(True)
        po_form_layout = QFormLayout(); po_form_layout.addRow("Supplier:", self.supplier_combo); po_form_layout.addRow("Expected Delivery:", self.expected_delivery_date_edit)
        self.product_search_input = QLineEdit(); self.product_search_input.setPlaceholderText("Enter Product SKU to add...")
        self.add_product_button = QPushButton("Add Item"); product_search_layout = QHBoxLayout()
        product_search_layout.addWidget(self.product_search_input, 1); product_search_layout.addWidget(self.add_product_button)
        self.po_table = QTableView(); self.table_model = PurchaseOrderTableModel(self); self.po_table.setModel(self.table_model)
        self.po_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch); self.po_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.total_cost_label = QLabel("<b>Total PO Cost: S$0.00</b>"); self.total_cost_label.setStyleSheet("font-size: 18px;")
        self.button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel); self.button_box.button(QDialogButtonBox.Save).setText("Create Purchase Order")
        main_layout = QVBoxLayout(self); main_layout.addLayout(po_form_layout); main_layout.addLayout(product_search_layout)
        main_layout.addWidget(self.po_table, 1); main_layout.addWidget(self.total_cost_label, alignment=Qt.AlignRight); main_layout.addWidget(self.button_box)

    def _connect_signals(self):
        self.add_product_button.clicked.connect(self._on_add_product_to_po); self.product_search_input.returnPressed.connect(self._on_add_product_to_po)
        self.button_box.accepted.connect(self._on_submit_po); self.button_box.rejected.connect(self.reject)
        self.table_model.total_cost_changed.connect(self._update_total_cost_label)
        self.supplier_combo.currentIndexChanged.connect(self._on_form_data_changed)
        self.table_model.data_changed_signal.connect(self._on_form_data_changed)
        self.po_table.customContextMenuRequested.connect(self._on_table_context_menu)

    @Slot()
    def _on_form_data_changed(self): self.button_box.button(QDialogButtonBox.Save).setEnabled(self.supplier_combo.currentData() is not None and self.table_model.has_items())
    @Slot()
    def _update_total_cost_label(self): self.total_cost_label.setText(f"<b>Total PO Cost: S${self.table_model.get_total_cost():.2f}</b>"); self._on_form_data_changed()

    def _load_initial_data(self):
        def _on_done(r, e):
            if e or isinstance(r, Failure): QMessageBox.critical(self, "Load Error", f"Failed to load suppliers: {e or r.error}"); return
            if isinstance(r, Success):
                self.supplier_combo.clear(); self.supplier_combo.addItem("-- Select Supplier --", userData=None)
                for supplier in r.value: self.supplier_combo.addItem(supplier.name, userData=supplier.id)
        self.async_worker.run_task(self.core.inventory_manager.get_all_suppliers(self.company_id), _on_done)

    @Slot()
    def _on_add_product_to_po(self):
        search_term = self.product_search_input.text().strip()
        if not search_term: return
        def _on_done(r, e):
            if e or isinstance(r, Failure): QMessageBox.warning(self, "Product Lookup Failed", f"Could not find product: {e or r.error}"); return
            if isinstance(r, Success) and r.value: self.table_model.add_item(POLineItem(r.value[0])); self.product_search_input.clear()
            else: QMessageBox.warning(self, "Not Found", f"No product found for '{search_term}'.")
        self.async_worker.run_task(self.core.product_manager.search_products(self.company_id, search_term, limit=1), _on_done)

    @Slot()
    def _on_submit_po(self):
        supplier_id = self.supplier_combo.currentData()
        if not supplier_id or not self.table_model.has_items(): self._on_form_data_changed(); return
        po_dto = PurchaseOrderCreateDTO(
            company_id=self.company_id, outlet_id=self.outlet_id, supplier_id=supplier_id,
            expected_delivery_date=datetime.combine(self.expected_delivery_date_edit.date().toPython(), datetime.min.time()),
            items=self.table_model.get_po_items_dto()
        )
        self.button_box.button(QDialogButtonBox.Save).setEnabled(False)
        def _on_done(r, e):
            self.button_box.button(QDialogButtonBox.Save).setEnabled(True)
            if e or isinstance(r, Failure): QMessageBox.critical(self, "Creation Failed", f"Could not create Purchase Order: {e or r.error}")
            elif isinstance(r, Success):
                QMessageBox.information(self, "Success", f"Purchase Order '{r.value.po_number}' created successfully!"); self.po_operation_completed.emit(); self.accept()
        self.async_worker.run_task(self.core.inventory_manager.create_purchase_order(po_dto), _on_done)

    @Slot(QPoint)
    def _on_table_context_menu(self, pos):
        index = self.po_table.indexAt(pos)
        if not index.isValid(): return
        menu = QMenu(self)
        remove_action = menu.addAction("Remove Item")
        if menu.exec(self.po_table.mapToGlobal(pos)) == remove_action:
            self.table_model.remove_item_at_row(index.row())

```

# app/ui/dialogs/payment_dialog.py
```py
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
from app.models.sales import PaymentMethod # For type hinting

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
        self.setMinimumSize(500, 400)

        self._setup_ui()
        self._connect_signals()
        self._load_payment_methods() # Load methods asynchronously

    def _setup_ui(self):
        """Build the user interface."""
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

        payment_entry_layout = QHBoxLayout()
        self.method_combo = QComboBox()
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setRange(0, 9999999.99)
        self.amount_input.setDecimals(2)
        self.add_payment_button = QPushButton("Add Payment")
        
        payment_entry_layout.addWidget(self.method_combo, 1)
        payment_entry_layout.addWidget(self.amount_input)
        payment_entry_layout.addWidget(self.add_payment_button)

        self.payments_table = QTableWidget(0, 3) # Rows, Cols
        self.payments_table.setHorizontalHeaderLabels(["Method", "Amount", "Action"])
        self.payments_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.payments_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.button(QDialogButtonBox.Ok).setText("Finalize Sale")
        self.button_box.button(QDialogButtonBox.Ok).setEnabled(False)

        main_layout = QVBoxLayout(self)
        main_layout.addLayout(summary_layout)
        main_layout.addStretch(1)
        main_layout.addLayout(payment_entry_layout)
        main_layout.addWidget(self.payments_table, 2)
        main_layout.addWidget(self.button_box)

        self._update_summary_labels()

    def _connect_signals(self):
        self.add_payment_button.clicked.connect(self._on_add_payment_clicked)
        self.button_box.accepted.connect(self._on_finalize_sale_clicked)
        self.button_box.rejected.connect(self.reject)

    def _load_payment_methods(self):
        def _on_done(result: Any, error: Optional[Exception]):
            if error:
                QMessageBox.critical(self, "Load Error", f"Failed to load payment methods: {error}")
                self.add_payment_button.setEnabled(False)
            elif isinstance(result, Success):
                self.available_payment_methods = result.value
                self.method_combo.clear()
                for method in self.available_payment_methods:
                    self.method_combo.addItem(method.name, userData=method.id)
                
                if self.method_combo.count() > 0:
                    self.amount_input.setValue(float(self.total_due))
                else:
                    QMessageBox.warning(self, "No Payment Methods", "No active payment methods found.")
                    self.add_payment_button.setEnabled(False)
            elif isinstance(result, Failure):
                QMessageBox.warning(self, "Load Failed", f"Could not load payment methods: {result.error}")
                self.add_payment_button.setEnabled(False)

        coro = self.core.payment_method_service.get_all_active_methods(self.core.current_company_id)
        self.core.async_worker.run_task(coro, on_done_callback=_on_done)

    @Slot()
    def _update_summary_labels(self):
        total_paid = sum(p.amount for p in self.current_payments).quantize(Decimal("0.01"))
        balance = (self.total_due - total_paid).quantize(Decimal("0.01"))

        self.total_paid_label.setText(f"Amount Paid: S${total_paid:.2f}")
        self.balance_label.setText(f"Balance: S${balance:.2f}")
        
        if balance <= 0:
            self.balance_label.setStyleSheet("font-size: 18px; font-weight: bold; color: green;")
            self.button_box.button(QDialogButtonBox.Ok).setEnabled(True)
        else:
            self.balance_label.setStyleSheet("font-size: 18px; font-weight: bold; color: red;")
            self.button_box.button(QDialogButtonBox.Ok).setEnabled(False)

    @Slot()
    def _on_add_payment_clicked(self):
        selected_method_id = self.method_combo.currentData()
        selected_method_name = self.method_combo.currentText()
        amount = Decimal(str(self.amount_input.value()))

        if not selected_method_id or amount <= 0:
            QMessageBox.warning(self, "Invalid Input", "Please select a payment method and enter a valid amount.")
            return

        payment_entry = PaymentEntry(selected_method_id, selected_method_name, amount)
        self.current_payments.append(payment_entry)
        
        row_idx = self.payments_table.rowCount()
        self.payments_table.insertRow(row_idx)
        self.payments_table.setItem(row_idx, 0, QTableWidgetItem(selected_method_name))
        self.payments_table.setItem(row_idx, 1, QTableWidgetItem(f"S${amount:.2f}"))

        remove_button = QPushButton("Remove")
        remove_button.clicked.connect(lambda _, r=row_idx: self._on_remove_payment_clicked(r))
        self.payments_table.setCellWidget(row_idx, 2, remove_button)

        self._update_summary_labels()
        remaining_balance = self.total_due - sum(p.amount for p in self.current_payments)
        self.amount_input.setValue(float(max(0, remaining_balance)))

    @Slot(int)
    def _on_remove_payment_clicked(self, row_idx: int):
        self.payments_table.removeRow(row_idx)
        del self.current_payments[row_idx]
        self._update_summary_labels()
        remaining_balance = self.total_due - sum(p.amount for p in self.current_payments)
        self.amount_input.setValue(float(max(0, remaining_balance)))

    @Slot()
    def _on_finalize_sale_clicked(self):
        if sum(p.amount for p in self.current_payments) < self.total_due:
            QMessageBox.warning(self, "Insufficient Payment", "Amount paid is less than total due.")
            return
        self.accept()

    def get_payment_info(self) -> List[PaymentInfoDTO]:
        return [p.to_payment_info_dto() for p in self.current_payments]

```

# app/ui/dialogs/user_dialog.py
```py
# File: app/ui/dialogs/user_dialog.py
"""A QDialog for creating and editing User entities."""
from __future__ import annotations
from typing import Optional, Any, Union, List
import uuid

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit,
    QCheckBox, QDialogButtonBox, QMessageBox, QComboBox, QListView
)
from PySide6.QtCore import Slot, Signal, QObject
from PySide6.QtGui import QStandardItemModel, QStandardItem

from app.business_logic.dto.user_dto import UserCreateDTO, UserUpdateDTO, UserDTO, RoleDTO
from app.core.application_core import ApplicationCore
from app.core.result import Success, Failure
from app.core.async_bridge import AsyncWorker

class UserDialog(QDialog):
    """A dialog for creating or editing a user and assigning roles."""
    user_operation_completed = Signal(bool, str)

    def __init__(self, core: ApplicationCore, user: Optional[UserDTO] = None, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.core = core
        self.async_worker: AsyncWorker = core.async_worker
        self.user = user
        self.is_edit_mode = user is not None
        self.available_roles: List[RoleDTO] = []

        self.setWindowTitle("Edit User" if self.is_edit_mode else "Add New User")
        self.setMinimumWidth(450)

        self._setup_ui()
        self._connect_signals()
        self._load_roles() # Asynchronously load available roles
        
        if self.is_edit_mode:
            self._populate_form()

    def _setup_ui(self):
        """Initializes the UI widgets and layout."""
        self.username_input = QLineEdit()
        self.fullname_input = QLineEdit()
        self.email_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        if self.is_edit_mode:
            self.password_input.setPlaceholderText("Leave blank to keep current password")
        
        # Using a QListView with checkboxes for multi-role selection
        self.roles_view = QListView()
        self.roles_model = QStandardItemModel()
        self.roles_view.setModel(self.roles_model)

        self.is_active_checkbox = QCheckBox("Is Active")

        form_layout = QFormLayout()
        form_layout.addRow("Username:", self.username_input)
        form_layout.addRow("Full Name:", self.fullname_input)
        form_layout.addRow("Email:", self.email_input)
        form_layout.addRow("Password:", self.password_input)
        form_layout.addRow("Roles:", self.roles_view)
        form_layout.addRow(self.is_active_checkbox)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        self.button_box.button(QDialogButtonBox.Save).setText("Save User")
        
        main_layout = QVBoxLayout(self)
        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.button_box)

        if not self.is_edit_mode: self.is_active_checkbox.setChecked(True)

    def _connect_signals(self):
        self.button_box.accepted.connect(self._on_save_accepted)
        self.button_box.rejected.connect(self.reject)

    def _load_roles(self):
        """Loads available roles and populates the roles view."""
        def _on_done(result: Any, error: Optional[Exception]):
            if error or isinstance(result, Failure):
                QMessageBox.critical(self, "Error", f"Failed to load roles: {error or result.error}")
                return
            
            self.available_roles = result.value
            self.roles_model.clear()
            for role in self.available_roles:
                item = QStandardItem(role.name)
                item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                item.setData(role.id, Qt.UserRole)
                item.setCheckState(Qt.Unchecked)
                self.roles_model.appendRow(item)
            
            # If in edit mode, check the roles the user already has
            if self.is_edit_mode and self.user:
                user_role_ids = {role.id for role in self.user.roles}
                for i in range(self.roles_model.rowCount()):
                    item = self.roles_model.item(i)
                    role_id = item.data(Qt.UserRole)
                    if role_id in user_role_ids:
                        item.setCheckState(Qt.Checked)

        self.async_worker.run_task(self.core.user_manager.get_all_roles(self.core.current_company_id), _on_done)

    def _populate_form(self):
        if self.user:
            self.username_input.setText(self.user.username)
            self.fullname_input.setText(self.user.full_name or "")
            self.email_input.setText(self.user.email)
            self.is_active_checkbox.setChecked(self.user.is_active)
    
    def _get_selected_role_ids(self) -> List[uuid.UUID]:
        """Gets the UUIDs of the checked roles."""
        selected_ids = []
        for i in range(self.roles_model.rowCount()):
            item = self.roles_model.item(i)
            if item.checkState() == Qt.Checked:
                selected_ids.append(item.data(Qt.UserRole))
        return selected_ids

    def _get_dto(self) -> Union[UserCreateDTO, UserUpdateDTO, None]:
        password = self.password_input.text().strip()
        if not self.is_edit_mode and not password:
            QMessageBox.warning(self, "Validation Error", "Password is required for a new user.")
            return None

        try:
            common_data = {
                "username": self.username_input.text().strip(),
                "full_name": self.fullname_input.text().strip() or None,
                "email": self.email_input.text().strip(),
                "is_active": self.is_active_checkbox.isChecked(),
                "roles": self._get_selected_role_ids()
            }
            if self.is_edit_mode:
                return UserUpdateDTO(password=password or None, **common_data)
            else:
                return UserCreateDTO(password=password, **common_data)
        except Exception as e:
            QMessageBox.warning(self, "Invalid Input", f"Please check your inputs: {e}")
            return None

    @Slot()
    def _on_save_accepted(self):
        dto = self._get_dto()
        if not dto: return

        if self.is_edit_mode:
            coro = self.core.user_manager.update_user(self.user.id, dto)
        else:
            coro = self.core.user_manager.create_user(self.core.current_company_id, dto)

        self.button_box.button(QDialogButtonBox.Save).setEnabled(False)
        def _on_done(result: Any, error: Optional[Exception]):
            self.button_box.button(QDialogButtonBox.Save).setEnabled(True)
            if error or isinstance(result, Failure):
                QMessageBox.critical(self, "Error", f"Operation failed: {error or result.error}")
                self.user_operation_completed.emit(False, str(error or result.error))
            else:
                QMessageBox.information(self, "Success", "User saved successfully.")
                self.user_operation_completed.emit(True, "Success")
                self.accept()

        self.async_worker.run_task(coro, _on_done)

```

# app/ui/resources/styles.qss
```qss

```

# app/ui/resources/__init__.py
```py

```

# app/ui/resources/icons/__init__.py
```py

```

# app/ui/views/pos_view.py
```py
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
from app.business_logic.dto.sales_dto import SaleCreateDTO, FinalizedSaleDTO
from app.business_logic.dto.product_dto import ProductDTO
from app.business_logic.dto.customer_dto import CustomerDTO
from app.ui.dialogs.payment_dialog import PaymentDialog
from app.core.async_bridge import AsyncWorker

class CartItemDisplay(QObject):
    """Helper class to hold and represent cart item data for the TableModel."""
    def __init__(self, product: ProductDTO, quantity: Decimal, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.product = product
        self.quantity = quantity
        self.recalculate()

    def recalculate(self):
        self.line_subtotal = (self.quantity * self.product.selling_price).quantize(Decimal("0.01"))
        self.line_tax = (self.line_subtotal * (self.product.gst_rate / Decimal("100.0"))).quantize(Decimal("0.01"))
        self.line_total = (self.line_subtotal + self.line_tax).quantize(Decimal("0.01"))

    def to_cart_item_dto(self) -> Dict[str, Any]:
        return {
            "product_id": self.product.id,
            "quantity": self.quantity,
            "unit_price_override": self.product.selling_price,
            "variant_id": None, # TODO: Handle variants
            "sku": self.product.sku,
            "product": self.product
        }

class CartTableModel(QAbstractTableModel):
    """A Qt Table Model for displaying items in the sales cart."""
    HEADERS = ["SKU", "Name", "Qty", "Unit Price", "Line Total"]
    COLUMN_QTY = 2
    cart_changed = Signal()

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._items: List[CartItemDisplay] = []

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int: return len(self._items)
    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int: return len(self.HEADERS)
    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole) -> Any:
        if role == Qt.DisplayRole and orientation == Qt.Orientation.Horizontal: return self.HEADERS[section]
        return None
    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        if not index.isValid(): return None
        item = self._items[index.row()]
        col = index.column()
        if role == Qt.DisplayRole:
            if col == 0: return item.product.sku
            if col == 1: return item.product.name
            if col == 2: return str(item.quantity)
            if col == 3: return f"S${item.product.selling_price:.2f}"
            if col == 4: return f"S${item.line_total:.2f}"
        if role == Qt.EditRole and col == self.COLUMN_QTY: return str(item.quantity)
        if role == Qt.TextAlignmentRole and col in [2, 3, 4]: return Qt.AlignRight | Qt.AlignVCenter
        return None
    def setData(self, index: QModelIndex, value: Any, role: int = Qt.EditRole) -> bool:
        if role == Qt.EditRole and index.column() == self.COLUMN_QTY:
            try:
                new_qty = Decimal(value)
                if new_qty <= 0:
                    self.remove_item_at_row(index.row())
                    return True
                self._items[index.row()].quantity = new_qty
                self._items[index.row()].recalculate()
                self.dataChanged.emit(index, self.createIndex(index.row(), self.columnCount() - 1))
                self.cart_changed.emit()
                return True
            except: return False
        return False
    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        flags = super().flags(index)
        if index.column() == self.COLUMN_QTY: flags |= Qt.ItemFlag.ItemIsEditable
        return flags
    def add_item(self, product_dto: ProductDTO, quantity: Decimal = Decimal("1")):
        for item_display in self._items:
            if item_display.product.id == product_dto.id:
                item_display.quantity += quantity
                item_display.recalculate()
                idx = self._items.index(item_display)
                self.dataChanged.emit(self.createIndex(idx, 0), self.createIndex(idx, self.columnCount() - 1))
                self.cart_changed.emit()
                return
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        self._items.append(CartItemDisplay(product_dto, quantity))
        self.endInsertRows()
        self.cart_changed.emit()
    def clear_cart(self):
        self.beginResetModel(); self._items.clear(); self.endResetModel(); self.cart_changed.emit()
    def get_cart_summary(self) -> Tuple[Decimal, Decimal, Decimal]:
        # FIX: Provide a Decimal start value to sum() to prevent errors on empty carts
        subtotal = sum((item.line_subtotal for item in self._items), Decimal('0.0')).quantize(Decimal("0.01"))
        tax_amount = sum((item.line_tax for item in self._items), Decimal('0.0')).quantize(Decimal("0.01"))
        total_amount = sum((item.line_total for item in self._items), Decimal('0.0')).quantize(Decimal("0.01"))
        return subtotal, tax_amount, total_amount
    def get_cart_items(self) -> List[Dict[str, Any]]: return [item.to_cart_item_dto() for item in self._items]

class POSView(QWidget):
    # ... (Rest of POSView is identical and correct)
    def __init__(self, core: ApplicationCore, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.core = core
        self.async_worker: AsyncWorker = core.async_worker
        self.selected_customer_id: Optional[uuid.UUID] = None
        self._setup_ui()
        self._connect_signals()
        self._reset_sale_clicked()

    def _setup_ui(self):
        left_panel = QWidget(); left_layout = QVBoxLayout(left_panel)
        self.cart_table = QTableView(); self.cart_model = CartTableModel()
        self.cart_table.setModel(self.cart_model); self.cart_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.cart_table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows); self.cart_table.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self.cart_table.setEditTriggers(QTableView.EditTrigger.DoubleClicked | QTableView.EditTrigger.AnyKeyPressed)
        self.subtotal_label = QLabel("Subtotal: S$0.00"); self.tax_label = QLabel("GST (9.00%): S$0.00") # FIX: GST Rate Update
        self.total_label = QLabel("Total: S$0.00"); self.total_label.setStyleSheet("font-size: 28px; font-weight: bold; color: #333;")
        totals_form_layout = QFormLayout(); totals_form_layout.addRow(self.subtotal_label); totals_form_layout.addRow(self.tax_label); totals_form_layout.addRow(self.total_label)
        left_layout.addWidget(QLabel("Current Sale Items")); left_layout.addWidget(self.cart_table, 1); left_layout.addLayout(totals_form_layout)
        right_panel = QWidget(); right_layout = QVBoxLayout(right_panel)
        product_search_form = QFormLayout(); self.product_search_input = QLineEdit(); self.product_search_input.setPlaceholderText("Scan barcode or enter SKU/name...")
        self.add_item_button = QPushButton("Add to Cart"); product_search_form.addRow("Product:", self.product_search_input); right_layout.addLayout(product_search_form); right_layout.addWidget(self.add_item_button)
        customer_form = QFormLayout(); self.customer_search_input = QLineEdit(); self.customer_search_input.setPlaceholderText("Search customer by code/name...")
        self.select_customer_button = QPushButton("Select Customer"); self.clear_customer_button = QPushButton("Clear")
        self.selected_customer_label = QLabel("Customer: N/A"); customer_actions_layout = QHBoxLayout(); customer_actions_layout.addWidget(self.select_customer_button); customer_actions_layout.addWidget(self.clear_customer_button)
        customer_form.addRow(self.selected_customer_label); customer_form.addRow(self.customer_search_input); customer_form.addRow(customer_actions_layout); right_layout.addLayout(customer_form)
        right_layout.addStretch()
        self.new_sale_button = QPushButton("New Sale"); self.void_sale_button = QPushButton("Void Sale"); self.pay_button = QPushButton("PAY")
        self.pay_button.setStyleSheet("background-color: #4CAF50; color: white; font-size: 28px; padding: 20px;")
        right_layout.addWidget(self.new_sale_button); right_layout.addWidget(self.void_sale_button); right_layout.addWidget(self.pay_button)
        main_layout = QHBoxLayout(self); main_layout.addWidget(left_panel, 2); main_layout.addWidget(right_panel, 1)

    def _connect_signals(self):
        self.add_item_button.clicked.connect(self._on_add_item_clicked); self.product_search_input.returnPressed.connect(self._on_add_item_clicked)
        self.pay_button.clicked.connect(self._on_pay_clicked); self.new_sale_button.clicked.connect(self._reset_sale_clicked)
        self.void_sale_button.clicked.connect(self._void_sale_clicked); self.cart_model.cart_changed.connect(self._update_totals)
        self.select_customer_button.clicked.connect(self._on_select_customer_clicked); self.clear_customer_button.clicked.connect(self._clear_customer_selection)

    @Slot()
    def _update_totals(self):
        subtotal, tax_amount, total_amount = self.cart_model.get_cart_summary()
        self.subtotal_label.setText(f"Subtotal: S${subtotal:.2f}"); self.tax_label.setText(f"GST: S${tax_amount:.2f}")
        self.total_label.setText(f"Total: S${total_amount:.2f}")

    @Slot()
    def _on_add_item_clicked(self):
        search_term = self.product_search_input.text().strip();
        if not search_term: return
        def _on_done(result: Any, error: Optional[Exception]):
            if error or isinstance(result, Failure):
                QMessageBox.warning(self, "Product Lookup Failed", f"Could not find product: {error or result.error}")
            elif isinstance(result, Success):
                products = result.value
                if not products: QMessageBox.warning(self, "Not Found", f"No product found for '{search_term}'."); return
                self.cart_model.add_item(products[0]); self.product_search_input.clear(); self.product_search_input.setFocus()
        coro = self.core.product_manager.search_products(self.core.current_company_id, search_term, limit=1)
        self.async_worker.run_task(coro, on_done_callback=_on_done)

    @Slot()
    def _on_pay_clicked(self):
        if not self.cart_model.rowCount(): QMessageBox.warning(self, "Empty Cart", "Cannot process payment for an empty cart."); return
        _, _, total_amount = self.cart_model.get_cart_summary()
        payment_dialog = PaymentDialog(self.core, total_amount, parent=self)
        if payment_dialog.exec():
            payment_info_dtos = payment_dialog.get_payment_info()
            if not payment_info_dtos: QMessageBox.critical(self, "Payment Error", "No payment information received."); return
            sale_create_dto = SaleCreateDTO(
                company_id=self.core.current_company_id, outlet_id=self.core.current_outlet_id,
                cashier_id=self.core.current_user_id, customer_id=self.selected_customer_id,
                cart_items=self.cart_model.get_cart_items(), payments=payment_info_dtos
            )
            def _on_done(result: Any, error: Optional[Exception]):
                self.pay_button.setEnabled(True)
                if error or isinstance(result, Failure):
                    QMessageBox.warning(self, "Sale Failed", f"Could not finalize sale: {error or result.error}")
                elif isinstance(result, Success):
                    finalized_dto: FinalizedSaleDTO = result.value
                    QMessageBox.information(self, "Sale Completed", f"Transaction {finalized_dto.transaction_number} completed!\nTotal: S${finalized_dto.total_amount:.2f}\nChange Due: S${finalized_dto.change_due:.2f}")
                    self._reset_sale_clicked()
            self.pay_button.setEnabled(False)
            self.async_worker.run_task(self.core.sales_manager.finalize_sale(sale_create_dto), on_done_callback=_on_done)
        else:
            QMessageBox.information(self, "Payment Cancelled", "Payment process cancelled.")

    @Slot()
    def _reset_sale_clicked(self):
        self.cart_model.clear_cart(); self.product_search_input.clear(); self._clear_customer_selection(); self.product_search_input.setFocus()

    @Slot()
    def _void_sale_clicked(self):
        if self.cart_model.rowCount() == 0: QMessageBox.information(self, "No Sale", "There is no active sale to void."); return
        if QMessageBox.question(self, "Confirm Void", "Are you sure you want to void the current sale?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            self._reset_sale_clicked(); QMessageBox.information(self, "Sale Voided", "Current sale has been voided.")

    @Slot()
    def _on_select_customer_clicked(self):
        search_term = self.customer_search_input.text().strip()
        if not search_term: return
        def _on_done(result: Any, error: Optional[Exception]):
            if error or isinstance(result, Failure): QMessageBox.warning(self, "Customer Lookup Failed", f"Could not find customer: {error or result.error}"); return
            if isinstance(result, Success) and result.value:
                customer = result.value[0]
                self.selected_customer_id = customer.id; self.selected_customer_label.setText(f"Customer: {customer.name}"); self.customer_search_input.clear()
            else: QMessageBox.warning(self, "Not Found", f"No customer found for '{search_term}'.")
        self.async_worker.run_task(self.core.customer_manager.search_customers(self.core.current_company_id, search_term, limit=1), on_done_callback=_on_done)

    @Slot()
    def _clear_customer_selection(self):
        self.selected_customer_id = None; self.selected_customer_label.setText("Customer: N/A"); self.customer_search_input.clear()

```

# app/ui/views/__init__.py
```py

```

# app/ui/views/customer_view.py
```py
# File: app/ui/views/customer_view.py
"""The main view for managing customers."""
import uuid
from typing import List, Any, Optional

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableView,
    QMessageBox, QLineEdit, QHeaderView, QSizePolicy
)
from PySide6.QtCore import Slot, Signal, QAbstractTableModel, QModelIndex, Qt, QObject

from app.core.application_core import ApplicationCore
from app.core.result import Success, Failure
from app.business_logic.dto.customer_dto import CustomerDTO
from app.ui.dialogs.customer_dialog import CustomerDialog
from app.core.async_bridge import AsyncWorker

class CustomerTableModel(QAbstractTableModel):
    """A Qt Table Model for displaying CustomerDTOs."""
    
    HEADERS = ["Code", "Name", "Email", "Phone", "Loyalty Points", "Credit Limit", "Active"]

    def __init__(self, customers: List[CustomerDTO], parent: Optional[QObject] = None):
        super().__init__(parent)
        self._customers = customers

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._customers)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self.HEADERS)

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return self.HEADERS[section]
        return None

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if not index.isValid():
            return None
        
        customer = self._customers[index.row()]
        col = index.column()

        if role == Qt.ItemDataRole.DisplayRole:
            if col == 0: return customer.customer_code
            if col == 1: return customer.name
            if col == 2: return customer.email or "N/A"
            if col == 3: return customer.phone or "N/A"
            if col == 4: return str(customer.loyalty_points)
            if col == 5: return f"S${customer.credit_limit:.2f}"
            if col == 6: return "Yes" if customer.is_active else "No"
        
        if role == Qt.ItemDataRole.TextAlignmentRole:
            if col in [4, 5]: # Loyalty points, credit limit
                return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            if col == 6: # Active
                return Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter
        
        return None

    def get_customer_at_row(self, row: int) -> Optional[CustomerDTO]:
        """Returns the CustomerDTO at the given row index."""
        if 0 <= row < len(self._customers):
            return self._customers[row]
        return None

    def refresh_data(self, new_customers: List[CustomerDTO]):
        """Updates the model with new data and notifies views."""
        self.beginResetModel()
        self._customers = new_customers
        self.endResetModel()

class CustomerView(QWidget):
    """A view widget to display and manage the customer list."""
    
    def __init__(self, core: ApplicationCore, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.core = core
        self.async_worker: AsyncWorker = core.async_worker

        self._setup_ui()
        self._connect_signals()
        self._load_customers()

    def _setup_ui(self):
        """Initializes the UI widgets and layout."""
        # --- Search and Action Buttons ---
        top_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search customers by code, name, email, or phone...")
        self.add_button = QPushButton("Add New Customer")
        self.edit_button = QPushButton("Edit Selected")
        self.delete_button = QPushButton("Deactivate Selected") # Soft delete

        top_layout.addWidget(self.search_input, 1)
        top_layout.addStretch()
        top_layout.addWidget(self.add_button)
        top_layout.addWidget(self.edit_button)
        top_layout.addWidget(self.delete_button)
        
        # --- Customer Table ---
        self.table_view = QTableView()
        self.customer_model = CustomerTableModel([])
        self.table_view.setModel(self.customer_model)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_view.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.table_view.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self.table_view.setSortingEnabled(True)

        # --- Main Layout ---
        main_layout = QVBoxLayout(self)
        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.table_view)

        self.setLayout(main_layout)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)


    def _connect_signals(self):
        """Connects UI signals to slots."""
        self.add_button.clicked.connect(self._on_add_customer)
        self.edit_button.clicked.connect(self._on_edit_customer)
        self.delete_button.clicked.connect(self._on_deactivate_customer)
        self.search_input.textChanged.connect(self._on_search_customers)
        self.table_view.doubleClicked.connect(self._on_edit_customer)

    def _get_selected_customer(self) -> Optional[CustomerDTO]:
        """Helper to get the currently selected customer from the table."""
        selected_indexes = self.table_view.selectionModel().selectedRows()
        if selected_indexes:
            row = selected_indexes[0].row()
            return self.customer_model.get_customer_at_row(row)
        return None

    @Slot()
    def _load_customers(self, search_term: str = ""):
        """Loads customer data asynchronously into the table model."""
        company_id = self.core.current_company_id

        def _on_done(result: Any, error: Optional[Exception]):
            if error:
                QMessageBox.critical(self, "Load Error", f"Failed to load customers: {error}")
            elif isinstance(result, Success):
                self.customer_model.refresh_data(result.value)
            elif isinstance(result, Failure):
                QMessageBox.warning(self, "Load Failed", f"Could not load customers: {result.error}")
        
        if search_term:
            coro = self.core.customer_manager.search_customers(company_id, search_term)
        else:
            coro = self.core.customer_manager.get_all_customers(company_id)
        
        self.async_worker.run_task(coro, on_done_callback=_on_done)

    @Slot()
    def _on_add_customer(self):
        """Opens the dialog to add a new customer."""
        dialog = CustomerDialog(self.core, parent=self)
        dialog.customer_operation_completed.connect(self._handle_customer_dialog_result)
        dialog.exec()

    @Slot()
    def _on_edit_customer(self):
        """Opens the dialog to edit the selected customer."""
        selected_customer = self._get_selected_customer()
        if not selected_customer:
            QMessageBox.information(self, "No Selection", "Please select a customer to edit.")
            return

        dialog = CustomerDialog(self.core, customer=selected_customer, parent=self)
        dialog.customer_operation_completed.connect(self._handle_customer_dialog_result)
        dialog.exec()

    @Slot()
    def _on_deactivate_customer(self):
        """Deactivates the selected customer."""
        selected_customer = self._get_selected_customer()
        if not selected_customer:
            QMessageBox.information(self, "No Selection", "Please select a customer to deactivate.")
            return
        
        reply = QMessageBox.question(self, "Confirm Deactivation",
                                    f"Are you sure you want to deactivate customer '{selected_customer.name}' (Code: {selected_customer.customer_code})?",
                                    QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.No:
            return

        def _on_done(result: Any, error: Optional[Exception]):
            if error:
                QMessageBox.critical(self, "Error", f"Failed to deactivate customer: {error}")
            elif isinstance(result, Success) and result.value:
                QMessageBox.information(self, "Success", f"Customer '{selected_customer.name}' deactivated.")
                self._load_customers()
            elif isinstance(result, Failure):
                QMessageBox.warning(self, "Deactivation Failed", f"Could not deactivate customer: {result.error}")
            else:
                QMessageBox.warning(self, "Deactivation Failed", "Customer not found or unknown error.")
        
        coro = self.core.customer_manager.deactivate_customer(selected_customer.id)
        self.async_worker.run_task(coro, on_done_callback=_on_done)

    @Slot(str)
    def _on_search_customers(self, text: str):
        """Triggers customer search based on input text."""
        self._load_customers(search_term=text)

    @Slot(bool, str)
    def _handle_customer_dialog_result(self, success: bool, message: str):
        """Slot to handle results from CustomerDialog and refresh the view."""
        if success:
            self._load_customers(search_term=self.search_input.text())

```

# app/ui/views/inventory_view.py
```py
# File: app/ui/views/inventory_view.py
"""Main View for Inventory Management."""
from __future__ import annotations
from typing import List, Any, Optional
import uuid

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableView, QLabel, QLineEdit, QHeaderView, QSizePolicy, QMessageBox,
    QTabWidget
)
from PySide6.QtCore import Slot, Signal, QAbstractTableModel, QModelIndex, Qt, QObject, QPoint
from PySide6.QtGui import QAction, QCursor

from app.core.application_core import ApplicationCore
from app.core.result import Success, Failure
from app.business_logic.dto.inventory_dto import InventorySummaryDTO, PurchaseOrderDTO, StockMovementDTO
from app.ui.dialogs.stock_adjustment_dialog import StockAdjustmentDialog
from app.ui.dialogs.purchase_order_dialog import PurchaseOrderDialog
from app.core.async_bridge import AsyncWorker

class InventoryTableModel(QAbstractTableModel):
    HEADERS = ["SKU", "Name", "Category", "On Hand", "Reorder Pt.", "Cost", "Selling Price", "Active"]
    def __init__(self, items: List[InventorySummaryDTO], parent: Optional[QObject] = None): super().__init__(parent); self._items = items
    def rowCount(self, p=QModelIndex()): return len(self._items)
    def columnCount(self, p=QModelIndex()): return len(self.HEADERS)
    def headerData(self, s, o, r=Qt.DisplayRole):
        if r == Qt.DisplayRole and o == Qt.Horizontal: return self.HEADERS[s]
    def data(self, i, r=Qt.DisplayRole):
        if not i.isValid(): return
        item = self._items[i.row()]
        col = i.column()
        if r == Qt.DisplayRole:
            if col == 0: return item.sku
            if col == 1: return item.name
            if col == 2: return item.category_name or "N/A"
            if col == 3: return str(item.quantity_on_hand)
            if col == 4: return str(item.reorder_point)
            if col == 5: return f"S${item.cost_price:.2f}"
            if col == 6: return f"S${item.selling_price:.2f}"
            if col == 7: return "Yes" if item.is_active else "No"
        if r == Qt.TextAlignmentRole:
            if col in [3, 4, 5, 6]: return Qt.AlignRight | Qt.AlignVCenter
            if col == 7: return Qt.AlignCenter
    def get_item_at_row(self, r): return self._items[r] if 0 <= r < len(self._items) else None
    def refresh_data(self, new_items): self.beginResetModel(); self._items = new_items; self.endResetModel()

class PurchaseOrderTableModel(QAbstractTableModel):
    HEADERS = ["PO Number", "Supplier", "Order Date", "Expected", "Total (S$)", "Status"]
    def __init__(self, pos: List[PurchaseOrderDTO], parent: Optional[QObject] = None): super().__init__(parent); self._pos = pos
    def rowCount(self, p=QModelIndex()): return len(self._pos)
    def columnCount(self, p=QModelIndex()): return len(self.HEADERS)
    def headerData(self, s, o, r=Qt.DisplayRole):
        if r == Qt.DisplayRole and o == Qt.Horizontal: return self.HEADERS[s]
    def data(self, i, r=Qt.DisplayRole):
        if not i.isValid(): return
        po = self._pos[i.row()]
        col = i.column()
        if r == Qt.DisplayRole:
            if col == 0: return po.po_number
            if col == 1: return po.supplier_name
            if col == 2: return po.order_date.strftime("%Y-%m-%d")
            if col == 3: return po.expected_delivery_date.strftime("%Y-%m-%d") if po.expected_delivery_date else "N/A"
            if col == 4: return f"{po.total_amount:.2f}"
            if col == 5: return po.status.replace('_', ' ').title()
        if r == Qt.TextAlignmentRole:
            if col == 4: return Qt.AlignRight | Qt.AlignVCenter
            if col == 5: return Qt.AlignCenter
    def get_po_at_row(self, r): return self._pos[r] if 0 <= r < len(self._pos) else None
    def refresh_data(self, new_pos): self.beginResetModel(); self._pos = new_pos; self.endResetModel()

class StockMovementTableModel(QAbstractTableModel):
    HEADERS = ["Date", "Product", "SKU", "Type", "Change", "User", "Notes"]
    def __init__(self, movements: List[StockMovementDTO], parent: Optional[QObject] = None): super().__init__(parent); self._movements = movements
    def rowCount(self, p=QModelIndex()): return len(self._movements)
    def columnCount(self, p=QModelIndex()): return len(self.HEADERS)
    def headerData(self, s, o, r=Qt.DisplayRole):
        if r == Qt.DisplayRole and o == Qt.Horizontal: return self.HEADERS[s]
    def data(self, i, r=Qt.DisplayRole):
        if not i.isValid(): return
        m = self._movements[i.row()]
        col = i.column()
        if r == Qt.DisplayRole:
            if col == 0: return m.created_at.strftime("%Y-%m-%d %H:%M")
            if col == 1: return m.product_name
            if col == 2: return m.sku
            if col == 3: return m.movement_type.replace('_', ' ').title()
            if col == 4: change = m.quantity_change; return f"+{change}" if change > 0 else str(change)
            if col == 5: return m.created_by_user_name or "System"
            if col == 6: return m.notes or "N/A"
        if r == Qt.TextAlignmentRole and col == 4: return Qt.AlignRight | Qt.AlignVCenter
    def refresh_data(self, new_m): self.beginResetModel(); self._movements = new_m; self.endResetModel()

class InventoryView(QWidget):
    """A view to display stock levels and initiate inventory operations."""
    def __init__(self, core: ApplicationCore, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.core = core
        self.async_worker: AsyncWorker = core.async_worker
        self.company_id = self.core.current_company_id
        self.outlet_id = self.core.current_outlet_id
        self.user_id = self.core.current_user_id
        self._setup_ui()
        self._connect_signals()
        self._load_inventory_summary()

    def _setup_ui(self):
        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(self._create_inventory_summary_tab(), "Current Stock")
        self.tab_widget.addTab(self._create_purchase_orders_tab(), "Purchase Orders")
        self.tab_widget.addTab(self._create_stock_movements_tab(), "Stock Movements")
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.tab_widget)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def _create_inventory_summary_tab(self):
        tab = QWidget(); layout = QVBoxLayout(tab); top_layout = QHBoxLayout()
        self.inventory_search_input = QLineEdit(); self.inventory_search_input.setPlaceholderText("Search product...")
        self.adjust_stock_button = QPushButton("Adjust Stock")
        top_layout.addWidget(self.inventory_search_input, 1); top_layout.addStretch(); top_layout.addWidget(self.adjust_stock_button)
        self.inventory_table = QTableView(); self.inventory_model = InventoryTableModel([])
        self.inventory_table.setModel(self.inventory_model); self.inventory_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.inventory_table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows); self.inventory_table.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        layout.addLayout(top_layout); layout.addWidget(self.inventory_table)
        return tab

    def _create_purchase_orders_tab(self):
        tab = QWidget(); layout = QVBoxLayout(tab); top_layout = QHBoxLayout()
        self.new_po_button = QPushButton("New Purchase Order"); self.receive_po_button = QPushButton("Receive Items on PO")
        top_layout.addStretch(); top_layout.addWidget(self.new_po_button); top_layout.addWidget(self.receive_po_button)
        self.po_table = QTableView(); self.po_model = PurchaseOrderTableModel([])
        self.po_table.setModel(self.po_model); self.po_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.po_table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows); self.po_table.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        layout.addLayout(top_layout); layout.addWidget(self.po_table)
        return tab

    def _create_stock_movements_tab(self):
        tab = QWidget(); layout = QVBoxLayout(tab)
        self.movements_table = QTableView(); self.movements_model = StockMovementTableModel([])
        self.movements_table.setModel(self.movements_model); self.movements_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.movements_title_label = QLabel("Stock movement history will appear here.")
        layout.addWidget(self.movements_title_label); layout.addWidget(self.movements_table)
        return tab

    def _connect_signals(self):
        self.tab_widget.currentChanged.connect(self._on_tab_changed)
        self.inventory_search_input.textChanged.connect(self._on_inventory_search)
        self.adjust_stock_button.clicked.connect(self._on_adjust_stock)
        self.inventory_table.doubleClicked.connect(self._on_view_product_stock_history)
        self.new_po_button.clicked.connect(self._on_new_po)
        self.receive_po_button.clicked.connect(self._on_receive_po_items)

    @Slot(int)
    def _on_tab_changed(self, index):
        if index == 0: self._load_inventory_summary()
        elif index == 1: self._load_purchase_orders()
        elif index == 2: self.movements_title_label.setText("Stock movement history will appear here."); self.movements_model.refresh_data([])

    def _load_inventory_summary(self, search_term: str = ""):
        def _on_done(r, e):
            if e or isinstance(r, Failure): QMessageBox.critical(self, "Error", f"Failed to load inventory: {e or r.error}")
            elif isinstance(r, Success): self.inventory_model.refresh_data(r.value)
        self.async_worker.run_task(self.core.inventory_manager.get_inventory_summary(self.company_id, self.outlet_id, search_term=search_term), _on_done)

    @Slot(str)
    def _on_inventory_search(self, text): self._load_inventory_summary(search_term=text)

    @Slot()
    def _on_adjust_stock(self):
        dialog = StockAdjustmentDialog(self.core, self.outlet_id, self.user_id, parent=self)
        dialog.operation_completed.connect(self._load_inventory_summary)
        dialog.exec()

    @Slot(QModelIndex)
    def _on_view_product_stock_history(self, index):
        item = self.inventory_model.get_item_at_row(index.row())
        if not item: return
        self.tab_widget.setCurrentWidget(self.stock_movements_tab)
        self._load_stock_movements(product_id=item.product_id, product_sku=item.sku)

    def _load_purchase_orders(self):
        def _on_done(r, e):
            if e or isinstance(r, Failure): QMessageBox.critical(self, "Error", f"Failed to load purchase orders: {e or r.error}")
            elif isinstance(r, Success): self.po_model.refresh_data(r.value)
        self.async_worker.run_task(self.core.inventory_manager.get_all_purchase_orders(self.company_id, self.outlet_id), _on_done)

    @Slot()
    def _on_new_po(self):
        dialog = PurchaseOrderDialog(self.core, self.outlet_id, parent=self)
        dialog.po_operation_completed.connect(self._load_purchase_orders)
        dialog.exec()

    @Slot()
    def _on_receive_po_items(self):
        selected_po = self.po_model.get_po_at_row(self.po_table.currentIndex().row())
        if not selected_po: QMessageBox.information(self, "No Selection", "Please select a Purchase Order to receive items."); return
        QMessageBox.information(self, "Not Implemented", f"Functionality to receive items for PO {selected_po.po_number} is not yet implemented.")

    def _load_stock_movements(self, product_id: Optional[uuid.UUID] = None, product_sku: str = "product"):
        if not product_id: self.movements_model.refresh_data([]); return
        self.movements_title_label.setText(f"Stock Movement History for: {product_sku}")
        def _on_done(r, e):
            if e or isinstance(r, Failure): QMessageBox.critical(self, "Error", f"Failed to load stock movements: {e or r.error}")
            elif isinstance(r, Success): self.movements_model.refresh_data(r.value)
        self.async_worker.run_task(self.core.inventory_manager.get_stock_movements_for_product(self.company_id, product_id), _on_done)

```

# app/ui/views/settings_view.py
```py
# File: app/ui/views/settings_view.py
"""A view for managing application and company settings."""
from __future__ import annotations
from typing import Optional, Any, List
import uuid

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTabWidget, QFormLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox, QTableView, QHBoxLayout, QHeaderView
)
from PySide6.QtCore import Slot, Signal, QAbstractTableModel, QModelIndex, Qt, QObject

from app.core.application_core import ApplicationCore
from app.core.result import Success, Failure
from app.business_logic.dto.company_dto import CompanyDTO
from app.business_logic.dto.user_dto import UserDTO, UserCreateDTO, UserUpdateDTO, RoleDTO
from app.core.async_bridge import AsyncWorker
from app.ui.dialogs.user_dialog import UserDialog # FIX: Import the new UserDialog

class UserTableModel(QAbstractTableModel):
    HEADERS = ["Username", "Full Name", "Email", "Role(s)", "Active"]
    def __init__(self, users: List[UserDTO], parent: Optional[QObject] = None):
        super().__init__(parent)
        self._users = users
    def rowCount(self, p=QModelIndex()): return len(self._users)
    def columnCount(self, p=QModelIndex()): return len(self.HEADERS)
    def headerData(self, s, o, r=Qt.DisplayRole):
        if r == Qt.DisplayRole and o == Qt.Horizontal: return self.HEADERS[s]
    def data(self, i, r=Qt.DisplayRole):
        if not i.isValid(): return
        user, col = self._users[i.row()], i.column()
        if r == Qt.DisplayRole:
            if col == 0: return user.username
            if col == 1: return user.full_name or "N/A"
            if col == 2: return user.email
            if col == 3: return ", ".join(role.name for role in user.roles) if user.roles else "No Roles"
            if col == 4: return "Yes" if user.is_active else "No"
    def get_user_at_row(self, r): return self._users[r] if 0 <= r < len(self._users) else None
    def refresh_data(self, new_users: List[UserDTO]): self.beginResetModel(); self._users = new_users; self.endResetModel()

class SettingsView(QWidget):
    """UI for administrators to configure the system."""
    def __init__(self, core: ApplicationCore, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.core = core
        self.async_worker: AsyncWorker = core.async_worker
        self.company_id = self.core.current_company_id
        self._setup_ui()
        self._connect_signals()
        self._load_company_info()
        self._load_users()

    def _setup_ui(self):
        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(self._create_company_tab(), "Company Information")
        self.tab_widget.addTab(self._create_users_tab(), "User Management")
        self.tab_widget.addTab(QLabel("Payment Methods Configuration (Coming Soon)"), "Payment Methods")
        main_layout = QVBoxLayout(self); main_layout.addWidget(self.tab_widget)

    def _create_company_tab(self):
        tab = QWidget(); layout = QFormLayout(tab)
        self.company_name_input = QLineEdit(); self.company_reg_no_input = QLineEdit()
        self.company_gst_no_input = QLineEdit(); self.company_address_input = QLineEdit()
        self.company_phone_input = QLineEdit(); self.company_email_input = QLineEdit()
        self.company_save_button = QPushButton("Save Company Information")
        layout.addRow("Company Name:", self.company_name_input); layout.addRow("Registration No.:", self.company_reg_no_input)
        layout.addRow("GST Reg. No.:", self.company_gst_no_input); layout.addRow("Address:", self.company_address_input)
        layout.addRow("Phone:", self.company_phone_input); layout.addRow("Email:", self.company_email_input); layout.addWidget(self.company_save_button)
        return tab
        
    def _create_users_tab(self):
        tab = QWidget(); layout = QVBoxLayout(tab)
        buttons_layout = QHBoxLayout()
        self.add_user_button = QPushButton("Add New User")
        self.edit_user_button = QPushButton("Edit Selected User")
        self.deactivate_user_button = QPushButton("Deactivate Selected") # FIX: Add deactivate button
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.add_user_button)
        buttons_layout.addWidget(self.edit_user_button)
        buttons_layout.addWidget(self.deactivate_user_button)
        self.user_table = QTableView(); self.user_model = UserTableModel([]); self.user_table.setModel(self.user_model)
        self.user_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.user_table.setSelectionBehavior(QTableView.SelectRows)
        self.user_table.setSelectionMode(QTableView.SingleSelection)
        layout.addLayout(buttons_layout); layout.addWidget(self.user_table)
        return tab

    def _connect_signals(self):
        self.company_save_button.clicked.connect(self._on_save_company_info)
        self.add_user_button.clicked.connect(self._on_add_user)
        self.edit_user_button.clicked.connect(self._on_edit_user)
        self.deactivate_user_button.clicked.connect(self._on_deactivate_user) # FIX: Connect deactivate button
        self.user_table.doubleClicked.connect(self._on_edit_user)

    @Slot()
    def _load_company_info(self):
        # NOTE: company_manager is not yet in ApplicationCore, this is a placeholder call.
        # It needs to be added to ApplicationCore for this to work.
        # For now, this will raise an AttributeError, which is a known gap.
        # def _on_done(r, e):
        #     if e or isinstance(r, Failure): QMessageBox.critical(self, "Load Error", f"Failed to load company info: {e or r.error}")
        #     elif isinstance(r, Success) and r.value:
        #         dto: CompanyDTO = r.value
        #         self.company_name_input.setText(dto.name); self.company_reg_no_input.setText(dto.registration_number)
        #         # ... and so on
        # self.async_worker.run_task(self.core.company_manager.get_company(self.company_id), _on_done)
        pass # Placeholder until company_manager is added

    @Slot()
    def _on_save_company_info(self):
        QMessageBox.information(self, "Not Implemented", "Save Company Info functionality is not yet implemented.")

    @Slot()
    def _load_users(self):
        def _on_done(r, e):
            if e or isinstance(r, Failure): QMessageBox.critical(self, "Load Error", f"Failed to load users: {e or r.error}")
            elif isinstance(r, Success): self.user_model.refresh_data(r.value)
        self.async_worker.run_task(self.core.user_manager.get_all_users(self.company_id), _on_done)

    @Slot()
    def _on_add_user(self):
        # FIX: Replace placeholder with functional dialog
        dialog = UserDialog(self.core, parent=self)
        dialog.user_operation_completed.connect(self._handle_user_operation_completed)
        dialog.exec()
    
    @Slot()
    def _on_edit_user(self):
        # FIX: Replace placeholder with functional dialog
        selected_user = self.user_model.get_user_at_row(self.user_table.currentIndex().row())
        if not selected_user:
            QMessageBox.information(self, "No Selection", "Please select a user to edit.")
            return
        dialog = UserDialog(self.core, user=selected_user, parent=self)
        dialog.user_operation_completed.connect(self._handle_user_operation_completed)
        dialog.exec()

    @Slot()
    def _on_deactivate_user(self):
        # FIX: Implement deactivation logic
        selected_user = self.user_model.get_user_at_row(self.user_table.currentIndex().row())
        if not selected_user:
            QMessageBox.information(self, "No Selection", "Please select a user to deactivate.")
            return
        
        reply = QMessageBox.question(self, "Confirm Deactivation", f"Are you sure you want to deactivate '{selected_user.username}'?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.No: return

        def _on_done(result: Any, error: Optional[Exception]):
            if error or isinstance(result, Failure):
                QMessageBox.critical(self, "Error", f"Failed to deactivate user: {error or result.error}")
            else:
                QMessageBox.information(self, "Success", "User deactivated successfully.")
                self._load_users()
        
        self.async_worker.run_task(self.core.user_manager.deactivate_user(selected_user.id), _on_done)

    @Slot(bool, str)
    def _handle_user_operation_completed(self, success: bool, message: str):
        if success:
            self._load_users()

```

# app/ui/views/reports_view.py
```py
# File: app/ui/views/reports_view.py
"""The main view for generating and displaying reports."""
from __future__ import annotations
from typing import List, Any, Optional
from datetime import date, timedelta
from decimal import Decimal
import uuid

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QComboBox,
    QPushButton, QDateEdit, QTableWidget, QTableWidgetItem, QLabel,
    QHeaderView, QSizePolicy, QMessageBox, QScrollArea, QFileDialog
)
from PySide6.QtCore import Slot, QDate, QAbstractTableModel, QModelIndex, Qt, QObject
from PySide6.QtGui import QDesktopServices
from PySide6.QtCore import QUrl # Import QUrl

from app.core.application_core import ApplicationCore
from app.core.result import Success, Failure
from app.business_logic.dto.reporting_dto import (
    SalesSummaryReportDTO, GstReportDTO, InventoryValuationReportDTO,
    SalesByPeriodDTO, ProductPerformanceDTO, InventoryValuationItemDTO
)
from app.core.async_bridge import AsyncWorker

class SalesByPeriodTableModel(QAbstractTableModel):
    HEADERS = ["Date", "Total Sales (S$)", "Transactions", "Avg. Tx Value (S$)"]
    def __init__(self, data: List[SalesByPeriodDTO], parent: Optional[QObject] = None): super().__init__(parent); self._data = data
    def rowCount(self, p=QModelIndex()): return len(self._data)
    def columnCount(self, p=QModelIndex()): return len(self.HEADERS)
    def headerData(self, s, o, r=Qt.DisplayRole):
        if r == Qt.DisplayRole and o == Qt.Horizontal: return self.HEADERS[s]
    def data(self, i, r=Qt.DisplayRole):
        if not i.isValid(): return
        item = self._data[i.row()]
        col = i.column()
        if r == Qt.DisplayRole:
            if col == 0: return item.period.strftime("%Y-%m-%d")
            if col == 1: return f"{item.total_sales:.2f}"
            if col == 2: return str(item.transaction_count)
            if col == 3: return f"{item.average_transaction_value:.2f}"
        if r == Qt.TextAlignmentRole and col in [1,2,3]: return Qt.AlignRight | Qt.AlignVCenter

class ProductPerformanceTableModel(QAbstractTableModel):
    HEADERS = ["SKU", "Product Name", "Qty Sold", "Revenue (S$)", "Margin (S$)", "Margin (%)"]
    def __init__(self, data: List[ProductPerformanceDTO], parent: Optional[QObject] = None): super().__init__(parent); self._data = data
    def rowCount(self, p=QModelIndex()): return len(self._data)
    def columnCount(self, p=QModelIndex()): return len(self.HEADERS)
    def headerData(self, s, o, r=Qt.DisplayRole):
        if r == Qt.DisplayRole and o == Qt.Horizontal: return self.HEADERS[s]
    def data(self, i, r=Qt.DisplayRole):
        if not i.isValid(): return
        item = self._data[i.row()]
        col = i.column()
        if r == Qt.DisplayRole:
            if col == 0: return item.sku
            if col == 1: return item.name
            if col == 2: return f"{item.quantity_sold:.4f}"
            if col == 3: return f"{item.total_revenue:.2f}"
            if col == 4: return f"{item.gross_margin:.2f}"
            if col == 5: return f"{item.gross_margin_percentage:.2f}%"
        if r == Qt.TextAlignmentRole and col in [2,3,4,5]: return Qt.AlignRight | Qt.AlignVCenter

class InventoryValuationTableModel(QAbstractTableModel):
    HEADERS = ["SKU", "Product Name", "Qty On Hand", "Cost Price (S$)", "Total Value (S$)"]
    def __init__(self, data: List[InventoryValuationItemDTO], parent: Optional[QObject] = None): super().__init__(parent); self._data = data
    def rowCount(self, p=QModelIndex()): return len(self._data)
    def columnCount(self, p=QModelIndex()): return len(self.HEADERS)
    def headerData(self, s, o, r=Qt.DisplayRole):
        if r == Qt.DisplayRole and o == Qt.Horizontal: return self.HEADERS[s]
    def data(self, i, r=Qt.DisplayRole):
        if not i.isValid(): return
        item = self._data[i.row()]
        col = i.column()
        if r == Qt.DisplayRole:
            if col == 0: return item.sku
            if col == 1: return item.name
            if col == 2: return f"{item.quantity_on_hand:.4f}"
            if col == 3: return f"{item.cost_price:.4f}"
            if col == 4: return f"{item.total_value:.2f}"
        if r == Qt.TextAlignmentRole and col in [2,3,4]: return Qt.AlignRight | Qt.AlignVCenter

class ReportsView(QWidget):
    """UI for generating and viewing business reports."""
    def __init__(self, core: ApplicationCore, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.core = core
        self.async_worker: AsyncWorker = core.async_worker
        self.company_id = self.core.current_company_id
        self.outlet_id = self.core.current_outlet_id
        self.current_report_data: Optional[Any] = None
        self._setup_ui()
        self._connect_signals()
        self._set_default_dates()

    def _setup_ui(self):
        controls_layout = QHBoxLayout()
        self.report_selector = QComboBox(); self.report_selector.addItems(["Sales Summary Report", "Inventory Valuation Report", "GST Form 5"])
        self.start_date_edit = QDateEdit(); self.start_date_edit.setCalendarPopup(True)
        self.end_date_edit = QDateEdit(); self.end_date_edit.setCalendarPopup(True)
        self.generate_button = QPushButton("Generate Report"); self.export_pdf_button = QPushButton("Export PDF"); self.export_csv_button = QPushButton("Export CSV")
        controls_layout.addWidget(QLabel("Report:")); controls_layout.addWidget(self.report_selector); controls_layout.addWidget(QLabel("From:")); controls_layout.addWidget(self.start_date_edit)
        controls_layout.addWidget(QLabel("To:")); controls_layout.addWidget(self.end_date_edit); controls_layout.addStretch()
        controls_layout.addWidget(self.generate_button); controls_layout.addWidget(self.export_pdf_button); controls_layout.addWidget(self.export_csv_button)
        self.report_content_widget = QWidget(); self.report_content_layout = QVBoxLayout(self.report_content_widget)
        self.report_content_layout.addWidget(QLabel("Select a report and date range, then click 'Generate Report'.")); self.report_content_layout.addStretch()
        self.report_scroll_area = QScrollArea(); self.report_scroll_area.setWidgetResizable(True); self.report_scroll_area.setWidget(self.report_content_widget)
        main_layout = QVBoxLayout(self); main_layout.addLayout(controls_layout); main_layout.addWidget(self.report_scroll_area)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def _set_default_dates(self):
        today = QDate.currentDate(); self.end_date_edit.setDate(today); self.start_date_edit.setDate(today.addMonths(-1).addDays(1 - today.day()))

    def _connect_signals(self):
        self.generate_button.clicked.connect(self._on_generate_report_clicked)
        self.export_pdf_button.clicked.connect(self._on_export_pdf_clicked); self.export_csv_button.clicked.connect(self._on_export_csv_clicked)

    def _clear_display_area(self):
        while self.report_content_layout.count():
            item = self.report_content_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
            elif item.layout(): self._clear_layout(item.layout())
        self.report_content_layout.addStretch()

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
            elif item.layout(): self._clear_layout(item.layout())

    @Slot()
    def _on_generate_report_clicked(self):
        report_name = self.report_selector.currentText(); start_date = self.start_date_edit.date().toPython(); end_date = self.end_date_edit.date().toPython()
        if start_date > end_date: QMessageBox.warning(self, "Invalid Date Range", "Start date cannot be after end date."); return
        self._clear_display_area(); self.generate_button.setEnabled(False); self.export_pdf_button.setEnabled(False); self.export_csv_button.setEnabled(False)
        self.report_content_layout.addWidget(QLabel("Generating report... Please wait."))
        def _on_done(r, e):
            self.generate_button.setEnabled(True); self._clear_display_area()
            if e or isinstance(r, Failure):
                QMessageBox.critical(self, "Report Error", f"An error occurred: {e or r.error}"); self.current_report_data = None
            elif isinstance(r, Success):
                self.current_report_data = r.value
                self.report_content_layout.addWidget(QLabel(f"<h3>{report_name} ({start_date.strftime('%d %b %Y')} to {end_date.strftime('%d %b %Y')})</h3>"))
                if report_name == "Sales Summary Report": self._display_sales_summary_report(r.value)
                elif report_name == "Inventory Valuation Report": self._display_inventory_valuation_report(r.value)
                elif report_name == "GST Form 5": self._display_gst_report(r.value)
                self.report_content_layout.addStretch(); self.export_pdf_button.setEnabled(True); self.export_csv_button.setEnabled(True)
        coro = None
        if report_name == "Sales Summary Report": coro = self.core.reporting_manager.generate_sales_summary_report(self.company_id, start_date, end_date)
        elif report_name == "Inventory Valuation Report": coro = self.core.reporting_manager.generate_inventory_valuation_report(self.company_id, self.outlet_id)
        elif report_name == "GST Form 5": coro = self.core.gst_manager.generate_gst_f5_report(self.company_id, start_date, end_date)
        if coro: self.async_worker.run_task(coro, on_done_callback=_on_done)
        else: self.generate_button.setEnabled(True); self._clear_display_area(); self.current_report_data = None

    def _display_sales_summary_report(self, dto: SalesSummaryReportDTO):
        self.report_content_layout.addWidget(QLabel(f"<b>Overall Revenue: S${dto.total_revenue:.2f}</b> | <b>Total Transactions: {dto.total_transactions}</b>"))
        self.report_content_layout.addWidget(QLabel("<b>Sales by Period:</b>")); table = QTableView(); table.setModel(SalesByPeriodTableModel(dto.sales_by_period)); table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch); self.report_content_layout.addWidget(table)
        self.report_content_layout.addWidget(QLabel("<br><b>Top Performing Products:</b>")); table2 = QTableView(); table2.setModel(ProductPerformanceTableModel(dto.top_performing_products)); table2.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch); self.report_content_layout.addWidget(table2)

    def _display_inventory_valuation_report(self, dto: InventoryValuationReportDTO):
        self.report_content_layout.addWidget(QLabel(f"<b>Valuation for {dto.outlet_name} as of {dto.as_of_date.strftime('%d %b %Y')}</b>"))
        self.report_content_layout.addWidget(QLabel(f"<b>Total Inventory Value: S${dto.total_inventory_value:.2f}</b> | <b>Total Items: {dto.total_distinct_items}</b>"))
        table = QTableView(); table.setModel(InventoryValuationTableModel(dto.items)); table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch); self.report_content_layout.addWidget(table)

    def _display_gst_report(self, dto: GstReportDTO):
        html = f"""<h3>IRAS GST Form 5 Summary</h3>
                   <p><b>Company:</b> {dto.company_name} (GST Reg No: {dto.company_gst_reg_no or 'N/A'})</p>
                   <p><b>Period:</b> {dto.start_date.strftime('%d %b %Y')} to {dto.end_date.strftime('%d %b %Y')}</p><hr>
                   <table width='100%'>
                     <tr><td><b>Box 1: Standard-Rated Supplies</b></td><td align='right'>S${dto.box_1_standard_rated_supplies:.2f}</td></tr>
                     <tr><td>Box 2: Zero-Rated Supplies</td><td align='right'>S${dto.box_2_zero_rated_supplies:.2f}</td></tr>
                     <tr><td>Box 3: Exempt Supplies</td><td align='right'>S${dto.box_3_exempt_supplies:.2f}</td></tr>
                     <tr><td><b>Box 4: Total Supplies</b></td><td align='right'><b>S${dto.box_4_total_supplies:.2f}</b></td></tr>
                     <tr><td colspan=2><br></td></tr>
                     <tr><td><b>Box 6: Output Tax Due</b></td><td align='right'><b>S${dto.box_6_output_tax_due:.2f}</b></td></tr>
                     <tr><td colspan=2><br><b>Purchases (Input Tax)</b></td></tr>
                     <tr><td><b>Box 5: Taxable Purchases</b></td><td align='right'><b>S${dto.box_5_taxable_purchases:.2f}</b></td></tr>
                     <tr><td><b>Box 7: Input Tax Claimed</b></td><td align='right'><b>S${dto.box_7_input_tax_claimed:.2f}</b></td></tr>
                   </table><hr>
                   <p align='right'><b>Box 13: Net GST {'Payable' if dto.box_13_net_gst_payable >= 0 else 'Reclaimable'} (S$): 
                   <span style='font-size: 24px; color: {'red' if dto.box_13_net_gst_payable >= 0 else 'green'};'>
                   {abs(dto.box_13_net_gst_payable):.2f}</span></b></p>"""
        self.report_content_layout.addWidget(QLabel(html))

    @Slot()
    def _on_export_pdf_clicked(self):
        if not self.current_report_data: QMessageBox.warning(self, "No Report", "Please generate a report first."); return
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Report as PDF", "", "PDF Files (*.pdf)")
        if file_name:
            QMessageBox.information(self, "Not Implemented", "PDF export functionality is not yet implemented.")

    @Slot()
    def _on_export_csv_clicked(self):
        if not self.current_report_data: QMessageBox.warning(self, "No Report", "Please generate a report first."); return
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Report as CSV", "", "CSV Files (*.csv)")
        if file_name:
            QMessageBox.information(self, "Not Implemented", "CSV export functionality is not yet implemented.")

```

# app/ui/views/product_view.py
```py
# File: app/ui/views/product_view.py
"""The main view for managing products."""
from __future__ import annotations
from typing import List, Any, Optional
from decimal import Decimal

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableView,
    QMessageBox, QLineEdit, QHeaderView, QSizePolicy
)
from PySide6.QtCore import Slot, Signal, QAbstractTableModel, QModelIndex, Qt, QObject

from app.core.application_core import ApplicationCore
from app.core.result import Success, Failure
from app.business_logic.dto.product_dto import ProductDTO
from app.ui.dialogs.product_dialog import ProductDialog
from app.core.async_bridge import AsyncWorker

class ProductTableModel(QAbstractTableModel):
    """A Qt Table Model for displaying ProductDTOs."""
    HEADERS = ["SKU", "Name", "Selling Price", "Cost Price", "GST Rate", "Active"]

    def __init__(self, products: List[ProductDTO] = None, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._products = products or []

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._products)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self.HEADERS)

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole) -> Any:
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.HEADERS[section]
        return None

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        if not index.isValid(): return None
        product = self._products[index.row()]
        col = index.column()
        if role == Qt.DisplayRole:
            if col == 0: return product.sku
            if col == 1: return product.name
            if col == 2: return f"S${product.selling_price:.2f}"
            if col == 3: return f"S${product.cost_price:.2f}"
            if col == 4: return f"{product.gst_rate:.2f}%"
            if col == 5: return "Yes" if product.is_active else "No"
        if role == Qt.TextAlignmentRole:
            if col in [2, 3, 4]: return Qt.AlignRight | Qt.AlignVCenter
            if col == 5: return Qt.AlignCenter
        return None

    def get_product_at_row(self, row: int) -> Optional[ProductDTO]:
        return self._products[row] if 0 <= row < len(self._products) else None

    def refresh_data(self, new_products: List[ProductDTO]):
        self.beginResetModel()
        self._products = new_products
        self.endResetModel()

class ProductView(QWidget):
    """A view widget to display and manage the product catalog."""
    def __init__(self, core: ApplicationCore, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.core = core
        self.async_worker: AsyncWorker = core.async_worker
        self._setup_ui()
        self._connect_signals()
        self._load_products()

    def _setup_ui(self):
        top_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search products by SKU, name, or barcode...")
        self.add_button = QPushButton("Add New Product")
        self.edit_button = QPushButton("Edit Selected")
        self.delete_button = QPushButton("Deactivate Selected")
        top_layout.addWidget(self.search_input, 1)
        top_layout.addStretch()
        top_layout.addWidget(self.add_button)
        top_layout.addWidget(self.edit_button)
        top_layout.addWidget(self.delete_button)
        
        self.table_view = QTableView()
        self.product_model = ProductTableModel()
        self.table_view.setModel(self.product_model)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_view.setSelectionBehavior(QTableView.SelectRows)
        self.table_view.setSelectionMode(QTableView.SingleSelection)
        self.table_view.setSortingEnabled(True)

        main_layout = QVBoxLayout(self)
        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.table_view)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def _connect_signals(self):
        self.add_button.clicked.connect(self._on_add_product)
        self.edit_button.clicked.connect(self._on_edit_product)
        self.delete_button.clicked.connect(self._on_deactivate_product)
        self.search_input.textChanged.connect(self._on_search_products)
        self.table_view.doubleClicked.connect(self._on_edit_product)

    def _get_selected_product(self) -> Optional[ProductDTO]:
        selected_indexes = self.table_view.selectionModel().selectedRows()
        return self.product_model.get_product_at_row(selected_indexes[0].row()) if selected_indexes else None

    @Slot()
    def _load_products(self, search_term: str = ""):
        def _on_done(result: Any, error: Optional[Exception]):
            if error or isinstance(result, Failure):
                QMessageBox.critical(self, "Load Error", f"Failed to load products: {error or result.error}")
            elif isinstance(result, Success):
                self.product_model.refresh_data(result.value)
        
        coro = self.core.product_manager.search_products(self.core.current_company_id, search_term) if search_term else self.core.product_manager.get_all_products(self.core.current_company_id)
        self.async_worker.run_task(coro, _on_done)

    @Slot()
    def _on_add_product(self):
        dialog = ProductDialog(self.core, parent=self)
        dialog.product_operation_completed.connect(self._handle_operation_completed)
        dialog.exec()

    @Slot()
    def _on_edit_product(self):
        selected_product = self._get_selected_product()
        if not selected_product:
            QMessageBox.information(self, "No Selection", "Please select a product to edit.")
            return
        dialog = ProductDialog(self.core, product=selected_product, parent=self)
        dialog.product_operation_completed.connect(self._handle_operation_completed)
        dialog.exec()

    @Slot()
    def _on_deactivate_product(self):
        selected_product = self._get_selected_product()
        if not selected_product:
            QMessageBox.information(self, "No Selection", "Please select a product to deactivate.")
            return
        
        reply = QMessageBox.question(self, "Confirm Deactivation", f"Are you sure you want to deactivate '{selected_product.name}'?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.No: return

        def _on_done(result: Any, error: Optional[Exception]):
            if error or isinstance(result, Failure):
                QMessageBox.critical(self, "Error", f"Failed to deactivate product: {error or result.error}")
            elif isinstance(result, Success) and result.value:
                QMessageBox.information(self, "Success", f"Product '{selected_product.name}' deactivated.")
                self._load_products(self.search_input.text())
        
        self.async_worker.run_task(self.core.product_manager.deactivate_product(selected_product.id), _on_done)

    @Slot(str)
    def _on_search_products(self, text: str):
        self._load_products(search_term=text)

    @Slot(bool, str)
    def _handle_operation_completed(self, success: bool, message: str):
        if success:
            self._load_products(self.search_input.text())

```

# app/ui/main_window.py
```py
# File: app/ui/main_window.py
"""
The main window of the SG-POS application.
This QMainWindow acts as the shell, hosting different views like the POS screen,
inventory management, etc., and providing navigation.

This version implements lazy loading for all non-default views to improve
startup performance.
"""
import sys
from typing import Dict, Optional, Type

from PySide6.QtWidgets import (
    QMainWindow, QWidget,
    QStackedWidget, QMenuBar
)
from PySide6.QtCore import Slot, QEvent

from app.core.application_core import ApplicationCore
from app.core.async_bridge import AsyncWorker

# Import all view classes that will be lazy-loaded
from app.ui.views.pos_view import POSView
from app.ui.views.product_view import ProductView
from app.ui.views.customer_view import CustomerView
from app.ui.views.inventory_view import InventoryView
from app.ui.views.reports_view import ReportsView
from app.ui.views.settings_view import SettingsView

class MainWindow(QMainWindow):
    """The main application window."""
    def __init__(self, core: ApplicationCore):
        super().__init__()
        self.core = core
        self.async_worker: AsyncWorker = core.async_worker
        self.setWindowTitle("SG Point-of-Sale System")
        self.setGeometry(100, 100, 1440, 900)

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # --- Lazy Loading Implementation ---
        # 1. A dictionary to hold view definitions and cache instances
        self.views: Dict[str, Dict[str, Optional[Type[QWidget]]]] = {
            "product":   {"class": ProductView,   "instance": None},
            "customer":  {"class": CustomerView,  "instance": None},
            "inventory": {"class": InventoryView, "instance": None},
            "reports":   {"class": ReportsView,   "instance": None},
            "settings":  {"class": SettingsView,  "instance": None},
        }

        # 2. Eagerly create and show only the default view
        self.pos_view = POSView(self.core)
        self.stacked_widget.addWidget(self.pos_view)
        self.stacked_widget.setCurrentWidget(self.pos_view)
        
        # 3. Create the menu, which will connect actions to the lazy loader
        self._create_menu()

    def _create_menu(self):
        """Creates the main menu bar with navigation actions wired for lazy loading."""
        menu_bar = self.menuBar()
        
        file_menu = menu_bar.addMenu("&File")
        file_menu.addAction("E&xit", self.close)

        pos_menu = menu_bar.addMenu("&POS")
        pos_menu.addAction("Sales Screen", lambda: self.stacked_widget.setCurrentWidget(self.pos_view))

        data_menu = menu_bar.addMenu("&Data Management")
        data_menu.addAction("Products", lambda: self._show_view("product"))
        data_menu.addAction("Customers", lambda: self._show_view("customer"))
        
        inventory_menu = menu_bar.addMenu("&Inventory")
        inventory_menu.addAction("Stock Management", lambda: self._show_view("inventory"))
        
        reports_menu = menu_bar.addMenu("&Reports")
        reports_menu.addAction("Business Reports", lambda: self._show_view("reports"))
        
        settings_menu = menu_bar.addMenu("&Settings")
        settings_menu.addAction("Application Settings", lambda: self._show_view("settings"))

    def _show_view(self, view_key: str):
        """
        Generic handler for showing a view. Creates the view on first request.
        
        Args:
            view_key: The key corresponding to the view in the self.views dictionary.
        """
        if view_key not in self.views:
            return

        view_info = self.views[view_key]
        
        # If the view instance hasn't been created yet, create and cache it
        if view_info["instance"] is None:
            view_class = view_info["class"]
            view_info["instance"] = view_class(self.core)
            self.stacked_widget.addWidget(view_info["instance"])

        # Set the current widget to the now-guaranteed-to-exist instance
        self.stacked_widget.setCurrentWidget(view_info["instance"])

    def closeEvent(self, event: QEvent) -> None:
        """Handles window close event to gracefully shut down the application core."""
        if self.core:
            self.core.shutdown()
        event.accept()

```

# app/ui/widgets/__init__.py
```py

```

# app/ui/widgets/searchable_table_view.py
```py

```

# app/services/customer_service.py
```py
# File: app/services/customer_service.py
"""Data Access Service (Repository) for Customer entities."""
from __future__ import annotations
from typing import TYPE_CHECKING
from uuid import UUID
import sqlalchemy as sa
from sqlalchemy.future import select

from app.core.result import Result, Success, Failure
from app.models.customer import Customer
from app.services.base_service import BaseService

if TYPE_CHECKING:
    from app.core.application_core import ApplicationCore

class CustomerService(BaseService):
    """Handles all database interactions for the Customer model."""

    def __init__(self, core: "ApplicationCore"):
        super().__init__(core, Customer)

    async def get_by_code(self, company_id: UUID, code: str) -> Result[Customer | None, str]:
        """Fetches a customer by their unique code for a given company."""
        try:
            async with self.core.get_session() as session:
                stmt = select(Customer).where(
                    Customer.company_id == company_id,
                    Customer.customer_code == code
                )
                result = await session.execute(stmt)
                customer = result.scalar_one_or_none()
                return Success(customer)
        except Exception as e:
            return Failure(f"Database error fetching customer by code: {e}")

    async def create_customer(self, customer: Customer) -> Result[Customer, str]:
        """Saves a new customer instance to the database."""
        try:
            async with self.core.get_session() as session:
                session.add(customer)
                await session.flush()
                await session.refresh(customer)
                return Success(customer)
        except sa.exc.IntegrityError:
            return Failure("Customer with this code or email already exists.")
        except Exception as e:
            return Failure(f"Database error creating customer: {e}")

    async def update_customer(self, customer: Customer) -> Result[Customer, str]:
        """Updates an existing customer instance in the database."""
        try:
            async with self.core.get_session() as session:
                session.add(customer)
                await session.flush()
                await session.refresh(customer)
                return Success(customer)
        except Exception as e:
            return Failure(f"Database error updating customer: {e}")

```

# app/services/__init__.py
```py

```

# app/services/inventory_service.py
```py
# File: app/services/inventory_service.py
"""Data Access Service (Repository) for Inventory operations."""
from __future__ import annotations
from typing import TYPE_CHECKING, List, Optional
from uuid import UUID
from decimal import Decimal
import sqlalchemy as sa
from sqlalchemy.future import select

from app.core.result import Result, Success, Failure
from app.models.inventory import Inventory, StockMovement
from app.models.product import Product
from app.services.base_service import BaseService

if TYPE_CHECKING:
    from app.core.application_core import ApplicationCore
    from sqlalchemy.ext.asyncio import AsyncSession

class InventoryService(BaseService):
    """
    Handles direct database interactions for inventory levels and stock movements.
    """
    def __init__(self, core: "ApplicationCore"):
        super().__init__(core, Inventory)

    async def get_stock_level(self, outlet_id: UUID, product_id: UUID, variant_id: Optional[UUID], session: Optional[AsyncSession] = None) -> Result[Decimal, str]:
        """Gets the current quantity_on_hand for a product/variant at an outlet."""
        db_session = session if session else self.core.get_session()
        try:
            async with db_session as session:
                stmt = select(Inventory.quantity_on_hand).where(
                    Inventory.outlet_id == outlet_id,
                    Inventory.product_id == product_id,
                    Inventory.variant_id == variant_id
                )
                result = await session.execute(stmt)
                quantity = result.scalar_one_or_none()
                return Success(quantity if quantity is not None else Decimal("0"))
        except Exception as e:
            return Failure(f"Database error getting stock level: {e}")

    async def adjust_stock_level(self, outlet_id: UUID, product_id: UUID, variant_id: Optional[UUID], quantity_change: Decimal, session: AsyncSession) -> Result[Decimal, str]:
        """Adjusts the stock level for a product. Must be called within an existing transaction."""
        try:
            stmt = select(Inventory).where(
                Inventory.outlet_id == outlet_id,
                Inventory.product_id == product_id,
                Inventory.variant_id == variant_id
            ).with_for_update()
            
            result = await session.execute(stmt)
            inventory_item = result.scalar_one_or_none()

            if inventory_item:
                inventory_item.quantity_on_hand += quantity_change
            else:
                inventory_item = Inventory(
                    outlet_id=outlet_id,
                    product_id=product_id,
                    variant_id=variant_id,
                    quantity_on_hand=quantity_change
                )
                session.add(inventory_item)
            
            if inventory_item.quantity_on_hand < 0:
                raise ValueError("Stock quantity cannot be negative.")

            await session.flush()
            return Success(inventory_item.quantity_on_hand)
        except ValueError as ve:
            return Failure(str(ve))
        except Exception as e:
            return Failure(f"Failed to adjust stock level: {e}")

    async def log_movement(self, movement: StockMovement, session: AsyncSession) -> Result[StockMovement, str]:
        """Logs a stock movement record within an existing transaction."""
        try:
            session.add(movement)
            await session.flush()
            return Success(movement)
        except Exception as e:
            return Failure(f"Failed to log stock movement: {e}")

    async def get_inventory_summary(self, company_id: UUID, outlet_id: Optional[UUID], limit: int, offset: int, search_term: Optional[str]) -> Result[List[dict], str]:
        """Retrieves a summary of inventory levels for display."""
        try:
            async with self.core.get_session() as session:
                stmt = select(
                    Product.id.label("product_id"),
                    Product.name.label("product_name"),
                    Product.sku,
                    Product.barcode,
                    Product.reorder_point,
                    Product.is_active,
                    Product.cost_price,
                    Product.selling_price,
                    sa.func.coalesce(Inventory.quantity_on_hand, Decimal('0.0')).label("quantity_on_hand"),
                    sa.text("(SELECT name FROM sgpos.categories WHERE id = products.category_id) AS category_name")
                ).select_from(Product).outerjoin(Inventory, sa.and_(
                    Inventory.product_id == Product.id,
                    Inventory.outlet_id == outlet_id
                )).where(Product.company_id == company_id)

                if search_term:
                    search_pattern = f"%{search_term}%"
                    stmt = stmt.where(sa.or_(
                        Product.sku.ilike(search_pattern),
                        Product.name.ilike(search_pattern)
                    ))
                
                stmt = stmt.order_by(Product.name).offset(offset).limit(limit)
                result = await session.execute(stmt)
                return Success([row._asdict() for row in result.all()])
        except Exception as e:
            return Failure(f"Database error getting inventory summary: {e}")

```

# app/services/purchase_order_service.py
```py
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

# app/services/payment_service.py
```py
# File: app/services/payment_service.py
"""Data Access Service (Repository) for Payment methods and Payments."""
from __future__ import annotations
from typing import TYPE_CHECKING, List
from uuid import UUID
import sqlalchemy as sa
from sqlalchemy.future import select

from app.core.result import Result, Success, Failure
from app.models.sales import PaymentMethod, Payment # Import ORM models from sales.py
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
                ).order_by(PaymentMethod.name)
                result = await session.execute(stmt)
                methods = result.scalars().all()
                return Success(methods)
        except Exception as e:
            return Failure(f"Database error fetching active payment methods: {e}")

class PaymentService(BaseService):
    """
    Handles database interactions for Payment models.
    For now, mostly used for retrieving, as creation is part of SalesService.
    """
    def __init__(self, core: "ApplicationCore"):
        super().__init__(core, Payment)

    # TODO: Add methods for retrieving payments, e.g., by sales_transaction_id

```

# app/services/user_service.py
```py
# File: app/services/user_service.py
"""Data Access Service for User and Role entities."""
from __future__ import annotations
from typing import TYPE_CHECKING, List, Optional
from uuid import UUID
import sqlalchemy as sa
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.core.result import Result, Success, Failure
from app.models import User, Role, UserRole, Permission
from app.services.base_service import BaseService

if TYPE_CHECKING:
    from app.core.application_core import ApplicationCore
    from sqlalchemy.ext.asyncio import AsyncSession

class UserService(BaseService):
    """Handles database interactions for the User model."""
    def __init__(self, core: "ApplicationCore"):
        super().__init__(core, User)

    async def get_by_username(self, company_id: UUID, username: str) -> Result[Optional[User], str]:
        try:
            async with self.core.get_session() as session:
                stmt = select(User).where(User.company_id == company_id, User.username == username).options(selectinload(User.user_roles).selectinload(UserRole.role))
                result = await session.execute(stmt)
                return Success(result.scalar_one_or_none())
        except Exception as e:
            return Failure(f"Database error fetching user by username: {e}")

class RoleService(BaseService):
    """Handles database interactions for the Role model."""
    def __init__(self, core: "ApplicationCore"):
        super().__init__(core, Role)
    
    async def get_all_with_permissions(self, company_id: UUID) -> Result[List[Role], str]:
        try:
            async with self.core.get_session() as session:
                stmt = select(Role).where(Role.company_id == company_id).options(selectinload(Role.role_permissions).selectinload(RolePermission.permission))
                result = await session.execute(stmt)
                return Success(result.scalars().unique().all())
        except Exception as e:
            return Failure(f"Database error fetching roles: {e}")

```

# app/services/base_service.py
```py
# File: app/services/base_service.py
"""
Abstract Base Class for all data services (Repositories).

This provides a consistent interface and reusable logic for common CRUD
operations, reducing boilerplate code in concrete service implementations.
"""
from __future__ import annotations
from typing import TYPE_CHECKING, Type, TypeVar, List, Optional, Any
from uuid import UUID
import sqlalchemy as sa
from sqlalchemy.future import select

from app.core.result import Result, Success, Failure
from app.core.exceptions import CoreException 

if TYPE_CHECKING:
    from app.core.application_core import ApplicationCore
    from app.models.base import Base 

ModelType = TypeVar("ModelType", bound="Base")

class BaseService:
    """
    Implements the Repository pattern for a given SQLAlchemy model.
    Provides generic CRUD operations.
    """
    def __init__(self, core: "ApplicationCore", model: Type[ModelType]):
        if not isinstance(model, type):
            raise ValueError("Model must be a SQLAlchemy model class.")
        self.core = core
        self.model = model

    async def get_by_id(self, record_id: UUID) -> Result[ModelType | None, str]:
        """
        Fetches a single record by its primary key (ID).
        """
        try:
            async with self.core.get_session() as session:
                stmt = select(self.model).where(self.model.id == record_id)
                result = await session.execute(stmt)
                record = result.scalar_one_or_none()
                return Success(record)
        except Exception as e:
            return Failure(f"Database error fetching {self.model.__tablename__} by ID: {e}")

    async def get_by_ids(self, record_ids: List[UUID]) -> Result[List[ModelType], str]:
        """
        Fetches multiple records by a list of primary keys (IDs).
        
        Args:
            record_ids: A list of UUIDs to fetch.
        
        Returns:
            A Success containing a list of model instances, or a Failure.
        """
        if not record_ids:
            return Success([])
        try:
            async with self.core.get_session() as session:
                stmt = select(self.model).where(self.model.id.in_(record_ids))
                result = await session.execute(stmt)
                records = result.scalars().all()
                return Success(records)
        except Exception as e:
            return Failure(f"Database error fetching {self.model.__tablename__} by IDs: {e}")

    async def get_all(
        self,
        company_id: UUID,
        limit: int = 100,
        offset: int = 0,
        options: Optional[List] = None,
        **kwargs: Any
    ) -> Result[List[ModelType], str]:
        """
        Fetches all records for the model with pagination and dynamic filtering.
        
        Args:
            company_id: The UUID of the company to filter by.
            limit: Maximum number of records to return.
            offset: Number of records to skip.
            options: A list of SQLAlchemy loader options (e.g., for eager loading).
            **kwargs: Additional filter conditions where key is a column name.
        
        Returns:
            A Success containing a list of model instances, or a Failure.
        """
        try:
            async with self.core.get_session() as session:
                stmt = select(self.model).where(self.model.company_id == company_id).offset(offset).limit(limit)
                
                # FIX: Dynamically apply filters from kwargs
                for key, value in kwargs.items():
                    if hasattr(self.model, key) and value is not None:
                        stmt = stmt.where(getattr(self.model, key) == value)

                if options:
                    stmt = stmt.options(*options)

                result = await session.execute(stmt)
                records = result.scalars().unique().all()
                return Success(records)
        except Exception as e:
            return Failure(f"Database error fetching all {self.model.__tablename__}: {e}")

    async def create(self, model_instance: ModelType) -> Result[ModelType, str]:
        """
        Saves a new model instance to the database.
        """
        try:
            async with self.core.get_session() as session:
                session.add(model_instance)
                await session.flush()
                await session.refresh(model_instance)
                return Success(model_instance)
        except sa.exc.IntegrityError as e:
            return Failure(f"Data integrity error creating {self.model.__tablename__}: Duplicate entry or missing reference. Details: {e.orig}")
        except Exception as e:
            return Failure(f"Database error creating {self.model.__tablename__}: {e}")

    async def update(self, model_instance: ModelType) -> Result[ModelType, str]:
        """
        Updates an existing model instance in the database.
        """
        try:
            async with self.core.get_session() as session:
                session.add(model_instance) 
                await session.flush()
                await session.refresh(model_instance)
                return Success(model_instance)
        except Exception as e:
            return Failure(f"Database error updating {self.model.__tablename__}: {e}")

    async def delete(self, record_id: UUID) -> Result[bool, str]:
        """
        Deletes a record by its ID.
        """
        try:
            async with self.core.get_session() as session:
                stmt = select(self.model).where(self.model.id == record_id)
                result = await session.execute(stmt)
                record = result.scalar_one_or_none()
                if record:
                    await session.delete(record)
                    return Success(True)
                return Success(False)
        except sa.exc.IntegrityError as e:
            return Failure(f"Cannot delete {self.model.__tablename__}: It is referenced by other records. (Integrity error: {e.orig})")
        except Exception as e:
            return Failure(f"Database error deleting {self.model.__tablename__}: {e}")

```

# app/services/company_service.py
```py
# File: app/services/company_service.py
"""Data Access Service (Repository) for Company and Outlet entities."""
from __future__ import annotations
from typing import TYPE_CHECKING, List, Optional
from uuid import UUID
import sqlalchemy as sa
from sqlalchemy.future import select

from app.core.result import Result, Success, Failure
from app.models import Company, Outlet
from app.services.base_service import BaseService

if TYPE_CHECKING:
    from app.core.application_core import ApplicationCore

class CompanyService(BaseService):
    """Handles database interactions for Company models."""
    def __init__(self, core: "ApplicationCore"):
        super().__init__(core, Company)

class OutletService(BaseService):
    """Handles database interactions for Outlet models."""
    def __init__(self, core: "ApplicationCore"):
        super().__init__(core, Outlet)

    async def get_all_by_company(self, company_id: UUID) -> Result[List[Outlet], str]:
        """Fetches all active outlets for a specific company."""
        try:
            async with self.core.get_session() as session:
                stmt = select(Outlet).where(Outlet.company_id == company_id, Outlet.is_active == True).order_by(Outlet.name)
                result = await session.execute(stmt)
                return Success(result.scalars().all())
        except Exception as e:
            return Failure(f"Database error fetching outlets for company {company_id}: {e}")

```

# app/services/supplier_service.py
```py
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

# app/services/report_service.py
```py
# File: app/services/report_service.py
"""
Data Access Service for complex reporting queries.

This service is responsible for running efficient data aggregation queries
directly against the database to generate the raw data needed for business reports.
It primarily uses SQLAlchemy Core for performance-critical aggregation.
"""
from __future__ import annotations
from typing import TYPE_CHECKING, List, Dict, Any, Optional
from datetime import date, datetime, timedelta
from decimal import Decimal
import uuid
import sqlalchemy as sa
from sqlalchemy.sql import func, cast

from app.core.result import Result, Success, Failure
from app.models import SalesTransaction, SalesTransactionItem, Product, Inventory, PurchaseOrder, PurchaseOrderItem

if TYPE_CHECKING:
    from app.core.application_core import ApplicationCore

class ReportService:
    """Handles all database aggregation queries for reporting."""

    def __init__(self, core: "ApplicationCore"):
        self.core = core

    async def get_sales_summary_raw_data(self, company_id: uuid.UUID, start_date: date, end_date: date) -> Result[List[Dict[str, Any]], str]:
        """Fetches aggregated sales data grouped by day."""
        try:
            async with self.core.get_session() as session:
                end_datetime = datetime.combine(end_date, datetime.max.time())
                stmt = (
                    sa.select(
                        cast(SalesTransaction.transaction_date, sa.Date).label("period"),
                        func.sum(SalesTransaction.total_amount).label("total_sales"),
                        func.count(SalesTransaction.id).label("transaction_count"),
                        func.sum(SalesTransaction.discount_amount).label("total_discount_amount"),
                        func.sum(SalesTransaction.tax_amount).label("total_tax_collected")
                    ).where(
                        SalesTransaction.company_id == company_id,
                        SalesTransaction.transaction_date >= datetime.combine(start_date, datetime.min.time()),
                        SalesTransaction.transaction_date <= end_datetime,
                        SalesTransaction.status == 'COMPLETED'
                    ).group_by("period").order_by("period")
                )
                result = await session.execute(stmt)
                return Success([row._asdict() for row in result.all()])
        except Exception as e:
            return Failure(f"Database error generating sales summary: {e}")

    async def get_product_performance_raw_data(self, company_id: uuid.UUID, start_date: date, end_date: date, limit: int = 10) -> Result[List[Dict[str, Any]], str]:
        """Fetches product performance data (quantity sold, revenue, cost, margin)."""
        try:
            async with self.core.get_session() as session:
                end_datetime = datetime.combine(end_date, datetime.max.time())
                stmt = (
                    sa.select(
                        Product.id.label("product_id"), Product.sku, Product.name,
                        func.sum(SalesTransactionItem.quantity).label("quantity_sold"),
                        func.sum(SalesTransactionItem.line_total).label("total_revenue"),
                        func.sum(SalesTransactionItem.quantity * SalesTransactionItem.cost_price).label("total_cost")
                    ).join(SalesTransactionItem, SalesTransactionItem.product_id == Product.id)
                     .join(SalesTransaction, SalesTransactionItem.sales_transaction_id == SalesTransaction.id)
                     .where(
                        SalesTransaction.company_id == company_id,
                        SalesTransaction.transaction_date >= datetime.combine(start_date, datetime.min.time()),
                        SalesTransaction.transaction_date <= end_datetime,
                        SalesTransaction.status == 'COMPLETED'
                     ).group_by(Product.id).order_by(sa.desc("total_revenue")).limit(limit)
                )
                result = await session.execute(stmt)
                return Success([row._asdict() for row in result.all()])
        except Exception as e:
            return Failure(f"Database error generating product performance: {e}")

    async def get_inventory_valuation_raw_data(self, company_id: uuid.UUID, outlet_id: Optional[uuid.UUID] = None) -> Result[List[Dict[str, Any]], str]:
        """Fetches raw data for inventory valuation report."""
        try:
            async with self.core.get_session() as session:
                stmt = select(
                    Product.id.label("product_id"), Product.sku, Product.name,
                    Product.cost_price, Inventory.quantity_on_hand
                ).join(Inventory, Inventory.product_id == Product.id).where(Product.company_id == company_id)
                if outlet_id:
                    stmt = stmt.where(Inventory.outlet_id == outlet_id)
                result = await session.execute(stmt)
                return Success([row._asdict() for row in result.all()])
        except Exception as e:
            return Failure(f"Database error generating inventory valuation: {e}")

    async def get_gst_f5_raw_data(self, company_id: uuid.UUID, start_date: date, end_date: date) -> Result[Dict[str, Any], str]:
        """Fetches all necessary data points for the IRAS GST F5 form."""
        try:
            async with self.core.get_session() as session:
                end_datetime = datetime.combine(end_date, datetime.max.time())
                sales_stmt = (
                    sa.select(
                        func.sum(SalesTransactionItem.line_total).filter(Product.gst_rate > 0).label("standard_rated_sales"),
                        func.sum(SalesTransactionItem.line_total).filter(Product.gst_rate == 0).label("zero_rated_sales"),
                        func.sum(SalesTransaction.tax_amount).label("output_tax_due")
                    ).join(SalesTransactionItem, SalesTransaction.id == SalesTransactionItem.sales_transaction_id)
                     .join(Product, SalesTransactionItem.product_id == Product.id)
                     .where(
                        SalesTransaction.company_id == company_id,
                        SalesTransaction.transaction_date.between(datetime.combine(start_date, datetime.min.time()), end_datetime),
                        SalesTransaction.status == 'COMPLETED'
                    )
                )
                sales_res = (await session.execute(sales_stmt)).one_or_none()

                purchase_stmt = (
                    sa.select(
                        func.sum(PurchaseOrderItem.quantity_received * PurchaseOrderItem.unit_cost).label("taxable_purchases")
                    ).join(PurchaseOrder, PurchaseOrderItem.purchase_order_id == PurchaseOrder.id)
                     .where(
                        PurchaseOrder.company_id == company_id,
                        PurchaseOrder.order_date.between(start_date, end_date),
                        PurchaseOrder.status.in_(['RECEIVED', 'PARTIALLY_RECEIVED'])
                    )
                )
                purchase_res = (await session.execute(purchase_stmt)).one_or_none()
                
                # Assume a fixed GST rate for calculating input tax for this demo
                taxable_purchases = purchase_res.taxable_purchases or Decimal('0.00')
                input_tax_claimed = (taxable_purchases * (Decimal('8.00') / (Decimal('100.00') + Decimal('8.00')))).quantize(Decimal("0.01"))

                return Success({
                    "box_1_standard_rated_supplies": sales_res.standard_rated_sales or Decimal('0.00'),
                    "box_2_zero_rated_supplies": sales_res.zero_rated_sales or Decimal('0.00'),
                    "box_3_exempt_supplies": Decimal('0.00'),
                    "box_6_output_tax_due": sales_res.output_tax_due or Decimal('0.00'),
                    "box_5_taxable_purchases": taxable_purchases,
                    "box_7_input_tax_claimed": input_tax_claimed,
                })
        except Exception as e:
            return Failure(f"Database error generating GST F5 data: {e}")

```

# app/services/product_service.py
```py
# File: app/services/product_service.py
"""Data Access Service (Repository) for Product entities."""
from __future__ import annotations
from typing import TYPE_CHECKING
from uuid import UUID
import sqlalchemy as sa
from sqlalchemy.future import select

from app.core.result import Result, Success, Failure
from app.models.product import Product
from app.services.base_service import BaseService

if TYPE_CHECKING:
    from app.core.application_core import ApplicationCore

class ProductService(BaseService):
    """Handles all database interactions for the Product model."""

    def __init__(self, core: "ApplicationCore"):
        super().__init__(core, Product)

    async def get_by_sku(self, company_id: UUID, sku: str) -> Result[Product | None, str]:
        """Fetches a product by its unique SKU for a given company."""
        try:
            async with self.core.get_session() as session:
                stmt = select(Product).where(
                    Product.company_id == company_id,
                    Product.sku == sku
                )
                result = await session.execute(stmt)
                product = result.scalar_one_or_none()
                return Success(product)
        except Exception as e:
            return Failure(f"Database error fetching product by SKU: {e}")

    async def create_product(self, product: Product) -> Result[Product, str]:
        """Saves a new product instance to the database."""
        try:
            async with self.core.get_session() as session:
                session.add(product)
                await session.flush()  # Use flush to get the ID before commit
                await session.refresh(product)
                return Success(product)
        except sa.exc.IntegrityError:
            # Handles cases like duplicate SKU
            return Failure("Product with this SKU already exists.")
        except Exception as e:
            return Failure(f"Database error creating product: {e}")

    async def update_product(self, product: Product) -> Result[Product, str]:
        """Updates an existing product instance in the database."""
        try:
            async with self.core.get_session() as session:
                session.add(product) # Add to session to track changes
                await session.flush()
                await session.refresh(product)
                return Success(product)
        except Exception as e:
            return Failure(f"Database error updating product: {e}")

```

# app/services/sales_service.py
```py
# File: app/services/sales_service.py
"""Data Access Service (Repository) for Sales entities."""
from __future__ import annotations
from typing import TYPE_CHECKING
import sqlalchemy as sa

from app.core.result import Result, Success, Failure
from app.models.sales import SalesTransaction
from app.services.base_service import BaseService

if TYPE_CHECKING:
    from app.core.application_core import ApplicationCore
    from sqlalchemy.ext.asyncio import AsyncSession

class SalesService(BaseService):
    """
    Handles all database interactions for sales-related models.
    It encapsulates the atomic persistence of SalesTransaction and its related entities.
    """

    def __init__(self, core: "ApplicationCore"):
        super().__init__(core, SalesTransaction)

    async def create_full_transaction(self, transaction: SalesTransaction, session: AsyncSession) -> Result[SalesTransaction, str]:
        """
        Saves a complete SalesTransaction object, including its items and payments,
        within a provided session. This ensures the operation is part of a larger, atomic transaction.
        Args:
            transaction: The complete SalesTransaction ORM instance to save.
            session: The active SQLAlchemy AsyncSession from the calling manager.
        Returns:
            A Success containing the saved SalesTransaction, or a Failure with an error.
        """
        try:
            # The session is managed by the calling manager's `get_session` context.
            # `session.add(transaction)` automatically adds related objects (items, payments)
            # if relationships are configured with cascade="all, delete-orphan"
            session.add(transaction)
            await session.flush() # Flush to get any generated IDs (like transaction_id)
            await session.refresh(transaction) # Refresh the transaction instance to get generated fields

            # If related items/payments have defaults or triggers, they might need refreshing too
            for item in transaction.items:
                await session.refresh(item)
            for payment in transaction.payments:
                await session.refresh(payment)
                
            return Success(transaction)
        except sa.exc.IntegrityError as e:
            return Failure(f"Data integrity error creating sales transaction: {e.orig}")
        except Exception as e:
            return Failure(f"Database error saving full transaction: {e}")

    # TODO: Add methods to retrieve sales transactions by various criteria (e.g., date range, customer, number)

```

# app/core/result.py
```py
# File: app/core/result.py
"""
Defines the Result pattern for explicit error handling.

This module provides a functional approach to error handling, avoiding the use
of exceptions for predictable business logic failures. All service and manager
methods should return a Result object.
"""
from typing import TypeVar, Generic, Union, Optional, final
from dataclasses import dataclass

# Generic TypeVars for Success (T) and Failure (E) values.
T = TypeVar('T')
E = TypeVar('E')

@final
@dataclass(frozen=True)
class Success(Generic[T]):
    """Represents a successful operation with a return value."""
    value: T

@final
@dataclass(frozen=True)
class Failure(Generic[E]):
    """Represents a failed operation with an error object."""
    error: E

# The Result type is a union of a Success or a Failure.
Result = Union[Success[T], Failure[E]]

```

# app/core/__init__.py
```py

```

# app/core/exceptions.py
```py
# File: app/core/exceptions.py
"""
Defines custom exception classes for the application.

While the Result pattern is used for predictable business errors, exceptions
are still used for unexpected, catastrophic system failures (e.g., database
is unreachable, configuration is missing).
"""

class CoreException(Exception):
    """Base exception for all application-specific errors."""
    pass

class ConfigurationError(CoreException):
    """Raised when there is an error in the application configuration."""
    pass

class DatabaseConnectionError(CoreException):
    """Raised when the application cannot connect to the database."""
    pass

class AsyncBridgeError(CoreException):
    """Raised when there is an error in the asynchronous bridge setup or operation."""
    pass

# TODO: Add more specific exceptions as needed for different domains (e.g., SalesError, InventoryError)
# These would typically be subclasses of a higher-level business exception,
# distinct from CoreException. For example:
# class BusinessError(CoreException): pass
# class InsufficientStockError(BusinessError): pass

```

# app/core/config.py
```py
# File: app/core/config.py
"""
Manages all application configuration.

This module uses Pydantic's BaseSettings to provide a strongly-typed configuration
model that loads settings from environment variables and a .env file. This ensures
that all configuration is validated at startup.
"""
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict # Use pydantic_settings for newer Pydantic versions

class Settings(BaseSettings):
    """
    Application settings model.
    Pydantic automatically reads values from environment variables or a .env file.
    The names are case-insensitive.
    """
    model_config = SettingsConfigDict(
        env_file='.env.dev', # Specifies the env file to load for local development.
        env_file_encoding='utf-8',
        extra='ignore' # Allow extra environment variables not defined in the model
    )

    # Database Configuration
    DATABASE_URL: str = Field(..., description="PostgreSQL database connection URL")

    # Application-level settings
    APP_ENV: str = Field("development", description="Application environment (e.g., 'development', 'production')")
    DEBUG: bool = Field(True, description="Enable debug mode (e.g., SQLAlchemy echoing)")
    LOG_LEVEL: str = Field("DEBUG", description="Logging level (e.g., 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')")
    SECRET_KEY: str = Field(..., description="Secret key for security purposes (e.g., session management, hashing)")

    # Context IDs for current company/outlet/user (for development/testing convenience)
    # In production, these would be derived from authentication/session.
    CURRENT_COMPANY_ID: str = Field("00000000-0000-0000-0000-000000000001", description="Placeholder for current company UUID")
    CURRENT_OUTLET_ID: str = Field("00000000-0000-0000-0000-000000000002", description="Placeholder for current outlet UUID")
    CURRENT_USER_ID: str = Field("00000000-0000-0000-0000-000000000003", description="Placeholder for current user UUID")

# Create a single, importable instance of the settings.
# The application will import this `settings` object to access configuration.
settings = Settings()

```

# app/core/async_bridge.py
```py
# File: app/core/async_bridge.py
"""
Provides a robust, thread-safe bridge between the PySide6 (Qt) event loop
and the asyncio event loop. This prevents UI freezes during I/O-bound operations.
"""
import asyncio
import threading
from typing import Coroutine, Any, Callable, Optional
import inspect
import sys
from concurrent.futures import Future

from PySide6.QtCore import QObject, QThread, Signal, Slot
from PySide6.QtWidgets import QApplication

from app.core.exceptions import AsyncBridgeError

class AsyncWorker(QObject):
    """
    An object that lives in a QThread and runs an asyncio event loop.
    It accepts coroutines for execution and signals results back to the main thread.
    """
    # FIX: A new signal specifically to carry the callback and its results
    # This is the key to safe, cross-thread callback invocation.
    callback_ready = Signal(object, object, object)

    def __init__(self, loop: asyncio.AbstractEventLoop, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._loop = loop
        self._tasks = set()

    def stop(self, final_coro: Optional[Coroutine] = None):
        """Gracefully stops the asyncio event loop, optionally running one final coroutine."""
        if self._loop.is_running():
            async def _stop_coro():
                if final_coro:
                    try:
                        await final_coro
                    except Exception as e:
                        print(f"Error during final shutdown coroutine: {e}", file=sys.stderr)
                
                tasks = [task for task in self._tasks if not task.done()]
                for task in tasks:
                    task.cancel()
                await asyncio.gather(*tasks, return_exceptions=True)
                self._loop.stop()

            self._loop.call_soon_threadsafe(lambda: asyncio.create_task(_stop_coro()))

    def run_task(self, coro: Coroutine[Any, Any, Any], on_done_callback: Optional[Callable] = None):
        """Submits a fire-and-forget coroutine to be run on the event loop."""
        if not inspect.iscoroutine(coro):
            raise TypeError("Input must be a coroutine.")
        
        def _task_wrapper():
            task = self._loop.create_task(coro)
            self._tasks.add(task)
            task.add_done_callback(lambda fut: self._on_task_completed(fut, on_done_callback))
            task.add_done_callback(lambda fut: self._tasks.discard(fut))

        self._loop.call_soon_threadsafe(_task_wrapper)

    def run_task_and_wait(self, coro: Coroutine) -> Any:
        """Submits a coroutine and blocks until it returns a result."""
        if not self._loop.is_running():
            raise AsyncBridgeError("Cannot run task: event loop is not running.")
        
        future = asyncio.run_coroutine_threadsafe(coro, self._loop)
        return future.result()

    def _on_task_completed(self, fut: asyncio.Future, on_done_callback: Optional[Callable]):
        result, error = None, None
        try:
            result = fut.result()
        except asyncio.CancelledError:
            error = AsyncBridgeError("Task was cancelled.")
        except Exception as e:
            error = e
        
        if on_done_callback:
            # FIX: Emit a signal containing the callback and its arguments.
            # This is thread-safe and lets the main thread execute the callback.
            self.callback_ready.emit(on_done_callback, result, error)

class AsyncWorkerThread(QThread):
    """A QThread that manages an asyncio event loop and an AsyncWorker."""
    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self.worker: Optional[AsyncWorker] = None
        self._thread_started_event = threading.Event()

    def run(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.worker = AsyncWorker(self.loop)
        # The worker's signals will be connected from the main thread after it starts.
        self._thread_started_event.set()
        self.loop.run_forever()
        self.loop.close()

    def start_and_wait(self):
        if self.isRunning(): return
        self._thread_started_event.clear()
        self.start()
        if not self._thread_started_event.wait(timeout=5):
            raise AsyncBridgeError("AsyncWorkerThread failed to start event loop in time.")

    def stop_and_wait(self, final_coro: Optional[Coroutine] = None):
        if not self.isRunning() or not self.worker: return
        self.worker.stop(final_coro)
        if not self.wait(5000):
            print("Warning: AsyncWorkerThread did not terminate gracefully.", file=sys.stderr)
            self.terminate()

```

# app/core/application_core.py
```py
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

```

# app/models/customer.py
```py
# File: app/models/customer.py
"""SQLAlchemy models for Customer entities."""
import uuid
import sqlalchemy as sa
from sqlalchemy import Column, String, Boolean, ForeignKey, Numeric, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin

class Customer(Base, TimestampMixin):
    __tablename__ = "customers"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.companies.id", ondelete="RESTRICT"), nullable=False, index=True)
    customer_code = Column(String(50), nullable=False)
    name = Column(String(255), nullable=False)
    email = Column(String(255))
    phone = Column(String(50))
    address = Column(Text)
    loyalty_points = Column(Integer, nullable=False, default=0)
    credit_limit = Column(Numeric(19, 2), nullable=False, default=0)
    is_active = Column(Boolean, nullable=False, default=True)
    company = relationship("Company", back_populates="customers")
    sales_transactions = relationship("SalesTransaction", back_populates="customer")
    __table_args__ = (sa.UniqueConstraint('company_id', 'customer_code', name='uq_customer_company_code'), sa.UniqueConstraint('company_id', 'email', name='uq_customer_company_email'))

```

# app/models/__init__.py
```py
# File: app/models/__init__.py
"""
Models Package Initialization

This file makes the `app/models` directory a Python package and conveniently
imports all ORM model classes into its namespace. This allows for cleaner imports
in other parts of the application (e.g., `from app.models import Product`).
"""
from .base import Base, TimestampMixin
from .company import Company, Outlet
from .user import User, Role, Permission, RolePermission, UserRole
from .product import Category, Supplier, Product, ProductVariant
from .inventory import Inventory, StockMovement, PurchaseOrder, PurchaseOrderItem
from .customer import Customer
from .sales import SalesTransaction, SalesTransactionItem, PaymentMethod, Payment
from .accounting import ChartOfAccount, JournalEntry, JournalEntryLine
from .audit_log import AuditLog

__all__ = [
    "Base",
    "TimestampMixin",
    "Company",
    "Outlet",
    "User",
    "Role",
    "Permission",
    "RolePermission",
    "UserRole",
    "Category",
    "Supplier",
    "Product",
    "ProductVariant",
    "Inventory",
    "StockMovement",
    "PurchaseOrder",
    "PurchaseOrderItem",
    "Customer",
    "SalesTransaction",
    "SalesTransactionItem",
    "PaymentMethod",
    "Payment",
    "ChartOfAccount",
    "JournalEntry",
    "JournalEntryLine",
    "AuditLog",
]

```

# app/models/product.py
```py
# File: app/models/product.py
"""SQLAlchemy models for Product and Category entities, and Product Variants and Suppliers."""
import uuid
from decimal import Decimal
import sqlalchemy as sa
from sqlalchemy import Column, String, Boolean, ForeignKey, Numeric, DateTime, Text, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin

class Category(Base, TimestampMixin):
    __tablename__ = "categories"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.companies.id", ondelete="RESTRICT"), nullable=False, index=True)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.categories.id", ondelete="SET NULL"), nullable=True)
    name = Column(String(255), nullable=False)
    company = relationship("Company")
    products = relationship("Product", back_populates="category")
    parent = relationship("Category", remote_side=[id], backref="children")
    __table_args__ = (sa.UniqueConstraint('company_id', 'name', name='uq_category_company_name'),)

class Supplier(Base, TimestampMixin):
    __tablename__ = "suppliers"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.companies.id", ondelete="RESTRICT"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    contact_person = Column(String(255))
    email = Column(String(255))
    phone = Column(String(50))
    address = Column(Text)
    is_active = Column(Boolean, nullable=False, default=True)
    company = relationship("Company", back_populates="suppliers")
    products = relationship("Product", back_populates="supplier") 
    purchase_orders = relationship("PurchaseOrder", back_populates="supplier", cascade="all, delete-orphan")
    __table_args__ = (sa.UniqueConstraint('company_id', 'name', name='uq_supplier_company_name'),)

class Product(Base, TimestampMixin):
    __tablename__ = "products"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.companies.id", ondelete="RESTRICT"), nullable=False, index=True)
    category_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.categories.id"), nullable=True, index=True)
    supplier_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.suppliers.id"), nullable=True, index=True)
    sku = Column(String(100), nullable=False)
    barcode = Column(String(100), index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    cost_price = Column(Numeric(19, 4), nullable=False, default=0)
    selling_price = Column(Numeric(19, 4), nullable=False)
    gst_rate = Column(Numeric(5, 2), nullable=False, default=Decimal("9.00")) # FIX: Updated GST Rate
    track_inventory = Column(Boolean, nullable=False, default=True)
    reorder_point = Column(Integer, nullable=False, default=0)
    is_active = Column(Boolean, nullable=False, default=True)
    company = relationship("Company", back_populates="products")
    category = relationship("Category", back_populates="products")
    supplier = relationship("Supplier", back_populates="products")
    product_variants = relationship("ProductVariant", back_populates="product", cascade="all, delete-orphan")
    inventory_items = relationship("Inventory", back_populates="product", cascade="all, delete-orphan")
    sales_transaction_items = relationship("SalesTransactionItem", back_populates="product", cascade="all, delete-orphan")
    purchase_order_items = relationship("PurchaseOrderItem", back_populates="product", cascade="all, delete-orphan")
    stock_movements = relationship("StockMovement", back_populates="product", cascade="all, delete-orphan")
    __table_args__ = (sa.UniqueConstraint('company_id', 'sku', name='uq_product_company_sku'),)

class ProductVariant(Base, TimestampMixin):
    __tablename__ = "product_variants"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.products.id", ondelete="CASCADE"), nullable=False, index=True)
    sku_suffix = Column(String(100), nullable=False)
    barcode = Column(String(100))
    attributes = Column(JSONB, nullable=False)
    cost_price_override = Column(Numeric(19, 4))
    selling_price_override = Column(Numeric(19, 4))
    is_active = Column(Boolean, nullable=False, default=True)
    product = relationship("Product", back_populates="product_variants")
    inventory_items = relationship("Inventory", back_populates="variant", cascade="all, delete-orphan")
    sales_transaction_items = relationship("SalesTransactionItem", back_populates="variant", cascade="all, delete-orphan")
    stock_movements = relationship("StockMovement", back_populates="variant", cascade="all, delete-orphan")
    purchase_order_items = relationship("PurchaseOrderItem", back_populates="variant", cascade="all, delete-orphan")
    __table_args__ = (sa.UniqueConstraint('product_id', 'sku_suffix', name='uq_product_variant_sku_suffix'),)

```

# app/models/base.py
```py
# File: app/models/base.py
"""
Defines the base for all SQLAlchemy ORM models.
Includes a mixin for common timestamp columns.
"""
from datetime import datetime
from sqlalchemy import MetaData, Column, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

# It's good practice to use a naming convention for constraints.
# This helps in generating consistent constraint names in the database.
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

# IMPORTANT: Specify the schema here. All tables defined using this Base will
# automatically belong to the 'sgpos' schema.
metadata = MetaData(naming_convention=convention, schema="sgpos")
Base = declarative_base(metadata=metadata)

class TimestampMixin:
    """Mixin to add created_at and updated_at columns to a model."""
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        doc="Timestamp when the record was created (UTC)"
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(), # Automatically updates on record modification
        nullable=False,
        doc="Timestamp when the record was last updated (UTC)"
    )

```

# app/models/company.py
```py
# File: app/models/company.py
"""SQLAlchemy models for Company and Outlet entities."""
import uuid
from datetime import date
import sqlalchemy as sa
from sqlalchemy import Column, String, Boolean, ForeignKey, Text, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin

class Company(Base, TimestampMixin):
    """
    Represents a company (multi-tenancy root).
    Each company owns its own data within the system.
    """
    __tablename__ = "companies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, doc="Unique identifier for the company")
    name = Column(String(255), nullable=False, doc="Legal name of the company")
    registration_number = Column(String(20), unique=True, nullable=False, doc="Singapore UEN (Unique Entity Number)")
    gst_registration_number = Column(String(20), unique=True, doc="GST registration number (optional)")
    address = Column(Text, doc="Company's primary address")
    phone = Column(String(20), doc="Company's primary phone number")
    email = Column(String(255), doc="Company's primary email address")
    base_currency = Column(String(3), nullable=False, default='SGD', doc="Base currency for financial transactions")
    fiscal_year_start = Column(Date, doc="Start date of the company's fiscal year")
    is_active = Column(Boolean, nullable=False, default=True, doc="Indicates if the company account is active")
    
    # Relationships
    outlets = relationship("Outlet", back_populates="company", cascade="all, delete-orphan", doc="Outlets belonging to this company")
    users = relationship("User", back_populates="company", cascade="all, delete-orphan", doc="Users associated with this company")
    roles = relationship("Role", back_populates="company", cascade="all, delete-orphan", doc="Roles defined by this company")
    products = relationship("Product", back_populates="company", cascade="all, delete-orphan", doc="Products defined by this company")
    customers = relationship("Customer", back_populates="company", cascade="all, delete-orphan", doc="Customers of this company")
    suppliers = relationship("Supplier", back_populates="company", cascade="all, delete-orphan", doc="Suppliers for this company")
    sales_transactions = relationship("SalesTransaction", back_populates="company", cascade="all, delete-orphan", doc="Sales transactions by this company")
    payment_methods = relationship("PaymentMethod", back_populates="company", cascade="all, delete-orphan", doc="Payment methods configured by this company")
    stock_movements = relationship("StockMovement", back_populates="company", cascade="all, delete-orphan", doc="Stock movements recorded by this company")
    chart_of_accounts = relationship("ChartOfAccount", back_populates="company", cascade="all, delete-orphan", doc="Chart of accounts for this company")
    journal_entries = relationship("JournalEntry", back_populates="company", cascade="all, delete-orphan", doc="Journal entries for this company")
    audit_logs = relationship("AuditLog", back_populates="company", doc="Audit logs related to this company")

class Outlet(Base, TimestampMixin):
    """Represents a physical retail outlet or store."""
    __tablename__ = "outlets"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, doc="Unique identifier for the outlet")
    company_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.companies.id", ondelete="RESTRICT"), nullable=False, index=True, doc="Foreign key to the owning company")
    code = Column(String(50), nullable=False, doc="Unique code for the outlet within the company")
    name = Column(String(255), nullable=False, doc="Name of the outlet")
    address = Column(Text, doc="Physical address of the outlet")
    phone = Column(String(20), doc="Contact phone number for the outlet")
    is_active = Column(Boolean, nullable=False, default=True, doc="Indicates if the outlet is active")

    # Relationships
    company = relationship("Company", back_populates="outlets", doc="The company this outlet belongs to")
    inventory_items = relationship("Inventory", back_populates="outlet", cascade="all, delete-orphan", doc="Inventory items currently in this outlet")
    sales_transactions = relationship("SalesTransaction", back_populates="outlet", cascade="all, delete-orphan", doc="Sales transactions made at this outlet")
    stock_movements = relationship("StockMovement", back_populates="outlet", cascade="all, delete-orphan", doc="Stock movements recorded at this outlet")
    purchase_orders = relationship("PurchaseOrder", back_populates="outlet", cascade="all, delete-orphan", doc="Purchase orders related to this outlet")
    
    __table_args__ = (
        sa.UniqueConstraint('company_id', 'code', name='uq_outlet_company_code'),
    )

```

# app/models/accounting.py
```py
# File: app/models/accounting.py
"""SQLAlchemy models for core Accounting entities."""
import uuid
from datetime import date, datetime
import sqlalchemy as sa
from sqlalchemy import Column, String, Boolean, ForeignKey, Numeric, DateTime, Text, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, foreign
from app.models.base import Base, TimestampMixin

class ChartOfAccount(Base, TimestampMixin):
    __tablename__ = "chart_of_accounts"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.companies.id"), nullable=False, index=True)
    account_code = Column(String(20), nullable=False)
    account_name = Column(String(255), nullable=False)
    account_type = Column(String(50), nullable=False)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.chart_of_accounts.id"))
    is_active = Column(Boolean, nullable=False, default=True)
    company = relationship("Company", back_populates="chart_of_accounts")
    parent_account = relationship("ChartOfAccount", remote_side=[id], backref="children_accounts")
    journal_entry_lines = relationship("JournalEntryLine", back_populates="account")
    __table_args__ = (sa.UniqueConstraint('company_id', 'account_code', name='uq_coa_company_code'), sa.CheckConstraint("account_type IN ('ASSET', 'LIABILITY', 'EQUITY', 'REVENUE', 'EXPENSE')", name="chk_account_type"))

class JournalEntry(Base, TimestampMixin):
    __tablename__ = "journal_entries"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.companies.id"), nullable=False, index=True)
    entry_number = Column(String(50), nullable=False)
    entry_date = Column(Date, nullable=False)
    description = Column(Text)
    reference_type = Column(String(50))
    reference_id = Column(UUID(as_uuid=True))
    status = Column(String(20), nullable=False, default='POSTED')
    created_by_user_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.users.id"), nullable=False, index=True)
    company = relationship("Company", back_populates="journal_entries")
    created_by_user = relationship("User", back_populates="journal_entries_created")
    journal_entry_lines = relationship("JournalEntryLine", back_populates="journal_entry", cascade="all, delete-orphan")
    # FIX: Corrected foreign_keys and primaryjoin syntax
    sales_transaction = relationship(
        "SalesTransaction",
        primaryjoin="and_(foreign(JournalEntry.reference_id) == SalesTransaction.id, JournalEntry.reference_type == 'SALE')",
        back_populates="journal_entries",
        uselist=False, # A journal entry can only link to one sale
        viewonly=True
    )
    __table_args__ = (sa.UniqueConstraint('company_id', 'entry_number', name='uq_journal_entry_company_number'), sa.CheckConstraint("status IN ('DRAFT', 'POSTED', 'VOID')", name="chk_journal_entry_status"))

class JournalEntryLine(Base, TimestampMixin):
    __tablename__ = "journal_entry_lines"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    journal_entry_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.journal_entries.id", ondelete="CASCADE"), nullable=False, index=True)
    account_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.chart_of_accounts.id"), nullable=False, index=True)
    debit_amount = Column(Numeric(19, 2), nullable=False, default=0)
    credit_amount = Column(Numeric(19, 2), nullable=False, default=0)
    description = Column(Text)
    journal_entry = relationship("JournalEntry", back_populates="journal_entry_lines")
    account = relationship("ChartOfAccount", back_populates="journal_entry_lines")
    __table_args__ = (sa.CheckConstraint("(debit_amount >= 0 AND credit_amount >= 0) AND (debit_amount != credit_amount)", name="debit_or_credit_check"),)

```

# app/models/sales.py
```py
# File: app/models/sales.py
"""SQLAlchemy models for Sales Transactions, Sales Items, and Payments."""
import uuid
from datetime import datetime
import sqlalchemy as sa
from sqlalchemy import Column, String, Boolean, ForeignKey, Numeric, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin

class SalesTransaction(Base, TimestampMixin):
    __tablename__ = "sales_transactions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.companies.id", ondelete="RESTRICT"), nullable=False, index=True)
    outlet_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.outlets.id"), nullable=False, index=True)
    transaction_number = Column(String(50), nullable=False)
    transaction_date = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.customers.id"), nullable=True, index=True)
    cashier_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.users.id"), nullable=False, index=True)
    subtotal = Column(Numeric(19, 2), nullable=False)
    tax_amount = Column(Numeric(19, 2), nullable=False)
    discount_amount = Column(Numeric(19, 2), nullable=False, default=0)
    rounding_adjustment = Column(Numeric(19, 2), nullable=False, default=0)
    total_amount = Column(Numeric(19, 2), nullable=False)
    status = Column(String(20), nullable=False)
    notes = Column(Text)
    company = relationship("Company", back_populates="sales_transactions")
    outlet = relationship("Outlet", back_populates="sales_transactions")
    customer = relationship("Customer", back_populates="sales_transactions")
    cashier = relationship("User", back_populates="sales_transactions")
    items = relationship("SalesTransactionItem", back_populates="sales_transaction", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="sales_transaction", cascade="all, delete-orphan")
    # FIX: Add explicit primaryjoin to tell SQLAlchemy how to link this to JournalEntry
    journal_entries = relationship(
        "JournalEntry",
        primaryjoin="and_(SalesTransaction.id == foreign(JournalEntry.reference_id), JournalEntry.reference_type == 'SALE')",
        back_populates="sales_transaction",
        viewonly=True  # Usually a good idea for such reverse relationships to prevent accidental modifications
    )
    __table_args__ = (sa.UniqueConstraint('company_id', 'transaction_number', name='uq_sales_transaction_company_number'), sa.CheckConstraint("status IN ('COMPLETED', 'VOIDED', 'HELD')", name="chk_sales_transaction_status"))

class SalesTransactionItem(Base):
    __tablename__ = "sales_transaction_items"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sales_transaction_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.sales_transactions.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.products.id"), nullable=False, index=True)
    variant_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.product_variants.id"), nullable=True, index=True)
    quantity = Column(Numeric(15, 4), nullable=False)
    unit_price = Column(Numeric(19, 4), nullable=False)
    cost_price = Column(Numeric(19, 4), nullable=False)
    line_total = Column(Numeric(19, 2), nullable=False)
    sales_transaction = relationship("SalesTransaction", back_populates="items")
    product = relationship("Product", back_populates="sales_transaction_items")
    variant = relationship("ProductVariant", back_populates="sales_transaction_items")
    __table_args__ = (sa.UniqueConstraint('sales_transaction_id', 'product_id', 'variant_id', name='uq_sales_item_transaction_product_variant'),)

class PaymentMethod(Base, TimestampMixin):
    __tablename__ = "payment_methods"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.companies.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    type = Column(String(50), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    company = relationship("Company", back_populates="payment_methods")
    payments = relationship("Payment", back_populates="payment_method")
    __table_args__ = (sa.UniqueConstraint('company_id', 'name', name='uq_payment_methods_company_name'), sa.CheckConstraint("type IN ('CASH', 'CARD', 'NETS', 'PAYNOW', 'VOUCHER', 'STORE_CREDIT')", name="chk_payment_method_type"))

class Payment(Base):
    __tablename__ = "payments"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sales_transaction_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.sales_transactions.id", ondelete="CASCADE"), nullable=False, index=True)
    payment_method_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.payment_methods.id"), nullable=False, index=True)
    amount = Column(Numeric(19, 2), nullable=False)
    reference_number = Column(String(100))
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    sales_transaction = relationship("SalesTransaction", back_populates="payments")
    payment_method = relationship("PaymentMethod", back_populates="payments")

```

# app/models/inventory.py
```py
# File: app/models/inventory.py
"""SQLAlchemy models for Inventory, Stock Movements, and Purchase Orders."""
import uuid
from datetime import datetime
import sqlalchemy as sa
from sqlalchemy import Column, String, Boolean, ForeignKey, Numeric, DateTime, Text, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin

class Inventory(Base, TimestampMixin):
    __tablename__ = "inventory"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    outlet_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.outlets.id", ondelete="RESTRICT"), nullable=False, index=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.products.id", ondelete="RESTRICT"), nullable=False, index=True)
    variant_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.product_variants.id", ondelete="RESTRICT"), nullable=True, index=True)
    quantity_on_hand = Column(Numeric(15, 4), nullable=False, default=0)
    outlet = relationship("Outlet", back_populates="inventory_items")
    product = relationship("Product", back_populates="inventory_items")
    variant = relationship("ProductVariant", back_populates="inventory_items")
    __table_args__ = (sa.UniqueConstraint('outlet_id', 'product_id', 'variant_id', name='uq_inventory_outlet_product_variant'),)

class StockMovement(Base):
    __tablename__ = "stock_movements"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.companies.id"), nullable=False, index=True)
    outlet_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.outlets.id"), nullable=False, index=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.products.id"), nullable=False, index=True)
    variant_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.product_variants.id"), nullable=True, index=True)
    movement_type = Column(String(50), nullable=False)
    quantity_change = Column(Numeric(15, 4), nullable=False)
    reference_id = Column(UUID(as_uuid=True))
    reference_type = Column(String(50)) # Added reference_type from schema
    notes = Column(Text)
    created_by_user_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.users.id"), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    company = relationship("Company", back_populates="stock_movements")
    outlet = relationship("Outlet", back_populates="stock_movements")
    product = relationship("Product", back_populates="stock_movements")
    variant = relationship("ProductVariant", back_populates="stock_movements")
    user = relationship("User", back_populates="stock_movements_created")
    __table_args__ = (sa.CheckConstraint("movement_type IN ('SALE', 'RETURN', 'PURCHASE', 'ADJUSTMENT_IN', 'ADJUSTMENT_OUT', 'TRANSFER_IN', 'TRANSFER_OUT')", name="chk_stock_movement_type"),)

class PurchaseOrder(Base, TimestampMixin):
    __tablename__ = "purchase_orders"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.companies.id"), nullable=False, index=True)
    outlet_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.outlets.id"), nullable=False, index=True)
    supplier_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.suppliers.id"), nullable=False, index=True)
    po_number = Column(String(50), nullable=False)
    order_date = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    expected_delivery_date = Column(DateTime(timezone=True))
    status = Column(String(20), nullable=False, default='DRAFT')
    notes = Column(Text)
    total_amount = Column(Numeric(19, 2), nullable=False, default=0)
    outlet = relationship("Outlet", back_populates="purchase_orders")
    supplier = relationship("Supplier", back_populates="purchase_orders")
    items = relationship("PurchaseOrderItem", back_populates="purchase_order", cascade="all, delete-orphan")
    __table_args__ = (sa.UniqueConstraint('company_id', 'po_number', name='uq_purchase_order_company_po_number'), sa.CheckConstraint("status IN ('DRAFT', 'SENT', 'PARTIALLY_RECEIVED', 'RECEIVED', 'CANCELLED')", name="chk_purchase_order_status"))

class PurchaseOrderItem(Base, TimestampMixin):
    __tablename__ = "purchase_order_items"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    purchase_order_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.purchase_orders.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.products.id"), nullable=False, index=True)
    variant_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.product_variants.id"), nullable=True, index=True)
    quantity_ordered = Column(Numeric(15, 4), nullable=False)
    quantity_received = Column(Numeric(15, 4), nullable=False, default=0)
    unit_cost = Column(Numeric(19, 4), nullable=False)
    purchase_order = relationship("PurchaseOrder", back_populates="items")
    product = relationship("Product", back_populates="purchase_order_items")
    variant = relationship("ProductVariant", back_populates="purchase_order_items")
    __table_args__ = (sa.UniqueConstraint('purchase_order_id', 'product_id', 'variant_id', name='uq_po_item_po_product_variant'),)

```

# app/models/user.py
```py
# File: app/models/user.py
"""SQLAlchemy models for User, Role, and Permission entities."""
import uuid
from datetime import datetime
import sqlalchemy as sa
from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin

class User(Base, TimestampMixin):
    """Represents a user (employee) of the SG-POS system."""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, doc="Unique identifier for the user")
    company_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.companies.id", ondelete="RESTRICT"), nullable=False, index=True, doc="Foreign key to the owning company")
    username = Column(String(100), nullable=False, doc="Unique username for login")
    email = Column(String(255), nullable=False, doc="User's email address")
    password_hash = Column(String(255), nullable=False, doc="Hashed password using bcrypt")
    full_name = Column(String(255), doc="User's full name")
    is_active = Column(Boolean, nullable=False, default=True, doc="Indicates if the user account is active")
    last_login_at = Column(DateTime(timezone=True), doc="Timestamp of the user's last successful login")
    
    # Relationships
    company = relationship("Company", back_populates="users", doc="The company this user belongs to")
    user_roles = relationship("UserRole", back_populates="user", cascade="all, delete-orphan", doc="Roles assigned to this user")
    sales_transactions = relationship("SalesTransaction", back_populates="cashier", doc="Sales transactions processed by this user")
    stock_movements_created = relationship("StockMovement", back_populates="user", doc="Stock movements created by this user")
    journal_entries_created = relationship("JournalEntry", back_populates="created_by_user", doc="Journal entries created by this user")
    audit_logs = relationship("AuditLog", back_populates="user", doc="Audit logs associated with this user")

    __table_args__ = (
        sa.UniqueConstraint('company_id', 'username', name='uq_user_company_username'),
        sa.UniqueConstraint('company_id', 'email', name='uq_user_company_email')
    )

class Role(Base):
    """Defines user roles (e.g., Admin, Manager, Cashier)."""
    __tablename__ = "roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, doc="Unique identifier for the role")
    company_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.companies.id", ondelete="RESTRICT"), nullable=False, doc="Foreign key to the owning company")
    name = Column(String(50), nullable=False, doc="Name of the role (unique per company)")
    description = Column(Text, doc="Description of the role's responsibilities")
    is_system_role = Column(Boolean, nullable=False, default=False, doc="True for built-in roles that cannot be deleted or modified by users")
    
    # Relationships
    company = relationship("Company", back_populates="roles", doc="The company this role belongs to")
    role_permissions = relationship("RolePermission", back_populates="role", cascade="all, delete-orphan", doc="Permissions assigned to this role")
    user_roles = relationship("UserRole", back_populates="role", cascade="all, delete-orphan", doc="Users assigned to this role")

    __table_args__ = (
        sa.UniqueConstraint('company_id', 'name', name='uq_role_company_name'),
    )

class Permission(Base):
    """Defines granular permissions within the system."""
    __tablename__ = "permissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, doc="Unique identifier for the permission")
    action = Column(String(100), nullable=False, doc="The action permitted (e.g., 'CREATE', 'READ', 'UPDATE', 'DELETE')")
    resource = Column(String(100), nullable=False, doc="The resource or module the action applies to (e.g., 'PRODUCT', 'SALE_TRANSACTION')")
    description = Column(Text, doc="Description of what this permission allows")

    # Relationships
    role_permissions = relationship("RolePermission", back_populates="permission", cascade="all, delete-orphan", doc="Roles that have this permission")

    __table_args__ = (
        sa.UniqueConstraint('action', 'resource', name='uq_permission_action_resource'),
    )

class RolePermission(Base):
    """Junction table linking roles to their permissions."""
    __tablename__ = "role_permissions"

    role_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.roles.id", ondelete="CASCADE"), primary_key=True, doc="Foreign key to the role")
    permission_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.permissions.id", ondelete="CASCADE"), primary_key=True, doc="Foreign key to the permission")

    # Relationships
    role = relationship("Role", back_populates="role_permissions", doc="The role associated with this permission")
    permission = relationship("Permission", back_populates="role_permissions", doc="The permission associated with this role")

class UserRole(Base):
    """Assigns roles to users, potentially on a per-outlet basis."""
    __tablename__ = "user_roles"

    user_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.users.id", ondelete="CASCADE"), primary_key=True, doc="Foreign key to the user")
    role_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.roles.id", ondelete="CASCADE"), primary_key=True, doc="Foreign key to the role")
    outlet_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.outlets.id", ondelete="CASCADE"), primary_key=True, doc="Foreign key to the assigned outlet (part of composite PK)")

    # Relationships
    user = relationship("User", back_populates="user_roles", doc="The user assigned to this role")
    role = relationship("Role", back_populates="user_roles", doc="The role assigned to this user")
    outlet = relationship("Outlet", doc="The outlet this role assignment is specific to")

```

# app/models/audit_log.py
```py
# File: app/models/audit_log.py
"""SQLAlchemy model for the Audit Logs."""
import uuid
from datetime import datetime
import sqlalchemy as sa
from sqlalchemy import Column, String, ForeignKey, DateTime, Text, BigInteger
from sqlalchemy.dialects.postgresql import UUID, INET, JSONB
from sqlalchemy.orm import relationship
from app.models.base import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(BigInteger, primary_key=True)
    company_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.companies.id"), index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.users.id", ondelete="SET NULL"), nullable=True, index=True)
    action = Column(String(50), nullable=False)
    table_name = Column(String(100), nullable=False)
    record_id = Column(UUID(as_uuid=True), nullable=False)
    old_values = Column(JSONB)
    new_values = Column(JSONB)
    ip_address = Column(INET)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    company = relationship("Company", back_populates="audit_logs")
    user = relationship("User", back_populates="audit_logs")

```

# app/business_logic/__init__.py
```py

```

# app/business_logic/managers/inventory_manager.py
```py
# File: app/business_logic/managers/inventory_manager.py
"""Business Logic Manager for orchestrating Inventory operations."""
from __future__ import annotations
from typing import TYPE_CHECKING, List, Dict, Any, Optional
from uuid import UUID
from decimal import Decimal
import uuid as uuid_pkg

from app.core.result import Result, Success, Failure
from app.business_logic.managers.base_manager import BaseManager
from app.business_logic.dto.inventory_dto import (
    StockAdjustmentDTO, PurchaseOrderCreateDTO, PurchaseOrderDTO,
    InventorySummaryDTO, StockMovementDTO, SupplierDTO, PurchaseOrderItemDTO
)
from app.models.inventory import StockMovement, PurchaseOrder, PurchaseOrderItem
from app.models.product import Product
from sqlalchemy.orm import selectinload

if TYPE_CHECKING:
    from app.core.application_core import ApplicationCore
    from app.services.inventory_service import InventoryService
    from app.services.product_service import ProductService
    from app.services.supplier_service import SupplierService
    from app.services.purchase_order_service import PurchaseOrderService
    from app.services.user_service import UserService
    from app.services.company_service import OutletService
    from sqlalchemy.ext.asyncio import AsyncSession


class InventoryManager(BaseManager):
    """Handles high-level inventory workflows like stock takes, adjustments, and purchase orders."""
    
    @property
    def inventory_service(self) -> "InventoryService": return self.core.inventory_service
    @property
    def product_service(self) -> "ProductService": return self.core.product_service
    @property
    def supplier_service(self) -> "SupplierService": return self.core.supplier_service
    @property
    def purchase_order_service(self) -> "PurchaseOrderService": return self.core.purchase_order_service
    @property
    def user_service(self) -> "UserService": return self.core.user_service
    @property
    def outlet_service(self) -> "OutletService": return self.core.outlet_service

    async def adjust_stock(self, dto: StockAdjustmentDTO) -> Result[None, str]:
        """Performs a stock adjustment for one or more products, creating an auditable stock movement record for each change."""
        try:
            async with self.core.get_session() as session:
                for item_dto in dto.items:
                    current_stock_result = await self.inventory_service.get_stock_level(dto.outlet_id, item_dto.product_id, item_dto.variant_id, session)
                    if isinstance(current_stock_result, Failure): raise Exception(f"Failed to get current stock for {item_dto.product_id}: {current_stock_result.error}")
                    
                    quantity_change = item_dto.counted_quantity - current_stock_result.value
                    if quantity_change == 0: continue

                    adjust_result = await self.inventory_service.adjust_stock_level(dto.outlet_id, item_dto.product_id, item_dto.variant_id, quantity_change, session)
                    if isinstance(adjust_result, Failure): raise Exception(f"Failed to update inventory for {item_dto.product_id}: {adjust_result.error}")

                    movement = StockMovement(
                        company_id=dto.company_id, outlet_id=dto.outlet_id, product_id=item_dto.product_id,
                        variant_id=item_dto.variant_id, movement_type='ADJUSTMENT_IN' if quantity_change > 0 else 'ADJUSTMENT_OUT',
                        quantity_change=quantity_change, notes=dto.notes, created_by_user_id=dto.user_id, reference_type="STOCK_ADJUSTMENT"
                    )
                    log_result = await self.inventory_service.log_movement(movement, session)
                    if isinstance(log_result, Failure): raise Exception(f"Failed to log stock movement for {item_dto.product_id}: {log_result.error}")
            return Success(None)
        except Exception as e:
            return Failure(str(e))

    async def deduct_stock_for_sale(self, company_id: UUID, outlet_id: UUID, sale_items: List[Dict[str, Any]], cashier_id: UUID, session: AsyncSession) -> Result[List[StockMovement], str]:
        """Deduct stock for a finalized sale. Called by SalesManager within its atomic transaction."""
        stock_movements = []
        for item_data in sale_items:
            product: Product = item_data['product']
            if not product.track_inventory: continue
            
            adjust_result = await self.inventory_service.adjust_stock_level(
                outlet_id, product.id, item_data.get('variant_id'), -item_data['quantity'], session
            )
            if isinstance(adjust_result, Failure): return Failure(f"Insufficient stock for {product.sku}: {adjust_result.error}")

            movement = StockMovement(
                company_id=company_id, outlet_id=outlet_id, product_id=product.id, variant_id=item_data.get('variant_id'),
                movement_type='SALE', quantity_change=-item_data['quantity'], created_by_user_id=cashier_id, reference_type="SALES_TRANSACTION"
            )
            stock_movements.append(movement)
            log_result = await self.inventory_service.log_movement(movement, session)
            if isinstance(log_result, Failure): return Failure(f"Failed to log sale stock movement for {product.sku}: {log_result.error}")
        return Success(stock_movements)

    async def create_purchase_order(self, dto: PurchaseOrderCreateDTO) -> Result[PurchaseOrderDTO, str]:
        """Creates a new purchase order, including its line items."""
        try:
            async with self.core.get_session() as session:
                supplier_result = await self.supplier_service.get_by_id(dto.supplier_id)
                if isinstance(supplier_result, Failure) or supplier_result.value is None: raise Exception("Supplier not found.")

                po_total_amount = Decimal("0.0")
                po_items: List[PurchaseOrderItem] = []
                for item_dto in dto.items:
                    product_result = await self.product_service.get_by_id(item_dto.product_id)
                    if isinstance(product_result, Failure) or product_result.value is None: raise Exception(f"Product {item_dto.product_id} not found.")
                    po_items.append(PurchaseOrderItem(**item_dto.dict()))
                    po_total_amount += item_dto.quantity_ordered * item_dto.unit_cost

                po_number = dto.po_number or f"PO-{uuid_pkg.uuid4().hex[:8].upper()}"
                new_po = PurchaseOrder(
                    company_id=dto.company_id, outlet_id=dto.outlet_id, supplier_id=dto.supplier_id, po_number=po_number,
                    order_date=dto.order_date, expected_delivery_date=dto.expected_delivery_date, notes=dto.notes,
                    total_amount=po_total_amount.quantize(Decimal("0.01")), items=po_items
                )
                save_po_result = await self.purchase_order_service.create_full_purchase_order(new_po, session)
                if isinstance(save_po_result, Failure): raise Exception(save_po_result.error)

                return await self._create_po_dto(save_po_result.value, supplier_result.value.name)
        except Exception as e:
            return Failure(f"Failed to create purchase order: {e}")

    async def receive_purchase_order_items(self, po_id: UUID, items_received: List[Dict[str, Any]], user_id: UUID) -> Result[None, str]:
        """Records the receipt of items against a purchase order."""
        try:
            async with self.core.get_session() as session:
                po = await session.get(PurchaseOrder, po_id, options=[selectinload(PurchaseOrder.items).selectinload(PurchaseOrderItem.product)])
                if not po: raise Exception(f"Purchase Order {po_id} not found.")
                if po.status not in ['SENT', 'PARTIALLY_RECEIVED']: raise Exception(f"Cannot receive items for PO in '{po.status}' status.")

                for received_item in items_received:
                    po_item = next((item for item in po.items if item.product_id == received_item['product_id']), None)
                    if not po_item: raise Exception(f"Product {received_item['product_id']} not found in PO {po_id}.")
                    
                    quantity_received = received_item['quantity_received']
                    if po_item.quantity_received + quantity_received > po_item.quantity_ordered: raise Exception(f"Received quantity for {po_item.product.sku} exceeds ordered quantity.")

                    po_item.quantity_received += quantity_received
                    adjust_res = await self.inventory_service.adjust_stock_level(po.outlet_id, po_item.product_id, po_item.variant_id, quantity_received, session)
                    if isinstance(adjust_res, Failure): raise Exception(adjust_res.error)

                    movement = StockMovement(
                        company_id=po.company_id, outlet_id=po.outlet_id, product_id=po_item.product_id, variant_id=po_item.variant_id,
                        movement_type='PURCHASE', quantity_change=quantity_received, notes=f"Received via PO {po.po_number}",
                        created_by_user_id=user_id, reference_type="PURCHASE_ORDER", reference_id=po.id
                    )
                    log_res = await self.inventory_service.log_movement(movement, session)
                    if isinstance(log_res, Failure): raise Exception(log_res.error)
                
                po.status = 'RECEIVED' if all(item.quantity_received >= item.quantity_ordered for item in po.items) else 'PARTIALLY_RECEIVED'
                return Success(None)
        except Exception as e:
            return Failure(f"Failed to receive PO items: {e}")

    async def get_inventory_summary(self, company_id: UUID, outlet_id: Optional[UUID] = None, limit: int = 100, offset: int = 0, search_term: Optional[str] = None) -> Result[List[InventorySummaryDTO], str]:
        """Retrieves a summary of inventory levels for display."""
        summary_result = await self.inventory_service.get_inventory_summary(company_id, outlet_id, limit, offset, search_term)
        if isinstance(summary_result, Failure): return summary_result
        return Success([InventorySummaryDTO(**row) for row in summary_result.value])

    async def get_all_suppliers(self, company_id: UUID) -> Result[List[SupplierDTO], str]:
        """Retrieves all active suppliers for a given company."""
        result = await self.supplier_service.get_all_active_suppliers(company_id)
        if isinstance(result, Failure): return result
        return Success([SupplierDTO.from_orm(s) for s in result.value])
    
    async def get_all_purchase_orders(self, company_id: UUID, outlet_id: Optional[UUID] = None) -> Result[List[PurchaseOrderDTO], str]:
        """Retrieves all purchase orders for a given company, optionally filtered by outlet."""
        po_results = await self.purchase_order_service.get_all(company_id, outlet_id=outlet_id) # Assumes BaseService.get_all can take extra filters
        if isinstance(po_results, Failure): return po_results

        po_dtos: List[PurchaseOrderDTO] = []
        for po in po_results.value:
            supplier_res = await self.supplier_service.get_by_id(po.supplier_id)
            supplier_name = supplier_res.value.name if isinstance(supplier_res, Success) and supplier_res.value else "Unknown"
            po_dto_res = await self._create_po_dto(po, supplier_name)
            if isinstance(po_dto_res, Success): po_dtos.append(po_dto_res.value)
        return Success(po_dtos)
        
    async def _create_po_dto(self, po: PurchaseOrder, supplier_name: str) -> Result[PurchaseOrderDTO, str]:
        """Helper to construct a PurchaseOrderDTO from an ORM object."""
        items_dto: List[PurchaseOrderItemDTO] = []
        for item in po.items:
            product_res = await self.product_service.get_by_id(item.product_id)
            if isinstance(product_res, Failure): return product_res
            product = product_res.value
            items_dto.append(
                PurchaseOrderItemDTO(
                    id=item.id, product_id=item.product_id, variant_id=item.variant_id,
                    product_name=product.name, sku=product.sku, quantity_ordered=item.quantity_ordered,
                    quantity_received=item.quantity_received, unit_cost=item.unit_cost,
                    line_total=(item.quantity_ordered * item.unit_cost).quantize(Decimal("0.01"))
                )
            )
        return Success(PurchaseOrderDTO(
            id=po.id, company_id=po.company_id, outlet_id=po.outlet_id, supplier_id=po.supplier_id,
            supplier_name=supplier_name, po_number=po.po_number, order_date=po.order_date,
            expected_delivery_date=po.expected_delivery_date, status=po.status, notes=po.notes,
            total_amount=po.total_amount, items=items_dto
        ))

```

# app/business_logic/managers/base_manager.py
```py
# File: app/business_logic/managers/base_manager.py
"""Abstract Base Class for all business logic managers."""
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.core.application_core import ApplicationCore

class BaseManager:
    """
    Provides managers with access to the application core.
    All managers should inherit from this class.
    """
    def __init__(self, core: "ApplicationCore"):
        self.core = core

```

# app/business_logic/managers/__init__.py
```py

```

# app/business_logic/managers/company_manager.py
```py
# File: app/business_logic/managers/company_manager.py
"""Business Logic Manager for Company and Outlet operations."""
from __future__ import annotations
from typing import TYPE_CHECKING
from uuid import UUID

from app.core.result import Result, Success, Failure
from app.business_logic.managers.base_manager import BaseManager
from app.business_logic.dto.company_dto import CompanyDTO

if TYPE_CHECKING:
    from app.core.application_core import ApplicationCore
    from app.services.company_service import CompanyService

class CompanyManager(BaseManager):
    """Orchestrates business logic for companies and outlets."""
    @property
    def company_service(self) -> "CompanyService":
        return self.core.company_service

    async def get_company(self, company_id: UUID) -> Result[CompanyDTO, str]:
        """Retrieves company details."""
        # This is a placeholder implementation.
        # A full implementation would call the service and handle the result.
        return Failure("get_company is not yet fully implemented in the manager.")

```

# app/business_logic/managers/sales_manager.py
```py
# File: app/business_logic/managers/sales_manager.py
"""
Business Logic Manager for orchestrating the entire sales workflow.
"""
from __future__ import annotations
from decimal import Decimal
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Dict, Any

from app.core.result import Result, Success, Failure
from app.business_logic.managers.base_manager import BaseManager
from app.business_logic.dto.sales_dto import SaleCreateDTO, FinalizedSaleDTO, SalesTransactionItemDTO
from app.models.sales import SalesTransaction, SalesTransactionItem, Payment
from app.models.inventory import StockMovement

if TYPE_CHECKING:
    from app.core.application_core import ApplicationCore
    from app.services.sales_service import SalesService
    from app.services.product_service import ProductService
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
        Args:
            cart_items: A list of dictionaries, each containing a Product ORM model instance and quantity.
        Returns:
            A Success containing a dictionary with 'subtotal', 'tax_amount', 'total_amount', and 'items_with_details', or a Failure.
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
                "gst_rate": product.gst_rate
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
        # --- 1. Pre-computation & Validation Phase (before database transaction) ---
        total_payment = sum(p.amount for p in dto.payments).quantize(Decimal("0.01"))
        
        # Fetch all product details in one go for efficiency
        product_ids = [item.product_id for item in dto.cart_items]
        fetched_products_result = await self.product_service.get_by_ids(product_ids)
        if isinstance(fetched_products_result, Failure):
            return fetched_products_result
        
        products_map = {p.id: p for p in fetched_products_result.value}
        if len(products_map) != len(product_ids):
            return Failure("One or more products in the cart could not be found.")

        # Prepare detailed cart items for calculation
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
        
        # --- 2. Orchestration within a single atomic transaction ---
        try:
            async with self.core.get_session() as session:
                # 2a. Deduct inventory and get stock movement objects
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
                    total_amount=total_amount_due, notes=dto.notes
                )
                
                # 2c. Construct line items and payments
                sale.items = [SalesTransactionItem(**{k: v for k, v in item_data.items() if k in SalesTransactionItem.__table__.columns}) for item_data in calculated_totals["items_with_details"]]
                sale.payments = [Payment(**p_info.dict()) for p_info in dto.payments]
                
                # 2d. Persist the entire transaction atomically
                saved_sale_result = await self.sales_service.create_full_transaction(sale, session)
                if isinstance(saved_sale_result, Failure):
                    return saved_sale_result
                
                saved_sale = saved_sale_result.value
                
                # 2e. Update stock movement records with the new sales_transaction_id
                for movement in stock_movements:
                    movement.reference_id = saved_sale.id
                
                # 2f. Update loyalty points if applicable
                if dto.customer_id:
                    loyalty_result = await self.customer_manager.add_loyalty_points_for_sale(dto.customer_id, saved_sale.total_amount)
                    if isinstance(loyalty_result, Failure):
                        print(f"WARNING: Failed to update loyalty points for customer {dto.customer_id}: {loyalty_result.error}")

                # 2g. Fetch customer and cashier names for the receipt
                customer_name = None
                if dto.customer_id:
                    customer_res = await self.customer_manager.get_customer(dto.customer_id)
                    if isinstance(customer_res, Success): customer_name = customer_res.value.name
                
                cashier_res = await self.user_service.get_by_id(dto.cashier_id)
                cashier_name = cashier_res.value.full_name if isinstance(cashier_res, Success) and cashier_res.value else "Unknown"

                # 2h. Construct FinalizedSaleDTO for UI feedback
                finalized_dto = FinalizedSaleDTO(
                    transaction_id=saved_sale.id, transaction_number=saved_sale.transaction_number,
                    transaction_date=saved_sale.transaction_date, subtotal=saved_sale.subtotal,
                    tax_amount=saved_sale.tax_amount, discount_amount=saved_sale.discount_amount,
                    rounding_adjustment=saved_sale.rounding_adjustment, total_amount=saved_sale.total_amount,
                    amount_paid=total_payment, change_due=change_due, customer_name=customer_name,
                    cashier_name=cashier_name, items=[SalesTransactionItemDTO.from_orm(item) for item in saved_sale.items]
                )
                return Success(finalized_dto)
        except Exception as e:
            return Failure(f"A critical error occurred while finalizing the sale: {e}")

```

# app/business_logic/managers/gst_manager.py
```py
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
    from app.services.company_service import CompanyService

class GstManager(BaseManager):
    """Handles logic related to Singapore GST compliance."""

    @property
    def report_service(self) -> "ReportService":
        return self.core.report_service

    @property
    def company_service(self) -> "CompanyService":
        return self.core.company_service

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
        # For MVP, assume adjustments are zero. A full implementation would fetch these.
        box_8, box_9 = Decimal("0.00"), Decimal("0.00")
        
        box_13_net_gst = (box_6 + box_8 - box_7 - box_9).quantize(Decimal("0.01"))
        
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
            box_13_net_gst_payable=box_13_net_gst
        )
        
        return Success(report_dto)

```

# app/business_logic/managers/product_manager.py
```py
# File: app/business_logic/managers/product_manager.py
"""
Business Logic Manager for Product operations.

This manager orchestrates product-related workflows, enforces business rules,
and coordinates with the data access layer (ProductService).
"""
from __future__ import annotations
from typing import TYPE_CHECKING, List
from uuid import UUID

from app.core.result import Result, Success, Failure
from app.business_logic.managers.base_manager import BaseManager
from app.business_logic.dto.product_dto import ProductDTO, ProductCreateDTO, ProductUpdateDTO
from app.models.product import Product # Import the ORM model

if TYPE_CHECKING:
    from app.core.application_core import ApplicationCore
    from app.services.product_service import ProductService

class ProductManager(BaseManager):
    """Orchestrates business logic for products."""

    @property
    def product_service(self) -> "ProductService":
        """Lazy-loads the ProductService instance from the core."""
        return self.core.product_service

    async def create_product(self, company_id: UUID, dto: ProductCreateDTO) -> Result[ProductDTO, str]:
        """
        Creates a new product after validating business rules.
        Rule: SKU must be unique for the company.
        Args:
            company_id: The UUID of the company creating the product.
            dto: The ProductCreateDTO containing product data.
        Returns:
            A Success with the created ProductDTO, or a Failure with an error message.
        """
        # Business rule: Check for duplicate SKU
        existing_product_result = await self.product_service.get_by_sku(company_id, dto.sku)
        if isinstance(existing_product_result, Failure):
            return existing_product_result # Propagate database error
        if existing_product_result.value is not None:
            return Failure(f"Business Rule Error: Product with SKU '{dto.sku}' already exists.")

        # Convert DTO to ORM model instance
        new_product = Product(company_id=company_id, **dto.dict())
        
        # Persist via service
        create_result = await self.product_service.create(new_product)
        if isinstance(create_result, Failure):
            return create_result # Propagate database error from service

        return Success(ProductDTO.from_orm(create_result.value))

    async def update_product(self, product_id: UUID, dto: ProductUpdateDTO) -> Result[ProductDTO, str]:
        """
        Updates an existing product after validating business rules.
        Args:
            product_id: The UUID of the product to update.
            dto: The ProductUpdateDTO containing updated product data.
        Returns:
            A Success with the updated ProductDTO, or a Failure with an error message.
        """
        # Retrieve existing product
        product_result = await self.product_service.get_by_id(product_id)
        if isinstance(product_result, Failure):
            return product_result
        
        product = product_result.value
        if not product:
            return Failure("Product not found.")

        # Business rule: If SKU is changed, check for duplication
        if dto.sku != product.sku:
            existing_product_result = await self.product_service.get_by_sku(product.company_id, dto.sku)
            if isinstance(existing_product_result, Failure):
                return existing_product_result
            if existing_product_result.value is not None and existing_product_result.value.id != product_id:
                return Failure(f"Business Rule Error: New SKU '{dto.sku}' is already in use by another product.")

        # Update fields from DTO
        for field, value in dto.dict(exclude_unset=True).items(): # exclude_unset for partial updates
            setattr(product, field, value)

        # Persist update via service
        update_result = await self.product_service.update(product)
        if isinstance(update_result, Failure):
            return update_result # Propagate database error
        
        return Success(ProductDTO.from_orm(update_result.value))

    async def get_product(self, product_id: UUID) -> Result[ProductDTO, str]:
        """
        Retrieves a single product by its ID.
        Args:
            product_id: The UUID of the product.
        Returns:
            A Success with the ProductDTO, or a Failure if not found or a database error occurs.
        """
        result = await self.product_service.get_by_id(product_id)
        if isinstance(result, Failure):
            return result
        
        product = result.value
        if not product:
            return Failure("Product not found.")
            
        return Success(ProductDTO.from_orm(product))

    async def get_all_products(self, company_id: UUID, limit: int = 100, offset: int = 0) -> Result[List[ProductDTO], str]:
        """
        Retrieves all products for a given company.
        Args:
            company_id: The UUID of the company.
            limit: Max number of products to return.
            offset: Number of products to skip.
        Returns:
            A Success with a list of ProductDTOs, or a Failure.
        """
        result = await self.product_service.get_all(company_id, limit, offset)
        if isinstance(result, Failure):
            return result
        
        return Success([ProductDTO.from_orm(p) for p in result.value])
    
    async def search_products(self, company_id: UUID, term: str, limit: int = 100, offset: int = 0) -> Result[List[ProductDTO], str]:
        """
        Searches for products by SKU, barcode, or name for a given company.
        Args:
            company_id: The UUID of the company.
            term: The search term.
            limit: Max number of products to return.
            offset: Number of products to skip.
        Returns:
            A Success with a list of matching ProductDTOs, or a Failure.
        """
        result = await self.product_service.search(company_id, term, limit, offset)
        if isinstance(result, Failure):
            return result
        
        return Success([ProductDTO.from_orm(p) for p in result.value])

    async def deactivate_product(self, product_id: UUID) -> Result[bool, str]:
        """
        Deactivates a product (soft delete) by setting its is_active flag to False.
        Args:
            product_id: The UUID of the product to deactivate.
        Returns:
            A Success with True if deactivated, or a Failure.
        """
        product_result = await self.product_service.get_by_id(product_id)
        if isinstance(product_result, Failure):
            return product_result
        
        product = product_result.value
        if not product:
            return Failure("Product not found.")
        
        product.is_active = False # Set the flag
        update_result = await self.product_service.update(product)
        if isinstance(update_result, Failure):
            return update_result
        
        return Success(True)

```

# app/business_logic/managers/user_manager.py
```py
# File: app/business_logic/managers/user_manager.py
"""Business Logic Manager for User, Role, and Permission operations."""
from __future__ import annotations
from typing import TYPE_CHECKING, List, Optional
from uuid import UUID
import bcrypt

from app.core.result import Result, Success, Failure
from app.business_logic.managers.base_manager import BaseManager
from app.business_logic.dto.user_dto import UserDTO, UserCreateDTO, UserUpdateDTO, RoleDTO
from app.models import User, Role, UserRole
from sqlalchemy.orm import selectinload

if TYPE_CHECKING:
    from app.core.application_core import ApplicationCore
    from app.services.user_service import UserService, RoleService

class UserManager(BaseManager):
    """Orchestrates business logic for users and roles."""
    @property
    def user_service(self) -> "UserService": return self.core.user_service
    @property
    def role_service(self) -> "RoleService": return self.core.role_service

    def _hash_password(self, password: str) -> str:
        """Hashes a password using bcrypt."""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verifies a plain password against a hashed one."""
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

    async def create_user(self, company_id: UUID, dto: UserCreateDTO) -> Result[UserDTO, str]:
        """Creates a new user and assigns roles."""
        user_res = await self.user_service.get_by_username(company_id, dto.username)
        if isinstance(user_res, Failure): return user_res
        if user_res.value: return Failure(f"Username '{dto.username}' already exists.")

        hashed_password = self._hash_password(dto.password)
        new_user = User(company_id=company_id, password_hash=hashed_password, **dto.dict(exclude={'password', 'roles'}))
        
        try:
            async with self.core.get_session() as session:
                session.add(new_user)
                await session.flush()  # Ensures new_user.id is available

                # FIX: Implement role assignment logic
                for role_id in dto.roles:
                    # TODO: For multi-outlet scenarios, the DTO should specify the outlet.
                    # For now, we assign the role for the currently active outlet.
                    user_role = UserRole(
                        user_id=new_user.id,
                        role_id=role_id,
                        outlet_id=self.core.current_outlet_id
                    )
                    session.add(user_role)
                
                await session.flush()
                await session.refresh(new_user, attribute_names=['user_roles'])
                return Success(UserDTO.from_orm(new_user))
        except Exception as e:
            return Failure(f"Database error creating user: {e}")

    async def update_user(self, user_id: UUID, dto: UserUpdateDTO) -> Result[UserDTO, str]:
        """Updates an existing user's details, password, and roles."""
        async with self.core.get_session() as session:
            try:
                # Use selectinload to fetch user with roles efficiently
                stmt = select(User).where(User.id == user_id).options(selectinload(User.user_roles))
                result = await session.execute(stmt)
                user = result.scalar_one_or_none()

                if not user:
                    return Failure("User not found.")

                # Update basic user fields
                update_data = dto.dict(exclude_unset=True, exclude={'password', 'roles'})
                for key, value in update_data.items():
                    setattr(user, key, value)
                
                # Update password if provided
                if dto.password:
                    user.password_hash = self._hash_password(dto.password)

                # Update roles: clear existing roles and add new ones
                user.user_roles.clear()
                await session.flush()

                for role_id in dto.roles:
                    user_role = UserRole(
                        user_id=user.id,
                        role_id=role_id,
                        outlet_id=self.core.current_outlet_id # Assumes update is for current context
                    )
                    session.add(user_role)
                
                await session.flush()
                await session.refresh(user, attribute_names=['user_roles'])
                
                return Success(UserDTO.from_orm(user))
            except Exception as e:
                return Failure(f"Database error updating user: {e}")

    async def deactivate_user(self, user_id: UUID) -> Result[bool, str]:
        """Deactivates a user (soft delete)."""
        user_res = await self.user_service.get_by_id(user_id)
        if isinstance(user_res, Failure): return user_res
        
        user = user_res.value
        if not user: return Failure("User not found.")
        
        user.is_active = False
        update_result = await self.user_service.update(user)
        if isinstance(update_result, Failure): return update_result
        
        return Success(True)

    async def get_all_users(self, company_id: UUID) -> Result[List[UserDTO], str]:
        """Retrieves all users for a given company."""
        res = await self.user_service.get_all(company_id, options=[selectinload(User.user_roles).selectinload(UserRole.role)])
        if isinstance(res, Failure): return res
        return Success([UserDTO.from_orm(u) for u in res.value])

    async def get_all_roles(self, company_id: UUID) -> Result[List[RoleDTO], str]:
        """Retrieves all roles for a given company."""
        res = await self.role_service.get_all(company_id)
        if isinstance(res, Failure): return res
        return Success([RoleDTO.from_orm(r) for r in res.value])

```

# app/business_logic/managers/customer_manager.py
```py
# File: app/business_logic/managers/customer_manager.py
"""Business Logic Manager for Customer operations."""
from __future__ import annotations
from typing import TYPE_CHECKING, List
from uuid import UUID
from decimal import Decimal

from app.core.result import Result, Success, Failure
from app.business_logic.managers.base_manager import BaseManager
from app.business_logic.dto.customer_dto import CustomerDTO, CustomerCreateDTO, CustomerUpdateDTO
from app.models.customer import Customer # Import the ORM model

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
        """
        Creates a new customer.
        Business rule: Customer code and email must be unique for the company.
        """
        # Business rule: Check for duplicate customer code
        existing_result = await self.customer_service.get_by_code(company_id, dto.customer_code)
        if isinstance(existing_result, Failure):
            return existing_result # Propagate database error
        if existing_result.value is not None:
            return Failure(f"Business Rule Error: Customer with code '{dto.customer_code}' already exists.")

        # Business rule: If email is provided, check for duplicate email
        if dto.email:
            email_check_result = await self.customer_service.get_by_email(company_id, dto.email)
            if isinstance(email_check_result, Failure):
                return email_check_result
            if email_check_result.value is not None:
                return Failure(f"Business Rule Error: Customer with email '{dto.email}' already exists.")

        new_customer = Customer(company_id=company_id, **dto.dict())
        
        create_result = await self.customer_service.create(new_customer)
        if isinstance(create_result, Failure):
            return create_result

        return Success(CustomerDTO.from_orm(create_result.value))

    async def update_customer(self, customer_id: UUID, dto: CustomerUpdateDTO) -> Result[CustomerDTO, str]:
        """Updates an existing customer."""
        customer_result = await self.customer_service.get_by_id(customer_id)
        if isinstance(customer_result, Failure):
            return customer_result
        
        customer = customer_result.value
        if not customer:
            return Failure("Customer not found.")

        if dto.customer_code != customer.customer_code:
            existing_result = await self.customer_service.get_by_code(customer.company_id, dto.customer_code)
            if isinstance(existing_result, Failure):
                return existing_result
            if existing_result.value is not None and existing_result.value.id != customer_id:
                return Failure(f"Business Rule Error: New customer code '{dto.customer_code}' is already in use by another customer.")
        
        if dto.email and dto.email != customer.email:
            email_check_result = await self.customer_service.get_by_email(customer.company_id, dto.email)
            if isinstance(email_check_result, Failure):
                return email_check_result
            if email_check_result.value is not None and email_check_result.value.id != customer_id:
                return Failure(f"Business Rule Error: New email '{dto.email}' is already in use by another customer.")

        for field, value in dto.dict(exclude_unset=True).items():
            setattr(customer, field, value)

        update_result = await self.customer_service.update(customer)
        if isinstance(update_result, Failure):
            return update_result
        
        return Success(CustomerDTO.from_orm(update_result.value))

    async def get_customer(self, customer_id: UUID) -> Result[CustomerDTO, str]:
        """Retrieves a single customer by ID."""
        result = await self.customer_service.get_by_id(customer_id)
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
        Business Rule: 1 point for every S$10 spent (configurable in a future settings module).
        """
        loyalty_rate = Decimal("10.00")
        points_to_add = int(sale_total // loyalty_rate)
        
        if points_to_add <= 0:
            return Success(0)

        try:
            async with self.core.get_session() as session:
                customer_result = await self.customer_service.get_by_id(customer_id)
                if isinstance(customer_result, Failure): return customer_result
                
                customer = customer_result.value
                if not customer: return Failure(f"Customer with ID {customer_id} not found.")
                
                customer.loyalty_points += points_to_add
                
                update_result = await self.customer_service.update(customer)
                if isinstance(update_result, Failure): return update_result
                    
                # TODO: Log the loyalty transaction for auditing
                return Success(customer.loyalty_points)
        except Exception as e:
            print(f"ERROR: Failed to add loyalty points for customer {customer_id}: {e}")
            return Failure(f"Failed to add loyalty points: {e}")

```

# app/business_logic/managers/reporting_manager.py
```py
# File: app/business_logic/managers/reporting_manager.py
"""Business Logic Manager for generating business reports and analytics."""
from __future__ import annotations
from typing import TYPE_CHECKING, List, Optional
from datetime import date
from decimal import Decimal
import uuid

from app.core.result import Result, Success, Failure
from app.business_logic.managers.base_manager import BaseManager
from app.business_logic.dto.reporting_dto import (
    SalesSummaryReportDTO, SalesByPeriodDTO, ProductPerformanceDTO,
    InventoryValuationReportDTO, InventoryValuationItemDTO
)

if TYPE_CHECKING:
    from app.core.application_core import ApplicationCore
    from app.services.report_service import ReportService
    from app.services.company_service import OutletService

class ReportingManager(BaseManager):
    """Orchestrates the creation of business intelligence reports."""
    @property
    def report_service(self) -> "ReportService": return self.core.report_service
    @property
    def outlet_service(self) -> "OutletService": return self.core.outlet_service

    async def generate_sales_summary_report(self, company_id: uuid.UUID, start_date: date, end_date: date) -> Result[SalesSummaryReportDTO, str]:
        """Generates a comprehensive sales summary report."""
        sales_data_res = await self.report_service.get_sales_summary_raw_data(company_id, start_date, end_date)
        if isinstance(sales_data_res, Failure): return sales_data_res
        
        product_perf_res = await self.report_service.get_product_performance_raw_data(company_id, start_date, end_date)
        if isinstance(product_perf_res, Failure): product_perf_res.value = [] # Continue if this part fails
        
        # Process sales data
        sales_by_period = [SalesByPeriodDTO(
            period=row["period"], total_sales=row["total_sales"], transaction_count=row["transaction_count"],
            average_transaction_value=(row["total_sales"] / row["transaction_count"] if row["transaction_count"] > 0 else Decimal(0))
        ) for row in sales_data_res.value]
        
        # Process product performance data
        top_products = []
        for p_data in product_perf_res.value:
            revenue = p_data.get('total_revenue', Decimal(0))
            cost = p_data.get('total_cost', Decimal(0))
            margin = revenue - cost
            margin_pct = (margin / revenue * 100) if revenue > 0 else Decimal(0)
            top_products.append(ProductPerformanceDTO(
                product_id=p_data['product_id'], sku=p_data['sku'], name=p_data['name'],
                quantity_sold=p_data['quantity_sold'], total_revenue=revenue, total_cost=cost,
                gross_margin=margin, gross_margin_percentage=margin_pct
            ))
            
        return Success(SalesSummaryReportDTO(
            start_date=start_date, end_date=end_date,
            total_revenue=sum(s.total_sales for s in sales_by_period),
            total_transactions=sum(s.transaction_count for s in sales_by_period),
            total_discount_amount=sum(row.get("total_discount_amount", Decimal(0)) for row in sales_data_res.value),
            total_tax_collected=sum(row.get("total_tax_collected", Decimal(0)) for row in sales_data_res.value),
            sales_by_period=sales_by_period, top_performing_products=top_products
        ))

    async def generate_inventory_valuation_report(self, company_id: uuid.UUID, outlet_id: Optional[uuid.UUID] = None) -> Result[InventoryValuationReportDTO, str]:
        """Generates a report showing the current value of inventory."""
        raw_data_res = await self.report_service.get_inventory_valuation_raw_data(company_id, outlet_id)
        if isinstance(raw_data_res, Failure): return raw_data_res
        
        items_data = raw_data_res.value
        valuation_items = [InventoryValuationItemDTO(
            product_id=item['product_id'], sku=item['sku'], name=item['name'],
            quantity_on_hand=item['quantity_on_hand'], cost_price=item['cost_price'],
            total_value=(item['quantity_on_hand'] * item['cost_price'])
        ) for item in items_data]

        outlet_name = "All Outlets"
        if outlet_id:
            outlet_res = await self.outlet_service.get_by_id(outlet_id)
            if isinstance(outlet_res, Success) and outlet_res.value: outlet_name = outlet_res.value.name

        return Success(InventoryValuationReportDTO(
            as_of_date=date.today(), outlet_id=outlet_id or uuid.uuid4(), outlet_name=outlet_name,
            total_inventory_value=sum(v.total_value for v in valuation_items),
            total_distinct_items=len(valuation_items), items=valuation_items
        ))

```

# app/business_logic/dto/company_dto.py
```py
# File: app/business_logic/dto/company_dto.py
"""Data Transfer Objects for Company and Outlet operations."""
import uuid
from typing import Optional, List
from pydantic import BaseModel, Field

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

    class Config:
        from_attributes = True

class OutletDTO(BaseModel):
    """DTO representing a retail outlet."""
    id: uuid.UUID
    name: str
    code: str
    is_active: bool

    class Config:
        from_attributes = True

```

# app/business_logic/dto/inventory_dto.py
```py
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
        from_attributes = True

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
        from_attributes = True

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
        from_attributes = True

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
        from_attributes = True

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
        from_attributes = True

```

# app/business_logic/dto/__init__.py
```py

```

# app/business_logic/dto/product_dto.py
```py
# File: app/business_logic/dto/product_dto.py
"""
Data Transfer Objects (DTOs) for the Product entity.
"""
import uuid
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, validator

class ProductBaseDTO(BaseModel):
    """Base DTO with common product fields."""
    sku: str = Field(..., min_length=1, max_length=100, description="Stock Keeping Unit")
    name: str = Field(..., min_length=1, max_length=255, description="Product name")
    description: Optional[str] = Field(None, description="Detailed description of the product")
    selling_price: Decimal = Field(..., gt=Decimal("0.00"), decimal_places=4, description="The retail price of the product")
    cost_price: Decimal = Field(..., ge=Decimal("0.00"), decimal_places=4, description="The cost of acquiring the product")
    gst_rate: Decimal = Field(Decimal("9.00"), ge=Decimal("0.00"), le=Decimal("100.00"), decimal_places=2, description="Goods and Services Tax rate (e.g., 9.00 for 9%)") # FIX: Updated GST Rate
    track_inventory: bool = True
    is_active: bool = True
    category_id: Optional[uuid.UUID] = Field(None, description="UUID of the product's category")
    supplier_id: Optional[uuid.UUID] = Field(None, description="UUID of the product's primary supplier")
    barcode: Optional[str] = Field(None, max_length=100, description="Product barcode (EAN, UPC, etc.)")
    reorder_point: int = Field(0, ge=0, description="Threshold quantity for reordering suggestions")

    @validator('selling_price')
    def check_selling_price_not_less_than_cost_price(cls, v, values):
        if 'cost_price' in values and v < values['cost_price']:
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

    class Config:
        from_attributes = True

```

# app/business_logic/dto/user_dto.py
```py
# File: app/business_logic/dto/user_dto.py
"""Data Transfer Objects for User operations."""
import uuid
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr

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
    class Config:
        from_attributes = True

class UserDTO(UserBaseDTO):
    id: uuid.UUID
    roles: List[RoleDTO]
    class Config:
        from_attributes = True

```

# app/business_logic/dto/sales_dto.py
```py
# File: app/business_logic/dto/sales_dto.py
"""Data Transfer Objects for Sales operations."""
import uuid
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field
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
    cart_items: List[CartItemDTO] = Field(..., min_items=1)
    payments: List[PaymentInfoDTO] = Field(..., min_items=1)
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
    
    class Config:
        from_attributes = True

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

# app/business_logic/dto/reporting_dto.py
```py
# File: app/business_logic/dto/reporting_dto.py
"""
Data Transfer Objects (DTOs) for Reporting and Analytics.

These models define the structure of the data returned by the reporting engine.
They are read-only and designed for clear presentation in the UI or for export.
"""
import uuid
from decimal import Decimal
from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, Field

# --- Sales Report DTOs ---

class SalesByPeriodDTO(BaseModel):
    """Aggregated sales data for a specific period (e.g., a day or month)."""
    period: date = Field(..., description="Date of the period")
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
    total_revenue: Decimal = Field(..., decimal_places=2)
    total_transactions: int = Field(..., ge=0)
    total_discount_amount: Decimal = Field(..., decimal_places=2)
    total_tax_collected: Decimal = Field(..., decimal_places=2)
    sales_by_period: List[SalesByPeriodDTO]
    top_performing_products: List[ProductPerformanceDTO]

# --- Inventory Report DTOs ---

class InventoryValuationItemDTO(BaseModel):
    product_id: uuid.UUID
    sku: str
    name: str
    quantity_on_hand: Decimal = Field(..., decimal_places=4)
    cost_price: Decimal = Field(..., decimal_places=4)
    total_value: Decimal = Field(..., decimal_places=2)

class InventoryValuationReportDTO(BaseModel):
    """DTO for the inventory valuation report."""
    as_of_date: date
    outlet_id: uuid.UUID
    outlet_name: str
    total_inventory_value: Decimal = Field(..., decimal_places=2)
    total_distinct_items: int = Field(..., ge=0)
    items: List[InventoryValuationItemDTO]

# --- GST Report DTOs (IRAS Form 5 Structure) ---

class GstReportDTO(BaseModel):
    """
    DTO structured to match the fields of the Singapore IRAS GST Form 5.
    """
    company_id: uuid.UUID
    company_name: str
    company_gst_reg_no: Optional[str]
    start_date: date
    end_date: date
    box_1_standard_rated_supplies: Decimal = Field(..., decimal_places=2)
    box_2_zero_rated_supplies: Decimal = Field(..., decimal_places=2)
    box_3_exempt_supplies: Decimal = Field(..., decimal_places=2)
    box_4_total_supplies: Decimal = Field(..., decimal_places=2)
    box_5_taxable_purchases: Decimal = Field(..., decimal_places=2)
    box_6_output_tax_due: Decimal = Field(..., decimal_places=2)
    box_7_input_tax_claimed: Decimal = Field(..., decimal_places=2)
    box_8_adjustments_output_tax: Decimal = Field(Decimal("0.00"), decimal_places=2)
    box_9_adjustments_input_tax: Decimal = Field(Decimal("0.00"), decimal_places=2)
    box_13_net_gst_payable: Decimal = Field(..., decimal_places=2)

```

# app/business_logic/dto/customer_dto.py
```py
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
        from_attributes = True

class LoyaltyPointAdjustmentDTO(BaseModel):
    """DTO for manually adjusting a customer's loyalty points."""
    customer_id: uuid.UUID
    points_change: int # Can be positive (add) or negative (deduct)
    reason: str = Field(..., min_length=1, description="Reason for the manual adjustment (e.g., 'Goodwill gesture', 'Point correction')")
    admin_user_id: uuid.UUID # User performing the adjustment

```

# scripts/database/seed_data.py
```py

```

# scripts/database/schema.sql
```sql
-- File: scripts/database/schema.sql
-- =============================================================================
-- SG Point-of-Sale (SG-POS) System - Complete Database Schema
-- Version: 2.0 (Super-Set Edition)
-- Database: PostgreSQL 15+
-- =============================================================================

-- Best practice: Isolate the application's tables within their own schema.
CREATE SCHEMA IF NOT EXISTS sgpos;
SET search_path TO sgpos;

-- Enable the pgcrypto extension to generate UUIDs.
-- This should be run once by a superuser on the target database.
CREATE EXTENSION IF NOT EXISTS "pgcrypto";


-- =============================================================================
-- Section 1: Core Business & Multi-Tenancy Structure
-- Description: Defines the top-level entities for companies and their outlets.
-- =============================================================================

CREATE TABLE companies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    registration_number VARCHAR(20) UNIQUE NOT NULL,
    gst_registration_number VARCHAR(20) UNIQUE,
    address TEXT,
    phone VARCHAR(20),
    email VARCHAR(255),
    base_currency VARCHAR(3) NOT NULL DEFAULT 'SGD', -- Corrected from CHAR(3)
    fiscal_year_start DATE,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
COMMENT ON TABLE sgpos.companies IS 'Top-level entity for multi-tenancy support. Each company is a separate business customer.';
COMMENT ON COLUMN sgpos.companies.registration_number IS 'Singapore UEN (Unique Entity Number)';


CREATE TABLE outlets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES sgpos.companies(id) ON DELETE RESTRICT,
    code VARCHAR(50) NOT NULL,
    name VARCHAR(255) NOT NULL,
    address TEXT,
    phone VARCHAR(20),
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(company_id, code)
);
COMMENT ON TABLE sgpos.outlets IS 'Represents physical store locations or branches for a company.';


-- =============================================================================
-- Section 2: Users, Roles, and Security (RBAC Model)
-- Description: Manages user authentication and role-based access control.
-- =============================================================================

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES sgpos.companies(id) ON DELETE RESTRICT,
    username VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN NOT NULL DEFAULT true,
    last_login_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(company_id, username),
    UNIQUE(company_id, email)
);
COMMENT ON COLUMN sgpos.users.password_hash IS 'Hashed using bcrypt';

CREATE TABLE roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES sgpos.companies(id) ON DELETE RESTRICT,
    name VARCHAR(50) NOT NULL,
    description TEXT,
    is_system_role BOOLEAN NOT NULL DEFAULT false,
    UNIQUE(company_id, name)
);
COMMENT ON TABLE sgpos.roles IS 'Defines user roles like Admin, Manager, Cashier.';
COMMENT ON COLUMN sgpos.roles.is_system_role IS 'True for built-in roles like "Admin", which cannot be deleted.';

CREATE TABLE permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    action VARCHAR(100) NOT NULL, -- e.g., 'CREATE', 'READ', 'UPDATE', 'DELETE', 'APPROVE'
    resource VARCHAR(100) NOT NULL, -- e.g., 'PRODUCT', 'SALE_TRANSACTION', 'USER_MANAGEMENT'
    description TEXT,
    UNIQUE(action, resource)
);
COMMENT ON TABLE sgpos.permissions IS 'Defines granular permissions within the system.';

CREATE TABLE role_permissions (
    role_id UUID NOT NULL REFERENCES sgpos.roles(id) ON DELETE CASCADE,
    permission_id UUID NOT NULL REFERENCES sgpos.permissions(id) ON DELETE CASCADE,
    PRIMARY KEY (role_id, permission_id)
);
COMMENT ON TABLE sgpos.role_permissions IS 'Junction table linking roles to their permissions.';

CREATE TABLE user_roles (
    user_id UUID NOT NULL REFERENCES sgpos.users(id) ON DELETE CASCADE,
    role_id UUID NOT NULL REFERENCES sgpos.roles(id) ON DELETE CASCADE,
    -- outlet_id allows for role assignment specific to a store, can be NULL for company-wide roles.
    outlet_id UUID REFERENCES sgpos.outlets(id) ON DELETE CASCADE, -- Made implicitly NOT NULL by PK below. If NULLable global roles are required, PK needs to be reconsidered or separate table.
    PRIMARY KEY (user_id, role_id, outlet_id)
);
COMMENT ON TABLE sgpos.user_roles IS 'Assigns roles to users, potentially on a per-outlet basis.';


-- =============================================================================
-- Section 3: Product Catalog & Inventory
-- Description: Manages products, suppliers, categories, and stock levels.
-- =============================================================================

CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES sgpos.companies(id) ON DELETE RESTRICT,
    parent_id UUID REFERENCES sgpos.categories(id) ON DELETE SET NULL,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(company_id, name)
);

CREATE TABLE suppliers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES sgpos.companies(id) ON DELETE RESTRICT,
    name VARCHAR(255) NOT NULL,
    contact_person VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(50),
    address TEXT,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(company_id, name)
);

CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES sgpos.companies(id) ON DELETE RESTRICT,
    category_id UUID REFERENCES sgpos.categories(id),
    supplier_id UUID REFERENCES sgpos.suppliers(id),
    sku VARCHAR(100) NOT NULL,
    barcode VARCHAR(100),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    cost_price NUMERIC(19, 4) NOT NULL DEFAULT 0,
    selling_price NUMERIC(19, 4) NOT NULL,
    gst_rate NUMERIC(5, 2) NOT NULL DEFAULT 8.00,
    track_inventory BOOLEAN NOT NULL DEFAULT true,
    reorder_point INT NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(company_id, sku)
);
COMMENT ON COLUMN sgpos.products.gst_rate IS 'Current SG GST rate, can be overridden per product';

CREATE TABLE product_variants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID NOT NULL REFERENCES sgpos.products(id) ON DELETE CASCADE,
    sku_suffix VARCHAR(100) NOT NULL,
    barcode VARCHAR(100),
    attributes JSONB NOT NULL,
    cost_price_override NUMERIC(19, 4),
    selling_price_override NUMERIC(19, 4),
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(product_id, sku_suffix)
);
COMMENT ON TABLE sgpos.product_variants IS 'Stores variations of a base product, like size or color.';
COMMENT ON COLUMN sgpos.product_variants.attributes IS 'e.g., {"size": "L", "color": "Red"}';


CREATE TABLE inventory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    outlet_id UUID NOT NULL REFERENCES sgpos.outlets(id) ON DELETE RESTRICT,
    product_id UUID NOT NULL REFERENCES sgpos.products(id) ON DELETE RESTRICT,
    variant_id UUID REFERENCES sgpos.product_variants(id) ON DELETE RESTRICT,
    quantity_on_hand NUMERIC(15, 4) NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(outlet_id, product_id, variant_id)
);
COMMENT ON TABLE sgpos.inventory IS 'Tracks the actual stock count of a specific product/variant at a specific outlet.';

CREATE TABLE stock_movements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES sgpos.companies(id),
    outlet_id UUID NOT NULL REFERENCES sgpos.outlets(id),
    product_id UUID NOT NULL REFERENCES sgpos.products(id),
    variant_id UUID REFERENCES sgpos.product_variants(id),
    movement_type VARCHAR(50) NOT NULL CHECK (movement_type IN ('SALE', 'RETURN', 'PURCHASE', 'ADJUSTMENT_IN', 'ADJUSTMENT_OUT', 'TRANSFER_IN', 'TRANSFER_OUT')),
    quantity_change NUMERIC(15, 4) NOT NULL,
    reference_id UUID,
    notes TEXT,
    created_by_user_id UUID REFERENCES sgpos.users(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
COMMENT ON TABLE sgpos.stock_movements IS 'Immutable log of all inventory changes for full auditability.';
COMMENT ON COLUMN sgpos.stock_movements.quantity_change IS 'Positive for stock in, negative for stock out';
COMMENT ON COLUMN sgpos.stock_movements.reference_id IS 'e.g., sales_transaction_id, purchase_order_id';

-- Added Purchase Orders and Purchase Order Items to this section as they are part of inventory management
CREATE TABLE purchase_orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES sgpos.companies(id),
    outlet_id UUID NOT NULL REFERENCES sgpos.outlets(id),
    supplier_id UUID NOT NULL REFERENCES sgpos.suppliers(id),
    po_number VARCHAR(50) NOT NULL,
    order_date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expected_delivery_date TIMESTAMPTZ,
    status VARCHAR(20) NOT NULL CHECK (status IN ('DRAFT', 'SENT', 'PARTIALLY_RECEIVED', 'RECEIVED', 'CANCELLED')),
    notes TEXT,
    total_amount NUMERIC(19, 2) NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(company_id, po_number)
);
COMMENT ON TABLE sgpos.purchase_orders IS 'Represents a purchase order sent to a supplier.';

CREATE TABLE purchase_order_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    purchase_order_id UUID NOT NULL REFERENCES sgpos.purchase_orders(id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES sgpos.products(id),
    variant_id UUID REFERENCES sgpos.product_variants(id), -- Added variant_id for PO items if variants are ordered
    quantity_ordered NUMERIC(15, 4) NOT NULL,
    quantity_received NUMERIC(15, 4) NOT NULL DEFAULT 0,
    unit_cost NUMERIC(19, 4) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(purchase_order_id, product_id, variant_id) -- Unique constraint includes variant_id
);
COMMENT ON TABLE sgpos.purchase_order_items IS 'A line item within a purchase order.';


-- =============================================================================
-- Section 4: Sales & Transactions
-- Description: The core tables for handling sales, customers, and payments.
-- =============================================================================

CREATE TABLE customers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES sgpos.companies(id) ON DELETE RESTRICT,
    customer_code VARCHAR(50) NOT NULL,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(50),
    address TEXT,
    loyalty_points INT NOT NULL DEFAULT 0,
    credit_limit NUMERIC(19, 2) NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(company_id, customer_code),
    UNIQUE(company_id, email)
);

CREATE TABLE sales_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES sgpos.companies(id) ON DELETE RESTRICT,
    outlet_id UUID NOT NULL REFERENCES sgpos.outlets(id),
    transaction_number VARCHAR(50) NOT NULL,
    transaction_date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    customer_id UUID REFERENCES sgpos.customers(id),
    cashier_id UUID NOT NULL REFERENCES sgpos.users(id),
    subtotal NUMERIC(19, 2) NOT NULL,
    tax_amount NUMERIC(19, 2) NOT NULL,
    discount_amount NUMERIC(19, 2) NOT NULL DEFAULT 0,
    rounding_adjustment NUMERIC(19, 2) NOT NULL DEFAULT 0,
    total_amount NUMERIC(19, 2) NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('COMPLETED', 'VOIDED', 'HELD')),
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(company_id, transaction_number)
);

CREATE TABLE sales_transaction_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sales_transaction_id UUID NOT NULL REFERENCES sgpos.sales_transactions(id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES sgpos.products(id),
    variant_id UUID REFERENCES sgpos.product_variants(id), -- Added variant_id for sales items
    quantity NUMERIC(15, 4) NOT NULL,
    unit_price NUMERIC(19, 4) NOT NULL,
    cost_price NUMERIC(19, 4) NOT NULL,
    line_total NUMERIC(19, 2) NOT NULL,
    UNIQUE(sales_transaction_id, product_id, variant_id) -- Unique constraint includes variant_id
);
COMMENT ON TABLE sgpos.sales_transaction_items IS 'Individual line items for a sales transaction.';
COMMENT ON COLUMN sgpos.sales_transaction_items.unit_price IS 'Price at time of sale';
COMMENT ON COLUMN sgpos.sales_transaction_items.cost_price IS 'Cost at time of sale for margin analysis';

CREATE TABLE payment_methods (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES sgpos.companies(id),
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL CHECK (type IN ('CASH', 'CARD', 'NETS', 'PAYNOW', 'VOUCHER', 'STORE_CREDIT')),
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), -- Added created_at/updated_at to match other tables for consistency
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(company_id, name)
);

CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sales_transaction_id UUID NOT NULL REFERENCES sgpos.sales_transactions(id) ON DELETE CASCADE,
    payment_method_id UUID NOT NULL REFERENCES sgpos.payment_methods(id),
    amount NUMERIC(19, 2) NOT NULL,
    reference_number VARCHAR(100),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW() -- Added updated_at for consistency
);
COMMENT ON TABLE sgpos.payments IS 'Records individual payments, supporting split tender.';
COMMENT ON COLUMN sgpos.payments.reference_number IS 'For card transactions, e-wallets, etc.';


-- =============================================================================
-- Section 5: Accounting & GST
-- Description: Tables for financial records, chart of accounts, and GST compliance.
-- =============================================================================

CREATE TABLE chart_of_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES sgpos.companies(id),
    account_code VARCHAR(20) NOT NULL,
    account_name VARCHAR(255) NOT NULL,
    account_type VARCHAR(50) NOT NULL CHECK (account_type IN ('ASSET', 'LIABILITY', 'EQUITY', 'REVENUE', 'EXPENSE')),
    parent_id UUID REFERENCES sgpos.chart_of_accounts(id),
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), -- Added for consistency
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), -- Added for consistency
    UNIQUE(company_id, account_code)
);

CREATE TABLE journal_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES sgpos.companies(id),
    entry_number VARCHAR(50) NOT NULL,
    entry_date DATE NOT NULL,
    description TEXT,
    reference_type VARCHAR(50), -- e.g., 'SALE', 'PURCHASE'
    reference_id UUID,
    status VARCHAR(20) NOT NULL DEFAULT 'POSTED' CHECK (status IN ('DRAFT', 'POSTED', 'VOID')),
    created_by_user_id UUID NOT NULL REFERENCES sgpos.users(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), -- Added for consistency
    UNIQUE(company_id, entry_number)
);

CREATE TABLE journal_entry_lines (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    journal_entry_id UUID NOT NULL REFERENCES sgpos.journal_entries(id) ON DELETE CASCADE,
    account_id UUID NOT NULL REFERENCES sgpos.chart_of_accounts(id),
    debit_amount NUMERIC(19, 2) NOT NULL DEFAULT 0,
    credit_amount NUMERIC(19, 2) NOT NULL DEFAULT 0,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), -- Added for consistency
    -- A line must be either a debit or a credit, but not both or neither.
    CONSTRAINT debit_or_credit_check CHECK ( (debit_amount > 0 AND credit_amount = 0) OR (credit_amount > 0 AND debit_amount = 0) )
);
COMMENT ON TABLE sgpos.journal_entry_lines IS 'Individual lines of a double-entry bookkeeping record.';


-- =============================================================================
-- Section 6: Auditing
-- Description: A comprehensive, immutable log of all significant changes.
-- =============================================================================

CREATE TABLE audit_logs (
    id BIGSERIAL PRIMARY KEY,
    company_id UUID,
    user_id UUID REFERENCES sgpos.users(id) ON DELETE SET NULL,
    action VARCHAR(50) NOT NULL, -- e.g., 'CREATE_PRODUCT', 'UPDATE_PRICE'
    table_name VARCHAR(100) NOT NULL,
    record_id UUID NOT NULL,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
COMMENT ON TABLE sgpos.audit_logs IS 'Immutable log for tracking all data modifications for compliance and debugging.';


-- =============================================================================
-- Section 7: Indexes for Performance
-- Description: Strategic indexes to optimize common query patterns.
-- =============================================================================

-- Indexes on foreign keys and frequently filtered columns
CREATE INDEX idx_outlets_company_id ON sgpos.outlets(company_id);
CREATE INDEX idx_users_company_id ON sgpos.users(company_id);
CREATE INDEX idx_roles_company_id ON sgpos.roles(company_id);
CREATE INDEX idx_role_permissions_role_id ON sgpos.role_permissions(role_id);
CREATE INDEX idx_role_permissions_permission_id ON sgpos.role_permissions(permission_id);
CREATE INDEX idx_user_roles_user_id ON sgpos.user_roles(user_id);
CREATE INDEX idx_user_roles_role_id ON sgpos.user_roles(role_id);
CREATE INDEX idx_user_roles_outlet_id ON sgpos.user_roles(outlet_id);
CREATE INDEX idx_categories_company_id ON sgpos.categories(company_id);
CREATE INDEX idx_suppliers_company_id ON sgpos.suppliers(company_id);
CREATE INDEX idx_products_company_id ON sgpos.products(company_id);
CREATE INDEX idx_products_category_id ON sgpos.products(category_id);
CREATE INDEX idx_products_supplier_id ON sgpos.products(supplier_id);
CREATE INDEX idx_products_barcode ON sgpos.products(barcode) WHERE barcode IS NOT NULL;
CREATE INDEX idx_product_variants_product_id ON sgpos.product_variants(product_id);
CREATE INDEX idx_inventory_outlet_id ON sgpos.inventory(outlet_id);
CREATE INDEX idx_inventory_product_id ON sgpos.inventory(product_id);
CREATE INDEX idx_inventory_variant_id ON sgpos.inventory(variant_id);
CREATE INDEX idx_stock_movements_company_id ON sgpos.stock_movements(company_id);
CREATE INDEX idx_stock_movements_outlet_id ON sgpos.stock_movements(outlet_id);
CREATE INDEX idx_stock_movements_product_id ON sgpos.stock_movements(product_id);
CREATE INDEX idx_stock_movements_created_by_user_id ON sgpos.stock_movements(created_by_user_id);
CREATE INDEX idx_purchase_orders_company_id ON sgpos.purchase_orders(company_id);
CREATE INDEX idx_purchase_orders_outlet_id ON sgpos.purchase_orders(outlet_id);
CREATE INDEX idx_purchase_orders_supplier_id ON sgpos.purchase_orders(supplier_id);
CREATE INDEX idx_purchase_order_items_po_id ON sgpos.purchase_order_items(purchase_order_id);
CREATE INDEX idx_purchase_order_items_product_id ON sgpos.purchase_order_items(product_id);
CREATE INDEX idx_customers_company_id ON sgpos.customers(company_id);
CREATE INDEX idx_sales_transactions_company_id ON sgpos.sales_transactions(company_id);
CREATE INDEX idx_sales_transactions_outlet_id ON sgpos.sales_transactions(outlet_id);
    -- Changed from sales_transactions_date to sales_transactions_transaction_date to be more specific
CREATE INDEX idx_sales_transactions_transaction_date ON sgpos.sales_transactions(transaction_date DESC);
CREATE INDEX idx_sales_transactions_customer_id ON sgpos.sales_transactions(customer_id);
CREATE INDEX idx_sales_transactions_cashier_id ON sgpos.sales_transactions(cashier_id);
CREATE INDEX idx_sales_transaction_items_transaction_id ON sgpos.sales_transaction_items(sales_transaction_id);
CREATE INDEX idx_sales_transaction_items_product_id ON sgpos.sales_transaction_items(product_id);
CREATE INDEX idx_payment_methods_company_id ON sgpos.payment_methods(company_id);
CREATE INDEX idx_payments_sales_transaction_id ON sgpos.payments(sales_transaction_id);
CREATE INDEX idx_payments_payment_method_id ON sgpos.payments(payment_method_id);
CREATE INDEX idx_chart_of_accounts_company_id ON sgpos.chart_of_accounts(company_id);
CREATE INDEX idx_chart_of_accounts_parent_id ON sgpos.chart_of_accounts(parent_id);
CREATE INDEX idx_journal_entries_company_id ON sgpos.journal_entries(company_id);
CREATE INDEX idx_journal_entries_entry_date ON sgpos.journal_entries(entry_date DESC);
CREATE INDEX idx_journal_entries_reference_id ON sgpos.journal_entries(reference_id);
CREATE INDEX idx_journal_entry_lines_journal_entry_id ON sgpos.journal_entry_lines(journal_entry_id);
CREATE INDEX idx_journal_entry_lines_account_id ON sgpos.journal_entry_lines(account_id);
CREATE INDEX idx_audit_logs_company_id ON sgpos.audit_logs(company_id);
CREATE INDEX idx_audit_logs_user_id ON sgpos.audit_logs(user_id);
CREATE INDEX idx_audit_logs_record ON sgpos.audit_logs(table_name, record_id);
CREATE INDEX idx_audit_logs_created_at ON sgpos.audit_logs(created_at DESC);


-- =============================================================================
-- Section 8: Triggers and Functions
-- Description: Database-level automation for integrity and auditing.
-- =============================================================================

-- Function to automatically update the 'updated_at' timestamp on any row update.
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Generic trigger application for 'updated_at'
-- This block will create the trigger for all tables within the 'sgpos' schema
-- that have an 'updated_at' column.
DO $$
DECLARE
    t text;
BEGIN
    FOR t IN SELECT tablename FROM pg_tables WHERE schemaname = 'sgpos' AND EXISTS (SELECT 1 FROM pg_attribute WHERE attrelid = tablename::regclass AND attname = 'updated_at')
    LOOP
        EXECUTE format('CREATE TRIGGER set_updated_at_on_%I BEFORE UPDATE ON sgpos.%I FOR EACH ROW EXECUTE FUNCTION update_updated_at_column()', t, t);
    END LOOP;
END;
$$ LANGUAGE plpgsql;


-- Function to log all changes to designated tables into the audit_logs table.
-- The application should set session variables for user/company context:
-- e.g., SET sgpos.current_user_id = '...'; SET sgpos.current_company_id = '...';
CREATE OR REPLACE FUNCTION log_changes()
RETURNS TRIGGER AS $$
DECLARE
    old_data JSONB;
    new_data JSONB;
    action_type VARCHAR(50);
    current_user UUID;
    current_company UUID;
BEGIN
    -- Attempt to retrieve session variables set by the application
    BEGIN
        current_user := current_setting('sgpos.current_user_id', true)::UUID;
    EXCEPTION WHEN OTHERS THEN
        current_user := NULL;
    END;
    
    BEGIN
        current_company := current_setting('sgpos.current_company_id', true)::UUID;
    EXCEPTION WHEN OTHERS THEN
        current_company := NULL;
    END;

    IF (TG_OP = 'UPDATE') THEN
        old_data := to_jsonb(OLD);
        new_data := to_jsonb(NEW);
        action_type := 'UPDATE_' || UPPER(TG_TABLE_NAME);
        INSERT INTO sgpos.audit_logs (company_id, user_id, action, table_name, record_id, old_values, new_values)
        VALUES (current_company, current_user, action_type, TG_TABLE_NAME, OLD.id, old_data, new_data);
        RETURN NEW;
    ELSIF (TG_OP = 'DELETE') THEN
        old_data := to_jsonb(OLD);
        new_data := NULL;
        action_type := 'DELETE_' || UPPER(TG_TABLE_NAME);
        INSERT INTO sgpos.audit_logs (company_id, user_id, action, table_name, record_id, old_values, new_values)
        VALUES (current_company, current_user, action_type, TG_TABLE_NAME, OLD.id, old_data, new_data);
        RETURN OLD;
    ELSIF (TG_OP = 'INSERT') THEN
        new_data := to_jsonb(NEW);
        old_data := NULL;
        action_type := 'CREATE_' || UPPER(TG_TABLE_NAME);
        INSERT INTO sgpos.audit_logs (company_id, user_id, action, table_name, record_id, old_values, new_values)
        VALUES (current_company, current_user, action_type, TG_TABLE_NAME, NEW.id, old_data, new_data);
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Apply the audit trigger to tables that require a detailed audit trail.
-- These specific triggers must be explicitly created.
CREATE TRIGGER products_audit
AFTER INSERT OR UPDATE OR DELETE ON sgpos.products
FOR EACH ROW EXECUTE FUNCTION sgpos.log_changes();

CREATE TRIGGER customers_audit
AFTER INSERT OR UPDATE OR DELETE ON sgpos.customers
FOR EACH ROW EXECUTE FUNCTION sgpos.log_changes();

CREATE TRIGGER users_audit
AFTER INSERT OR UPDATE OR DELETE ON sgpos.users
FOR EACH ROW EXECUTE FUNCTION sgpos.log_changes();

CREATE TRIGGER sales_transactions_audit
AFTER INSERT OR UPDATE OR DELETE ON sgpos.sales_transactions
FOR EACH ROW EXECUTE FUNCTION sgpos.log_changes();

-- Add other critical tables here as needed for auditing.
-- E.g., CREATE TRIGGER payment_methods_audit AFTER INSERT OR UPDATE OR DELETE ON sgpos.payment_methods FOR EACH ROW EXECUTE FUNCTION sgpos.log_changes();
-- E.g., CREATE TRIGGER inventory_audit AFTER INSERT OR UPDATE OR DELETE ON sgpos.inventory FOR EACH ROW EXECUTE FUNCTION sgpos.log_changes();
-- E.g., CREATE TRIGGER suppliers_audit AFTER INSERT OR UPDATE OR DELETE ON sgpos.suppliers FOR EACH ROW EXECUTE FUNCTION sgpos.log_changes();

```

# migrations/script.py.mako
```mako
# migrations/script.py.mako
"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision}
Create Date: ${create_date}

"""
from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}


def upgrade() -> None:
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    ${downgrades if downgrades else "pass"}

```

# migrations/versions/d5a6759ef2f7_initial_schema_setup.py
```py
# File: migrations/versions/d5a6759ef2f7_initial_schema_setup.py
"""Initial schema setup

Revision ID: d5a6759ef2f7
Revises: 
Create Date: 2025-06-16 00:57:37.705263

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'd5a6759ef2f7'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - adjusted for correctness ###
    op.create_table('companies',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('registration_number', sa.String(length=20), nullable=False),
    sa.Column('gst_registration_number', sa.String(length=20), nullable=True),
    sa.Column('address', sa.Text(), nullable=True),
    sa.Column('phone', sa.String(length=20), nullable=True),
    sa.Column('email', sa.String(length=255), nullable=True),
    sa.Column('base_currency', sa.String(length=3), nullable=False),
    sa.Column('fiscal_year_start', sa.Date(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_companies')),
    sa.UniqueConstraint('gst_registration_number', name=op.f('uq_companies_gst_registration_number')),
    sa.UniqueConstraint('registration_number', name=op.f('uq_companies_registration_number')),
    schema='sgpos'
    )
    op.create_table('permissions',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('action', sa.String(length=100), nullable=False),
    sa.Column('resource', sa.String(length=100), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_permissions')),
    sa.UniqueConstraint('action', 'resource', name='uq_permission_action_resource'),
    schema='sgpos'
    )
    op.create_table('categories',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('company_id', sa.UUID(), nullable=False),
    sa.Column('parent_id', sa.UUID(), nullable=True),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['company_id'], ['sgpos.companies.id'], name=op.f('fk_categories_company_id_companies'), ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['parent_id'], ['sgpos.categories.id'], name=op.f('fk_categories_parent_id_categories'), ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_categories')),
    sa.UniqueConstraint('company_id', 'name', name='uq_category_company_name'),
    schema='sgpos'
    )
    op.create_index(op.f('ix_sgpos_categories_company_id'), 'categories', ['company_id'], unique=False, schema='sgpos')
    op.create_table('chart_of_accounts',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('company_id', sa.UUID(), nullable=False),
    sa.Column('account_code', sa.String(length=20), nullable=False),
    sa.Column('account_name', sa.String(length=255), nullable=False),
    sa.Column('account_type', sa.String(length=50), nullable=False),
    sa.Column('parent_id', sa.UUID(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint("account_type IN ('ASSET', 'LIABILITY', 'EQUITY', 'REVENUE', 'EXPENSE')", name=op.f('ck_chart_of_accounts_chk_account_type')),
    sa.ForeignKeyConstraint(['company_id'], ['sgpos.companies.id'], name=op.f('fk_chart_of_accounts_company_id_companies')),
    sa.ForeignKeyConstraint(['parent_id'], ['sgpos.chart_of_accounts.id'], name=op.f('fk_chart_of_accounts_parent_id_chart_of_accounts')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_chart_of_accounts')),
    sa.UniqueConstraint('company_id', 'account_code', name='uq_coa_company_code'),
    schema='sgpos'
    )
    op.create_index(op.f('ix_sgpos_chart_of_accounts_company_id'), 'chart_of_accounts', ['company_id'], unique=False, schema='sgpos')
    op.create_table('customers',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('company_id', sa.UUID(), nullable=False),
    sa.Column('customer_code', sa.String(length=50), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=True),
    sa.Column('phone', sa.String(length=50), nullable=True),
    sa.Column('address', sa.Text(), nullable=True),
    sa.Column('loyalty_points', sa.Integer(), nullable=False),
    sa.Column('credit_limit', sa.Numeric(precision=19, scale=2), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['company_id'], ['sgpos.companies.id'], name=op.f('fk_customers_company_id_companies'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_customers')),
    sa.UniqueConstraint('company_id', 'customer_code', name='uq_customer_company_code'),
    sa.UniqueConstraint('company_id', 'email', name='uq_customer_company_email'),
    schema='sgpos'
    )
    op.create_index(op.f('ix_sgpos_customers_company_id'), 'customers', ['company_id'], unique=False, schema='sgpos')
    op.create_table('outlets',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('company_id', sa.UUID(), nullable=False),
    sa.Column('code', sa.String(length=50), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('address', sa.Text(), nullable=True),
    sa.Column('phone', sa.String(length=20), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['company_id'], ['sgpos.companies.id'], name=op.f('fk_outlets_company_id_companies'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_outlets')),
    sa.UniqueConstraint('company_id', 'code', name='uq_outlet_company_code'),
    schema='sgpos'
    )
    op.create_index(op.f('ix_sgpos_outlets_company_id'), 'outlets', ['company_id'], unique=False, schema='sgpos')
    op.create_table('payment_methods',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('company_id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('type', sa.String(length=50), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint("type IN ('CASH', 'CARD', 'NETS', 'PAYNOW', 'VOUCHER', 'STORE_CREDIT')", name=op.f('ck_payment_methods_chk_payment_method_type')),
    sa.ForeignKeyConstraint(['company_id'], ['sgpos.companies.id'], name=op.f('fk_payment_methods_company_id_companies')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_payment_methods')),
    sa.UniqueConstraint('company_id', 'name', name='uq_payment_methods_company_name'),
    schema='sgpos'
    )
    op.create_index(op.f('ix_sgpos_payment_methods_company_id'), 'payment_methods', ['company_id'], unique=False, schema='sgpos')
    op.create_table('roles',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('company_id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('is_system_role', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['company_id'], ['sgpos.companies.id'], name=op.f('fk_roles_company_id_companies'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_roles')),
    sa.UniqueConstraint('company_id', 'name', name='uq_role_company_name'),
    schema='sgpos'
    )
    op.create_table('suppliers',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('company_id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('contact_person', sa.String(length=255), nullable=True),
    sa.Column('email', sa.String(length=255), nullable=True),
    sa.Column('phone', sa.String(length=50), nullable=True),
    sa.Column('address', sa.Text(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['company_id'], ['sgpos.companies.id'], name=op.f('fk_suppliers_company_id_companies'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_suppliers')),
    sa.UniqueConstraint('company_id', 'name', name='uq_supplier_company_name'),
    schema='sgpos'
    )
    op.create_index(op.f('ix_sgpos_suppliers_company_id'), 'suppliers', ['company_id'], unique=False, schema='sgpos')
    op.create_table('users',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('company_id', sa.UUID(), nullable=False),
    sa.Column('username', sa.String(length=100), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('password_hash', sa.String(length=255), nullable=False),
    sa.Column('full_name', sa.String(length=255), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['company_id'], ['sgpos.companies.id'], name=op.f('fk_users_company_id_companies'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_users')),
    sa.UniqueConstraint('company_id', 'email', name='uq_user_company_email'),
    sa.UniqueConstraint('company_id', 'username', name='uq_user_company_username'),
    schema='sgpos'
    )
    op.create_index(op.f('ix_sgpos_users_company_id'), 'users', ['company_id'], unique=False, schema='sgpos')
    op.create_table('audit_logs',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('company_id', sa.UUID(), nullable=True),
    sa.Column('user_id', sa.UUID(), nullable=True),
    sa.Column('action', sa.String(length=50), nullable=False),
    sa.Column('table_name', sa.String(length=100), nullable=False),
    sa.Column('record_id', sa.UUID(), nullable=False),
    sa.Column('old_values', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('new_values', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('ip_address', postgresql.INET(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['company_id'], ['sgpos.companies.id'], name=op.f('fk_audit_logs_company_id_companies')),
    sa.ForeignKeyConstraint(['user_id'], ['sgpos.users.id'], name=op.f('fk_audit_logs_user_id_users'), ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_audit_logs')),
    schema='sgpos'
    )
    op.create_index(op.f('ix_sgpos_audit_logs_company_id'), 'audit_logs', ['company_id'], unique=False, schema='sgpos')
    op.create_index(op.f('ix_sgpos_audit_logs_user_id'), 'audit_logs', ['user_id'], unique=False, schema='sgpos')
    op.create_table('journal_entries',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('company_id', sa.UUID(), nullable=False),
    sa.Column('entry_number', sa.String(length=50), nullable=False),
    sa.Column('entry_date', sa.Date(), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('reference_id', sa.UUID(), nullable=True),
    sa.Column('reference_type', sa.String(length=50), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('created_by_user_id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint("status IN ('DRAFT', 'POSTED', 'VOID')", name=op.f('ck_journal_entries_chk_journal_entry_status')),
    sa.ForeignKeyConstraint(['company_id'], ['sgpos.companies.id'], name=op.f('fk_journal_entries_company_id_companies')),
    sa.ForeignKeyConstraint(['created_by_user_id'], ['sgpos.users.id'], name=op.f('fk_journal_entries_created_by_user_id_users')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_journal_entries')),
    sa.UniqueConstraint('company_id', 'entry_number', name='uq_journal_entry_company_number'),
    schema='sgpos'
    )
    op.create_index(op.f('ix_sgpos_journal_entries_company_id'), 'journal_entries', ['company_id'], unique=False, schema='sgpos')
    op.create_index(op.f('ix_sgpos_journal_entries_created_by_user_id'), 'journal_entries', ['created_by_user_id'], unique=False, schema='sgpos')
    op.create_index(op.f('ix_sgpos_journal_entries_reference_id'), 'journal_entries', ['reference_id'], unique=False, schema='sgpos')
    op.create_table('products',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('company_id', sa.UUID(), nullable=False),
    sa.Column('category_id', sa.UUID(), nullable=True),
    sa.Column('supplier_id', sa.UUID(), nullable=True),
    sa.Column('sku', sa.String(length=100), nullable=False),
    sa.Column('barcode', sa.String(length=100), nullable=True),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('cost_price', sa.Numeric(precision=19, scale=4), nullable=False),
    sa.Column('selling_price', sa.Numeric(precision=19, scale=4), nullable=False),
    sa.Column('gst_rate', sa.Numeric(precision=5, scale=2), nullable=False),
    sa.Column('track_inventory', sa.Boolean(), nullable=False),
    sa.Column('reorder_point', sa.Integer(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['category_id'], ['sgpos.categories.id'], name=op.f('fk_products_category_id_categories')),
    sa.ForeignKeyConstraint(['company_id'], ['sgpos.companies.id'], name=op.f('fk_products_company_id_companies'), ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['supplier_id'], ['sgpos.suppliers.id'], name=op.f('fk_products_supplier_id_suppliers')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_products')),
    sa.UniqueConstraint('company_id', 'sku', name='uq_product_company_sku'),
    schema='sgpos'
    )
    op.create_index(op.f('ix_sgpos_products_barcode'), 'products', ['barcode'], unique=False, schema='sgpos')
    op.create_index(op.f('ix_sgpos_products_category_id'), 'products', ['category_id'], unique=False, schema='sgpos')
    op.create_index(op.f('ix_sgpos_products_company_id'), 'products', ['company_id'], unique=False, schema='sgpos')
    op.create_index(op.f('ix_sgpos_products_supplier_id'), 'products', ['supplier_id'], unique=False, schema='sgpos')
    op.create_table('purchase_orders',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('company_id', sa.UUID(), nullable=False),
    sa.Column('outlet_id', sa.UUID(), nullable=False),
    sa.Column('supplier_id', sa.UUID(), nullable=False),
    sa.Column('po_number', sa.String(length=50), nullable=False),
    sa.Column('order_date', sa.DateTime(timezone=True), nullable=False),
    sa.Column('expected_delivery_date', sa.DateTime(timezone=True), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('total_amount', sa.Numeric(precision=19, scale=2), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint("status IN ('DRAFT', 'SENT', 'PARTIALLY_RECEIVED', 'RECEIVED', 'CANCELLED')", name=op.f('ck_purchase_orders_chk_purchase_order_status')),
    sa.ForeignKeyConstraint(['company_id'], ['sgpos.companies.id'], name=op.f('fk_purchase_orders_company_id_companies')),
    sa.ForeignKeyConstraint(['outlet_id'], ['sgpos.outlets.id'], name=op.f('fk_purchase_orders_outlet_id_outlets')),
    sa.ForeignKeyConstraint(['supplier_id'], ['sgpos.suppliers.id'], name=op.f('fk_purchase_orders_supplier_id_suppliers')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_purchase_orders')),
    sa.UniqueConstraint('company_id', 'po_number', name='uq_purchase_order_company_po_number'),
    schema='sgpos'
    )
    op.create_index(op.f('ix_sgpos_purchase_orders_company_id'), 'purchase_orders', ['company_id'], unique=False, schema='sgpos')
    op.create_index(op.f('ix_sgpos_purchase_orders_outlet_id'), 'purchase_orders', ['outlet_id'], unique=False, schema='sgpos')
    op.create_index(op.f('ix_sgpos_purchase_orders_supplier_id'), 'purchase_orders', ['supplier_id'], unique=False, schema='sgpos')
    op.create_table('role_permissions',
    sa.Column('role_id', sa.UUID(), nullable=False),
    sa.Column('permission_id', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['permission_id'], ['sgpos.permissions.id'], name=op.f('fk_role_permissions_permission_id_permissions'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['role_id'], ['sgpos.roles.id'], name=op.f('fk_role_permissions_role_id_roles'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('role_id', 'permission_id', name=op.f('pk_role_permissions')),
    schema='sgpos'
    )
    op.create_table('sales_transactions',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('company_id', sa.UUID(), nullable=False),
    sa.Column('outlet_id', sa.UUID(), nullable=False),
    sa.Column('transaction_number', sa.String(length=50), nullable=False),
    sa.Column('transaction_date', sa.DateTime(timezone=True), nullable=False),
    sa.Column('customer_id', sa.UUID(), nullable=True),
    sa.Column('cashier_id', sa.UUID(), nullable=False),
    sa.Column('subtotal', sa.Numeric(precision=19, scale=2), nullable=False),
    sa.Column('tax_amount', sa.Numeric(precision=19, scale=2), nullable=False),
    sa.Column('discount_amount', sa.Numeric(precision=19, scale=2), nullable=False),
    sa.Column('rounding_adjustment', sa.Numeric(precision=19, scale=2), nullable=False),
    sa.Column('total_amount', sa.Numeric(precision=19, scale=2), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint("status IN ('COMPLETED', 'VOIDED', 'HELD')", name=op.f('ck_sales_transactions_chk_sales_transaction_status')),
    sa.ForeignKeyConstraint(['cashier_id'], ['sgpos.users.id'], name=op.f('fk_sales_transactions_cashier_id_users')),
    sa.ForeignKeyConstraint(['company_id'], ['sgpos.companies.id'], name=op.f('fk_sales_transactions_company_id_companies'), ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['customer_id'], ['sgpos.customers.id'], name=op.f('fk_sales_transactions_customer_id_customers')),
    sa.ForeignKeyConstraint(['outlet_id'], ['sgpos.outlets.id'], name=op.f('fk_sales_transactions_outlet_id_outlets')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_sales_transactions')),
    sa.UniqueConstraint('company_id', 'transaction_number', name='uq_sales_transaction_company_number'),
    schema='sgpos'
    )
    op.create_index(op.f('ix_sgpos_sales_transactions_cashier_id'), 'sales_transactions', ['cashier_id'], unique=False, schema='sgpos')
    op.create_index(op.f('ix_sgpos_sales_transactions_company_id'), 'sales_transactions', ['company_id'], unique=False, schema='sgpos')
    op.create_index(op.f('ix_sgpos_sales_transactions_customer_id'), 'sales_transactions', ['customer_id'], unique=False, schema='sgpos')
    op.create_index(op.f('ix_sgpos_sales_transactions_outlet_id'), 'sales_transactions', ['outlet_id'], unique=False, schema='sgpos')
    op.create_index(op.f('ix_sgpos_sales_transactions_transaction_date'), 'sales_transactions', ['transaction_date'], unique=False, schema='sgpos')
    op.create_table('user_roles',
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('role_id', sa.UUID(), nullable=False),
    sa.Column('outlet_id', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['outlet_id'], ['sgpos.outlets.id'], name=op.f('fk_user_roles_outlet_id_outlets'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['role_id'], ['sgpos.roles.id'], name=op.f('fk_user_roles_role_id_roles'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['sgpos.users.id'], name=op.f('fk_user_roles_user_id_users'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('user_id', 'role_id', 'outlet_id', name=op.f('pk_user_roles')),
    schema='sgpos'
    )
    op.create_table('journal_entry_lines',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('journal_entry_id', sa.UUID(), nullable=False),
    sa.Column('account_id', sa.UUID(), nullable=False),
    sa.Column('debit_amount', sa.Numeric(precision=19, scale=2), nullable=False),
    sa.Column('credit_amount', sa.Numeric(precision=19, scale=2), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint("(debit_amount > 0 AND credit_amount = 0) OR (credit_amount > 0 AND debit_amount = 0)", name=op.f('ck_journal_entry_lines_debit_or_credit_check')),
    sa.ForeignKeyConstraint(['account_id'], ['sgpos.chart_of_accounts.id'], name=op.f('fk_journal_entry_lines_account_id_chart_of_accounts')),
    sa.ForeignKeyConstraint(['journal_entry_id'], ['sgpos.journal_entries.id'], name=op.f('fk_journal_entry_lines_journal_entry_id_journal_entries'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_journal_entry_lines')),
    schema='sgpos'
    )
    op.create_index(op.f('ix_sgpos_journal_entry_lines_account_id'), 'journal_entry_lines', ['account_id'], unique=False, schema='sgpos')
    op.create_index(op.f('ix_sgpos_journal_entry_lines_journal_entry_id'), 'journal_entry_lines', ['journal_entry_id'], unique=False, schema='sgpos')
    op.create_table('payments',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('sales_transaction_id', sa.UUID(), nullable=False),
    sa.Column('payment_method_id', sa.UUID(), nullable=False),
    sa.Column('amount', sa.Numeric(precision=19, scale=2), nullable=False),
    sa.Column('reference_number', sa.String(length=100), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['payment_method_id'], ['sgpos.payment_methods.id'], name=op.f('fk_payments_payment_method_id_payment_methods')),
    sa.ForeignKeyConstraint(['sales_transaction_id'], ['sgpos.sales_transactions.id'], name=op.f('fk_payments_sales_transaction_id_sales_transactions'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_payments')),
    schema='sgpos'
    )
    op.create_index(op.f('ix_sgpos_payments_payment_method_id'), 'payments', ['payment_method_id'], unique=False, schema='sgpos')
    op.create_index(op.f('ix_sgpos_payments_sales_transaction_id'), 'payments', ['sales_transaction_id'], unique=False, schema='sgpos')
    op.create_table('product_variants',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('product_id', sa.UUID(), nullable=False),
    sa.Column('sku_suffix', sa.String(length=100), nullable=False),
    sa.Column('barcode', sa.String(length=100), nullable=True),
    sa.Column('attributes', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('cost_price_override', sa.Numeric(precision=19, scale=4), nullable=True),
    sa.Column('selling_price_override', sa.Numeric(precision=19, scale=4), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['product_id'], ['sgpos.products.id'], name=op.f('fk_product_variants_product_id_products'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_product_variants')),
    sa.UniqueConstraint('product_id', 'sku_suffix', name='uq_product_variant_sku_suffix'),
    schema='sgpos'
    )
    op.create_index(op.f('ix_sgpos_product_variants_product_id'), 'product_variants', ['product_id'], unique=False, schema='sgpos')
    op.create_table('inventory',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('outlet_id', sa.UUID(), nullable=False),
    sa.Column('product_id', sa.UUID(), nullable=False),
    sa.Column('variant_id', sa.UUID(), nullable=True),
    sa.Column('quantity_on_hand', sa.Numeric(precision=15, scale=4), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['outlet_id'], ['sgpos.outlets.id'], name=op.f('fk_inventory_outlet_id_outlets'), ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['product_id'], ['sgpos.products.id'], name=op.f('fk_inventory_product_id_products'), ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['variant_id'], ['sgpos.product_variants.id'], name=op.f('fk_inventory_variant_id_product_variants'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_inventory')),
    sa.UniqueConstraint('outlet_id', 'product_id', 'variant_id', name='uq_inventory_outlet_product_variant'),
    schema='sgpos'
    )
    op.create_index(op.f('ix_sgpos_inventory_outlet_id'), 'inventory', ['outlet_id'], unique=False, schema='sgpos')
    op.create_index(op.f('ix_sgpos_inventory_product_id'), 'inventory', ['product_id'], unique=False, schema='sgpos')
    op.create_index(op.f('ix_sgpos_inventory_variant_id'), 'inventory', ['variant_id'], unique=False, schema='sgpos')
    op.create_table('purchase_order_items',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('purchase_order_id', sa.UUID(), nullable=False),
    sa.Column('product_id', sa.UUID(), nullable=False),
    sa.Column('variant_id', sa.UUID(), nullable=True),
    sa.Column('quantity_ordered', sa.Numeric(precision=15, scale=4), nullable=False),
    sa.Column('quantity_received', sa.Numeric(precision=15, scale=4), nullable=False),
    sa.Column('unit_cost', sa.Numeric(precision=19, scale=4), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['product_id'], ['sgpos.products.id'], name=op.f('fk_purchase_order_items_product_id_products')),
    sa.ForeignKeyConstraint(['purchase_order_id'], ['sgpos.purchase_orders.id'], name=op.f('fk_purchase_order_items_purchase_order_id_purchase_orders'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['variant_id'], ['sgpos.product_variants.id'], name=op.f('fk_purchase_order_items_variant_id_product_variants')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_purchase_order_items')),
    sa.UniqueConstraint('purchase_order_id', 'product_id', 'variant_id', name='uq_po_item_po_product_variant'),
    schema='sgpos'
    )
    op.create_index(op.f('ix_sgpos_purchase_order_items_product_id'), 'purchase_order_items', ['product_id'], unique=False, schema='sgpos')
    op.create_index(op.f('ix_sgpos_purchase_order_items_purchase_order_id'), 'purchase_order_items', ['purchase_order_id'], unique=False, schema='sgpos')
    op.create_index(op.f('ix_sgpos_purchase_order_items_variant_id'), 'purchase_order_items', ['variant_id'], unique=False, schema='sgpos')
    op.create_table('sales_transaction_items',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('sales_transaction_id', sa.UUID(), nullable=False),
    sa.Column('product_id', sa.UUID(), nullable=False),
    sa.Column('variant_id', sa.UUID(), nullable=True),
    sa.Column('quantity', sa.Numeric(precision=15, scale=4), nullable=False),
    sa.Column('unit_price', sa.Numeric(precision=19, scale=4), nullable=False),
    sa.Column('cost_price', sa.Numeric(precision=19, scale=4), nullable=False),
    sa.Column('line_total', sa.Numeric(precision=19, scale=2), nullable=False),
    sa.ForeignKeyConstraint(['product_id'], ['sgpos.products.id'], name=op.f('fk_sales_transaction_items_product_id_products')),
    sa.ForeignKeyConstraint(['sales_transaction_id'], ['sgpos.sales_transactions.id'], name=op.f('fk_sales_transaction_items_sales_transaction_id_sales_transactions'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['variant_id'], ['sgpos.product_variants.id'], name=op.f('fk_sales_transaction_items_variant_id_product_variants')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_sales_transaction_items')),
    sa.UniqueConstraint('sales_transaction_id', 'product_id', 'variant_id', name='uq_sales_item_transaction_product_variant'),
    schema='sgpos'
    )
    op.create_index(op.f('ix_sgpos_sales_transaction_items_product_id'), 'sales_transaction_items', ['product_id'], unique=False, schema='sgpos')
    op.create_index(op.f('ix_sgpos_sales_transaction_items_sales_transaction_id'), 'sales_transaction_items', ['sales_transaction_id'], unique=False, schema='sgpos')
    op.create_index(op.f('ix_sgpos_sales_transaction_items_variant_id'), 'sales_transaction_items', ['variant_id'], unique=False, schema='sgpos')
    op.create_table('stock_movements',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('company_id', sa.UUID(), nullable=False),
    sa.Column('outlet_id', sa.UUID(), nullable=False),
    sa.Column('product_id', sa.UUID(), nullable=False),
    sa.Column('variant_id', sa.UUID(), nullable=True),
    sa.Column('movement_type', sa.String(length=50), nullable=False),
    sa.Column('quantity_change', sa.Numeric(precision=15, scale=4), nullable=False),
    sa.Column('reference_id', sa.UUID(), nullable=True),
    sa.Column('reference_type', sa.String(length=50), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('created_by_user_id', sa.UUID(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.CheckConstraint("movement_type IN ('SALE', 'RETURN', 'PURCHASE', 'ADJUSTMENT_IN', 'ADJUSTMENT_OUT', 'TRANSFER_IN', 'TRANSFER_OUT')", name=op.f('ck_stock_movements_chk_stock_movement_type')),
    sa.ForeignKeyConstraint(['company_id'], ['sgpos.companies.id'], name=op.f('fk_stock_movements_company_id_companies')),
    sa.ForeignKeyConstraint(['created_by_user_id'], ['sgpos.users.id'], name=op.f('fk_stock_movements_created_by_user_id_users')),
    sa.ForeignKeyConstraint(['outlet_id'], ['sgpos.outlets.id'], name=op.f('fk_stock_movements_outlet_id_outlets')),
    sa.ForeignKeyConstraint(['product_id'], ['sgpos.products.id'], name=op.f('fk_stock_movements_product_id_products')),
    sa.ForeignKeyConstraint(['variant_id'], ['sgpos.product_variants.id'], name=op.f('fk_stock_movements_variant_id_product_variants')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_stock_movements')),
    schema='sgpos'
    )
    op.create_index(op.f('ix_sgpos_stock_movements_company_id'), 'stock_movements', ['company_id'], unique=False, schema='sgpos')
    op.create_index(op.f('ix_sgpos_stock_movements_created_by_user_id'), 'stock_movements', ['created_by_user_id'], unique=False, schema='sgpos')
    op.create_index(op.f('ix_sgpos_stock_movements_outlet_id'), 'stock_movements', ['outlet_id'], unique=False, schema='sgpos')
    op.create_index(op.f('ix_sgpos_stock_movements_product_id'), 'stock_movements', ['product_id'], unique=False, schema='sgpos')
    op.create_index(op.f('ix_sgpos_stock_movements_variant_id'), 'stock_movements', ['variant_id'], unique=False, schema='sgpos')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_sgpos_stock_movements_variant_id'), table_name='stock_movements', schema='sgpos')
    op.drop_index(op.f('ix_sgpos_stock_movements_product_id'), table_name='stock_movements', schema='sgpos')
    op.drop_index(op.f('ix_sgpos_stock_movements_outlet_id'), table_name='stock_movements', schema='sgpos')
    op.drop_index(op.f('ix_sgpos_stock_movements_created_by_user_id'), table_name='stock_movements', schema='sgpos')
    op.drop_index(op.f('ix_sgpos_stock_movements_company_id'), table_name='stock_movements', schema='sgpos')
    op.drop_table('stock_movements', schema='sgpos')
    op.drop_index(op.f('ix_sgpos_sales_transaction_items_variant_id'), table_name='sales_transaction_items', schema='sgpos')
    op.drop_index(op.f('ix_sgpos_sales_transaction_items_sales_transaction_id'), table_name='sales_transaction_items', schema='sgpos')
    op.drop_index(op.f('ix_sgpos_sales_transaction_items_product_id'), table_name='sales_transaction_items', schema='sgpos')
    op.drop_table('sales_transaction_items', schema='sgpos')
    op.drop_index(op.f('ix_sgpos_purchase_order_items_variant_id'), table_name='purchase_order_items', schema='sgpos')
    op.drop_index(op.f('ix_sgpos_purchase_order_items_purchase_order_id'), table_name='purchase_order_items', schema='sgpos')
    op.drop_index(op.f('ix_sgpos_purchase_order_items_product_id'), table_name='purchase_order_items', schema='sgpos')
    op.drop_table('purchase_order_items', schema='sgpos')
    op.drop_index(op.f('ix_sgpos_inventory_variant_id'), table_name='inventory', schema='sgpos')
    op.drop_index(op.f('ix_sgpos_inventory_product_id'), table_name='inventory', schema='sgpos')
    op.drop_index(op.f('ix_sgpos_inventory_outlet_id'), table_name='inventory', schema='sgpos')
    op.drop_table('inventory', schema='sgpos')
    op.drop_index(op.f('ix_sgpos_product_variants_product_id'), table_name='product_variants', schema='sgpos')
    op.drop_table('product_variants', schema='sgpos')
    op.drop_index(op.f('ix_sgpos_payments_sales_transaction_id'), table_name='payments', schema='sgpos')
    op.drop_index(op.f('ix_sgpos_payments_payment_method_id'), table_name='payments', schema='sgpos')
    op.drop_table('payments', schema='sgpos')
    op.drop_index(op.f('ix_sgpos_journal_entry_lines_journal_entry_id'), table_name='journal_entry_lines', schema='sgpos')
    op.drop_index(op.f('ix_sgpos_journal_entry_lines_account_id'), table_name='journal_entry_lines', schema='sgpos')
    op.drop_table('journal_entry_lines', schema='sgpos')
    op.drop_table('user_roles', schema='sgpos')
    op.drop_index(op.f('ix_sgpos_sales_transactions_transaction_date'), table_name='sales_transactions', schema='sgpos')
    op.drop_index(op.f('ix_sgpos_sales_transactions_outlet_id'), table_name='sales_transactions', schema='sgpos')
    op.drop_index(op.f('ix_sgpos_sales_transactions_customer_id'), table_name='sales_transactions', schema='sgpos')
    op.drop_index(op.f('ix_sgpos_sales_transactions_company_id'), table_name='sales_transactions', schema='sgpos')
    op.drop_index(op.f('ix_sgpos_sales_transactions_cashier_id'), table_name='sales_transactions', schema='sgpos')
    op.drop_table('sales_transactions', schema='sgpos')
    op.drop_table('role_permissions', schema='sgpos')
    op.drop_index(op.f('ix_sgpos_purchase_orders_supplier_id'), table_name='purchase_orders', schema='sgpos')
    op.drop_index(op.f('ix_sgpos_purchase_orders_outlet_id'), table_name='purchase_orders', schema='sgpos')
    op.drop_index(op.f('ix_sgpos_purchase_orders_company_id'), table_name='purchase_orders', schema='sgpos')
    op.drop_table('purchase_orders', schema='sgpos')
    op.drop_index(op.f('ix_sgpos_products_supplier_id'), table_name='products', schema='sgpos')
    op.drop_index(op.f('ix_sgpos_products_company_id'), table_name='products', schema='sgpos')
    op.drop_index(op.f('ix_sgpos_products_category_id'), table_name='products', schema='sgpos')
    op.drop_index(op.f('ix_sgpos_products_barcode'), table_name='products', schema='sgpos')
    op.drop_table('products', schema='sgpos')
    op.drop_index(op.f('ix_sgpos_journal_entries_reference_id'), table_name='journal_entries', schema='sgpos')
    op.drop_index(op.f('ix_sgpos_journal_entries_created_by_user_id'), table_name='journal_entries', schema='sgpos')
    op.drop_index(op.f('ix_sgpos_journal_entries_company_id'), table_name='journal_entries', schema='sgpos')
    op.drop_table('journal_entries', schema='sgpos')
    op.drop_index(op.f('ix_sgpos_audit_logs_user_id'), table_name='audit_logs', schema='sgpos')
    op.drop_index(op.f('ix_sgpos_audit_logs_company_id'), table_name='audit_logs', schema='sgpos')
    op.drop_table('audit_logs', schema='sgpos')
    op.drop_index(op.f('ix_sgpos_users_company_id'), table_name='users', schema='sgpos')
    op.drop_table('users', schema='sgpos')
    op.drop_index(op.f('ix_sgpos_suppliers_company_id'), table_name='suppliers', schema='sgpos')
    op.drop_table('suppliers', schema='sgpos')
    op.drop_table('roles', schema='sgpos')
    op.drop_index(op.f('ix_sgpos_payment_methods_company_id'), table_name='payment_methods', schema='sgpos')
    op.drop_table('payment_methods', schema='sgpos')
    op.drop_index(op.f('ix_sgpos_outlets_company_id'), table_name='outlets', schema='sgpos')
    op.drop_table('outlets', schema='sgpos')
    op.drop_index(op.f('ix_sgpos_customers_company_id'), table_name='customers', schema='sgpos')
    op.drop_table('customers', schema='sgpos')
    op.drop_index(op.f('ix_sgpos_chart_of_accounts_company_id'), table_name='chart_of_accounts', schema='sgpos')
    op.drop_table('chart_of_accounts', schema='sgpos')
    op.drop_index(op.f('ix_sgpos_categories_company_id'), table_name='categories', schema='sgpos')
    op.drop_table('categories', schema='sgpos')
    op.drop_table('permissions', schema='sgpos')
    op.drop_table('companies', schema='sgpos')
    # ### end Alembic commands ###

```

# migrations/env.py
```py
# File: migrations/env.py
import sys
import os 
from logging.config import fileConfig
import asyncio # Import asyncio for the new run_migrations_online

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from sqlalchemy import text 

from alembic import context

# NEW: Import load_dotenv from python-dotenv
from dotenv import load_dotenv

# Add the project's root directory to sys.path
# This allows 'app' modules to be imported correctly regardless of
# where the alembic command is executed from.
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# NEW: Load environment variables from .env.dev file
# This must be done BEFORE alembic tries to read config values
load_dotenv(os.path.join(project_root, '.env.dev'))

# This is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
from app.models.base import Base # IMPORTANT: Import your Base

# IMPORT ALL YOUR ORM MODELS HERE SO ALEMBIC CAN DETECT THEM FOR AUTOGENERATE
# Using '*' imports all classes defined in these modules.
from app.models.company import *
from app.models.user import *
from app.models.product import *
from app.models.inventory import *
from app.models.customer import *
from app.models.sales import *
from app.models.accounting import *
from app.models.audit_log import *


target_metadata = Base.metadata # IMPORTANT: Set this to your Base.metadata

# Retrieve DATABASE_URL explicitly from environment after dotenv loads it
db_url = os.environ.get("DATABASE_URL")
if db_url is None:
    raise Exception("DATABASE_URL environment variable is not set. Please ensure .env.dev is configured correctly or the variable is in your environment.")

# Modify the DATABASE_URL to use psycopg2 (synchronous driver) for Alembic.
# This avoids the "MissingGreenlet" error as Alembic runs synchronously.
# The application itself will continue to use asyncpg.
if db_url.startswith("postgresql+asyncpg"):
    alembic_db_url = db_url.replace("postgresql+asyncpg", "postgresql+psycopg2", 1) # Only replace first occurrence
else:
    alembic_db_url = db_url # Use as is if it's not asyncpg

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a database to begin with.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    # Use the explicitly loaded alembic_db_url instead of config.get_main_option
    context.configure(
        url=alembic_db_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # IMPORTANT: Tell Alembic to manage its version table within the 'sgpos' schema
        version_table_schema=target_metadata.schema if target_metadata and target_metadata.schema else None
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    """Helper function to run the migrations within a context."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        # IMPORTANT: Tell Alembic to manage its version table within the 'sgpos' schema
        version_table_schema=target_metadata.schema if target_metadata and target_metadata.schema else None
    )

    with context.begin_transaction():
        # Ensure the schema exists before running migrations
        context.execute(text(f"CREATE SCHEMA IF NOT EXISTS {target_metadata.schema}"))
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.
    This online migration is now async to support creating an async engine.
    """
    # Create an engine and connect to the database.
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        url=alembic_db_url
    )

    with connectable.connect() as connection:
        do_run_migrations(connection)

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

```

# tests/integration/__init__.py
```py

```

# tests/__init__.py
```py

```

# tests/conftest.py
```py

```

# tests/unit/__init__.py
```py

```

# 'README (draft - to be updated to reflect current state of the codebase more accurately).md'
```md
<p align="center">
  <img src="https://raw.githubusercontent.com/nordeim/SG-Point-Of-Sale/refs/heads/main/POS_home_screen.png" alt="SG-POS System Logo" width="600"/>
</p>

<h1 align="center">SG Point-of-Sale (SG-POS) System</h1>

<p align="center">
  <strong>An enterprise-grade, open-source Point-of-Sale system, meticulously engineered for Singapore's SMB retail landscape.</strong>
</p>

<p align="center">
  <!-- Badges -->
  <a href="#">
    <img src="https://img.shields.io/badge/Status-In%20Development-orange" alt="Project Status">
  </a>
  <a href="https://github.com/your-org/sg-pos-system/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License: MIT">
  </a>
  <a href="https://www.python.org/">
    <img src="https://img.shields.io/badge/Python-3.11+-3776AB.svg" alt="Python 3.11+">
  </a>
  <a href="https://www.qt.io/">
    <img src="https://img.shields.io/badge/UI-PySide6%20(Qt6)-41CD52.svg" alt="PySide6">
  </a>
  <a href="https://www.postgresql.org/">
    <img src="https://img.shields.io/badge/Database-PostgreSQL-336791.svg" alt="PostgreSQL">
  </a>
  <a href="https://github.com/psf/black">
    <img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Code style: black">
  </a>
</p>

---

## 📖 Table of Contents

*   [1. Introduction: What is SG-POS?](#1-introduction-what-is-sg-pos)
*   [2. Current Features & Status](#2-current-features--status)
*   [3. Architectural Deep Dive](#3-architectural-deep-dive)
    *   [The Layered Architecture](#the-layered-architecture)
    *   [Module Interaction Flowchart](#module-interaction-flowchart)
*   [4. Codebase Deep Dive](#4-codebase-deep-dive)
    *   [Project File Hierarchy](#project-file-hierarchy)
    *   [Key File & Directory Descriptions](#key-file--directory-descriptions)
*   [5. Technology Stack](#5-technology-stack)
*   [6. Developer Setup & Deployment Guide](#6-developer-setup--deployment-guide)
    *   [Prerequisites](#prerequisites)
    *   [Step-by-Step Setup Guide](#step-by-step-setup-guide)
*   [7. User Guide: Running the Application](#7-user-guide-running-the-application)
*   [8. Project Roadmap](#8-project-roadmap)
    *   [Immediate Goals (v1.0.1)](#immediate-goals-v101)
    *   [Long-Term Goals (v1.1+)](#long-term-goals-v11)
*   [9. How to Contribute](#9-how-to-contribute)
*   [10. License](#10-license)

---

## **1. Introduction: What is SG-POS?**

**SG-POS** is a free and open-source Point-of-Sale system, engineered from the ground up to address the specific operational and regulatory challenges faced by Small to Medium-sized Businesses (SMBs) in Singapore. It aims to provide the power and polish of expensive enterprise systems in an accessible, modern, and maintainable package.

This project is built with an obsessive focus on quality, both in the user experience and, most importantly, in the engineering. It serves not only as a functional tool but also as a reference implementation for professional-grade Python application architecture.

---

## **2. Current Features & Status**

The application is currently in a feature-complete skeleton state, with the core architecture and many key workflows fully implemented.

| Feature Area                      | Status                  | Notes                                                                                                         |
| --------------------------------- | ----------------------- | ------------------------------------------------------------------------------------------------------------- |
| **Sales & Checkout**              | ✅ **Functional**       | Core sales processing, cart management, and payment collection via the `POSView` and `PaymentDialog` are working. |
| **Customer Management**           | ✅ **Functional**       | Full CRUD (Create, Read, Update, Deactivate) operations for customers are implemented in `CustomerView`.      |
| **Inventory Management**          | ✅ **Functional**       | `InventoryView` provides a stock summary, PO management, and stock movement history.                          |
| **Purchase Orders & Stock-ins**   | ✅ **Functional**       | Creation of Purchase Orders and stock adjustments are fully implemented via dialogs.                          |
| **Reporting & Analytics**         | ✅ **Functional**       | The backend `ReportingManager` and `GstManager` correctly generate data for all implemented reports.          |
| **User & Company Settings**       | 🟡 **Partially Implemented** | `SettingsView` can display company and user info. Role assignment logic is a backend `TODO`.                |
| **Product Management**            | 🔴 **Placeholder**      | The `ProductView` UI is a placeholder. The backend logic is complete, but the UI is not yet functional.     |

---

## **3. Architectural Deep Dive**

SG-POS is built on a set of robust architectural principles designed for maintainability and scalability.

### The Layered Architecture

Our architecture strictly separates the application into four logical layers:

1.  **Presentation Layer (`app/ui`):** Built with PySide6, this layer is responsible *only* for what the user sees and how they interact with it. It contains no business logic.
2.  **Business Logic Layer (`app/business_logic`):** The brain of the application. `Managers` orchestrate workflows and enforce business rules, using `DTOs` (Data Transfer Objects) as data contracts.
3.  **Data Access Layer (`app/services`):** Implements the Repository Pattern. It provides a clean, abstract API (e.g., `product_service.get_by_sku()`) for database operations, hiding SQL complexity.
4.  **Persistence Layer (`app/models`):** Defines the database schema using SQLAlchemy ORM models, which map directly to PostgreSQL tables.

### Module Interaction Flowchart

The flow of control and data is unidirectional and decoupled, ensuring a responsive UI and testable components. The `ApplicationCore` acts as a Dependency Injection (DI) container, providing services and managers to the components that need them.

```mermaid
graph TD
    subgraph "User Interface (app/ui)"
        direction TB
        A[Views & Dialogs] -- "1. User Action" --> B{Async Bridge};
    end

    subgraph "Business Logic (app/business_logic)"
        direction TB
        C[Managers] --> D[Data Transfer Objects (DTOs)];
    end

    subgraph "Data Access (app/services)"
        direction TB
        E[Services (Repositories)];
    end

    subgraph "Data Model (app/models)"
        direction TB
        F[ORM Models (SQLAlchemy)];
    end
    
    subgraph "Database"
        direction TB
        G[PostgreSQL];
    end

    subgraph "Application Core (app/core)"
        direction TB
        H[ApplicationCore (DI Container)] -- Manages --> I[Async Worker];
    end

    %% Interactions
    B -- "2. Submits Task to Worker Thread" --> I;
    I -- "3. Executes Task" --> C;
    H -- Provides Dependencies --> C;
    C -- "4. Orchestrates Logic" --> E;
    E -- "5. Queries Database" --> F;
    F -- "6. Maps to" --> G;
    E -- "7. Returns ORM Models" --> C;
    C -- "8. Converts to DTOs" --> D;
    C -- "9. Returns Result(DTO)" --> I;
    I -- "10. Signals Result" --> B;
    B -- "11. Delivers to UI Callback" --> A;

```
---

## **4. Codebase Deep Dive**

### Project File Hierarchy

```
sg-pos-system/
├── app/
│   ├── core/
│   ├── models/
│   ├── services/
│   ├── business_logic/
│   │   ├── dto/
│   │   └── managers/
│   ├── ui/
│   │   ├── dialogs/
│   │   ├── resources/
│   │   ├── views/
│   │   └── widgets/
│   ├── integrations/
│   └── main.py
├── migrations/
│   ├── versions/
│   └── env.py
├── scripts/
│   └── database/
├── tests/
├── .env.example
├── alembic.ini
├── docker-compose.dev.yml
└── pyproject.toml
```

### Key File & Directory Descriptions

| Path                             | Description                                                                                              |
| -------------------------------- | -------------------------------------------------------------------------------------------------------- |
| `pyproject.toml`                 | **Project Definition.** Manages all dependencies, project metadata, and development tool configurations.     |
| `docker-compose.dev.yml`         | **Database Service.** Defines and configures the PostgreSQL database container for local development.        |
| `alembic.ini` / `migrations/`    | **Database Migrations.** Configuration and scripts for managing database schema evolution using Alembic. |
| `app/main.py`                    | **Application Entry Point.** Initializes the application core, the UI, and starts the event loop.        |
| `app/core/`                      | **The Backbone.** Contains the `ApplicationCore` (DI container), `async_bridge`, `config`, and `Result` pattern. |
| `app/models/`                    | **Persistence Layer.** Defines all SQLAlchemy ORM models, mirroring the database tables.               |
| `app/services/`                  | **Data Access Layer.** Implements the Repository pattern; contains all database query logic.         |
| `app/business_logic/managers/`   | **Business Logic Layer.** Orchestrates workflows, enforces business rules, and makes decisions.        |
| `app/business_logic/dto/`        | **Data Contracts.** Pydantic models that define the structure of data passed between layers.           |
| `app/ui/views/`                  | **Main UI Screens.** The primary user-facing views like the POS screen, inventory, and settings panels. |
| `app/ui/dialogs/`                | **Interactive Dialogs.** Contains dialog windows for specific operations like making a payment or a PO. |

---

## **5. Technology Stack**

This project uses a modern, professional-grade technology stack.

| Category          | Technology                                         | Rationale                                                                                                   |
| ----------------- | -------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| **Language**      | Python 3.11+                                       | Modern features, performance improvements, and strong ecosystem.                                            |
| **GUI Framework** | PySide6 (Qt 6)                                     | The gold standard for professional, high-performance, cross-platform desktop applications in Python.        |
| **Database**      | PostgreSQL 16+                                     | Unmatched reliability, scalability, and feature set for handling critical business and financial data.      |
| **ORM**           | SQLAlchemy 2.0                                     | Industry-leading Object-Relational Mapper with powerful features and excellent async support.               |
| **DB Migrations** | Alembic                                            | The standard for managing database schema changes with SQLAlchemy.                                          |
| **Async**         | `asyncio`                                          | Python's native library for writing concurrent code, essential for a responsive application.                |
| **Testing**       | `pytest`, `pytest-qt`, `pytest-asyncio`            | A powerful and flexible testing ecosystem that covers all aspects of our application (core, UI, async).      |
| **Packaging**     | Poetry                                             | Modern, reliable dependency management and packaging that guarantees reproducible environments.             |
| **Code Quality**  | Black (Formatter), Ruff (Linter), MyPy (Type Checker)| A trifecta of tools to enforce code style, catch bugs early, and ensure long-term maintainability.          |

---

## **6. Developer Setup & Deployment Guide**

This guide provides step-by-step instructions to set up a complete local development environment.

### Prerequisites

*   **Git:** For version control.
*   **Python 3.11+:** Make sure it's installed and available in your `PATH`.
*   **Poetry:** For managing dependencies. See the [official installation guide](https://python-poetry.org/docs/#installation).
*   **Docker & Docker Compose:** To run the PostgreSQL database locally without needing to install it on your system.

### Step-by-Step Setup Guide

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/your-org/sg-pos-system.git
    cd sg-pos-system
    ```

2.  **Configure Environment Variables**
    Copy the example environment file. No changes are needed for a standard local setup.
    ```bash
    cp .env.example .env.dev
    ```

3.  **Start the Database Server**
    This command downloads the PostgreSQL image (if not present) and starts the database container in the background.
    ```bash
    docker compose -f docker-compose.dev.yml up -d
    ```
    You can check if the database is ready by running `docker logs sgpos_dev_db`.

4.  **Install Project Dependencies**
    Poetry will read the `pyproject.toml` file, create a virtual environment, and install all necessary production and development packages.
    ```bash
    poetry install
    ```

5.  **Activate the Virtual Environment**
    All subsequent commands must be run inside this environment to use the installed packages.
    ```bash
    poetry shell
    ```

6.  **Run Database Migrations**
    This command connects to the database and creates all the tables defined in `app/models`.
    ```bash
    alembic upgrade head
    ```

7.  **Run the Application**
    You are now ready to launch the POS system.
    ```bash
    python app/main.py
    ```

---

## **7. User Guide: Running the Application**

Once the application is running, here is a brief guide on how to use it:

*   **Main Window:** The application opens to the main `POSView`, ready for a sale.
*   **Navigation:** Use the menu bar at the top of the window (`File`, `POS`, `Data Management`, `Inventory`, etc.) to switch between different sections of the application.
*   **Making a Sale:**
    1.  In the `POSView`, use the "Product" search bar on the right to find an item by its SKU.
    2.  Click "Add to Cart". The item will appear in the "Current Sale Items" list on the left.
    3.  When all items are added, click the green "PAY" button.
    4.  In the `PaymentDialog`, add one or more payment methods until the balance is zero.
    5.  Click "Finalize Sale" to complete the transaction.
*   **Managing Data:** Navigate to `Data Management > Customers` or `Inventory > Current Stock` to view, add, and edit data. Most views follow a similar pattern of a search bar, an action button (`Add`, `Edit`), and a table displaying the data.

---

## **8. Project Roadmap**

### Immediate Goals (v1.0.1)

These tasks focus on fixing bugs, completing existing features, and improving developer experience.

*   [ ] **Fix Product Dialog:** Implement the asynchronous save logic in `app/ui/dialogs/product_dialog.py`.
*   [ ] **Complete User Roles:** Implement the role assignment logic in `app/business_logic/managers/user_manager.py`.
*   [ ] **Implement Product View:** Build a functional `QAbstractTableModel` and data loading logic for `app/ui/views/product_view.py`.
*   [ ] **Align Database Migrations:** Correct the initial Alembic migration file to match the latest ORM models, especially in `journal_entries`.
*   [ ] **Create Contribution Docs:** Write the `CONTRIBUTING.md` and `CODE_OF_CONDUCT.md` files.

### Long-Term Goals (v1.1+)

These are larger features that build on the stable foundation.

*   [ ] **Advanced Promotions Module:** Implement logic for complex discounts (e.g., "Buy One Get One", tiered discounts).
*   [ ] **Multi-Location Inventory:** Build features for transferring stock between different outlets.
*   [ ] **Accounting Integration:** Add functionality to export sales and purchase data to formats compatible with Xero and QuickBooks.
*   [ ] **E-commerce Connector:** Develop an integration with Shopify to sync products and inventory levels.
*   [ ] **Cloud Backend (v2.0):** Architect a cloud-based version of the backend to support a mobile companion app and centralized data management for multi-outlet businesses.

---

## **9. How to Contribute**

We welcome contributions from the community! Whether you're fixing a bug, adding a new feature, or improving documentation, your help is valued.

**Our contribution workflow is simple:**

1.  **Find an issue:** Look for issues tagged with `good first issue` or `help wanted` on our GitHub Issues page.
2.  **Fork the repository:** Create your own copy of the project.
3.  **Create a feature branch:** `git checkout -b feature/your-awesome-feature`.
4.  **Make your changes:** Write your code and make sure to add corresponding tests.
5.  **Run all checks:** Before pushing, ensure your code passes all quality checks: `pytest`, `black .`, `ruff .`, `mypy app`.
6.  **Submit a Pull Request (PR):** Push your branch to your fork and open a PR against our `main` branch.
7.  **Code Review:** Your PR will be reviewed by the maintainers.

*(A detailed CONTRIBUTING.md file is in the repo).*

---

## **10. License**

This project is licensed under the **MIT License**. See the `LICENSE` file for full details. You are free to use, modify, and distribute this software, but it is provided "as is" without warranty.

```

# CODE_OF_CONDUCT.md
```md
# Contributor Covenant Code of Conduct

## Our Pledge

We as members, contributors, and leaders pledge to make participation in our
community a harassment-free experience for everyone, regardless of age, body
size, visible or invisible disability, ethnicity, sex characteristics, gender
identity and expression, level of experience, education, socio-economic status,
nationality, personal appearance, race, religion, or sexual identity
and orientation.

We pledge to act and interact in ways that contribute to an open, welcoming,
diverse, inclusive, and healthy community.

## Our Standards

Examples of behavior that contributes to a positive environment for our
community include:

*   Demonstrating empathy and kindness toward other people
*   Being respectful of differing opinions, viewpoints, and experiences
*   Giving and gracefully accepting constructive feedback
*   Accepting responsibility and apologizing to those affected by our mistakes,
    and learning from the experience
*   Focusing on what is best not just for us as individuals, but for the
    overall community

Examples of unacceptable behavior include:

*   The use of sexualized language or imagery, and sexual attention or
    advances of any kind
*   Trolling, insulting or derogatory comments, and personal or political attacks
*   Public or private harassment
*   Publishing others' private information, such as a physical or email
    address, without their explicit permission
*   Other conduct which could reasonably be considered inappropriate in a
    professional setting

## Our Responsibilities

Project maintainers are responsible for clarifying and enforcing our standards of
acceptable behavior and will take appropriate and fair corrective action in
response to any behavior that they deem inappropriate, threatening, offensive,
or harmful.

Project maintainers have the right and responsibility to remove, edit, or reject
comments, commits, code, wiki edits, issues, and other contributions that are
not aligned to this Code of Conduct, and will communicate reasons for moderation
decisions when appropriate.

## Scope

This Code of Conduct applies within all community spaces, and also applies when
an individual is officially representing the community in public spaces.
Examples of representing our community include using an official e-mail address,
posting via an official social media account, or acting as an appointed
representative at an online or offline event.

## Enforcement

Instances of abusive, harassing, or otherwise unacceptable behavior may be
reported to the project team responsible for enforcement at
**sgpos.maintainers@example.com**.
All complaints will be reviewed and investigated promptly and fairly.

All community leaders are obligated to respect the privacy and security of the
reporter of any incident.

## Enforcement Guidelines

Community leaders will follow these Community Impact Guidelines in determining
the consequences for any action they deem in violation of this Code of Conduct:

### 1. Correction

**Community Impact**: Use of inappropriate language or other behavior deemed
unprofessional or unwelcome in the community.

**Consequence**: A private, written warning from community leaders, providing
clarity around the nature of the violation and an explanation of why the
behavior was inappropriate. A public apology may be requested.

### 2. Warning

**Community Impact**: A violation through a single incident or series
of actions.

**Consequence**: A warning with consequences for continued behavior. No
interaction with the people involved, including unsolicited interaction with
those enforcing the Code of Conduct, for a specified period of time. This
includes avoiding interaction in community spaces as well as external channels
like social media. Violating these terms may lead to a temporary or
permanent ban.

### 3. Temporary Ban

**Community Impact**: A serious violation of community standards, including
sustained inappropriate behavior.

**Consequence**: A temporary ban from any sort of interaction or public
communication with the community for a specified period of time. No public or
private interaction with the people involved, including unsolicited interaction
with those enforcing the Code of Conduct, is allowed during this period.
Violating these terms may lead to a permanent ban.

### 4. Permanent Ban

**Community Impact**: Demonstrating a pattern of violation of community
standards, including sustained inappropriate behavior, harassment of an
individual, or aggression toward or disparagement of classes of individuals.

**Consequence**: A permanent ban from any sort of public interaction within
the community.

## Attribution

This Code of Conduct is adapted from the [Contributor Covenant][homepage],
version 2.1, available at
[https://www.contributor-covenant.org/version/2/1/code_of_conduct.html][v2.1].

[homepage]: https://www.contributor-covenant.org
[v2.1]: https://www.contributor-covenant.org/version/2/1/code_of_conduct.html


```

# CONTRIBUTING.md
```md
# Contributing to the SG-POS System

First off, thank you for considering contributing to the SG-POS System! It's people like you that make open source such a powerful and rewarding ecosystem. Your contributions will directly help small business owners in Singapore run their businesses more effectively.

This document provides guidelines for contributing to the project. We want to make it as easy and transparent as possible for you to get involved.

## Code of Conduct

By participating in this project, you are expected to uphold our [Code of Conduct](CODE_OF_CONDUCT.md). Please read it before you start. We are committed to fostering an open, welcoming, and harassment-free environment.

## How Can I Contribute?

There are many ways to contribute, and all of them are valuable.

*   **Reporting Bugs:** If you find a bug, please open an issue on our GitHub repository. Provide a clear title, a detailed description of the bug, steps to reproduce it, and any relevant logs or screenshots.
*   **Suggesting Enhancements:** If you have an idea for a new feature or an improvement to an existing one, open an issue to start a discussion. This allows us to align on the goals before any code is written.
*   **Improving Documentation:** Good documentation is crucial. If you find gaps in our `README.md`, docstrings, or other project documents, feel free to submit a pull request with your improvements.
*   **Writing Code:** If you're ready to write some code, look for issues tagged with `help wanted` or `good first issue`.

## Your First Code Contribution: The Pull Request Process

We follow a standard fork-and-pull workflow for code contributions.

1.  **Fork the repository** on GitHub to create your own copy of the project.

2.  **Set up your development environment** by following the detailed [Developer Setup & Deployment Guide](README.md#6-developer-setup--deployment-guide) in our main `README.md`.

3.  **Create a new branch** from the `main` branch in your fork. Please use a descriptive branch name.
    *   For new features: `feature/my-awesome-feature`
    *   For bug fixes: `fix/correct-calculation-bug`
    *   For documentation: `docs/update-readme`
    ```bash
    git checkout -b feature/your-branch-name
    ```

4.  **Make your changes.** Write your code, and don't forget to add or update tests to cover your changes!

5.  **Ensure all quality checks pass.** Before you submit your pull request, run all the local checks to ensure your code adheres to our quality standards.
    ```bash
    # Ensure all tests pass
    pytest

    # Format your code with Black
    black .

    # Lint your code with Ruff
    ruff . --fix

    # Check static types with MyPy
    mypy app
    ```
    The pre-commit hooks, if configured, will help automate this process.

6.  **Commit your changes** with a clear and descriptive commit message. We recommend following the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) specification.
    *   Example: `feat(sales): Add support for gift card payments`
    *   Example: `fix(inventory): Prevent negative stock adjustments`
    ```bash
    git commit -m "feat(ui): Add new customer search functionality"
    ```

7.  **Push your branch** to your fork on GitHub.
    ```bash
    git push origin feature/your-branch-name
    ```

8.  **Open a Pull Request (PR)** from your fork's branch to the `main` branch of the official SG-POS repository.
    *   Provide a clear title for your PR.
    *   In the description, explain the "what" and "why" of your changes.
    *   If your PR addresses an existing issue, link it using `Closes #123`.

9.  **Engage in the Code Review.** A maintainer will review your PR. Be prepared to discuss your changes and make adjustments based on the feedback. We aim to be responsive and provide constructive reviews.

Thank you again for your contribution!


```

