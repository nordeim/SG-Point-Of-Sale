<think>
### **CodeNavigator's Deep Thought Process**

**1. Deconstruct the User's Request**

*   **Primary Goal:** Generate complete, updated replacement files for all `*.py` files in the `app/models/` directory.
*   **Core Task:** The only change required is to remove the hardcoded `"sgpos."` schema prefix from all `ForeignKey` definitions.
*   **Methodology:**
    1.  Systematically go through each file in `app/models/`.
    2.  For each file, identify every `ForeignKey("sgpos. ... ")` declaration.
    3.  Create a new version of the file where the `ForeignKey` is changed to `ForeignKey(" ... ")`.
    4.  All other code, including column definitions, relationships, and mixins, must remain identical.
    5.  I will not touch `__init__.py` or `base.py` as they do not contain `ForeignKey` definitions with the schema prefix.
*   **Validation:** After generating each file, I will perform a mental `diff` against the original version to confirm that only the `ForeignKey` strings have been modified.

**2. Detailed Execution Plan**

I will process each model file sequentially.

*   **File: `app/models/accounting.py`**
    *   **Checklist:**
        *   [ ] `ChartOfAccount.parent_id`: `ForeignKey("sgpos.chart_of_accounts.id")` -> `ForeignKey("chart_of_accounts.id")`.
        *   [ ] `ChartOfAccount.company_id`: `ForeignKey("sgpos.companies.id")` -> `ForeignKey("companies.id")`.
        *   [ ] `JournalEntry.company_id`: `ForeignKey("sgpos.companies.id")` -> `ForeignKey("companies.id")`.
        *   [ ] `JournalEntry.created_by_user_id`: `ForeignKey("sgpos.users.id")` -> `ForeignKey("users.id")`.
        *   [ ] `JournalEntryLine.journal_entry_id`: `ForeignKey("sgpos.journal_entries.id", ...)` -> `ForeignKey("journal_entries.id", ...)`.
        *   [ ] `JournalEntryLine.account_id`: `ForeignKey("sgpos.chart_of_accounts.id")` -> `ForeignKey("chart_of_accounts.id")`.

*   **File: `app/models/audit_log.py`**
    *   **Checklist:**
        *   [ ] `AuditLog.company_id`: `ForeignKey("sgpos.companies.id")` -> `ForeignKey("companies.id")`.
        *   [ ] `AuditLog.user_id`: `ForeignKey("sgpos.users.id", ...)` -> `ForeignKey("users.id", ...)`.

*   **File: `app/models/company.py`**
    *   **Checklist:**
        *   [ ] `Outlet.company_id`: `ForeignKey("sgpos.companies.id", ...)` -> `ForeignKey("companies.id", ...)`.

*   **File: `app/models/customer.py`**
    *   **Checklist:**
        *   [ ] `Customer.company_id`: `ForeignKey("sgpos.companies.id", ...)` -> `ForeignKey("companies.id", ...)`.

*   **File: `app/models/inventory.py`**
    *   **Checklist:**
        *   [ ] `Inventory.outlet_id`: `ForeignKey("sgpos.outlets.id", ...)` -> `ForeignKey("outlets.id", ...)`.
        *   [ ] `Inventory.product_id`: `ForeignKey("sgpos.products.id", ...)` -> `ForeignKey("products.id", ...)`.
        *   [ ] `Inventory.variant_id`: `ForeignKey("sgpos.product_variants.id", ...)` -> `ForeignKey("product_variants.id", ...)`.
        *   [ ] `StockMovement.company_id`: `ForeignKey("sgpos.companies.id")` -> `ForeignKey("companies.id")`.
        *   [ ] `StockMovement.outlet_id`: `ForeignKey("sgpos.outlets.id")` -> `ForeignKey("outlets.id")`.
        *   [ ] `StockMovement.product_id`: `ForeignKey("sgpos.products.id")` -> `ForeignKey("products.id")`.
        *   [ ] `StockMovement.variant_id`: `ForeignKey("sgpos.product_variants.id")` -> `ForeignKey("product_variants.id")`.
        *   [ ] `StockMovement.created_by_user_id`: `ForeignKey("sgpos.users.id")` -> `ForeignKey("users.id")`.
        *   [ ] `PurchaseOrder.company_id`: `ForeignKey("sgpos.companies.id")` -> `ForeignKey("companies.id")`.
        *   [ ] `PurchaseOrder.outlet_id`: `ForeignKey("sgpos.outlets.id")` -> `ForeignKey("outlets.id")`.
        *   [ ] `PurchaseOrder.supplier_id`: `ForeignKey("sgpos.suppliers.id")` -> `ForeignKey("suppliers.id")`.
        *   [ ] `PurchaseOrderItem.purchase_order_id`: `ForeignKey("sgpos.purchase_orders.id", ...)` -> `ForeignKey("purchase_orders.id", ...)`.
        *   [ ] `PurchaseOrderItem.product_id`: `ForeignKey("sgpos.products.id")` -> `ForeignKey("products.id")`.
        *   [ ] `PurchaseOrderItem.variant_id`: `ForeignKey("sgpos.product_variants.id")` -> `ForeignKey("product_variants.id")`.

*   **File: `app/models/product.py`**
    *   **Checklist:**
        *   [ ] `Category.company_id`: `ForeignKey("sgpos.companies.id", ...)` -> `ForeignKey("companies.id", ...)`.
        *   [ ] `Category.parent_id`: `ForeignKey("sgpos.categories.id", ...)` -> `ForeignKey("categories.id", ...)`.
        *   [ ] `Supplier.company_id`: `ForeignKey("sgpos.companies.id", ...)` -> `ForeignKey("companies.id", ...)`.
        *   [ ] `Product.company_id`: `ForeignKey("sgpos.companies.id", ...)` -> `ForeignKey("companies.id", ...)`.
        *   [ ] `Product.category_id`: `ForeignKey("sgpos.categories.id")` -> `ForeignKey("categories.id")`.
        *   [ ] `Product.supplier_id`: `ForeignKey("sgpos.suppliers.id")` -> `ForeignKey("suppliers.id")`.
        *   [ ] `ProductVariant.product_id`: `ForeignKey("sgpos.products.id", ...)` -> `ForeignKey("products.id", ...)`.

*   **File: `app/models/sales.py`**
    *   **Checklist:**
        *   [ ] `SalesTransaction.company_id`: `ForeignKey("sgpos.companies.id", ...)` -> `ForeignKey("companies.id", ...)`.
        *   [ ] `SalesTransaction.outlet_id`: `ForeignKey("sgpos.outlets.id")` -> `ForeignKey("outlets.id")`.
        *   [ ] `SalesTransaction.customer_id`: `ForeignKey("sgpos.customers.id")` -> `ForeignKey("customers.id")`.
        *   [ ] `SalesTransaction.cashier_id`: `ForeignKey("sgpos.users.id")` -> `ForeignKey("users.id")`.
        *   [ ] `SalesTransactionItem.sales_transaction_id`: `ForeignKey("sgpos.sales_transactions.id", ...)` -> `ForeignKey("sales_transactions.id", ...)`.
        *   [ ] `SalesTransactionItem.product_id`: `ForeignKey("sgpos.products.id")` -> `ForeignKey("products.id")`.
        *   [ ] `SalesTransactionItem.variant_id`: `ForeignKey("sgpos.product_variants.id")` -> `ForeignKey("product_variants.id")`.
        *   [ ] `PaymentMethod.company_id`: `ForeignKey("sgpos.companies.id")` -> `ForeignKey("companies.id")`.
        *   [ ] `Payment.sales_transaction_id`: `ForeignKey("sgpos.sales_transactions.id", ...)` -> `ForeignKey("sales_transactions.id", ...)`.
        *   [ ] `Payment.payment_method_id`: `ForeignKey("sgpos.payment_methods.id")` -> `ForeignKey("payment_methods.id")`.

*   **File: `app/models/user.py`**
    *   **Checklist:**
        *   [ ] `User.company_id`: `ForeignKey("sgpos.companies.id", ...)` -> `ForeignKey("companies.id", ...)`.
        *   [ ] `Role.company_id`: `ForeignKey("sgpos.companies.id", ...)` -> `ForeignKey("companies.id", ...)`.
        *   [ ] `RolePermission.role_id`: `ForeignKey("sgpos.roles.id", ...)` -> `ForeignKey("roles.id", ...)`.
        *   [ ] `RolePermission.permission_id`: `ForeignKey("sgpos.permissions.id", ...)` -> `ForeignKey("permissions.id", ...)`.
        *   [ ] `UserRole.user_id`: `ForeignKey("sgpos.users.id", ...)` -> `ForeignKey("users.id", ...)`.
        *   [ ] `UserRole.role_id`: `ForeignKey("sgpos.roles.id", ...)` -> `ForeignKey("roles.id", ...)`.
        *   [ ] `UserRole.outlet_id`: `ForeignKey("sgpos.outlets.id", ...)` -> `ForeignKey("outlets.id", ...)`.

This plan is exhaustive and covers every required modification. I will now generate the complete replacement files for all affected models. This is a purely mechanical but critical refactoring.

