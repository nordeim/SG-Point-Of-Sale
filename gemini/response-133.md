<think>
### **CodeNavigator's Deep Thought Process**

**1. Deconstruct the User's Request**

*   **Primary Goal:** Carefully review and validate the `scripts/database/schema.sql` file.
*   **Methodology:** Perform a line-by-line comparison between the raw SQL in `schema.sql` and the definitive ORM models found in `app/models/*.py`.
*   **Definition of "Correct":** The SQL schema should be a perfect representation of the schema that the SQLAlchemy ORM models would generate. This includes table names, column names, data types, constraints (PRIMARY KEY, FOREIGN KEY, UNIQUE, CHECK), nullability, defaults, and indexes.
*   **Output:** The request implies I should identify any discrepancies. Since my role is to help fix things, I should not only list the discrepancies but also provide a corrected version of the `scripts/database/schema.sql` file.

**2. Systematic Diagnosis & Analysis: The Cross-Referencing Process**

I will now perform a meticulous comparison, table by table.

**Table `companies` (`app/models/company.py`)**
*   **ORM:** `id`, `name`, `registration_number` (unique), `gst_registration_number` (unique), `address`, `phone`, `email`, `base_currency`, `fiscal_year_start`, `is_active`, `created_at`, `updated_at`.
*   **SQL:** `id`, `name`, `registration_number` (UNIQUE), `gst_registration_number` (UNIQUE), `address`, `phone`, `email`, `base_currency CHAR(3)`, `fiscal_year_start`, `is_active`, `created_at`, `updated_at`.
*   **Diff:** `base_currency` is `String(3)` in ORM, but `CHAR(3)` in SQL. `String` typically maps to `VARCHAR`. While `CHAR(3)` is functionally okay for a 3-letter currency code, `VARCHAR(3)` is more idiomatic for SQLAlchemy's `String` type. This is a very minor discrepancy, but I'll flag it for correction to achieve a perfect match. The SQL comment is also slightly different from the ORM `doc` string, which is fine.

**Table `outlets` (`app/models/company.py`)**
*   **ORM:** `id`, `company_id` (FK to `companies`), `code`, `name`, `address`, `phone`, `is_active`, `created_at`, `updated_at`. `UniqueConstraint('company_id', 'code')`.
*   **SQL:** All columns match. `UNIQUE(company_id, code)` matches. `ON DELETE RESTRICT` matches.
*   **Diff:** No discrepancy. Perfect match.

**Table `users` (`app/models/user.py`)**
*   **ORM:** `id`, `company_id` (FK to `companies`), `username`, `email`, `password_hash`, `full_name`, `is_active`, `last_login_at`, `created_at`, `updated_at`. `UniqueConstraint('company_id', 'username')`, `UniqueConstraint('company_id', 'email')`.
*   **SQL:** All columns and constraints match.
*   **Diff:** No discrepancy. Perfect match.

**Table `roles` (`app/models/user.py`)**
*   **ORM:** `id`, `company_id` (FK to `companies`), `name`, `description`, `is_system_role`. `UniqueConstraint('company_id', 'name')`.
*   **SQL:** All columns and constraints match.
*   **Diff:** No discrepancy. Perfect match.

**Table `permissions` (`app/models/user.py`)**
*   **ORM:** `id`, `action`, `resource`, `description`. `UniqueConstraint('action', 'resource')`.
*   **SQL:** All columns and constraints match.
*   **Diff:** No discrepancy. Perfect match.

**Table `role_permissions` (`app/gmodels/user.py`)**
*   **ORM:** `role_id` (PK, FK to `roles`), `permission_id` (PK, FK to `permissions`).
*   **SQL:** All columns and constraints match.
*   **Diff:** No discrepancy. Perfect match.

**Table `user_roles` (`app/models/user.py`)**
*   **ORM:** `user_id` (PK, FK to `users`), `role_id` (PK, FK to `roles`), `outlet_id` (PK, FK to `outlets`).
*   **SQL:** All columns and constraints match.
*   **Diff:** No discrepancy. Perfect match.

**Table `categories` (`app/models/product.py`)**
*   **ORM:** `id`, `company_id` (FK to `companies`), `parent_id` (FK to `categories`, `ondelete="SET NULL"`), `name`, `created_at`, `updated_at`. `UniqueConstraint('company_id', 'name')`.
*   **SQL:** All columns and constraints match. `ON DELETE SET NULL` for `parent_id` is correct.
*   **Diff:** No discrepancy. Perfect match.

**Table `suppliers` (`app/models/product.py`)**
*   **ORM:** `id`, `company_id` (FK to `companies`), `name`, `contact_person`, `email`, `phone`, `address`, `is_active`, `created_at`, `updated_at`. `UniqueConstraint('company_id', 'name')`.
*   **SQL:** All columns and constraints match.
*   **Diff:** No discrepancy. Perfect match.

**Table `products` (`app/models/product.py`)**
*   **ORM:** `id`, `company_id`, `category_id`, `supplier_id`, `sku`, `barcode`, `name`, `description`, `cost_price` (19,4), `selling_price` (19,4), `gst_rate` (5,2), `track_inventory`, `reorder_point`, `is_active`, `created_at`, `updated_at`. `UniqueConstraint('company_id', 'sku')`.
*   **SQL:** All columns and constraints match.
*   **Diff:** No discrepancy. Perfect match.

**Table `product_variants` (`app/models/product.py`)**
*   **ORM:** `id`, `product_id` (FK to `products`, `ondelete="CASCADE"`), `sku_suffix`, `barcode`, `attributes` (JSONB), `cost_price_override` (19,4), `selling_price_override` (19,4), `is_active`, `created_at`, `updated_at`. `UniqueConstraint('product_id', 'sku_suffix')`.
*   **SQL:** All columns and constraints match.
*   **Diff:** No discrepancy. Perfect match.

**Table `inventory` (`app/models/inventory.py`)**
*   **ORM:** `id`, `outlet_id`, `product_id`, `variant_id`, `quantity_on_hand` (15,4), `created_at`, `updated_at`. `UniqueConstraint('outlet_id', 'product_id', 'variant_id')`.
*   **SQL:** All columns and constraints match.
*   **Diff:** No discrepancy. Perfect match.

**Table `stock_movements` (`app/models/inventory.py`)**
*   **ORM:** `id`, `company_id`, `outlet_id`, `product_id`, `variant_id`, `movement_type`, `quantity_change` (15,4), `reference_id`, **`reference_type`**, `notes`, `created_by_user_id`, `created_at`.
*   **SQL:** `id`, `company_id`, `outlet_id`, `product_id`, `variant_id`, `movement_type`, `quantity_change`, `reference_id`, `notes`, `created_by_user_id`, `created_at`.
*   **Diff:** **CRITICAL DISCREPANCY.** The SQL schema is **missing the `reference_type` column**. The ORM model `app/models/inventory.py` clearly defines it: `reference_type = Column(String(50))`. This is a significant omission.

**Table `purchase_orders` (`app/models/inventory.py`)**
*   **ORM:** `id`, `company_id`, `outlet_id`, `supplier_id`, `po_number`, `order_date`, `expected_delivery_date`, `status`, `notes`, `total_amount` (19,2), `created_at`, `updated_at`.
*   **SQL:** All columns and constraints match.
*   **Diff:** No discrepancy. Perfect match.

**Table `purchase_order_items` (`app/models/inventory.py`)**
*   **ORM:** `id`, `purchase_order_id`, `product_id`, `variant_id`, `quantity_ordered` (15,4), `quantity_received` (15,4), `unit_cost` (19,4), `created_at`, `updated_at`.
*   **SQL:** All columns and constraints match. `variant_id` is present.
*   **Diff:** No discrepancy. Perfect match.

**Table `customers` (`app/models/customer.py`)**
*   **ORM:** `id`, `company_id`, `customer_code`, `name`, `email`, `phone`, `address`, `loyalty_points`, `credit_limit` (19,2), `is_active`, `created_at`, `updated_at`.
*   **SQL:** All columns and constraints match.
*   **Diff:** No discrepancy. Perfect match.

**Table `sales_transactions` (`app/models/sales.py`)**
*   **ORM:** `id`, `company_id`, `outlet_id`, `transaction_number`, `transaction_date`, `customer_id`, `cashier_id`, `subtotal`, `tax_amount`, `discount_amount`, `rounding_adjustment`, `total_amount`, `status`, `notes`, `created_at`, `updated_at`.
*   **SQL:** All columns and constraints match.
*   **Diff:** No discrepancy. Perfect match.

**Table `sales_transaction_items` (`app/models/sales.py`)**
*   **ORM:** `id`, `sales_transaction_id`, `product_id`, `variant_id`, `quantity` (15,4), `unit_price` (19,4), `cost_price` (19,4), `line_total` (19,2). `created_at` and `updated_at` are **not** present in the model (it inherits from `Base` only).
*   **SQL:** `id`, `sales_transaction_id`, `product_id`, `variant_id`, `quantity`, `unit_price`, `cost_price`, `line_total`.
*   **Diff:** No discrepancy. The SQL correctly reflects the ORM.

**Table `payment_methods` (`app/models/sales.py`)**
*   **ORM:** `id`, `company_id`, `name`, `type`, `is_active`, `created_at`, `updated_at`. Inherits `TimestampMixin`.
*   **SQL:** `id`, `company_id`, `name`, `type`, `is_active`, `created_at`, `updated_at`.
*   **Diff:** No discrepancy. Perfect match.

**Table `payments` (`app/models/sales.py`)**
*   **ORM:** `id`, `sales_transaction_id`, `payment_method_id`, `amount` (19,2), `reference_number`, `created_at`. Does **not** have `updated_at`.
*   **SQL:** `id`, `sales_transaction_id`, `payment_method_id`, `amount`, `reference_number`, `created_at`, **`updated_at`**.
*   **Diff:** **CRITICAL DISCREPANCY.** The SQL schema has an `updated_at` column, but the ORM model does not. The ORM is the source of truth for the application's behavior. The `updated_at` column should be removed from the SQL schema to match.

**Table `chart_of_accounts` (`app/models/accounting.py`)**
*   **ORM:** `id`, `company_id`, `account_code`, `account_name`, `account_type`, `parent_id`, `is_active`, `created_at`, `updated_at`.
*   **SQL:** All columns and constraints match.
*   **Diff:** No discrepancy. Perfect match.

**Table `journal_entries` (`app/models/accounting.py`)**
*   **ORM:** `id`, `company_id`, `entry_number`, `entry_date`, `description`, `reference_type`, `reference_id`, `status`, `created_by_user_id`, `created_at`, `updated_at`.
*   **SQL:** All columns and constraints match.
*   **Diff:** No discrepancy. Perfect match.

**Table `journal_entry_lines` (`app/models/accounting.py`)**
*   **ORM:** `id`, `journal_entry_id`, `account_id`, `debit_amount` (19,2), `credit_amount` (19,2), `description`, `created_at`, `updated_at`. CHECK constraint is `(debit_amount > 0 AND credit_amount = 0) OR (credit_amount > 0 AND debit_amount = 0)`.
*   **SQL:** `id`, `journal_entry_id`, `account_id`, `debit_amount`, `credit_amount`, `description`, `created_at`, `updated_at`. CHECK constraint is `(debit_amount > 0 AND credit_amount = 0) OR (credit_amount > 0 AND debit_amount = 0)`.
*   **Diff:** No discrepancy. Perfect match.

**Table `audit_logs` (`app/models/audit_log.py`)**
*   **ORM:** `id` (BigInteger, PK), `company_id`, `user_id`, `action`, `table_name`, `record_id`, `old_values`, `new_values`, `ip_address`, `created_at`.
*   **SQL:** `id` (BIGSERIAL, PK), `company_id`, `user_id`, `action`, `table_name`, `record_id`, `old_values`, `new_values`, `ip_address`, `created_at`.
*   **Diff:** `BIGSERIAL` in SQL vs `BigInteger` in ORM. `BIGSERIAL` is a PostgreSQL-specific shorthand for `bigint NOT NULL DEFAULT nextval(...)`. The ORM model correctly uses the generic `BigInteger` type, which SQLAlchemy will translate appropriately. This is not a functional discrepancy. It's a perfect match.

**Indexes Section (`schema.sql`)**
*   I will now cross-check the indexes. The ORM models define indexes implicitly (`index=True` on a column) or explicitly. `schema.sql` lists them all out.
*   `idx_products_barcode`: Exists in both.
*   `idx_stock_movements_...`: All seem correct.
*   `idx_sales_transactions_transaction_date`: In SQL it is `DESC`. The ORM model (`sales.py`) does not specify a direction. This is a minor enhancement in the SQL file, not a discrepancy with the ORM's base requirement. I will leave the `DESC` as it is good practice.
*   `idx_journal_entries_entry_date`: Same as above, `DESC` is an enhancement.
*   **Missing Index:** The `stock_movements` table in the ORM model has `reference_id` and `created_by_user_id` both marked with `index=True` (implicitly, via FK convention). Let me check the SQL. Yes, `idx_stock_movements_created_by_user_id` exists. `reference_id` is not indexed in the SQL. Let me check the ORM `app/models/inventory.py` `StockMovement`... `reference_id = Column(UUID(as_uuid=True))`. No `index=True`. The SQL `idx_journal_entries_reference_id` is present. The SQL is inconsistent. I will add an index on `stock_movements.reference_id` for consistency and likely performance.
*   `reference_type` on `stock_movements` is not indexed in either, which is probably fine unless it's frequently filtered on.

**Triggers and Functions Section (`schema.sql`)**
*   `update_updated_at_column()`: Standard and correct.
*   `log_changes()`: This is a database-level audit trigger. The application doesn't currently use it, as there's no code setting the session variables (`sgpos.current_user_id`). It's a good-to-have feature documented in the schema, but not strictly part of the ORM definition. It doesn't conflict with the ORM, so it can remain as a potential future enhancement.

**Summary of Discrepancies to Fix in `schema.sql`:**
1.  **`companies.base_currency`:** Change `CHAR(3)` to `VARCHAR(3)` for perfect ORM alignment.
2.  **`stock_movements`:** Add the missing `reference_type VARCHAR(50)` column.
3.  **`payments`:** Remove the `updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()` column, as it's not in the `Payment` ORM model.
4.  **Indexes:** Add `CREATE INDEX idx_stock_movements_reference_id ON sgpos.stock_movements(reference_id);` for consistency with `journal_entries`.

**6. Planning the Implementation**

1.  I will take the existing `scripts/database/schema.sql` as the baseline.
2.  I will apply the four changes identified above.
3.  I will perform a final line-by-line review of the generated file against my plan to ensure accuracy and completeness, making sure no other parts of the file are accidentally altered.
4.  I will present the complete, corrected file along with a detailed explanation of the changes made.

This meticulous process guarantees that the final `schema.sql` will be a true and accurate reflection of the ORM models, serving as a reliable source of truth for the project.I acknowledge the request. As CodeNavigator, I will now perform a meticulous, line-by-line validation of `scripts/database/schema.sql` against the definitive source of truth: the SQLAlchemy ORM models in `app/models/`.

My analysis has revealed a few critical discrepancies where the raw SQL schema has diverged from the application's ORM models. An accurate `schema.sql` is vital for documentation, manual database setups, and ensuring a shared understanding of the database structure.

### **1. Systematic Diagnosis: Discrepancies Found**

After a thorough comparison, I have identified the following inconsistencies between the `schema.sql` file and the ORM models:

1.  **`companies` Table:** The `base_currency` column is defined as `CHAR(3)` in the SQL file, while the ORM's `String(3)` more accurately maps to `VARCHAR(3)`. While functionally similar for this specific case, `VARCHAR` is the more conventional mapping.
2.  **`stock_movements` Table:** This is the most significant discrepancy. The SQL schema is **missing the `reference_type` column**. The ORM model `app/models/inventory.py` clearly defines this `String(50)` column, which is crucial for identifying the source of a stock movement (e.g., `'SALE'`, `'PURCHASE'`).
3.  **`payments` Table:** The SQL schema incorrectly includes an `updated_at` column. The corresponding `Payment` model in `app/models/sales.py` intentionally only has a `created_at` field, as payments are generally considered immutable once created. The SQL file must be corrected to match the ORM's definition.
4.  **Indexes:** The `stock_movements` table was missing a recommended index on its `reference_id` column. While not a strict schema mismatch, adding it aligns with best practices and the indexing strategy seen on similar tables like `journal_entries`.

### **2. Strategic Plan for Resolution**

I will now provide a corrected version of the `schema.sql` file. My plan is to make surgical edits to the original file to address each of the identified discrepancies, ensuring that the rest of the well-structured file, including its valuable comments and indexing, remains intact.

*   Modify `companies.base_currency` to `VARCHAR(3)`.
*   Add the `reference_type VARCHAR(50)` column to the `stock_movements` table definition.
*   Remove the `updated_at` column from the `payments` table definition.
*   Add the missing index for `stock_movements.reference_id`.

### **3. Implementation: Corrected `scripts/database/schema.sql`**

Here is the complete, validated, and corrected replacement for the `schema.sql` file.

```sql
-- File: scripts/database/schema.sql
-- =============================================================================
-- SG Point-of-Sale (SG-POS) System - Complete Database Schema
-- Version: 2.2 (Corrected to match ORM Models)
-- Database: PostgreSQL 15+
-- =============================================================================

-- Best practice: Isolate the application's tables within their own schema.
CREATE SCHEMA IF NOT EXISTS sgpos;
SET search_path TO sgpos;

-- Enable the pgcrypto extension to generate UUIDs.
-- This should be run once by a superuser on the target database.
CREATE EXTENSION IF NOT EXISTS "pgcrypto";


-- =============================================================================
-- Section 1: Core Business & Multi-Tenancy Structure
-- Description: Defines the top-level entities for companies and their outlets.
-- =============================================================================

CREATE TABLE companies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    registration_number VARCHAR(20) UNIQUE NOT NULL,
    gst_registration_number VARCHAR(20) UNIQUE,
    address TEXT,
    phone VARCHAR(20),
    email VARCHAR(255),
    -- FIX: Changed CHAR(3) to VARCHAR(3) to perfectly match SQLAlchemy's String(3) mapping.
    base_currency VARCHAR(3) NOT NULL DEFAULT 'SGD',
    fiscal_year_start DATE,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
COMMENT ON TABLE sgpos.companies IS 'Top-level entity for multi-tenancy support. Each company is a separate business customer.';
COMMENT ON COLUMN sgpos.companies.registration_number IS 'Singapore UEN (Unique Entity Number)';


CREATE TABLE outlets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES sgpos.companies(id) ON DELETE RESTRICT,
    code VARCHAR(50) NOT NULL,
    name VARCHAR(255) NOT NULL,
    address TEXT,
    phone VARCHAR(20),
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(company_id, code)
);
COMMENT ON TABLE sgpos.outlets IS 'Represents physical store locations or branches for a company.';


-- =============================================================================
-- Section 2: Users, Roles, and Security (RBAC Model)
-- Description: Manages user authentication and role-based access control.
-- =============================================================================

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES sgpos.companies(id) ON DELETE RESTRICT,
    username VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN NOT NULL DEFAULT true,
    last_login_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(company_id, username),
    UNIQUE(company_id, email)
);
COMMENT ON COLUMN sgpos.users.password_hash IS 'Hashed using bcrypt';

CREATE TABLE roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES sgpos.companies(id) ON DELETE RESTRICT,
    name VARCHAR(50) NOT NULL,
    description TEXT,
    is_system_role BOOLEAN NOT NULL DEFAULT false,
    UNIQUE(company_id, name)
);
COMMENT ON TABLE sgpos.roles IS 'Defines user roles like Admin, Manager, Cashier.';
COMMENT ON COLUMN sgpos.roles.is_system_role IS 'True for built-in roles like "Admin", which cannot be deleted.';

CREATE TABLE permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    action VARCHAR(100) NOT NULL, -- e.g., 'CREATE', 'READ', 'UPDATE', 'DELETE', 'APPROVE'
    resource VARCHAR(100) NOT NULL, -- e.g., 'PRODUCT', 'SALE_TRANSACTION', 'USER_MANAGEMENT'
    description TEXT,
    UNIQUE(action, resource)
);
COMMENT ON TABLE sgpos.permissions IS 'Defines granular permissions within the system.';

CREATE TABLE role_permissions (
    role_id UUID NOT NULL REFERENCES sgpos.roles(id) ON DELETE CASCADE,
    permission_id UUID NOT NULL REFERENCES sgpos.permissions(id) ON DELETE CASCADE,
    PRIMARY KEY (role_id, permission_id)
);
COMMENT ON TABLE sgpos.role_permissions IS 'Junction table linking roles to their permissions.';

CREATE TABLE user_roles (
    user_id UUID NOT NULL REFERENCES sgpos.users(id) ON DELETE CASCADE,
    role_id UUID NOT NULL REFERENCES sgpos.roles(id) ON DELETE CASCADE,
    -- outlet_id allows for role assignment specific to a store, can be NULL for company-wide roles.
    outlet_id UUID REFERENCES sgpos.outlets(id) ON DELETE CASCADE, -- Made implicitly NOT NULL by PK below. If NULLable global roles are required, PK needs to be reconsidered or separate table.
    PRIMARY KEY (user_id, role_id, outlet_id)
);
COMMENT ON TABLE sgpos.user_roles IS 'Assigns roles to users, potentially on a per-outlet basis.';


-- =============================================================================
-- Section 3: Product Catalog & Inventory
-- Description: Manages products, suppliers, categories, and stock levels.
-- =============================================================================

CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES sgpos.companies(id) ON DELETE RESTRICT,
    parent_id UUID REFERENCES sgpos.categories(id) ON DELETE SET NULL,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(company_id, name)
);

CREATE TABLE suppliers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES sgpos.companies(id) ON DELETE RESTRICT,
    name VARCHAR(255) NOT NULL,
    contact_person VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(50),
    address TEXT,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(company_id, name)
);

CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES sgpos.companies(id) ON DELETE RESTRICT,
    category_id UUID REFERENCES sgpos.categories(id),
    supplier_id UUID REFERENCES sgpos.suppliers(id),
    sku VARCHAR(100) NOT NULL,
    barcode VARCHAR(100),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    cost_price NUMERIC(19, 4) NOT NULL DEFAULT 0,
    selling_price NUMERIC(19, 4) NOT NULL,
    gst_rate NUMERIC(5, 2) NOT NULL DEFAULT 9.00,
    track_inventory BOOLEAN NOT NULL DEFAULT true,
    reorder_point INT NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(company_id, sku)
);
COMMENT ON COLUMN sgpos.products.gst_rate IS 'Current SG GST rate, can be overridden per product';

CREATE TABLE product_variants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID NOT NULL REFERENCES sgpos.products(id) ON DELETE CASCADE,
    sku_suffix VARCHAR(100) NOT NULL,
    barcode VARCHAR(100),
    attributes JSONB NOT NULL,
    cost_price_override NUMERIC(19, 4),
    selling_price_override NUMERIC(19, 4),
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(product_id, sku_suffix)
);
COMMENT ON TABLE sgpos.product_variants IS 'Stores variations of a base product, like size or color.';
COMMENT ON COLUMN sgpos.product_variants.attributes IS 'e.g., {"size": "L", "color": "Red"}';


CREATE TABLE inventory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    outlet_id UUID NOT NULL REFERENCES sgpos.outlets(id) ON DELETE RESTRICT,
    product_id UUID NOT NULL REFERENCES sgpos.products(id) ON DELETE RESTRICT,
    variant_id UUID REFERENCES sgpos.product_variants(id) ON DELETE RESTRICT,
    quantity_on_hand NUMERIC(15, 4) NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(outlet_id, product_id, variant_id)
);
COMMENT ON TABLE sgpos.inventory IS 'Tracks the actual stock count of a specific product/variant at a specific outlet.';

CREATE TABLE stock_movements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES sgpos.companies(id),
    outlet_id UUID NOT NULL REFERENCES sgpos.outlets(id),
    product_id UUID NOT NULL REFERENCES sgpos.products(id),
    variant_id UUID REFERENCES sgpos.product_variants(id),
    movement_type VARCHAR(50) NOT NULL CHECK (movement_type IN ('SALE', 'RETURN', 'PURCHASE', 'ADJUSTMENT_IN', 'ADJUSTMENT_OUT', 'TRANSFER_IN', 'TRANSFER_OUT')),
    quantity_change NUMERIC(15, 4) NOT NULL,
    reference_id UUID,
    -- FIX: Added missing reference_type column to match the ORM model.
    reference_type VARCHAR(50),
    notes TEXT,
    created_by_user_id UUID REFERENCES sgpos.users(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
COMMENT ON TABLE sgpos.stock_movements IS 'Immutable log of all inventory changes for full auditability.';
COMMENT ON COLUMN sgpos.stock_movements.quantity_change IS 'Positive for stock in, negative for stock out';
COMMENT ON COLUMN sgpos.stock_movements.reference_id IS 'e.g., sales_transaction_id, purchase_order_id';
COMMENT ON COLUMN sgpos.stock_movements.reference_type IS 'e.g., ''SALE'', ''PURCHASE_ORDER''';


CREATE TABLE purchase_orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES sgpos.companies(id),
    outlet_id UUID NOT NULL REFERENCES sgpos.outlets(id),
    supplier_id UUID NOT NULL REFERENCES sgpos.suppliers(id),
    po_number VARCHAR(50) NOT NULL,
    order_date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expected_delivery_date TIMESTAMPTZ,
    status VARCHAR(20) NOT NULL CHECK (status IN ('DRAFT', 'SENT', 'PARTIALLY_RECEIVED', 'RECEIVED', 'CANCELLED')),
    notes TEXT,
    total_amount NUMERIC(19, 2) NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(company_id, po_number)
);
COMMENT ON TABLE sgpos.purchase_orders IS 'Represents a purchase order sent to a supplier.';

CREATE TABLE purchase_order_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    purchase_order_id UUID NOT NULL REFERENCES sgpos.purchase_orders(id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES sgpos.products(id),
    variant_id UUID REFERENCES sgpos.product_variants(id),
    quantity_ordered NUMERIC(15, 4) NOT NULL,
    quantity_received NUMERIC(15, 4) NOT NULL DEFAULT 0,
    unit_cost NUMERIC(19, 4) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(purchase_order_id, product_id, variant_id)
);
COMMENT ON TABLE sgpos.purchase_order_items IS 'A line item within a purchase order.';


-- =============================================================================
-- Section 4: Sales & Transactions
-- Description: The core tables for handling sales, customers, and payments.
-- =============================================================================

CREATE TABLE customers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES sgpos.companies(id) ON DELETE RESTRICT,
    customer_code VARCHAR(50) NOT NULL,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(50),
    address TEXT,
    loyalty_points INT NOT NULL DEFAULT 0,
    credit_limit NUMERIC(19, 2) NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(company_id, customer_code),
    UNIQUE(company_id, email)
);

CREATE TABLE sales_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES sgpos.companies(id) ON DELETE RESTRICT,
    outlet_id UUID NOT NULL REFERENCES sgpos.outlets(id),
    transaction_number VARCHAR(50) NOT NULL,
    transaction_date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    customer_id UUID REFERENCES sgpos.customers(id),
    cashier_id UUID NOT NULL REFERENCES sgpos.users(id),
    subtotal NUMERIC(19, 2) NOT NULL,
    tax_amount NUMERIC(19, 2) NOT NULL,
    discount_amount NUMERIC(19, 2) NOT NULL DEFAULT 0,
    rounding_adjustment NUMERIC(19, 2) NOT NULL DEFAULT 0,
    total_amount NUMERIC(19, 2) NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('COMPLETED', 'VOIDED', 'HELD')),
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(company_id, transaction_number)
);

CREATE TABLE sales_transaction_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sales_transaction_id UUID NOT NULL REFERENCES sgpos.sales_transactions(id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES sgpos.products(id),
    variant_id UUID REFERENCES sgpos.product_variants(id),
    quantity NUMERIC(15, 4) NOT NULL,
    unit_price NUMERIC(19, 4) NOT NULL,
    cost_price NUMERIC(19, 4) NOT NULL,
    line_total NUMERIC(19, 2) NOT NULL,
    UNIQUE(sales_transaction_id, product_id, variant_id)
);
COMMENT ON TABLE sgpos.sales_transaction_items IS 'Individual line items for a sales transaction.';
COMMENT ON COLUMN sgpos.sales_transaction_items.unit_price IS 'Price at time of sale';
COMMENT ON COLUMN sgpos.sales_transaction_items.cost_price IS 'Cost at time of sale for margin analysis';

CREATE TABLE payment_methods (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES sgpos.companies(id),
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL CHECK (type IN ('CASH', 'CARD', 'NETS', 'PAYNOW', 'VOUCHER', 'STORE_CREDIT')),
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(company_id, name)
);

CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sales_transaction_id UUID NOT NULL REFERENCES sgpos.sales_transactions(id) ON DELETE CASCADE,
    payment_method_id UUID NOT NULL REFERENCES sgpos.payment_methods(id),
    amount NUMERIC(19, 2) NOT NULL,
    reference_number VARCHAR(100),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    -- FIX: Removed updated_at column to match the ORM model, as payments are immutable.
);
COMMENT ON TABLE sgpos.payments IS 'Records individual payments, supporting split tender.';
COMMENT ON COLUMN sgpos.payments.reference_number IS 'For card transactions, e-wallets, etc.';


-- =============================================================================
-- Section 5: Accounting & GST
-- Description: Tables for financial records, chart of accounts, and GST compliance.
-- =============================================================================

CREATE TABLE chart_of_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES sgpos.companies(id),
    account_code VARCHAR(20) NOT NULL,
    account_name VARCHAR(255) NOT NULL,
    account_type VARCHAR(50) NOT NULL CHECK (account_type IN ('ASSET', 'LIABILITY', 'EQUITY', 'REVENUE', 'EXPENSE')),
    parent_id UUID REFERENCES sgpos.chart_of_accounts(id),
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(company_id, account_code)
);

CREATE TABLE journal_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES sgpos.companies(id),
    entry_number VARCHAR(50) NOT NULL,
    entry_date DATE NOT NULL,
    description TEXT,
    reference_type VARCHAR(50),
    reference_id UUID,
    status VARCHAR(20) NOT NULL DEFAULT 'POSTED' CHECK (status IN ('DRAFT', 'POSTED', 'VOID')),
    created_by_user_id UUID NOT NULL REFERENCES sgpos.users(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(company_id, entry_number)
);

CREATE TABLE journal_entry_lines (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    journal_entry_id UUID NOT NULL REFERENCES sgpos.journal_entries(id) ON DELETE CASCADE,
    account_id UUID NOT NULL REFERENCES sgpos.chart_of_accounts(id),
    debit_amount NUMERIC(19, 2) NOT NULL DEFAULT 0,
    credit_amount NUMERIC(19, 2) NOT NULL DEFAULT 0,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT debit_or_credit_check CHECK ( (debit_amount > 0 AND credit_amount = 0) OR (credit_amount > 0 AND debit_amount = 0) )
);
COMMENT ON TABLE sgpos.journal_entry_lines IS 'Individual lines of a double-entry bookkeeping record.';


-- =============================================================================
-- Section 6: Auditing
-- Description: A comprehensive, immutable log of all significant changes.
-- =============================================================================

CREATE TABLE audit_logs (
    id BIGSERIAL PRIMARY KEY,
    company_id UUID,
    user_id UUID REFERENCES sgpos.users(id) ON DELETE SET NULL,
    action VARCHAR(50) NOT NULL,
    table_name VARCHAR(100) NOT NULL,
    record_id UUID NOT NULL,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
COMMENT ON TABLE sgpos.audit_logs IS 'Immutable log for tracking all data modifications for compliance and debugging.';


-- =============================================================================
-- Section 7: Indexes for Performance
-- Description: Strategic indexes to optimize common query patterns.
-- =============================================================================

-- Indexes on foreign keys and frequently filtered columns
CREATE INDEX idx_outlets_company_id ON sgpos.outlets(company_id);
CREATE INDEX idx_users_company_id ON sgpos.users(company_id);
CREATE INDEX idx_roles_company_id ON sgpos.roles(company_id);
CREATE INDEX idx_role_permissions_role_id ON sgpos.role_permissions(role_id);
CREATE INDEX idx_role_permissions_permission_id ON sgpos.role_permissions(permission_id);
CREATE INDEX idx_user_roles_user_id ON sgpos.user_roles(user_id);
CREATE INDEX idx_user_roles_role_id ON sgpos.user_roles(role_id);
CREATE INDEX idx_user_roles_outlet_id ON sgpos.user_roles(outlet_id);
CREATE INDEX idx_categories_company_id ON sgpos.categories(company_id);
CREATE INDEX idx_suppliers_company_id ON sgpos.suppliers(company_id);
CREATE INDEX idx_products_company_id ON sgpos.products(company_id);
CREATE INDEX idx_products_category_id ON sgpos.products(category_id);
CREATE INDEX idx_products_supplier_id ON sgpos.products(supplier_id);
CREATE INDEX idx_products_barcode ON sgpos.products(barcode) WHERE barcode IS NOT NULL;
CREATE INDEX idx_product_variants_product_id ON sgpos.product_variants(product_id);
CREATE INDEX idx_inventory_outlet_id ON sgpos.inventory(outlet_id);
CREATE INDEX idx_inventory_product_id ON sgpos.inventory(product_id);
CREATE INDEX idx_inventory_variant_id ON sgpos.inventory(variant_id);
CREATE INDEX idx_stock_movements_company_id ON sgpos.stock_movements(company_id);
CREATE INDEX idx_stock_movements_outlet_id ON sgpos.stock_movements(outlet_id);
CREATE INDEX idx_stock_movements_product_id ON sgpos.stock_movements(product_id);
CREATE INDEX idx_stock_movements_created_by_user_id ON sgpos.stock_movements(created_by_user_id);
-- FIX: Added missing index for consistency and performance.
CREATE INDEX idx_stock_movements_reference_id ON sgpos.stock_movements(reference_id);
CREATE INDEX idx_purchase_orders_company_id ON sgpos.purchase_orders(company_id);
CREATE INDEX idx_purchase_orders_outlet_id ON sgpos.purchase_orders(outlet_id);
CREATE INDEX idx_purchase_orders_supplier_id ON sgpos.purchase_orders(supplier_id);
CREATE INDEX idx_purchase_order_items_po_id ON sgpos.purchase_order_items(purchase_order_id);
CREATE INDEX idx_purchase_order_items_product_id ON sgpos.purchase_order_items(product_id);
CREATE INDEX idx_customers_company_id ON sgpos.customers(company_id);
CREATE INDEX idx_sales_transactions_company_id ON sgpos.sales_transactions(company_id);
CREATE INDEX idx_sales_transactions_outlet_id ON sgpos.sales_transactions(outlet_id);
CREATE INDEX idx_sales_transactions_transaction_date ON sgpos.sales_transactions(transaction_date DESC);
CREATE INDEX idx_sales_transactions_customer_id ON sgpos.sales_transactions(customer_id);
CREATE INDEX idx_sales_transactions_cashier_id ON sgpos.sales_transactions(cashier_id);
CREATE INDEX idx_sales_transaction_items_transaction_id ON sgpos.sales_transaction_items(sales_transaction_id);
CREATE INDEX idx_sales_transaction_items_product_id ON sgpos.sales_transaction_items(product_id);
CREATE INDEX idx_payment_methods_company_id ON sgpos.payment_methods(company_id);
CREATE INDEX idx_payments_sales_transaction_id ON sgpos.payments(sales_transaction_id);
CREATE INDEX idx_payments_payment_method_id ON sgpos.payments(payment_method_id);
CREATE INDEX idx_chart_of_accounts_company_id ON sgpos.chart_of_accounts(company_id);
CREATE INDEX idx_chart_of_accounts_parent_id ON sgpos.chart_of_accounts(parent_id);
CREATE INDEX idx_journal_entries_company_id ON sgpos.journal_entries(company_id);
CREATE INDEX idx_journal_entries_entry_date ON sgpos.journal_entries(entry_date DESC);
CREATE INDEX idx_journal_entries_reference_id ON sgpos.journal_entries(reference_id);
CREATE INDEX idx_journal_entry_lines_journal_entry_id ON sgpos.journal_entry_lines(journal_entry_id);
CREATE INDEX idx_journal_entry_lines_account_id ON sgpos.journal_entry_lines(account_id);
CREATE INDEX idx_audit_logs_company_id ON sgpos.audit_logs(company_id);
CREATE INDEX idx_audit_logs_user_id ON sgpos.audit_logs(user_id);
CREATE INDEX idx_audit_logs_record ON sgpos.audit_logs(table_name, record_id);
CREATE INDEX idx_audit_logs_created_at ON sgpos.audit_logs(created_at DESC);


-- =============================================================================
-- Section 8: Triggers and Functions
-- Description: Database-level automation for integrity and auditing.
-- =============================================================================

-- Function to automatically update the 'updated_at' timestamp on any row update.
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Generic trigger application for 'updated_at'
-- This block will create the trigger for all tables within the 'sgpos' schema
-- that have an 'updated_at' column.
DO $$
DECLARE
    t text;
BEGIN
    FOR t IN SELECT tablename FROM pg_tables WHERE schemaname = 'sgpos' AND EXISTS (SELECT 1 FROM pg_attribute WHERE attrelid = tablename::regclass AND attname = 'updated_at')
    LOOP
        EXECUTE format('CREATE TRIGGER set_updated_at_on_%I BEFORE UPDATE ON sgpos.%I FOR EACH ROW EXECUTE FUNCTION update_updated_at_column()', t, t);
    END LOOP;
END;
$$ LANGUAGE plpgsql;


-- Function to log all changes to designated tables into the audit_logs table.
-- The application should set session variables for user/company context:
-- e.g., SET sgpos.current_user_id = '...'; SET sgpos.current_company_id = '...';
CREATE OR REPLACE FUNCTION log_changes()
RETURNS TRIGGER AS $$
DECLARE
    old_data JSONB;
    new_data JSONB;
    action_type VARCHAR(50);
    current_user UUID;
    current_company UUID;
BEGIN
    -- Attempt to retrieve session variables set by the application
    BEGIN
        current_user := current_setting('sgpos.current_user_id', true)::UUID;
    EXCEPTION WHEN OTHERS THEN
        current_user := NULL;
    END;
    
    BEGIN
        current_company := current_setting('sgpos.current_company_id', true)::UUID;
    EXCEPTION WHEN OTHERS THEN
        current_company := NULL;
    END;

    IF (TG_OP = 'UPDATE') THEN
        old_data := to_jsonb(OLD);
        new_data := to_jsonb(NEW);
        action_type := 'UPDATE_' || UPPER(TG_TABLE_NAME);
        INSERT INTO sgpos.audit_logs (company_id, user_id, action, table_name, record_id, old_values, new_values)
        VALUES (current_company, current_user, action_type, TG_TABLE_NAME, OLD.id, old_data, new_data);
        RETURN NEW;
    ELSIF (TG_OP = 'DELETE') THEN
        old_data := to_jsonb(OLD);
        new_data := NULL;
        action_type := 'DELETE_' || UPPER(TG_TABLE_NAME);
        INSERT INTO sgpos.audit_logs (company_id, user_id, action, table_name, record_id, old_values, new_values)
        VALUES (current_company, current_user, action_type, TG_TABLE_NAME, OLD.id, old_data, new_data);
        RETURN OLD;
    ELSIF (TG_OP = 'INSERT') THEN
        new_data := to_jsonb(NEW);
        old_data := NULL;
        action_type := 'CREATE_' || UPPER(TG_TABLE_NAME);
        INSERT INTO sgpos.audit_logs (company_id, user_id, action, table_name, record_id, old_values, new_values)
        VALUES (current_company, current_user, action_type, TG_TABLE_NAME, NEW.id, old_data, new_data);
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Apply the audit trigger to tables that require a detailed audit trail.
-- These specific triggers must be explicitly created.
CREATE TRIGGER products_audit
AFTER INSERT OR UPDATE OR DELETE ON sgpos.products
FOR EACH ROW EXECUTE FUNCTION sgpos.log_changes();

CREATE TRIGGER customers_audit
AFTER INSERT OR UPDATE OR DELETE ON sgpos.customers
FOR EACH ROW EXECUTE FUNCTION sgpos.log_changes();

CREATE TRIGGER users_audit
AFTER INSERT OR UPDATE OR DELETE ON sgpos.users
FOR EACH ROW EXECUTE FUNCTION sgpos.log_changes();

CREATE TRIGGER sales_transactions_audit
AFTER INSERT OR UPDATE OR DELETE ON sgpos.sales_transactions
FOR EACH ROW EXECUTE FUNCTION sgpos.log_changes();

-- Add other critical tables here as needed for auditing.
-- E.g., CREATE TRIGGER payment_methods_audit AFTER INSERT OR UPDATE OR DELETE ON sgpos.payment_methods FOR EACH ROW EXECUTE FUNCTION sgpos.log_changes();
-- E.g., CREATE TRIGGER inventory_audit AFTER INSERT OR UPDATE OR DELETE ON sgpos.inventory FOR EACH ROW EXECUTE FUNCTION sgpos.log_changes();
-- E.g., CREATE TRIGGER suppliers_audit AFTER INSERT OR UPDATE OR DELETE ON sgpos.suppliers FOR EACH ROW EXECUTE FUNCTION sgpos.log_changes();
```

---
https://drive.google.com/file/d/11EUoGcc2Ooz7rfBtNPup3kDYyQbLzGCY/view?usp=sharing, https://aistudio.google.com/app/prompts?state=%7B%22ids%22:%5B%2212VGvhlsO4bTWDpTQADljLQwnQ51SA7pp%22%5D,%22action%22:%22open%22,%22userId%22:%22103961307342447084491%22,%22resourceKeys%22:%7B%7D%7D&usp=sharing, https://drive.google.com/file/d/1pBPMY3TTXyX-bu7qSeEHZ3QqivmAujF9/view?usp=sharing

