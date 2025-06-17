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
