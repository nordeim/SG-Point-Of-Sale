# File: app/ui/dialogs/payment_dialog.py
"""A QDialog for collecting payment for a sales transaction."""
import uuid
from decimal import Decimal
from typing import List, Optional, Any

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit,
    QDoubleSpinBox, QComboBox, QPushButton, QLabel, QDialogButtonBox, QMessageBox,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Slot, Signal, Qt, QObject

from app.core.application_core import ApplicationCore
from app.core.result import Success, Failure
from app.business_logic.dto.sales_dto import PaymentInfoDTO
from app.models.sales import PaymentMethod # For type hinting

class PaymentEntry:
    """Helper class to hold payment details entered by user."""
    def __init__(self, method_id: uuid.UUID, method_name: str, amount: Decimal):
        self.method_id = method_id
        self.method_name = method_name
        self.amount = amount

    def to_payment_info_dto(self) -> PaymentInfoDTO:
        """Converts to PaymentInfoDTO."""
        return PaymentInfoDTO(payment_method_id=self.method_id, amount=self.amount)

class PaymentDialog(QDialog):
    """A dialog for collecting payment for a sales transaction, supporting split tender."""

    def __init__(self, core: ApplicationCore, total_due: Decimal, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.core = core
        self.total_due = total_due.quantize(Decimal("0.01"))
        self.current_payments: List[PaymentEntry] = []
        self.available_payment_methods: List[PaymentMethod] = []

        self.setWindowTitle("Process Payment")
        self.setMinimumSize(500, 400)

        self._setup_ui()
        self._connect_signals()
        self._load_payment_methods() # Load methods asynchronously

    def _setup_ui(self):
        """Build the user interface."""
        summary_layout = QFormLayout()
        self.total_due_label = QLabel(f"<b>Amount Due: S${self.total_due:.2f}</b>")
        self.total_paid_label = QLabel("Amount Paid: S$0.00")
        self.balance_label = QLabel("Balance: S$0.00")
        
        self.total_due_label.setStyleSheet("font-size: 20px;")
        self.total_paid_label.setStyleSheet("font-size: 16px; color: #555;")
        self.balance_label.setStyleSheet("font-size: 18px; font-weight: bold; color: red;")

        summary_layout.addRow("Total Due:", self.total_due_label)
        summary_layout.addRow("Amount Paid:", self.total_paid_label)
        summary_layout.addRow("Balance:", self.balance_label)

        payment_entry_layout = QHBoxLayout()
        self.method_combo = QComboBox()
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setRange(0, 9999999.99)
        self.amount_input.setDecimals(2)
        self.add_payment_button = QPushButton("Add Payment")
        
        payment_entry_layout.addWidget(self.method_combo, 1)
        payment_entry_layout.addWidget(self.amount_input)
        payment_entry_layout.addWidget(self.add_payment_button)

        self.payments_table = QTableWidget(0, 3) # Rows, Cols
        self.payments_table.setHorizontalHeaderLabels(["Method", "Amount", "Action"])
        self.payments_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.payments_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.button(QDialogButtonBox.Ok).setText("Finalize Sale")
        self.button_box.button(QDialogButtonBox.Ok).setEnabled(False)

        main_layout = QVBoxLayout(self)
        main_layout.addLayout(summary_layout)
        main_layout.addStretch(1)
        main_layout.addLayout(payment_entry_layout)
        main_layout.addWidget(self.payments_table, 2)
        main_layout.addWidget(self.button_box)

        self._update_summary_labels()

    def _connect_signals(self):
        self.add_payment_button.clicked.connect(self._on_add_payment_clicked)
        self.button_box.accepted.connect(self._on_finalize_sale_clicked)
        self.button_box.rejected.connect(self.reject)

    def _load_payment_methods(self):
        def _on_done(result: Any, error: Optional[Exception]):
            if error:
                QMessageBox.critical(self, "Load Error", f"Failed to load payment methods: {error}")
                self.add_payment_button.setEnabled(False)
            elif isinstance(result, Success):
                self.available_payment_methods = result.value
                self.method_combo.clear()
                for method in self.available_payment_methods:
                    self.method_combo.addItem(method.name, userData=method.id)
                
                if self.method_combo.count() > 0:
                    self.amount_input.setValue(float(self.total_due))
                else:
                    QMessageBox.warning(self, "No Payment Methods", "No active payment methods found.")
                    self.add_payment_button.setEnabled(False)
            elif isinstance(result, Failure):
                QMessageBox.warning(self, "Load Failed", f"Could not load payment methods: {result.error}")
                self.add_payment_button.setEnabled(False)

        coro = self.core.payment_method_service.get_all_active_methods(self.core.current_company_id)
        self.core.async_worker.run_task(coro, on_done_callback=_on_done)

    @Slot()
    def _update_summary_labels(self):
        total_paid = sum(p.amount for p in self.current_payments).quantize(Decimal("0.01"))
        balance = (self.total_due - total_paid).quantize(Decimal("0.01"))

        self.total_paid_label.setText(f"Amount Paid: S${total_paid:.2f}")
        self.balance_label.setText(f"Balance: S${balance:.2f}")
        
        if balance <= 0:
            self.balance_label.setStyleSheet("font-size: 18px; font-weight: bold; color: green;")
            self.button_box.button(QDialogButtonBox.Ok).setEnabled(True)
        else:
            self.balance_label.setStyleSheet("font-size: 18px; font-weight: bold; color: red;")
            self.button_box.button(QDialogButtonBox.Ok).setEnabled(False)

    @Slot()
    def _on_add_payment_clicked(self):
        selected_method_id = self.method_combo.currentData()
        selected_method_name = self.method_combo.currentText()
        amount = Decimal(str(self.amount_input.value()))

        if not selected_method_id or amount <= 0:
            QMessageBox.warning(self, "Invalid Input", "Please select a payment method and enter a valid amount.")
            return

        payment_entry = PaymentEntry(selected_method_id, selected_method_name, amount)
        self.current_payments.append(payment_entry)
        
        row_idx = self.payments_table.rowCount()
        self.payments_table.insertRow(row_idx)
        self.payments_table.setItem(row_idx, 0, QTableWidgetItem(selected_method_name))
        self.payments_table.setItem(row_idx, 1, QTableWidgetItem(f"S${amount:.2f}"))

        remove_button = QPushButton("Remove")
        remove_button.clicked.connect(lambda _, r=row_idx: self._on_remove_payment_clicked(r))
        self.payments_table.setCellWidget(row_idx, 2, remove_button)

        self._update_summary_labels()
        remaining_balance = self.total_due - sum(p.amount for p in self.current_payments)
        self.amount_input.setValue(float(max(0, remaining_balance)))

    @Slot(int)
    def _on_remove_payment_clicked(self, row_idx: int):
        self.payments_table.removeRow(row_idx)
        del self.current_payments[row_idx]
        self._update_summary_labels()
        remaining_balance = self.total_due - sum(p.amount for p in self.current_payments)
        self.amount_input.setValue(float(max(0, remaining_balance)))

    @Slot()
    def _on_finalize_sale_clicked(self):
        if sum(p.amount for p in self.current_payments) < self.total_due:
            QMessageBox.warning(self, "Insufficient Payment", "Amount paid is less than total due.")
            return
        self.accept()

    def get_payment_info(self) -> List[PaymentInfoDTO]:
        return [p.to_payment_info_dto() for p in self.current_payments]
