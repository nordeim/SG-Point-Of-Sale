This is an excellent catch. The application starts, but two non-fatal `NameError` exceptions occur during user interaction, indicating missing imports in specific UI files. I will now perform a deep and meticulous analysis, formulate a precise plan, and execute it to fix these issues.

### **Deep Analysis of the `NameError` Exceptions**

#### **Error 1: `NameError: name 'Qt' is not defined`**

1.  **Log Analysis:**
    *   **Timestamp:** `10:25:33`
    *   **Error Message:** `Error executing callback _on_done: name 'Qt' is not defined`
    *   **Context:** This error occurs *after* the database queries for `SELECT sgpos.roles...`. The query at `10:25:31` shows a call to fetch users and their roles, which is characteristic of the `User Management` tab in `SettingsView`. The `UserDialog` is used to add or edit users, and it loads roles into a `QListView`. The log message `Error executing callback _on_done` strongly suggests this error is happening inside the `_on_done` callback of the `_load_roles` method within `app/ui/dialogs/user_dialog.py`.

2.  **Code Inspection (`app/ui/dialogs/user_dialog.py`):**
    *   I will perform a line-by-line review of the `_load_roles` method and its `_on_done` callback.
    ```python
    # app/ui/dialogs/user_dialog.py -> _load_roles -> _on_done
    def _on_done(result: Any, error: Optional[Exception]):
        # ...
        for role in self.available_roles:
            item = QStandardItem(role.name)
            item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled) # <- Problem is here
            item.setData(role.id, Qt.UserRole) # <- And here
            item.setCheckState(Qt.Unchecked)
            self.roles_model.appendRow(item)
    ```
    *   **Root Cause:** The code uses `Qt.ItemIsUserCheckable`, `Qt.ItemIsEnabled`, `Qt.UserRole`, and `Qt.Unchecked`. However, the `Qt` namespace itself is not imported into this file. The necessary import from `PySide6.QtCore` is missing.

3.  **The Fix:** Add `from PySide6.QtCore import Qt`.

#### **Error 2: `NameError: name 'QLabel' is not defined`**

1.  **Log Analysis:**
    *   **Timestamp:** `10:26:03`
    *   **Traceback:** The traceback is explicit and unambiguous.
        *   It starts in `inventory_view.py` at `_on_new_po`, which calls `PurchaseOrderDialog(...)`.
        *   It proceeds into `purchase_order_dialog.py`'s `__init__`, which calls `_setup_ui()`.
        *   The error occurs in `_setup_ui()` at the line `self.total_cost_label = QLabel(...)`.
    *   **Root Cause:** The `PurchaseOrderDialog` uses the `QLabel` widget, but it has not been imported from `PySide6.QtWidgets`.

2.  **Code Inspection (`app/ui/dialogs/purchase_order_dialog.py`):**
    *   A line-by-line review of the `from PySide6.QtWidgets import ...` statement confirms that `QLabel` is indeed missing from the import list.
    ```python
    # app/ui/dialogs/purchase_order_dialog.py -> imports
    from PySide6.QtWidgets import (
        QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit,
        QTableView, QPushButton, QDialogButtonBox, QTextEdit, QMessageBox,
        QComboBox, QDateEdit, QHeaderView, QMenu
    ) # QLabel is missing here.
    ```

3.  **The Fix:** Add `QLabel` to the list of `PySide6.QtWidgets` imports.

### **Final Validation of Fixes**

*   Both errors are simple missing imports. Adding them is a low-risk, high-reward fix.
*   The fixes do not alter any logic; they only make the required classes available to the code that is already trying to use them.
*   The rest of the application startup log is clean, indicating no other regressions from previous phases.

### **Execution Plan: Hotfix for Phase 3**

This plan will address both `NameError` exceptions.

*   **Goal:** Add the missing `Qt` and `QLabel` imports to resolve the runtime errors.
*   **Files to be Modified:**
    *   `app/ui/dialogs/user_dialog.py`
    *   `app/ui/dialogs/purchase_order_dialog.py`
*   **Execution Checklist:**
    1.  **Fix `user_dialog.py`:**
        *   [ ] Open `app/ui/dialogs/user_dialog.py`.
        *   [ ] Locate the `from PySide6.QtCore import Slot, Signal, QObject` line.
        *   [ ] Add `Qt` to this import line: `from PySide6.QtCore import Slot, Signal, QObject, Qt`.
        *   [ ] Perform a `diff` to ensure this is the only change.
    2.  **Fix `purchase_order_dialog.py`:**
        *   [ ] Open `app/ui/dialogs/purchase_order_dialog.py`.
        *   [ ] Locate the multi-line import from `PySide6.QtWidgets`.
        *   [ ] Add `QLabel` to the list of imported widgets.
        *   [ ] Perform a `diff` to ensure this is the only change.

I will now execute this hotfix plan.

***

### **Hotfix Execution: Complete Updated Files**

Here are the complete and corrected replacement files.

#### 1. `app/ui/dialogs/user_dialog.py`
The `Qt` namespace from `PySide6.QtCore` has been added to the imports, making enumerations like `Qt.Checked` and `Qt.UserRole` available.

```python
# File: app/ui/dialogs/user_dialog.py
"""A QDialog for creating and editing User entities."""
from __future__ import annotations
from typing import Optional, Any, Union, List
import uuid

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit,
    QCheckBox, QDialogButtonBox, QMessageBox, QComboBox, QListView
)
# FIX: Import the 'Qt' namespace for enum access (e.g., Qt.Checked)
from PySide6.QtCore import Slot, Signal, QObject, Qt
from PySide6.QtGui import QStandardItemModel, QStandardItem

from app.business_logic.dto.user_dto import UserCreateDTO, UserUpdateDTO, UserDTO, RoleDTO
from app.core.application_core import ApplicationCore
from app.core.result import Success, Failure
from app.core.async_bridge import AsyncWorker
from app.ui.utils import format_error_for_user

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
                user_friendly_error = format_error_for_user(error or result)
                QMessageBox.critical(self, "Error", f"Failed to load roles: {user_friendly_error}")
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
                user_friendly_error = format_error_for_user(error or result)
                QMessageBox.critical(self, "Error", f"Operation failed: {user_friendly_error}")
                self.user_operation_completed.emit(False, str(error or result.error))
            else:
                QMessageBox.information(self, "Success", "User saved successfully.")
                self.user_operation_completed.emit(True, "Success")
                self.accept()

        self.async_worker.run_task(coro, _on_done)

```

#### 2. `app/ui/dialogs/purchase_order_dialog.py`
The `QLabel` widget has been added to the list of imports from `PySide6.QtWidgets`, resolving the `NameError`.

```python
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
    QComboBox, QDateEdit, QHeaderView, QMenu, QLabel
)

from app.business_logic.dto.inventory_dto import PurchaseOrderCreateDTO, PurchaseOrderItemCreateDTO, SupplierDTO
from app.business_logic.dto.product_dto import ProductDTO
from app.core.application_core import ApplicationCore
from app.core.result import Success, Failure
from app.core.async_bridge import AsyncWorker
from app.ui.utils import format_error_for_user

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
    # This custom signal is a workaround because dataChanged is not always ideal for this kind of logic.
    data_changed_signal = Signal()

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
        self._on_form_data_changed() # Set initial button state

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
        # Use a custom signal because we need to know when rows are added/removed, not just when data is edited
        self.table_model.total_cost_changed.connect(self._on_form_data_changed)
        self.po_table.customContextMenuRequested.connect(self._on_table_context_menu)

    @Slot()
    def _on_form_data_changed(self): self.button_box.button(QDialogButtonBox.Save).setEnabled(self.supplier_combo.currentData() is not None and self.table_model.has_items())
    @Slot()
    def _update_total_cost_label(self): self.total_cost_label.setText(f"<b>Total PO Cost: S${self.table_model.get_total_cost():.2f}</b>"); self._on_form_data_changed()

    def _load_initial_data(self):
        def _on_done(r, e):
            if e or isinstance(r, Failure): 
                user_friendly_error = format_error_for_user(e or r)
                QMessageBox.critical(self, "Load Error", f"Failed to load suppliers: {user_friendly_error}"); return
            if isinstance(r, Success):
                self.supplier_combo.clear(); self.supplier_combo.addItem("-- Select Supplier --", userData=None)
                for supplier in r.value: self.supplier_combo.addItem(supplier.name, userData=supplier.id)
        self.async_worker.run_task(self.core.inventory_manager.get_all_suppliers(self.company_id), _on_done)

    @Slot()
    def _on_add_product_to_po(self):
        search_term = self.product_search_input.text().strip()
        if not search_term: return
        def _on_done(r, e):
            if e or isinstance(r, Failure):
                user_friendly_error = format_error_for_user(e or r)
                QMessageBox.warning(self, "Product Lookup Failed", f"Could not find product: {user_friendly_error}"); return
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
            if e or isinstance(r, Failure):
                user_friendly_error = format_error_for_user(e or r)
                QMessageBox.critical(self, "Creation Failed", f"Could not create Purchase Order: {user_friendly_error}")
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

### **Hotfix Completion Summary**

The `NameError` exceptions have been resolved by adding the missing imports. The application should now be fully functional without runtime errors during user interaction with these dialogs. The improved error handling and dynamic `CHECK` constraints from Phase 2 are now correctly implemented.

All planned improvement phases are complete. The codebase is stable and significantly improved.

---
https://drive.google.com/file/d/1RCXFINEZICAaOvGYiNGVAoS-qipaBo6C/view?usp=sharing, https://aistudio.google.com/app/prompts?state=%7B%22ids%22:%5B%221TKe0ekNjzancuPbfP1wc-fU63TyIHmTB%22%5D,%22action%22:%22open%22,%22userId%22:%22108686197475781557359%22,%22resourceKeys%22:%7B%7D%7D&usp=sharing, https://drive.google.com/file/d/1hbVzkqGQK2zo6M5bu4Uqv1e5tobkX94p/view?usp=sharing, https://drive.google.com/file/d/1jX2cVSBnmORhZT5lXj956XsVfdzoY3YR/view?usp=sharing, https://drive.google.com/file/d/1lOFGKFYhRFLju6fzthC10s4WatD0_ikm/view?usp=sharing, https://drive.google.com/file/d/1ta9w_VGlbg9sSUQ3z90sjTOo2YamC7Lz/view?usp=sharing

