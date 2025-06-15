<think>
The user is encountering a `NameError: name 'Decimal' is not defined` when Alembic tries to load `app/models/product.py`. This error occurs because the `Decimal` type is used in the `default` argument for the `gst_rate` column, but the `Decimal` class itself has not been imported.

**Root Cause:**
The `Decimal` type from the `decimal` module needs to be explicitly imported before it can be used in Python code. It was correctly used in the type hint `Numeric(5, 2)`, but the Python literal `Decimal("8.00")` requires the import.

**Solution Options:**

1.  **Import `Decimal` in `app/models/product.py`:** Add `from decimal import Decimal` at the top of the file. This is the standard and most correct way to resolve this.

**Decision:**
The most straightforward and Pythonic solution is to add the import statement for `Decimal` in `app/models/product.py`.

**Execution Plan to resolve the error:**

1.  **Identify the problematic file:** `app/models/product.py`.
2.  **Add import:** Insert `from decimal import Decimal` at the top of the file, alongside other imports.
3.  **Validate:** Provide the complete updated file and perform a diff.

Let's proceed with generating the updated `app/models/product.py` file.You are absolutely correct. The `NameError: name 'Decimal' is not defined` indicates a missing import for the `Decimal` type in `app/models/product.py`. While `Numeric` is from SQLAlchemy, the `Decimal("8.00")` literal used as a default value requires `Decimal` to be imported from Python's `decimal` module.

**Solution:**
Add `from decimal import Decimal` to `app/models/product.py`.

---

Here is the complete updated replacement file for `app/models/product.py`, with the `Decimal` import added.

### **File: `app/models/product.py`**

*   **File Path:** `app/models/product.py`
*   **Purpose & Goals:** Defines the SQLAlchemy ORM models for `categories`, `suppliers`, `products`, `product_variants` tables, managing the product catalog and supplier information.
*   **Interfaces:** Exports `Category`, `Supplier`, `Product`, `ProductVariant` classes.
*   **Interactions:** Imported by services and managers. Defines relationships crucial for inventory, sales, and purchase orders.

```python
# File: app/models/product.py
"""SQLAlchemy models for Product and Category entities, and Product Variants and Suppliers."""
import uuid
from datetime import datetime
import sqlalchemy as sa
from sqlalchemy import Column, String, Boolean, ForeignKey, Numeric, DateTime, Text, Integer, Date
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from decimal import Decimal # NEW: Import Decimal

from app.models.base import Base, TimestampMixin

class Category(Base, TimestampMixin):
    """Represents a product category."""
    __tablename__ = "categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, doc="Unique identifier for the category")
    company_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.companies.id", ondelete="RESTRICT"), nullable=False, index=True, doc="Foreign key to the owning company")
    parent_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.categories.id", ondelete="SET NULL"), nullable=True, doc="Self-referencing foreign key for nested categories")
    name = Column(String(255), nullable=False, doc="Name of the category")
    
    # Relationships
    company = relationship("Company", doc="The company this category belongs to") # No back_populates on Company for this; Company has general collections
    products = relationship("Product", back_populates="category", doc="Products belonging to this category") 
    parent = relationship("Category", remote_side=[id], backref="children", doc="Parent category for nested categories") # Self-referencing relationship

    __table_args__ = (
        sa.UniqueConstraint('company_id', 'name', name='uq_category_company_name'),
    )

class Supplier(Base, TimestampMixin): 
    """Represents a product supplier."""
    __tablename__ = "suppliers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, doc="Unique identifier for the supplier")
    company_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.companies.id", ondelete="RESTRICT"), nullable=False, index=True, doc="Foreign key to the owning company")
    name = Column(String(255), nullable=False, doc="Name of the supplier (unique per company)")
    contact_person = Column(String(255), doc="Main contact person at the supplier")
    email = Column(String(255), doc="Supplier's email address")
    phone = Column(String(50), doc="Supplier's phone number")
    address = Column(Text, doc="Supplier's address")
    is_active = Column(Boolean, nullable=False, default=True, doc="Indicates if the supplier is active")

    # Relationships
    company = relationship("Company", back_populates="suppliers", doc="The company this supplier is associated with")
    products = relationship("Product", back_populates="supplier", doc="Products sourced from this supplier") 
    purchase_orders = relationship("PurchaseOrder", back_populates="supplier", cascade="all, delete-orphan", doc="Purchase orders placed with this supplier")


    __table_args__ = (
        sa.UniqueConstraint('company_id', 'name', name='uq_supplier_company_name'),
    )


class Product(Base, TimestampMixin):
    """Represents a single product for sale."""
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, doc="Unique identifier for the product")
    company_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.companies.id", ondelete="RESTRICT"), nullable=False, index=True, doc="Foreign key to the owning company")
    category_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.categories.id"), nullable=True, index=True, doc="Foreign key to the product's category")
    supplier_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.suppliers.id"), nullable=True, index=True, doc="Foreign key to the product's supplier")
    sku = Column(String(100), nullable=False, doc="Stock Keeping Unit (unique per company)")
    barcode = Column(String(100), doc="Product barcode (EAN, UPC, etc.)")
    name = Column(String(255), nullable=False, doc="Product name")
    description = Column(Text, doc="Detailed description of the product")
    cost_price = Column(Numeric(19, 4), nullable=False, default=0, doc="Cost of the product to the business")
    selling_price = Column(Numeric(19, 4), nullable=False, doc="Retail selling price of the product")
    gst_rate = Column(Numeric(5, 2), nullable=False, default=Decimal("8.00"), doc="Goods and Services Tax rate applicable to the product (e.g., 8.00 for 8%)")
    track_inventory = Column(Boolean, nullable=False, default=True, doc="If true, inventory levels for this product are tracked")
    reorder_point = Column(Integer, nullable=False, default=0, doc="Threshold quantity at which a reorder is suggested")
    is_active = Column(Boolean, nullable=False, default=True, doc="Indicates if the product is available for sale")

    # Relationships
    company = relationship("Company", back_populates="products", doc="The company that owns this product")
    category = relationship("Category", back_populates="products", doc="The category this product belongs to")
    supplier = relationship("Supplier", back_populates="products", doc="The primary supplier of this product")
    product_variants = relationship("ProductVariant", back_populates="product", cascade="all, delete-orphan", doc="Variants of this base product")
    inventory_items = relationship("Inventory", back_populates="product", doc="Inventory records for this product across outlets") 
    sales_transaction_items = relationship("SalesTransactionItem", back_populates="product", doc="Line items in sales transactions involving this product")
    purchase_order_items = relationship("PurchaseOrderItem", back_populates="product", doc="Line items in purchase orders involving this product")
    stock_movements = relationship("StockMovement", back_populates="product", doc="Stock movement records for this product")

    __table_args__ = (
        sa.UniqueConstraint('company_id', 'sku', name='uq_product_company_sku'),
        # TODO: Consider adding a unique constraint on barcode per company if needed
    )

class ProductVariant(Base, TimestampMixin):
    """Stores variations of a base product, like size or color."""
    __tablename__ = "product_variants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, doc="Unique identifier for the product variant")
    product_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.products.id", ondelete="CASCADE"), nullable=False, index=True, doc="Foreign key to the base product")
    sku_suffix = Column(String(100), nullable=False, doc="Suffix appended to base product SKU to form variant SKU")
    barcode = Column(String(100), doc="Unique barcode for this specific variant")
    attributes = Column(JSONB, nullable=False, doc="JSONB object of variant attributes (e.g., {'size': 'L', 'color': 'Red'})")
    cost_price_override = Column(Numeric(19, 4), nullable=True, doc="Override for base product's cost price for this variant")
    selling_price_override = Column(Numeric(19, 4), nullable=True, doc="Override for base product's selling price for this variant")
    is_active = Column(Boolean, nullable=False, default=True, doc="Indicates if this variant is available")
    
    # Relationships
    product = relationship("Product", back_populates="product_variants", doc="The base product this is a variant of")
    inventory_items = relationship("Inventory", back_populates="variant", doc="Inventory records for this variant")
    sales_transaction_items = relationship("SalesTransactionItem", back_populates="variant", doc="Sales items involving this variant")
    stock_movements = relationship("StockMovement", back_populates="variant", doc="Stock movements involving this variant")

    __table_args__ = (
        sa.UniqueConstraint('product_id', 'sku_suffix', name='uq_product_variant_sku_suffix'),
        # TODO: Consider adding unique constraint on barcode per product_id if barcodes are specific to variants
    )
```

**Double-check and Validate `app/models/product.py`:**

```diff
--- a/app/models/product.py
+++ b/app/models/product.py
@@ -3,6 +3,7 @@
 import uuid
 from datetime import datetime
 import sqlalchemy as sa
-from sqlalchemy import Column, String, Boolean, ForeignKey, Numeric, DateTime, Text, Integer, Date
+from sqlalchemy import Column, String, Boolean, ForeignKey, Numeric, DateTime, Text, Integer, Date
 from sqlalchemy.dialects.postgresql import UUID, JSONB
 from sqlalchemy.orm import relationship
+from decimal import Decimal # NEW: Import Decimal
 
 from app.models.base import Base, TimestampMixin
 
```

**Review and Validation Summary for `app/models/product.py`:**
The `app/models/product.py` file is now complete and correct.
*   The `from decimal import Decimal` statement has been successfully added. This resolves the `NameError`.
*   All other code remains unchanged from the previously validated version.

This ensures that Alembic can now load the `Product` model without errors and proceed with schema introspection.

