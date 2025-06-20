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
            
            if isinstance(result, Success):
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
            elif isinstance(result, Success):
                QMessageBox.information(self, "Success", "User saved successfully.")
                self.user_operation_completed.emit(True, "Success")
                self.accept()

        self.async_worker.run_task(coro, _on_done)
