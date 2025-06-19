# File: app/ui/views/dashboard_view.py
"""The main dashboard view for displaying Key Performance Indicators (KPIs)."""
from __future__ import annotations
from typing import Optional, Any
from decimal import Decimal

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QSizePolicy, QGridLayout
)
from PySide6.QtCore import Qt, QObject, Slot

from app.core.application_core import ApplicationCore
from app.core.result import Success, Failure
from app.business_logic.dto.reporting_dto import DashboardStatsDTO
from app.ui.widgets.kpi_widget import KpiWidget

class DashboardView(QWidget):
    """A view widget to display a dashboard of business KPIs."""
    
    def __init__(self, core: ApplicationCore, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.core = core
        self.async_worker = core.async_worker
        
        self._setup_ui()
        self._connect_signals()
        
    def showEvent(self, event):
        """Overrides QWidget.showEvent to trigger data loading when the view becomes visible."""
        super().showEvent(event)
        # Load data every time the dashboard is shown to ensure it's fresh.
        self._load_data()

    def _setup_ui(self):
        """Initializes the UI widgets and layout."""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        title = QLabel("Dashboard")
        title.setStyleSheet("font-size: 28px; font-weight: bold; padding-bottom: 10px;")
        
        # Grid layout for KPIs
        kpi_layout = QGridLayout()
        kpi_layout.setSpacing(20)

        self.sales_kpi = KpiWidget("Today's Sales")
        self.transactions_kpi = KpiWidget("Today's Transactions")
        self.customers_kpi = KpiWidget("New Customers (Month)")
        self.low_stock_kpi = KpiWidget("Low Stock Items")
        self.low_stock_kpi.set_value_color("#E74C3C") # Use a warning color for low stock

        kpi_layout.addWidget(self.sales_kpi, 0, 0)
        kpi_layout.addWidget(self.transactions_kpi, 0, 1)
        kpi_layout.addWidget(self.customers_kpi, 1, 0)
        kpi_layout.addWidget(self.low_stock_kpi, 1, 1)

        main_layout.addWidget(title)
        main_layout.addLayout(kpi_layout)
        main_layout.addStretch()
        
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
    def _connect_signals(self):
        """Connect UI signals to slots."""
        pass # No interactive signals yet.
        
    @Slot()
    def _load_data(self):
        """Fetches and displays dashboard data."""
        # Set loading text on all KPI widgets
        self.sales_kpi.set_kpi_value("Loading...")
        self.transactions_kpi.set_kpi_value("...")
        self.customers_kpi.set_kpi_value("...")
        self.low_stock_kpi.set_kpi_value("...")

        def on_done(result: Any, error: Optional[Exception]):
            if error or isinstance(result, Failure):
                error_msg = f"Error: {error or result.error}"
                self.sales_kpi.set_kpi_value(error_msg)
                self.transactions_kpi.set_kpi_value("N/A")
                self.customers_kpi.set_kpi_value("N/A")
                self.low_stock_kpi.set_kpi_value("N/A")
                return

            if isinstance(result, Success):
                stats: DashboardStatsDTO = result.value
                self.sales_kpi.set_kpi_value(f"S$ {stats.total_sales_today:,.2f}")
                self.transactions_kpi.set_kpi_value(f"{stats.transaction_count_today}")
                self.customers_kpi.set_kpi_value(f"{stats.new_customers_this_month}")
                self.low_stock_kpi.set_kpi_value(f"{stats.low_stock_item_count}")
        
        coro = self.core.reporting_manager.generate_dashboard_stats(self.core.current_company_id)
        self.core.async_worker.run_task(coro, on_done_callback=on_done)
