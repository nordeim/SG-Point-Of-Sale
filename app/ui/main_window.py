# File: app/ui/main_window.py
"""
The main window of the SG-POS application.
This QMainWindow acts as the shell, hosting different views like the POS screen,
inventory management, etc., and providing navigation.
"""
import sys
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout,
    QStackedWidget, QMenuBar, QMenu
)
from PySide6.QtCore import Slot, QEvent

from app.core.application_core import ApplicationCore
from app.core.async_bridge import AsyncWorker

from app.ui.views.pos_view import POSView
from app.ui.views.product_view import ProductView
from app.ui.views.customer_view import CustomerView
from app.ui.views.inventory_view import InventoryView
from app.ui.views.reports_view import ReportsView
from app.ui.views.settings_view import SettingsView

class MainWindow(QMainWindow):
    """The main application window."""
    def __init__(self, core: ApplicationCore):
        super().__init__()
        self.core = core
        self.async_worker: AsyncWorker = core.async_worker
        self.setWindowTitle("SG Point-of-Sale System")
        self.setGeometry(100, 100, 1440, 900)

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.pos_view = POSView(self.core)
        self.product_view = ProductView(self.core)
        self.customer_view = CustomerView(self.core)
        self.inventory_view = InventoryView(self.core)
        self.reports_view = ReportsView(self.core)
        self.settings_view = SettingsView(self.core)

        self.stacked_widget.addWidget(self.pos_view)
        self.stacked_widget.addWidget(self.product_view)
        self.stacked_widget.addWidget(self.customer_view)
        self.stacked_widget.addWidget(self.inventory_view)
        self.stacked_widget.addWidget(self.reports_view)
        self.stacked_widget.addWidget(self.settings_view)
        
        self.stacked_widget.setCurrentWidget(self.pos_view)
        self._create_menu()

    def _create_menu(self):
        menu_bar = self.menuBar()
        
        file_menu = menu_bar.addMenu("&File")
        exit_action = file_menu.addAction("E&xit")
        exit_action.triggered.connect(self.close)

        pos_menu = menu_bar.addMenu("&POS")
        pos_menu.addAction("Sales Screen", lambda: self.stacked_widget.setCurrentWidget(self.pos_view))

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
        if self.core:
            self.core.shutdown()
        event.accept()
