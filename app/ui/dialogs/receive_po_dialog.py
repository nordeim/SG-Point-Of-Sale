# File: app/ui/dialogs/receive_po_dialog.py
"""A QDialog for receiving items against a Purchase Order."""
from __future__ import annotations
from decimal import Decimal
from typing import List, Optional, Any, Dict

from PySide6.QtCore import (
    Qt, QAbstractTableModel, QModelIndex, Slot, Signal, QObject
)
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QTableView, QPushButton, QDialogButtonBox,
    QMessageBox, QHeaderView, QLabel
)

from app.business_logic.dto.inventory_dto import PurchaseOrderDTO, PurchaseOrderItemDTO

class ReceivePOTableModel(QAbstractTableModel):
    """A Qt Table Model for managing items being received against a PO."""
    HEADERS = ["SKU", "Product Name", "Ordered", "Received", "Outstanding", "Receiving Now"]
    COLUMN_RECEIVING_NOW = 5

    items_changed = Signal()

    def __init__(self, items: List[PurchaseOrderItemDTO], parent: Optional[QObject] = None):
        super().__init__(parent)
        self._items = items
        # Initialize "receiving now" quantities
        for item in self._items:
            item.receiving_now = (item.quantity_ordered - item.quantity_received)

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._items)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self.HEADERS)

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole) -> Any:
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.HEADERS[section]

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        if not index.isValid():
            return None
        item = self._items[index.row()]
        col = index.column()

        if role == Qt.DisplayRole:
            outstanding = item.quantity_ordered - item.quantity_received
            if col == 0: return item.sku
            if col == 1: return item.product_name
            if col == 2: return f"{item.quantity_ordered:.4f}"
            if col == 3: return f"{item.quantity_received:.4f}"
            if col == 4: return f"{outstanding:.4f}"
            if col == 5: return f"{item.receiving_now:.4f}"
        
        if role == Qt.EditRole and col == self.COLUMN_RECEIVING_NOW:
            return str(item.receiving_now)

        if role == Qt.TextAlignmentRole and col in [2, 3, 4, 5]:
            return Qt.AlignRight | Qt.AlignVCenter

    def setData(self, index: QModelIndex, value: Any, role: int = Qt.EditRole) -> bool:
        if role == Qt.EditRole and index.column() == self.COLUMN_RECEIVING_NOW:
            item = self._items[index.row()]
            outstanding = item.quantity_ordered - item.quantity_received
            try:
                new_qty = Decimal(value)
                if new_qty < 0:
                    QMessageBox.warning(self.parent(), "Invalid Quantity", "Receiving quantity cannot be negative.")
                    return False
                if new_qty > outstanding:
                    QMessageBox.warning(self.parent(), "Invalid Quantity", f"Cannot receive more than the outstanding quantity of {outstanding:.4f}.")
                    return False
                
                item.receiving_now = new_qty
                self.dataChanged.emit(index, index)
                self.items_changed.emit()
                return True
            except (ValueError, TypeError):
                QMessageBox.warning(self.parent(), "Invalid Input", "Please enter a valid number.")
                return False
        return False

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        flags = super().flags(index)
        if index.column() == self.COLUMN_RECEIVING_NOW:
            flags |= Qt.ItemIsEditable
        return flags

    def get_items_to_receive(self) -> List[Dict[str, Any]]:
        """Returns a list of items with a non-zero receiving quantity."""
        return [
            {"product_id": item.product_id, "quantity_received": item.receiving_now}
            for item in self._items if item.receiving_now > 0
        ]

class ReceivePODialog(QDialog):
    """Dialog to receive items for a specific purchase order."""
    
    # Signal emitted when the user confirms the items to receive.
    # Payload: list of dicts [{'product_id': UUID, 'quantity_received': Decimal}]
    items_to_receive = Signal(list)

    def __init__(self, po: PurchaseOrderDTO, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.po = po
        self.setWindowTitle(f"Receive Items for PO: {po.po_number}")
        self.setMinimumSize(800, 400)

        self._setup_ui()
        self._connect_signals()
        self._on_items_changed() # Initial check for button state

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        
        info_label = QLabel(f"<b>Supplier:</b> {self.po.supplier_name}<br>"
                            f"<b>Status:</b> {self.po.status.replace('_', ' ').title()}")
        main_layout.addWidget(info_label)

        self.table_view = QTableView()
        self.table_model = ReceivePOTableModel(self.po.items, self)
        self.table_view.setModel(self.table_model)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        main_layout.addWidget(self.table_view)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        self.button_box.button(QDialogButtonBox.Save).setText("Receive Items")
        main_layout.addWidget(self.button_box)

    def _connect_signals(self):
        self.button_box.accepted.connect(self._on_accept)
        self.button_box.rejected.connect(self.reject)
        self.table_model.items_changed.connect(self._on_items_changed)

    @Slot()
    def _on_items_changed(self):
        """Enable the save button only if there are items to receive."""
        can_receive = any(item.receiving_now > 0 for item in self.table_model._items)
        self.button_box.button(QDialogButtonBox.Save).setEnabled(can_receive)

    @Slot()
    def _on_accept(self):
        items = self.table_model.get_items_to_receive()
        if not items:
            QMessageBox.warning(self, "No Items", "Please enter a quantity for at least one item to receive.")
            return

        self.items_to_receive.emit(items)
        self.accept()
