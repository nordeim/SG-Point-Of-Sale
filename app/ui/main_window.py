# File: app/ui/main_window.py
"""
The main window of the SG-POS application.
This QMainWindow acts as the shell, hosting different views like the POS screen,
inventory management, etc., and providing navigation.
"""
import asyncio
import sys
from typing import Optional, Any
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel,
    QStackedWidget, QMenuBar, QMenu, QMessageBox, QApplication
)
from PySide6.QtCore import Slot, QEvent, QObject, QMetaObject, Qt, QGenericArgument as Q_ARG

from app.core.application_core import ApplicationCore
from app.core.async_bridge import AsyncWorker
from app.core.exceptions import CoreException

# Import all views that will be hosted
from app.ui.views.product_view import ProductView
from app.ui.views.customer_view import CustomerView
from app.ui.views.pos_view import POSView
from app.ui.views.inventory_view import InventoryView
# from app.ui.views.reports_view import ReportsView # To be implemented in Stage 5
# from app.ui.views.settings_view import SettingsView # To be implemented in Stage 5


class MainWindow(QMainWindow):
    """The main application window."""

    def __init__(self, core: ApplicationCore):
        """
        Initializes the main window.
        
        Args:
            core: The central ApplicationCore instance.
        """
        super().__init__()
        self.core = core
        self.async_worker: AsyncWorker = core.async_worker

        self.setWindowTitle("SG Point-of-Sale System")
        self.setGeometry(100, 100, 1280, 720)

        # Create a QStackedWidget to hold the different views
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # --- Initialize and add actual views ---
        self.pos_view = POSView(self.core)
        self.product_view = ProductView(self.core)
        self.customer_view = CustomerView(self.core)
        self.inventory_view = InventoryView(self.core)

        # Add views to the stack
        self.stacked_widget.addWidget(self.pos_view)
        self.stacked_widget.addWidget(self.product_view)
        self.stacked_widget.addWidget(self.customer_view)
        self.stacked_widget.addWidget(self.inventory_view)
        
        # Show the POS view by default
        self.stacked_widget.setCurrentWidget(self.pos_view)

        # --- Connect the AsyncWorker's general task_finished signal ---
        self.async_worker.task_finished.connect(self._handle_async_task_result)

        # --- Create menu bar for navigation ---
        self._create_menu()

    def _create_menu(self):
        """Creates the main menu bar with navigation items."""
        menu_bar = self.menuBar()
        
        # File Menu
        file_menu = menu_bar.addMenu("&File")
        exit_action = file_menu.addAction("E&xit")
        exit_action.triggered.connect(self.close)

        # POS Menu
        pos_menu = menu_bar.addMenu("&POS")
        pos_action = pos_menu.addAction("Sales")
        pos_action.triggered.connect(lambda: self.stacked_widget.setCurrentWidget(self.pos_view))

        # Data Management Menu
        data_menu = menu_bar.addMenu("&Data Management")
        product_action = data_menu.addAction("Products")
        product_action.triggered.connect(lambda: self.stacked_widget.setCurrentWidget(self.product_view))
        customer_action = data_menu.addAction("Customers")
        customer_action.triggered.connect(lambda: self.stacked_widget.setCurrentWidget(self.customer_view))

        # Inventory Menu (Populated in Stage 4)
        inventory_menu = menu_bar.addMenu("&Inventory")
        inventory_action = inventory_menu.addAction("Stock Management")
        inventory_action.triggered.connect(lambda: self.stacked_widget.setCurrentWidget(self.inventory_view))

    @Slot(object, object)
    def _handle_async_task_result(self, result: Any, error: Optional[Exception]):
        if error:
            print(f"Unhandled async error: {error}", file=sys.stderr)

    def closeEvent(self, event: QEvent) -> None:
        print("Main window closing. Initiating ApplicationCore shutdown...")
        
        async def shutdown_task():
            try:
                await self.core.shutdown()
                print("ApplicationCore shutdown complete.")
            except Exception as e:
                print(f"Error during ApplicationCore shutdown: {e}", file=sys.stderr)
                QMetaObject.invokeMethod(self, "show_shutdown_error", Qt.ConnectionType.QueuedConnection, Q_ARG(str, str(e)))
            QMetaObject.invokeMethod(self, "accept_close_event", Qt.ConnectionType.QueuedConnection)

        self.async_worker.run_task(shutdown_task())
        
        event.ignore()

    @Slot()
    def accept_close_event(self) -> None:
        QApplication.instance().quit()

    @Slot(str)
    def show_shutdown_error(self, error_message: str) -> None:
        QMessageBox.critical(self, "Shutdown Error", f"Failed to gracefully shut down application:\n{error_message}")
