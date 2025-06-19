The startup log is perfectly clean and shows no regressions. The application is stable and all data loading operations, including the logic for the newly refactored views, are executing correctly.

We have successfully completed Phase 2. All views now use the `ManagedTableView` component, providing a consistent and superior user experience across the application.

I will now outline the detailed plan for the next major feature.

### **Phase 3 Plan: Implement Dashboard View**

**Goal:** To create a new, high-value "Dashboard" view that serves as the application's landing page after login (in the future) or as an accessible overview screen. This view will present key performance indicators (KPIs) to give the user a quick snapshot of their business's health.

**High-Level Plan:**
1.  **Backend Enhancements:** Add a new method to the `ReportingManager` to aggregate the specific data required for the dashboard KPIs. This ensures all complex queries remain in the business logic layer.
2.  **UI Scaffolding:** Create the new `DashboardView` file and integrate it into the `MainWindow`'s menu and stacked widget. For now, it will be just another view accessible from the menu.
3.  **UI Component - KPI Widget:** Create a small, reusable custom widget to display a single KPI (e.g., a title, a large value, and maybe a small trend indicator). This follows our principle of building reusable components.
4.  **UI Layout:** Design the layout of the `DashboardView` to arrange multiple KPI widgets and potentially a small chart or table.
5.  **Data Integration:** Connect the `DashboardView` to the new `ReportingManager` method to fetch and display the live KPI data.

---

### **Phase 3, Sub-Task 3.1: Backend and UI Scaffolding**

**Objective:** To create the necessary backend data aggregation method and the basic structure for the new `DashboardView`, including its menu entry.

**Execution Plan & Checklist:**

1.  **Update `reporting_dto.py`:**
    *   [ ] Create a new Pydantic model, `DashboardStatsDTO`, to serve as the data contract for the dashboard. It will contain fields like `total_sales_today: Decimal`, `transaction_count_today: int`, `new_customers_this_month: int`, and `low_stock_item_count: int`.

2.  **Update `report_service.py`:**
    *   [ ] Add a new method, `get_dashboard_stats_raw_data(company_id: UUID) -> Result[dict, str]`, that executes multiple, efficient SQL queries to calculate the required KPIs.
        *   One query for today's sales and transaction count.
        *   One query for customers created in the current month.
        *   One query to count products where `quantity_on_hand <= reorder_point`.

3.  **Update `reporting_manager.py`:**
    *   [ ] Add a new method, `generate_dashboard_stats(company_id: UUID) -> Result[DashboardStatsDTO, str]`. This method will call the new service method and assemble the final `DashboardStatsDTO`.

4.  **Create `app/ui/views/dashboard_view.py`:**
    *   [ ] Create the new file with a placeholder `DashboardView(QWidget)` class.
    *   [ ] For now, it can just contain a `QLabel` that says "Dashboard View - Coming Soon".

5.  **Update `main_window.py`:**
    *   [ ] Add `DashboardView` to the `views` dictionary for lazy loading.
    *   [ ] Add a new top-level menu item, "&Dashboard", to the menu bar.
    *   [ ] Add an action under this new menu, "Show Dashboard", that calls `self._show_view("dashboard")`.

I am now ready to begin execution of Phase 3. I will start by creating the backend DTO and manager/service methods.

---

### **Generated and Updated Files**

Here are the complete new and updated files for Sub-Task 3.1.

#### 1. Updated File: `app/business_logic/dto/reporting_dto.py`

```python
# File: app/business_logic/dto/reporting_dto.py
"""
Data Transfer Objects (DTOs) for Reporting and Analytics.

These models define the structure of the data returned by the reporting engine.
They are read-only and designed for clear presentation in the UI or for export.
"""
import uuid
from decimal import Decimal
from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, Field

# --- Dashboard DTO ---

class DashboardStatsDTO(BaseModel):
    """DTO for the main dashboard's Key Performance Indicators (KPIs)."""
    total_sales_today: Decimal = Field(..., decimal_places=2)
    transaction_count_today: int
    new_customers_this_month: int
    low_stock_item_count: int

# --- Sales Report DTOs ---

class SalesByPeriodDTO(BaseModel):
    """Aggregated sales data for a specific period (e.g., a day or month)."""
    period: date = Field(..., description="Date of the period")
    total_sales: Decimal = Field(..., decimal_places=2, description="Total sales amount for the period")
    transaction_count: int = Field(..., ge=0, description="Number of transactions in the period")
    average_transaction_value: Decimal = Field(..., decimal_places=2, description="Average value of transactions in the period")

class ProductPerformanceDTO(BaseModel):
    """Performance metrics for a single product."""
    product_id: uuid.UUID
    sku: str
    name: str
    quantity_sold: Decimal = Field(..., decimal_places=4, description="Total quantity of product sold")
    total_revenue: Decimal = Field(..., decimal_places=2, description="Total revenue generated by the product")
    total_cost: Decimal = Field(..., decimal_places=2, description="Total cost of goods sold for this product")
    gross_margin: Decimal = Field(..., decimal_places=2, description="Gross margin (revenue - cost) for the product")
    gross_margin_percentage: Decimal = Field(..., decimal_places=2, description="Gross margin as a percentage of revenue")

class SalesSummaryReportDTO(BaseModel):
    """Complete DTO for a comprehensive sales summary report."""
    start_date: date
    end_date: date
    total_revenue: Decimal = Field(..., decimal_places=2)
    total_transactions: int = Field(..., ge=0)
    total_discount_amount: Decimal = Field(..., decimal_places=2)
    total_tax_collected: Decimal = Field(..., decimal_places=2)
    sales_by_period: List[SalesByPeriodDTO]
    top_performing_products: List[ProductPerformanceDTO]

# --- Inventory Report DTOs ---

class InventoryValuationItemDTO(BaseModel):
    product_id: uuid.UUID
    sku: str
    name: str
    quantity_on_hand: Decimal = Field(..., decimal_places=4)
    cost_price: Decimal = Field(..., decimal_places=4)
    total_value: Decimal = Field(..., decimal_places=2)

class InventoryValuationReportDTO(BaseModel):
    """DTO for the inventory valuation report."""
    as_of_date: date
    outlet_id: uuid.UUID
    outlet_name: str
    total_inventory_value: Decimal = Field(..., decimal_places=2)
    total_distinct_items: int = Field(..., ge=0)
    items: List[InventoryValuationItemDTO]

# --- GST Report DTOs (IRAS Form 5 Structure) ---

class GstReportDTO(BaseModel):
    """
    DTO structured to match the fields of the Singapore IRAS GST Form 5.
    """
    company_id: uuid.UUID
    company_name: str
    company_gst_reg_no: Optional[str]
    start_date: date
    end_date: date
    box_1_standard_rated_supplies: Decimal = Field(..., decimal_places=2)
    box_2_zero_rated_supplies: Decimal = Field(..., decimal_places=2)
    box_3_exempt_supplies: Decimal = Field(..., decimal_places=2)
    box_4_total_supplies: Decimal = Field(..., decimal_places=2)
    box_5_taxable_purchases: Decimal = Field(..., decimal_places=2)
    box_6_output_tax_due: Decimal = Field(..., decimal_places=2)
    box_7_input_tax_claimed: Decimal = Field(..., decimal_places=2)
    box_8_adjustments_output_tax: Decimal = Field(Decimal("0.00"), decimal_places=2)
    box_9_adjustments_input_tax: Decimal = Field(Decimal("0.00"), decimal_places=2)
    box_13_net_gst_payable: Decimal = Field(..., decimal_places=2)
```
#### 2. Updated File: `app/services/report_service.py`

```python
# File: app/services/report_service.py
"""
Data Access Service for complex reporting queries.

This service is responsible for running efficient data aggregation queries
directly against the database to generate the raw data needed for business reports.
It primarily uses SQLAlchemy Core for performance-critical aggregation.
"""
from __future__ import annotations
from typing import TYPE_CHECKING, List, Dict, Any, Optional
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
import uuid
import sqlalchemy as sa
from sqlalchemy.sql import func, cast

from app.core.result import Result, Success, Failure
from app.models import SalesTransaction, SalesTransactionItem, Product, Inventory, PurchaseOrder, PurchaseOrderItem, Customer

if TYPE_CHECKING:
    from app.core.application_core import ApplicationCore

class ReportService:
    """Handles all database aggregation queries for reporting."""

    def __init__(self, core: "ApplicationCore"):
        self.core = core

    async def get_dashboard_stats_raw_data(self, company_id: uuid.UUID) -> Result[Dict[str, Any], str]:
        """Fetches raw data points required for the main dashboard KPIs."""
        try:
            async with self.core.get_session() as session:
                today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
                today_end = today_start + timedelta(days=1)
                
                month_start = today_start.replace(day=1)

                # 1. Today's Sales
                sales_stmt = (
                    sa.select(
                        func.coalesce(func.sum(SalesTransaction.total_amount), Decimal('0.0')).label("sales"),
                        func.coalesce(func.count(SalesTransaction.id), 0).label("transactions")
                    ).where(
                        SalesTransaction.company_id == company_id,
                        SalesTransaction.transaction_date >= today_start,
                        SalesTransaction.transaction_date < today_end,
                        SalesTransaction.status == 'COMPLETED'
                    )
                )
                sales_res = (await session.execute(sales_stmt)).one()

                # 2. New Customers This Month
                customer_stmt = (
                    sa.select(func.coalesce(func.count(Customer.id), 0))
                    .where(
                        Customer.company_id == company_id,
                        Customer.created_at >= month_start
                    )
                )
                customer_res = (await session.execute(customer_stmt)).scalar()

                # 3. Low Stock Items
                low_stock_stmt = (
                    sa.select(func.coalesce(func.count(Product.id), 0))
                    .join(Inventory, Product.id == Inventory.product_id)
                    .where(
                        Product.company_id == company_id,
                        Product.track_inventory == True,
                        Inventory.quantity_on_hand <= Product.reorder_point
                    )
                )
                low_stock_res = (await session.execute(low_stock_stmt)).scalar()

                return Success({
                    "total_sales_today": sales_res.sales,
                    "transaction_count_today": sales_res.transactions,
                    "new_customers_this_month": customer_res,
                    "low_stock_item_count": low_stock_res
                })

        except Exception as e:
            return Failure(f"Database error fetching dashboard stats: {e}")

    async def get_sales_summary_raw_data(self, company_id: uuid.UUID, start_date: date, end_date: date) -> Result[List[Dict[str, Any]], str]:
        """Fetches aggregated sales data grouped by day."""
        try:
            async with self.core.get_session() as session:
                end_datetime = datetime.combine(end_date, datetime.max.time())
                stmt = (
                    sa.select(
                        cast(SalesTransaction.transaction_date, sa.Date).label("period"),
                        func.sum(SalesTransaction.total_amount).label("total_sales"),
                        func.count(SalesTransaction.id).label("transaction_count"),
                        func.sum(SalesTransaction.discount_amount).label("total_discount_amount"),
                        func.sum(SalesTransaction.tax_amount).label("total_tax_collected")
                    ).where(
                        SalesTransaction.company_id == company_id,
                        SalesTransaction.transaction_date >= datetime.combine(start_date, datetime.min.time()),
                        SalesTransaction.transaction_date <= end_datetime,
                        SalesTransaction.status == 'COMPLETED'
                    ).group_by("period").order_by("period")
                )
                result = await session.execute(stmt)
                return Success([row._asdict() for row in result.all()])
        except Exception as e:
            return Failure(f"Database error generating sales summary: {e}")

    async def get_product_performance_raw_data(self, company_id: uuid.UUID, start_date: date, end_date: date, limit: int = 10) -> Result[List[Dict[str, Any]], str]:
        """Fetches product performance data (quantity sold, revenue, cost, margin)."""
        try:
            async with self.core.get_session() as session:
                end_datetime = datetime.combine(end_date, datetime.max.time())
                stmt = (
                    sa.select(
                        Product.id.label("product_id"), Product.sku, Product.name,
                        func.sum(SalesTransactionItem.quantity).label("quantity_sold"),
                        func.sum(SalesTransactionItem.line_total).label("total_revenue"),
                        func.sum(SalesTransactionItem.quantity * SalesTransactionItem.cost_price).label("total_cost")
                    ).join(SalesTransactionItem, SalesTransactionItem.product_id == Product.id)
                     .join(SalesTransaction, SalesTransactionItem.sales_transaction_id == SalesTransaction.id)
                     .where(
                        SalesTransaction.company_id == company_id,
                        SalesTransaction.transaction_date >= datetime.combine(start_date, datetime.min.time()),
                        SalesTransaction.transaction_date <= end_datetime,
                        SalesTransaction.status == 'COMPLETED'
                     ).group_by(Product.id).order_by(sa.desc("total_revenue")).limit(limit)
                )
                result = await session.execute(stmt)
                return Success([row._asdict() for row in result.all()])
        except Exception as e:
            return Failure(f"Database error generating product performance: {e}")

    async def get_inventory_valuation_raw_data(self, company_id: uuid.UUID, outlet_id: Optional[uuid.UUID] = None) -> Result[List[Dict[str, Any]], str]:
        """Fetches raw data for inventory valuation report."""
        try:
            async with self.core.get_session() as session:
                stmt = select(
                    Product.id.label("product_id"), Product.sku, Product.name,
                    Product.cost_price, Inventory.quantity_on_hand
                ).join(Inventory, Inventory.product_id == Product.id).where(Product.company_id == company_id)
                if outlet_id:
                    stmt = stmt.where(Inventory.outlet_id == outlet_id)
                result = await session.execute(stmt)
                return Success([row._asdict() for row in result.all()])
        except Exception as e:
            return Failure(f"Database error generating inventory valuation: {e}")

    async def get_gst_f5_raw_data(self, company_id: uuid.UUID, start_date: date, end_date: date) -> Result[Dict[str, Any], str]:
        """Fetches all necessary data points for the IRAS GST F5 form."""
        try:
            async with self.core.get_session() as session:
                end_datetime = datetime.combine(end_date, datetime.max.time())
                sales_stmt = (
                    sa.select(
                        func.sum(SalesTransactionItem.line_total).filter(Product.gst_rate > 0).label("standard_rated_sales"),
                        func.sum(SalesTransactionItem.line_total).filter(Product.gst_rate == 0).label("zero_rated_sales"),
                        func.sum(SalesTransaction.tax_amount).label("output_tax_due")
                    ).join(SalesTransactionItem, SalesTransaction.id == SalesTransactionItem.sales_transaction_id)
                     .join(Product, SalesTransactionItem.product_id == Product.id)
                     .where(
                        SalesTransaction.company_id == company_id,
                        SalesTransaction.transaction_date.between(datetime.combine(start_date, datetime.min.time()), end_datetime),
                        SalesTransaction.status == 'COMPLETED'
                    )
                )
                sales_res = (await session.execute(sales_stmt)).one_or_none()

                purchase_stmt = (
                    sa.select(
                        func.sum(PurchaseOrderItem.quantity_received * PurchaseOrderItem.unit_cost).label("taxable_purchases")
                    ).join(PurchaseOrder, PurchaseOrderItem.purchase_order_id == PurchaseOrder.id)
                     .where(
                        PurchaseOrder.company_id == company_id,
                        PurchaseOrder.order_date.between(start_date, end_date),
                        PurchaseOrder.status.in_(['RECEIVED', 'PARTIALLY_RECEIVED'])
                    )
                )
                purchase_res = (await session.execute(purchase_stmt)).one_or_none()
                
                # Assume a fixed GST rate for calculating input tax for this demo
                taxable_purchases = purchase_res.taxable_purchases or Decimal('0.00')
                input_tax_claimed = (taxable_purchases * (Decimal('8.00') / (Decimal('100.00') + Decimal('8.00')))).quantize(Decimal("0.01"))

                return Success({
                    "box_1_standard_rated_supplies": sales_res.standard_rated_sales or Decimal('0.00'),
                    "box_2_zero_rated_supplies": sales_res.zero_rated_sales or Decimal('0.00'),
                    "box_3_exempt_supplies": Decimal('0.00'),
                    "box_6_output_tax_due": sales_res.output_tax_due or Decimal('0.00'),
                    "box_5_taxable_purchases": taxable_purchases,
                    "box_7_input_tax_claimed": input_tax_claimed,
                })
        except Exception as e:
            return Failure(f"Database error generating GST F5 data: {e}")
```

#### 3. Updated File: `app/business_logic/managers/reporting_manager.py`

```python
# File: app/business_logic/managers/reporting_manager.py
"""Business Logic Manager for generating business reports and analytics."""
from __future__ import annotations
import csv
from typing import TYPE_CHECKING, List, Optional, Any
from datetime import date
from decimal import Decimal
import uuid

from app.core.result import Result, Success, Failure
from app.business_logic.managers.base_manager import BaseManager
from app.business_logic.dto.reporting_dto import (
    DashboardStatsDTO, SalesSummaryReportDTO, SalesByPeriodDTO, ProductPerformanceDTO,
    InventoryValuationReportDTO, InventoryValuationItemDTO, GstReportDTO
)
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

if TYPE_CHECKING:
    from app.core.application_core import ApplicationCore
    from app.services.report_service import ReportService
    from app.services.company_service import OutletService

class ReportingManager(BaseManager):
    """Orchestrates the creation and exportation of business intelligence reports."""
    @property
    def report_service(self) -> "ReportService": return self.core.report_service
    @property
    def outlet_service(self) -> "OutletService": return self.core.outlet_service

    async def generate_dashboard_stats(self, company_id: uuid.UUID) -> Result[DashboardStatsDTO, str]:
        """Generates the aggregated statistics for the main dashboard."""
        raw_data_result = await self.report_service.get_dashboard_stats_raw_data(company_id)
        if isinstance(raw_data_result, Failure):
            return raw_data_result
        
        return Success(DashboardStatsDTO(**raw_data_result.value))

    async def generate_sales_summary_report(self, company_id: uuid.UUID, start_date: date, end_date: date) -> Result[SalesSummaryReportDTO, str]:
        """Generates a comprehensive sales summary report."""
        sales_data_res = await self.report_service.get_sales_summary_raw_data(company_id, start_date, end_date)
        if isinstance(sales_data_res, Failure): return sales_data_res
        
        product_perf_res = await self.report_service.get_product_performance_raw_data(company_id, start_date, end_date)
        if isinstance(product_perf_res, Failure): product_perf_res.value = [] # Continue if this part fails
        
        sales_by_period = [SalesByPeriodDTO(
            period=row["period"], total_sales=row["total_sales"], transaction_count=row["transaction_count"],
            average_transaction_value=(row["total_sales"] / row["transaction_count"] if row["transaction_count"] > 0 else Decimal(0))
        ) for row in sales_data_res.value]
        
        top_products = []
        for p_data in product_perf_res.value:
            revenue = p_data.get('total_revenue', Decimal(0))
            cost = p_data.get('total_cost', Decimal(0))
            margin = revenue - cost
            margin_pct = (margin / revenue * 100) if revenue > 0 else Decimal(0)
            top_products.append(ProductPerformanceDTO(
                product_id=p_data['product_id'], sku=p_data['sku'], name=p_data['name'],
                quantity_sold=p_data['quantity_sold'], total_revenue=revenue, total_cost=cost,
                gross_margin=margin, gross_margin_percentage=margin_pct
            ))
            
        return Success(SalesSummaryReportDTO(
            start_date=start_date, end_date=end_date,
            total_revenue=sum(s.total_sales for s in sales_by_period),
            total_transactions=sum(s.transaction_count for s in sales_by_period),
            total_discount_amount=sum(row.get("total_discount_amount", Decimal(0)) for row in sales_data_res.value),
            total_tax_collected=sum(row.get("total_tax_collected", Decimal(0)) for row in sales_data_res.value),
            sales_by_period=sales_by_period, top_performing_products=top_products
        ))

    async def generate_inventory_valuation_report(self, company_id: uuid.UUID, outlet_id: Optional[uuid.UUID] = None) -> Result[InventoryValuationReportDTO, str]:
        """Generates a report showing the current value of inventory."""
        raw_data_res = await self.report_service.get_inventory_valuation_raw_data(company_id, outlet_id)
        if isinstance(raw_data_res, Failure): return raw_data_res
        
        items_data = raw_data_res.value
        valuation_items = [InventoryValuationItemDTO(**item) for item in items_data]

        outlet_name = "All Outlets"
        if outlet_id:
            outlet_res = await self.outlet_service.get_by_id(outlet_id)
            if isinstance(outlet_res, Success) and outlet_res.value: outlet_name = outlet_res.value.name

        return Success(InventoryValuationReportDTO(
            as_of_date=date.today(), outlet_id=outlet_id or uuid.uuid4(), outlet_name=outlet_name,
            total_inventory_value=sum(v.total_value for v in valuation_items),
            total_distinct_items=len(valuation_items), items=valuation_items
        ))

    async def export_report_to_pdf(self, report_data: Any, file_path: str) -> Result[str, str]:
        """Exports the provided report data DTO to a PDF file."""
        try:
            if isinstance(report_data, SalesSummaryReportDTO):
                self._create_sales_summary_pdf(report_data, file_path)
            elif isinstance(report_data, InventoryValuationReportDTO):
                self._create_inventory_valuation_pdf(report_data, file_path)
            elif isinstance(report_data, GstReportDTO):
                self._create_gst_report_pdf(report_data, file_path)
            else:
                return Failure("Unsupported report type for PDF export.")
            return Success(f"Report successfully exported to {file_path}")
        except Exception as e:
            return Failure(f"Failed to export PDF: {e}")

    async def export_report_to_csv(self, report_data: Any, file_path: str) -> Result[str, str]:
        """Exports the provided report data DTO to a CSV file."""
        try:
            if isinstance(report_data, SalesSummaryReportDTO):
                self._create_product_performance_csv(report_data, file_path)
            elif isinstance(report_data, InventoryValuationReportDTO):
                self._create_inventory_valuation_csv(report_data, file_path)
            else:
                return Failure("Unsupported report type for CSV export.")
            return Success(f"Report successfully exported to {file_path}")
        except Exception as e:
            return Failure(f"Failed to export CSV: {e}")

    # --- Private PDF Creation Helpers ---
    def _create_sales_summary_pdf(self, data: SalesSummaryReportDTO, file_path: str):
        doc = SimpleDocTemplate(file_path, rightMargin=inch/2, leftMargin=inch/2, topMargin=inch/2, bottomMargin=inch/2)
        styles = getSampleStyleSheet()
        story = [Paragraph("Sales Summary Report", styles['h1']), Spacer(1, 0.2*inch)]
        
        summary_text = f"Period: {data.start_date.strftime('%d %b %Y')} to {data.end_date.strftime('%d %b %Y')}<br/>" \
                       f"Total Revenue: S${data.total_revenue:.2f}<br/>" \
                       f"Total Transactions: {data.total_transactions}"
        story.append(Paragraph(summary_text, styles['Normal']))
        story.append(Spacer(1, 0.2*inch))

        story.append(Paragraph("Sales by Period", styles['h2']))
        sales_by_period_headers = ["Date", "Total Sales (S$)", "Transactions", "Avg. Tx Value (S$)"]
        table_data = [sales_by_period_headers] + [[p.period.strftime('%Y-%m-%d'), f"{p.total_sales:.2f}", str(p.transaction_count), f"{p.average_transaction_value:.2f}"] for p in data.sales_by_period]
        story.append(self._create_styled_table(table_data))
        story.append(Spacer(1, 0.2*inch))

        story.append(Paragraph("Top Performing Products", styles['h2']))
        product_perf_headers = ["SKU", "Product Name", "Qty Sold", "Revenue (S$)", "Margin (S$)", "Margin (%)"]
        table_data_2 = [product_perf_headers] + [[p.sku, p.name, f"{p.quantity_sold:.2f}", f"{p.total_revenue:.2f}", f"{p.gross_margin:.2f}", f"{p.gross_margin_percentage:.2f}%"] for p in data.top_performing_products]
        story.append(self._create_styled_table(table_data_2))
        
        doc.build(story)

    def _create_inventory_valuation_pdf(self, data: InventoryValuationReportDTO, file_path: str):
        doc = SimpleDocTemplate(file_path, rightMargin=inch/2, leftMargin=inch/2, topMargin=inch/2, bottomMargin=inch/2)
        styles = getSampleStyleSheet()
        story = [Paragraph("Inventory Valuation Report", styles['h1']), Spacer(1, 0.2*inch)]
        
        summary_text = f"As of Date: {data.as_of_date.strftime('%d %b %Y')}<br/>" \
                       f"Outlet: {data.outlet_name}<br/>" \
                       f"Total Inventory Value: S${data.total_inventory_value:.2f}"
        story.append(Paragraph(summary_text, styles['Normal']))
        story.append(Spacer(1, 0.2*inch))

        inv_val_headers = ["SKU", "Product Name", "Qty On Hand", "Cost Price (S$)", "Total Value (S$)"]
        table_data = [inv_val_headers] + [[i.sku, i.name, f"{i.quantity_on_hand:.4f}", f"{i.cost_price:.4f}", f"{i.total_value:.2f}"] for i in data.items]
        story.append(self._create_styled_table(table_data))
        doc.build(story)
    
    def _create_gst_report_pdf(self, data: GstReportDTO, file_path: str):
        doc = SimpleDocTemplate(file_path, rightMargin=inch, leftMargin=inch, topMargin=inch, bottomMargin=inch)
        styles = getSampleStyleSheet()
        story = [Paragraph("GST Form 5 Summary", styles['h1']), Spacer(1, 0.2*inch)]
        
        company_info = f"Company: {data.company_name} (GST Reg No: {data.company_gst_reg_no or 'N/A'})<br/>" \
                       f"Period: {data.start_date.strftime('%d %b %Y')} to {data.end_date.strftime('%d %b %Y')}"
        story.append(Paragraph(company_info, styles['Normal']))
        story.append(Spacer(1, 0.2*inch))

        gst_data = [
            ["Box 1: Standard-Rated Supplies", f"S${data.box_1_standard_rated_supplies:.2f}"],
            ["Box 6: Output Tax Due", f"S${data.box_6_output_tax_due:.2f}"],
            ["Box 5: Taxable Purchases", f"S${data.box_5_taxable_purchases:.2f}"],
            ["Box 7: Input Tax Claimed", f"S${data.box_7_input_tax_claimed:.2f}"],
            ["", ""],
            [f"Net GST {'Payable' if data.box_13_net_gst_payable >=0 else 'Claimable'}", f"S${abs(data.box_13_net_gst_payable):.2f}"]
        ]
        story.append(self._create_styled_table(gst_data, align_right_cols=[1]))
        doc.build(story)

    def _create_styled_table(self, data: List[List[Any]], align_right_cols: List[int] = []) -> Table:
        style = TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.grey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('BACKGROUND', (0,1), (-1,-1), colors.beige),
            ('GRID', (0,0), (-1,-1), 1, colors.black)
        ])
        for col_idx in align_right_cols:
            style.add('ALIGN', (col_idx, 1), (col_idx, -1), 'RIGHT')
        
        table = Table(data)
        table.setStyle(style)
        return table

    # --- Private CSV Creation Helpers ---
    def _create_product_performance_csv(self, data: SalesSummaryReportDTO, file_path: str):
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            headers = ["SKU", "Product Name", "Qty Sold", "Revenue (S$)", "Margin (S$)", "Margin (%)"]
            writer.writerow(headers)
            for p in data.top_performing_products:
                writer.writerow([p.sku, p.name, f"{p.quantity_sold:.4f}", f"{p.total_revenue:.2f}", f"{p.gross_margin:.2f}", f"{p.gross_margin_percentage:.2f}"])

    def _create_inventory_valuation_csv(self, data: InventoryValuationReportDTO, file_path: str):
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["As of Date", data.as_of_date.strftime('%Y-%m-%d')])
            writer.writerow(["Outlet Name", data.outlet_name])
            writer.writerow(["Total Value (S$)", f"{data.total_inventory_value:.2f}"])
            writer.writerow([])
            headers = ["SKU", "Product Name", "Qty On Hand", "Cost Price (S$)", "Total Value (S$)"]
            writer.writerow(headers)
            for i in data.items:
                writer.writerow([i.sku, i.name, f"{i.quantity_on_hand:.4f}", f"{i.cost_price:.4f}", f"{i.total_value:.2f}"])
```

#### 4. New File: `app/ui/views/dashboard_view.py`
```python
# File: app/ui/views/dashboard_view.py
"""The main dashboard view for displaying Key Performance Indicators (KPIs)."""
from __future__ import annotations
from typing import Optional

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QSizePolicy
)
from PySide6.QtCore import Qt, QObject

from app.core.application_core import ApplicationCore

class DashboardView(QWidget):
    """A view widget to display a dashboard of business KPIs."""
    
    def __init__(self, core: ApplicationCore, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.core = core
        self.async_worker = core.async_worker
        
        self._setup_ui()
        self._connect_signals()
        
    def _setup_ui(self):
        """Initializes the UI widgets and layout."""
        main_layout = QVBoxLayout(self)
        
        title = QLabel("Dashboard")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        
        # Placeholder for now. This will be replaced with KPI widgets.
        placeholder_label = QLabel("Dashboard View - KPI Widgets Coming Soon!")
        placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        main_layout.addWidget(title)
        main_layout.addWidget(placeholder_label)
        main_layout.addStretch()
        
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
    def _connect_signals(self):
        """Connect UI signals to slots."""
        pass # No signals to connect in the scaffold yet.
        
    def load_dashboard_data(self):
        """
        This method will be called to fetch and display dashboard data.
        To be implemented in the next sub-task.
        """
        pass

```

#### 5. Updated File: `app/ui/main_window.py`

```python
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
from app.ui.views.dashboard_view import DashboardView
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
            "dashboard": {"class": DashboardView, "instance": None},
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

        dashboard_menu = menu_bar.addMenu("&Dashboard")
        dashboard_menu.addAction("Show Dashboard", lambda: self._show_view("dashboard"))

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
```
