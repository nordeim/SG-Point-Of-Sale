# File: app/ui/views/product_view.py
"""The main view for managing products."""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTableView, QMessageBox
from PySide6.QtCore import Slot

from app.core.application_core import ApplicationCore
from app.ui.dialogs.product_dialog import ProductDialog
# We would need a QAbstractTableModel for products here.
# For simplicity, we'll omit the model implementation in this stage.

class ProductView(QWidget):
    """A view widget to display and manage the product catalog."""
    
    def __init__(self, core: ApplicationCore, parent=None):
        super().__init__(parent)
        self.core = core
        
        # --- Widgets ---
        self.add_button = QPushButton("Add New Product")
        self.edit_button = QPushButton("Edit Selected")
        self.delete_button = QPushButton("Delete Selected")
        self.table_view = QTableView()
        # self.table_view.setModel(ProductTableModel(core)) # To be implemented
        
        # --- Layout ---
        layout = QVBoxLayout(self)
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        layout.addWidget(self.table_view)

        # --- Connections ---
        self.add_button.clicked.connect(self.open_add_dialog)

    @Slot()
    def open_add_dialog(self):
        """Opens the dialog to add a new product."""
        dialog = ProductDialog(self.core, parent=self)
        if dialog.exec():
            QMessageBox.information(self, "Success", "Product operation successful.")
            # Here you would refresh the table model
            # self.table_view.model().refresh()
