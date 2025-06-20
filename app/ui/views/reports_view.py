# File: app/ui/views/reports_view.py
"""The main view for generating and displaying reports."""
from __future__ import annotations
from typing import List, Any, Optional
from datetime import date, timedelta
from decimal import Decimal
import uuid
import os

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QComboBox,
    QPushButton, QDateEdit, QTableWidget, QTableWidgetItem, QLabel,
    QHeaderView, QSizePolicy, QMessageBox, QScrollArea, QFileDialog, QTableView
)
from PySide6.QtCore import Slot, QDate, QAbstractTableModel, QModelIndex, Qt, QObject, QUrl
from PySide6.QtGui import QDesktopServices

from app.core.application_core import ApplicationCore
from app.core.result import Success, Failure
from app.business_logic.dto.reporting_dto import (
    SalesSummaryReportDTO, GstReportDTO, InventoryValuationReportDTO,
    SalesByPeriodDTO, ProductPerformanceDTO, InventoryValuationItemDTO
)
from app.core.async_bridge import AsyncWorker

class SalesByPeriodTableModel(QAbstractTableModel):
    HEADERS = ["Date", "Total Sales (S$)", "Transactions", "Avg. Tx Value (S$)"]
    def __init__(self, data: List[SalesByPeriodDTO], parent: Optional[QObject] = None): super().__init__(parent); self._data = data
    def rowCount(self, p=QModelIndex()): return len(self._data)
    def columnCount(self, p=QModelIndex()): return len(self.HEADERS)
    def headerData(self, s, o, r=Qt.DisplayRole):
        if r == Qt.DisplayRole and o == Qt.Horizontal: return self.HEADERS[s]
    def data(self, i, r=Qt.DisplayRole):
        if not i.isValid(): return
        item = self._data[i.row()]
        col = i.column()
        if r == Qt.DisplayRole:
            if col == 0: return item.period.strftime("%Y-%m-%d")
            if col == 1: return f"{item.total_sales:.2f}"
            if col == 2: return str(item.transaction_count)
            if col == 3: return f"{item.average_transaction_value:.2f}"
        if r == Qt.TextAlignmentRole and col in [1,2,3]: return Qt.AlignRight | Qt.AlignVCenter

class ProductPerformanceTableModel(QAbstractTableModel):
    HEADERS = ["SKU", "Product Name", "Qty Sold", "Revenue (S$)", "Margin (S$)", "Margin (%)"]
    def __init__(self, data: List[ProductPerformanceDTO], parent: Optional[QObject] = None): super().__init__(parent); self._data = data
    def rowCount(self, p=QModelIndex()): return len(self._data)
    def columnCount(self, p=QModelIndex()): return len(self.HEADERS)
    def headerData(self, s, o, r=Qt.DisplayRole):
        if r == Qt.DisplayRole and o == Qt.Horizontal: return self.HEADERS[s]
    def data(self, i, r=Qt.DisplayRole):
        if not i.isValid(): return
        item = self._data[i.row()]
        col = i.column()
        if r == Qt.DisplayRole:
            if col == 0: return item.sku
            if col == 1: return item.name
            if col == 2: return f"{item.quantity_sold:.4f}"
            if col == 3: return f"{item.total_revenue:.2f}"
            if col == 4: return f"{item.gross_margin:.2f}"
            if col == 5: return f"{item.gross_margin_percentage:.2f}%"
        if r == Qt.TextAlignmentRole and col in [2,3,4,5]: return Qt.AlignRight | Qt.AlignVCenter

class InventoryValuationTableModel(QAbstractTableModel):
    HEADERS = ["SKU", "Product Name", "Qty On Hand", "Cost Price (S$)", "Total Value (S$)"]
    def __init__(self, data: List[InventoryValuationItemDTO], parent: Optional[QObject] = None): super().__init__(parent); self._data = data
    def rowCount(self, p=QModelIndex()): return len(self._data)
    def columnCount(self, p=QModelIndex()): return len(self.HEADERS)
    def headerData(self, s, o, r=Qt.DisplayRole):
        if r == Qt.DisplayRole and o == Qt.Horizontal: return self.HEADERS[s]
    def data(self, i, r=Qt.DisplayRole):
        if not i.isValid(): return
        item = self._data[i.row()]
        col = i.column()
        if r == Qt.DisplayRole:
            if col == 0: return item.sku
            if col == 1: return item.name
            if col == 2: return f"{item.quantity_on_hand:.4f}"
            if col == 3: return f"{item.cost_price:.4f}"
            if col == 4: return f"{item.total_value:.2f}"
        if r == Qt.TextAlignmentRole and col in [2,3,4]: return Qt.AlignRight | Qt.AlignVCenter

class ReportsView(QWidget):
    """UI for generating and viewing business reports."""
    def __init__(self, core: ApplicationCore, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.core = core
        self.async_worker: AsyncWorker = core.async_worker
        self.company_id = self.core.current_company_id
        self.outlet_id = self.core.current_outlet_id
        self.current_report_data: Optional[Any] = None
        self._setup_ui()
        self._connect_signals()
        self._set_default_dates()

    def _setup_ui(self):
        controls_layout = QHBoxLayout()
        self.report_selector = QComboBox(); self.report_selector.addItems(["Sales Summary Report", "Inventory Valuation Report", "GST Form 5"])
        self.start_date_edit = QDateEdit(); self.start_date_edit.setCalendarPopup(True)
        self.end_date_edit = QDateEdit(); self.end_date_edit.setCalendarPopup(True)
        self.generate_button = QPushButton("Generate Report"); self.export_pdf_button = QPushButton("Export PDF"); self.export_csv_button = QPushButton("Export CSV")
        self.export_pdf_button.setEnabled(False)
        self.export_csv_button.setEnabled(False)
        controls_layout.addWidget(QLabel("Report:")); controls_layout.addWidget(self.report_selector); controls_layout.addWidget(QLabel("From:")); controls_layout.addWidget(self.start_date_edit)
        controls_layout.addWidget(QLabel("To:")); controls_layout.addWidget(self.end_date_edit); controls_layout.addStretch()
        controls_layout.addWidget(self.generate_button); controls_layout.addWidget(self.export_pdf_button); controls_layout.addWidget(self.export_csv_button)
        self.report_content_widget = QWidget(); self.report_content_layout = QVBoxLayout(self.report_content_widget)
        self.report_content_layout.addWidget(QLabel("Select a report and date range, then click 'Generate Report'.")); self.report_content_layout.addStretch()
        self.report_scroll_area = QScrollArea(); self.report_scroll_area.setWidgetResizable(True); self.report_scroll_area.setWidget(self.report_content_widget)
        main_layout = QVBoxLayout(self); main_layout.addLayout(controls_layout); main_layout.addWidget(self.report_scroll_area)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def _set_default_dates(self):
        today = QDate.currentDate(); self.end_date_edit.setDate(today); self.start_date_edit.setDate(today.addMonths(-1).addDays(1 - today.day()))

    def _connect_signals(self):
        self.generate_button.clicked.connect(self._on_generate_report_clicked)
        self.export_pdf_button.clicked.connect(self._on_export_pdf_clicked); self.export_csv_button.clicked.connect(self._on_export_csv_clicked)
        self.report_selector.currentIndexChanged.connect(lambda: self._set_export_buttons_enabled(False))

    def _set_export_buttons_enabled(self, enabled: bool):
        self.export_pdf_button.setEnabled(enabled)
        # GST report is complex and not suitable for a simple CSV table export
        is_gst_report = self.report_selector.currentText() == "GST Form 5"
        self.export_csv_button.setEnabled(enabled and not is_gst_report)

    def _clear_display_area(self):
        while self.report_content_layout.count():
            item = self.report_content_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self.report_content_layout.addStretch()

    @Slot()
    def _on_generate_report_clicked(self):
        report_name = self.report_selector.currentText(); start_date = self.start_date_edit.date().toPython(); end_date = self.end_date_edit.date().toPython()
        if start_date > end_date: QMessageBox.warning(self, "Invalid Date Range", "Start date cannot be after end date."); return
        self._clear_display_area(); self.generate_button.setEnabled(False); self._set_export_buttons_enabled(False)
        self.report_content_layout.addWidget(QLabel("Generating report... Please wait."))
        def _on_done(r, e):
            self.generate_button.setEnabled(True); self._clear_display_area()
            if e or isinstance(r, Failure):
                self.current_report_data = None
                QMessageBox.critical(self, "Report Error", f"An error occurred: {e or r.error}")
            elif isinstance(r, Success):
                self.current_report_data = r.value
                self.report_content_layout.addWidget(QLabel(f"<h3>{report_name} ({start_date.strftime('%d %b %Y')} to {end_date.strftime('%d %b %Y')})</h3>"))
                if report_name == "Sales Summary Report": self._display_sales_summary_report(r.value)
                elif report_name == "Inventory Valuation Report": self._display_inventory_valuation_report(r.value)
                elif report_name == "GST Form 5": self._display_gst_report(r.value)
                self.report_content_layout.addStretch(); self._set_export_buttons_enabled(True)
        coro = None
        if report_name == "Sales Summary Report": coro = self.core.reporting_manager.generate_sales_summary_report(self.company_id, start_date, end_date)
        elif report_name == "Inventory Valuation Report": coro = self.core.reporting_manager.generate_inventory_valuation_report(self.company_id, self.outlet_id)
        elif report_name == "GST Form 5": coro = self.core.gst_manager.generate_gst_f5_report(self.company_id, start_date, end_date)
        if coro: self.async_worker.run_task(coro, on_done_callback=_on_done)
        else: self.generate_button.setEnabled(True); self._clear_display_area(); self.current_report_data = None

    def _display_sales_summary_report(self, dto: SalesSummaryReportDTO):
        self.report_content_layout.addWidget(QLabel(f"<b>Overall Revenue: S${dto.total_revenue:.2f}</b> | <b>Total Transactions: {dto.total_transactions}</b>"))
        self.report_content_layout.addWidget(QLabel("<b>Sales by Period:</b>")); table = QTableView(); table.setModel(SalesByPeriodTableModel(dto.sales_by_period)); table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch); self.report_content_layout.addWidget(table)
        self.report_content_layout.addWidget(QLabel("<br><b>Top Performing Products:</b>")); table2 = QTableView(); table2.setModel(ProductPerformanceTableModel(dto.top_performing_products)); table2.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch); self.report_content_layout.addWidget(table2)

    def _display_inventory_valuation_report(self, dto: InventoryValuationReportDTO):
        self.report_content_layout.addWidget(QLabel(f"<b>Valuation for {dto.outlet_name} as of {dto.as_of_date.strftime('%d %b %Y')}</b>"))
        self.report_content_layout.addWidget(QLabel(f"<b>Total Inventory Value: S${dto.total_inventory_value:.2f}</b> | <b>Total Items: {dto.total_distinct_items}</b>"))
        table = QTableView(); table.setModel(InventoryValuationTableModel(dto.items)); table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch); self.report_content_layout.addWidget(table)

    def _display_gst_report(self, dto: GstReportDTO):
        html = f"""<h3>IRAS GST Form 5 Summary</h3>
                   <p><b>Company:</b> {dto.company_name} (GST Reg No: {dto.company_gst_reg_no or 'N/A'})</p>
                   <p><b>Period:</b> {dto.start_date.strftime('%d %b %Y')} to {dto.end_date.strftime('%d %b %Y')}</p><hr>
                   <table width='100%'>
                     <tr><td><b>Box 1: Standard-Rated Supplies</b></td><td align='right'>S${dto.box_1_standard_rated_supplies:.2f}</td></tr>
                     <tr><td>Box 2: Zero-Rated Supplies</td><td align='right'>S${dto.box_2_zero_rated_supplies:.2f}</td></tr>
                     <tr><td>Box 3: Exempt Supplies</td><td align='right'>S${dto.box_3_exempt_supplies:.2f}</td></tr>
                     <tr><td><b>Box 4: Total Supplies</b></td><td align='right'><b>S${dto.box_4_total_supplies:.2f}</b></td></tr>
                     <tr><td colspan=2><br></td></tr>
                     <tr><td><b>Box 6: Output Tax Due</b></td><td align='right'><b>S${dto.box_6_output_tax_due:.2f}</b></td></tr>
                     <tr><td colspan=2><br><b>Purchases (Input Tax)</b></td></tr>
                     <tr><td><b>Box 5: Taxable Purchases</b></td><td align='right'><b>S${dto.box_5_taxable_purchases:.2f}</b></td></tr>
                     <tr><td><b>Box 7: Input Tax Claimed</b></td><td align='right'><b>S${dto.box_7_input_tax_claimed:.2f}</b></td></tr>
                   </table><hr>
                   <p align='right'><b>Box 13: Net GST {'Payable' if dto.box_13_net_gst_payable >= 0 else 'Reclaimable'} (S$): 
                   <span style='font-size: 24px; color: {'red' if dto.box_13_net_gst_payable >= 0 else 'green'};'>
                   {abs(dto.box_13_net_gst_payable):.2f}</span></b></p>"""
        self.report_content_layout.addWidget(QLabel(html))

    def _get_save_path(self, file_type: str, extension: str) -> str:
        """Opens a QFileDialog to get a save path from the user."""
        report_name = self.report_selector.currentText().replace(" ", "_")
        default_filename = f"{report_name}_{date.today().strftime('%Y%m%d')}.{extension}"
        file_path, _ = QFileDialog.getSaveFileName(
            self, f"Save Report as {file_type}", os.path.join(os.path.expanduser("~"), default_filename), f"{file_type} Files (*.{extension})"
        )
        return file_path

    @Slot()
    def _on_export_pdf_clicked(self):
        if not self.current_report_data:
            QMessageBox.warning(self, "No Report", "Please generate a report first.")
            return
        
        file_path = self._get_save_path("PDF", "pdf")
        if file_path:
            self.export_pdf_button.setEnabled(False)
            def _on_done(result, error):
                self.export_pdf_button.setEnabled(True)
                if error or isinstance(result, Failure):
                    QMessageBox.critical(self, "Export Error", f"Failed to export PDF: {error or result.error}")
                else:
                    reply = QMessageBox.information(self, "Export Successful", f"Report saved to:\n{file_path}", QMessageBox.Ok | QMessageBox.Open)
                    if reply == QMessageBox.Open:
                        QDesktopServices.openUrl(QUrl.fromLocalFile(file_path))

            self.async_worker.run_task(self.core.reporting_manager.export_report_to_pdf(self.current_report_data, file_path), on_done_callback=_on_done)

    @Slot()
    def _on_export_csv_clicked(self):
        if not self.current_report_data:
            QMessageBox.warning(self, "No Report", "Please generate a report first.")
            return

        file_path = self._get_save_path("CSV", "csv")
        if file_path:
            self.export_csv_button.setEnabled(False)
            def _on_done(result, error):
                self.export_csv_button.setEnabled(True)
                if error or isinstance(result, Failure):
                    QMessageBox.critical(self, "Export Error", f"Failed to export CSV: {error or result.error}")
                else:
                    reply = QMessageBox.information(self, "Export Successful", f"Report saved to:\n{file_path}", QMessageBox.Ok | QMessageBox.Open)
                    if reply == QMessageBox.Open:
                        QDesktopServices.openUrl(QUrl.fromLocalFile(file_path))
            
            self.async_worker.run_task(self.core.reporting_manager.export_report_to_csv(self.current_report_data, file_path), on_done_callback=_on_done)
