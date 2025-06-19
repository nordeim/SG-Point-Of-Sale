# File: app/ui/dialogs/payment_method_dialog.py
"""A QDialog for creating and editing PaymentMethod entities."""
from __future__ import annotations
from typing import Optional, Any
import uuid

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit,
    QCheckBox, QDialogButtonBox, QMessageBox, QComboBox
)
from PySide6.QtCore import Slot, Signal, QObject

from app.core.application_core import ApplicationCore
from app.core.result import Success, Failure
from app.business_logic.dto.payment_dto import (
    PaymentMethodCreateDTO, PaymentMethodUpdateDTO, PaymentMethodDTO, PaymentMethodType
)

class PaymentMethodDialog(QDialog):
    """A dialog for creating or editing a payment method."""
    operation_completed = Signal()

    def __init__(self, core: ApplicationCore, method: Optional[PaymentMethodDTO] = None, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.core = core
        self.method = method
        self.is_edit_mode = method is not None

        self.setWindowTitle("Edit Payment Method" if self.is_edit_mode else "Add New Payment Method")
        self.setMinimumWidth(400)

        self._setup_ui()
        self._connect_signals()

        if self.is_edit_mode:
            self._populate_form()

    def _setup_ui(self):
        """Initializes the UI widgets and layout."""
        self.name_input = QLineEdit()
        self.type_combo = QComboBox()
        # Populate the combo box from the PaymentMethodType enum
        for member in PaymentMethodType:
            self.type_combo.addItem(member.name.replace('_', ' ').title(), member.value)
        
        self.is_active_checkbox = QCheckBox("Is Active")

        form_layout = QFormLayout()
        form_layout.addRow("Method Name:", self.name_input)
        form_layout.addRow("Method Type:", self.type_combo)
        form_layout.addRow(self.is_active_checkbox)
        
        self.button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        self.button_box.button(QDialogButtonBox.Save).setText("Save Method")
        
        main_layout = QVBoxLayout(self)
        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.button_box)

        if not self.is_edit_mode:
            self.is_active_checkbox.setChecked(True)

    def _connect_signals(self):
        self.button_box.accepted.connect(self._on_save)
        self.button_box.rejected.connect(self.reject)

    def _populate_form(self):
        """Populates the form fields with existing data in edit mode."""
        if self.method:
            self.name_input.setText(self.method.name)
            self.is_active_checkbox.setChecked(self.method.is_active)
            # Find the index in the combo box that matches the method's type
            index = self.type_combo.findData(self.method.type)
            if index >= 0:
                self.type_combo.setCurrentIndex(index)

    def _get_dto(self) -> PaymentMethodCreateDTO | PaymentMethodUpdateDTO:
        """Constructs a DTO from the current form data."""
        common_data = {
            "name": self.name_input.text().strip(),
            "type": self.type_combo.currentData(role=Qt.UserRole), # Get the enum value
            "is_active": self.is_active_checkbox.isChecked(),
        }
        if self.is_edit_mode:
            return PaymentMethodUpdateDTO(**common_data)
        else:
            return PaymentMethodCreateDTO(**common_data)

    @Slot()
    def _on_save(self):
        """Handles the save action, triggering the async operation."""
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Validation Error", "Method name cannot be empty.")
            return

        dto = self._get_dto()
        
        if self.is_edit_mode:
            coro = self.core.payment_method_manager.update_payment_method(self.method.id, dto)
            success_msg = f"Payment method '{dto.name}' updated successfully!"
        else:
            coro = self.core.payment_method_manager.create_payment_method(self.core.current_company_id, dto)
            success_msg = f"Payment method '{dto.name}' created successfully!"

        self.button_box.button(QDialogButtonBox.Save).setEnabled(False)
        
        def on_done(result: Any, error: Optional[Exception]):
            self.button_box.button(QDialogButtonBox.Save).setEnabled(True)
            if error or isinstance(result, Failure):
                QMessageBox.critical(self, "Operation Failed", f"Could not save payment method:\n{error or result.error}")
            elif isinstance(result, Success):
                QMessageBox.information(self, "Success", success_msg)
                self.operation_completed.emit()
                self.accept()

        self.core.async_worker.run_task(coro, on_done_callback=on_done)
