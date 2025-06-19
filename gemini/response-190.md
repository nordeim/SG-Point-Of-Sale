Excellent. The physical file deletion is confirmed. I will now execute the remaining tasks for Phase 1: refactoring the `PaymentDialog` and removing hardcoded values.

I have meticulously followed the execution plan, applying the changes to `app/ui/dialogs/payment_dialog.py` and `app/ui/views/pos_view.py`.

Below are the complete and updated replacement files for your review.

***

### **Phase 1 Execution: Complete Updated Files**

#### 1. `app/ui/dialogs/payment_dialog.py`

This file has been updated to remove the redundant `PaymentEntry` class and the hardcoded table column count. It now directly uses `PaymentInfoDTO` and a class constant for the table headers, making the code cleaner and more maintainable.

```python
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

class PaymentDialog(QDialog):
    """A dialog for collecting payment for a sales transaction, supporting split tender."""

    # Class constant for table headers to avoid magic numbers
    PAYMENTS_TABLE_HEADERS = ["Method", "Amount", "Action"]

    def __init__(self, core: ApplicationCore, total_due: Decimal, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.core = core
        self.total_due = total_due.quantize(Decimal("0.01"))
        self.current_payments: List[PaymentInfoDTO] = [] # REFACTOR: Use DTO directly
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

        # REFACTOR: Use class constant for column count and headers
        self.payments_table = QTableWidget(0, len(self.PAYMENTS_TABLE_HEADERS))
        self.payments_table.setHorizontalHeaderLabels(self.PAYMENTS_TABLE_HEADERS)
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

        # REFACTOR: Instantiate DTO directly
        payment_info = PaymentInfoDTO(payment_method_id=selected_method_id, amount=amount)
        self.current_payments.append(payment_info)
        
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
        # REFACTOR: Simplified return
        return self.current_payments
```

---

#### 2. `app/ui/views/pos_view.py`

This file has been updated to remove the hardcoded GST rate from the UI label. The label text is now dynamically generated in the `_update_totals` method, ensuring it will always reflect the correct default rate from the application's business logic layer.

```python
# File: app/ui/views/pos_view.py
"""The primary Point-of-Sale (POS) view."""
from __future__ import annotations
import uuid
from decimal import Decimal
from typing import List, Any, Optional, Dict, Tuple

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLineEdit,
    QTableView, QPushButton, QLabel, QFormLayout, QMessageBox, QHeaderView
)
from PySide6.QtCore import Slot, Signal, QAbstractTableModel, QModelIndex, Qt, QObject

from app.core.application_core import ApplicationCore
from app.core.result import Result, Success, Failure
from app.business_logic.dto.sales_dto import SaleCreateDTO, FinalizedSaleDTO
from app.business_logic.dto.product_dto import ProductDTO, ProductBaseDTO
from app.business_logic.dto.customer_dto import CustomerDTO
from app.ui.dialogs.payment_dialog import PaymentDialog
from app.core.async_bridge import AsyncWorker

class CartItemDisplay(QObject):
    """Helper class to hold and represent cart item data for the TableModel."""
    def __init__(self, product: ProductDTO, quantity: Decimal, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.product = product
        self.quantity = quantity
        self.recalculate()

    def recalculate(self):
        self.line_subtotal = (self.quantity * self.product.selling_price).quantize(Decimal("0.01"))
        self.line_tax = (self.line_subtotal * (self.product.gst_rate / Decimal("100.0"))).quantize(Decimal("0.01"))
        self.line_total = (self.line_subtotal + self.line_tax).quantize(Decimal("0.01"))

    def to_cart_item_dto(self) -> Dict[str, Any]:
        return {
            "product_id": self.product.id,
            "quantity": self.quantity,
            "unit_price_override": self.product.selling_price,
            "variant_id": None, # TODO: Handle variants
            "sku": self.product.sku,
            "product": self.product
        }

class CartTableModel(QAbstractTableModel):
    """A Qt Table Model for displaying items in the sales cart."""
    HEADERS = ["SKU", "Name", "Qty", "Unit Price", "Line Total"]
    COLUMN_QTY = 2
    cart_changed = Signal()

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._items: List[CartItemDisplay] = []

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int: return len(self._items)
    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int: return len(self.HEADERS)
    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole) -> Any:
        if role == Qt.DisplayRole and orientation == Qt.Orientation.Horizontal: return self.HEADERS[section]
        return None
    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        if not index.isValid(): return None
        item = self._items[index.row()]
        col = index.column()
        if role == Qt.DisplayRole:
            if col == 0: return item.product.sku
            if col == 1: return item.product.name
            if col == 2: return str(item.quantity)
            if col == 3: return f"S${item.product.selling_price:.2f}"
            if col == 4: return f"S${item.line_total:.2f}"
        if role == Qt.EditRole and col == self.COLUMN_QTY: return str(item.quantity)
        if role == Qt.TextAlignmentRole and col in [2, 3, 4]: return Qt.AlignRight | Qt.AlignVCenter
        return None
    def setData(self, index: QModelIndex, value: Any, role: int = Qt.EditRole) -> bool:
        if role == Qt.EditRole and index.column() == self.COLUMN_QTY:
            try:
                new_qty = Decimal(value)
                if new_qty <= 0:
                    self.remove_item_at_row(index.row())
                    return True
                self._items[index.row()].quantity = new_qty
                self._items[index.row()].recalculate()
                self.dataChanged.emit(index, self.createIndex(index.row(), self.columnCount() - 1))
                self.cart_changed.emit()
                return True
            except: return False
        return False
    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        flags = super().flags(index)
        if index.column() == self.COLUMN_QTY: flags |= Qt.ItemFlag.ItemIsEditable
        return flags
    def add_item(self, product_dto: ProductDTO, quantity: Decimal = Decimal("1")):
        for item_display in self._items:
            if item_display.product.id == product_dto.id:
                item_display.quantity += quantity
                item_display.recalculate()
                idx = self._items.index(item_display)
                self.dataChanged.emit(self.createIndex(idx, 0), self.createIndex(idx, self.columnCount() - 1))
                self.cart_changed.emit()
                return
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        self._items.append(CartItemDisplay(product_dto, quantity))
        self.endInsertRows()
        self.cart_changed.emit()
    def clear_cart(self):
        self.beginResetModel(); self._items.clear(); self.endResetModel(); self.cart_changed.emit()
    def get_cart_summary(self) -> Tuple[Decimal, Decimal, Decimal]:
        subtotal = sum((item.line_subtotal for item in self._items), Decimal('0.0')).quantize(Decimal("0.01"))
        tax_amount = sum((item.line_tax for item in self._items), Decimal('0.0')).quantize(Decimal("0.01"))
        total_amount = sum((item.line_total for item in self._items), Decimal('0.0')).quantize(Decimal("0.01"))
        return subtotal, tax_amount, total_amount
    def get_cart_items(self) -> List[Dict[str, Any]]: return [item.to_cart_item_dto() for item in self._items]

class POSView(QWidget):
    def __init__(self, core: ApplicationCore, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.core = core
        self.async_worker: AsyncWorker = core.async_worker
        self.selected_customer_id: Optional[uuid.UUID] = None
        self._setup_ui()
        self._connect_signals()
        self._reset_sale_clicked()

    def _setup_ui(self):
        left_panel = QWidget(); left_layout = QVBoxLayout(left_panel)
        self.cart_table = QTableView(); self.cart_model = CartTableModel()
        self.cart_table.setModel(self.cart_model); self.cart_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.cart_table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows); self.cart_table.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self.cart_table.setEditTriggers(QTableView.EditTrigger.DoubleClicked | QTableView.EditTrigger.AnyKeyPressed)
        self.subtotal_label = QLabel("Subtotal: S$0.00")
        
        # REFACTOR: Remove hardcoded GST rate from label text
        self.tax_label = QLabel() 
        
        self.total_label = QLabel("Total: S$0.00"); self.total_label.setStyleSheet("font-size: 28px; font-weight: bold; color: #333;")
        totals_form_layout = QFormLayout(); totals_form_layout.addRow(self.subtotal_label); totals_form_layout.addRow(self.tax_label); totals_form_layout.addRow(self.total_label)
        left_layout.addWidget(QLabel("Current Sale Items")); left_layout.addWidget(self.cart_table, 1); left_layout.addLayout(totals_form_layout)
        right_panel = QWidget(); right_layout = QVBoxLayout(right_panel)
        product_search_form = QFormLayout(); self.product_search_input = QLineEdit(); self.product_search_input.setPlaceholderText("Scan barcode or enter SKU/name...")
        self.add_item_button = QPushButton("Add to Cart"); product_search_form.addRow("Product:", self.product_search_input); right_layout.addLayout(product_search_form); right_layout.addWidget(self.add_item_button)
        customer_form = QFormLayout(); self.customer_search_input = QLineEdit(); self.customer_search_input.setPlaceholderText("Search customer by code/name...")
        self.select_customer_button = QPushButton("Select Customer"); self.clear_customer_button = QPushButton("Clear")
        self.selected_customer_label = QLabel("Customer: N/A"); customer_actions_layout = QHBoxLayout(); customer_actions_layout.addWidget(self.select_customer_button); customer_actions_layout.addWidget(self.clear_customer_button)
        customer_form.addRow(self.selected_customer_label); customer_form.addRow(self.customer_search_input); customer_form.addRow(customer_actions_layout); right_layout.addLayout(customer_form)
        right_layout.addStretch()
        self.new_sale_button = QPushButton("New Sale"); self.void_sale_button = QPushButton("Void Sale"); self.pay_button = QPushButton("PAY")
        self.pay_button.setStyleSheet("background-color: #4CAF50; color: white; font-size: 28px; padding: 20px;")
        right_layout.addWidget(self.new_sale_button); right_layout.addWidget(self.void_sale_button); right_layout.addWidget(self.pay_button)
        main_layout = QHBoxLayout(self); main_layout.addWidget(left_panel, 2); main_layout.addWidget(right_panel, 1)

        # REFACTOR: Set initial label text dynamically
        self._update_totals()

    def _connect_signals(self):
        self.add_item_button.clicked.connect(self._on_add_item_clicked); self.product_search_input.returnPressed.connect(self._on_add_item_clicked)
        self.pay_button.clicked.connect(self._on_pay_clicked); self.new_sale_button.clicked.connect(self._reset_sale_clicked)
        self.void_sale_button.clicked.connect(self._void_sale_clicked); self.cart_model.cart_changed.connect(self._update_totals)
        self.select_customer_button.clicked.connect(self._on_select_customer_clicked); self.clear_customer_button.clicked.connect(self._clear_customer_selection)

    @Slot()
    def _update_totals(self):
        subtotal, tax_amount, total_amount = self.cart_model.get_cart_summary()
        
        # REFACTOR: Dynamically get default GST rate for display in the label
        default_gst_rate = ProductBaseDTO.model_fields['gst_rate'].default

        self.subtotal_label.setText(f"Subtotal: S${subtotal:.2f}")
        self.tax_label.setText(f"GST ({default_gst_rate:.2f}%): S${tax_amount:.2f}")
        self.total_label.setText(f"Total: S${total_amount:.2f}")

    @Slot()
    def _on_add_item_clicked(self):
        search_term = self.product_search_input.text().strip();
        if not search_term: return
        def _on_done(result: Any, error: Optional[Exception]):
            if error or isinstance(result, Failure):
                QMessageBox.warning(self, "Product Lookup Failed", f"Could not find product: {error or result.error}")
            elif isinstance(result, Success):
                products = result.value
                if not products: QMessageBox.warning(self, "Not Found", f"No product found for '{search_term}'."); return
                self.cart_model.add_item(products[0]); self.product_search_input.clear(); self.product_search_input.setFocus()
        coro = self.core.product_manager.search_products(self.core.current_company_id, search_term, limit=1)
        self.async_worker.run_task(coro, on_done_callback=_on_done)

    @Slot()
    def _on_pay_clicked(self):
        if not self.cart_model.rowCount(): QMessageBox.warning(self, "Empty Cart", "Cannot process payment for an empty cart."); return
        _, _, total_amount = self.cart_model.get_cart_summary()
        payment_dialog = PaymentDialog(self.core, total_amount, parent=self)
        if payment_dialog.exec():
            payment_info_dtos = payment_dialog.get_payment_info()
            if not payment_info_dtos: QMessageBox.critical(self, "Payment Error", "No payment information received."); return
            sale_create_dto = SaleCreateDTO(
                company_id=self.core.current_company_id, outlet_id=self.core.current_outlet_id,
                cashier_id=self.core.current_user_id, customer_id=self.selected_customer_id,
                cart_items=self.cart_model.get_cart_items(), payments=payment_info_dtos
            )
            def _on_done(result: Any, error: Optional[Exception]):
                self.pay_button.setEnabled(True)
                if error or isinstance(result, Failure):
                    QMessageBox.warning(self, "Sale Failed", f"Could not finalize sale: {error or result.error}")
                elif isinstance(result, Success):
                    finalized_dto: FinalizedSaleDTO = result.value
                    QMessageBox.information(self, "Sale Completed", f"Transaction {finalized_dto.transaction_number} completed!\nTotal: S${finalized_dto.total_amount:.2f}\nChange Due: S${finalized_dto.change_due:.2f}")
                    self._reset_sale_clicked()
            self.pay_button.setEnabled(False)
            self.async_worker.run_task(self.core.sales_manager.finalize_sale(sale_create_dto), on_done_callback=_on_done)
        else:
            QMessageBox.information(self, "Payment Cancelled", "Payment process cancelled.")

    @Slot()
    def _reset_sale_clicked(self):
        self.cart_model.clear_cart(); self.product_search_input.clear(); self._clear_customer_selection(); self.product_search_input.setFocus()

    @Slot()
    def _void_sale_clicked(self):
        if self.cart_model.rowCount() == 0: QMessageBox.information(self, "No Sale", "There is no active sale to void."); return
        if QMessageBox.question(self, "Confirm Void", "Are you sure you want to void the current sale?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            self._reset_sale_clicked(); QMessageBox.information(self, "Sale Voided", "Current sale has been voided.")

    @Slot()
    def _on_select_customer_clicked(self):
        search_term = self.customer_search_input.text().strip()
        if not search_term: return
        def _on_done(result: Any, error: Optional[Exception]):
            if error or isinstance(result, Failure): QMessageBox.warning(self, "Customer Lookup Failed", f"Could not find customer: {error or result.error}"); return
            if isinstance(result, Success) and result.value:
                customer = result.value[0]
                self.selected_customer_id = customer.id; self.selected_customer_label.setText(f"Customer: {customer.name}"); self.customer_search_input.clear()
            else: QMessageBox.warning(self, "Not Found", f"No customer found for '{search_term}'.")
        self.async_worker.run_task(self.core.customer_manager.search_customers(self.core.current_company_id, search_term, limit=1), on_done_callback=_on_done)

    @Slot()
    def _clear_customer_selection(self):
        self.selected_customer_id = None; self.selected_customer_label.setText("Customer: N/A"); self.customer_search_input.clear()
```

***

### **Phase 1 Completion Summary**

*   **Task 1 (CLEANUP-001):** Obsolete file `app/ui/widgets/searchable_table_view.py` has been removed.
*   **Task 2 (REFACTOR-001):** `app/ui/dialogs/payment_dialog.py` has been successfully refactored to use the central `PaymentInfoDTO`, eliminating the redundant `PaymentEntry` class.
*   **Task 3 (REFACTOR-002):** Hardcoded values have been removed. The `PaymentDialog` now derives its table structure from a class constant, and the `POSView` dynamically generates its GST label text from the `ProductBaseDTO` definition.

Phase 1 is complete. The codebase is now cleaner and more maintainable. Please confirm these changes, and I will proceed with the detailed plan for Phase 2.

---
https://drive.google.com/file/d/1RCXFINEZICAaOvGYiNGVAoS-qipaBo6C/view?usp=sharing, https://aistudio.google.com/app/prompts?state=%7B%22ids%22:%5B%221TKe0ekNjzancuPbfP1wc-fU63TyIHmTB%22%5D,%22action%22:%22open%22,%22userId%22:%22108686197475781557359%22,%22resourceKeys%22:%7B%7D%7D&usp=sharing, https://drive.google.com/file/d/1hbVzkqGQK2zo6M5bu4Uqv1e5tobkX94p/view?usp=sharing, https://drive.google.com/file/d/1jX2cVSBnmORhZT5lXj956XsVfdzoY3YR/view?usp=sharing, https://drive.google.com/file/d/1lOFGKFYhRFLju6fzthC10s4WatD0_ikm/view?usp=sharing, https://drive.google.com/file/d/1ta9w_VGlbg9sSUQ3z90sjTOo2YamC7Lz/view?usp=sharing

