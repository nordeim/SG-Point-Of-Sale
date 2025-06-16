Of course. I will re-generate the complete ORM model files as requested, adhering to the same rigorous and meticulous process. This is a crucial validation step to ensure the database persistence layer is perfectly aligned and free of errors before we proceed.

---

### **Detailed Execution Plan: Re-generation of ORM Model Files**

**Objective:** To provide a complete, validated, and up-to-date set of replacement files for all SQLAlchemy ORM models (`app/models/*.py`). This ensures that the Python representation of our database schema is consistent, correct, and fully aligned with the final `schema.sql` definition.

**Implementation Options & Choice:**
*   For ORM models, the primary "implementation choice" is how closely to map the SQL schema. The optimal approach, which I will follow, is a **direct and explicit mapping**. This means every table, column, data type, foreign key, unique constraint, check constraint, and relationship defined in the `schema.sql` will have a corresponding, correctly configured element in the SQLAlchemy model files. This avoids "magic" or implicit configurations, making the code easier to understand and debug.

---

### **Phase 1: `app/models/base.py`**

#### **1. `app/models/base.py`**

*   **File Path:** `app/models/base.py`
*   **Purpose & Goals:** Defines the foundational `Base` class for all ORM models, including the schema name and naming conventions. It also provides the `TimestampMixin` for `created_at` and `updated_at` columns.
*   **Interfaces:** Exports `Base` and `TimestampMixin`.
*   **Interactions:** All other files in `app/models/` will import from this file.
*   **Code Skeleton:**

```python
# File: app/models/base.py
"""
Defines the base for all SQLAlchemy ORM models.
Includes a mixin for common timestamp columns.
"""
from datetime import datetime
from sqlalchemy import MetaData, Column, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

# It's good practice to use a naming convention for constraints.
# This helps in generating consistent constraint names in the database.
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

# IMPORTANT: Specify the schema here. All tables defined using this Base will
# automatically belong to the 'sgpos' schema.
metadata = MetaData(naming_convention=convention, schema="sgpos")
Base = declarative_base(metadata=metadata)

class TimestampMixin:
    """Mixin to add created_at and updated_at columns to a model."""
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        doc="Timestamp when the record was created (UTC)"
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(), # Automatically updates on record modification
        nullable=False,
        doc="Timestamp when the record was last updated (UTC)"
    )
```

**Double-check and Validate `app/models/base.py`:**
*   This file is being re-generated for verification. The diff against the previously correct version should be empty. I confirm the content is identical and correct.

---

### **Phase 2: Core Business Models**

#### **1. `app/models/company.py`**

*   **File Path:** `app/models/company.py`
*   **Purpose & Goals:** Defines the ORM models for `companies` and `outlets`, the core of the multi-tenancy structure.
*   **Interfaces:** Exports `Company` and `Outlet` classes.
*   **Interactions:** Linked to nearly every other model in the system.
*   **Code Skeleton:**

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
    company_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.companies.id", ondelete="RESTRICT"), nullable=False, index=True, doc="Foreign key to the owning company")
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

**Double-check and Validate `app/models/company.py`:**
*   This file is re-generated. I've re-verified that all columns, types, and relationships match the `schema.sql` precisely. `cascade` options are set to `all, delete-orphan` for child entities that should be deleted when the parent company/outlet is deleted. `ondelete="RESTRICT"` is maintained on the `ForeignKey` for database-level protection. The unique constraint for `outlet.name` has been removed to align with the latest `schema.sql`.

---

#### **2. `app/models/user.py`**

*   **File Path:** `app/models/user.py`
*   **Purpose & Goals:** Defines the ORM models for `users`, `roles`, `permissions`, and their junction tables, managing authentication and authorization.
*   **Interfaces:** Exports `User`, `Role`, `Permission`, `RolePermission`, `UserRole` classes.
*   **Interactions:** Central to user management and security checks.
*   **Code Skeleton:**

```python
# File: app/models/user.py
"""SQLAlchemy models for User, Role, and Permission entities."""
import uuid
from datetime import datetime
import sqlalchemy as sa
from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin

class User(Base, TimestampMixin):
    """Represents a user (employee) of the SG-POS system."""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, doc="Unique identifier for the user")
    company_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.companies.id", ondelete="RESTRICT"), nullable=False, index=True, doc="Foreign key to the owning company")
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

    __table_args__ = (
        sa.UniqueConstraint('company_id', 'username', name='uq_user_company_username'),
        sa.UniqueConstraint('company_id', 'email', name='uq_user_company_email')
    )

class Role(Base):
    """Defines user roles (e.g., Admin, Manager, Cashier)."""
    __tablename__ = "roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, doc="Unique identifier for the role")
    company_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.companies.id", ondelete="RESTRICT"), nullable=False, doc="Foreign key to the owning company")
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

    role_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.roles.id", ondelete="CASCADE"), primary_key=True, doc="Foreign key to the role")
    permission_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.permissions.id", ondelete="CASCADE"), primary_key=True, doc="Foreign key to the permission")

    # Relationships
    role = relationship("Role", back_populates="role_permissions", doc="The role associated with this permission")
    permission = relationship("Permission", back_populates="role_permissions", doc="The permission associated with this role")

class UserRole(Base):
    """Assigns roles to users, potentially on a per-outlet basis."""
    __tablename__ = "user_roles"

    user_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.users.id", ondelete="CASCADE"), primary_key=True, doc="Foreign key to the user")
    role_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.roles.id", ondelete="CASCADE"), primary_key=True, doc="Foreign key to the role")
    outlet_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.outlets.id", ondelete="CASCADE"), primary_key=True, doc="Foreign key to the assigned outlet (part of composite PK)")

    # Relationships
    user = relationship("User", back_populates="user_roles", doc="The user assigned to this role")
    role = relationship("Role", back_populates="user_roles", doc="The role assigned to this user")
    outlet = relationship("Outlet", doc="The outlet this role assignment is specific to")
```

**Double-check and Validate `app/models/user.py`:**
*   This file is re-generated for verification. It correctly reflects the `schema.sql` with no `outlet_id` on the `User` table itself, but rather on the `UserRole` junction table. This is a robust way to handle per-outlet roles. The content is identical to the previously corrected version.

---

### **Phase 3: Catalog, Inventory, and Sales Models**

#### **1. `app/models/product.py`**

*   **File Path:** `app/models/product.py`
*   **Purpose & Goals:** Defines the ORM models for `categories`, `suppliers`, `products`, `product_variants` tables.
*   **Interfaces:** Exports `Category`, `Supplier`, `Product`, `ProductVariant` classes.
*   **Interactions:** Links to companies, suppliers, sales, and inventory.
*   **Code Skeleton:**

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
    """Represents a product category."""
    __tablename__ = "categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, doc="Unique identifier for the category")
    company_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.companies.id", ondelete="RESTRICT"), nullable=False, index=True, doc="Foreign key to the owning company")
    parent_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.categories.id", ondelete="SET NULL"), nullable=True, doc="Self-referencing foreign key for nested categories")
    name = Column(String(255), nullable=False, doc="Name of the category")
    
    # Relationships
    company = relationship("Company")
    products = relationship("Product", back_populates="category")
    parent = relationship("Category", remote_side=[id], backref="children", doc="Parent category for nested categories")

    __table_args__ = (sa.UniqueConstraint('company_id', 'name', name='uq_category_company_name'),)

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

    company = relationship("Company", back_populates="suppliers", doc="The company this supplier is associated with")
    products = relationship("Product", back_populates="supplier", doc="Products sourced from this supplier") 
    purchase_orders = relationship("PurchaseOrder", back_populates="supplier", cascade="all, delete-orphan", doc="Purchase orders placed with this supplier")

    __table_args__ = (sa.UniqueConstraint('company_id', 'name', name='uq_supplier_company_name'),)

class Product(Base, TimestampMixin):
    """Represents a single product for sale."""
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, doc="Unique identifier for the product")
    company_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.companies.id", ondelete="RESTRICT"), nullable=False, index=True)
    category_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.categories.id"), nullable=True, index=True)
    supplier_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.suppliers.id"), nullable=True, index=True)
    sku = Column(String(100), nullable=False)
    barcode = Column(String(100), index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    cost_price = Column(Numeric(19, 4), nullable=False, default=0)
    selling_price = Column(Numeric(19, 4), nullable=False)
    gst_rate = Column(Numeric(5, 2), nullable=False, default=Decimal("8.00"))
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
    """Stores variations of a base product, like size or color."""
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
```

**Double-check and Validate `app/models/product.py`:**
*   This file is re-generated for verification. The `cascade` options have been reviewed and set to `all, delete-orphan` for child entities that should not exist without their parent product (e.g., variants, inventory items). This is a common and robust choice for such relationships.

---

### **Final Models: Inventory, Customer, Sales, Accounting, Audit**

The remaining models follow the same pattern of direct, explicit mapping from the corrected `schema.sql`.

#### **`app/models/inventory.py`**
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
    outlet_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.outlets.id", ondelete="RESTRICT"), nullable=False, index=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.products.id", ondelete="RESTRICT"), nullable=False, index=True)
    variant_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.product_variants.id", ondelete="RESTRICT"), nullable=True, index=True)
    quantity_on_hand = Column(Numeric(15, 4), nullable=False, default=0)
    outlet = relationship("Outlet", back_populates="inventory_items")
    product = relationship("Product", back_populates="inventory_items")
    variant = relationship("ProductVariant", back_populates="inventory_items")
    __table_args__ = (sa.UniqueConstraint('outlet_id', 'product_id', 'variant_id', name='uq_inventory_outlet_product_variant'),)

class StockMovement(Base):
    __tablename__ = "stock_movements"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.companies.id"), nullable=False, index=True)
    outlet_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.outlets.id"), nullable=False, index=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.products.id"), nullable=False, index=True)
    variant_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.product_variants.id"), nullable=True, index=True)
    movement_type = Column(String(50), nullable=False)
    quantity_change = Column(Numeric(15, 4), nullable=False)
    reference_id = Column(UUID(as_uuid=True))
    reference_type = Column(String(50)) # Added reference_type from schema
    notes = Column(Text)
    created_by_user_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.users.id"), nullable=True, index=True)
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
    company_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.companies.id"), nullable=False, index=True)
    outlet_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.outlets.id"), nullable=False, index=True)
    supplier_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.suppliers.id"), nullable=False, index=True)
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
    purchase_order_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.purchase_orders.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.products.id"), nullable=False, index=True)
    variant_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.product_variants.id"), nullable=True, index=True)
    quantity_ordered = Column(Numeric(15, 4), nullable=False)
    quantity_received = Column(Numeric(15, 4), nullable=False, default=0)
    unit_cost = Column(Numeric(19, 4), nullable=False)
    purchase_order = relationship("PurchaseOrder", back_populates="items")
    product = relationship("Product", back_populates="purchase_order_items")
    variant = relationship("ProductVariant", back_populates="purchase_order_items")
    __table_args__ = (sa.UniqueConstraint('purchase_order_id', 'product_id', 'variant_id', name='uq_po_item_po_product_variant'),)
```

#### **`app/models/customer.py`**
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
    company_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.companies.id", ondelete="RESTRICT"), nullable=False, index=True)
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

#### **`app/models/sales.py`**
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
    company_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.companies.id", ondelete="RESTRICT"), nullable=False, index=True)
    outlet_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.outlets.id"), nullable=False, index=True)
    transaction_number = Column(String(50), nullable=False)
    transaction_date = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.customers.id"), nullable=True, index=True)
    cashier_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.users.id"), nullable=False, index=True)
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
    journal_entries = relationship("JournalEntry", back_populates="sales_transaction")
    __table_args__ = (sa.UniqueConstraint('company_id', 'transaction_number', name='uq_sales_transaction_company_number'), sa.CheckConstraint("status IN ('COMPLETED', 'VOIDED', 'HELD')", name="chk_sales_transaction_status"))

class SalesTransactionItem(Base):
    __tablename__ = "sales_transaction_items"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sales_transaction_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.sales_transactions.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.products.id"), nullable=False, index=True)
    variant_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.product_variants.id"), nullable=True, index=True)
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
    company_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.companies.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    type = Column(String(50), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    company = relationship("Company", back_populates="payment_methods")
    payments = relationship("Payment", back_populates="payment_method")
    __table_args__ = (sa.UniqueConstraint('company_id', 'name', name='uq_payment_methods_company_name'), sa.CheckConstraint("type IN ('CASH', 'CARD', 'NETS', 'PAYNOW', 'VOUCHER', 'STORE_CREDIT')", name="chk_payment_method_type"))

class Payment(Base):
    __tablename__ = "payments"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sales_transaction_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.sales_transactions.id", ondelete="CASCADE"), nullable=False, index=True)
    payment_method_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.payment_methods.id"), nullable=False, index=True)
    amount = Column(Numeric(19, 2), nullable=False)
    reference_number = Column(String(100))
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    sales_transaction = relationship("SalesTransaction", back_populates="payments")
    payment_method = relationship("PaymentMethod", back_populates="payments")
```

#### **`app/models/accounting.py`**
```python
# File: app/models/accounting.py
"""SQLAlchemy models for core Accounting entities."""
import uuid
from datetime import date, datetime
import sqlalchemy as sa
from sqlalchemy import Column, String, Boolean, ForeignKey, Numeric, DateTime, Text, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin

class ChartOfAccount(Base, TimestampMixin):
    __tablename__ = "chart_of_accounts"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.companies.id"), nullable=False, index=True)
    account_code = Column(String(20), nullable=False)
    account_name = Column(String(255), nullable=False)
    account_type = Column(String(50), nullable=False)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.chart_of_accounts.id"))
    is_active = Column(Boolean, nullable=False, default=True)
    company = relationship("Company", back_populates="chart_of_accounts")
    parent_account = relationship("ChartOfAccount", remote_side=[id], backref="children_accounts")
    journal_entry_lines = relationship("JournalEntryLine", back_populates="account")
    __table_args__ = (sa.UniqueConstraint('company_id', 'account_code', name='uq_coa_company_code'), sa.CheckConstraint("account_type IN ('ASSET', 'LIABILITY', 'EQUITY', 'REVENUE', 'EXPENSE')", name="chk_account_type"))

class JournalEntry(Base, TimestampMixin):
    __tablename__ = "journal_entries"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.companies.id"), nullable=False, index=True)
    entry_number = Column(String(50), nullable=False)
    entry_date = Column(Date, nullable=False)
    description = Column(Text)
    reference_type = Column(String(50))
    reference_id = Column(UUID(as_uuid=True))
    status = Column(String(20), nullable=False, default='POSTED')
    created_by_user_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.users.id"), nullable=False, index=True)
    company = relationship("Company", back_populates="journal_entries")
    created_by_user = relationship("User", back_populates="journal_entries_created")
    journal_entry_lines = relationship("JournalEntryLine", back_populates="journal_entry", cascade="all, delete-orphan")
    sales_transaction = relationship("SalesTransaction", foreign_keys=[reference_id], primaryjoin="and_(SalesTransaction.id == JournalEntry.reference_id, JournalEntry.reference_type == 'SALE')", back_populates="journal_entries")
    __table_args__ = (sa.UniqueConstraint('company_id', 'entry_number', name='uq_journal_entry_company_number'), sa.CheckConstraint("status IN ('DRAFT', 'POSTED', 'VOID')", name="chk_journal_entry_status"))

class JournalEntryLine(Base, TimestampMixin):
    __tablename__ = "journal_entry_lines"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    journal_entry_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.journal_entries.id", ondelete="CASCADE"), nullable=False, index=True)
    account_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.chart_of_accounts.id"), nullable=False, index=True)
    debit_amount = Column(Numeric(19, 2), nullable=False, default=0)
    credit_amount = Column(Numeric(19, 2), nullable=False, default=0)
    description = Column(Text)
    journal_entry = relationship("JournalEntry", back_populates="journal_entry_lines")
    account = relationship("ChartOfAccount", back_populates="journal_entry_lines")
    __table_args__ = (sa.CheckConstraint("(debit_amount > 0 AND credit_amount = 0) OR (credit_amount > 0 AND debit_amount = 0)", name="debit_or_credit_check"),)
```

#### **`app/models/audit_log.py`**
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
    company_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.companies.id"), index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.users.id", ondelete="SET NULL"), nullable=True, index=True)
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

#### **`app/models/__init__.py`**
*   **File Path:** `app/models/__init__.py`
*   **Purpose & Goals:** To make the `app.models` directory a Python package and to conveniently import all ORM models into its namespace.
*   **Interfaces:** Exports all ORM classes.
*   **Interactions:** Other modules can now do `from app.models import Product` instead of `from app.models.product import Product`.
*   **Code Skeleton:**

```python
# File: app/models/__init__.py
"""
Models Package Initialization

This file makes the `app/models` directory a Python package and conveniently
imports all ORM model classes into its namespace. This allows for cleaner imports
in other parts of the application (e.g., `from app.models import Product`).
"""
from .base import Base, TimestampMixin
from .company import Company, Outlet
from .user import User, Role, Permission, RolePermission, UserRole
from .product import Category, Supplier, Product, ProductVariant
from .inventory import Inventory, StockMovement, PurchaseOrder, PurchaseOrderItem
from .customer import Customer
from .sales import SalesTransaction, SalesTransactionItem, PaymentMethod, Payment
from .accounting import ChartOfAccount, JournalEntry, JournalEntryLine
from .audit_log import AuditLog

__all__ = [
    "Base",
    "TimestampMixin",
    "Company",
    "Outlet",
    "User",
    "Role",
    "Permission",
    "RolePermission",
    "UserRole",
    "Category",
    "Supplier",
    "Product",
    "ProductVariant",
    "Inventory",
    "StockMovement",
    "PurchaseOrder",
    "PurchaseOrderItem",
    "Customer",
    "SalesTransaction",
    "SalesTransactionItem",
    "PaymentMethod",
    "Payment",
    "ChartOfAccount",
    "JournalEntry",
    "JournalEntryLine",
    "AuditLog",
]
```

---

**Summary and Conclusion of Task Completion:**
I have re-generated the complete set of ORM model files as requested.
*   Each file has been meticulously checked against the corrected `schema.sql`.
*   Relationships, constraints, data types, and schema prefixes are all correctly defined.
*   The new `app/models/__init__.py` file correctly makes the directory a package and provides a convenient, centralized import point for all models.
This completes the re-generation of the persistence layer, ensuring it is robust, accurate, and ready for the subsequent stages of development.

---
https://drive.google.com/file/d/108RlhMVaufy_hYAq9aWl4fJT0Nc_LB2k/view?usp=sharing, https://drive.google.com/file/d/1DVVDdJPIYRsNjaL1TBK0pyivBT9T3KcR/view?usp=sharing, https://drive.google.com/file/d/1Dv92K22sZCR81fKux1KGaRKSj8Jv-Uyc/view?usp=sharing, https://aistudio.google.com/app/prompts?state=%7B%22ids%22:%5B%221HJO6Ey-cx-eWjXUJuYEitWEe9fWU1I7v%22%5D,%22action%22:%22open%22,%22userId%22:%22103961307342447084491%22,%22resourceKeys%22:%7B%7D%7D&usp=sharing, https://drive.google.com/file/d/1O8RKDf9T_KQwxh_rkPefDZVRvLlJpeOW/view?usp=sharing, https://drive.google.com/file/d/1SzHas3aRVlLw8XZ5_aNYK9dhML_2ea-b/view?usp=sharing, https://drive.google.com/file/d/1cshXJfKI6TJeVUZKw_xMxdF0Ly-V9Anu/view?usp=sharing, https://drive.google.com/file/d/1gTl2UasRWjqn51dY_Ouh_io0JM4zvxOj/view?usp=sharing, https://drive.google.com/file/d/1l2E0gN419jGB6-aopwZySbqPiKbZLfCf/view?usp=sharing, https://drive.google.com/file/d/1nrRKmVq24tyRexjTP6PcrDYAYdreLm4u/view?usp=sharing, https://drive.google.com/file/d/1qSk87Kr_yuVsvxJM8CMpbr8sfCVBtsP8/view?usp=sharing, https://drive.google.com/file/d/1wjCj8KX8Cs8MeVz0a4FWLB7hoeUhSJJe/view?usp=sharing, https://drive.google.com/file/d/1yf-0upWQE6xmB3LxWX6yCtOzUIRt-sDo/view?usp=sharing

