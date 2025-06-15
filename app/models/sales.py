# File: app/models/sales.py
"""SQLAlchemy models for Sales Transactions, Sales Items, Payments and Payment Methods."""
import uuid
from datetime import datetime
import sqlalchemy as sa
from sqlalchemy import Column, String, Boolean, ForeignKey, Numeric, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin

class SalesTransaction(Base, TimestampMixin):
    """Represents the header of a sales transaction."""
    __tablename__ = "sales_transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, doc="Unique identifier for the sales transaction")
    company_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.companies.id", ondelete="RESTRICT"), nullable=False, index=True, doc="Foreign key to the owning company")
    outlet_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.outlets.id"), nullable=False, index=True, doc="Foreign key to the outlet where the transaction occurred")
    transaction_number = Column(String(50), nullable=False, unique=True, doc="Unique transaction number (e.g., INV-0001)")
    transaction_date = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, doc="Date and time of the transaction")
    
    customer_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.customers.id"), nullable=True, index=True, doc="Foreign key to the customer involved (optional)")
    cashier_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.users.id"), nullable=False, index=True, doc="Foreign key to the user (cashier) who processed the transaction")

    subtotal = Column(Numeric(19, 2), nullable=False, doc="Sum of prices of all items before tax and discount")
    tax_amount = Column(Numeric(19, 2), nullable=False, doc="Total tax collected on the transaction")
    discount_amount = Column(Numeric(19, 2), nullable=False, default=0, doc="Total discount applied to the transaction")
    rounding_adjustment = Column(Numeric(19, 2), nullable=False, default=0, doc="Small adjustment for cash rounding (if applicable)")
    total_amount = Column(Numeric(19, 2), nullable=False, doc="Final total amount of the transaction, including tax and discounts")

    status = Column(String(20), nullable=False, default='COMPLETED', doc="Status of the transaction (COMPLETED, VOIDED, HELD)") # COMPLETED, VOIDED, HELD
    notes = Column(Text, doc="Any notes or comments for the transaction")

    # Relationships
    company = relationship("Company", back_populates="sales_transactions", doc="The company this transaction belongs to")
    outlet = relationship("Outlet", back_populates="sales_transactions", doc="The outlet where this transaction occurred")
    customer = relationship("Customer", back_populates="sales_transactions", doc="The customer involved in this transaction")
    cashier = relationship("User", back_populates="sales_transactions", doc="The cashier who processed this transaction")
    items = relationship("SalesTransactionItem", back_populates="sales_transaction", cascade="all, delete-orphan", doc="Line items in this sales transaction")
    payments = relationship("Payment", back_populates="sales_transaction", cascade="all, delete-orphan", doc="Payments applied to this sales transaction")
    journal_entries = relationship("JournalEntry", back_populates="sales_transaction", doc="Journal entries created for this sales transaction")


    __table_args__ = (
        sa.UniqueConstraint('company_id', 'transaction_number', name='uq_sales_transaction_company_number'),
        sa.CheckConstraint("status IN ('COMPLETED', 'VOIDED', 'HELD')", name="chk_sales_transaction_status") # Explicit CHECK constraint
    )

class SalesTransactionItem(Base): # Sales items are part of an immutable transaction, no updated_at
    """Represents a single line item within a sales transaction."""
    __tablename__ = "sales_transaction_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, doc="Unique identifier for the sales item")
    sales_transaction_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.sales_transactions.id", ondelete="CASCADE"), nullable=False, index=True, doc="Foreign key to the parent sales transaction")
    
    product_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.products.id"), nullable=False, index=True, doc="Foreign key to the product sold")
    variant_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.product_variants.id"), nullable=True, index=True, doc="Foreign key to the specific product variant (if applicable)") # Explicitly nullable
    
    quantity = Column(Numeric(15, 4), nullable=False, doc="Quantity of the product sold")
    unit_price = Column(Numeric(19, 4), nullable=False, doc="Selling price per unit at the time of sale")
    cost_price = Column(Numeric(19, 4), nullable=False, doc="Cost price per unit at the time of sale (for margin calculation)")
    line_total = Column(Numeric(19, 2), nullable=False, doc="Total amount for this line item (quantity * unit_price)")

    # Relationships
    sales_transaction = relationship("SalesTransaction", back_populates="items", doc="The sales transaction this item belongs to")
    product = relationship("Product", back_populates="sales_transaction_items", doc="The product sold in this line item")
    variant = relationship("ProductVariant", back_populates="sales_transaction_items", doc="The product variant sold in this line item")

    __table_args__ = (
        sa.UniqueConstraint('sales_transaction_id', 'product_id', 'variant_id', name='uq_sales_item_transaction_product_variant'), # Include variant_id in unique constraint
    )

class PaymentMethod(Base, TimestampMixin): # Payment methods can be managed, so updated_at is useful
    """Represents a payment method available to a company (e.g., Cash, NETS, Credit Card)."""
    __tablename__ = "payment_methods"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, doc="Unique identifier for the payment method")
    company_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.companies.id"), nullable=False, index=True, doc="Foreign key to the owning company")
    name = Column(String(100), nullable=False, doc="Name of the payment method (e.g., 'Cash', 'Visa', 'PayNow')")
    type = Column(String(50), nullable=False, doc="Classification of payment method (e.g., 'CASH', 'CARD', 'NETS', 'PAYNOW')")
    is_active = Column(Boolean, nullable=False, default=True, doc="Indicates if the payment method is active and available")

    # Relationships
    company = relationship("Company", back_populates="payment_methods", doc="The company this payment method belongs to")
    payments = relationship("Payment", back_populates="payment_method", doc="Payments made using this method")

    __table_args__ = (
        sa.UniqueConstraint('company_id', 'name', name='uq_payment_methods_company_name'),
        sa.CheckConstraint("type IN ('CASH', 'CARD', 'NETS', 'PAYNOW', 'VOUCHER', 'STORE_CREDIT')", name="chk_payment_method_type") # Explicit CHECK constraint
    )

class Payment(Base): # Payments are part of an immutable transaction, no updated_at
    """Represents a single payment applied to a sales transaction."""
    __tablename__ = "payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, doc="Unique identifier for the payment")
    sales_transaction_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.sales_transactions.id", ondelete="CASCADE"), nullable=False, index=True, doc="Foreign key to the sales transaction this payment is for")
    payment_method_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.payment_methods.id"), nullable=False, index=True, doc="Foreign key to the payment method used")
    
    amount = Column(Numeric(19, 2), nullable=False, doc="Amount of the payment")
    reference_number = Column(String(100), doc="Reference number for the payment (e.g., card approval code, PayNow transaction ID)")
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, doc="Timestamp when the payment was recorded") # No updated_at for immutability

    # Relationships
    sales_transaction = relationship("SalesTransaction", back_populates="payments", doc="The sales transaction this payment belongs to")
    payment_method = relationship("PaymentMethod", back_populates="payments", doc="The method used for this payment")
