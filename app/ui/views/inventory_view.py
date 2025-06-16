# File: app/ui/views/inventory_view.py
"""Main View for Inventory Management."""
from __future__ import annotations
from typing import List, Any, Optional
import uuid

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableView, QLabel, QLineEdit, QHeaderView, QSizePolicy, QMessageBox,
    QTabWidget
)
from PySide6.QtCore import Slot, Signal, QAbstractTableModel, QModelIndex, Qt, QObject, QPoint
from PySide6.QtGui import QAction, QCursor

from app.core.application_core import ApplicationCore
from app.core.result import Success, Failure
from app.business_logic.dto.inventory_dto import InventorySummaryDTO, PurchaseOrderDTO, StockMovementDTO
from app.ui.dialogs.stock_adjustment_dialog import StockAdjustmentDialog
from app.ui.dialogs.purchase_order_dialog import PurchaseOrderDialog
from app.core.async_bridge import AsyncWorker

class InventoryTableModel(QAbstractTableModel):
    HEADERS = ["SKU", "Name", "Category", "On Hand", "Reorder Pt.", "Cost", "Selling Price", "Active"]
    def __init__(self, items: List[InventorySummaryDTO], parent: Optional[QObject] = None): super().__init__(parent); self._items = items
    def rowCount(self, p=QModelIndex()): return len(self._items)
    def columnCount(self, p=QModelIndex()): return len(self.HEADERS)
    def headerData(self, s, o, r=Qt.DisplayRole):
        if r == Qt.DisplayRole and o == Qt.Horizontal: return self.HEADERS[s]
    def data(self, i, r=Qt.DisplayRole):
        if not i.isValid(): return
        item = self._items[i.row()]
        col = i.column()
        if r == Qt.DisplayRole:
            if col == 0: return item.sku
            if col == 1: return item.name
            if col == 2: return item.category_name or "N/A"
            if col == 3: return str(item.quantity_on_hand)
            if col == 4: return str(item.reorder_point)
            if col == 5: return f"S${item.cost_price:.2f}"
            if col == 6: return f"S${item.selling_price:.2f}"
            if col == 7: return "Yes" if item.is_active else "No"
        if r == Qt.TextAlignmentRole:
            if col in [3, 4, 5, 6]: return Qt.AlignRight | Qt.AlignVCenter
            if col == 7: return Qt.AlignCenter
    def get_item_at_row(self, r): return self._items[r] if 0 <= r < len(self._items) else None
    def refresh_data(self, new_items): self.beginResetModel(); self._items = new_items; self.endResetModel()

class PurchaseOrderTableModel(QAbstractTableModel):
    HEADERS = ["PO Number", "Supplier", "Order Date", "Expected", "Total (S$)", "Status"]
    def __init__(self, pos: List[PurchaseOrderDTO], parent: Optional[QObject] = None): super().__init__(parent); self._pos = pos
    def rowCount(self, p=QModelIndex()): return len(self._pos)
    def columnCount(self, p=QModelIndex()): return len(self.HEADERS)
    def headerData(self, s, o, r=Qt.DisplayRole):
        if r == Qt.DisplayRole and o == Qt.Horizontal: return self.HEADERS[s]
    def data(self, i, r=Qt.DisplayRole):
        if not i.isValid(): return
        po = self._pos[i.row()]
        col = i.column()
        if r == Qt.DisplayRole:
            if col == 0: return po.po_number
            if col == 1: return po.supplier_name
            if col == 2: return po.order_date.strftime("%Y-%m-%d")
            if col == 3: return po.expected_delivery_date.strftime("%Y-%m-%d") if po.expected_delivery_date else "N/A"
            if col == 4: return f"{po.total_amount:.2f}"
            if col == 5: return po.status.replace('_', ' ').title()
        if r == Qt.TextAlignmentRole:
            if col == 4: return Qt.AlignRight | Qt.AlignVCenter
            if col == 5: return Qt.AlignCenter
    def get_po_at_row(self, r): return self._pos[r] if 0 <= r < len(self._pos) else None
    def refresh_data(self, new_pos): self.beginResetModel(); self._pos = new_pos; self.endResetModel()

class StockMovementTableModel(QAbstractTableModel):
    HEADERS = ["Date", "Product", "SKU", "Type", "Change", "User", "Notes"]
    def __init__(self, movements: List[StockMovementDTO], parent: Optional[QObject] = None): super().__init__(parent); self._movements = movements
    def rowCount(self, p=QModelIndex()): return len(self._movements)
    def columnCount(self, p=QModelIndex()): return len(self.HEADERS)
    def headerData(self, s, o, r=Qt.DisplayRole):
        if r == Qt.DisplayRole and o == Qt.Horizontal: return self.HEADERS[s]
    def data(self, i, r=Qt.DisplayRole):
        if not i.isValid(): return
        m = self._movements[i.row()]
        col = i.column()
        if r == Qt.DisplayRole:
            if col == 0: return m.created_at.strftime("%Y-%m-%d %H:%M")
            if col == 1: return m.product_name
            if col == 2: return m.sku
            if col == 3: return m.movement_type.replace('_', ' ').title()
            if col == 4: change = m.quantity_change; return f"+{change}" if change > 0 else str(change)
            if col == 5: return m.created_by_user_name or "System"
            if col == 6: return m.notes or "N/A"
        if r == Qt.TextAlignmentRole and col == 4: return Qt.AlignRight | Qt.AlignVCenter
    def refresh_data(self, new_m): self.beginResetModel(); self._movements = new_m; self.endResetModel()

class InventoryView(QWidget):
    """A view to display stock levels and initiate inventory operations."""
    def __init__(self, core: ApplicationCore, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.core = core
        self.async_worker: AsyncWorker = core.async_worker
        self.company_id = self.core.current_company_id
        self.outlet_id = self.core.current_outlet_id
        self.user_id = self.core.current_user_id
        self._setup_ui()
        self._connect_signals()
        self._load_inventory_summary()

    def _setup_ui(self):
        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(self._create_inventory_summary_tab(), "Current Stock")
        self.tab_widget.addTab(self._create_purchase_orders_tab(), "Purchase Orders")
        self.tab_widget.addTab(self._create_stock_movements_tab(), "Stock Movements")
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.tab_widget)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def _create_inventory_summary_tab(self):
        tab = QWidget(); layout = QVBoxLayout(tab); top_layout = QHBoxLayout()
        self.inventory_search_input = QLineEdit(); self.inventory_search_input.setPlaceholderText("Search product...")
        self.adjust_stock_button = QPushButton("Adjust Stock")
        top_layout.addWidget(self.inventory_search_input, 1); top_layout.addStretch(); top_layout.addWidget(self.adjust_stock_button)
        self.inventory_table = QTableView(); self.inventory_model = InventoryTableModel([])
        self.inventory_table.setModel(self.inventory_model); self.inventory_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.inventory_table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows); self.inventory_table.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        layout.addLayout(top_layout); layout.addWidget(self.inventory_table)
        return tab

    def _create_purchase_orders_tab(self):
        tab = QWidget(); layout = QVBoxLayout(tab); top_layout = QHBoxLayout()
        self.new_po_button = QPushButton("New Purchase Order"); self.receive_po_button = QPushButton("Receive Items on PO")
        top_layout.addStretch(); top_layout.addWidget(self.new_po_button); top_layout.addWidget(self.receive_po_button)
        self.po_table = QTableView(); self.po_model = PurchaseOrderTableModel([])
        self.po_table.setModel(self.po_model); self.po_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.po_table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows); self.po_table.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        layout.addLayout(top_layout); layout.addWidget(self.po_table)
        return tab

    def _create_stock_movements_tab(self):
        tab = QWidget(); layout = QVBoxLayout(tab)
        self.movements_table = QTableView(); self.movements_model = StockMovementTableModel([])
        self.movements_table.setModel(self.movements_model); self.movements_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.movements_title_label = QLabel("Stock movement history will appear here.")
        layout.addWidget(self.movements_title_label); layout.addWidget(self.movements_table)
        return tab

    def _connect_signals(self):
        self.tab_widget.currentChanged.connect(self._on_tab_changed)
        self.inventory_search_input.textChanged.connect(self._on_inventory_search)
        self.adjust_stock_button.clicked.connect(self._on_adjust_stock)
        self.inventory_table.doubleClicked.connect(self._on_view_product_stock_history)
        self.new_po_button.clicked.connect(self._on_new_po)
        self.receive_po_button.clicked.connect(self._on_receive_po_items)

    @Slot(int)
    def _on_tab_changed(self, index):
        if index == 0: self._load_inventory_summary()
        elif index == 1: self._load_purchase_orders()
        elif index == 2: self.movements_title_label.setText("Stock movement history will appear here."); self.movements_model.refresh_data([])

    def _load_inventory_summary(self, search_term: str = ""):
        def _on_done(r, e):
            if e or isinstance(r, Failure): QMessageBox.critical(self, "Error", f"Failed to load inventory: {e or r.error}")
            elif isinstance(r, Success): self.inventory_model.refresh_data(r.value)
        self.async_worker.run_task(self.core.inventory_manager.get_inventory_summary(self.company_id, self.outlet_id, search_term=search_term), _on_done)

    @Slot(str)
    def _on_inventory_search(self, text): self._load_inventory_summary(search_term=text)

    @Slot()
    def _on_adjust_stock(self):
        dialog = StockAdjustmentDialog(self.core, self.outlet_id, self.user_id, parent=self)
        dialog.operation_completed.connect(self._load_inventory_summary)
        dialog.exec()

    @Slot(QModelIndex)
    def _on_view_product_stock_history(self, index):
        item = self.inventory_model.get_item_at_row(index.row())
        if not item: return
        self.tab_widget.setCurrentWidget(self.stock_movements_tab)
        self._load_stock_movements(product_id=item.product_id, product_sku=item.sku)

    def _load_purchase_orders(self):
        def _on_done(r, e):
            if e or isinstance(r, Failure): QMessageBox.critical(self, "Error", f"Failed to load purchase orders: {e or r.error}")
            elif isinstance(r, Success): self.po_model.refresh_data(r.value)
        self.async_worker.run_task(self.core.inventory_manager.get_all_purchase_orders(self.company_id, self.outlet_id), _on_done)

    @Slot()
    def _on_new_po(self):
        dialog = PurchaseOrderDialog(self.core, self.outlet_id, parent=self)
        dialog.po_operation_completed.connect(self._load_purchase_orders)
        dialog.exec()

    @Slot()
    def _on_receive_po_items(self):
        selected_po = self.po_model.get_po_at_row(self.po_table.currentIndex().row())
        if not selected_po: QMessageBox.information(self, "No Selection", "Please select a Purchase Order to receive items."); return
        QMessageBox.information(self, "Not Implemented", f"Functionality to receive items for PO {selected_po.po_number} is not yet implemented.")

    def _load_stock_movements(self, product_id: Optional[uuid.UUID] = None, product_sku: str = "product"):
        if not product_id: self.movements_model.refresh_data([]); return
        self.movements_title_label.setText(f"Stock Movement History for: {product_sku}")
        def _on_done(r, e):
            if e or isinstance(r, Failure): QMessageBox.critical(self, "Error", f"Failed to load stock movements: {e or r.error}")
            elif isinstance(r, Success): self.movements_model.refresh_data(r.value)
        self.async_worker.run_task(self.core.inventory_manager.get_stock_movements_for_product(self.company_id, product_id), _on_done)
