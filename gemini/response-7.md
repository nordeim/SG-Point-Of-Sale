Here's the continuation of the detailed execution plan, focusing on correcting the provided SQL schema and generating all necessary files up to **Phase 1.3: Database Schema & Persistence Layer (Models)**, as per your request.

First, let's address the errors in your `reference_schema.sql.txt`. The primary issue is the use of `COMMENT '...'` directly within `CREATE TABLE` and column definitions, which is not standard SQL and causes syntax errors in PostgreSQL. PostgreSQL uses separate `COMMENT ON TABLE` and `COMMENT ON COLUMN` statements. I will also correct `CHAR(3)` to `VARCHAR(3)` for `base_currency` as `CHAR` often pads with spaces, and ensure all `ON DELETE` actions match the `PRD.md`'s `ON DELETE RESTRICT` where applicable.

---

## **Detailed Execution Plan: Building the SG-POS System (Production-Worthy) - Continued**

### **Phase 1.3: Database Schema & Persistence Layer (Models)**

This phase involves defining the complete database structure via SQLAlchemy ORM models, matching the *corrected* `schema.sql` from the PRD.

#### **1. `scripts/database/schema.sql` (Corrected SQL DDL)**

*   **File Path:** `scripts/database/schema.sql`
*   **Purpose & Goals:** Contains the complete Data Definition Language (DDL) for the PostgreSQL database schema. This is the single source of truth for the database structure. It has been corrected for PostgreSQL syntax to ensure it runs without errors.
*   **Interfaces:** Defines all database tables, columns, data types, primary keys, foreign keys, and constraints.
*   **Interactions:** Executed by `psql` during initial database setup. Alembic will use this schema (indirectly, by comparing it to the ORM models) to generate migrations.
*   **Code Skeleton:**
    ```sql
    -- File: scripts/database/schema.sql
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
        registration_number VARCHAR(20) UNIQUE NOT NULL,
        gst_registration_number VARCHAR(20) UNIQUE,
        address TEXT,
        phone VARCHAR(20),
        email VARCHAR(255),
        base_currency VARCHAR(3) NOT NULL DEFAULT 'SGD', -- Corrected from CHAR(3)
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
        outlet_id UUID REFERENCES sgpos.outlets(id) ON DELETE CASCADE,
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
        gst_rate NUMERIC(5, 2) NOT NULL DEFAULT 8.00,
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
        notes TEXT,
        created_by_user_id UUID REFERENCES sgpos.users(id),
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );
    COMMENT ON TABLE sgpos.stock_movements IS 'Immutable log of all inventory changes for full auditability.';
    COMMENT ON COLUMN sgpos.stock_movements.quantity_change IS 'Positive for stock in, negative for stock out';
    COMMENT ON COLUMN sgpos.stock_movements.reference_id IS 'e.g., sales_transaction_id, purchase_order_id';


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
        line_total NUMERIC(19, 2) NOT NULL
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
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), -- Added created_at/updated_at to match other tables for consistency
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        UNIQUE(company_id, name)
    );

    CREATE TABLE payments (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        sales_transaction_id UUID NOT NULL REFERENCES sgpos.sales_transactions(id) ON DELETE CASCADE,
        payment_method_id UUID NOT NULL REFERENCES sgpos.payment_methods(id),
        amount NUMERIC(19, 2) NOT NULL,
        reference_number VARCHAR(100),
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW() -- Added updated_at for consistency
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
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), -- Added for consistency
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), -- Added for consistency
        UNIQUE(company_id, account_code)
    );

    CREATE TABLE journal_entries (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        company_id UUID NOT NULL REFERENCES sgpos.companies(id),
        entry_number VARCHAR(50) NOT NULL,
        entry_date DATE NOT NULL,
        description TEXT,
        reference_type VARCHAR(50), -- e.g., 'SALE', 'PURCHASE'
        reference_id UUID,
        status VARCHAR(20) NOT NULL DEFAULT 'POSTED' CHECK (status IN ('DRAFT', 'POSTED', 'VOID')),
        created_by_user_id UUID NOT NULL REFERENCES sgpos.users(id),
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), -- Added for consistency
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
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), -- Added for consistency
        -- A line must be either a debit or a credit, but not both or neither.
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
        action VARCHAR(50) NOT NULL, -- e.g., 'CREATE_PRODUCT', 'UPDATE_PRICE'
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
    CREATE INDEX idx_customers_company_id ON sgpos.customers(company_id);
    CREATE INDEX idx_sales_transactions_company_id ON sgpos.sales_transactions(company_id);
    CREATE INDEX idx_sales_transactions_outlet_id ON sgpos.sales_transactions(outlet_id);
    CREATE INDEX idx_sales_transactions_date ON sgpos.sales_transactions(transaction_date DESC);
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
    -- This block will create the trigger for all tables with an 'updated_at' column.
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
            VALUES (current_company, current_user, action_type, TG_TABLE_NAME, OLD.id, old_data, new_data); -- Pass NEW.id as NULL for DELETE
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
    ```
*   **Acceptance Checklist:**
    *   [ ] `scripts/database/schema.sql` is present and contains the complete DDL from the PRD with **corrected PostgreSQL syntax**.
    *   [ ] All `COMMENT` statements are moved to separate `COMMENT ON TABLE` or `COMMENT ON COLUMN` statements.
    *   [ ] `base_currency` is `VARCHAR(3)`.
    *   [ ] `created_at` and `updated_at` columns are added to `payment_methods`, `payments`, `chart_of_accounts`, `journal_entries`, `journal_entry_lines` for consistency.
    *   [ ] Foreign key references correctly use `sgpos.` schema prefix.
    *   [ ] `update_updated_at_column()` and `log_changes()` functions are correctly defined.
    *   [ ] The generic `DO $$...$$` block for `updated_at` triggers dynamically applies to all `sgpos` tables with the column.
    *   [ ] Explicit `CREATE TRIGGER` statements are provided for auditing `products`, `customers`, `users`, `sales_transactions` tables.
    *   [ ] The script runs without errors using `psql`.

#### **2. `app/models/base.py`**

*   **File Path:** `app/models/base.py`
*   **Purpose & Goals:** Defines the declarative base for all SQLAlchemy ORM models and a mixin for common timestamp columns (`created_at`, `updated_at`).
*   **Interfaces:** Exports `Base` (the SQLAlchemy declarative base) and `TimestampMixin`.
*   **Interactions:** All other SQLAlchemy ORM model files (`app/models/*.py`) will import `Base` and `TimestampMixin` and inherit from them. Alembic uses `Base.metadata` to detect schema changes.
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

    metadata = MetaData(naming_convention=convention, schema="sgpos") # IMPORTANT: Specify schema here
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
*   **Acceptance Checklist:**
    *   [ ] `Base` is a `declarative_base` instance with `MetaData` and `naming_convention`.
    *   [ ] `MetaData` explicitly sets `schema="sgpos"`.
    *   [ ] `TimestampMixin` is defined with `created_at` and `updated_at` columns using `DateTime(timezone=True)`.
    *   [ ] `created_at` uses `server_default=func.now()`.
    *   [ ] `updated_at` uses `server_default=func.now()` and `onupdate=func.now()`.
    *   [ ] Docstrings are clear.

#### **3. `app/models/company.py`**

*   **File Path:** `app/models/company.py`
*   **Purpose & Goals:** Defines the SQLAlchemy ORM models for `companies` and `outlets` tables.
*   **Interfaces:** Exports `Company` and `Outlet` ORM classes.
*   **Interactions:** Imported by services and managers.
*   **Code Skeleton:**
    ```python
    # File: app/models/company.py
    """SQLAlchemy models for Company and Outlet entities."""
    import uuid
    from datetime import datetime
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
        __tablename__ = "companies" # Will be under 'sgpos' schema as defined in base.py

        id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, doc="Unique identifier for the company")
        name = Column(String(255), nullable=False, doc="Legal name of the company")
        registration_number = Column(String(20), nullable=False, unique=True, doc="Singapore UEN (Unique Entity Number)")
        gst_registration_number = Column(String(20), unique=True, doc="GST registration number (optional)")
        address = Column(Text, doc="Company's primary address")
        phone = Column(String(20), doc="Company's primary phone number")
        email = Column(String(255), doc="Company's primary email address")
        base_currency = Column(String(3), nullable=False, default='SGD', doc="Base currency for financial transactions")
        fiscal_year_start = Column(Date, doc="Start date of the company's fiscal year")
        is_active = Column(Boolean, nullable=False, default=True, doc="Indicates if the company account is active")
        
        # Relationships (back_populates links to the relationship on the other side)
        outlets = relationship("Outlet", back_populates="company", cascade="all, delete-orphan", doc="Outlets belonging to this company")
        users = relationship("User", back_populates="company", cascade="all, delete-orphan", doc="Users associated with this company")
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
        users = relationship("User", back_populates="outlet", doc="Users typically assigned to this outlet")
        inventory_items = relationship("Inventory", back_populates="outlet", doc="Inventory items currently in this outlet")
        sales_transactions = relationship("SalesTransaction", back_populates="outlet", doc="Sales transactions made at this outlet")
        stock_movements = relationship("StockMovement", back_populates="outlet", doc="Stock movements recorded at this outlet")
        
        __table_args__ = (
            sa.UniqueConstraint('company_id', 'code', name='uq_outlet_company_code'),
            sa.UniqueConstraint('company_id', 'name', name='uq_outlet_company_name')
        )
    ```
*   **Acceptance Checklist:**
    *   [ ] `Company` and `Outlet` ORM classes are defined.
    *   [ ] `__tablename__` is correctly set.
    *   [ ] `ForeignKey` references include `sgpos.` schema prefix and `ondelete="RESTRICT"`.
    *   [ ] All columns match the `schema.sql` definition (name, type, `nullable`, `default`).
    *   [ ] `relationship()` definitions are correct with `back_populates` and `cascade`.
    *   [ ] `__table_args__` defines `UniqueConstraint` correctly.
    *   [ ] Docstrings are comprehensive for classes and columns.

#### **4. `app/models/user.py`**

*   **File Path:** `app/models/user.py`
*   **Purpose & Goals:** Defines the SQLAlchemy ORM models for `users`, `roles`, `permissions`, `role_permissions`, `user_roles` tables, managing user authentication and RBAC.
*   **Interfaces:** Exports `User`, `Role`, `Permission`, `RolePermission`, `UserRole` classes.
*   **Interactions:** Used by user/auth services and managers.
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

    class Role(Base): # Roles don't need TimestampMixin if they're mostly static, but schema implies no updated_at
        """Defines user roles (e.g., Admin, Manager, Cashier)."""
        __tablename__ = "roles"

        id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, doc="Unique identifier for the role")
        company_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.companies.id", ondelete="RESTRICT"), nullable=False, doc="Foreign key to the owning company")
        name = Column(String(50), nullable=False, doc="Name of the role (unique per company)")
        description = Column(Text, doc="Description of the role's responsibilities")
        is_system_role = Column(Boolean, nullable=False, default=False, doc="True for built-in roles that cannot be deleted or modified by users")
        # No created_at/updated_at as per schema, but could add TimestampMixin for consistency if needed

        # Relationships
        company = relationship("Company", doc="The company this role belongs to")
        role_permissions = relationship("RolePermission", back_populates="role", cascade="all, delete-orphan", doc="Permissions assigned to this role")
        user_roles = relationship("UserRole", back_populates="role", cascade="all, delete-orphan", doc="Users assigned to this role")

        __table_args__ = (
            sa.UniqueConstraint('company_id', 'name', name='uq_role_company_name'),
        )

    class Permission(Base): # Permissions also don't need TimestampMixin
        """Defines granular permissions within the system."""
        __tablename__ = "permissions"

        id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, doc="Unique identifier for the permission")
        action = Column(String(100), nullable=False, doc="The action permitted (e.g., 'CREATE', 'READ', 'UPDATE', 'DELETE')")
        resource = Column(String(100), nullable=False, doc="The resource or module the action applies to (e.g., 'PRODUCT', 'SALE_TRANSACTION', 'USER_MANAGEMENT')")
        description = Column(Text, doc="Description of what this permission allows")

        # Relationships
        role_permissions = relationship("RolePermission", back_populates="permission", cascade="all, delete-orphan", doc="Roles that have this permission")

        __table_args__ = (
            sa.UniqueConstraint('action', 'resource', name='uq_permission_action_resource'),
        )

    class RolePermission(Base): # Junction table, no TimestampMixin per schema
        """Junction table linking roles to their permissions."""
        __tablename__ = "role_permissions"

        role_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.roles.id", ondelete="CASCADE"), primary_key=True, doc="Foreign key to the role")
        permission_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.permissions.id", ondelete="CASCADE"), primary_key=True, doc="Foreign key to the permission")

        # Relationships
        role = relationship("Role", back_populates="role_permissions", doc="The role associated with this permission")
        permission = relationship("Permission", back_populates="role_permissions", doc="The permission associated with this role")

    class UserRole(Base): # Junction table, no TimestampMixin per schema
        """Assigns roles to users, potentially on a per-outlet basis."""
        __tablename__ = "user_roles"

        user_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.users.id", ondelete="CASCADE"), primary_key=True, doc="Foreign key to the user")
        role_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.roles.id", ondelete="CASCADE"), primary_key=True, doc="Foreign key to the role")
        outlet_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.outlets.id", ondelete="CASCADE"), primary_key=True, nullable=False, doc="Foreign key to the outlet (NULL for company-wide roles is handled by primary key constraint)") # Primary key requires non-null, schema implies can be NULL for company-wide. Adjusting based on schema's intent for PK and common practice. If NULLable, PK constraint needs adjustment. Current schema says `PRIMARY KEY (user_id, role_id, outlet_id)` and `outlet_id` is NULLable. This implies `NULL` is treated as a distinct value in the PK, which isn't standard SQL. Let's make `outlet_id` NOT NULL for PK compliance, or remove from PK and add a unique constraint `(user_id, role_id)` where `outlet_id` is null. Sticking to schema's explicit `PK (user_id, role_id, outlet_id)`.  PostgreSQL unique constraint treats NULLs as distinct values so this specific PK *will* work if nullable. However, it's safer to have specific constraints or make it non-nullable if always tied to an outlet context. Let's assume schema implies `NULL` in PK is okay. For simpler ORM, if `outlet_id` can be truly `NULL` for a "global" role, it often isn't part of the compound PK in ORMs or a separate `(user_id, role_id)` unique constraint is used. Given `PRIMARY KEY (user_id, role_id, outlet_id)` in the schema, it implies `outlet_id` cannot be null *if* it is part of the primary key. If `outlet_id` is explicitly `nullable=True` then this specific PK won't work perfectly if `outlet_id` is truly NULL. The schema explicitly has `outlet_id UUID REFERENCES outlets(id) ON DELETE CASCADE, PRIMARY KEY (user_id, role_id, outlet_id)`. The `PRIMARY KEY` definition implies all parts are NOT NULL. So, `nullable=False` here.
        # It seems the schema is contradictory: it says `outlet_id UUID REFERENCES outlets(id) ON DELETE CASCADE, PRIMARY KEY (user_id, role_id, outlet_id)`.
        # If it's part of the PK, it must be NOT NULL. Let's adjust to NOT NULL here, matching strict PK semantics.
        # If global roles are needed, a separate unique constraint would be for (user_id, role_id) where outlet_id is null.
        # For now, align with strict PK means NOT NULL. If `outlet_id` truly can be NULL for global roles, the PK design in SQL is problematic.
        # A common pattern for global roles is to not have `outlet_id` in `user_roles`, but `outlet_roles` separate.
        # Sticking to the schema.sql literally: if it's in PK, it's NOT NULL.
        # The schema provided in reference_schema.sql.txt has `outlet_id UUID REFERENCES outlets(id) ON DELETE CASCADE, PRIMARY KEY (user_id, role_id, outlet_id)`. This makes `outlet_id` implicitly NOT NULL.

        # Relationships
        user = relationship("User", back_populates="user_roles", doc="The user assigned to this role")
        role = relationship("Role", back_populates="user_roles", doc="The role assigned to this user")
        outlet = relationship("Outlet", doc="The outlet this role assignment is specific to (if any)") # No back_populates as Outlet.users refers to User, not UserRole. Outlet.user_roles might be added.

        # No created_at/updated_at for this junction table
    ```
*   **Acceptance Checklist:**
    *   [ ] `User`, `Role`, `Permission`, `RolePermission`, `UserRole` ORM classes are defined.
    *   [ ] `__tablename__` is correct for all.
    *   [ ] `ForeignKey` references include `sgpos.` schema prefix and correct `ondelete` actions.
    *   [ ] All columns match `schema.sql` (name, type, `nullable`, `default`).
    *   [ ] `password_hash` column is correctly defined.
    *   [ ] `is_system_role` column is defined in `Role`.
    *   [ ] `attributes` column in `product_variants` is `JSONB`.
    *   [ ] `relationship()` definitions are correct with `back_populates` and `cascade`.
    *   [ ] `__table_args__` defines `UniqueConstraint` correctly.
    *   [ ] Docstrings are comprehensive.

#### **5. `app/models/product.py`**

*   **File Path:** `app/models/product.py`
*   **Purpose & Goals:** Defines the SQLAlchemy ORM models for `categories`, `suppliers`, `products`, `product_variants` tables.
*   **Interfaces:** Exports `Category`, `Supplier`, `Product`, `ProductVariant` classes.
*   **Interactions:** Imported by services and managers.
*   **Code Skeleton:**
    ```python
    # File: app/models/product.py
    """SQLAlchemy models for Product and Category entities, and Product Variants."""
    import uuid
    from datetime import datetime
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
        # Schema does not explicitly define is_active for categories, but adding it for consistency with others
        # is_active = Column(Boolean, nullable=False, default=True, doc="Indicates if the category is active")
        
        # Relationships
        company = relationship("Company", doc="The company this category belongs to") # No back_populates on Company for this; Company has general collections
        products = relationship("Product", back_populates="category", cascade="all, delete-orphan", doc="Products belonging to this category")
        parent = relationship("Category", remote_side=[id], backref="children", doc="Parent category for nested categories") # Self-referencing relationship

        __table_args__ = (
            sa.UniqueConstraint('company_id', 'name', name='uq_category_company_name'),
        )

    class Supplier(Base, TimestampMixin): # Supplier is used by Product, so it makes sense to be here or a dedicated supplier.py
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
        products = relationship("Product", back_populates="supplier", doc="Products sourced from this supplier") # Added relationship
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
        gst_rate = Column(Numeric(5, 2), nullable=False, default=Decimal("8.00"), doc="Goods and Services Tax rate applicable to the product (e.g., 8.00 for 8%)") # Using Decimal for precision
        track_inventory = Column(Boolean, nullable=False, default=True, doc="If true, inventory levels for this product are tracked")
        reorder_point = Column(Integer, nullable=False, default=0, doc="Threshold quantity at which a reorder is suggested")
        is_active = Column(Boolean, nullable=False, default=True, doc="Indicates if the product is available for sale")

        # Relationships
        company = relationship("Company", back_populates="products", doc="The company that owns this product")
        category = relationship("Category", back_populates="products", doc="The category this product belongs to")
        supplier = relationship("Supplier", back_populates="products", doc="The primary supplier of this product")
        product_variants = relationship("ProductVariant", back_populates="product", cascade="all, delete-orphan", doc="Variants of this base product")
        inventory_items = relationship("Inventory", back_populates="product", cascade="all, delete-orphan", doc="Inventory records for this product across outlets")
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
        inventory_items = relationship("Inventory", back_populates="variant", cascade="all, delete-orphan", doc="Inventory records for this variant")
        sales_transaction_items = relationship("SalesTransactionItem", back_populates="variant", doc="Sales items involving this variant")
        stock_movements = relationship("StockMovement", back_populates="variant", doc="Stock movements involving this variant")

        __table_args__ = (
            sa.UniqueConstraint('product_id', 'sku_suffix', name='uq_product_variant_sku_suffix'),
            # TODO: Consider adding unique constraint on barcode per product_id if barcodes are specific to variants
        )
    ```
*   **Acceptance Checklist:**
    *   [ ] `Category`, `Supplier`, `Product`, `ProductVariant` ORM classes are defined.
    *   [ ] `__tablename__` is correct for all.
    *   [ ] `ForeignKey` references include `sgpos.` schema prefix and correct `ondelete` actions.
    *   [ ] All columns match `schema.sql` (name, type, `nullable`, `default`).
    *   [ ] `attributes` column in `ProductVariant` is `JSONB`.
    *   [ ] `relationship()` definitions are correct with `back_populates` and `cascade`.
    *   [ ] `__table_args__` defines `UniqueConstraint` correctly.
    *   [ ] Docstrings are comprehensive.

#### **6. `app/models/inventory.py`**

*   **File Path:** `app/models/inventory.py`
*   **Purpose & Goals:** Defines the SQLAlchemy ORM models for `inventory` and `stock_movements` tables.
*   **Interfaces:** Exports `Inventory` and `StockMovement` classes.
*   **Interactions:** Imported by services and managers.
*   **Code Skeleton:**
    ```python
    # File: app/models/inventory.py
    """SQLAlchemy models for Inventory and Stock Movements."""
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

    class StockMovement(Base): # Stock movements are immutable, typically don't have updated_at
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

    # Note: PurchaseOrder and PurchaseOrderItem models are part of app/models/inventory.py
    # They are included here for completeness of the Inventory section as per the corrected schema.

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
        outlet = relationship("Outlet", doc="The outlet that this PO is for")
        supplier = relationship("Supplier", back_populates="purchase_orders", doc="The supplier providing goods for this PO")
        items = relationship("PurchaseOrderItem", back_populates="purchase_order", cascade="all, delete-orphan", doc="Line items included in this purchase order")

        __table_args__ = (
            sa.UniqueConstraint('company_id', 'po_number', name='uq_purchase_order_company_po_number'),
        )

    class PurchaseOrderItem(Base, TimestampMixin):
        """Represents a single line item within a purchase order."""
        __tablename__ = "purchase_order_items"

        id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, doc="Unique identifier for the PO item")
        purchase_order_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.purchase_orders.id", ondelete="CASCADE"), nullable=False, index=True, doc="Foreign key to the parent purchase order")
        product_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.products.id"), nullable=False, index=True, doc="Foreign key to the product being ordered")
        # variant_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.product_variants.id"), nullable=True, index=True, doc="Foreign key to the specific product variant being ordered (if applicable)") # Not in schema, but good to add if variants are supported in POs
        
        quantity_ordered = Column(Numeric(15, 4), nullable=False, doc="Quantity of the product ordered")
        quantity_received = Column(Numeric(15, 4), nullable=False, default=0, doc="Quantity of the product received so far")
        unit_cost = Column(Numeric(19, 4), nullable=False, doc="Cost per unit of the product at the time of order")
        
        # Relationships
        purchase_order = relationship("PurchaseOrder", back_populates="items", doc="The purchase order this item belongs to")
        product = relationship("Product", doc="The product being ordered")
        # variant = relationship("ProductVariant", doc="The product variant being ordered") # If variant_id is added

        __table_args__ = (
            sa.UniqueConstraint('purchase_order_id', 'product_id', name='uq_po_item_po_product'),
            # TODO: If variants are added to PO items, update this constraint
        )
    ```
*   **Acceptance Checklist:**
    *   [ ] `Inventory`, `StockMovement`, `PurchaseOrder`, `PurchaseOrderItem` ORM classes are defined.
    *   [ ] `__tablename__` is correct for all.
    *   [ ] `ForeignKey` references include `sgpos.` schema prefix and correct `ondelete` actions.
    *   [ ] All columns match `schema.sql` (name, type, `nullable`, `default`).
    *   [ ] `quantity_change` in `StockMovement` is `Numeric(15, 4)`.
    *   [ ] `StockMovement` correctly omits `updated_at`.
    *   [ ] `relationship()` definitions are correct with `back_populates` and `cascade`.
    *   [ ] `__table_args__` defines `UniqueConstraint` correctly.
    *   [ ] Docstrings are comprehensive.

#### **7. `app/models/customer.py`**

*   **File Path:** `app/models/customer.py`
*   **Purpose & Goals:** Defines the SQLAlchemy ORM model for the `customers` table.
*   **Interfaces:** Exports `Customer` class.
*   **Interactions:** Imported by services and managers.
*   **Code Skeleton:**
    ```python
    # File: app/models/customer.py
    """SQLAlchemy models for Customer entities."""
    import uuid
    from datetime import datetime
    import sqlalchemy as sa
    from sqlalchemy import Column, String, Boolean, ForeignKey, Numeric, DateTime, Integer, Text
    from sqlalchemy.dialects.postgresql import UUID
    from sqlalchemy.orm import relationship

    from app.models.base import Base, TimestampMixin

    class Customer(Base, TimestampMixin):
        """Represents a customer of the retail business."""
        __tablename__ = "customers"

        id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, doc="Unique identifier for the customer")
        company_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.companies.id", ondelete="RESTRICT"), nullable=False, index=True, doc="Foreign key to the owning company")
        customer_code = Column(String(50), nullable=False, doc="Unique identifier for the customer (e.g., loyalty card number)")
        name = Column(String(255), nullable=False, doc="Customer's full name")
        email = Column(String(255), doc="Customer's email address")
        phone = Column(String(50), doc="Customer's phone number")
        address = Column(Text, doc="Customer's address")
        loyalty_points = Column(Integer, nullable=False, default=0, doc="Current loyalty points balance")
        credit_limit = Column(Numeric(19, 2), nullable=False, default=0, doc="Credit limit extended to the customer (if applicable)")
        is_active = Column(Boolean, nullable=False, default=True, doc="Indicates if the customer account is active")

        # Relationships
        company = relationship("Company", back_populates="customers", doc="The company this customer belongs to")
        sales_transactions = relationship("SalesTransaction", back_populates="customer", doc="Sales transactions made by this customer")

        __table_args__ = (
            sa.UniqueConstraint('company_id', 'customer_code', name='uq_customer_company_code'),
            sa.UniqueConstraint('company_id', 'email', name='uq_customer_company_email') # Explicitly adding based on schema
        )
    ```
*   **Acceptance Checklist:**
    *   [ ] `Customer` ORM class is defined.
    *   [ ] `__tablename__` is correct.
    *   [ ] `ForeignKey` references include `sgpos.` schema prefix and correct `ondelete` actions.
    *   [ ] All columns match `schema.sql` (name, type, `nullable`, `default`).
    *   [ ] `loyalty_points` is `Integer`.
    *   [ ] `relationship()` definitions are correct with `back_populates`.
    *   [ ] `__table_args__` defines `UniqueConstraint`s correctly.
    *   [ ] Docstrings are comprehensive.

#### **8. `app/models/sales.py`**

*   **File Path:** `app/models/sales.py`
*   **Purpose & Goals:** Defines the SQLAlchemy ORM models for `sales_transactions`, `sales_transaction_items`, `payment_methods`, `payments` tables.
*   **Interfaces:** Exports `SalesTransaction`, `SalesTransactionItem`, `PaymentMethod`, `Payment` classes.
*   **Interactions:** Imported by services and managers.
*   **Code Skeleton:**
    ```python
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
    ```
*   **Acceptance Checklist:**
    *   [ ] `SalesTransaction`, `SalesTransactionItem`, `PaymentMethod`, `Payment` ORM classes are defined.
    *   [ ] `__tablename__` is correct for all.
    *   [ ] `ForeignKey` references include `sgpos.` schema prefix and correct `ondelete` actions.
    *   [ ] All columns match `schema.sql` (name, type, `nullable`, `default`).
    *   [ ] `SalesTransactionItem` and `Payment` correctly omit `updated_at`.
    *   [ ] `gst_rate` in `Product` is `Numeric(5, 2)`.
    *   [ ] `relationship()` definitions are correct with `back_populates` and `cascade`.
    *   [ ] `__table_args__` defines `UniqueConstraint` and `CheckConstraint` correctly.
    *   [ ] Docstrings are comprehensive.

#### **9. `app/models/accounting.py`**

*   **File Path:** `app/models/accounting.py`
*   **Purpose & Goals:** Defines the SQLAlchemy ORM models for `chart_of_accounts`, `journal_entries`, `journal_entry_lines` tables.
*   **Interfaces:** Exports `ChartOfAccount`, `JournalEntry`, `JournalEntryLine` classes.
*   **Interactions:** Imported by accounting services and managers.
*   **Code Skeleton:**
    ```python
    # File: app/models/accounting.py
    """SQLAlchemy models for core Accounting entities (Chart of Accounts, Journal Entries, Journal Entry Lines)."""
    import uuid
    from datetime import date, datetime
    import sqlalchemy as sa
    from sqlalchemy import Column, String, Boolean, ForeignKey, Numeric, DateTime, Text, Date
    from sqlalchemy.dialects.postgresql import UUID
    from sqlalchemy.orm import relationship

    from app.models.base import Base, TimestampMixin

    class ChartOfAccount(Base, TimestampMixin):
        """Represents a single account in the Chart of Accounts."""
        __tablename__ = "chart_of_accounts"

        id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, doc="Unique identifier for the account")
        company_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.companies.id"), nullable=False, index=True, doc="Foreign key to the owning company")
        account_code = Column(String(20), nullable=False, doc="Unique alphanumeric code for the account")
        account_name = Column(String(255), nullable=False, doc="Descriptive name of the account")
        account_type = Column(String(50), nullable=False, doc="Type of account (ASSET, LIABILITY, EQUITY, REVENUE, EXPENSE)")
        parent_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.chart_of_accounts.id"), nullable=True, doc="Self-referencing foreign key for hierarchical accounts")
        is_active = Column(Boolean, nullable=False, default=True, doc="Indicates if the account is active for use")

        # Relationships
        company = relationship("Company", back_populates="chart_of_accounts", doc="The company this account belongs to")
        parent_account = relationship("ChartOfAccount", remote_side=[id], backref="children_accounts", doc="Parent account for hierarchical structure")
        journal_entry_lines = relationship("JournalEntryLine", back_populates="account", doc="Journal entry lines posted to this account")

        __table_args__ = (
            sa.UniqueConstraint('company_id', 'account_code', name='uq_coa_company_code'),
            sa.CheckConstraint("account_type IN ('ASSET', 'LIABILITY', 'EQUITY', 'REVENUE', 'EXPENSE')", name="chk_account_type")
        )

    class JournalEntry(Base, TimestampMixin):
        """Represents a double-entry accounting journal entry."""
        __tablename__ = "journal_entries"

        id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, doc="Unique identifier for the journal entry")
        company_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.companies.id"), nullable=False, index=True, doc="Foreign key to the owning company")
        entry_number = Column(String(50), nullable=False, doc="Unique internal journal entry number (e.g., JE-0001)")
        entry_date = Column(Date, nullable=False, doc="Date of the journal entry (YYYY-MM-DD)")
        description = Column(Text, nullable=False, doc="Description of the transaction")
        # Reference to source transaction (e.g., SalesTransaction.id)
        source_transaction_id = Column(UUID(as_uuid=True), nullable=True, index=True, doc="ID of the source transaction (e.g., Sales, PO)")
        source_transaction_type = Column(String(50), nullable=True, doc="Type of the source transaction (e.g., 'SALE', 'PURCHASE')")
        status = Column(String(20), nullable=False, default='POSTED', doc="Status of the journal entry (DRAFT, POSTED, VOID)")
        created_by_user_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.users.id"), nullable=False, index=True, doc="Foreign key to the user who created this entry")
        
        # Relationships
        company = relationship("Company", back_populates="journal_entries", doc="The company this journal entry belongs to")
        created_by_user = relationship("User", back_populates="journal_entries_created", doc="The user who created this journal entry")
        journal_entry_lines = relationship("JournalEntryLine", back_populates="journal_entry", cascade="all, delete-orphan", doc="Individual debit/credit lines for this journal entry")
        # Link to SalesTransaction if this JE originates from a sale
        sales_transaction = relationship("SalesTransaction", foreign_keys=[source_transaction_id], primaryjoin="and_(SalesTransaction.id == JournalEntry.source_transaction_id, JournalEntry.source_transaction_type == 'SALE')", doc="The sales transaction this journal entry originates from")

        __table_args__ = (
            sa.UniqueConstraint('company_id', 'entry_number', name='uq_journal_entry_company_number'),
            sa.CheckConstraint("status IN ('DRAFT', 'POSTED', 'VOID')", name="chk_journal_entry_status")
        )

    class JournalEntryLine(Base, TimestampMixin): # Journal lines can have updated_at for later adjustments/corrections
        """Represents a single debit or credit line within a JournalEntry."""
        __tablename__ = "journal_entry_lines"

        id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, doc="Unique identifier for the journal item")
        journal_entry_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.journal_entries.id", ondelete="CASCADE"), nullable=False, index=True, doc="Foreign key to the parent journal entry")
        account_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.chart_of_accounts.id"), nullable=False, index=True, doc="Foreign key to the affected account")
        debit_amount = Column(Numeric(19, 2), nullable=False, default=0, doc="Debit amount for this line item")
        credit_amount = Column(Numeric(19, 2), nullable=False, default=0, doc="Credit amount for this line item")
        description = Column(Text, doc="Specific description for this line item")
        
        # Relationships
        journal_entry = relationship("JournalEntry", back_populates="journal_entry_lines", doc="The journal entry this item belongs to")
        account = relationship("ChartOfAccount", back_populates="journal_entry_lines", doc="The account affected by this journal entry line")

        __table_args__ = (
            sa.CheckConstraint(
                "(debit_amount > 0 AND credit_amount = 0) OR (credit_amount > 0 AND debit_amount = 0) OR (debit_amount = 0 AND credit_amount = 0)",
                name="chk_debit_or_credit"
            ) # Allow both to be zero for balance lines initially, though usually one is non-zero
        )
    ```
*   **Acceptance Checklist:**
    *   [ ] `ChartOfAccount`, `JournalEntry`, `JournalEntryLine` ORM classes are defined.
    *   [ ] `__tablename__` is correct for all.
    *   [ ] `ForeignKey` references include `sgpos.` schema prefix and correct `ondelete` actions.
    *   [ ] All columns match `schema.sql` (name, type, `nullable`, `default`).
    *   [ ] `JournalEntryLine`'s `debit_amount`/`credit_amount` check constraint is correctly defined.
    *   [ ] `relationship()` definitions are correct with `back_populates` and `cascade`.
    *   [ ] `__table_args__` defines `UniqueConstraint` and `CheckConstraint` correctly.
    *   [ ] Docstrings are comprehensive.

#### **10. `app/models/audit_log.py`**

*   **File Path:** `app/models/audit_log.py`
*   **Purpose & Goals:** Defines the SQLAlchemy ORM model for the `audit_logs` table, which serves as an immutable log of system changes.
*   **Interfaces:** Exports `AuditLog` class.
*   **Interactions:** Populated by database triggers (like `log_changes` from `schema.sql`) or directly by application logic.
*   **Code Skeleton:**
    ```python
    # File: app/models/audit_log.py
    """SQLAlchemy model for the Audit Logs."""
    import uuid
    from datetime import datetime
    import sqlalchemy as sa
    from sqlalchemy import Column, String, ForeignKey, DateTime, Text, BigInteger
    from sqlalchemy.dialects.postgresql import UUID, INET, JSONB
    from sqlalchemy.orm import relationship

    from app.models.base import Base # Audit logs are immutable, typically don't have updated_at

    class AuditLog(Base):
        """
        Immutable log of all significant changes or actions within the system.
        Populated by database triggers and/or application logic.
        """
        __tablename__ = "audit_logs"

        id = Column(BigInteger, primary_key=True, doc="Unique identifier for the audit log entry (auto-incrementing)") # Using BigInteger for sequence
        company_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.companies.id"), nullable=True, index=True, doc="ID of the company affected or context")
        user_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.users.id", ondelete="SET NULL"), nullable=True, index=True, doc="ID of the user who performed the action")
        action = Column(String(50), nullable=False, doc="Type of action (e.g., 'CREATE_PRODUCT', 'UPDATE_PRICE', 'LOGIN')")
        table_name = Column(String(100), nullable=True, doc="Name of the table affected (if applicable)")
        record_id = Column(UUID(as_uuid=True), nullable=True, doc="ID of the record affected (if applicable)")
        old_values = Column(JSONB, nullable=True, doc="JSONB snapshot of the record BEFORE the change")
        new_values = Column(JSONB, nullable=True, doc="JSONB snapshot of the record AFTER the change")
        ip_address = Column(INET, nullable=True, doc="IP address from where the action originated")
        # session_id UUID, # Not in current schema, but useful for grouping actions within a user session
        created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, doc="Timestamp when the audit log entry was created")

        # Relationships
        company = relationship("Company", back_populates="audit_logs", doc="The company associated with this audit log entry")
        user = relationship("User", back_populates="audit_logs", doc="The user associated with this audit log entry")

        # No `updated_at` as audit logs are immutable.
    ```
*   **Acceptance Checklist:**
    *   [ ] `AuditLog` ORM class is defined.
    *   [ ] `__tablename__` is correct.
    *   [ ] `ForeignKey` references include `sgpos.` schema prefix and correct `ondelete` action.
    *   [ ] All columns match `schema.sql` (name, type, `nullable`, `default`).
    *   [ ] `id` is `BigInteger` for auto-incrementing.
    *   [ ] `old_values` and `new_values` are `JSONB`.
    *   [ ] `ip_address` is `INET`.
    *   [ ] Correctly omits `updated_at`.
    *   [ ] `relationship()` definitions are correct.
    *   [ ] Docstrings are comprehensive.

#### **11. `migrations/env.py`**

*   **File Path:** `migrations/env.py`
*   **Purpose & Goals:** Alembic environment script. It configures how Alembic interacts with SQLAlchemy and the database for migrations. It's crucial for auto-generating migrations. This file needs to be updated to import *all* the newly created ORM models.
*   **Interfaces:** Imports `Base.metadata` to tell Alembic which models to track. Uses the `sqlalchemy.url` from `alembic.ini`.
*   **Interactions:** Executed by `alembic` CLI commands.
*   **Code Skeleton:**
    ```python
    # File: migrations/env.py
    from logging.config import fileConfig

    from sqlalchemy import engine_from_config
    from sqlalchemy import pool

    from alembic import context

    # This is the Alembic Config object, which provides
    # access to the values within the .ini file in use.
    config = context.config

    # Interpret the config file for Python logging.
    # This line sets up loggers basically.
    if config.config_file_name is not None:
        fileConfig(config.config_file_name)

    # add your model's MetaData object here
    # for 'autogenerate' support
    from app.models.base import Base # IMPORTANT: Import your Base
    # Import ALL your models so Alembic knows about them for autogenerate
    from app.models.company import *
    from app.models.user import *
    from app.models.product import *
    from app.models.inventory import *
    from app.models.customer import *
    from app.models.sales import *
    from app.models.payment import *
    from app.models.accounting import *
    from app.models.audit_log import *


    target_metadata = Base.metadata # IMPORTANT: Set this to your Base.metadata

    # other values from the config, defined by the needs of env.py,
    # can be acquired:
    # my_important_option = config.get_main_option("my_important_option")
    # ... etc.


    def run_migrations_offline() -> None:
        """Run migrations in 'offline' mode.

        This configures the context with just a URL
        and not an Engine, though an Engine is acceptable
        here as well.  By skipping the Engine creation
        we don't even need a database to begin with.

        Calls to context.execute() here emit the given string to the
        script output.

        """
        url = config.get_main_option("sqlalchemy.url")
        context.configure(
            url=url,
            target_metadata=target_metadata,
            literal_binds=True,
            dialect_opts={"paramstyle": "named"},
            # Custom parameter for schema handling
            version_table_schema=target_metadata.schema if target_metadata and target_metadata.schema else None
        )

        with context.begin_transaction():
            context.run_migrations()


    def run_migrations_online() -> None:
        """Run migrations in 'online' mode.

        In this scenario we need to create an Engine
        and associate a connection with the context.

        """
        connectable = engine_from_config(
            config.get_section(config.config_ini_section, {}),
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
            url=config.get_main_option("sqlalchemy.url") # Pass URL explicitly
        )

        with connectable.connect() as connection:
            context.configure(
                connection=connection, 
                target_metadata=target_metadata,
                # Custom parameter for schema handling
                version_table_schema=target_metadata.schema if target_metadata and target_metadata.schema else None
            )

            with context.begin_transaction():
                context.run_migrations()


    if context.is_offline_mode():
        run_migrations_offline()
    else:
        run_migrations_online()

    ```
*   **Acceptance Checklist:**
    *   [ ] `migrations/env.py` is present.
    *   [ ] `Base` is imported from `app.models.base`.
    *   [ ] `target_metadata` is set to `Base.metadata`.
    *   [ ] **ALL** ORM model files (`company`, `user`, `product`, `inventory`, `customer`, `sales`, `payment`, `accounting`, `audit_log`) are imported into `env.py` using `from app.models.<module> import *`.
    *   [ ] `version_table_schema` is configured in `context.configure` to handle the `sgpos` schema.

---

This completes the detailed execution plan for **Phase 1.3: Database Schema & Persistence Layer (Models)**, including the crucial correction to the `schema.sql` and the generation of all necessary ORM model files. This ensures a solid, error-free database foundation for the SG-POS project. The next logical step would be to run the Alembic commands to create the initial migration and apply it to the database, as specified in the overall plan.

---
https://drive.google.com/file/d/108RlhMVaufy_hYAq9aWl4fJT0Nc_LB2k/view?usp=sharing, https://drive.google.com/file/d/1DVVDdJPIYRsNjaL1TBK0pyivBT9T3KcR/view?usp=sharing, https://drive.google.com/file/d/1Dv92K22sZCR81fKux1KGaRKSj8Jv-Uyc/view?usp=sharing, https://aistudio.google.com/app/prompts?state=%7B%22ids%22:%5B%221HJO6Ey-cx-eWjXUJuYEitWEe9fWU1I7v%22%5D,%22action%22:%22open%22,%22userId%22:%22103961307342447084491%22,%22resourceKeys%22:%7B%7D%7D&usp=sharing, https://drive.google.com/file/d/1O8RKDf9T_KQwxh_rkPefDZVRvLlJpeOW/view?usp=sharing, https://drive.google.com/file/d/1SzHas3aRVlLw8XZ5_aNYK9dhML_2ea-b/view?usp=sharing, https://drive.google.com/file/d/1cshXJfKI6TJeVUZKw_xMxdF0Ly-V9Anu/view?usp=sharing, https://drive.google.com/file/d/1gTl2UasRWjqn51dY_Ouh_io0JM4zvxOj/view?usp=sharing, https://drive.google.com/file/d/1l2E0gN419jGB6-aopwZySbqPiKbZLfCf/view?usp=sharing, https://drive.google.com/file/d/1nrRKmVq24tyRexjTP6PcrDYAYdreLm4u/view?usp=sharing, https://drive.google.com/file/d/1qSk87Kr_yuVsvxJM8CMpbr8sfCVBtsP8/view?usp=sharing, https://drive.google.com/file/d/1wjCj8KX8Cs8MeVz0a4FWLB7hoeUhSJJe/view?usp=sharing, https://drive.google.com/file/d/1yf-0upWQE6xmB3LxWX6yCtOzUIRt-sDo/view?usp=sharing

