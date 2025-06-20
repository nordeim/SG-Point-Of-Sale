# File: app/ui/dialogs/purchase_order_dialog.py
"""A QDialog for creating and managing Purchase Orders (POs)."""
from __future__ import annotations
from decimal import Decimal
from typing import List, Optional, Any
import uuid
from datetime import datetime

from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex, Slot, Signal, QObject, QDate, QPoint
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit,
    QTableView, QPushButton, QDialogButtonBox, QTextEdit, QMessageBox,
    QComboBox, QDateEdit, QHeaderView, QMenu, QLabel
)

from app.business_logic.dto.inventory_dto import PurchaseOrderCreateDTO, PurchaseOrderItemCreateDTO, SupplierDTO
from app.business_logic.dto.product_dto import ProductDTO
from app.core.application_core import ApplicationCore
from app.core.result import Success, Failure
from app.core.async_bridge import AsyncWorker
from app.ui.utils import format_error_for_user

class POLineItem(QObject):
    """Helper class to hold and represent PO line item data for the TableModel."""
    def __init__(self, product: ProductDTO, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.product = product
        self.quantity: Decimal = Decimal("1.0000")
        self.unit_cost: Decimal = product.cost_price

    @property
    def total_cost(self) -> Decimal:
        return (self.quantity * self.unit_cost).quantize(Decimal("0.01"))

    def to_create_dto(self) -> PurchaseOrderItemCreateDTO:
        return PurchaseOrderItemCreateDTO(
            product_id=self.product.id,
            variant_id=None, # TODO: Handle variants
            quantity_ordered=self.quantity,
            unit_cost=self.unit_cost
        )

class PurchaseOrderTableModel(QAbstractTableModel):
    """A Qt Table Model for managing items in a Purchase Order."""
    HEADERS = ["SKU", "Product Name", "Quantity", "Unit Cost (S$)", "Total Cost (S$)"]
    COLUMN_QTY, COLUMN_UNIT_COST = 2, 3
    total_cost_changed = Signal()

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._items: List[POLineItem] = []

    def rowCount(self, p=QModelIndex()): return len(self._items)
    def columnCount(self, p=QModelIndex()): return len(self.HEADERS)
    def headerData(self, s, o, r=Qt.DisplayRole):
        if r == Qt.DisplayRole and o == Qt.Horizontal: return self.HEADERS[s]
    def data(self, i, r=Qt.DisplayRole):
        if not i.isValid(): return
        item, col = self._items[i.row()], i.column()
        if r == Qt.DisplayRole:
            if col == 0: return item.product.sku
            if col == 1: return item.product.name
            if col == 2: return f"{item.quantity:.4f}"
            if col == 3: return f"{item.unit_cost:.4f}"
            if col == 4: return f"{item.total_cost:.2f}"
        if r == Qt.EditRole:
            if col == self.COLUMN_QTY: return str(item.quantity)
            if col == self.COLUMN_UNIT_COST: return str(item.unit_cost)
        if r == Qt.TextAlignmentRole and col in [2, 3, 4]: return Qt.AlignRight | Qt.AlignVCenter
    def setData(self, i, v, r=Qt.EditRole):
        if r != Qt.EditRole: return False
        item, col = self._items[i.row()], i.column()
        try:
            if col == self.COLUMN_QTY:
                new_qty = Decimal(v)
                if new_qty <= 0: QMessageBox.warning(self.parent(), "Invalid Quantity", "Quantity must be greater than zero."); return False
                item.quantity = new_qty
            elif col == self.COLUMN_UNIT_COST:
                new_cost = Decimal(v)
                if new_cost < 0: QMessageBox.warning(self.parent(), "Invalid Cost", "Unit cost cannot be negative."); return False
                item.unit_cost = new_cost
            else: return False
            self.dataChanged.emit(self.createIndex(i.row(), 0), self.createIndex(i.row(), self.columnCount() - 1))
            self.total_cost_changed.emit()
            return True
        except: QMessageBox.warning(self.parent(), "Invalid Input", "Please enter a valid number."); return False
    def flags(self, i):
        flags = super().flags(i)
        if i.column() in [self.COLUMN_QTY, self.COLUMN_UNIT_COST]: flags |= Qt.ItemIsEditable
        return flags
    def add_item(self, item: POLineItem):
        if any(i.product.id == item.product.id for i in self._items):
            QMessageBox.information(self.parent(), "Duplicate Item", f"Product '{item.product.name}' is already in the PO list.")
            return
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount()); self._items.append(item); self.endInsertRows()
        self.total_cost_changed.emit()
    def remove_item_at_row(self, r):
        if 0 <= r < len(self._items): self.beginRemoveRows(QModelIndex(), r, r); del self._items[r]; self.endRemoveRows(); self.total_cost_changed.emit()
    def get_total_cost(self): return sum(item.total_cost for item in self._items).quantize(Decimal("0.01"))
    def get_po_items_dto(self): return [item.to_create_dto() for item in self._items]
    def has_items(self): return bool(self._items)

class PurchaseOrderDialog(QDialog):
    """A dialog for creating a new Purchase Order."""
    po_operation_completed = Signal()

    def __init__(self, core: ApplicationCore, outlet_id: uuid.UUID, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.core = core
        self.async_worker: AsyncWorker = core.async_worker
        self.company_id = self.core.current_company_id
        self.outlet_id = outlet_id
        self.setWindowTitle("Create New Purchase Order"); self.setMinimumSize(900, 700)
        self._setup_ui(); self._connect_signals(); self._load_initial_data()
        self._on_form_data_changed() # Set initial button state

    def _setup_ui(self):
        self.supplier_combo = QComboBox(); self.expected_delivery_date_edit = QDateEdit(QDate.currentDate().addDays(7)); self.expected_delivery_date_edit.setCalendarPopup(True)
        po_form_layout = QFormLayout(); po_form_layout.addRow("Supplier:", self.supplier_combo); po_form_layout.addRow("Expected Delivery:", self.expected_delivery_date_edit)
        self.product_search_input = QLineEdit(); self.product_search_input.setPlaceholderText("Enter Product SKU to add...")
        self.add_product_button = QPushButton("Add Item"); product_search_layout = QHBoxLayout()
        product_search_layout.addWidget(self.product_search_input, 1); product_search_layout.addWidget(self.add_product_button)
        self.po_table = QTableView(); self.table_model = PurchaseOrderTableModel(self); self.po_table.setModel(self.table_model)
        self.po_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch); self.po_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.total_cost_label = QLabel("<b>Total PO Cost: S$0.00</b>"); self.total_cost_label.setStyleSheet("font-size: 18px;")
        self.button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel); self.button_box.button(QDialogButtonBox.Save).setText("Create Purchase Order")
        main_layout = QVBoxLayout(self); main_layout.addLayout(po_form_layout); main_layout.addLayout(product_search_layout)
        main_layout.addWidget(self.po_table, 1); main_layout.addWidget(self.total_cost_label, alignment=Qt.AlignRight); main_layout.addWidget(self.button_box)

    def _connect_signals(self):
        self.add_product_button.clicked.connect(self._on_add_product_to_po); self.product_search_input.returnPressed.connect(self._on_add_product_to_po)
        self.button_box.accepted.connect(self._on_submit_po); self.button_box.rejected.connect(self.reject)
        self.table_model.total_cost_changed.connect(self._update_total_cost_label)
        self.supplier_combo.currentIndexChanged.connect(self._on_form_data_changed)
        # Use a custom signal because we need to know when rows are added/removed, not just when data is edited
        self.table_model.total_cost_changed.connect(self._on_form_data_changed)
        self.po_table.customContextMenuRequested.connect(self._on_table_context_menu)

    @Slot()
    def _on_form_data_changed(self): self.button_box.button(QDialogButtonBox.Save).setEnabled(self.supplier_combo.currentData() is not None and self.table_model.has_items())
    @Slot()
    def _update_total_cost_label(self): self.total_cost_label.setText(f"<b>Total PO Cost: S${self.table_model.get_total_cost():.2f}</b>"); self._on_form_data_changed()

    def _load_initial_data(self):
        def _on_done(r, e):
            if e or isinstance(r, Failure): 
                user_friendly_error = format_error_for_user(e or r)
                QMessageBox.critical(self, "Load Error", f"Failed to load suppliers: {user_friendly_error}"); return
            if isinstance(r, Success):
                self.supplier_combo.clear(); self.supplier_combo.addItem("-- Select Supplier --", userData=None)
                for supplier in r.value: self.supplier_combo.addItem(supplier.name, userData=supplier.id)
        self.async_worker.run_task(self.core.inventory_manager.get_all_suppliers(self.company_id), _on_done)

    @Slot()
    def _on_add_product_to_po(self):
        search_term = self.product_search_input.text().strip()
        if not search_term: return
        def _on_done(r, e):
            if e or isinstance(r, Failure):
                user_friendly_error = format_error_for_user(e or r)
                QMessageBox.warning(self, "Product Lookup Failed", f"Could not find product: {user_friendly_error}"); return
            if isinstance(r, Success) and r.value: self.table_model.add_item(POLineItem(r.value[0])); self.product_search_input.clear()
            else: QMessageBox.warning(self, "Not Found", f"No product found for '{search_term}'.")
        self.async_worker.run_task(self.core.product_manager.search_products(self.company_id, search_term, limit=1), _on_done)

    @Slot()
    def _on_submit_po(self):
        supplier_id = self.supplier_combo.currentData()
        if not supplier_id or not self.table_model.has_items(): self._on_form_data_changed(); return
        po_dto = PurchaseOrderCreateDTO(
            company_id=self.company_id, outlet_id=self.outlet_id, supplier_id=supplier_id,
            expected_delivery_date=datetime.combine(self.expected_delivery_date_edit.date().toPython(), datetime.min.time()),
            items=self.table_model.get_po_items_dto()
        )
        self.button_box.button(QDialogButtonBox.Save).setEnabled(False)
        def _on_done(r, e):
            self.button_box.button(QDialogButtonBox.Save).setEnabled(True)
            if e or isinstance(r, Failure):
                user_friendly_error = format_error_for_user(e or r)
                QMessageBox.critical(self, "Creation Failed", f"Could not create Purchase Order: {user_friendly_error}")
            elif isinstance(r, Success):
                QMessageBox.information(self, "Success", f"Purchase Order '{r.value.po_number}' created successfully!"); self.po_operation_completed.emit(); self.accept()
        self.async_worker.run_task(self.core.inventory_manager.create_purchase_order(po_dto), _on_done)

    @Slot(QPoint)
    def _on_table_context_menu(self, pos):
        index = self.po_table.indexAt(pos)
        if not index.isValid(): return
        menu = QMenu(self)
        remove_action = menu.addAction("Remove Item")
        if menu.exec(self.po_table.mapToGlobal(pos)) == remove_action:
            self.table_model.remove_item_at_row(index.row())
