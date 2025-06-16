# File: app/services/report_service.py
"""
Data Access Service for complex reporting queries.

This service is responsible for running efficient data aggregation queries
directly against the database to generate the raw data needed for business reports.
It primarily uses SQLAlchemy Core for performance-critical aggregation.
"""
from __future__ import annotations
from typing import TYPE_CHECKING, List, Dict, Any, Optional
from datetime import date, datetime, timedelta
from decimal import Decimal
import uuid
import sqlalchemy as sa
from sqlalchemy.sql import func, cast

from app.core.result import Result, Success, Failure
from app.models import SalesTransaction, SalesTransactionItem, Product, Inventory, PurchaseOrder, PurchaseOrderItem

if TYPE_CHECKING:
    from app.core.application_core import ApplicationCore

class ReportService:
    """Handles all database aggregation queries for reporting."""

    def __init__(self, core: "ApplicationCore"):
        self.core = core

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
