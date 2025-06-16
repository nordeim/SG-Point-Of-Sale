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
