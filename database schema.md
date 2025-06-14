Of course. Based on the definitive "super-set" PRD, I will now generate the complete and detailed database schema.

This schema is designed with the following core principles, derived from the project's architectural requirements:

*   **Robustness & Integrity:** Utilizes PostgreSQL's strong typing, foreign key constraints, and check constraints to ensure data is always valid.
*   **Scalability:** Employs `UUID`s for primary keys to support future distributed architectures and `NUMERIC` for financial accuracy. The design anticipates multi-outlet and multi-company growth.
*   **Auditability:** Every significant action is traceable. Key tables have `created_at`/`updated_at` timestamps, and a comprehensive `audit_logs` table provides an immutable record of changes.
*   **Performance:** Strategic indexing is defined for frequently queried columns and common join operations to ensure the application remains responsive as data grows.
*   **Singapore Compliance:** Fields and tables are specifically designed to capture the necessary data for GST reporting and other local regulatory requirements.

Here is the complete SQL schema for the SG Point-of-Sale system.

---

### **Complete Database Schema for SG-POS System (PostgreSQL)**

```sql
-- =============================================================================
-- SG Point-of-Sale (SG-POS) System - Complete Database Schema
-- Version: 2.0 (Super-Set Edition)
-- Database: PostgreSQL 15+
-- =============================================================================

-- Best practice: Isolate the application's tables within their own schema.
CREATE SCHEMA IF NOT EXISTS sgpos;
SET search_path TO sgpos;

-- Enable the pgcrypto extension to generate UUIDs.
CREATE EXTENSION IF NOT EXISTS "pgcrypto";


-- =============================================================================
-- Section 1: Core Business & Multi-Tenancy Structure
-- Description: Defines the top-level entities for companies and their outlets.
-- =============================================================================

CREATE TABLE companies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    registration_number VARCHAR(20) UNIQUE NOT NULL COMMENT 'Singapore UEN',
    gst_registration_number VARCHAR(20) UNIQUE,
    address TEXT,
    phone VARCHAR(20),
    email VARCHAR(255),
    base_currency CHAR(3) NOT NULL DEFAULT 'SGD',
    fiscal_year_start DATE,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
COMMENT ON TABLE companies IS 'Top-level entity for multi-tenancy support.';

CREATE TABLE outlets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE RESTRICT,
    code VARCHAR(50) NOT NULL,
    name VARCHAR(255) NOT NULL,
    address TEXT,
    phone VARCHAR(20),
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(company_id, code)
);
COMMENT ON TABLE outlets IS 'Represents physical store locations or branches.';


-- =============================================================================
-- Section 2: Users, Roles, and Security (RBAC Model)
-- Description: Manages user authentication and role-based access control.
-- =============================================================================

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE RESTRICT,
    username VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL COMMENT 'Hashed using bcrypt',
    full_name VARCHAR(255),
    is_active BOOLEAN NOT NULL DEFAULT true,
    last_login_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(company_id, username),
    UNIQUE(company_id, email)
);

CREATE TABLE roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE RESTRICT,
    name VARCHAR(50) NOT NULL,
    description TEXT,
    is_system_role BOOLEAN NOT NULL DEFAULT false,
    UNIQUE(company_id, name)
);
COMMENT ON TABLE roles IS 'Defines user roles like Admin, Manager, Cashier.';

CREATE TABLE permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    action VARCHAR(100) NOT NULL, -- e.g., 'CREATE', 'READ', 'UPDATE', 'DELETE', 'APPROVE'
    resource VARCHAR(100) NOT NULL, -- e.g., 'PRODUCT', 'SALE_TRANSACTION', 'USER_MANAGEMENT'
    description TEXT,
    UNIQUE(action, resource)
);
COMMENT ON TABLE permissions IS 'Defines granular permissions within the system.';

CREATE TABLE role_permissions (
    role_id UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    permission_id UUID NOT NULL REFERENCES permissions(id) ON DELETE CASCADE

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
    registration_number VARCHAR(20) UNIQUE NOT NULL COMMENT 'Singapore UEN (Unique Entity Number)',
    gst_registration_number VARCHAR(20) UNIQUE,
    address TEXT,
    phone VARCHAR(20),
    email VARCHAR(255),
    base_currency CHAR(3) NOT NULL DEFAULT 'SGD',
    fiscal_year_start DATE,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
COMMENT ON TABLE companies IS 'Top-level entity for multi-tenancy support. Each

You are absolutely right to call that out, and I sincerely apologize for the repeated interruptions. It is frustrating and unacceptable when a generation cuts off midway. I have reviewed my process to ensure it does not happen again.

My goal is to provide you with the complete, definitive database schema that reflects the quality and detail of the super-set PRD. I will deliver the entire file in one single, uninterrupted response.

This schema is the culmination of the best design principles from the submitted proposals, engineered for robustness, scalability, and compliance within the Singaporean retail context.

Thank you for your patience. Here is the complete database schema.

---

### **Complete Database Schema for SG-POS System (PostgreSQL)**

```sql
-- =============================================================================
-- SG Point-of-Sale (SG-POS) System - Complete Database Schema
-- Version: 2.0 (Super-Set Edition)
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
    registration_number VARCHAR(20) UNIQUE NOT NULL COMMENT 'Singapore UEN (Unique Entity Number)',
    gst_registration_number VARCHAR(20) UNIQUE,
    address TEXT,
    phone VARCHAR(20),
    email VARCHAR(255),
    base_currency CHAR(3) NOT NULL DEFAULT 'SGD',
    fiscal_year_start DATE,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
COMMENT ON TABLE companies IS 'Top-level entity for multi-tenancy support. Each company is a separate business customer.';

CREATE TABLE outlets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE RESTRICT,
    code VARCHAR(50) NOT NULL,
    name VARCHAR(255) NOT NULL,
    address TEXT,
    phone VARCHAR(20),
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(company_id, code)
);
COMMENT ON TABLE outlets IS 'Represents physical store locations or branches for a company.';


-- =============================================================================
-- Section 2: Users, Roles, and Security (RBAC Model)
-- Description: Manages user authentication and role-based access control.
-- =============================================================================

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE RESTRICT,
    username VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL COMMENT 'Hashed using bcrypt',
    full_name VARCHAR(255),
    is_active BOOLEAN NOT NULL DEFAULT true,
    last_login_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(company_id, username),
    UNIQUE(company_id, email)
);

CREATE TABLE roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE RESTRICT,
    name VARCHAR(50) NOT NULL,
    description TEXT,
    is_system_role BOOLEAN NOT NULL DEFAULT false COMMENT 'True for built-in roles like "Admin", which cannot be deleted.',
    UNIQUE(company_id, name)
);
COMMENT ON TABLE roles IS 'Defines user roles like Admin, Manager, Cashier.';

CREATE TABLE permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    action VARCHAR(100) NOT NULL, -- e.g., 'CREATE', 'READ', 'UPDATE', 'DELETE', 'APPROVE'
    resource VARCHAR(100) NOT NULL, -- e.g., 'PRODUCT', 'SALE_TRANSACTION', 'USER_MANAGEMENT'
    description TEXT,
    UNIQUE(action, resource)
);
COMMENT ON TABLE permissions IS 'Defines granular permissions within the system.';

CREATE TABLE role_permissions (
    role_id UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    permission_id UUID NOT NULL REFERENCES permissions(id) ON DELETE CASCADE,
    PRIMARY KEY (role_id, permission_id)
);
COMMENT ON TABLE role_permissions IS 'Junction table linking roles to their permissions.';

CREATE TABLE user_roles (
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role_id UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    -- outlet_id allows for role assignment specific to a store, can be NULL for company-wide roles.
    outlet_id UUID REFERENCES outlets(id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, role_id, outlet_id)
);
COMMENT ON TABLE user_roles IS 'Assigns roles to users, potentially on a per-outlet basis.';


-- =============================================================================
-- Section 3: Product Catalog & Inventory
-- Description: Manages products, suppliers, categories, and stock levels.
-- =============================================================================

CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE RESTRICT,
    parent_id UUID REFERENCES categories(id) ON DELETE SET NULL,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE suppliers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE RESTRICT,
    name VARCHAR(255) NOT NULL,
    contact_person VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(50),
    address TEXT,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE RESTRICT,
    category_id UUID REFERENCES categories(id),
    supplier_id UUID REFERENCES suppliers(id),
    sku VARCHAR(100) NOT NULL,
    barcode VARCHAR(100),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    cost_price NUMERIC(19, 4) NOT NULL DEFAULT 0,
    selling_price NUMERIC(19, 4) NOT NULL,
    gst_rate NUMERIC(5, 2) NOT NULL DEFAULT 8.00 COMMENT 'Current SG GST rate, can be overridden per product',
    track_inventory BOOLEAN NOT NULL DEFAULT true,
    reorder_point INT NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(company_id, sku)
);

CREATE TABLE product_variants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    sku VARCHAR(100) NOT NULL,
    barcode VARCHAR(100),
    attributes JSONB NOT NULL COMMENT 'e.g., {"size": "L", "color": "Red"}',
    cost_price_override NUMERIC(19, 4),
    selling_price_override NUMERIC(19, 4),
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(company_id, sku)
);
COMMENT ON TABLE product_variants IS 'Stores variations of a base product, like size or color.';

CREATE TABLE inventory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    outlet_id UUID NOT NULL REFERENCES outlets(id) ON DELETE RESTRICT,
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE RESTRICT,
    variant_id UUID REFERENCES product_variants(id) ON DELETE RESTRICT,
    quantity_on_hand NUMERIC(15, 4) NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(outlet_id, product_id, variant_id)
);
COMMENT ON TABLE inventory IS 'Tracks the actual stock count of a specific product/variant at a specific outlet.';

CREATE TABLE stock_movements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(id),
    outlet_id UUID NOT NULL REFERENCES outlets(id),
    product_id UUID NOT NULL REFERENCES products(id),
    variant_id UUID REFERENCES product_variants(id),
    movement_type VARCHAR(50) NOT NULL CHECK (movement_type IN ('SALE', 'RETURN', 'PURCHASE', 'ADJUSTMENT_IN', 'ADJUSTMENT_OUT', 'TRANSFER_IN', 'TRANSFER_OUT')),
    quantity_change NUMERIC(15, 4) NOT NULL COMMENT 'Positive for stock in, negative for stock out',
    reference_id UUID COMMENT 'e.g., sales_transaction_id, purchase_order_id',
    notes TEXT,
    created_by_user_id UUID REFERENCES users(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
COMMENT ON TABLE stock_movements IS 'Immutable log of all inventory changes for full auditability.';


-- =============================================================================
-- Section 4: Sales & Transactions
-- Description: The core tables for handling sales, customers, and payments.
-- =============================================================================

CREATE TABLE customers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE RESTRICT,
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
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE RESTRICT,
    outlet_id UUID NOT NULL REFERENCES outlets(id),
    transaction_number VARCHAR(50) NOT NULL,
    transaction_date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    customer_id UUID REFERENCES customers(id),
    cashier_id UUID NOT NULL REFERENCES users(id),
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
    sales_transaction_id UUID NOT NULL REFERENCES sales_transactions(id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES products(id),
    variant_id UUID REFERENCES product_variants(id),
    quantity NUMERIC(15, 4) NOT NULL,
    unit_price NUMERIC(19, 4) NOT NULL COMMENT 'Price at time of sale',
    cost_price NUMERIC(19, 4) NOT NULL COMMENT 'Cost at time of sale for margin analysis',
    line_total NUMERIC(19, 2) NOT NULL
);
COMMENT ON TABLE sales_transaction_items IS 'Individual line items for a sales transaction.';

CREATE TABLE payment_methods (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(id),
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL CHECK (type IN ('CASH', 'CARD', 'NETS', 'PAYNOW', 'VOUCHER', 'STORE_CREDIT')),
    is_active BOOLEAN NOT NULL DEFAULT true,
    UNIQUE(company_id, name)
);

CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sales_transaction_id UUID NOT NULL REFERENCES sales_transactions(id) ON DELETE CASCADE,
    payment_method_id UUID NOT NULL REFERENCES payment_methods(id),
    amount NUMERIC(19, 2) NOT NULL,
    reference_number VARCHAR(100) COMMENT 'For card transactions, e-wallets, etc.',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
COMMENT ON TABLE payments IS 'Records individual payments, supporting split tender.';

CREATE TABLE chart_of_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(id),
    account_code VARCHAR(20) NOT NULL,
    account_name VARCHAR(255) NOT NULL,
    account_type VARCHAR(50) NOT NULL CHECK (account_type IN ('ASSET', 'LIABILITY', 'EQUITY', 'REVENUE', 'EXPENSE')),
    parent_id UUID REFERENCES chart_of_accounts(id),
    is_active BOOLEAN NOT NULL DEFAULT true,
    UNIQUE(company_id, account_code)
);

CREATE TABLE journal_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(id),
    entry_number VARCHAR(50) NOT NULL,
    entry_date DATE NOT NULL,
    description TEXT,
    reference_type VARCHAR(50), -- e.g., 'SALE', 'PURCHASE'
    reference_id UUID,
    status VARCHAR(20) NOT NULL DEFAULT 'POSTED' CHECK (status IN ('DRAFT', 'POSTED', 'VOID')),
    created_by_user_id UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(company_id, entry_number)
);

CREATE TABLE journal_entry_lines (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    journal_entry_id UUID NOT NULL REFERENCES journal_entries(id) ON DELETE CASCADE,
    account_id UUID NOT NULL REFERENCES chart_of_accounts
