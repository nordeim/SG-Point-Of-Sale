# File: app/models/inventory.py
"""SQLAlchemy models for Inventory and Stock Movements, Purchase Orders and Items."""
import uuid
from datetime import datetime
import sqlalchemy as sa
from sqlalchemy import Column, String, Boolean, ForeignKey, Numeric, DateTime, Text, Integer
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import Base, TimestampMixin
from sqlalchemy.orm import relationship # Import relationship here too

class Inventory(Base, TimestampMixin):
    """Represents the current quantity on hand for a product at a specific outlet."""
    __tablename__ = "inventory"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, doc="Unique identifier for the inventory record")
    outlet_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.outlets.id", ondelete="RESTRICT"), nullable=False, index=True, doc="Foreign key to the outlet where this inventory is held")
    product_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.products.id", ondelete="RESTRICT"), nullable=False, index=True, doc="Foreign key to the product being tracked")
    variant_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.product_variants.id", ondelete="RESTRICT"), nullable=True, index=True, doc="Foreign key to the specific product variant being tracked (if applicable)")
    quantity_on_hand = Column(Numeric(15, 4), nullable=False, default=0, doc="Current quantity of the product in stock")
    
    # Relationships
    outlet = relationship("Outlet", back_populates="inventory_items", doc="The outlet where this inventory is located")
    product = relationship("Product", back_populates="inventory_items", doc="The product associated with this inventory record")
    variant = relationship("ProductVariant", back_populates="inventory_items", doc="The specific product variant associated with this inventory record")

    __table_args__ = (
        sa.UniqueConstraint('outlet_id', 'product_id', 'variant_id', name='uq_inventory_outlet_product_variant'),
    )

class StockMovement(Base): # Stock movements are immutable, schema does not define updated_at
    """Immutable log of all inventory changes for full auditability."""
    __tablename__ = "stock_movements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, doc="Unique identifier for the stock movement")
    company_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.companies.id"), nullable=False, index=True, doc="Foreign key to the owning company")
    outlet_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.outlets.id"), nullable=False, index=True, doc="Foreign key to the outlet where the movement occurred")
    product_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.products.id"), nullable=False, index=True, doc="Foreign key to the product involved in the movement")
    variant_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.product_variants.id"), nullable=True, index=True, doc="Foreign key to the specific product variant involved (if applicable)")
    movement_type = Column(String(50), nullable=False, doc="Type of stock movement (e.g., SALE, PURCHASE_RECEIPT, ADJUSTMENT_IN)")
    quantity_change = Column(Numeric(15, 4), nullable=False, doc="Change in quantity (+ for stock in, - for stock out)")
    
    reference_id = Column(UUID(as_uuid=True), nullable=True, doc="ID of the related transaction (e.g., sales_transaction_id, purchase_order_id)")
    reference_type = Column(String(50), nullable=True, doc="Type of the related transaction (e.g., 'SALES_TRANSACTION', 'PURCHASE_ORDER', 'STOCK_ADJUSTMENT')")
    
    notes = Column(Text, doc="Notes or reason for the stock movement")
    created_by_user_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.users.id"), nullable=True, index=True, doc="Foreign key to the user who initiated the movement (for audit)")
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, doc="Timestamp when the stock movement record was created") # No updated_at for immutability

    # Relationships
    company = relationship("Company", back_populates="stock_movements", doc="The company this movement belongs to")
    outlet = relationship("Outlet", back_populates="stock_movements", doc="The outlet where this movement occurred")
    product = relationship("Product", back_populates="stock_movements", doc="The product affected by this movement")
    variant = relationship("ProductVariant", back_populates="stock_movements", doc="The specific product variant affected by this movement")
    user = relationship("User", back_populates="stock_movements_created", doc="The user who created this stock movement record")

# PurchaseOrder and PurchaseOrderItem models are part of app/models/inventory.py
# They are included here as per the comprehensive schema for this section.

class PurchaseOrder(Base, TimestampMixin):
    """Represents a purchase order sent to a supplier."""
    __tablename__ = "purchase_orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, doc="Unique identifier for the purchase order")
    company_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.companies.id"), nullable=False, index=True, doc="Foreign key to the owning company")
    outlet_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.outlets.id"), nullable=False, index=True, doc="Foreign key to the outlet requesting the order")
    supplier_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.suppliers.id"), nullable=False, index=True, doc="Foreign key to the supplier for this order")
    
    po_number = Column(String(50), nullable=False, doc="Unique purchase order number (generated by system)")
    order_date = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, doc="Date and time the PO was created")
    expected_delivery_date = Column(DateTime(timezone=True), nullable=True, doc="Expected date of delivery for the goods")
    status = Column(String(20), nullable=False, default='DRAFT', doc="Current status of the purchase order (e.g., DRAFT, SENT, RECEIVED)") # DRAFT, SENT, PARTIALLY_RECEIVED, RECEIVED, CANCELLED

    notes = Column(Text, doc="Any notes or comments related to the purchase order")
    total_amount = Column(Numeric(19, 2), nullable=False, default=0, doc="Calculated total cost of the purchase order")
    
    # Relationships
    company = relationship("Company", doc="The company that placed this PO")
    outlet = relationship("Outlet", back_populates="purchase_orders", doc="The outlet that this PO is for")
    supplier = relationship("Supplier", back_populates="purchase_orders", doc="The supplier providing goods for this PO")
    items = relationship("PurchaseOrderItem", back_populates="purchase_order", cascade="all, delete-orphan", doc="Line items included in this purchase order")

    __table_args__ = (
        sa.UniqueConstraint('company_id', 'po_number', name='uq_purchase_order_company_po_number'),
        sa.CheckConstraint("status IN ('DRAFT', 'SENT', 'PARTIALLY_RECEIVED', 'RECEIVED', 'CANCELLED')", name="chk_purchase_order_status") # Explicit CHECK constraint
    )

class PurchaseOrderItem(Base, TimestampMixin): # PO Items can have updated_at for receiving logic
    """Represents a single line item within a purchase order."""
    __tablename__ = "purchase_order_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, doc="Unique identifier for the PO item")
    purchase_order_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.purchase_orders.id", ondelete="CASCADE"), nullable=False, index=True, doc="Foreign key to the parent purchase order")
    product_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.products.id"), nullable=False, index=True, doc="Foreign key to the product being ordered")
    variant_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.product_variants.id"), nullable=True, index=True, doc="Foreign key to the specific product variant being ordered (if applicable)") # Added variant_id for PO items if variants are ordered
    
    quantity_ordered = Column(Numeric(15, 4), nullable=False, doc="Quantity of the product ordered")
    quantity_received = Column(Numeric(15, 4), nullable=False, default=0, doc="Quantity of the product received so far")
    unit_cost = Column(Numeric(19, 4), nullable=False, doc="Cost per unit of the product at the time of order")
    
    # Relationships
    purchase_order = relationship("PurchaseOrder", back_populates="items", doc="The purchase order this item belongs to")
    product = relationship("Product", doc="The product being ordered")
    variant = relationship("ProductVariant", back_populates="purchase_order_items", doc="The product variant being ordered") # Added relationship

    __table_args__ = (
        sa.UniqueConstraint('purchase_order_id', 'product_id', 'variant_id', name='uq_po_item_po_product_variant'), # Unique constraint includes variant_id
    )
