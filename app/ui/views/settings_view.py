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
        
        # Load data when the view is created
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
        
    def _create_users_tab(self):
        tab = QWidget(); layout = QVBoxLayout(tab)
        buttons_layout = QHBoxLayout()
        self.add_user_button = QPushButton("Add New User")
        self.edit_user_button = QPushButton("Edit Selected User")
        self.deactivate_user_button = QPushButton("Deactivate Selected")
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
        self.deactivate_user_button.clicked.connect(self._on_deactivate_user)
        self.user_table.doubleClicked.connect(self._on_edit_user)

    @Slot()
    def _load_company_info(self):
        """Loads the current company's information into the form fields."""
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
        """Gathers data from form, creates DTO, and calls manager to save."""
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
                self._load_company_info() # Refresh data

        self.async_worker.run_task(self.core.company_manager.update_company(self.company_id, dto), on_done_callback=_on_done)

    @Slot()
    def _load_users(self):
        def _on_done(r, e):
            if e or isinstance(r, Failure): QMessageBox.critical(self, "Load Error", f"Failed to load users: {e or r.error}")
            elif isinstance(r, Success): self.user_model.refresh_data(r.value)
        self.async_worker.run_task(self.core.user_manager.get_all_users(self.company_id), on_done_callback=_on_done)

    @Slot()
    def _on_add_user(self):
        dialog = UserDialog(self.core, parent=self)
        dialog.user_operation_completed.connect(self._handle_user_operation_completed)
        dialog.exec()
    
    @Slot()
    def _on_edit_user(self):
        selected_user = self.user_model.get_user_at_row(self.user_table.currentIndex().row())
        if not selected_user:
            QMessageBox.information(self, "No Selection", "Please select a user to edit.")
            return
        dialog = UserDialog(self.core, user=selected_user, parent=self)
        dialog.user_operation_completed.connect(self._handle_user_operation_completed)
        dialog.exec()

    @Slot()
    def _on_deactivate_user(self):
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
        
        self.async_worker.run_task(self.core.user_manager.deactivate_user(selected_user.id), on_done_callback=_on_done)

    @Slot(bool, str)
    def _handle_user_operation_completed(self, success: bool, message: str):
        if success:
            self._load_users()
