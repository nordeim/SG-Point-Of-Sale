# File: app/models/product.py
"""SQLAlchemy models for Product and Category entities, and Product Variants and Suppliers."""
import uuid
from decimal import Decimal
import sqlalchemy as sa
from sqlalchemy import Column, String, Boolean, ForeignKey, Numeric, DateTime, Text, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin

class Category(Base, TimestampMixin):
    __tablename__ = "categories"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.companies.id", ondelete="RESTRICT"), nullable=False, index=True)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.categories.id", ondelete="SET NULL"), nullable=True)
    name = Column(String(255), nullable=False)
    company = relationship("Company")
    products = relationship("Product", back_populates="category")
    parent = relationship("Category", remote_side=[id], backref="children")
    __table_args__ = (sa.UniqueConstraint('company_id', 'name', name='uq_category_company_name'),)

class Supplier(Base, TimestampMixin):
    __tablename__ = "suppliers"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.companies.id", ondelete="RESTRICT"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    contact_person = Column(String(255))
    email = Column(String(255))
    phone = Column(String(50))
    address = Column(Text)
    is_active = Column(Boolean, nullable=False, default=True)
    company = relationship("Company", back_populates="suppliers")
    products = relationship("Product", back_populates="supplier") 
    purchase_orders = relationship("PurchaseOrder", back_populates="supplier", cascade="all, delete-orphan")
    __table_args__ = (sa.UniqueConstraint('company_id', 'name', name='uq_supplier_company_name'),)

class Product(Base, TimestampMixin):
    __tablename__ = "products"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.companies.id", ondelete="RESTRICT"), nullable=False, index=True)
    category_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.categories.id"), nullable=True, index=True)
    supplier_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.suppliers.id"), nullable=True, index=True)
    sku = Column(String(100), nullable=False)
    barcode = Column(String(100), index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    cost_price = Column(Numeric(19, 4), nullable=False, default=0)
    selling_price = Column(Numeric(19, 4), nullable=False)
    gst_rate = Column(Numeric(5, 2), nullable=False, default=Decimal("9.00")) # FIX: Updated GST Rate
    track_inventory = Column(Boolean, nullable=False, default=True)
    reorder_point = Column(Integer, nullable=False, default=0)
    is_active = Column(Boolean, nullable=False, default=True)
    company = relationship("Company", back_populates="products")
    category = relationship("Category", back_populates="products")
    supplier = relationship("Supplier", back_populates="products")
    product_variants = relationship("ProductVariant", back_populates="product", cascade="all, delete-orphan")
    inventory_items = relationship("Inventory", back_populates="product", cascade="all, delete-orphan")
    sales_transaction_items = relationship("SalesTransactionItem", back_populates="product", cascade="all, delete-orphan")
    purchase_order_items = relationship("PurchaseOrderItem", back_populates="product", cascade="all, delete-orphan")
    stock_movements = relationship("StockMovement", back_populates="product", cascade="all, delete-orphan")
    __table_args__ = (sa.UniqueConstraint('company_id', 'sku', name='uq_product_company_sku'),)

class ProductVariant(Base, TimestampMixin):
    __tablename__ = "product_variants"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.products.id", ondelete="CASCADE"), nullable=False, index=True)
    sku_suffix = Column(String(100), nullable=False)
    barcode = Column(String(100))
    attributes = Column(JSONB, nullable=False)
    cost_price_override = Column(Numeric(19, 4))
    selling_price_override = Column(Numeric(19, 4))
    is_active = Column(Boolean, nullable=False, default=True)
    product = relationship("Product", back_populates="product_variants")
    inventory_items = relationship("Inventory", back_populates="variant", cascade="all, delete-orphan")
    sales_transaction_items = relationship("SalesTransactionItem", back_populates="variant", cascade="all, delete-orphan")
    stock_movements = relationship("StockMovement", back_populates="variant", cascade="all, delete-orphan")
    purchase_order_items = relationship("PurchaseOrderItem", back_populates="variant", cascade="all, delete-orphan")
    __table_args__ = (sa.UniqueConstraint('product_id', 'sku_suffix', name='uq_product_variant_sku_suffix'),)
