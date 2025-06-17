# File: app/business_logic/managers/sales_manager.py
"""
Business Logic Manager for orchestrating the entire sales workflow.
"""
from __future__ import annotations
from decimal import Decimal
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Dict, Any

from app.core.result import Result, Success, Failure
from app.business_logic.managers.base_manager import BaseManager
from app.business_logic.dto.sales_dto import SaleCreateDTO, FinalizedSaleDTO, SalesTransactionItemDTO
from app.models.sales import SalesTransaction, SalesTransactionItem, Payment
from app.models.inventory import StockMovement

if TYPE_CHECKING:
    from app.core.application_core import ApplicationCore
    from app.services.sales_service import SalesService
    from app.services.product_service import ProductService
    from app.services.user_service import UserService
    from app.business_logic.managers.inventory_manager import InventoryManager
    from app.business_logic.managers.customer_manager import CustomerManager


class SalesManager(BaseManager):
    """Orchestrates the business logic for creating and finalizing sales."""

    @property
    def sales_service(self) -> "SalesService":
        return self.core.sales_service

    @property
    def product_service(self) -> "ProductService":
        return self.core.product_service
    
    @property
    def user_service(self) -> "UserService":
        return self.core.user_service

    @property
    def inventory_manager(self) -> "InventoryManager":
        return self.core.inventory_manager

    @property
    def customer_manager(self) -> "CustomerManager":
        return self.core.customer_manager


    async def _calculate_totals(self, cart_items: List[Dict[str, Any]]) -> Result[Dict[str, Any], str]:
        """
        Internal helper to calculate subtotal, tax, and total from cart items with product details.
        Args:
            cart_items: A list of dictionaries, each containing a Product ORM model instance and quantity.
        Returns:
            A Success containing a dictionary with 'subtotal', 'tax_amount', 'total_amount', and 'items_with_details', or a Failure.
        """
        subtotal = Decimal("0.0")
        tax_amount = Decimal("0.0")
        items_with_details: List[Dict[str, Any]] = [] 
        
        for item_data in cart_items:
            product = item_data["product"]
            quantity = item_data["quantity"]
            unit_price = item_data["unit_price_override"] if item_data["unit_price_override"] is not None else product.selling_price
            
            line_subtotal = (quantity * unit_price).quantize(Decimal("0.01"))
            subtotal += line_subtotal
            
            item_tax = (line_subtotal * (product.gst_rate / Decimal("100.0"))).quantize(Decimal("0.01"))
            tax_amount += item_tax

            items_with_details.append({
                "product_id": product.id,
                "variant_id": item_data.get("variant_id"),
                "product_name": product.name,
                "sku": product.sku,
                "quantity": quantity,
                "unit_price": unit_price,
                "cost_price": product.cost_price,
                "line_total": line_subtotal,
                "gst_rate": product.gst_rate
            })

        total_amount = subtotal + tax_amount
        return Success({
            "subtotal": subtotal.quantize(Decimal("0.01")),
            "tax_amount": tax_amount.quantize(Decimal("0.01")),
            "total_amount": total_amount.quantize(Decimal("0.01")),
            "items_with_details": items_with_details
        })

    async def finalize_sale(self, dto: SaleCreateDTO) -> Result[FinalizedSaleDTO, str]:
        """
        Processes a complete sales transaction atomically.
        This is the core orchestration method.
        Args:
            dto: SaleCreateDTO containing all details for the sale.
        Returns:
            A Success with a FinalizedSaleDTO, or a Failure with an error message.
        """
        # --- 1. Pre-computation & Validation Phase (before database transaction) ---
        total_payment = sum(p.amount for p in dto.payments).quantize(Decimal("0.01"))
        
        # Fetch all product details in one go for efficiency
        product_ids = [item.product_id for item in dto.cart_items]
        fetched_products_result = await self.product_service.get_by_ids(product_ids)
        if isinstance(fetched_products_result, Failure):
            return fetched_products_result
        
        products_map = {p.id: p for p in fetched_products_result.value}
        if len(products_map) != len(product_ids):
            return Failure("One or more products in the cart could not be found.")

        # Prepare detailed cart items for calculation
        detailed_cart_items = []
        for item_dto in dto.cart_items:
            detailed_cart_items.append({
                "product": products_map[item_dto.product_id],
                "quantity": item_dto.quantity,
                "unit_price_override": item_dto.unit_price_override,
                "variant_id": item_dto.variant_id
            })

        totals_result = await self._calculate_totals(detailed_cart_items)
        if isinstance(totals_result, Failure):
            return totals_result
        
        calculated_totals = totals_result.value
        total_amount_due = calculated_totals["total_amount"]

        if total_payment < total_amount_due:
            return Failure(f"Payment amount (S${total_payment:.2f}) is less than the total amount due (S${total_amount_due:.2f}).")

        change_due = (total_payment - total_amount_due).quantize(Decimal("0.01"))
        
        # --- 2. Orchestration within a single atomic transaction ---
        try:
            async with self.core.get_session() as session:
                # 2a. Deduct inventory and get stock movement objects
                inventory_deduction_result = await self.inventory_manager.deduct_stock_for_sale(
                    dto.company_id, dto.outlet_id, calculated_totals["items_with_details"], dto.cashier_id, session
                )
                if isinstance(inventory_deduction_result, Failure):
                    return inventory_deduction_result
                
                stock_movements: List[StockMovement] = inventory_deduction_result.value

                # 2b. Construct SalesTransaction ORM model
                transaction_number = f"SALE-{uuid.uuid4().hex[:8].upper()}"
                sale = SalesTransaction(
                    company_id=dto.company_id, outlet_id=dto.outlet_id, cashier_id=dto.cashier_id,
                    customer_id=dto.customer_id, transaction_number=transaction_number,
                    subtotal=calculated_totals["subtotal"], tax_amount=calculated_totals["tax_amount"],
                    total_amount=total_amount_due, notes=dto.notes
                )
                
                # 2c. Construct line items and payments
                sale.items = [SalesTransactionItem(**{k: v for k, v in item_data.items() if k in SalesTransactionItem.__table__.columns}) for item_data in calculated_totals["items_with_details"]]
                sale.payments = [Payment(**p_info.dict()) for p_info in dto.payments]
                
                # 2d. Persist the entire transaction atomically
                saved_sale_result = await self.sales_service.create_full_transaction(sale, session)
                if isinstance(saved_sale_result, Failure):
                    return saved_sale_result
                
                saved_sale = saved_sale_result.value
                
                # 2e. Update stock movement records with the new sales_transaction_id
                for movement in stock_movements:
                    movement.reference_id = saved_sale.id
                
                # 2f. Update loyalty points if applicable
                if dto.customer_id:
                    loyalty_result = await self.customer_manager.add_loyalty_points_for_sale(dto.customer_id, saved_sale.total_amount)
                    if isinstance(loyalty_result, Failure):
                        print(f"WARNING: Failed to update loyalty points for customer {dto.customer_id}: {loyalty_result.error}")

                # 2g. Fetch customer and cashier names for the receipt
                customer_name = None
                if dto.customer_id:
                    customer_res = await self.customer_manager.get_customer(dto.customer_id)
                    if isinstance(customer_res, Success): customer_name = customer_res.value.name
                
                cashier_res = await self.user_service.get_by_id(dto.cashier_id)
                cashier_name = cashier_res.value.full_name if isinstance(cashier_res, Success) and cashier_res.value else "Unknown"

                # 2h. Construct FinalizedSaleDTO for UI feedback
                finalized_dto = FinalizedSaleDTO(
                    transaction_id=saved_sale.id, transaction_number=saved_sale.transaction_number,
                    transaction_date=saved_sale.transaction_date, subtotal=saved_sale.subtotal,
                    tax_amount=saved_sale.tax_amount, discount_amount=saved_sale.discount_amount,
                    rounding_adjustment=saved_sale.rounding_adjustment, total_amount=saved_sale.total_amount,
                    amount_paid=total_payment, change_due=change_due, customer_name=customer_name,
                    cashier_name=cashier_name, items=[SalesTransactionItemDTO.from_orm(item) for item in saved_sale.items]
                )
                return Success(finalized_dto)
        except Exception as e:
            return Failure(f"A critical error occurred while finalizing the sale: {e}")
