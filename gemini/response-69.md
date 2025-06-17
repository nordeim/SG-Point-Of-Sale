I understand the immense frustration of seeing the exact same error after multiple attempts at a fix. This represents a significant failure in my diagnostic process, and I will not offer another incremental patch. The error's persistence despite my previous fixes to the `async_bridge` and other modules indicates that the root cause is not what I hypothesized. It is time for a fundamentally different approach.

This situation requires me to step back and re-evaluate the problem from first principles, assuming nothing about my previous analyses. The error is simple and direct: somewhere, the code is attempting to call `.connect` on the `Signal` class itself, not an instance of it.

### **1. A New Diagnostic Approach: Code Isolation and Hypothesis Invalidation**

My previous method of scanning the code has failed to locate the bug. Therefore, I will now use a process of elimination and code isolation to definitively find the source. The error occurs during the instantiation of `MainWindow`. `MainWindow` instantiates all six of the main application views. The bug *must* be in the `__init__` or import chain of one of these views.

I will now generate a special, temporary version of `app/ui/main_window.py` designed specifically for debugging. This version will instantiate the views one by one, allowing us to pinpoint exactly which view's initialization triggers the crash.

**This is not a final fix**, but a necessary diagnostic tool to break this loop and find the true source of the problem once and for all.

### **2. Diagnostic Tool: A Modified `main_window.py`**

Please replace your current `app/ui/main_window.py` with the following **temporary, diagnostic version**. Run `python3 app/main.py` again. This will help us isolate the faulty module. The application will likely still crash, but the point at which it crashes will tell us where the error lies.

```python
# File: app/ui/main_window.py (DIAGNOSTIC VERSION)
"""
The main window of the SG-POS application.
This QMainWindow acts as the shell, hosting different views.
DIAGNOSTIC VERSION: This file will be used to isolate the source of the startup error.
"""
import sys
from typing import Optional, Any
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel,
    QStackedWidget, QMenuBar, QMenu, QMessageBox, QApplication
)
from PySide6.QtCore import Slot, QEvent, QObject, QMetaObject, Qt, Q_ARG

from app.core.application_core import ApplicationCore
from app.core.async_bridge import AsyncWorker

# Import all views that will be hosted
print("[DIAGNOSTIC] Importing views...")
from app.ui.views.pos_view import POSView
print("[DIAGNOSTIC] ... POSView imported successfully.")
from app.ui.views.product_view import ProductView
print("[DIAGNOSTIC] ... ProductView imported successfully.")
from app.ui.views.customer_view import CustomerView
print("[DIAGNOSTIC] ... CustomerView imported successfully.")
from app.ui.views.inventory_view import InventoryView
print("[DIAGNOSTIC] ... InventoryView imported successfully.")
from app.ui.views.reports_view import ReportsView
print("[DIAGNOSTIC] ... ReportsView imported successfully.")
from app.ui.views.settings_view import SettingsView
print("[DIAGNOSTIC] ... SettingsView imported successfully.")
print("[DIAGNOSTIC] All views imported.")


class MainWindow(QMainWindow):
    """The main application window."""
    def __init__(self, core: ApplicationCore):
        super().__init__()
        print("[DIAGNOSTIC] MainWindow.__init__ started.")
        self.core = core
        self.async_worker: AsyncWorker = core.async_worker
        self.setWindowTitle("SG Point-of-Sale System")
        self.setGeometry(100, 100, 1440, 900)

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # --- Initialize and add all primary views ONE BY ONE ---
        print("[DIAGNOSTIC] Instantiating POSView...")
        self.pos_view = POSView(self.core)
        self.stacked_widget.addWidget(self.pos_view)
        print("[DIAGNOSTIC] ... POSView instantiated and added.")

        print("[DIAGNOSTIC] Instantiating ProductView...")
        self.product_view = ProductView(self.core)
        self.stacked_widget.addWidget(self.product_view)
        print("[DIAGNOSTIC] ... ProductView instantiated and added.")
        
        print("[DIAGNOSTIC] Instantiating CustomerView...")
        self.customer_view = CustomerView(self.core)
        self.stacked_widget.addWidget(self.customer_view)
        print("[DIAGNOSTIC] ... CustomerView instantiated and added.")
        
        print("[DIAGNOSTIC] Instantiating InventoryView...")
        self.inventory_view = InventoryView(self.core)
        self.stacked_widget.addWidget(self.inventory_view)
        print("[DIAGNOSTIC] ... InventoryView instantiated and added.")

        print("[DIAGNOSTIC] Instantiating ReportsView...")
        self.reports_view = ReportsView(self.core)
        self.stacked_widget.addWidget(self.reports_view)
        print("[DIAGNOSTIC] ... ReportsView instantiated and added.")

        print("[DIAGNOSTIC] Instantiating SettingsView...")
        self.settings_view = SettingsView(self.core)
        self.stacked_widget.addWidget(self.settings_view)
        print("[DIAGNOSTIC] ... SettingsView instantiated and added.")
        
        print("[DIAGNOSTIC] All views instantiated and added.")
        self.stacked_widget.setCurrentWidget(self.pos_view)
        self._create_menu()
        print("[DIAGNOSTIC] MainWindow.__init__ finished.")

    def _create_menu(self):
        """Creates the main menu bar with complete navigation."""
        menu_bar = self.menuBar()
        
        file_menu = menu_bar.addMenu("&File")
        exit_action = file_menu.addAction("E&xit")
        exit_action.triggered.connect(self.close)

        pos_menu = menu_bar.addMenu("&POS")
        pos_action = pos_menu.addAction("Sales Screen")
        pos_action.triggered.connect(lambda: self.stacked_widget.setCurrentWidget(self.pos_view))

        data_menu = menu_bar.addMenu("&Data Management")
        data_menu.addAction("Products", lambda: self.stacked_widget.setCurrentWidget(self.product_view))
        data_menu.addAction("Customers", lambda: self.stacked_widget.setCurrentWidget(self.customer_view))
        
        inventory_menu = menu_bar.addMenu("&Inventory")
        inventory_menu.addAction("Stock Management", lambda: self.stacked_widget.setCurrentWidget(self.inventory_view))
        
        reports_menu = menu_bar.addMenu("&Reports")
        reports_menu.addAction("Business Reports", lambda: self.stacked_widget.setCurrentWidget(self.reports_view))
        
        settings_menu = menu_bar.addMenu("&Settings")
        settings_menu.addAction("Application Settings", lambda: self.stacked_widget.setCurrentWidget(self.settings_view))

    def closeEvent(self, event: QEvent) -> None:
        """Handles window close event to gracefully shut down the application core."""
        # This is the correct shutdown logic from the previous fix.
        if self.core:
            self.core.shutdown()
        event.accept()
```

### **3. Required Action and Next Steps**

1.  **Replace** the contents of your existing `app/ui/main_window.py` with the **DIAGNOSTIC VERSION** provided above.
2.  **Run** the application again with `python3 app/main.py`.
3.  **Provide me with the complete console output.** The output will now contain `[DIAGNOSTIC]` print statements. The last message printed before the traceback will tell us exactly which view's initialization is causing the crash.

I apologize for making you perform this diagnostic step, but it is the only way to guarantee we find the true source of this elusive bug. Once you provide the new output, I will be able to perform a surgical fix on the single offending file and finally put this issue to rest.

