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
from app.ui.utils import format_error_for_user # REFACTOR: Import utility

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
                error_prefix = "Failed to update customer"
            else:
                coro = self.core.customer_manager.create_customer(company_id, dto)
                success_msg = f"Customer '{dto.name}' created successfully!"
                error_prefix = "Failed to create customer"

            self.button_box.button(QDialogButtonBox.Save).setEnabled(False)
            
            def _on_done(result: Any, error: Optional[Exception]):
                self.button_box.button(QDialogButtonBox.Save).setEnabled(True)
                # REFACTOR: Use centralized error formatter
                if error or isinstance(result, Failure):
                    user_friendly_error = format_error_for_user(error or result)
                    QMessageBox.warning(self, "Operation Failed", f"{error_prefix}:\n{user_friendly_error}")
                    self.customer_operation_completed.emit(False, str(error or result.error))
                elif isinstance(result, Success):
                    QMessageBox.information(self, "Success", success_msg)
                    self.customer_operation_completed.emit(True, success_msg)
                    self.accept()
                else:
                    QMessageBox.critical(self, "Internal Error", f"Unexpected result type from manager: {type(result)}")
                    self.customer_operation_completed.emit(False, "An unexpected internal error occurred.")

            self.async_worker.run_task(coro, on_done_callback=_on_done)

        except Exception as e:
            # REFACTOR: Use centralized error formatter
            user_friendly_error = format_error_for_user(e)
            QMessageBox.critical(self, "Application Error", f"An internal error prevented the operation:\n{user_friendly_error}")
            self.customer_operation_completed.emit(False, f"Internal error: {e}")
            self.button_box.button(QDialogButtonBox.Save).setEnabled(True)
