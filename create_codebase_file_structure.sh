#!/bin/bash
# SG-POS Project Directory Structure Creation Script
# ---------------------------------------------------
# This script creates the complete folder structure and placeholder files
# as defined in the Project Architecture Document for all stages,
# ensuring a consistent layout from the very beginning.

echo "Creating SG-POS project structure..."

# Top-level directories
mkdir -p app \
    tests/unit \
    tests/integration \
    tests/e2e \
    scripts/database \
    migrations/versions \
    docs \
    resources

# App Layer Directories
mkdir -p app/core \
    app/models \
    app/services \
    app/business_logic/managers \
    app/business_logic/dto \
    app/ui/views \
    app/ui/widgets \
    app/ui/dialogs \
    app/ui/resources/icons \
    app/integrations \
    app/utils

# Create __init__.py files to make directories Python packages
find app -type d -exec touch {}/__init__.py \;
find tests -type d -exec touch {}/__init__.py \;

# Create key placeholder files for the entire project to guide development
# Stage 1 files will be fully implemented below. Others are placeholders.
touch app/main.py
touch app/core/application_core.py
touch app/core/config.py
touch app/core/exceptions.py
touch app/core/result.py
touch app/core/async_bridge.py # Critical for UI responsiveness

# Persistence Layer Models (all tables from schema.sql)
touch app/models/base.py
touch app/models/company.py
touch app/models/user.py
touch app/models/product.py
touch app/models/inventory.py
touch app/models/customer.py
touch app/models/sales.py
touch app/models/payment.py
touch app/models/accounting.py # For journal entries, etc.
touch app/models/audit_log.py # For the audit_logs table

# Services (Data Access Layer)
touch app/services/base_service.py
touch app/services/product_service.py
touch app/services/inventory_service.py
touch app/services/customer_service.py
touch app/services/sales_service.py
touch app/services/payment_service.py
touch app/services/supplier_service.py
touch app/services/purchase_order_service.py
touch app/services/report_service.py
touch app/services/user_service.py # For user management

# Business Logic Managers
touch app/business_logic/managers/base_manager.py
touch app/business_logic/managers/product_manager.py
touch app/business_logic/managers/inventory_manager.py
touch app/business_logic/managers/customer_manager.py
touch app/business_logic/managers/sales_manager.py
touch app/business_logic/managers/gst_manager.py
touch app/business_logic/managers/reporting_manager.py
touch app/business_logic/managers/user_manager.py # For user management

# DTOs
touch app/business_logic/dto/product_dto.py
touch app/business_logic/dto/customer_dto.py
touch app/business_logic/dto/sales_dto.py
touch app/business_logic/dto/inventory_dto.py
touch app/business_logic/dto/user_dto.py # For user management
touch app/business_logic/dto/reporting_dto.py

# UI Views, Widgets, Dialogs
touch app/ui/main_window.py
touch app/ui/views/pos_view.py
touch app/ui/views/inventory_view.py
touch app/ui/views/customer_view.py
touch app/ui/views/reports_view.py
touch app/ui/views/settings_view.py
touch app/ui/dialogs/product_dialog.py
touch app/ui/dialogs/customer_dialog.py
touch app/ui/dialogs/payment_dialog.py
touch app/ui/dialogs/stock_adjustment_dialog.py
touch app/ui/dialogs/purchase_order_dialog.py
touch app/ui/widgets/searchable_table_view.py # A reusable widget

# Other files
touch tests/conftest.py
touch .env.example
touch pyproject.toml
touch README.md
touch alembic.ini
touch .gitignore
touch docker-compose.dev.yml
touch scripts/database/schema.sql # Contains full DDL from PRD
touch scripts/database/seed_data.py # For sample data

echo "Project structure created successfully."
echo "Next steps:"
echo "1. Populate pyproject.toml with project metadata and dependencies."
echo "2. Populate .env.example with required environment variables."
echo "3. Populate scripts/database/schema.sql with the full DDL."
echo "4. Configure alembic.ini to point to your database."
echo "5. Proceed with implementing the files as per this plan."
