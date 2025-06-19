The startup log is clean and shows no errors. The refactoring of the views to use the `ManagedTableView` widget is proceeding smoothly and without regressions. The application is stable.

We can now proceed to the next step in the plan.

### **Phase 2 Plan: UI/UX Refinements**

We will continue rolling out the `ManagedTableView` widget to the final views.

**Previous Steps (Completed):**
*   **Sub-Task 2.1:** Create the `ManagedTableView` Custom Widget.
*   **Sub-Task 2.2:** Refactor `ProductView` to use `ManagedTableView`.
*   **Sub-Task 2.3:** Refactor `CustomerView` to use `ManagedTableView`.
*   **Sub-Task 2.4:** Refactor `InventoryView` to use `ManagedTableView`.

**Current Step (To Be Executed):**
*   **Sub-Task 2.5:** Refactor `SettingsView` (User Management tab) and `PaymentMethodView` to use `ManagedTableView`. This will complete the UI/UX enhancements for all existing views.

---

### **Phase 2, Sub-Task 2.5: Refactor Final Views**

**Objective:** To apply the `ManagedTableView` pattern to the remaining tables in the application, specifically the user list in `SettingsView` and the newly created `PaymentMethodView`, ensuring a 100% consistent user experience for all data tables.

**Execution Plan & Checklist:**

1.  **Modify `app/ui/views/settings_view.py`:**
    *   [x] Import `ManagedTableView`.
    *   [x] In the `_create_users_tab` method:
        *   [x] Replace `self.user_table = QTableView()` with `self.user_managed_table = ManagedTableView()`.
        *   [x] Apply the standard refactoring pattern: set the model on the new widget, configure the inner table, and add the managed widget to the layout.
        *   [x] Update signal connections (e.g., `doubleClicked`) and any helper methods (`_on_edit_user`) to reference `self.user_managed_table.table()`.
        *   [x] In the `_load_users` method, call `self.user_managed_table.show_loading()` at the start.
        *   [x] In the `_on_done` callback for loading users, implement the logic to call `show_table()` or `show_empty("No users found.")`.

2.  **Modify `app/ui/views/payment_method_view.py`:**
    *   [x] This view was just created, so we will be upgrading it immediately.
    *   [x] Import `ManagedTableView`.
    *   [x] In the `_setup_ui` method, replace `self.table_view = QTableView()` with `self.managed_table = ManagedTableView()`.
    *   [x] Apply the same full refactoring pattern as above.
    *   [x] Update `_connect_signals` and `_get_selected_method` to use `self.managed_table.table()`.
    *   [x] Update `_load_data` to call `self.managed_table.show_loading()` and its callback to call `show_table()` or `show_empty("No payment methods configured.")`.

This plan will complete the UX refinement phase, making the entire application more robust and user-friendly.

---

### **Generated and Updated Files**

Here are the complete updated replacement files for this final sub-task.

#### 1. Updated File: `app/ui/views/payment_method_view.py`
This refactors the recently created view to use our new best-practice component.

```python
# File: app/ui/views/payment_method_view.py
"""A view for managing PaymentMethod entities."""
from __future__ import annotations
from typing import List, Any, Optional

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableView,
    QMessageBox, QHeaderView, QSizePolicy
)
from PySide6.QtCore import Slot, Signal, QAbstractTableModel, QModelIndex, Qt, QObject

from app.core.application_core import ApplicationCore
from app.core.result import Success, Failure
from app.business_logic.dto.payment_dto import PaymentMethodDTO
from app.ui.dialogs.payment_method_dialog import PaymentMethodDialog
from app.ui.widgets.managed_table_view import ManagedTableView

class PaymentMethodTableModel(QAbstractTableModel):
    """A Qt Table Model for displaying PaymentMethodDTOs."""
    HEADERS = ["Name", "Type", "Is Active"]

    def __init__(self, methods: List[PaymentMethodDTO] = None, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._methods = methods or []

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._methods)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self.HEADERS)

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole) -> Any:
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.HEADERS[section]
        return None

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        if not index.isValid(): return None
        method = self._methods[index.row()]
        col = index.column()

        if role == Qt.DisplayRole:
            if col == 0: return method.name
            if col == 1: return method.type.value.replace('_', ' ').title()
            if col == 2: return "Yes" if method.is_active else "No"
        
        if role == Qt.TextAlignmentRole and col == 2:
            return Qt.AlignCenter | Qt.AlignVCenter
        
        return None

    def get_method_at_row(self, row: int) -> Optional[PaymentMethodDTO]:
        return self._methods[row] if 0 <= row < len(self._methods) else None

    def refresh_data(self, new_methods: List[PaymentMethodDTO]):
        self.beginResetModel()
        self._methods = new_methods
        self.endResetModel()

class PaymentMethodView(QWidget):
    """A view widget to display and manage the list of payment methods."""
    def __init__(self, core: ApplicationCore, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.core = core
        self._setup_ui()
        self._connect_signals()
        self._load_data()

    def _setup_ui(self):
        top_layout = QHBoxLayout()
        self.add_button = QPushButton("Add New Method")
        self.edit_button = QPushButton("Edit Selected")
        self.deactivate_button = QPushButton("Deactivate Selected")

        top_layout.addStretch()
        top_layout.addWidget(self.add_button)
        top_layout.addWidget(self.edit_button)
        top_layout.addWidget(self.deactivate_button)
        
        self.managed_table = ManagedTableView()
        self.table_model = PaymentMethodTableModel()
        self.managed_table.set_model(self.table_model)
        
        table = self.managed_table.table()
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        table.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        table.setSortingEnabled(True)

        main_layout = QVBoxLayout(self)
        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.managed_table)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def _connect_signals(self):
        self.add_button.clicked.connect(self._on_add)
        self.edit_button.clicked.connect(self._on_edit)
        self.deactivate_button.clicked.connect(self._on_deactivate)
        self.managed_table.table().doubleClicked.connect(self._on_edit)

    def _get_selected_method(self) -> Optional[PaymentMethodDTO]:
        selected_indexes = self.managed_table.table().selectionModel().selectedRows()
        if selected_indexes:
            row = selected_indexes[0].row()
            return self.table_model.get_method_at_row(row)
        return None

    @Slot()
    def _load_data(self):
        """Loads payment method data asynchronously into the table model."""
        self.managed_table.show_loading()

        def on_done(result: Any, error: Optional[Exception]):
            if error or isinstance(result, Failure):
                self.table_model.refresh_data([])
                self.managed_table.show_empty(f"Error: {error or result.error}")
            elif isinstance(result, Success):
                methods = result.value
                self.table_model.refresh_data(methods)
                if methods:
                    self.managed_table.show_table()
                else:
                    self.managed_table.show_empty("No payment methods have been configured.")

        coro = self.core.payment_method_manager.get_all_payment_methods(self.core.current_company_id)
        self.core.async_worker.run_task(coro, on_done_callback=on_done)

    @Slot()
    def _on_add(self):
        dialog = PaymentMethodDialog(self.core, parent=self)
        dialog.operation_completed.connect(self._load_data)
        dialog.exec()

    @Slot()
    def _on_edit(self):
        selected_method = self._get_selected_method()
        if not selected_method:
            QMessageBox.information(self, "No Selection", "Please select a payment method to edit.")
            return

        dialog = PaymentMethodDialog(self.core, method=selected_method, parent=self)
        dialog.operation_completed.connect(self._load_data)
        dialog.exec()

    @Slot()
    def _on_deactivate(self):
        selected_method = self._get_selected_method()
        if not selected_method:
            QMessageBox.information(self, "No Selection", "Please select a method to deactivate.")
            return

        if not selected_method.is_active:
            QMessageBox.information(self, "Already Inactive", f"'{selected_method.name}' is already inactive.")
            return
        
        reply = QMessageBox.question(self, "Confirm Deactivation",
                                     f"Are you sure you want to deactivate '{selected_method.name}'?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.No:
            return

        def on_done(result: Any, error: Optional[Exception]):
            if error or isinstance(result, Failure):
                QMessageBox.critical(self, "Error", f"Failed to deactivate method: {error or result.error}")
            elif isinstance(result, Success):
                QMessageBox.information(self, "Success", f"'{selected_method.name}' has been deactivated.")
                self._load_data()
        
        coro = self.core.payment_method_manager.deactivate_payment_method(selected_method.id)
        self.core.async_worker.run_task(coro, on_done_callback=on_done)

```
#### 2. Updated File: `app/ui/views/settings_view.py`
This refactors the User Management tab within the main `SettingsView`.

```python
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
from app.business_logic.dto.company_dto import CompanyDTO, CompanyUpdateDTO
from app.business_logic.dto.user_dto import UserDTO, UserCreateDTO, UserUpdateDTO, RoleDTO
from app.core.async_bridge import AsyncWorker
from app.ui.dialogs.user_dialog import UserDialog
from app.ui.views.payment_method_view import PaymentMethodView
from app.ui.widgets.managed_table_view import ManagedTableView

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
        
        # Load data for the initially visible tab
        self._load_company_info()
        self.tab_widget.currentChanged.connect(self._on_tab_changed)


    def _setup_ui(self):
        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(self._create_company_tab(), "Company Information")
        self.tab_widget.addTab(self._create_users_tab(), "User Management")
        self.tab_widget.addTab(self._create_payment_methods_tab(), "Payment Methods")
        main_layout = QVBoxLayout(self); main_layout.addWidget(self.tab_widget)

    def _create_company_tab(self) -> QWidget:
        tab = QWidget(); layout = QFormLayout(tab)
        self.company_name_input = QLineEdit()
        self.company_reg_no_input = QLineEdit()
        self.company_gst_no_input = QLineEdit()
        self.company_address_input = QLineEdit()
        self.company_phone_input = QLineEdit()
        self.company_email_input = QLineEdit()
        self.company_save_button = QPushButton("Save Company Information")
        layout.addRow("Company Name:", self.company_name_input)
        layout.addRow("Registration No.:", self.company_reg_no_input)
        layout.addRow("GST Reg. No.:", self.company_gst_no_input)
        layout.addRow("Address:", self.company_address_input)
        layout.addRow("Phone:", self.company_phone_input)
        layout.addRow("Email:", self.company_email_input)
        layout.addWidget(self.company_save_button)
        return tab
        
    def _create_users_tab(self) -> QWidget:
        tab = QWidget(); layout = QVBoxLayout(tab)
        buttons_layout = QHBoxLayout()
        self.add_user_button = QPushButton("Add New User")
        self.edit_user_button = QPushButton("Edit Selected User")
        self.deactivate_user_button = QPushButton("Deactivate Selected")
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.add_user_button)
        buttons_layout.addWidget(self.edit_user_button)
        buttons_layout.addWidget(self.deactivate_user_button)

        self.user_managed_table = ManagedTableView()
        self.user_model = UserTableModel([])
        self.user_managed_table.set_model(self.user_model)
        
        table = self.user_managed_table.table()
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setSelectionBehavior(QTableView.SelectRows)
        table.setSelectionMode(QTableView.SingleSelection)
        
        layout.addLayout(buttons_layout)
        layout.addWidget(self.user_managed_table)
        return tab

    def _create_payment_methods_tab(self) -> QWidget:
        payment_method_view = PaymentMethodView(self.core)
        return payment_method_view

    def _connect_signals(self):
        self.company_save_button.clicked.connect(self._on_save_company_info)
        self.add_user_button.clicked.connect(self._on_add_user)
        self.edit_user_button.clicked.connect(self._on_edit_user)
        self.deactivate_user_button.clicked.connect(self._on_deactivate_user)
        self.user_managed_table.table().doubleClicked.connect(self._on_edit_user)

    @Slot(int)
    def _on_tab_changed(self, index: int):
        """Load data for the newly selected tab."""
        if index == 0:
            self._load_company_info()
        elif index == 1:
            self._load_users()
        # The payment methods tab's view loads its own data upon creation.

    @Slot()
    def _load_company_info(self):
        self.company_save_button.setEnabled(False)
        def _on_done(result: Any, error: Optional[Exception]):
            self.company_save_button.setEnabled(True)
            if error or isinstance(result, Failure):
                QMessageBox.critical(self, "Load Error", f"Failed to load company info: {error or result.error}")
            elif isinstance(result, Success) and result.value:
                dto: CompanyDTO = result.value
                self.company_name_input.setText(dto.name)
                self.company_reg_no_input.setText(dto.registration_number)
                self.company_gst_no_input.setText(dto.gst_registration_number or "")
                self.company_address_input.setText(dto.address or "")
                self.company_phone_input.setText(dto.phone or "")
                self.company_email_input.setText(dto.email or "")

        self.async_worker.run_task(self.core.company_manager.get_company(self.company_id), on_done_callback=_on_done)

    @Slot()
    def _on_save_company_info(self):
        dto = CompanyUpdateDTO(
            name=self.company_name_input.text().strip(),
            registration_number=self.company_reg_no_input.text().strip(),
            gst_registration_number=self.company_gst_no_input.text().strip() or None,
            address=self.company_address_input.text().strip() or None,
            phone=self.company_phone_input.text().strip() or None,
            email=self.company_email_input.text().strip() or None,
        )

        self.company_save_button.setEnabled(False)
        def _on_done(result: Any, error: Optional[Exception]):
            self.company_save_button.setEnabled(True)
            if error or isinstance(result, Failure):
                QMessageBox.critical(self, "Save Error", f"Failed to save company info: {error or result.error}")
            elif isinstance(result, Success):
                QMessageBox.information(self, "Success", "Company information saved successfully.")
                self._load_company_info()

        self.async_worker.run_task(self.core.company_manager.update_company(self.company_id, dto), on_done_callback=_on_done)

    @Slot()
    def _load_users(self):
        self.user_managed_table.show_loading()
        def _on_done(r, e):
            if e or isinstance(r, Failure):
                self.user_model.refresh_data([])
                self.user_managed_table.show_empty(f"Error: {e or r.error}")
            elif isinstance(r, Success):
                self.user_model.refresh_data(r.value)
                if r.value:
                    self.user_managed_table.show_table()
                else:
                    self.user_managed_table.show_empty("No users found.")
        self.async_worker.run_task(self.core.user_manager.get_all_users(self.company_id), on_done_callback=_on_done)

    @Slot()
    def _on_add_user(self):
        dialog = UserDialog(self.core, parent=self)
        dialog.user_operation_completed.connect(self._handle_user_operation_completed)
        dialog.exec()
    
    @Slot()
    def _on_edit_user(self):
        selected_user = self.user_model.get_user_at_row(self.user_managed_table.table().currentIndex().row())
        if not selected_user:
            QMessageBox.information(self, "No Selection", "Please select a user to edit.")
            return
        dialog = UserDialog(self.core, user=selected_user, parent=self)
        dialog.user_operation_completed.connect(self._handle_user_operation_completed)
        dialog.exec()

    @Slot()
    def _on_deactivate_user(self):
        selected_user = self.user_model.get_user_at_row(self.user_managed_table.table().currentIndex().row())
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
        
        self.async_worker.run_task(self.core.user_manager.deactivate_user(selected_user.id), on_done_callback=_on_done)

    @Slot(bool, str)
    def _handle_user_operation_completed(self, success: bool, message: str):
        if success:
            self._load_users()
```

### **Summary of Phase 2 Completion**

Phase 2 is now complete. The `ManagedTableView` component has been created and successfully integrated into all relevant views: `ProductView`, `CustomerView`, `InventoryView` (all three tabs), `PaymentMethodView`, and `SettingsView`.

The entire application now benefits from a consistent, professional, and user-friendly experience when displaying tabular data, with clear visual indicators for loading states and empty data sets. This foundational UX work sets a high-quality standard for all future development.

---
https://drive.google.com/file/d/11EUoGcc2Ooz7rfBtNPup3kDYyQbLzGCY/view?usp=sharing, https://aistudio.google.com/app/prompts?state=%7B%22ids%22:%5B%2212VGvhlsO4bTWDpTQADljLQwnQ51SA7pp%22%5D,%22action%22:%22open%22,%22userId%22:%22103961307342447084491%22,%22resourceKeys%22:%7B%7D%7D&usp=sharing, https://drive.google.com/file/d/1HejEv1nlMxlOSzNkm4qHUdytCe9a0ISg/view?usp=sharing, https://drive.google.com/file/d/1pBPMY3TTXyX-bu7qSeEHZ3QqivmAujF9/view?usp=sharing

