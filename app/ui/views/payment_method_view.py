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
