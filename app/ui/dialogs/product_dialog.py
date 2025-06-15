# File: app/ui/dialogs/product_dialog.py
"""A QDialog for creating and editing Product entities."""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit,
    QDoubleSpinBox, QCheckBox, QDialogButtonBox, QMessageBox
)
from PySide6.QtCore import Slot

from app.business_logic.dto.product_dto import ProductCreateDTO, ProductUpdateDTO, ProductDTO
from app.core.application_core import ApplicationCore
from app.core.result import Success

class ProductDialog(QDialog):
    """A dialog for creating or editing a product."""

    def __init__(self, core: ApplicationCore, product: ProductDTO | None = None, parent=None):
        super().__init__(parent)
        self.core = core
        self.product = product
        self.is_edit_mode = product is not None

        self.setWindowTitle("Edit Product" if self.is_edit_mode else "Add New Product")

        # --- Create Widgets ---
        self.sku_input = QLineEdit()
        self.name_input = QLineEdit()
        self.selling_price_input = QDoubleSpinBox()
        self.selling_price_input.setRange(0, 999999.99)
        self.selling_price_input.setDecimals(2)
        self.cost_price_input = QDoubleSpinBox()
        self.cost_price_input.setRange(0, 999999.99)
        self.cost_price_input.setDecimals(2)
        self.is_active_checkbox = QCheckBox("Is Active")

        # --- Layout ---
        form_layout = QFormLayout()
        form_layout.addRow("SKU:", self.sku_input)
        form_layout.addRow("Name:", self.name_input)
        form_layout.addRow("Selling Price:", self.selling_price_input)
        form_layout.addRow("Cost Price:", self.cost_price_input)
        form_layout.addRow(self.is_active_checkbox)
        
        self.button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        
        main_layout = QVBoxLayout(self)
        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.button_box)

        # --- Connections ---
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        # --- Populate data for edit mode ---
        if self.is_edit_mode:
            self._populate_form()

    def _populate_form(self):
        self.sku_input.setText(self.product.sku)
        self.name_input.setText(self.product.name)
        self.selling_price_input.setValue(float(self.product.selling_price))
        self.cost_price_input.setValue(float(self.product.cost_price))
        self.is_active_checkbox.setChecked(self.product.is_active)

    def get_dto(self):
        """Constructs a DTO from the form data."""
        # This is a simplified example. A real implementation would have more fields.
        if self.is_edit_mode:
            return ProductUpdateDTO(
                sku=self.sku_input.text(),
                name=self.name_input.text(),
                selling_price=self.selling_price_input.value(),
                cost_price=self.cost_price_input.value(),
                is_active=self.is_active_checkbox.isChecked(),
            )
        else:
            return ProductCreateDTO(
                sku=self.sku_input.text(),
                name=self.name_input.text(),
                selling_price=self.selling_price_input.value(),
                cost_price=self.cost_price_input.value(),
            )

    @Slot()
    def accept(self):
        """Handle the save action."""
        dto = self.get_dto()
        # This is a blocking call for simplicity in this example.
        # A full implementation would use the async_bridge.
        # loop = asyncio.get_event_loop()
        if self.is_edit_mode:
            # result = loop.run_until_complete(
            #     self.core.product_manager.update_product(self.product.id, dto)
            # )
            pass # Placeholder for async call
        else:
            # result = loop.run_until_complete(
            #     self.core.product_manager.create_product(self.core.company_id, dto)
            # )
            pass # Placeholder for async call
        
        # A proper implementation would handle the result:
        # if isinstance(result, Success):
        #     super().accept()
        # else:
        #     QMessageBox.critical(self, "Error", result.error)
        
        # For now, we just accept to close the dialog.
        super().accept()
