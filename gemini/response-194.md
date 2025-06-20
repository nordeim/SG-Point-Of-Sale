Excellent. I have performed a systematic review of the startup log.

### **Startup Log Validation Report**

*   **Initial Connection (`10:08:19`):** **Validated.** The application successfully establishes a connection to the PostgreSQL database, confirms the version and schema, and performs a connection test (`SELECT 1`). The transaction is immediately rolled back, which is correct and efficient behavior.
*   **Module Imports and View Loading (`10:08:25` - `10:09:32`):** **Validated.** The application starts without any `SyntaxError` or `ImportError`. This confirms that the hotfix for the f-string quoting in the model files was successful. The sequence of `SELECT` statements corresponds to the lazy loading of different UI views as a user would navigate through the application, and all queries are correctly formed.
*   **Final Shutdown (`Shutting down core resources...`):** **Validated.** The application terminates cleanly, indicating that the core shutdown sequence completed without issue.

**Conclusion:** The application is stable. The critical `SyntaxError` from the previous step is resolved. **Phase 2 and its subsequent hotfix are validated as successful.**

We are now ready to proceed with the final phase of planned improvements.

---
---

## **Execution Plan: Phase 3**

*   **Objective:** To implement the final planned UI/UX improvement by adding a debouncing mechanism to all relevant search fields, creating a consistent, high-performance user experience across the application.
*   **Tasks:**
    1.  **PERF-001:** Apply the `QTimer`-based search debouncing pattern, already present in `ProductView`, to the `CustomerView` and `InventoryView`.

### **Deep Analysis and Implementation Strategy**

The goal is to prevent the UI from firing a database query on every single keystroke. The `QTimer` approach is the correct and optimal solution for this within a Qt application.

1.  **Re-use Existing Pattern:** The implementation in `ProductView` is a perfect template. It uses a `QTimer` with `setSingleShot(True)`. The `textChanged` signal of the `QLineEdit` simply *starts* or *restarts* this timer. The actual database query is only triggered when the timer's `timeout` signal is emitted, which only happens after the user has paused typing for the specified interval (e.g., 350ms).

2.  **Systematic Application:** This pattern will be systematically applied to the following views:
    *   `app/ui/views/customer_view.py`
    *   `app/ui/views/inventory_view.py`

3.  **Refactoring Plan:** For each target file, the following steps will be taken:
    *   **Import `QTimer`:** Add `from PySide6.QtCore import QTimer`.
    *   **Instantiate Timer:** In the view's `__init__` method, create and configure the `QTimer` instance.
    *   **Update Signal Connections:** In the `_connect_signals` method, disconnect the direct link from `search_input.textChanged` to the loading method. Instead, connect `textChanged` to `search_timer.start` and connect `search_timer.timeout` to a new slot.
    *   **Create Trigger Slot:** Create a new simple slot (e.g., `_trigger_search`) that reads the text from the search input and calls the main data loading method.

This approach ensures consistency, reuses a proven pattern, and directly addresses the performance issue.

I will now execute this plan.

***

### **Phase 3 Execution: Complete Updated Files**

Here are the complete and updated replacement files with the search debouncing functionality implemented.

#### 1. `app/ui/views/customer_view.py`

This view now uses a `QTimer` to delay database queries until the user has stopped typing in the search bar, preventing excessive load and improving responsiveness.

```python
# File: app/ui/views/customer_view.py
"""The main view for managing customers."""
import uuid
from typing import List, Any, Optional

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableView,
    QMessageBox, QLineEdit, QHeaderView, QSizePolicy
)
from PySide6.QtCore import Slot, Signal, QAbstractTableModel, QModelIndex, Qt, QObject, QTimer

from app.core.application_core import ApplicationCore
from app.core.result import Success, Failure
from app.business_logic.dto.customer_dto import CustomerDTO
from app.ui.dialogs.customer_dialog import CustomerDialog
from app.core.async_bridge import AsyncWorker
from app.ui.widgets.managed_table_view import ManagedTableView

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

        # REFACTOR: Add a timer for debouncing search input
        self.search_timer = QTimer(self)
        self.search_timer.setSingleShot(True)
        self.search_timer.setInterval(350) # 350ms delay

        self._setup_ui()
        self._connect_signals()
        self._load_customers()

    def _setup_ui(self):
        """Initializes the UI widgets and layout."""
        top_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search customers by code, name, email, or phone...")
        self.add_button = QPushButton("Add New Customer")
        self.edit_button = QPushButton("Edit Selected")
        self.delete_button = QPushButton("Deactivate Selected")

        top_layout.addWidget(self.search_input, 1)
        top_layout.addStretch()
        top_layout.addWidget(self.add_button)
        top_layout.addWidget(self.edit_button)
        top_layout.addWidget(self.delete_button)
        
        self.managed_table = ManagedTableView()
        self.customer_model = CustomerTableModel([])
        self.managed_table.set_model(self.customer_model)
        
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
        """Connects UI signals to slots."""
        self.add_button.clicked.connect(self._on_add_customer)
        self.edit_button.clicked.connect(self._on_edit_customer)
        self.delete_button.clicked.connect(self._on_deactivate_customer)
        
        # REFACTOR: Connect search input to the timer for debouncing
        self.search_input.textChanged.connect(self.search_timer.start)
        self.search_timer.timeout.connect(self._trigger_search)
        
        self.managed_table.table().doubleClicked.connect(self._on_edit_customer)

    def _get_selected_customer(self) -> Optional[CustomerDTO]:
        """Helper to get the currently selected customer from the table."""
        selected_indexes = self.managed_table.table().selectionModel().selectedRows()
        if selected_indexes:
            row = selected_indexes[0].row()
            return self.customer_model.get_customer_at_row(row)
        return None

    @Slot()
    def _trigger_search(self):
        """Slot that is called by the timer's timeout to initiate a search."""
        self._load_customers(search_term=self.search_input.text())

    @Slot()
    def _load_customers(self, search_term: str = ""):
        """Loads customer data asynchronously into the table model."""
        company_id = self.core.current_company_id
        self.managed_table.show_loading()

        def _on_done(result: Any, error: Optional[Exception]):
            if error or isinstance(result, Failure):
                self.customer_model.refresh_data([])
                self.managed_table.show_empty(f"Error loading customers: {error or result.error}")
                QMessageBox.critical(self, "Load Error", f"Failed to load customers: {error or result.error}")
            elif isinstance(result, Success):
                customers = result.value
                self.customer_model.refresh_data(customers)
                if customers:
                    self.managed_table.show_table()
                else:
                    self.managed_table.show_empty("No customers found.")
        
        coro = self.core.customer_manager.search_customers(company_id, search_term) if search_term else self.core.customer_manager.get_all_customers(company_id)
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
            if error or isinstance(result, Failure):
                QMessageBox.warning(self, "Deactivation Failed", f"Could not deactivate customer: {error or result.error}")
            elif isinstance(result, Success) and result.value:
                QMessageBox.information(self, "Success", f"Customer '{selected_customer.name}' deactivated.")
                self._load_customers(search_term=self.search_input.text())
        
        coro = self.core.customer_manager.deactivate_customer(selected_customer.id)
        self.async_worker.run_task(coro, on_done_callback=_on_done)

    @Slot(bool, str)
    def _handle_customer_dialog_result(self, success: bool, message: str):
        """Slot to handle results from CustomerDialog and refresh the view."""
        if success:
            self._load_customers(search_term=self.search_input.text())
```

#### 2. `app/ui/views/inventory_view.py`

This view's "Current Stock" tab now also benefits from a debounced search input, ensuring a smoother user experience when searching through a large inventory.

```python
# File: app/ui/views/inventory_view.py
"""Main View for Inventory Management."""
from __future__ import annotations
from typing import List, Any, Optional, Dict
import uuid

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableView, QLabel, QLineEdit, QHeaderView, QSizePolicy, QMessageBox,
    QTabWidget
)
from PySide6.QtCore import Slot, Signal, QAbstractTableModel, QModelIndex, Qt, QObject, QPoint, QTimer
from PySide6.QtGui import QAction, QCursor

from app.core.application_core import ApplicationCore
from app.core.result import Success, Failure
from app.business_logic.dto.inventory_dto import InventorySummaryDTO, PurchaseOrderDTO, StockMovementDTO
from app.ui.dialogs.stock_adjustment_dialog import StockAdjustmentDialog
from app.ui.dialogs.purchase_order_dialog import PurchaseOrderDialog
from app.ui.dialogs.receive_po_dialog import ReceivePODialog
from app.core.async_bridge import AsyncWorker
from app.ui.widgets.managed_table_view import ManagedTableView

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

        # REFACTOR: Add a timer for debouncing inventory search
        self.inventory_search_timer = QTimer(self)
        self.inventory_search_timer.setSingleShot(True)
        self.inventory_search_timer.setInterval(350)

        self._setup_ui()
        self._connect_signals()
        self._on_tab_changed(0) # Trigger initial load for the first tab

    def _setup_ui(self):
        self.tab_widget = QTabWidget()
        self.inventory_summary_tab = self._create_inventory_summary_tab()
        self.purchase_orders_tab = self._create_purchase_orders_tab()
        self.stock_movements_tab = self._create_stock_movements_tab()
        self.tab_widget.addTab(self.inventory_summary_tab, "Current Stock")
        self.tab_widget.addTab(self.purchase_orders_tab, "Purchase Orders")
        self.tab_widget.addTab(self.stock_movements_tab, "Stock Movements")
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.tab_widget)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def _create_inventory_summary_tab(self) -> QWidget:
        tab = QWidget(); layout = QVBoxLayout(tab); top_layout = QHBoxLayout()
        self.inventory_search_input = QLineEdit(); self.inventory_search_input.setPlaceholderText("Search product by SKU or name...")
        self.adjust_stock_button = QPushButton("Adjust Stock")
        top_layout.addWidget(self.inventory_search_input, 1); top_layout.addStretch(); top_layout.addWidget(self.adjust_stock_button)
        
        self.inventory_managed_table = ManagedTableView()
        self.inventory_model = InventoryTableModel([])
        self.inventory_managed_table.set_model(self.inventory_model)
        
        table = self.inventory_managed_table.table()
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        table.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        
        layout.addLayout(top_layout)
        layout.addWidget(self.inventory_managed_table)
        return tab

    def _create_purchase_orders_tab(self) -> QWidget:
        tab = QWidget(); layout = QVBoxLayout(tab); top_layout = QHBoxLayout()
        self.new_po_button = QPushButton("New Purchase Order")
        self.receive_po_button = QPushButton("Receive Items on PO")
        top_layout.addStretch(); top_layout.addWidget(self.new_po_button); top_layout.addWidget(self.receive_po_button)
        
        self.po_managed_table = ManagedTableView()
        self.po_model = PurchaseOrderTableModel([])
        self.po_managed_table.set_model(self.po_model)
        
        table = self.po_managed_table.table()
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        table.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        
        layout.addLayout(top_layout)
        layout.addWidget(self.po_managed_table)
        return tab

    def _create_stock_movements_tab(self) -> QWidget:
        tab = QWidget(); layout = QVBoxLayout(tab)
        
        self.movements_managed_table = ManagedTableView()
        self.movements_model = StockMovementTableModel([])
        self.movements_managed_table.set_model(self.movements_model)
        self.movements_managed_table.table().horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        self.movements_title_label = QLabel("Click on a product in 'Current Stock' to see its history.")
        self.movements_title_label.setStyleSheet("font-size: 14px; padding: 5px;")
        
        layout.addWidget(self.movements_title_label)
        layout.addWidget(self.movements_managed_table)
        return tab

    def _connect_signals(self):
        self.tab_widget.currentChanged.connect(self._on_tab_changed)
        
        # REFACTOR: Connect search to timer for debouncing
        self.inventory_search_input.textChanged.connect(self.inventory_search_timer.start)
        self.inventory_search_timer.timeout.connect(self._trigger_inventory_search)

        self.adjust_stock_button.clicked.connect(self._on_adjust_stock)
        self.inventory_managed_table.table().doubleClicked.connect(self._on_view_product_stock_history)
        self.new_po_button.clicked.connect(self._on_new_po)
        self.po_managed_table.table().doubleClicked.connect(self._on_receive_po_items)
        self.receive_po_button.clicked.connect(self._on_receive_po_items)

    @Slot(int)
    def _on_tab_changed(self, index: int):
        if index == 0: self._load_inventory_summary()
        elif index == 1: self._load_purchase_orders()
        elif index == 2:
            self.movements_title_label.setText("Click on a product in 'Current Stock' to see its history.")
            self.movements_model.refresh_data([])
            self.movements_managed_table.show_empty("Select a product to view its movements.")

    @Slot()
    def _trigger_inventory_search(self):
        self._load_inventory_summary(search_term=self.inventory_search_input.text())

    def _load_inventory_summary(self, search_term: str = ""):
        self.inventory_managed_table.show_loading()
        def _on_done(r, e):
            if e or isinstance(r, Failure):
                self.inventory_model.refresh_data([])
                self.inventory_managed_table.show_empty(f"Error: {e or r.error}")
            elif isinstance(r, Success):
                self.inventory_model.refresh_data(r.value)
                self.inventory_managed_table.show_table() if r.value else self.inventory_managed_table.show_empty("No inventory items found.")
        self.async_worker.run_task(self.core.inventory_manager.get_inventory_summary(self.company_id, self.outlet_id, search_term=search_term), on_done_callback=_on_done)

    @Slot()
    def _on_adjust_stock(self):
        dialog = StockAdjustmentDialog(self.core, self.outlet_id, self.user_id, parent=self)
        dialog.operation_completed.connect(self._load_inventory_summary)
        dialog.exec()

    @Slot(QModelIndex)
    def _on_view_product_stock_history(self, index: QModelIndex):
        item = self.inventory_model.get_item_at_row(index.row())
        if not item: return
        self.tab_widget.setCurrentWidget(self.stock_movements_tab)
        self._load_stock_movements(product_id=item.product_id, product_name=item.product_name)

    def _load_purchase_orders(self):
        self.po_managed_table.show_loading()
        def _on_done(r, e):
            if e or isinstance(r, Failure):
                self.po_model.refresh_data([])
                self.po_managed_table.show_empty(f"Error: {e or r.error}")
            elif isinstance(r, Success):
                self.po_model.refresh_data(r.value)
                self.po_managed_table.show_table() if r.value else self.po_managed_table.show_empty("No purchase orders found.")
        self.async_worker.run_task(self.core.inventory_manager.get_all_purchase_orders(self.company_id, self.outlet_id), on_done_callback=_on_done)

    @Slot()
    def _on_new_po(self):
        dialog = PurchaseOrderDialog(self.core, self.outlet_id, parent=self)
        dialog.po_operation_completed.connect(self._load_purchase_orders)
        dialog.exec()

    @Slot()
    def _on_receive_po_items(self):
        selected_index = self.po_managed_table.table().currentIndex()
        if not selected_index.isValid():
            QMessageBox.information(self, "No Selection", "Please select a Purchase Order to receive items.")
            return
        
        selected_po = self.po_model.get_po_at_row(selected_index.row())
        if not selected_po: return

        if selected_po.status not in ['SENT', 'PARTIALLY_RECEIVED']:
            QMessageBox.warning(self, "Invalid Status", f"Cannot receive items for a PO with status '{selected_po.status.replace('_', ' ').title()}'.")
            return

        dialog = ReceivePODialog(selected_po, self)
        dialog.items_to_receive.connect(self._process_po_receipt)
        dialog.exec()

    @Slot(list)
    def _process_po_receipt(self, items_to_receive: List[Dict[str, Any]]):
        selected_po = self.po_model.get_po_at_row(self.po_managed_table.table().currentIndex().row())
        if not selected_po: return

        self.receive_po_button.setEnabled(False)
        
        def _on_done(result: Any, error: Optional[Exception]):
            self.receive_po_button.setEnabled(True)
            if error or isinstance(result, Failure):
                QMessageBox.critical(self, "Receiving Failed", f"Could not process receipt: {error or result.error}")
            elif isinstance(result, Success):
                QMessageBox.information(self, "Success", "Items received successfully.")
                self._load_purchase_orders()
                if self.tab_widget.currentIndex() == 0: # If user is looking at stock, refresh it
                    self._load_inventory_summary()

        coro = self.core.inventory_manager.receive_purchase_order_items(
            selected_po.id, items_to_receive, self.user_id
        )
        self.async_worker.run_task(coro, on_done_callback=_on_done)

    def _load_stock_movements(self, product_id: Optional[uuid.UUID] = None, product_name: str = "product"):
        if not product_id:
            self.movements_model.refresh_data([])
            self.movements_managed_table.show_empty("Select a product to view its movements.")
            return

        self.movements_title_label.setText(f"Stock Movement History for: {product_name} ({product_id})")
        self.movements_managed_table.show_loading()

        def _on_done(r, e):
            if e or isinstance(r, Failure):
                self.movements_model.refresh_data([])
                self.movements_managed_table.show_empty(f"Error: {e or r.error}")
            elif isinstance(r, Success):
                self.movements_model.refresh_data(r.value)
                self.movements_managed_table.show_table() if r.value else self.movements_managed_table.show_empty("No movement history for this item.")
        
        self.async_worker.run_task(self.core.inventory_manager.get_stock_movements_for_product(self.company_id, product_id), on_done_callback=_on_done)
```

***

### **Phase 3 Completion Summary**

*   **Task 1 (PERF-001):** The `QTimer`-based debouncing pattern has been successfully implemented in `CustomerView` and `InventoryView`. All major search fields in the application now benefit from this performance optimization, ensuring a consistent and responsive user experience.

This completes all planned tasks. The codebase is now in an improved state, addressing all identified issues from the assessment report. The application is more performant, user-friendly, and architecturally robust.

---
https://drive.google.com/file/d/1RCXFINEZICAaOvGYiNGVAoS-qipaBo6C/view?usp=sharing, https://aistudio.google.com/app/prompts?state=%7B%22ids%22:%5B%221TKe0ekNjzancuPbfP1wc-fU63TyIHmTB%22%5D,%22action%22:%22open%22,%22userId%22:%22108686197475781557359%22,%22resourceKeys%22:%7B%7D%7D&usp=sharing, https://drive.google.com/file/d/1hbVzkqGQK2zo6M5bu4Uqv1e5tobkX94p/view?usp=sharing, https://drive.google.com/file/d/1jX2cVSBnmORhZT5lXj956XsVfdzoY3YR/view?usp=sharing, https://drive.google.com/file/d/1lOFGKFYhRFLju6fzthC10s4WatD0_ikm/view?usp=sharing, https://drive.google.com/file/d/1ta9w_VGlbg9sSUQ3z90sjTOo2YamC7Lz/view?usp=sharing

