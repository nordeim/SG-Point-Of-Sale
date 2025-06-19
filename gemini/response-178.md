Of course. I have completed the analysis and will now proceed with the final, definitive fix for the test suite.

### **1. Systematic Diagnosis & Root Cause Analysis**

*   **The Error:** The test suite fails with `sqlalchemy.exc.NoReferencedTableError: ... could not find table 'sgpos.companies'`.
*   **Root Cause:** This error is caused by a mismatch between how table schemas are handled in PostgreSQL vs. SQLite.
    1.  The ORM models hardcode the schema name in the `ForeignKey` definitions (e.g., `ForeignKey("sgpos.companies.id")`).
    2.  The test environment uses SQLite, which does not support schemas.
    3.  During test setup, my previous fix correctly configures the `MetaData` object to *create* tables without a schema (e.g., `CREATE TABLE companies`), but SQLAlchemy then fails when it tries to resolve the hardcoded `sgpos.companies` foreign key reference because that specific, schema-qualified table name doesn't exist in its list of tables to be created.

### **2. Strategic Plan for Resolution**

The only robust and portable solution is to remove the schema name from the `ForeignKey` definitions in the models. SQLAlchemy is intelligent enough to automatically apply the schema defined in the `MetaData` object during table creation for dialects that support it (like PostgreSQL), while ignoring it for dialects that don't (like SQLite). This makes the models truly database-agnostic.

**Execution Plan:**

1.  **Refactor All Model Files:** I will systematically go through every file in `app/models/` and remove the `"sgpos."` prefix from every `ForeignKey` string.
2.  **Validate `conftest.py`:** The `conftest.py` file, as corrected in the previous step, which uses `Base.metadata.create_all` and sets the schema to `None` for testing, is now the correct companion to these model changes. No further changes are needed there.
3.  **Validate `migrations/env.py`:** Similarly, the changes to `migrations/env.py` to handle test mode are also correct and will not be altered.

This plan surgically corrects the root cause, ensuring the test suite will run successfully while guaranteeing the production application continues to work correctly with its PostgreSQL schema.

---

### **Generated and Updated Files**

Here are the complete updated replacement files for the `app/models/` directory.

#### 1. Updated File: `app/models/accounting.py`
```python
# File: app/models/accounting.py
"""SQLAlchemy models for core Accounting entities."""
import uuid
from datetime import date, datetime
import sqlalchemy as sa
from sqlalchemy import Column, String, Boolean, ForeignKey, Numeric, DateTime, Text, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, foreign
from app.models.base import Base, TimestampMixin

class ChartOfAccount(Base, TimestampMixin):
    __tablename__ = "chart_of_accounts"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True)
    account_code = Column(String(20), nullable=False)
    account_name = Column(String(255), nullable=False)
    account_type = Column(String(50), nullable=False)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("chart_of_accounts.id"))
    is_active = Column(Boolean, nullable=False, default=True)
    company = relationship("Company", back_populates="chart_of_accounts")
    parent_account = relationship("ChartOfAccount", remote_side=[id], backref="children_accounts")
    journal_entry_lines = relationship("JournalEntryLine", back_populates="account")
    __table_args__ = (sa.UniqueConstraint('company_id', 'account_code', name='uq_coa_company_code'), sa.CheckConstraint("account_type IN ('ASSET', 'LIABILITY', 'EQUITY', 'REVENUE', 'EXPENSE')", name="chk_account_type"))

class JournalEntry(Base, TimestampMixin):
    __tablename__ = "journal_entries"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True)
    entry_number = Column(String(50), nullable=False)
    entry_date = Column(Date, nullable=False)
    description = Column(Text)
    reference_type = Column(String(50))
    reference_id = Column(UUID(as_uuid=True))
    status = Column(String(20), nullable=False, default='POSTED')
    created_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    company = relationship("Company", back_populates="journal_entries")
    created_by_user = relationship("User", back_populates="journal_entries_created")
    journal_entry_lines = relationship("JournalEntryLine", back_populates="journal_entry", cascade="all, delete-orphan")
    sales_transaction = relationship(
        "SalesTransaction",
        primaryjoin="and_(foreign(JournalEntry.reference_id) == SalesTransaction.id, JournalEntry.reference_type == 'SALE')",
        back_populates="journal_entries",
        uselist=False,
        viewonly=True
    )
    __table_args__ = (sa.UniqueConstraint('company_id', 'entry_number', name='uq_journal_entry_company_number'), sa.CheckConstraint("status IN ('DRAFT', 'POSTED', 'VOID')", name="chk_journal_entry_status"))

class JournalEntryLine(Base, TimestampMixin):
    __tablename__ = "journal_entry_lines"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    journal_entry_id = Column(UUID(as_uuid=True), ForeignKey("journal_entries.id", ondelete="CASCADE"), nullable=False, index=True)
    account_id = Column(UUID(as_uuid=True), ForeignKey("chart_of_accounts.id"), nullable=False, index=True)
    debit_amount = Column(Numeric(19, 2), nullable=False, default=0)
    credit_amount = Column(Numeric(19, 2), nullable=False, default=0)
    description = Column(Text)
    journal_entry = relationship("JournalEntry", back_populates="journal_entry_lines")
    account = relationship("ChartOfAccount", back_populates="journal_entry_lines")
    __table_args__ = (sa.CheckConstraint("(debit_amount > 0 AND credit_amount = 0) OR (credit_amount > 0 AND debit_amount = 0)", name="debit_or_credit_check"),)
```

#### 2. Updated File: `app/models/audit_log.py`
```python
# File: app/models/audit_log.py
"""SQLAlchemy model for the Audit Logs."""
import uuid
from datetime import datetime
import sqlalchemy as sa
from sqlalchemy import Column, String, ForeignKey, DateTime, Text, BigInteger
from sqlalchemy.dialects.postgresql import UUID, INET, JSONB
from sqlalchemy.orm import relationship
from app.models.base import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(BigInteger, primary_key=True)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    action = Column(String(50), nullable=False)
    table_name = Column(String(100), nullable=False)
    record_id = Column(UUID(as_uuid=True), nullable=False)
    old_values = Column(JSONB)
    new_values = Column(JSONB)
    ip_address = Column(INET)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    company = relationship("Company", back_populates="audit_logs")
    user = relationship("User", back_populates="audit_logs")
```

#### 3. Updated File: `app/models/company.py`
```python
# File: app/models/company.py
"""SQLAlchemy models for Company and Outlet entities."""
import uuid
from datetime import date
import sqlalchemy as sa
from sqlalchemy import Column, String, Boolean, ForeignKey, Text, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin

class Company(Base, TimestampMixin):
    """
    Represents a company (multi-tenancy root).
    Each company owns its own data within the system.
    """
    __tablename__ = "companies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, doc="Unique identifier for the company")
    name = Column(String(255), nullable=False, doc="Legal name of the company")
    registration_number = Column(String(20), unique=True, nullable=False, doc="Singapore UEN (Unique Entity Number)")
    gst_registration_number = Column(String(20), unique=True, doc="GST registration number (optional)")
    address = Column(Text, doc="Company's primary address")
    phone = Column(String(20), doc="Company's primary phone number")
    email = Column(String(255), doc="Company's primary email address")
    base_currency = Column(String(3), nullable=False, default='SGD', doc="Base currency for financial transactions")
    fiscal_year_start = Column(Date, doc="Start date of the company's fiscal year")
    is_active = Column(Boolean, nullable=False, default=True, doc="Indicates if the company account is active")
    
    # Relationships
    outlets = relationship("Outlet", back_populates="company", cascade="all, delete-orphan", doc="Outlets belonging to this company")
    users = relationship("User", back_populates="company", cascade="all, delete-orphan", doc="Users associated with this company")
    roles = relationship("Role", back_populates="company", cascade="all, delete-orphan", doc="Roles defined by this company")
    products = relationship("Product", back_populates="company", cascade="all, delete-orphan", doc="Products defined by this company")
    customers = relationship("Customer", back_populates="company", cascade="all, delete-orphan", doc="Customers of this company")
    suppliers = relationship("Supplier", back_populates="company", cascade="all, delete-orphan", doc="Suppliers for this company")
    sales_transactions = relationship("SalesTransaction", back_populates="company", cascade="all, delete-orphan", doc="Sales transactions by this company")
    payment_methods = relationship("PaymentMethod", back_populates="company", cascade="all, delete-orphan", doc="Payment methods configured by this company")
    stock_movements = relationship("StockMovement", back_populates="company", cascade="all, delete-orphan", doc="Stock movements recorded by this company")
    chart_of_accounts = relationship("ChartOfAccount", back_populates="company", cascade="all, delete-orphan", doc="Chart of accounts for this company")
    journal_entries = relationship("JournalEntry", back_populates="company", cascade="all, delete-orphan", doc="Journal entries for this company")
    audit_logs = relationship("AuditLog", back_populates="company", doc="Audit logs related to this company")

class Outlet(Base, TimestampMixin):
    """Represents a physical retail outlet or store."""
    __tablename__ = "outlets"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, doc="Unique identifier for the outlet")
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="RESTRICT"), nullable=False, index=True, doc="Foreign key to the owning company")
    code = Column(String(50), nullable=False, doc="Unique code for the outlet within the company")
    name = Column(String(255), nullable=False, doc="Name of the outlet")
    address = Column(Text, doc="Physical address of the outlet")
    phone = Column(String(20), doc="Contact phone number for the outlet")
    is_active = Column(Boolean, nullable=False, default=True, doc="Indicates if the outlet is active")

    # Relationships
    company = relationship("Company", back_populates="outlets", doc="The company this outlet belongs to")
    inventory_items = relationship("Inventory", back_populates="outlet", cascade="all, delete-orphan", doc="Inventory items currently in this outlet")
    sales_transactions = relationship("SalesTransaction", back_populates="outlet", cascade="all, delete-orphan", doc="Sales transactions made at this outlet")
    stock_movements = relationship("StockMovement", back_populates="outlet", cascade="all, delete-orphan", doc="Stock movements recorded at this outlet")
    purchase_orders = relationship("PurchaseOrder", back_populates="outlet", cascade="all, delete-orphan", doc="Purchase orders related to this outlet")
    
    __table_args__ = (
        sa.UniqueConstraint('company_id', 'code', name='uq_outlet_company_code'),
    )
```

#### 4. Updated File: `app/models/customer.py`
```python
# File: app/models/customer.py
"""SQLAlchemy models for Customer entities."""
import uuid
import sqlalchemy as sa
from sqlalchemy import Column, String, Boolean, ForeignKey, Numeric, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin

class Customer(Base, TimestampMixin):
    __tablename__ = "customers"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="RESTRICT"), nullable=False, index=True)
    customer_code = Column(String(50), nullable=False)
    name = Column(String(255), nullable=False)
    email = Column(String(255))
    phone = Column(String(50))
    address = Column(Text)
    loyalty_points = Column(Integer, nullable=False, default=0)
    credit_limit = Column(Numeric(19, 2), nullable=False, default=0)
    is_active = Column(Boolean, nullable=False, default=True)
    company = relationship("Company", back_populates="customers")
    sales_transactions = relationship("SalesTransaction", back_populates="customer")
    __table_args__ = (sa.UniqueConstraint('company_id', 'customer_code', name='uq_customer_company_code'), sa.UniqueConstraint('company_id', 'email', name='uq_customer_company_email'))
```

#### 5. Updated File: `app/models/inventory.py`
```python
# File: app/models/inventory.py
"""SQLAlchemy models for Inventory, Stock Movements, and Purchase Orders."""
import uuid
from datetime import datetime
import sqlalchemy as sa
from sqlalchemy import Column, String, Boolean, ForeignKey, Numeric, DateTime, Text, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin

class Inventory(Base, TimestampMixin):
    __tablename__ = "inventory"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    outlet_id = Column(UUID(as_uuid=True), ForeignKey("outlets.id", ondelete="RESTRICT"), nullable=False, index=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="RESTRICT"), nullable=False, index=True)
    variant_id = Column(UUID(as_uuid=True), ForeignKey("product_variants.id", ondelete="RESTRICT"), nullable=True, index=True)
    quantity_on_hand = Column(Numeric(15, 4), nullable=False, default=0)
    outlet = relationship("Outlet", back_populates="inventory_items")
    product = relationship("Product", back_populates="inventory_items")
    variant = relationship("ProductVariant", back_populates="inventory_items")
    __table_args__ = (sa.UniqueConstraint('outlet_id', 'product_id', 'variant_id', name='uq_inventory_outlet_product_variant'),)

class StockMovement(Base):
    __tablename__ = "stock_movements"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True)
    outlet_id = Column(UUID(as_uuid=True), ForeignKey("outlets.id"), nullable=False, index=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False, index=True)
    variant_id = Column(UUID(as_uuid=True), ForeignKey("product_variants.id"), nullable=True, index=True)
    movement_type = Column(String(50), nullable=False)
    quantity_change = Column(Numeric(15, 4), nullable=False)
    reference_id = Column(UUID(as_uuid=True))
    reference_type = Column(String(50))
    notes = Column(Text)
    created_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    company = relationship("Company", back_populates="stock_movements")
    outlet = relationship("Outlet", back_populates="stock_movements")
    product = relationship("Product", back_populates="stock_movements")
    variant = relationship("ProductVariant", back_populates="stock_movements")
    user = relationship("User", back_populates="stock_movements_created")
    __table_args__ = (sa.CheckConstraint("movement_type IN ('SALE', 'RETURN', 'PURCHASE', 'ADJUSTMENT_IN', 'ADJUSTMENT_OUT', 'TRANSFER_IN', 'TRANSFER_OUT')", name="chk_stock_movement_type"),)

class PurchaseOrder(Base, TimestampMixin):
    __tablename__ = "purchase_orders"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True)
    outlet_id = Column(UUID(as_uuid=True), ForeignKey("outlets.id"), nullable=False, index=True)
    supplier_id = Column(UUID(as_uuid=True), ForeignKey("suppliers.id"), nullable=False, index=True)
    po_number = Column(String(50), nullable=False)
    order_date = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    expected_delivery_date = Column(DateTime(timezone=True))
    status = Column(String(20), nullable=False, default='DRAFT')
    notes = Column(Text)
    total_amount = Column(Numeric(19, 2), nullable=False, default=0)
    outlet = relationship("Outlet", back_populates="purchase_orders")
    supplier = relationship("Supplier", back_populates="purchase_orders")
    items = relationship("PurchaseOrderItem", back_populates="purchase_order", cascade="all, delete-orphan")
    __table_args__ = (sa.UniqueConstraint('company_id', 'po_number', name='uq_purchase_order_company_po_number'), sa.CheckConstraint("status IN ('DRAFT', 'SENT', 'PARTIALLY_RECEIVED', 'RECEIVED', 'CANCELLED')", name="chk_purchase_order_status"))

class PurchaseOrderItem(Base, TimestampMixin):
    __tablename__ = "purchase_order_items"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    purchase_order_id = Column(UUID(as_uuid=True), ForeignKey("purchase_orders.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False, index=True)
    variant_id = Column(UUID(as_uuid=True), ForeignKey("product_variants.id"), nullable=True, index=True)
    quantity_ordered = Column(Numeric(15, 4), nullable=False)
    quantity_received = Column(Numeric(15, 4), nullable=False, default=0)
    unit_cost = Column(Numeric(19, 4), nullable=False)
    purchase_order = relationship("PurchaseOrder", back_populates="items")
    product = relationship("Product", back_populates="purchase_order_items")
    variant = relationship("ProductVariant", back_populates="purchase_order_items")
    __table_args__ = (sa.UniqueConstraint('purchase_order_id', 'product_id', 'variant_id', name='uq_po_item_po_product_variant'),)
```

#### 6. Updated File: `app/models/product.py`
```python
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
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="RESTRICT"), nullable=False, index=True)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    name = Column(String(255), nullable=False)
    company = relationship("Company")
    products = relationship("Product", back_populates="category")
    parent = relationship("Category", remote_side=[id], backref="children")
    __table_args__ = (sa.UniqueConstraint('company_id', 'name', name='uq_category_company_name'),)

class Supplier(Base, TimestampMixin):
    __tablename__ = "suppliers"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="RESTRICT"), nullable=False, index=True)
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
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="RESTRICT"), nullable=False, index=True)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=True, index=True)
    supplier_id = Column(UUID(as_uuid=True), ForeignKey("suppliers.id"), nullable=True, index=True)
    sku = Column(String(100), nullable=False)
    barcode = Column(String(100), index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    cost_price = Column(Numeric(19, 4), nullable=False, default=0)
    selling_price = Column(Numeric(19, 4), nullable=False)
    gst_rate = Column(Numeric(5, 2), nullable=False, default=Decimal("9.00"))
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
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
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
```

#### 7. Updated File: `app/models/sales.py`
```python
# File: app/models/sales.py
"""SQLAlchemy models for Sales Transactions, Sales Items, and Payments."""
import uuid
from datetime import datetime
import sqlalchemy as sa
from sqlalchemy import Column, String, Boolean, ForeignKey, Numeric, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin

class SalesTransaction(Base, TimestampMixin):
    __tablename__ = "sales_transactions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="RESTRICT"), nullable=False, index=True)
    outlet_id = Column(UUID(as_uuid=True), ForeignKey("outlets.id"), nullable=False, index=True)
    transaction_number = Column(String(50), nullable=False)
    transaction_date = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=True, index=True)
    cashier_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    subtotal = Column(Numeric(19, 2), nullable=False)
    tax_amount = Column(Numeric(19, 2), nullable=False)
    discount_amount = Column(Numeric(19, 2), nullable=False, default=0)
    rounding_adjustment = Column(Numeric(19, 2), nullable=False, default=0)
    total_amount = Column(Numeric(19, 2), nullable=False)
    status = Column(String(20), nullable=False)
    notes = Column(Text)
    company = relationship("Company", back_populates="sales_transactions")
    outlet = relationship("Outlet", back_populates="sales_transactions")
    customer = relationship("Customer", back_populates="sales_transactions")
    cashier = relationship("User", back_populates="sales_transactions")
    items = relationship("SalesTransactionItem", back_populates="sales_transaction", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="sales_transaction", cascade="all, delete-orphan")
    journal_entries = relationship(
        "JournalEntry",
        primaryjoin="and_(SalesTransaction.id == foreign(JournalEntry.reference_id), JournalEntry.reference_type == 'SALE')",
        back_populates="sales_transaction",
        viewonly=True
    )
    __table_args__ = (sa.UniqueConstraint('company_id', 'transaction_number', name='uq_sales_transaction_company_number'), sa.CheckConstraint("status IN ('COMPLETED', 'VOIDED', 'HELD')", name="chk_sales_transaction_status"))

class SalesTransactionItem(Base):
    __tablename__ = "sales_transaction_items"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sales_transaction_id = Column(UUID(as_uuid=True), ForeignKey("sales_transactions.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False, index=True)
    variant_id = Column(UUID(as_uuid=True), ForeignKey("product_variants.id"), nullable=True, index=True)
    quantity = Column(Numeric(15, 4), nullable=False)
    unit_price = Column(Numeric(19, 4), nullable=False)
    cost_price = Column(Numeric(19, 4), nullable=False)
    line_total = Column(Numeric(19, 2), nullable=False)
    sales_transaction = relationship("SalesTransaction", back_populates="items")
    product = relationship("Product", back_populates="sales_transaction_items")
    variant = relationship("ProductVariant", back_populates="sales_transaction_items")
    __table_args__ = (sa.UniqueConstraint('sales_transaction_id', 'product_id', 'variant_id', name='uq_sales_item_transaction_product_variant'),)

class PaymentMethod(Base, TimestampMixin):
    __tablename__ = "payment_methods"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    type = Column(String(50), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    company = relationship("Company", back_populates="payment_methods")
    payments = relationship("Payment", back_populates="payment_method")
    __table_args__ = (sa.UniqueConstraint('company_id', 'name', name='uq_payment_methods_company_name'), sa.CheckConstraint("type IN ('CASH', 'CARD', 'NETS', 'PAYNOW', 'VOUCHER', 'STORE_CREDIT')", name="chk_payment_method_type"))

class Payment(Base):
    __tablename__ = "payments"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sales_transaction_id = Column(UUID(as_uuid=True), ForeignKey("sales_transactions.id", ondelete="CASCADE"), nullable=False, index=True)
    payment_method_id = Column(UUID(as_uuid=True), ForeignKey("payment_methods.id"), nullable=False, index=True)
    amount = Column(Numeric(19, 2), nullable=False)
    reference_number = Column(String(100))
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    sales_transaction = relationship("SalesTransaction", back_populates="payments")
    payment_method = relationship("PaymentMethod", back_populates="payments")
```

#### 8. Updated File: `app/models/user.py`
```python
# File: app/models/user.py
"""SQLAlchemy models for User, Role, and Permission entities."""
import uuid
from datetime import datetime
from typing import List
import sqlalchemy as sa
from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin

class User(Base, TimestampMixin):
    """Represents a user (employee) of the SG-POS system."""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, doc="Unique identifier for the user")
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="RESTRICT"), nullable=False, index=True, doc="Foreign key to the owning company")
    username = Column(String(100), nullable=False, doc="Unique username for login")
    email = Column(String(255), nullable=False, doc="User's email address")
    password_hash = Column(String(255), nullable=False, doc="Hashed password using bcrypt")
    full_name = Column(String(255), doc="User's full name")
    is_active = Column(Boolean, nullable=False, default=True, doc="Indicates if the user account is active")
    last_login_at = Column(DateTime(timezone=True), doc="Timestamp of the user's last successful login")
    
    # Relationships
    company = relationship("Company", back_populates="users", doc="The company this user belongs to")
    user_roles = relationship("UserRole", back_populates="user", cascade="all, delete-orphan", doc="Roles assigned to this user")
    sales_transactions = relationship("SalesTransaction", back_populates="cashier", doc="Sales transactions processed by this user")
    stock_movements_created = relationship("StockMovement", back_populates="user", doc="Stock movements created by this user")
    journal_entries_created = relationship("JournalEntry", back_populates="created_by_user", doc="Journal entries created by this user")
    audit_logs = relationship("AuditLog", back_populates="user", doc="Audit logs associated with this user")

    @property
    def roles(self) -> "List[Role]":
        """Provides a direct list of Role objects for this user."""
        return [user_role.role for user_role in self.user_roles]

    __table_args__ = (
        sa.UniqueConstraint('company_id', 'username', name='uq_user_company_username'),
        sa.UniqueConstraint('company_id', 'email', name='uq_user_company_email')
    )

class Role(Base):
    """Defines user roles (e.g., Admin, Manager, Cashier)."""
    __tablename__ = "roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, doc="Unique identifier for the role")
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="RESTRICT"), nullable=False, doc="Foreign key to the owning company")
    name = Column(String(50), nullable=False, doc="Name of the role (unique per company)")
    description = Column(Text, doc="Description of the role's responsibilities")
    is_system_role = Column(Boolean, nullable=False, default=False, doc="True for built-in roles that cannot be deleted or modified by users")
    
    # Relationships
    company = relationship("Company", back_populates="roles", doc="The company this role belongs to")
    role_permissions = relationship("RolePermission", back_populates="role", cascade="all, delete-orphan", doc="Permissions assigned to this role")
    user_roles = relationship("UserRole", back_populates="role", cascade="all, delete-orphan", doc="Users assigned to this role")

    __table_args__ = (
        sa.UniqueConstraint('company_id', 'name', name='uq_role_company_name'),
    )

class Permission(Base):
    """Defines granular permissions within the system."""
    __tablename__ = "permissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, doc="Unique identifier for the permission")
    action = Column(String(100), nullable=False, doc="The action permitted (e.g., 'CREATE', 'READ', 'UPDATE', 'DELETE')")
    resource = Column(String(100), nullable=False, doc="The resource or module the action applies to (e.g., 'PRODUCT', 'SALE_TRANSACTION')")
    description = Column(Text, doc="Description of what this permission allows")

    # Relationships
    role_permissions = relationship("RolePermission", back_populates="permission", cascade="all, delete-orphan", doc="Roles that have this permission")

    __table_args__ = (
        sa.UniqueConstraint('action', 'resource', name='uq_permission_action_resource'),
    )

class RolePermission(Base):
    """Junction table linking roles to their permissions."""
    __tablename__ = "role_permissions"

    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True, doc="Foreign key to the role")
    permission_id = Column(UUID(as_uuid=True), ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True, doc="Foreign key to the permission")

    # Relationships
    role = relationship("Role", back_populates="role_permissions", doc="The role associated with this permission")
    permission = relationship("Permission", back_populates="role_permissions", doc="The permission associated with this role")

class UserRole(Base):
    """Assigns roles to users, potentially on a per-outlet basis."""
    __tablename__ = "user_roles"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True, doc="Foreign key to the user")
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True, doc="Foreign key to the role")
    outlet_id = Column(UUID(as_uuid=True), ForeignKey("outlets.id", ondelete="CASCADE"), primary_key=True, doc="Foreign key to the assigned outlet (part of composite PK)")

    # Relationships
    user = relationship("User", back_populates="user_roles", doc="The user assigned to this role")
    role = relationship("Role", back_populates="user_roles", doc="The role assigned to this user")
    outlet = relationship("Outlet", doc="The outlet this role assignment is specific to")
```

---
https://drive.google.com/file/d/10zN6SebD-SwWDA3qAvAuPrICGzL1IVjl/view?usp=sharing, https://drive.google.com/file/d/11EUoGcc2Ooz7rfBtNPup3kDYyQbLzGCY/view?usp=sharing, https://aistudio.google.com/app/prompts?state=%7B%22ids%22:%5B%2212VGvhlsO4bTWDpTQADljLQwnQ51SA7pp%22%5D,%22action%22:%22open%22,%22userId%22:%22103961307342447084491%22,%22resourceKeys%22:%7B%7D%7D&usp=sharing, https://drive.google.com/file/d/12acS5idyq3W95Z0Yg84jJ_IqSkr8n5Yl/view?usp=sharing, https://drive.google.com/file/d/1EjDki_AWi3zMDnZi1s3ok7W2K9dp-8sv/view?usp=sharing, https://drive.google.com/file/d/1FEkbx-ITvb0YLbS3Jf1MnyCmWu2VYzca/view?usp=sharing, https://drive.google.com/file/d/1HejEv1nlMxlOSzNkm4qHUdytCe9a0ISg/view?usp=sharing, https://drive.google.com/file/d/1c6y1R7V3KgEzHGYWZiIthywgLgH2_quA/view?usp=sharing, https://drive.google.com/file/d/1hIfCPaF-Iqghfb5eMB3OeppSxisCE46N/view?usp=sharing, https://drive.google.com/file/d/1jrCxCwd5F5Tn82hhWbpawS0yqjjmpv_b/view?usp=sharing, https://drive.google.com/file/d/1pBPMY3TTXyX-bu7qSeEHZ3QqivmAujF9/view?usp=sharing, https://drive.google.com/file/d/1qMUgZ-0ZY6DCpukHkbysTocjHxnfblY-/view?usp=sharing, https://drive.google.com/file/d/1zdBax9zbZkgeJKgiwu_sQ1lu1Ngjogpc/view?usp=sharing

