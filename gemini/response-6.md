```markdown
# Detailed Execution Plan: Building the SG-POS System (Production-Worthy) - Continued

This document continues the detailed execution plan for building the SG Point-of-Sale (SG-POS) system, resuming from where the previous response left off. We will complete Stage 5 and finalize the plan.

---

## **Stage 5: Business Intelligence & Final Polish - Reporting, GST & Settings**

**Objective:** To build the reporting and analytics features that provide business insights, ensure full regulatory compliance, and add the final layer of professional polish to the application.

### **Phase 5.4: UI for Reporting and Settings**

#### **1. `app/ui/views/reports_view.py`** (Continued)

*   **File Path:** `app/ui/views/reports_view.py`
*   **Purpose & Goals:** Provides the UI for generating and displaying various business reports (Sales Summary, Inventory Valuation, GST Form 5). It also offers export options.
*   **Interfaces:** `ReportsView(core: ApplicationCore)`.
*   **Interactions:** Calls `reporting_manager.generate_sales_summary_report`, `inventory_manager.generate_inventory_valuation_report`, `gst_manager.generate_gst_f5_report` via `async_worker.run_task()`. Uses `reportlab` and `openpyxl` for export (these are separate utility functions, not directly part of the view logic).
*   **Code Skeleton:**
    ```python
    # File: app/ui/views/reports_view.py
    """The main view for generating and displaying reports."""
    from __future__ import annotations
    from typing import List, Any, Optional
    from datetime import date, datetime, timedelta # Import datetime and timedelta
    from decimal import Decimal

    from PySide6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QComboBox,
        QPushButton, QDateEdit, QTableWidget, QTableWidgetItem, QLabel,
        QHeaderView, QSizePolicy, QMessageBox, QScrollArea, QFileDialog # Import QFileDialog for export
    )
    from PySide6.QtCore import Slot, QDate, QAbstractTableModel, QModelIndex, Qt, QObject, QPoint # Import QPoint
    from PySide6.QtGui import QDesktopServices # For opening exported files

    from app.core.application_core import ApplicationCore
    from app.core.result import Success, Failure
    from app.business_logic.dto.reporting_dto import (
        SalesSummaryReportDTO, GstReportDTO, InventoryValuationReportDTO,
        SalesByPeriodDTO, ProductPerformanceDTO, InventoryValuationItemDTO
    )
    from app.core.async_bridge import AsyncWorker
    # TODO: Import report generation utilities (e.g., pdf_exporter, excel_exporter) for export functions
    # from app.utils.report_exporters import export_sales_summary_pdf, export_sales_summary_csv # Example


    # --- Reusable Table Models for Reports (already defined, copied for completeness) ---
    class SalesByPeriodTableModel(QAbstractTableModel):
        HEADERS = ["Date", "Total Sales (S$)", "Transactions", "Avg. Tx Value (S$)"]
        def __init__(self, data: List[SalesByPeriodDTO], parent: Optional[QObject] = None):
            super().__init__(parent)
            self._data = data
        def rowCount(self, parent: QModelIndex = QModelIndex()) -> int: return len(self._data)
        def columnCount(self, parent: QModelIndex = QModelIndex()) -> int: return len(self.HEADERS)
        def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
            if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal: return self.HEADERS[section]
            return None
        def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
            if not index.isValid(): return None
            item = self._data[index.row()]
            col = index.column()
            if role == Qt.ItemDataRole.DisplayRole:
                if col == 0: return item.period.strftime("%Y-%m-%d")
                if col == 1: return f"{item.total_sales:.2f}"
                if col == 2: return str(item.transaction_count)
                if col == 3: return f"{item.average_transaction_value:.2f}"
            if role == Qt.ItemDataRole.TextAlignmentRole and col in [1,2,3]: return Qt.AlignRight | Qt.AlignVCenter
            return None
        def refresh_data(self, new_data: List[SalesByPeriodDTO]): self.beginResetModel(); self._data = new_data; self.endResetModel()

    class ProductPerformanceTableModel(QAbstractTableModel):
        HEADERS = ["SKU", "Product Name", "Qty Sold", "Revenue (S$)", "Margin (S$)", "Margin (%)"]
        def __init__(self, data: List[ProductPerformanceDTO], parent: Optional[QObject] = None):
            super().__init__(parent)
            self._data = data
        def rowCount(self, parent: QModelIndex = QModelIndex()) -> int: return len(self._data)
        def columnCount(self, parent: QModelIndex = QModelIndex()) -> int: return len(self.HEADERS)
        def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
            if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal: return self.HEADERS[section]
            return None
        def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
            if not index.isValid(): return None
            item = self._data[index.row()]
            col = index.column()
            if role == Qt.ItemDataRole.DisplayRole:
                if col == 0: return item.sku
                if col == 1: return item.name
                if col == 2: return str(item.quantity_sold)
                if col == 3: return f"{item.total_revenue:.2f}"
                if col == 4: return f"{item.gross_margin:.2f}"
                if col == 5: return f"{item.gross_margin_percentage:.2f}%"
            if role == Qt.ItemDataRole.TextAlignmentRole and col in [2,3,4,5]: return Qt.AlignRight | Qt.AlignVCenter
            return None
        def refresh_data(self, new_data: List[ProductPerformanceDTO]): self.beginResetModel(); self._data = new_data; self.endResetModel()

    class InventoryValuationTableModel(QAbstractTableModel):
        HEADERS = ["SKU", "Product Name", "Qty On Hand", "Cost Price (S$)", "Total Value (S$)"]
        def __init__(self, data: List[InventoryValuationItemDTO], parent: Optional[QObject] = None):
            super().__init__(parent)
            self._data = data
        def rowCount(self, parent: QModelIndex = QModelIndex()) -> int: return len(self._data)
        def columnCount(self, parent: QModelIndex = QModelIndex()) -> int: return len(self.HEADERS)
        def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
            if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal: return self.HEADERS[section]
            return None
        def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
            if not index.isValid(): return None
            item = self._data[index.row()]
            col = index.column()
            if role == Qt.ItemDataRole.DisplayRole:
                if col == 0: return item.sku
                if col == 1: return item.name
                if col == 2: return str(item.quantity_on_hand)
                if col == 3: return f"{item.cost_price:.2f}"
                if col == 4: return f"{item.total_value:.2f}"
            if role == Qt.ItemDataRole.TextAlignmentRole and col in [2,3,4]: return Qt.AlignRight | Qt.AlignVCenter
            return None
        def refresh_data(self, new_data: List[InventoryValuationItemDTO]): self.beginResetModel(); self._data = new_data; self.endResetModel()


    class ReportsView(QWidget):
        """UI for generating and viewing business reports."""

        def __init__(self, core: ApplicationCore, parent: Optional[QObject] = None):
            super().__init__(parent)
            self.core = core
            self.async_worker: AsyncWorker = core.async_worker
            self.company_id = self.core.current_company_id # From core context
            self.outlet_id = self.core.current_outlet_id # For inventory report filtering if needed

            self.current_report_data: Optional[Any] = None # Stores the last generated report DTO for export

            self._setup_ui()
            self._connect_signals()
            self._set_default_dates()

        def _setup_ui(self):
            """Build the user interface."""
            # --- Controls ---
            controls_layout = QHBoxLayout()
            self.report_selector = QComboBox()
            self.report_selector.addItems(["Sales Summary Report", "Inventory Valuation Report", "GST Form 5"])
            
            self.start_date_edit = QDateEdit()
            self.start_date_edit.setCalendarPopup(True)
            self.end_date_edit = QDateEdit()
            self.end_date_edit.setCalendarPopup(True)
            
            self.generate_button = QPushButton("Generate Report")
            self.export_pdf_button = QPushButton("Export PDF")
            self.export_csv_button = QPushButton("Export CSV")

            controls_layout.addWidget(QLabel("Report:"))
            controls_layout.addWidget(self.report_selector)
            controls_layout.addWidget(QLabel("From:"))
            controls_layout.addWidget(self.start_date_edit)
            controls_layout.addWidget(QLabel("To:"))
            controls_layout.addWidget(self.end_date_edit)
            controls_layout.addStretch()
            controls_layout.addWidget(self.generate_button)
            controls_layout.addWidget(self.export_pdf_button)
            controls_layout.addWidget(self.export_csv_button)

            # --- Display Area (using QScrollArea for flexibility) ---
            self.report_content_widget = QWidget()
            self.report_content_layout = QVBoxLayout(self.report_content_widget)
            self.report_content_layout.addWidget(QLabel("Select a report and date range, then click 'Generate Report'."))
            self.report_content_layout.addStretch() # Push content to top

            self.report_scroll_area = QScrollArea()
            self.report_scroll_area.setWidgetResizable(True)
            self.report_scroll_area.setWidget(self.report_content_widget)

            # --- Main Layout ---
            main_layout = QVBoxLayout(self)
            main_layout.addLayout(controls_layout)
            main_layout.addWidget(self.report_scroll_area) # Add scroll area
            self.setLayout(main_layout)
            self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        def _set_default_dates(self):
            """Sets default date ranges for reports (e.g., last month or current quarter)."""
            today = QDate.currentDate()
            # Default to last month
            self.end_date_edit.setDate(today)
            self.start_date_edit.setDate(today.addMonths(-1).day(1)) # First day of previous month

            # For GST, set to last quarter
            # current_month = today.month()
            # if current_month <= 3: # Q1 ends in March, use previous year Q4
            #     self.start_date_edit.setDate(QDate(today.year() - 1, 10, 1))
            #     self.end_date_edit.setDate(QDate(today.year() - 1, 12, 31))
            # elif current_month <= 6: # Q2 ends in June
            #     self.start_date_edit.setDate(QDate(today.year(), 4, 1))
            #     self.end_date_edit.setDate(QDate(today.year(), 6, 30))
            # elif current_month <= 9: # Q3 ends in Sept
            #     self.start_date_edit.setDate(QDate(today.year(), 7, 1))
            #     self.end_date_edit.setDate(QDate(today.year(), 9, 30))
            # else: # Q4 ends in Dec
            #     self.start_date_edit.setDate(QDate(today.year(), 10, 1))
            #     self.end_date_edit.setDate(QDate(today.year(), 12, 31))

        def _connect_signals(self):
            """Connects UI signals to slots."""
            self.generate_button.clicked.connect(self._on_generate_report_clicked)
            self.export_pdf_button.clicked.connect(self._on_export_pdf_clicked)
            self.export_csv_button.clicked.connect(self._on_export_csv_clicked)

        def _clear_display_area(self):
            """Helper to clear the previous report content."""
            while self.report_content_layout.count() > 0:
                item = self.report_content_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
                elif item.layout():
                    self._clear_layout(item.layout())
            self.report_content_layout.addStretch() # Add stretch back after clearing

        def _clear_layout(self, layout: QVBoxLayout | QHBoxLayout | QFormLayout):
            """Recursively clears a layout."""
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
                elif item.layout():
                    self._clear_layout(item.layout())


        @Slot()
        def _on_generate_report_clicked(self):
            """Generates the selected report asynchronously."""
            report_name = self.report_selector.currentText()
            start_date_py = self.start_date_edit.date().toPython()
            end_date_py = self.end_date_edit.date().toPython()
            
            if start_date_py > end_date_py:
                QMessageBox.warning(self, "Invalid Date Range", "Start date cannot be after end date.")
                return

            self._clear_display_area()
            self.generate_button.setEnabled(False) # Disable button during generation
            self.export_pdf_button.setEnabled(False) # Disable export until generated
            self.export_csv_button.setEnabled(False) # Disable export until generated
            self.report_content_layout.addWidget(QLabel("Generating report... Please wait."))


            def _on_done(result: Any, error: Optional[Exception]):
                self.generate_button.setEnabled(True)
                self._clear_display_area() # Clear "generating" message

                if error:
                    QMessageBox.critical(self, "Report Error", f"An error occurred during report generation: {error}")
                    self.report_content_layout.addWidget(QLabel(f"Error generating report: {error}"))
                    self.report_content_layout.addStretch()
                    self.current_report_data = None # Clear data on error
                elif isinstance(result, Success):
                    self.current_report_data = result.value # Store for export
                    self.report_content_layout.addWidget(QLabel(f"<h3>{report_name} ({start_date_py.strftime('%Y-%m-%d')} to {end_date_py.strftime('%Y-%m-%d')})</h3>"))
                    
                    if report_name == "Sales Summary Report":
                        self._display_sales_summary_report(self.current_report_data)
                    elif report_name == "Inventory Valuation Report":
                        self._display_inventory_valuation_report(self.current_report_data)
                    elif report_name == "GST Form 5":
                        self._display_gst_report(self.current_report_data)

                    self.report_content_layout.addStretch()
                    self.export_pdf_button.setEnabled(True) # Enable export buttons
                    self.export_csv_button.setEnabled(True)

                elif isinstance(result, Failure):
                    QMessageBox.warning(self, "Report Failed", f"Could not generate report: {result.error}")
                    self.report_content_layout.addWidget(QLabel(f"Failed to generate report: {result.error}"))
                    self.report_content_layout.addStretch()
                    self.current_report_data = None # Clear data on failure
                
            coro = None
            if report_name == "Sales Summary Report":
                coro = self.core.reporting_manager.generate_sales_summary_report(self.company_id, start_date_py, end_date_py)
            elif report_name == "Inventory Valuation Report":
                coro = self.core.reporting_manager.generate_inventory_valuation_report(self.company_id, self.outlet_id) # Can filter by outlet
            elif report_name == "GST Form 5":
                coro = self.core.gst_manager.generate_gst_f5_report(self.company_id, start_date_py, end_date_py)
            
            if coro:
                self.async_worker.run_task(coro, on_done_callback=_on_done)
            else:
                QMessageBox.warning(self, "Not Implemented", "Selected report type is not yet implemented.")
                self.generate_button.setEnabled(True)
                self.report_content_layout.addWidget(QLabel("Selected report type is not yet implemented."))
                self.report_content_layout.addStretch()
                self.current_report_data = None


        def _display_sales_summary_report(self, report_dto: SalesSummaryReportDTO):
            """Renders the Sales Summary Report DTO in the UI."""
            self.report_content_layout.addWidget(QLabel(f"<b>Overall Revenue: S${report_dto.total_revenue:.2f}</b>"))
            self.report_content_layout.addWidget(QLabel(f"<b>Total Transactions: {report_dto.total_transactions}</b>"))
            self.report_content_layout.addWidget(QLabel(f"Total Discount: S${report_dto.total_discount_amount:.2f}"))
            self.report_content_layout.addWidget(QLabel(f"Total GST Collected: S${report_dto.total_tax_collected:.2f}"))

            self.report_content_layout.addWidget(QLabel("<br><b>Sales by Period:</b>"))
            sales_by_period_table = QTableView()
            sales_by_period_table.setModel(SalesByPeriodTableModel(report_dto.sales_by_period))
            sales_by_period_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            self.report_content_layout.addWidget(sales_by_period_table)

            self.report_content_layout.addWidget(QLabel("<br><b>Top Performing Products:</b>"))
            product_performance_table = QTableView()
            product_performance_table.setModel(ProductPerformanceTableModel(report_dto.top_performing_products))
            product_performance_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            self.report_content_layout.addWidget(product_performance_table)

        
        def _display_inventory_valuation_report(self, report_dto: InventoryValuationReportDTO):
            """Renders the Inventory Valuation Report DTO in the UI."""
            self.report_content_layout.addWidget(QLabel(f"<b>Inventory Valuation as of {report_dto.as_of_date.strftime('%Y-%m-%d')} for {report_dto.outlet_name}</b>"))
            self.report_content_layout.addWidget(QLabel(f"<b>Total Inventory Value: S${report_dto.total_inventory_value:.2f}</b>"))
            self.report_content_layout.addWidget(QLabel(f"Total Distinct Items: {report_dto.total_item_count}"))

            self.report_content_layout.addWidget(QLabel("<br><b>Inventory Items:</b>"))
            inventory_table = QTableView()
            inventory_table.setModel(InventoryValuationTableModel(report_dto.items))
            inventory_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            self.report_content_layout.addWidget(inventory_table)


        def _display_gst_report(self, report_dto: GstReportDTO):
            """Renders the GST F5 report in the UI."""
            self.report_content_layout.addWidget(QLabel(f"<h3>IRAS GST Form 5 Summary</h3>"))
            self.report_content_layout.addWidget(QLabel(f"<b>Company:</b> {report_dto.company_name} (GST Reg No: {report_dto.company_gst_reg_no or 'N/A'})"))
            self.report_content_layout.addWidget(QLabel(f"<b>Period:</b> {report_dto.start_date.strftime('%Y-%m-%d')} to {report_dto.end_date.strftime('%Y-%m-%d')}"))
            self.report_content_layout.addWidget(QLabel("<hr>"))

            gst_form_layout = QFormLayout()
            # Sales (Output Tax)
            gst_form_layout.addRow("<b>Box 1: Standard-Rated Supplies (S$)</b>", QLabel(f"<b>{report_dto.box_1_standard_rated_supplies:.2f}</b>"))
            gst_form_layout.addRow("Box 2: Zero-Rated Supplies (S$)", QLabel(f"{report_dto.box_2_zero_rated_supplies:.2f}"))
            gst_form_layout.addRow("Box 3: Exempt Supplies (S$)", QLabel(f"{report_dto.box_3_exempt_supplies:.2f}"))
            gst_form_layout.addRow("<b>Box 4: Total Supplies (S$)</b>", QLabel(f"<b>{report_dto.box_4_total_supplies:.2f}</b>"))
            gst_form_layout.addRow("<b>Box 6: Output Tax Due (S$)</b>", QLabel(f"<b>{report_dto.box_6_output_tax_due:.2f}</b>"))

            gst_form_layout.addRow(QLabel("<br><b>Purchases (Input Tax)</b>"))
            gst_form_layout.addRow("<b>Box 5: Taxable Purchases (S$)</b>", QLabel(f"<b>{report_dto.box_5_taxable_purchases:.2f}</b>"))
            gst_form_layout.addRow("<b>Box 7: Input Tax Claimed (S$)</b>", QLabel(f"<b>{report_dto.box_7_input_tax_claimed:.2f}</b>"))

            # Adjustments (usually zero for simple POS)
            if report_dto.box_8_adjustments_output_tax != Decimal("0.00"):
                gst_form_layout.addRow("Box 8: Adjustments to Output Tax (S$)", QLabel(f"{report_dto.box_8_adjustments_output_tax:.2f}"))
            if report_dto.box_9_adjustments_input_tax != Decimal("0.00"):
                gst_form_layout.addRow("Box 9: Adjustments to Input Tax (S$)", QLabel(f"{report_dto.box_9_adjustments_input_tax:.2f}"))

            self.report_content_layout.addLayout(gst_form_layout)
            self.report_content_layout.addWidget(QLabel("<hr>"))
            
            # Net GST
            self.report_content_layout.addWidget(QLabel(f"<b>Box 13: Net GST Payable / Reclaimable (S$)</b>"))
            net_gst_label = QLabel(f"<b><span style='font-size: 24px;'>S${report_dto.box_13_net_gst_payable:.2f}</span></b>")
            if report_dto.box_13_net_gst_payable < 0:
                net_gst_label.setStyleSheet("color: green;") # Reclaimable
            elif report_dto.box_13_net_gst_payable > 0:
                net_gst_label.setStyleSheet("color: red;") # Payable
            self.report_content_layout.addWidget(net_gst_label, alignment=Qt.AlignmentFlag.AlignRight)


        @Slot()
        def _on_export_pdf_clicked(self):
            """Exports the currently displayed report to PDF."""
            if not self.current_report_data:
                QMessageBox.warning(self, "No Report", "Please generate a report first.")
                return

            file_name, _ = QFileDialog.getSaveFileName(self, "Save Report as PDF",
                                                    f"{self.report_selector.currentText().replace(' ', '_')}_{self.current_report_data.start_date.isoformat()}_{self.current_report_data.end_date.isoformat()}.pdf",
                                                    "PDF Files (*.pdf)")
            if file_name:
                try:
                    # TODO: Call a separate utility function for PDF export
                    # Example: export_sales_summary_pdf(self.current_report_data, file_name)
                    QMessageBox.information(self, "Export Successful", f"Report exported to:\n{file_name}")
                    QDesktopServices.openUrl(QUrl.fromLocalFile(file_name)) # Open the file

                except Exception as e:
                    QMessageBox.critical(self, "Export Error", f"Failed to export report to PDF: {e}")


        @Slot()
        def _on_export_csv_clicked(self):
            """Exports the currently displayed report to CSV."""
            if not self.current_report_data:
                QMessageBox.warning(self, "No Report", "Please generate a report first.")
                return

            file_name, _ = QFileDialog.getSaveFileName(self, "Save Report as CSV",
                                                    f"{self.report_selector.currentText().replace(' ', '_')}_{self.current_report_data.start_date.isoformat()}_{self.current_report_data.end_date.isoformat()}.csv",
                                                    "CSV Files (*.csv)")
            if file_name:
                try:
                    # TODO: Call a separate utility function for CSV export
                    # Example: export_inventory_valuation_csv(self.current_report_data, file_name)
                    QMessageBox.information(self, "Export Successful", f"Report exported to:\n{file_name}")
                    QDesktopServices.openUrl(QUrl.fromLocalFile(file_name)) # Open the file
                except Exception as e:
                    QMessageBox.critical(self, "Export Error", f"Failed to export report to CSV: {e}")
    ```
*   **Acceptance Checklist:**
    *   [ ] `ReportsView` inherits `QWidget`.
    *   [ ] `SalesByPeriodTableModel`, `ProductPerformanceTableModel`, `InventoryValuationTableModel` are implemented as `QAbstractTableModel`s for displaying report data tables.
    *   [ ] UI elements (report selector, date edits, generate/export buttons, scrollable display area) are created.
    *   [ ] `_connect_signals` connects buttons to their slots.
    *   [ ] `_set_default_dates` sets sensible default date ranges.
    *   [ ] `_on_generate_report_clicked` calls `reporting_manager` or `gst_manager` via `async_worker.run_task()` based on selection.
    *   [ ] `_on_generate_report_clicked` handles `Result` objects, displays `QMessageBox` feedback, and stores `current_report_data`.
    *   [ ] `_display_sales_summary_report`, `_display_inventory_valuation_report`, `_display_gst_report` methods dynamically render the report DTOs in the `report_content_layout` using labels and table views.
    *   [ ] `_display_gst_report` correctly formats and displays all IRAS Form 5 boxes.
    *   [ ] `_on_export_pdf_clicked` and `_on_export_csv_clicked` open `QFileDialog` and serve as placeholders for calling actual export utility functions. They open the exported file on success.
    *   [ ] Export buttons are disabled until a report is generated.
    *   [ ] Type hinting is complete.

#### **2. `app/ui/views/settings_view.py`**

*   **File Path:** `app/ui/views/settings_view.py`
*   **Purpose & Goals:** Provides the UI for administrators to configure application settings, company information, user management, and roles/permissions.
*   **Interfaces:** `SettingsView(core: ApplicationCore)`.
*   **Interactions:** Will interact with various managers (e.g., `company_manager`, `user_manager`, `payment_method_manager`) to load and save settings via `async_worker.run_task()`.
*   **Code Skeleton:**
    ```python
    # File: app/ui/views/settings_view.py
    """A view for managing application and company settings."""
    from __future__ import annotations
    from typing import Optional, Any, List
    import uuid

    from PySide6.QtWidgets import (
        QWidget, QVBoxLayout, QTabWidget, QFormLayout,
        QLineEdit, QPushButton, QGroupBox, QMessageBox,
        QTableView, QHBoxLayout, QHeaderView, QCheckBox, QComboBox
    )
    from PySide6.QtCore import Slot, Signal, QAbstractTableModel, QModelIndex, Qt, QObject

    from app.core.application_core import ApplicationCore
    from app.core.result import Success, Failure
    from app.business_logic.dto.company_dto import CompanyDTO, OutletDTO # Assuming these DTOs exist
    from app.business_logic.dto.user_dto import UserDTO, UserCreateDTO, UserUpdateDTO # Assuming these DTOs exist
    from app.models.payment import PaymentMethod # For Payment Methods tab
    from app.core.async_bridge import AsyncWorker

    # --- Table Model for Users ---
    class UserTableModel(QAbstractTableModel):
        HEADERS = ["Username", "Full Name", "Email", "Role", "Active"]
        def __init__(self, users: List[UserDTO], parent: Optional[QObject] = None):
            super().__init__(parent)
            self._users = users
        def rowCount(self, parent: QModelIndex = QModelIndex()) -> int: return len(self._users)
        def columnCount(self, parent: QModelIndex = QModelIndex()) -> int: return len(self.HEADERS)
        def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
            if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal: return self.HEADERS[section]
            return None
        def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
            if not index.isValid(): return None
            user = self._users[index.row()]
            col = index.column()
            if role == Qt.ItemDataRole.DisplayRole:
                if col == 0: return user.username
                if col == 1: return user.full_name or "N/A"
                if col == 2: return user.email
                if col == 3: return user.role.capitalize()
                if col == 4: return "Yes" if user.is_active else "No"
            if role == Qt.ItemDataRole.TextAlignmentRole and col == 4: return Qt.AlignCenter | Qt.AlignVCenter
            return None
        def get_user_at_row(self, row: int) -> Optional[UserDTO]:
            if 0 <= row < len(self._users): return self._users[row]
            return None
        def refresh_data(self, new_users: List[UserDTO]): self.beginResetModel(); self._users = new_users; self.endResetModel()

    # --- User Dialog (for creating/editing users) ---
    class UserDialog(QDialog):
        user_operation_completed = Signal(bool, str)
        def __init__(self, core: ApplicationCore, user: Optional[UserDTO] = None, parent: Optional[QObject] = None):
            super().__init__(parent)
            self.core = core
            self.async_worker = core.async_worker
            self.user = user
            self.is_edit_mode = user is not None
            self.setWindowTitle("Edit User" if self.is_edit_mode else "Add New User")
            self.setMinimumWidth(400)

            self._setup_ui()
            self._connect_signals()
            if self.is_edit_mode: self._populate_form()

        def _setup_ui(self):
            self.username_input = QLineEdit()
            self.fullname_input = QLineEdit()
            self.email_input = QLineEdit()
            self.password_input = QLineEdit()
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.role_combo = QComboBox()
            self.role_combo.addItems(["cashier", "manager", "admin"]) # Roles from models/user.py
            self.is_active_checkbox = QCheckBox("Is Active")

            form_layout = QFormLayout()
            form_layout.addRow("Username:", self.username_input)
            form_layout.addRow("Full Name:", self.fullname_input)
            form_layout.addRow("Email:", self.email_input)
            form_layout.addRow("Password:", self.password_input)
            form_layout.addRow("Role:", self.role_combo)
            form_layout.addRow(self.is_active_checkbox)

            self.button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
            self.button_box.button(QDialogButtonBox.Save).setText("Save User")
            
            main_layout = QVBoxLayout(self)
            main_layout.addLayout(form_layout)
            main_layout.addWidget(self.button_box)

            if not self.is_edit_mode: self.is_active_checkbox.setChecked(True)

        def _connect_signals(self):
            self.button_box.accepted.connect(self._on_save_accepted)
            self.button_box.rejected.connect(self.reject)

        def _populate_form(self):
            if self.user:
                self.username_input.setText(self.user.username)
                self.fullname_input.setText(self.user.full_name or "")
                self.email_input.setText(self.user.email)
                self.role_combo.setCurrentText(self.user.role)
                self.is_active_checkbox.setChecked(self.user.is_active)
                self.password_input.setPlaceholderText("Leave blank to keep current password")

        def _get_dto(self) -> Union[UserCreateDTO, UserUpdateDTO]:
            common_data = {
                "username": self.username_input.text().strip(),
                "full_name": self.fullname_input.text().strip() or None,
                "email": self.email_input.text().strip(),
                "role": self.role_combo.currentText(),
                "is_active": self.is_active_checkbox.isChecked(),
            }
            if self.is_edit_mode:
                return UserUpdateDTO(password=self.password_input.text().strip() or None, **common_data)
            else:
                return UserCreateDTO(password=self.password_input.text().strip(), **common_data)

        @Slot()
        def _on_save_accepted(self):
            dto = self._get_dto()
            company_id = self.core.current_company_id

            try:
                if self.is_edit_mode:
                    coro = self.core.user_manager.update_user(self.user.id, dto)
                    success_msg = f"User '{dto.username}' updated successfully!"
                    error_prefix = "Failed to update user:"
                else:
                    coro = self.core.user_manager.create_user(company_id, dto)
                    success_msg = f"User '{dto.username}' created successfully!"
                    error_prefix = "Failed to create user:"

                self.button_box.button(QDialogButtonBox.Save).setEnabled(False)
                
                def _on_done(result: Any, error: Optional[Exception]):
                    self.button_box.button(QDialogButtonBox.Save).setEnabled(True)
                    if error:
                        QMessageBox.critical(self, "Error", f"{error_prefix}\n{error}")
                        self.user_operation_completed.emit(False, str(error))
                    elif isinstance(result, Success):
                        QMessageBox.information(self, "Success", success_msg)
                        self.user_operation_completed.emit(True, success_msg)
                        self.accept()
                    elif isinstance(result, Failure):
                        QMessageBox.warning(self, "Validation Error", f"{error_prefix}\n{result.error}")
                        self.user_operation_completed.emit(False, result.error)
                    else:
                        QMessageBox.critical(self, "Internal Error", f"Unexpected result type from manager: {type(result)}")
                        self.user_operation_completed.emit(False, "An unexpected internal error occurred.")

                self.async_worker.run_task(coro, on_done_callback=_on_done)

            except Exception as e:
                QMessageBox.critical(self, "Application Error", f"An internal error prevented the operation:\n{e}")
                self.user_operation_completed.emit(False, f"Internal error: {e}")
                self.button_box.button(QDialogButtonBox.Save).setEnabled(True)


    class SettingsView(QWidget):
        """UI for administrators to configure the system."""

        def __init__(self, core: ApplicationCore, parent: Optional[QObject] = None):
            super().__init__(parent)
            self.core = core
            self.async_worker: AsyncWorker = core.async_worker
            self.company_id = self.core.current_company_id

            self._setup_ui()
            self._connect_signals()
            self._load_company_info() # Load initial company info
            self._load_users() # Load initial user list


        def _setup_ui(self):
            """Build the user interface with tabs for different settings categories."""
            self.tab_widget = QTabWidget()
            
            # --- Company Information Tab ---
            self.company_tab = QWidget()
            company_layout = QFormLayout(self.company_tab)
            self.company_name_input = QLineEdit()
            self.company_reg_no_input = QLineEdit()
            self.company_gst_no_input = QLineEdit()
            self.company_address_input = QLineEdit()
            self.company_phone_input = QLineEdit()
            self.company_email_input = QLineEdit()
            self.company_save_button = QPushButton("Save Company Information")

            company_layout.addRow("Company Name:", self.company_name_input)
            company_layout.addRow("Registration No.:", self.company_reg_no_input)
            company_layout.addRow("GST Reg. No.:", self.company_gst_no_input)
            company_layout.addRow("Address:", self.company_address_input)
            company_layout.addRow("Phone:", self.company_phone_input)
            company_layout.addRow("Email:", self.company_email_input)
            company_layout.addWidget(self.company_save_button)
            self.tab_widget.addTab(self.company_tab, "Company Information")

            # --- User Management Tab ---
            self.users_tab = QWidget()
            users_layout = QVBoxLayout(self.users_tab)
            
            user_buttons_layout = QHBoxLayout()
            self.add_user_button = QPushButton("Add New User")
            self.edit_user_button = QPushButton("Edit Selected User")
            self.deactivate_user_button = QPushButton("Deactivate Selected User")
            user_buttons_layout.addStretch()
            user_buttons_layout.addWidget(self.add_user_button)
            user_buttons_layout.addWidget(self.edit_user_button)
            user_buttons_layout.addWidget(self.deactivate_user_button)

            self.user_table = QTableView()
            self.user_model = UserTableModel([])
            self.user_table.setModel(self.user_model)
            self.user_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            self.user_table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
            self.user_table.setSelectionMode(QTableView.SelectionMode.SingleSelection)
            self.user_table.doubleClicked.connect(self._on_edit_user)

            users_layout.addLayout(user_buttons_layout)
            users_layout.addWidget(self.user_table)
            self.tab_widget.addTab(self.users_tab, "User Management")

            # --- Payment Methods Tab ---
            self.payment_methods_tab = QWidget()
            payment_methods_layout = QVBoxLayout(self.payment_methods_tab)
            # TODO: Implement UI for adding/editing payment methods
            payment_methods_layout.addWidget(QLabel("Payment Methods Configuration (Coming Soon)"))
            self.tab_widget.addTab(self.payment_methods_tab, "Payment Methods")

            # --- Main Layout ---
            main_layout = QVBoxLayout(self)
            main_layout.addWidget(self.tab_widget)
            self.setLayout(main_layout)
            self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)


        def _connect_signals(self):
            """Connects UI signals to slots."""
            # Company Info Tab
            self.company_save_button.clicked.connect(self._on_save_company_info)

            # User Management Tab
            self.add_user_button.clicked.connect(self._on_add_user)
            self.edit_user_button.clicked.connect(self._on_edit_user)
            self.deactivate_user_button.clicked.connect(self._on_deactivate_user)


        @Slot()
        def _load_company_info(self):
            """Loads company information asynchronously."""
            def _on_done(result: Any, error: Optional[Exception]):
                if error:
                    QMessageBox.critical(self, "Load Error", f"Failed to load company info: {error}")
                    self.company_save_button.setEnabled(False) # Disable save if cannot load
                elif isinstance(result, Success) and result.value:
                    company_dto: CompanyDTO = result.value
                    self.company_name_input.setText(company_dto.name)
                    self.company_reg_no_input.setText(company_dto.registration_number)
                    self.company_gst_no_input.setText(company_dto.gst_registration_number or "")
                    self.company_address_input.setText(company_dto.address or "")
                    self.company_phone_input.setText(company_dto.phone or "")
                    self.company_email_input.setText(company_dto.email or "")
                elif isinstance(result, Failure):
                    QMessageBox.warning(self, "Load Failed", f"Could not load company info: {result.error}")
                    # If no company info found, enable create for initial setup
                else: # No company found, might be first run
                    QMessageBox.information(self, "Setup", "No company information found. Please fill in and save.")
            
            # Assuming current_company_id is set up from .env or initial login
            coro = self.core.company_manager.get_company(self.company_id) # Need company_manager and get_company
            self.async_worker.run_task(coro, on_done_callback=_on_done)


        @Slot()
        def _on_save_company_info(self):
            """Saves/updates company information."""
            # This requires a CompanyUpdateDTO and a method on CompanyManager
            # For simplicity, assuming it's an update operation on the existing company ID.
            QMessageBox.information(self, "Save Company Info", "Save Company Info functionality is not yet implemented.")
            # TODO: Implement saving company info


        @Slot()
        def _load_users(self):
            """Loads user list asynchronously."""
            def _on_done(result: Any, error: Optional[Exception]):
                if error:
                    QMessageBox.critical(self, "Load Error", f"Failed to load users: {error}")
                elif isinstance(result, Success):
                    self.user_model.refresh_data(result.value)
                elif isinstance(result, Failure):
                    QMessageBox.warning(self, "Load Failed", f"Could not load users: {result.error}")
            
            coro = self.core.user_manager.get_all_users(self.company_id) # Need user_manager and get_all_users
            self.async_worker.run_task(coro, on_done_callback=_on_done)


        @Slot()
        def _on_add_user(self):
            """Opens dialog to add a new user."""
            dialog = UserDialog(self.core, parent=self)
            dialog.user_operation_completed.connect(self._handle_user_dialog_result)
            dialog.exec()


        @Slot()
        def _on_edit_user(self):
            """Opens dialog to edit selected user."""
            selected_user = self.user_model.get_user_at_row(self.user_table.currentIndex().row())
            if not selected_user:
                QMessageBox.information(self, "No Selection", "Please select a user to edit.")
                return
            dialog = UserDialog(self.core, user=selected_user, parent=self)
            dialog.user_operation_completed.connect(self._handle_user_dialog_result)
            dialog.exec()


        @Slot()
        def _on_deactivate_user(self):
            """Deactivates selected user."""
            selected_user = self.user_model.get_user_at_row(self.user_table.currentIndex().row())
            if not selected_user:
                QMessageBox.information(self, "No Selection", "Please select a user to deactivate.")
                return
            
            if selected_user.id == self.core.current_user_id: # Prevent deactivating self
                QMessageBox.warning(self, "Action Denied", "You cannot deactivate your own user account.")
                return

            reply = QMessageBox.question(self, "Confirm Deactivation",
                                        f"Are you sure you want to deactivate user '{selected_user.username}'?",
                                        QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.No: return

            def _on_done(result: Any, error: Optional[Exception]):
                if error:
                    QMessageBox.critical(self, "Error", f"Failed to deactivate user: {error}")
                elif isinstance(result, Success) and result.value:
                    QMessageBox.information(self, "Success", f"User '{selected_user.username}' deactivated.")
                    self._load_users()
                elif isinstance(result, Failure):
                    QMessageBox.warning(self, "Deactivation Failed", f"Could not deactivate user: {result.error}")
                else:
                    QMessageBox.warning(self, "Deactivation Failed", "User not found or unknown error.")
            
            coro = self.core.user_manager.deactivate_user(selected_user.id) # Need deactivate_user
            self.async_worker.run_task(coro, on_done_callback=_on_done)


        @Slot(bool, str)
        def _handle_user_dialog_result(self, success: bool, message: str):
            """Slot to handle results from UserDialog and refresh the user list."""
            if success:
                self._load_users()

    ```
*   **Acceptance Checklist:**
    *   [ ] `SettingsView` inherits `QWidget`.
    *   [ ] `QTabWidget` is used to organize tabs for "Company Information", "User Management", and "Payment Methods".
    *   [ ] "Company Information" tab has input fields for company details and a "Save" button.
    *   [ ] `_load_company_info` calls `company_manager.get_company` via `async_worker.run_task()` and populates fields.
    *   [ ] `_on_save_company_info` is a placeholder for saving company info.
    *   [ ] "User Management" tab has "Add", "Edit", "Deactivate" buttons and a `QTableView`.
    *   [ ] `UserTableModel` (inheriting `QAbstractTableModel`) is implemented to display `UserDTO` data.
    *   [ ] `_load_users` calls `user_manager.get_all_users` via `async_worker.run_task()` and populates the table.
    *   [ ] `_on_add_user` and `_on_edit_user` launch `UserDialog`.
    *   [ ] `_on_deactivate_user` calls `user_manager.deactivate_user` with confirmation and prevents self-deactivation.
    *   [ ] `UserDialog` (as an inner class or separate file) is implemented for user CRUD, using `user_manager` via `async_worker.run_task()`.
    *   [ ] `_handle_user_dialog_result` refreshes user list.
    *   [ ] "Payment Methods" tab is a placeholder.
    *   [ ] All async calls include `on_done_callback` for `QMessageBox` feedback.
    *   [ ] Type hinting is complete.

### **Phase 5.5: Updates to Existing Files for Stage 5**

#### **1. `app/ui/main_window.py`** (Modified from Stage 4)

*   **File Path:** `app/ui/main_window.py`
*   **Purpose & Goals:** To integrate the new `ReportsView` and `SettingsView` into the main application window and add navigation options to the menu bar.
*   **Interactions:** Instantiates `ReportsView` and `SettingsView`, adds them to `QStackedWidget`, and creates menu actions.
*   **Code Skeleton:**
    ```python
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
        QStackedWidget, QMenuBar, QMenu, QMessageBox, QApplication # Import QApplication
    )
    from PySide6.QtCore import Slot, QEvent, QObject, QMetaObject, Qt, QGenericArgument as Q_ARG # Import QGenericArgument

    from app.core.application_core import ApplicationCore
    from app.core.async_bridge import AsyncWorker
    from app.core.exceptions import CoreException

    # Import all views that will be hosted
    from app.ui.views.product_view import ProductView
    from app.ui.views.customer_view import CustomerView
    from app.ui.views.pos_view import POSView
    from app.ui.views.inventory_view import InventoryView
    from app.ui.views.reports_view import ReportsView # NEW: Import ReportsView
    from app.ui.views.settings_view import SettingsView # NEW: Import SettingsView


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
            self.product_view = ProductView(self.core)
            self.customer_view = CustomerView(self.core)
            self.pos_view = POSView(self.core)
            self.inventory_view = InventoryView(self.core)
            self.reports_view = ReportsView(self.core) # NEW: Initialize ReportsView
            self.settings_view = SettingsView(self.core) # NEW: Initialize SettingsView

            # Add views to the stack
            self.stacked_widget.addWidget(self.pos_view)
            self.stacked_widget.addWidget(self.product_view)
            self.stacked_widget.addWidget(self.customer_view)
            self.stacked_widget.addWidget(self.inventory_view)
            self.stacked_widget.addWidget(self.reports_view) # NEW: Add ReportsView
            self.stacked_widget.addWidget(self.settings_view) # NEW: Add SettingsView
            
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

            # Inventory Menu
            inventory_menu = menu_bar.addMenu("&Inventory")
            inventory_action = inventory_menu.addAction("Stock Management")
            inventory_action.triggered.connect(lambda: self.stacked_widget.setCurrentWidget(self.inventory_view))

            # Reports Menu (Populated in Stage 5)
            reports_menu = menu_bar.addMenu("&Reports") # NEW
            reports_action = reports_menu.addAction("Business Reports") # NEW
            reports_action.triggered.connect(lambda: self.stacked_widget.setCurrentWidget(self.reports_view)) # NEW

            # Settings Menu (Populated in Stage 5)
            settings_menu = menu_bar.addMenu("&Settings") # NEW
            settings_action = settings_menu.addAction("Application Settings") # NEW
            settings_action.triggered.connect(lambda: self.stacked_widget.setCurrentWidget(self.settings_view)) # NEW


        @Slot(object, object)
        def _handle_async_task_result(self, result: Any, error: Optional[Exception]):
            """
            Global handler for results/errors from async tasks that didn't have
            a specific `on_done_callback`. This can be used for general error reporting.
            Individual UI components should still use specific callbacks where needed.
            """
            if error:
                print(f"Unhandled async error: {error}", file=sys.stderr)
                # TODO: Implement more sophisticated global error logging/display
                # QMessageBox.critical(self, "Error", f"An unexpected background error occurred: {error}")

        def closeEvent(self, event: QEvent) -> None:
            """
            Handle window close event to gracefully shut down the application core.
            This ensures database connections and async threads are properly terminated.
            """
            print("Main window closing. Initiating ApplicationCore shutdown...")
            
            async def shutdown_task():
                try:
                    await self.core.shutdown()
                    print("ApplicationCore shutdown complete.")
                except Exception as e:
                    print(f"Error during ApplicationCore shutdown: {e}", file=sys.stderr)
                    QMetaObject.invokeMethod(self, "show_shutdown_error",
                                            Qt.ConnectionType.QueuedConnection,
                                            Q_ARG(str, str(e)))
                QMetaObject.invokeMethod(self, "accept_close_event",
                                         Qt.ConnectionType.QueuedConnection)

            self.async_worker.run_task(shutdown_task())
            
            event.ignore()

        @Slot()
        def accept_close_event(self) -> None:
            """Slot to finally accept the close event after async shutdown completes."""
            QApplication.instance().quit()

        @Slot(str)
        def show_shutdown_error(self, error_message: str) -> None:
            """Displays a critical error message if shutdown fails."""
            QMessageBox.critical(self, "Shutdown Error", f"Failed to gracefully shut down application:\n{error_message}")
    ```
*   **Acceptance Checklist:**
    *   [ ] `ReportsView` and `SettingsView` are imported and instantiated.
    *   [ ] These views are added to the `stacked_widget`.
    *   [ ] "Reports" menu is created in the menu bar.
    *   [ ] "Business Reports" action is added to the "Reports" menu and correctly switches the `stacked_widget` to `reports_view`.
    *   [ ] "Settings" menu is created in the menu bar.
    *   [ ] "Application Settings" action is added to the "Settings" menu and correctly switches the `stacked_widget` to `settings_view`.

---

This completes the *entire* detailed execution plan for building the SG-POS system to be production-worthy. By meticulously following these steps, a developer, even with novice experience, can systematically build the application layer by layer, adhering to strict architectural principles, ensuring responsiveness, and addressing all critical quality concerns.

**Final Steps for the Developer after completing all stages:**

1.  **Comprehensive Testing:** Write extensive unit, integration, and end-to-end tests for all implemented modules, ensuring high test coverage. Use `pytest`, `pytest-qt`, `pytest-asyncio`.
2.  **Error Handling Refinement:** Enhance UI error feedback with more specific messages based on `Result.error` types. Implement robust logging using `structlog`.
3.  **Authentication & Authorization:** Fully implement user login, session management, and role-based access control throughout the application's business logic and UI.
4.  **External Integrations:** Implement actual API calls for payment gateways (e.g., Stripe, NETS), Peppol e-invoicing, and accounting system exports (e.g., Xero, QuickBooks).
5.  **UI Polish:** Refine UI/UX, apply QSS styling, implement custom widgets where beneficial (e.g., a better product search with live results, a comprehensive customer selection dialog).
6.  **Performance Optimization:** Profile and optimize critical paths, especially database queries and complex UI rendering.
7.  **Documentation:** Keep internal code documentation (docstrings) up-to-date and maintain external documentation (e.g., `docs/` folder, `CONTRIBUTING.md`).
8.  **CI/CD Pipeline:** Ensure the GitHub Actions CI/CD pipeline runs all tests, linting, and builds, blocking merges if checks fail.

This plan serves as a robust roadmap for transforming the architectural vision into a high-quality, functional, and maintainable software product.
```

---
https://drive.google.com/file/d/108RlhMVaufy_hYAq9aWl4fJT0Nc_LB2k/view?usp=sharing, https://drive.google.com/file/d/1DVVDdJPIYRsNjaL1TBK0pyivBT9T3KcR/view?usp=sharing, https://drive.google.com/file/d/1Dv92K22sZCR81fKux1KGaRKSj8Jv-Uyc/view?usp=sharing, https://aistudio.google.com/app/prompts?state=%7B%22ids%22:%5B%221HJO6Ey-cx-eWjXUJuYEitWEe9fWU1I7v%22%5D,%22action%22:%22open%22,%22userId%22:%22103961307342447084491%22,%22resourceKeys%22:%7B%7D%7D&usp=sharing, https://drive.google.com/file/d/1O8RKDf9T_KQwxh_rkPefDZVRvLlJpeOW/view?usp=sharing, https://drive.google.com/file/d/1SzHas3aRVlLw8XZ5_aNYK9dhML_2ea-b/view?usp=sharing, https://drive.google.com/file/d/1cshXJfKI6TJeVUZKw_xMxdF0Ly-V9Anu/view?usp=sharing, https://drive.google.com/file/d/1gTl2UasRWjqn51dY_Ouh_io0JM4zvxOj/view?usp=sharing, https://drive.google.com/file/d/1l2E0gN419jGB6-aopwZySbqPiKbZLfCf/view?usp=sharing, https://drive.google.com/file/d/1nrRKmVq24tyRexjTP6PcrDYAYdreLm4u/view?usp=sharing, https://drive.google.com/file/d/1wjCj8KX8Cs8MeVz0a4FWLB7hoeUhSJJe/view?usp=sharing, https://drive.google.com/file/d/1yf-0upWQE6xmB3LxWX6yCtOzUIRt-sDo/view?usp=sharing

