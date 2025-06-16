# File: app/ui/dialogs/stock_adjustment_dialog.py
"""
A QDialog for performing stock adjustments.

This dialog allows users to add products, input their physically counted quantities,
and submit the adjustment. It orchestrates the process by:
1. Fetching product and current stock level data asynchronously.
2. Collecting user input for new quantities and adjustment notes.
3. Creating a StockAdjustmentDTO.
4. Calling the InventoryManager to process the adjustment asynchronously.
5. Handling the success or failure result to provide user feedback.
"""
from __future__ import annotations
from decimal import Decimal
from typing import List, Optional, Any
import uuid

from PySide6.QtCore import (
    Qt, QAbstractTableModel, QModelIndex, Slot, Signal, QObject, QPoint
)
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit,
    QTableView, QPushButton, QDialogButtonBox, QTextEdit, QMessageBox,
    QHeaderView, QMenu
)

from app.business_logic.dto.inventory_dto import StockAdjustmentDTO, StockAdjustmentItemDTO
from app.business_logic.dto.product_dto import ProductDTO
from app.core.application_core import ApplicationCore
from app.core.result import Success, Failure
from app.core.async_bridge import AsyncWorker

class AdjustmentLineItem(QObject):
    """Helper class to hold and represent adjustment line item data for the TableModel."""
    def __init__(self, product: ProductDTO, system_qty: Decimal, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.product = product
        self.system_qty = system_qty
        self.counted_qty: Optional[Decimal] = None

    @property
    def variance(self) -> Decimal:
        if self.counted_qty is None: return Decimal("0")
        return (self.counted_qty - self.system_qty).quantize(Decimal("0.0001"))

    def to_stock_adjustment_item_dto(self) -> StockAdjustmentItemDTO:
        return StockAdjustmentItemDTO(product_id=self.product.id, variant_id=None, counted_quantity=self.counted_qty) # TODO: Handle variant_id


class StockAdjustmentTableModel(QAbstractTableModel):
    """A Qt Table Model for managing items in the stock adjustment dialog."""
    HEADERS = ["SKU", "Product Name", "System Quantity", "Counted Quantity", "Variance"]
    COLUMN_COUNTED_QTY = 3

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._items: List[AdjustmentLineItem] = []
        self.data_changed_signal = Signal()

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int: return len(self._items)
    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int: return len(self.HEADERS)
    def headerData(self, s, o, r=Qt.DisplayRole):
        if r == Qt.DisplayRole and o == Qt.Horizontal: return self.HEADERS[s]
    def data(self, i, r=Qt.DisplayRole):
        if not i.isValid(): return None
        item = self._items[i.row()]
        col = i.column()
        if r == Qt.DisplayRole:
            if col == 0: return item.product.sku
            if col == 1: return item.product.name
            if col == 2: return str(item.system_qty)
            if col == 3: return str(item.counted_qty) if item.counted_qty is not None else ""
            if col == 4: v = item.variance; return f"+{v}" if v > 0 else str(v)
        if r == Qt.EditRole and col == self.COLUMN_COUNTED_QTY: return str(item.counted_qty or "")
        if r == Qt.TextAlignmentRole and col in [2, 3, 4]: return Qt.AlignRight | Qt.AlignVCenter
    def setData(self, i, v, r=Qt.EditRole):
        if r == Qt.EditRole and i.column() == self.COLUMN_COUNTED_QTY:
            try:
                self._items[i.row()].counted_qty = Decimal(v) if str(v).strip() else None
                self.dataChanged.emit(i, self.createIndex(i.row(), self.columnCount() - 1))
                self.data_changed_signal.emit()
                return True
            except: return False
        return False
    def flags(self, i):
        flags = super().flags(i)
        if i.column() == self.COLUMN_COUNTED_QTY: flags |= Qt.ItemIsEditable
        return flags
    def add_item(self, item: AdjustmentLineItem):
        if any(i.product.id == item.product.id for i in self._items):
            QMessageBox.information(self.parent(), "Duplicate Item", f"Product '{item.product.name}' is already in the list.")
            return
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount()); self._items.append(item); self.endInsertRows()
        self.data_changed_signal.emit()
    def remove_item_at_row(self, r):
        if 0 <= r < len(self._items):
            self.beginRemoveRows(QModelIndex(), r, r); del self._items[r]; self.endRemoveRows()
            self.data_changed_signal.emit()
    def get_adjustment_items(self): return [i.to_stock_adjustment_item_dto() for i in self._items if i.counted_qty is not None]

class StockAdjustmentDialog(QDialog):
    """A dialog for creating and submitting a stock adjustment."""
    operation_completed = Signal()

    def __init__(self, core: ApplicationCore, outlet_id: uuid.UUID, user_id: uuid.UUID, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.core = core
        self.async_worker: AsyncWorker = core.async_worker
        self.company_id = self.core.current_company_id
        self.outlet_id = outlet_id
        self.user_id = user_id
        self.setWindowTitle("Perform Stock Adjustment")
        self.setMinimumSize(800, 600)
        self._setup_ui()
        self._connect_signals()
        self._on_data_changed()

    def _setup_ui(self):
        self.product_search_input = QLineEdit(); self.product_search_input.setPlaceholderText("Enter Product SKU or Name to add...")
        self.add_product_button = QPushButton("Add Product"); search_layout = QHBoxLayout()
        search_layout.addWidget(self.product_search_input, 1); search_layout.addWidget(self.add_product_button)
        self.adjustment_table = QTableView(); self.table_model = StockAdjustmentTableModel(parent=self)
        self.adjustment_table.setModel(self.table_model); self.adjustment_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.adjustment_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.notes_input = QTextEdit(); self.notes_input.setPlaceholderText("Provide a reason (e.g., 'Annual stock count', 'Wastage')...")
        self.button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel); self.button_box.button(QDialogButtonBox.Save).setText("Submit Adjustment")
        main_layout = QVBoxLayout(self); main_layout.addLayout(search_layout); main_layout.addWidget(self.adjustment_table)
        main_layout.addWidget(QLabel("Adjustment Notes/Reason:")); main_layout.addWidget(self.notes_input, 1); main_layout.addWidget(self.button_box)

    def _connect_signals(self):
        self.add_product_button.clicked.connect(self._on_add_product_clicked)
        self.product_search_input.returnPressed.connect(self._on_add_product_clicked)
        self.button_box.accepted.connect(self._on_submit_adjustment_clicked)
        self.button_box.rejected.connect(self.reject)
        self.table_model.data_changed_signal.connect(self._on_data_changed)
        self.notes_input.textChanged.connect(self._on_data_changed)
        self.adjustment_table.customContextMenuRequested.connect(self._on_table_context_menu)

    @Slot()
    def _on_data_changed(self):
        self.button_box.button(QDialogButtonBox.Save).setEnabled(bool(self.notes_input.toPlainText().strip()) and bool(self.table_model.get_adjustment_items()))

    @Slot()
    def _on_add_product_clicked(self):
        search_term = self.product_search_input.text().strip()
        if not search_term: return
        def _on_product_search_done(result: Any, error: Optional[Exception]):
            if error or isinstance(result, Failure): QMessageBox.warning(self, "Product Lookup Failed", f"Could not find product: {error or result.error}"); return
            if isinstance(result, Success):
                products: List[ProductDTO] = result.value
                if not products: QMessageBox.warning(self, "Not Found", f"No product found for '{search_term}'."); return
                p = products[0]
                def _on_stock_fetch_done(stock_res, stock_err):
                    if stock_err or isinstance(stock_res, Failure): QMessageBox.critical(self, "Error", f"Failed to get stock level: {stock_err or stock_res.error}"); return
                    if isinstance(stock_res, Success):
                        self.table_model.add_item(AdjustmentLineItem(p, stock_res.value))
                        self.product_search_input.clear(); self.product_search_input.setFocus()
                self.async_worker.run_task(self.core.inventory_service.get_stock_level(self.outlet_id, p.id, None), _on_stock_fetch_done)
        self.async_worker.run_task(self.core.product_manager.search_products(self.company_id, search_term, limit=1), _on_product_search_done)

    @Slot()
    def _on_submit_adjustment_clicked(self):
        dto = StockAdjustmentDTO(company_id=self.company_id, outlet_id=self.outlet_id, user_id=self.user_id,
                                 notes=self.notes_input.toPlainText().strip(), items=self.table_model.get_adjustment_items())
        self.button_box.button(QDialogButtonBox.Save).setEnabled(False)
        def _on_done(r, e):
            self.button_box.button(QDialogButtonBox.Save).setEnabled(True)
            if e or isinstance(r, Failure): QMessageBox.critical(self, "Submission Failed", f"Could not submit adjustment: {e or r.error}")
            elif isinstance(r, Success):
                QMessageBox.information(self, "Success", "Stock adjustment submitted successfully."); self.operation_completed.emit(); self.accept()
        self.async_worker.run_task(self.core.inventory_manager.adjust_stock(dto), _on_done)

    @Slot(QPoint)
    def _on_table_context_menu(self, pos: QPoint):
        index = self.adjustment_table.indexAt(pos)
        if not index.isValid(): return
        menu = QMenu(self)
        remove_action = menu.addAction("Remove Item")
        if menu.exec(self.adjustment_table.mapToGlobal(pos)) == remove_action:
            self.table_model.remove_item_at_row(index.row())
