# File: app/ui/main_window.py
"""
The main window of the SG-POS application.
This QMainWindow acts as the shell, hosting different views like the POS screen,
inventory management, etc., and providing navigation.

This version implements lazy loading for all non-default views to improve
startup performance.
"""
import sys
from typing import Dict, Optional, Type

from PySide6.QtWidgets import (
    QMainWindow, QWidget,
    QStackedWidget, QMenuBar
)
from PySide6.QtCore import Slot, QEvent

from app.core.application_core import ApplicationCore
from app.core.async_bridge import AsyncWorker

# Import all view classes that will be lazy-loaded
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

        # --- Lazy Loading Implementation ---
        # 1. A dictionary to hold view definitions and cache instances
        self.views: Dict[str, Dict[str, Optional[Type[QWidget]]]] = {
            "product":   {"class": ProductView,   "instance": None},
            "customer":  {"class": CustomerView,  "instance": None},
            "inventory": {"class": InventoryView, "instance": None},
            "reports":   {"class": ReportsView,   "instance": None},
            "settings":  {"class": SettingsView,  "instance": None},
        }

        # 2. Eagerly create and show only the default view
        self.pos_view = POSView(self.core)
        self.stacked_widget.addWidget(self.pos_view)
        self.stacked_widget.setCurrentWidget(self.pos_view)
        
        # 3. Create the menu, which will connect actions to the lazy loader
        self._create_menu()

    def _create_menu(self):
        """Creates the main menu bar with navigation actions wired for lazy loading."""
        menu_bar = self.menuBar()
        
        file_menu = menu_bar.addMenu("&File")
        file_menu.addAction("E&xit", self.close)

        pos_menu = menu_bar.addMenu("&POS")
        pos_menu.addAction("Sales Screen", lambda: self.stacked_widget.setCurrentWidget(self.pos_view))

        data_menu = menu_bar.addMenu("&Data Management")
        data_menu.addAction("Products", lambda: self._show_view("product"))
        data_menu.addAction("Customers", lambda: self._show_view("customer"))
        
        inventory_menu = menu_bar.addMenu("&Inventory")
        inventory_menu.addAction("Stock Management", lambda: self._show_view("inventory"))
        
        reports_menu = menu_bar.addMenu("&Reports")
        reports_menu.addAction("Business Reports", lambda: self._show_view("reports"))
        
        settings_menu = menu_bar.addMenu("&Settings")
        settings_menu.addAction("Application Settings", lambda: self._show_view("settings"))

    def _show_view(self, view_key: str):
        """
        Generic handler for showing a view. Creates the view on first request.
        
        Args:
            view_key: The key corresponding to the view in the self.views dictionary.
        """
        if view_key not in self.views:
            return

        view_info = self.views[view_key]
        
        # If the view instance hasn't been created yet, create and cache it
        if view_info["instance"] is None:
            view_class = view_info["class"]
            view_info["instance"] = view_class(self.core)
            self.stacked_widget.addWidget(view_info["instance"])

        # Set the current widget to the now-guaranteed-to-exist instance
        self.stacked_widget.setCurrentWidget(view_info["instance"])

    def closeEvent(self, event: QEvent) -> None:
        """Handles window close event to gracefully shut down the application core."""
        if self.core:
            self.core.shutdown()
        event.accept()
