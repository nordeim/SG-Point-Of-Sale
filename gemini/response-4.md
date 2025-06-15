I fully commit to maintaining the highest level of diligence, code quality focus, and meticulous problem-solving for all future tasks related to the SG Bookkeeper project, and any other codebase we work on.

As CodeNavigator, my core purpose is to serve as your deep-thinking, elite AI coding assistant, specializing in comprehensive codebase management, systematic debugging, and strategic code improvement. My operational framework is built upon the principles you've outlined, ensuring precision, architectural foresight, and robustness in every change.

Here's how I will operate:

*   **Meticulousness, Rigor, and Systematic Approach**: I will adopt a methodical approach to every task, starting with a deep understanding of your requirements. My internal processes involve an "extremely long chain of thoughts" to deeply consider the problem, deliberate with myself via systematic reasoning, explore various options, and carefully choose the most optimal solution before proceeding.
*   **Systematic Diagnosis and Thorough Analysis**: For every issue or enhancement, I will conduct a thorough diagnosis to pinpoint the root cause or identify the optimal integration points. I will analyze potential solutions rigorously, considering their impact on existing architecture, performance, security, and maintainability.
*   **Precise, Minimal-Impact Implementation**: My goal is to make surgical, non-disruptive changes. I will develop a detailed execution plan, then cautiously implement according to that plan, ensuring correctness and robustness.
*   **Rigorous Validation for Complete File Updates**: This is paramount. When providing a "complete updated replacement file," I commit to the following:
    *   The file will be **truly complete**, preserving all original, harmless code.
    *   I will modify **only what is strictly necessary** to implement the requested change or fix the bug.
    *   Any removal of existing code will be clearly justified and will only occur if it directly conflicts with new functionality, is demonstrably causing an error, or if its removal is an explicit part of a requested refactoring with a clear rationale.
    *   Crucially, I will perform a **meticulous line-by-line "diff" comparison** against the original file for every generated output to double-check and validate that all changes are accurate, no existing functionality is inadvertently omitted, and no new regressions are introduced. This ensures error-free and complete output.
*   **Clear Communication and Detailed Explanations**: I will provide comprehensive explanations for my analysis, proposed solutions, rationale behind choices, and the impact of the changes, ensuring you have full clarity.
*   **Continuous Improvement**: I will learn from each interaction, refining my processes to deliver increasingly higher quality assistance and contribute to the continuous improvement of the codebase's health.

My working philosophy emphasizes **Architectural Integrity**, **Surgical Precision**, **Forward Compatibility**, **Defensive Implementation**, and comprehensive **Knowledge Transfer**. My ultimate goal is to solve immediate problems efficiently while simultaneously enhancing the long-term health, maintainability, and robustness of your codebase.

---

# Detailed Execution Plan: Building the SG-POS System (Production-Worthy)

This document outlines a comprehensive, step-by-step execution plan to build the SG Point-of-Sale (SG-POS) system, guiding a developer (even a novice) through the creation and completion of all necessary code and configuration files. This plan is meticulously structured based on the `Project Management Document (PMD.md)`'s 5-stage development plan, integrating the architectural principles from the `Project Architecture Document (PAD.md)` and addressing the completeness and quality concerns identified in the previous assessment.

For each file, I will provide:
*   **File Path:** The exact location within the project structure.
*   **Purpose & Goals:** A concise explanation of the file's role.
*   **Interfaces:** Key classes, methods, properties, and Data Transfer Objects (DTOs) it exposes or consumes.
*   **Interactions:** How this file communicates with other modules and layers.
*   **Code Skeleton:** A detailed code structure, including imports, class definitions, method signatures (with type hints and `async`/`await`), meaningful docstrings, and **explicit `TODO` comments** outlining the exact logic to be implemented. This "fleshing out" ensures a clear path for the developer.
*   **Acceptance Checklist:** A set of verifiable criteria to confirm the file's completeness and quality, derived from the PMD and expanded for clarity.

This plan aims to provide a "no-brainer" guide, ensuring that every piece of the puzzle is understood and built to the highest quality standards, culminating in a production-worthy application.

---

## **Stage 1: The Foundation - Core Services & Database Setup**

**Objective:** To establish the skeleton of the application, set up the core architectural patterns, and create a stable foundation upon which all future features will be built. At the end of this stage, we will have a runnable (but empty) application that can connect to a database.

**Crucial Task for this Stage:** Implement the `AsyncWorker` in `app/core/async_bridge.py` and integrate it into `ApplicationCore` and the UI. This is paramount to ensure the UI remains responsive, addressing the critical flaw identified in the assessment.

### **Phase 1.1: Project Scaffolding & Initial Configuration**

This phase sets up the project's foundational files and directory structure.

#### **1. Bash Script to Create Directory Structure**

*   **File Path:** (Run from project root)
*   **Purpose & Goals:** To create the entire directory and file skeleton as defined in the PAD, ensuring a consistent and organized project layout from the outset.
*   **Interactions:** This script is a one-time execution that prepares the filesystem for all subsequent coding efforts.
*   **Code Skeleton:**
    ```bash
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
    ```
*   **Acceptance Checklist (for running the script):**
    *   [ ] The script executes without errors.
    *   [ ] All specified directories are created.
    *   [ ] All `__init__.py` files are created in their respective directories.
    *   [ ] All placeholder `.py` files and other listed files exist in their correct locations.

#### **2. `pyproject.toml`**

*   **File Path:** `pyproject.toml`
*   **Purpose & Goals:** Defines project metadata, Python version compatibility, and all production and development dependencies using Poetry. It also centralizes tool configurations for `black`, `ruff`, `mypy`, and `pytest`.
*   **Interfaces:** Specifies the `name`, `version`, `description`, `authors`, `license`, `readme`, `homepage`, `repository`, `documentation`, `keywords` for the project. Lists all `[tool.poetry.dependencies]` and `[tool.poetry.group.dev.dependencies]`.
*   **Interactions:** Used by Poetry for environment setup (`poetry install`, `poetry shell`). Configuration sections are used by `black` for formatting, `ruff` for linting, `mypy` for type checking, and `pytest` for running tests.
*   **Code Skeleton:** (Based on the last updated `pyproject.toml` provided)
    ```toml
    # ==============================================================================
    # pyproject.toml for the SG Point-of-Sale (SG-POS) System
    # ------------------------------------------------------------------------------
    # This file manages the entire project's metadata, dependencies, and development
    # tool configurations using the Poetry build system. It is the single source of
    # truth for setting up the development environment.
    #
    # For more information on the TOML format: https://toml.io
    # For more information on Poetry: https://python-poetry.org
    # ==============================================================================

    [tool.poetry]
    # --- Project Metadata ---
    # This information is used for packaging the application and for display on
    # package indexes like PyPI if the project is ever published.
    name = "sg-pos-system"
    version = "1.0.0"
    description = "An enterprise-grade, open-source Point-of-Sale system, meticulously engineered for Singapore's SMB retail landscape."
    authors = ["Your Name <you@example.com>"]
    license = "MIT"
    readme = "README.md"
    homepage = "https://github.com/your-org/sg-pos-system"
    repository = "https://github.com/your-org/sg-pos-system"
    documentation = "https://github.com/your-org/sg-pos-system/blob/main/docs/index.md"
    keywords = ["pos", "point-of-sale", "retail", "singapore", "gst", "pyside6", "qt6", "python"]

    # --- Python Version Constraint ---
    # Specifies that this project is compatible with Python 3.11 and any later minor versions,
    # but not Python 4.0. This aligns with the PRD's technology stack choice.
    [tool.poetry.dependencies]
    python = ">=3.11,<3.14" # Updated to reflect compatibility with 3.11, 3.12, 3.13 (if available)

    # --- Core Production Dependencies ---
    # These are the essential packages required for the application to run in production.

    # GUI Framework
    PySide6 = "^6.9.0"         # The core Qt6 bindings for Python.

    # Database & ORM
    SQLAlchemy = {version = "^2.0.30", extras = ["asyncio"]} # The industry-standard ORM, with asyncio support.
    alembic = "^1.13.1"        # For database schema migrations.
    asyncpg = "^0.29.0"        # High-performance asyncio driver for PostgreSQL.

    # Data Validation & Settings
    pydantic = "^2.7.1"        # For Data Transfer Objects (DTOs) and settings management.
    python-dotenv = "^1.0.0"   # For loading environment variables from .env files.

    # Security
    bcrypt = "^4.1.2"          # For secure password hashing.
    cryptography = "^42.0.7"   # For any custom encryption needs.

    # Logging
    structlog = "^24.2.0"       # For structured, context-aware logging.

    # External Integrations & Utilities
    aiohttp = "^3.9.5"         # Asynchronous HTTP client for API integrations.
    reportlab = "^4.1.0"       # For generating PDF receipts and reports.
    openpyxl = "^3.1.2"        # For exporting data to Excel (.xlsx) files.
    qrcode = {version = "^7.4.2", extras = ["pil"]} # For generating QR codes (e.g., for PayNow).


    # --- Development Group Dependencies ---
    # These packages are only installed in development environments (`poetry install --with dev`).
    # This keeps the production installation lean and clean.
    [tool.poetry.group.dev.dependencies]
    # Testing Framework
    pytest = "^8.2.0"             # The primary testing framework.
    pytest-qt = "^4.2.0"          # For testing PySide6 UI components.
    pytest-asyncio = "^0.23.0"    # For testing asyncio code.
    pytest-cov = "^5.0.0"         # For measuring test coverage.
    factory-boy = "^3.3.0"        # For creating test data fixtures.

    # Code Quality & Formatting
    black = "^24.4.2"            # The uncompromising code formatter.
    ruff = "^0.4.4"               # An extremely fast Python linter, replacing flake8, isort, etc.
    mypy = "^1.10.0"              # Static type checker for Python.
    pre-commit = "^3.7.0"         # For managing and maintaining pre-commit hooks.

    # Documentation
    Sphinx = "^7.3.1"             # The standard documentation generator for Python projects.
    myst-parser = "^2.0.0"        # To write Sphinx documentation in Markdown.
    sphinx-rtd-theme = "^2.0.0"   # A popular theme for Sphinx docs.

    # Interactive Development
    ipython = "^8.24.0"           # A better interactive Python shell.


    # ==============================================================================
    # Tool Configurations
    # ------------------------------------------------------------------------------
    # Centralizing tool configurations here makes the project easier to manage.
    # ==============================================================================

    # --- Black (Code Formatter) Configuration ---
    [tool.black]
    line-length = 88
    target-version = ['py311']
    include = '\.pyi?$'
    exclude = '''
    /(
        \.git
      | \.hg
      | \.mypy_cache
      | \.tox
      | \.venv
      | _build
      | buck-out
      | build
      | dist
      | migrations
    )/
    '''

    # --- Ruff (Linter) Configuration ---
    # Ruff is configured to be strict and to replace multiple older tools.
    [tool.ruff]
    line-length = 88
    target-version = "py311"

    # Select a broad range of rules to enforce high code quality.
    # See all rules here: https://docs.astral.sh/ruff/rules/
    select = [
        "E",  # pycodestyle errors
        "W",  # pycodestyle warnings
        "F",  # pyflakes
        "I",  # isort (import sorting)
        "B",  # flake8-bugbear (finds likely bugs)
        "C4", # flake8-comprehensions
        "UP", # pyupgrade (modernizes syntax)
        "S",  # bandit (security linter)
        "SIM",# flake8-simplify
    ]
    ignore = ["E501"] # Ignored by black formatter anyway.

    [tool.ruff.mccabe]
    max-complexity = 10 # Keep functions simple and readable.

    # --- MyPy (Static Type Checker) Configuration ---
    # Enforces strict type checking for robust code.
    [tool.mypy]
    python_version = "3.11"
    warn_return_any = true
    warn_unused_configs = true
    disallow_untyped_defs = true
    disallow_incomplete_defs = true
    check_untyped_defs = true
    disallow_untyped_calls = true
    strict_optional = true
    show_error_codes = true
    exclude = ["migrations/"]


    # --- Pytest Configuration ---
    [tool.pytest.ini_options]
    minversion = "7.0"
    addopts = "-ra -q --cov=app --cov-report=term-missing"
    testpaths = ["tests"]
    python_files = "test_*.py"
    asyncio_mode = "auto" # Automatically handle asyncio tests.
    qt_api = "pyside6"    # Specify the Qt binding for pytest-qt.


    # ==============================================================================
    # Build System Configuration
    # ------------------------------------------------------------------------------
    # This section is required by PEP 517 and tells tools like pip how to build
    # the project package. For Poetry, this is standard boilerplate.
    # ==============================================================================

    [build-system]
    requires = ["poetry-core>=1.0.0"]
    build-backend = "poetry.core.masonry.api"
    ```
*   **Acceptance Checklist:**
    *   [ ] `pyproject.toml` is present in the project root.
    *   [ ] All listed production dependencies are included with their specified version constraints.
    *   [ ] All listed development dependencies are included in the `dev` group.
    *   [ ] `black`, `ruff`, `mypy`, and `pytest` configurations are correctly defined.
    *   [ ] Poetry successfully installs dependencies (`poetry install`).

#### **3. `docker-compose.dev.yml`**

*   **File Path:** `docker-compose.dev.yml`
*   **Purpose & Goals:** Defines the Docker Compose setup for the local development environment, primarily for the PostgreSQL database.
*   **Interfaces:** Exposes port `5432` for the database.
*   **Interactions:** Used by `docker compose up -d db` to start the database container. The Python application will connect to this database via the `DATABASE_URL` environment variable.
*   **Code Skeleton:** (Taken directly from provided samples)
    ```yml
    version: '3.8'

    services:
      db:
        image: postgres:15-alpine
        container_name: sgpos_dev_db
        env_file:
          - .env.dev
        ports:
          - "5432:5432"
        volumes:
          - postgres_dev_data:/var/lib/postgresql/data
        healthcheck:
          test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
          interval: 10s
          timeout: 5s
          retries: 5
          start_period: 10s
        restart: unless-stopped

    volumes:
      postgres_dev_data:
        driver: local
    ```
*   **Acceptance Checklist:**
    *   [ ] `docker-compose.dev.yml` is present in the project root.
    *   [ ] `docker compose up -d db` successfully starts the PostgreSQL container.
    *   [ ] The database is accessible on port `5432`.
    *   [ ] The healthcheck correctly reports the database status.

#### **4. `.env.example` & `.env.dev`**

*   **File Path:** `.env.example` (template), `.env.dev` (actual file copied from template)
*   **Purpose & Goals:** Provides a template for local development environment variables, including database connection details and application-level settings. `python-dotenv` loads these.
*   **Interfaces:** Defines environment variables like `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `DATABASE_URL`, `LOG_LEVEL`, `APP_ENV`, `DEBUG`, `SECRET_KEY`.
*   **Interactions:** Read by `docker-compose.dev.yml` for database container setup and by `app/core/config.py` for application settings.
*   **Code Skeleton:**
    ```env
    # SG-POS Development Environment Configuration
    # Copy this file to .env.dev and fill in the values.
    # IMPORTANT: Ensure .env.dev is NOT committed to version control in production!

    # --- PostgreSQL Database Configuration ---
    # These are used by both Docker Compose to initialize the DB
    # and by the application to connect to it.
    POSTGRES_USER=sgpos_dev_user
    POSTGRES_PASSWORD=a_very_secure_password_for_dev # *** REPLACE WITH A STRONG PASSWORD ***
    POSTGRES_DB=sgpos_dev

    # --- Application Configuration ---
    # The natively-run Python app will read this file via app/core/config.py.
    DATABASE_URL="postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@localhost:5432/${POSTGRES_DB}"

    # Application-level settings
    APP_ENV=development
    DEBUG=True
    LOG_LEVEL=DEBUG # DEBUG, INFO, WARNING, ERROR, CRITICAL
    SECRET_KEY=a_super_secret_dev_key_that_is_not_for_production # *** REPLACE WITH A STRONG, UNIQUE KEY ***

    # --- Example: For stage 4 to simulate current user/company/outlet context ---
    # In a real app, these would come from authentication/session management
    CURRENT_COMPANY_ID=00000000-0000-0000-0000-000000000001
    CURRENT_OUTLET_ID=00000000-0000-0000-0000-000000000002
    CURRENT_USER_ID=00000000-0000-0000-0000-000000000003
    ```
*   **Acceptance Checklist:**
    *   [ ] `.env.example` is present.
    *   [ ] `.env.dev` is created from `.env.example` and its values are filled (especially strong passwords).
    *   [ ] `DATABASE_URL` correctly points to the local Dockerized PostgreSQL instance.

#### **5. `README.md`**

*   **File Path:** `README.md`
*   **Purpose & Goals:** Provides a comprehensive overview of the project, its features, architecture, and detailed setup instructions for local development. Serves as the primary onboarding document for new developers.
*   **Interactions:** This document is the first point of contact for anyone interacting with the repository.
*   **Code Skeleton:** (Taken directly from provided samples)
    ```markdown
    <p align="center">
      <img src="https://example.com/sg-pos-logo.png" alt="SG-POS System Logo" width="200"/>
    </p>

    <h1 align="center">SG Point-of-Sale (SG-POS) System</h1>

    <p align="center">
      <strong>An enterprise-grade, open-source Point-of-Sale system, meticulously engineered for Singapore's SMB retail landscape.</strong>
    </p>

    <p align="center">
      <!-- Badges -->
      <a href="https://github.com/your-org/sg-pos-system/actions/workflows/ci.yml">
        <img src="https://github.com/your-org/sg-pos-system/actions/workflows/ci.yml/badge.svg" alt="CI Status">
      </a>
      <a href="https://codecov.io/gh/your-org/sg-pos-system">
        <img src="https://codecov.io/gh/your-org/sg-pos-system/branch/main/graph/badge.svg" alt="Code Coverage">
      </a>
      <a href="https://github.com/your-org/sg-pos-system/blob/main/LICENSE">
        <img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License: MIT">
      </a>
      <a href="https://www.python.org/">
        <img src="https://img.shields.io/badge/Python-3.11+-3776AB.svg" alt="Python 3.11+">
      </a>
      <a href="https://www.qt.io/">
        <img src="https://img.shields.io/badge/UI-PySide6 (Qt6)-41CD52.svg" alt="PySide6">
      </a>
      <a href="https://www.postgresql.org/">
        <img src="https://img.shields.io/badge/Database-PostgreSQL-336791.svg" alt="PostgreSQL">
      </a>
      <a href="https://github.com/psf/black">
        <img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Code style: black">
      </a>
    </p>

    ---

    ## 📖 Table of Contents

    *   [**1. Introduction: What is SG-POS?**](#1-introduction-what-is-sg-pos)
        *   [The Problem We're Solving](#the-problem-were-solving)
        *   [Our Vision](#our-vision)
    *   [**2. Key Features**](#2-key-features)
        *   [Sales & Checkout](#sales--checkout)
        *   [Inventory Management](#inventory-management)
        *   [Customer Relationship Management (CRM)](#customer-relationship-management-crm)
        *   [Singapore-Specific Compliance](#singapore-specific-compliance)
        *   [Reporting & Analytics](#reporting--analytics)
    *   [**3. Why Contribute? The SG-POS Difference**](#3-why-contribute-the-sg-pos-difference)
        *   [Professional Architecture](#professional-architecture)
        *   [Modern Technology Stack](#modern-technology-stack)
        *   [Real-World Impact](#real-world-impact)
        *   [A Learning Hub](#a-learning-hub)
    *   [**4. Screenshots & Demo**](#4-screenshots--demo)
    *   [**5. Architectural Deep Dive**](#5-architectural-deep-dive)
        *   [The Layered Architecture](#the-layered-architecture)
        *   [The Asynchronous Model](#the-asynchronous-model)
        *   [Core Design Patterns](#core-design-patterns)
    *   [**6. Database Design**](#6-database-design)
    *   [**7. Technology Stack**](#7-technology-stack)
    *   [**8. Getting Started: Your Local Development Environment**](#8-getting-started-your-local-development-environment)
        *   [Prerequisites](#prerequisites)
        *   [Step-by-Step Setup Guide](#step-by-step-setup-guide)
        *   [Running the Application](#running-the-application)
        *   [Running the Test Suite](#running-the-test-suite)
    *   [**9. Codebase Tour: Navigating the Project**](#9-codebase-tour-navigating-the-project)
    *   [**10. How to Contribute**](#10-how-to-contribute)
    *   [**11. Project Roadmap**](#11-project-roadmap)
    *   [**12. License**](#12-license)

    ---

    ## **1. Introduction: What is SG-POS?**

    **SG-POS** is a free and open-source Point-of-Sale system, engineered from the ground up to address the specific operational and regulatory challenges faced by Small to Medium-sized Businesses (SMBs) in Singapore. It aims to provide the power and polish of expensive enterprise systems in an accessible, modern, and maintainable package.

    ### The Problem We're Solving

    Retail in Singapore is a dynamic and demanding environment. Business owners often find themselves caught between several undesirable options:
    1.  **Generic International POS Systems:** These are often powerful but expensive, and their features are not tailored to Singapore's unique market. GST compliance can be a clumsy add-on, and support for local payment methods like NETS and PayNow is often lacking.
    2.  **Legacy Local POS Systems:** While they may handle local regulations, these systems are often built on dated technology, leading to slow performance, clunky user interfaces, poor security, and a lack of modern integration capabilities.
    3.  **Basic Tablet-Based Apps:** These are user-friendly but frequently lack the depth required for serious inventory management, multi-outlet operations, and comprehensive financial reporting.

    SG-POS bridges this gap. It is a "pro-tool" for the serious SMB, combining a deep understanding of the local context with world-class software architecture.

    ### Our Vision

    Our vision is to empower every Singaporean SMB retailer with a digital tool that is a genuine asset to their business—not a necessary evil. We aim to create a system that is:

    *   **Effortlessly Compliant:** Takes the headache out of GST filing and financial auditing.
    *   **Operationally Excellent:** Speeds up checkout lines, automates inventory management, and provides clarity.
    *   **A Source of Insight:** Transforms raw sales data into actionable business intelligence.
    *   **A Joy to Use:** An intuitive, responsive, and reliable tool that staff genuinely appreciate.

    ---

    ## **2. Key Features**

    SG-POS is a comprehensive suite of tools designed to manage every aspect of a retail business.

    ### 💼 Sales & Checkout
    *   **Blazing-Fast Transactions:** Optimized for speed with barcode scanning and a responsive touch interface.
    *   **Flexible Payments:** Accept cash, credit/debit cards, NETS, PayNow, and other QR-based payments. Handle split tenders and partial payments with ease.
    *   **Advanced Discounts:** Implement complex promotions, member-specific pricing, and transaction-level discounts.
    *   **Offline First:** Continue making sales even when the internet is down. Transactions are securely queued and synced automatically upon reconnection.
    *   **Professional Receipts:** Generate and print (or email) IRAS-compliant receipts with your business logo.

    ### 📦 Inventory Management
    *   **Real-Time Tracking:** Stock levels are updated instantly across all terminals and locations with every sale, return, and stock transfer.
    *   **Automated Reordering:** Set reorder points and let the system automatically generate purchase order suggestions.
    *   **Product Variants:** Effortlessly manage products with different sizes, colors, or other attributes.
    *   **Supplier & Purchase Orders:** Manage supplier information and track purchase orders from creation to receiving.
    *   **Stock Takes & Adjustments:** Conduct full or partial stock takes and record adjustments for wastage or discrepancies with a full audit trail.

    ### 👥 Customer Relationship Management (CRM)
    *   **Detailed Customer Profiles:** Maintain a database of your customers with their purchase history and contact details.
    *   **Integrated Loyalty Program:** Run a points-based loyalty program with configurable tiers and rewards to encourage repeat business.
    *   **PDPA Compliant:** Built with Singapore's Personal Data Protection Act in mind, including features for managing customer consent.

    ### 🇸🇬 Singapore-Specific Compliance
    *   **GST Engine:** Automated, accurate calculation of Goods & Services Tax based on current rates. Supports standard-rated, zero-rated, and exempt items.
    *   **IRAS-Compliant Reporting:** Generate GST F5 reports and the IRAS Audit File (IAF) directly from the system, drastically simplifying tax season.
    *   **Peppol e-Invoicing:** Ready for the future of B2B transactions in Singapore with the ability to generate and send Peppol-compliant e-invoices.

    ### 📈 Reporting & Analytics
    *   **Real-Time Dashboard:** A customizable dashboard gives you a live overview of your business KPIs.
    *   **In-Depth Reports:** Dive deep into sales trends, product performance, staff productivity, and customer behaviour.
    *   **Exportable Data:** Export any report to CSV or PDF for further analysis or sharing with your accountant.

    ---

    ## **3. Why Contribute? The SG-POS Difference**

    This isn't just another POS system. We are building SG-POS with an obsessive focus on quality, both in the user experience and, most importantly, in the engineering.

    ### 🏛️ Professional Architecture
    This project is a fantastic opportunity to work on a system built with enterprise-grade architectural patterns.
    *   **Clean Layered Design:** We enforce a strict separation between the UI, business logic, and data access layers. This makes the code easy to reason about, maintain, and test.
    *   **Dependency Injection:** The `ApplicationCore` pattern makes our components modular and decoupled. It's a real-world implementation of SOLID principles.
    *   **Robust Error Handling:** We use the **Result pattern** instead of exceptions for predictable business errors, leading to more resilient and bug-free code.

    ### 🚀 Modern Technology Stack
    You'll get to work with a curated stack of modern, high-demand technologies.
    *   **Python 3.11+:** Leverage the latest features of Python.
    *   **PySide6 (Qt6):** Build beautiful, high-performance, native desktop UIs.
    *   **PostgreSQL:** Work with a powerful, production-grade relational database.
    *   **Asyncio:** Master asynchronous programming in a real-world application, tackling complex concurrency challenges.
    *   **SQLAlchemy 2.0:** Use the industry-standard ORM in its most modern, async-first incarnation.
    *   **Docker & CI/CD:** Our development and deployment workflows are based on modern DevOps practices.

    ### 🌍 Real-World Impact
    Your contributions will directly help small business owners in Singapore run their businesses more effectively. This is a project with a clear, tangible, and positive impact on a real community.

    ### 🎓 A Learning Hub
    Whether you're a junior developer looking to learn best practices or a senior engineer wanting to apply your skills to a challenging project, SG-POS offers a great learning environment. The codebase is designed to be a reference for high-quality application development.

    ---

    ## **4. Screenshots & Demo**

    *(This section will be updated with actual screenshots and a GIF demo once the UI is further developed.)*

    **Placeholder: Main Sales Interface**
    > A clean, uncluttered interface showing a product search bar on the left, a running list of items in the current transaction in the center, and a customer/payment summary on the right. The layout is optimized for both touchscreens and keyboard/scanner input.

    **Placeholder: Inventory Dashboard**
    > A dashboard view showing key inventory metrics: items with low stock, top-selling products by quantity, and a chart of stock value over time. A filterable, searchable table of all products is visible below.

    **Placeholder: GST Report Generation**
    > A simple dialog window allowing the user to select a date range (e.g., a financial quarter). A "Generate GST F5" button produces a preview of the report, matching the official IRAS form layout, with options to export to PDF or CSV.

    ---

    ## **5. Architectural Deep Dive**

    SG-POS is built on a set of robust architectural principles designed for maintainability and scalability.

    ### The Layered Architecture

    Our architecture strictly separates the application into four logical layers:

    ```mermaid
    graph TD
        A[Presentation Layer (UI)] --> B[Business Logic Layer];
        B --> C[Data Access Layer];
        C --> D[Persistence Layer (Database)];
    ```

    1.  **Presentation Layer (`app/ui`):** This layer is responsible *only* for what the user sees and how they interact with it. It's built with PySide6 and contains no business logic. It receives data and sends user actions to the layer below.
    2.  **Business Logic Layer (`app/business_logic`):** This is the brain of the application. It contains the business rules, orchestrates workflows, and makes decisions. For example, the `SalesManager` decides if a discount is valid or if enough stock exists to complete a sale. It is completely independent of the UI.
    3.  **Data Access Layer (`app/services`):** This layer's job is to talk to the database. It implements the **Repository Pattern**, providing a clean, abstract API (e.g., `product_service.get_by_sku()`) that the business logic can use without needing to know anything about SQL or database tables.
    4.  **Persistence Layer (`app/models`):** This layer defines the shape of our data using SQLAlchemy ORM models, which map directly to our PostgreSQL database tables.

    ### The Asynchronous Model

    To ensure the UI is always fast and responsive, we run all I/O-bound operations (like database queries and API calls) in the background.

    *   The **UI runs on the main thread** in the Qt event loop.
    *   All other work happens in a **separate worker thread** running an `asyncio` event loop.
    *   A special **thread-safe bridge** allows the UI to safely request work from the async thread and receive results back without freezing. This is crucial for a smooth user experience.

    ### Core Design Patterns

    *   **Dependency Injection (DI) via `ApplicationCore`:** We avoid tight coupling by using a central `ApplicationCore` object. Instead of a component creating its own dependencies (like a database connection), it asks the `ApplicationCore` for it. This makes testing incredibly easy, as we can provide "mock" dependencies during tests.

    *   **Result Pattern:** For operations that can fail in predictable ways (e.g., "insufficient stock"), our functions don't raise exceptions. Instead, they return a `Result` object, which is either a `Success` containing the value, or a `Failure` containing an error object. This makes error handling explicit and robust.

    *   **Data Transfer Objects (DTOs):** We use Pydantic models to define the structure of data that moves between layers. This ensures that the data is always in the expected format and provides a clear "contract" for what each layer expects to receive and send.

    ---

    ## **6. Database Design**

    Our database is the bedrock of the system's data integrity.

    *   **Engine:** PostgreSQL 15+ for its reliability, performance, and advanced features.
    *   **Schema Principles:**
        *   **UUIDs for Primary Keys:** To support future scalability and prevent key collisions.
        *   **Strict Normalization (3NF):** To reduce data redundancy and improve consistency.
        *   **Referential Integrity:** Enforced with `FOREIGN KEY` constraints.
        *   **Data Types:** Correct types are used for all data (`NUMERIC` for money, `TIMESTAMPTZ` for dates/times).
        *   **Comprehensive Auditing:** A dedicated `audit_logs` table tracks all significant changes to the data, which is critical for financial compliance.

    For the complete database schema, please see the `schema.sql` file in the `/scripts/database` directory.

    ---

    ## **7. Technology Stack**

    This project uses a modern, professional-grade technology stack.

    | Category          | Technology                                         | Rationale                                                                                                   |
    | ----------------- | -------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
    | **Language**      | Python 3.11+                                       | Modern features, performance improvements, and strong ecosystem.                                            |
    | **GUI Framework** | PySide6 (Qt 6)                                     | The gold standard for professional, high-performance, cross-platform desktop applications in Python.        |
    | **Database**      | PostgreSQL 15+                                     | Unmatched reliability, scalability, and feature set for handling critical business and financial data.      |
    | **ORM**           | SQLAlchemy 2.0                                     | Industry-leading Object-Relational Mapper with powerful features and excellent async support.               |
    | **DB Migrations** | Alembic                                            | The standard for managing database schema changes with SQLAlchemy.                                          |
    | **Async**         | `asyncio`                                          | Python's native library for writing concurrent code, essential for a responsive application.                |
    | **Testing**       | `pytest`, `pytest-qt`, `pytest-asyncio`            | A powerful and flexible testing ecosystem that covers all aspects of our application (core, UI, async).      |
    | **Packaging**     | Poetry                                             | Modern, reliable dependency management and packaging that guarantees reproducible environments.             |
    | **Code Quality**  | Black (Formatter), Ruff (Linter), MyPy (Type Checker)| A trifecta of tools to enforce code style, catch bugs early, and ensure long-term maintainability.          |

    ---

    ## **8. Getting Started: Your Local Development Environment**

    We've made it as easy as possible to get a full development environment up and running.

    ### Prerequisites

    *   **Git:** For version control.
    *   **Python 3.11+:** Make sure it's installed and available in your PATH.
    *   **Poetry:** For managing dependencies. [Installation guide](https://python-poetry.org/docs/#installation).
    *   **Docker & Docker Compose:** To run the PostgreSQL database locally without needing to install it on your system.

    ### Step-by-Step Setup Guide

    ```bash
    # 1. Clone the repository from GitHub
    git clone https://github.com/your-org/sg-pos-system.git
    cd sg-pos-system

    # 2. Start the PostgreSQL database using Docker Compose.
    # This command will download the PostgreSQL image and start a container in the background.
    docker compose up -d db

    # 3. Install all project dependencies (including development tools) using Poetry.
    # This will create a virtual environment inside the project folder.
    poetry install

    # 4. Activate the virtual environment.
    # All subsequent commands should be run inside this environment.
    poetry shell

    # 5. Run the database migrations to create all the necessary tables.
    alembic upgrade head

    # 6. (Optional) Seed the database with sample data to have something to work with.
    python scripts/database/seed_data.py

    # You are now ready to run the application!
    ```

    ### Running the Application

    With the setup complete and the virtual environment active, simply run:

    ```bash
    python app/main.py
    ```

    ### Running the Test Suite

    We have a comprehensive test suite to ensure code quality. To run all tests:

    ```bash
    pytest
    ```

    To run tests with a coverage report:

    ```bash
    pytest --cov=app --cov-report=html
    ```
    This will generate a detailed HTML report in a `htmlcov/` directory.

    ---

    ## **9. Codebase Tour: Navigating the Project**

    Our project structure is organized by architectural layer to make it easy to find what you're looking for.

    *   `app/`: This is where all the application source code lives.
        *   `core/`: Contains the application's backbone—the `ApplicationCore`, configuration loaders, and core patterns like `Result`.
        *   `models/`: Defines the database tables as SQLAlchemy Python classes.
        *   `services/`: The Data Access Layer. Contains all the database query logic (Repositories).
        *   `business_logic/`: The Business Logic Layer. Contains `managers` for orchestrating workflows and `dto`s for data contracts.
        *   `ui/`: The Presentation Layer. Contains all the PySide6 widgets, dialogs, and UI-specific code.
        *   `integrations/`: Code for connecting to external APIs (e.g., payment gateways).
    *   `tests/`: Contains all our automated tests, mirroring the `app/` structure.
    *   `scripts/`: Holds utility scripts for database management, seeding, etc.
    *   `migrations/`: Contains the Alembic database migration scripts.
    *   `resources/`: Static assets like icons, images, and QSS stylesheets.

    ---

    ## **10. How to Contribute**

    We welcome contributions from the community! Whether you're fixing a bug, adding a new feature, or improving documentation, your help is valued.

    **Our contribution workflow is simple:**

    1.  **Find an issue:** Look for issues tagged with `good first issue` or `help wanted` on our GitHub Issues page.
    2.  **Fork the repository:** Create your own copy of the project.
    3.  **Create a feature branch:** `git checkout -b feature/your-awesome-feature`.
    4.  **Make your changes:** Write your code and make sure to add corresponding tests.
    5.  **Run all checks:** Before pushing, ensure your code passes all quality checks: `pytest`, `black .`, `ruff .`, `mypy app`.
    6.  **Submit a Pull Request (PR):** Push your branch to your fork and open a PR against our `main` branch.
    7.  **Code Review:** Your PR will be reviewed by the maintainers. We aim to provide feedback within 48 hours.

    For more detailed guidelines, please read our `CONTRIBUTING.md` file (link to be added).

    We adhere to a `CODE_OF_CONDUCT.md` to ensure our community is welcoming and inclusive for everyone.

    ---

    ## **11. Project Roadmap**

    We have an exciting future planned for SG-POS!

    | Phase         | Status          | Key Features                                                                                                 |
    | :------------ | :-------------- | :----------------------------------------------------------------------------------------------------------- |
    | **v1.0 (MVP)**| 🚧 In Progress | Core Sales & Checkout, Inventory Tracking, Basic CRM, GST F5 Reporting, NETS & PayNow Integration.                 |
    | **v1.1**      | 📝 Planned      | Advanced Promotions Module, Multi-Location Inventory Transfers, Xero/QuickBooks Export.                      |
    | **v1.2**      | 📝 Planned      | E-commerce Connector (Shopify), Customer Loyalty Tiers, Staff Performance Dashboard.                         |
    | **v2.0**      | 🌌 Vision       | Full Cloud-Based Backend, Mobile Companion App (for reporting), AI-driven Inventory Forecasting, Plugin API.   |

    ---

    ## **12. License**

    This project is licensed under the **MIT License**. See the `LICENSE` file for full details. You are free to use, modify, and distribute this software, but it is provided "as is" without warranty.
    ```
*   **Acceptance Checklist:**
    *   [ ] `README.md` is present and contains all outlined sections.
    *   [ ] The "Getting Started" section is accurate and allows a new developer to set up the environment.

#### **6. `alembic.ini`**

*   **File Path:** `alembic.ini`
*   **Purpose & Goals:** Configuration file for Alembic, the database migration tool. It tells Alembic where to find migration scripts and how to connect to the database.
*   **Interfaces:** Uses `sqlalchemy.url` to define the database connection string.
*   **Interactions:** Used by `alembic` CLI commands (e.g., `alembic revision`, `alembic upgrade`). It will interact with `app/core/config.py` by using placeholders for the database URL.
*   **Code Skeleton:**
    ```ini
    [alembic]
    script_location = migrations
    # Points to the env.py file in the migrations directory
    # where the Base metadata is imported.
    # This also uses the DATABASE_URL from our .env.dev config.
    sqlalchemy.url = ${DATABASE_URL}
    revision_table_name = alembic_version

    # A section for each environment if needed, e.g., test, prod
    [alembic:main]
    # For future multi-database support or more complex setups.
    ```
*   **Acceptance Checklist:**
    *   [ ] `alembic.ini` is present in the project root.
    *   [ ] `script_location` points to the `migrations` directory.
    *   [ ] `sqlalchemy.url` is correctly configured to use the `DATABASE_URL` environment variable.

#### **7. `.gitignore`**

*   **File Path:** `.gitignore`
*   **Purpose & Goals:** Specifies intentionally untracked files that Git should ignore. Essential for keeping the repository clean and avoiding sensitive data leaks.
*   **Interactions:** Used by Git.
*   **Code Skeleton:**
    ```gitignore
    # Byte-code files
    *.pyc
    __pycache__/

    # Environment variables
    .env
    .env.dev
    .env.production
    *.env # General ignore for .env files

    # Poetry specific
    .venv/
    poetry.lock

    # Database specific
    *.db
    *.sqlite
    data/

    # PySide6/Qt specific
    *.ui
    *.qrc
    *.moc
    *.qmlc
    *.pyi
    debug/
    release/

    # Build artifacts
    build/
    dist/
    *.egg-info/

    # Test coverage
    .coverage
    .pytest_cache/
    htmlcov/

    # MyPy cache
    .mypy_cache/

    # Editors & IDEs
    .vscode/
    .idea/
    *.sublime-project
    *.sublime-workspace

    # Logs
    *.log
    logs/

    # OS generated files
    .DS_Store
    Thumbs.db
    ```
*   **Acceptance Checklist:**
    *   [ ] `.gitignore` is present in the project root.
    *   [ ] It includes entries for `.venv/`, `.env.dev`, `__pycache__/`, `*.pyc`, `htmlcov/`, and `.mypy_cache/`.

### **Phase 1.2: Core Application Infrastructure**

This phase implements the fundamental building blocks of the application's architecture.

#### **1. `app/core/config.py`**

*   **File Path:** `app/core/config.py`
*   **Purpose & Goals:** To manage all application configuration from environment variables and `.env` files. Ensures strongly-typed and validated configuration.
*   **Interfaces:** Exposes a `Settings` class (Pydantic `BaseSettings`) with attributes like `DATABASE_URL`, `LOG_LEVEL`, `APP_ENV`, `DEBUG`. A singleton `settings` object is provided for easy import.
*   **Interactions:**
    *   Reads `.env.dev` (or other specified `.env` files).
    *   `ApplicationCore` consumes the `settings` object during initialization.
*   **Code Skeleton:**
    ```python
    # File: app/core/config.py
    """
    Manages all application configuration.

    This module uses Pydantic's BaseSettings to provide a strongly-typed configuration
    model that loads settings from environment variables and a .env file. This ensures
    that all configuration is validated at startup.
    """
    from pydantic import Field
    from pydantic_settings import BaseSettings, SettingsConfigDict # Use pydantic_settings for newer Pydantic versions

    class Settings(BaseSettings):
        """
        Application settings model.
        Pydantic automatically reads values from environment variables or a .env file.
        The names are case-insensitive.
        """
        model_config = SettingsConfigDict(
            env_file='.env.dev', # Specifies the env file to load for local development.
            env_file_encoding='utf-8',
            extra='ignore' # Allow extra environment variables not defined in the model
        )

        # Database Configuration
        DATABASE_URL: str = Field(..., description="PostgreSQL database connection URL")

        # Application-level settings
        APP_ENV: str = Field("development", description="Application environment (e.g., 'development', 'production')")
        DEBUG: bool = Field(True, description="Enable debug mode (e.g., SQLAlchemy echoing)")
        LOG_LEVEL: str = Field("DEBUG", description="Logging level (e.g., 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')")
        SECRET_KEY: str = Field(..., description="Secret key for security purposes (e.g., session management, hashing)")

        # Context IDs for current company/outlet/user (for development/testing convenience)
        # In production, these would be derived from authentication/session.
        CURRENT_COMPANY_ID: str = Field("00000000-0000-0000-0000-000000000001", description="Placeholder for current company UUID")
        CURRENT_OUTLET_ID: str = Field("00000000-0000-0000-0000-000000000002", description="Placeholder for current outlet UUID")
        CURRENT_USER_ID: str = Field("00000000-0000-0000-0000-000000000003", description="Placeholder for current user UUID")

    # Create a single, importable instance of the settings.
    # The application will import this `settings` object to access configuration.
    settings = Settings()
    ```
*   **Acceptance Checklist:**
    *   [ ] `Settings` class is implemented using `BaseSettings` (from `pydantic_settings`).
    *   [ ] It correctly loads variables from a `.env.dev` file.
    *   [ ] It includes `DATABASE_URL`, `LOG_LEVEL`, `APP_ENV`, `DEBUG`, `SECRET_KEY`, `CURRENT_COMPANY_ID`, `CURRENT_OUTLET_ID`, `CURRENT_USER_ID` with correct types and default values (where applicable).
    *   [ ] Unit tests (to be written later) exist to verify that variables are loaded correctly and validation works.

#### **2. `app/core/result.py`**

*   **File Path:** `app/core/result.py`
*   **Purpose & Goals:** To define the `Result`, `Success`, and `Failure` classes for explicit, functional error handling, avoiding exceptions for predictable business errors.
*   **Interfaces:** Exposes `Result` (a `Union` type hint), `Success(value: T)`, and `Failure(error: E)`.
*   **Interactions:** Used extensively by `app/services/` (Data Access Layer) and `app/business_logic/managers/` (Business Logic Layer) to return operation outcomes. UI components will consume `Result` objects to display success messages or errors.
*   **Code Skeleton:**
    ```python
    # File: app/core/result.py
    """
    Defines the Result pattern for explicit error handling.

    This module provides a functional approach to error handling, avoiding the use
    of exceptions for predictable business logic failures. All service and manager
    methods should return a Result object.
    """
    from typing import TypeVar, Generic, Union, Optional, final
    from dataclasses import dataclass

    # Generic TypeVars for Success (T) and Failure (E) values.
    T = TypeVar('T')
    E = TypeVar('E')

    @final
    @dataclass(frozen=True)
    class Success(Generic[T]):
        """Represents a successful operation with a return value."""
        value: T

    @final
    @dataclass(frozen=True)
    class Failure(Generic[E]):
        """Represents a failed operation with an error object."""
        error: E

    # The Result type is a union of a Success or a Failure.
    Result = Union[Success[T], Failure[E]]
    ```
*   **Acceptance Checklist:**
    *   [ ] `Success(Generic[T])` and `Failure(Generic[E])` dataclasses are implemented.
    *   [ ] `Result` type alias `Union[Success[T], Failure[E]]` is defined.
    *   [ ] The code is fully type-hinted and passes MyPy checks.
    *   [ ] `Success` and `Failure` are marked as `@final` and `frozen=True`.

#### **3. `app/core/exceptions.py`**

*   **File Path:** `app/core/exceptions.py`
*   **Purpose & Goals:** To define custom exception classes for unexpected, catastrophic system failures (e.g., database unreachable). These are distinct from predictable business errors handled by the `Result` pattern.
*   **Interfaces:** Defines custom exception classes inheriting from `Exception` or a common base.
*   **Interactions:** Raised by core components (e.g., `ApplicationCore` on DB connection failure) and caught at application entry points or higher-level error handlers.
*   **Code Skeleton:**
    ```python
    # File: app/core/exceptions.py
    """
    Defines custom exception classes for the application.

    While the Result pattern is used for predictable business errors, exceptions
    are still used for unexpected, catastrophic system failures (e.g., database
    is unreachable, configuration is missing).
    """

    class CoreException(Exception):
        """Base exception for all application-specific errors."""
        pass

    class ConfigurationError(CoreException):
        """Raised when there is an error in the application configuration."""
        pass

    class DatabaseConnectionError(CoreException):
        """Raised when the application cannot connect to the database."""
        pass

    class AsyncBridgeError(CoreException):
        """Raised when there is an error in the asynchronous bridge setup or operation."""
        pass

    # TODO: Add more specific exceptions as needed for different domains (e.g., SalesError, InventoryError)
    # These would typically be subclasses of a higher-level business exception,
    # distinct from CoreException. For example:
    # class BusinessError(CoreException): pass
    # class InsufficientStockError(BusinessError): pass
    ```
*   **Acceptance Checklist:**
    *   [ ] `CoreException` is defined as a base exception.
    *   [ ] `ConfigurationError`, `DatabaseConnectionError`, and `AsyncBridgeError` are defined, inheriting from `CoreException`.
    *   [ ] New business-specific exception types are added as development progresses, inheriting from a suitable base.

#### **4. `app/core/async_bridge.py`** (CRITICAL NEW IMPLEMENTATION)

*   **File Path:** `app/core/async_bridge.py`
*   **Purpose & Goals:** To provide a robust, thread-safe bridge between the PySide6 (Qt) event loop (running on the main thread) and the `asyncio` event loop (running on a dedicated worker thread). This prevents UI freezes during I/O-bound operations.
*   **Interfaces:**
    *   `AsyncWorker(QObject)`: A `QObject` subclass that lives in the worker thread.
    *   `task_finished = Signal(object, object)`: A Qt Signal emitted by `AsyncWorker` to send results back to the main UI thread. The first `object` is the result, the second is the error (if any).
    *   `run_task(coro: Coroutine, sender_info: Any = None)`: Method on `AsyncWorker` to submit a coroutine for execution.
    *   `AsyncWorkerThread(QThread)`: A `QThread` subclass that manages the `AsyncWorker` and its `asyncio` loop.
*   **Interactions:**
    *   `ApplicationCore` will instantiate and manage the `AsyncWorkerThread` and `AsyncWorker`.
    *   UI components (`POSView`, `ProductDialog`, etc.) will call `self.core.async_worker.run_task()` to offload async operations.
    *   UI components will connect to `self.core.async_worker.task_finished` signal to receive results safely on the main thread and update the UI.
*   **Code Skeleton:**
    ```python
    # File: app/core/async_bridge.py
    """
    Provides a robust, thread-safe bridge between the PySide6 (Qt) event loop
    and the asyncio event loop. This prevents UI freezes during I/O-bound operations.
    """
    import asyncio
    import threading
    from typing import Coroutine, Any, Callable, Optional, Union
    import inspect

    from PySide6.QtCore import QObject, QThread, Signal, Slot, QMetaObject, Qt
    from PySide6.QtWidgets import QApplication

    from app.core.exceptions import AsyncBridgeError

    class AsyncWorker(QObject):
        """
        An object that lives in a QThread and runs an asyncio event loop.
        It accepts coroutines for execution and signals results back to the main thread.
        """
        # Signal emitted when an async task finishes (result, error)
        # The result and error can be anything, so we use object for broad typing.
        task_finished = Signal(object, object)

        def __init__(self, loop: asyncio.AbstractEventLoop, parent: Optional[QObject] = None):
            super().__init__(parent)
            self._loop = loop
            self._tasks = set()
            self._running = True

        def stop(self):
            """Gracefully stops the asyncio loop."""
            self._running = False
            # Cancel all pending tasks
            for task in list(self._tasks):
                task.cancel()
            
            # Wait for tasks to finish cancelling
            # asyncio.run_coroutine_threadsafe(
            #     self._wait_for_tasks_to_finish(),
            #     self._loop
            # ).result(timeout=5) # blocking wait for 5 seconds

            # Schedule loop stop in its own thread
            self._loop.call_soon_threadsafe(self._loop.stop)

        # @Slot(object, object) # Not a slot that receives data, but emits
        def run_task(self, coro: Coroutine[Any, Any, Any], on_done_callback: Optional[Callable[[Any, Optional[Exception]], None]] = None):
            """
            Submits a coroutine to be run on the asyncio event loop in the worker thread.
            
            Args:
                coro: The awaitable (coroutine) to run.
                on_done_callback: An optional callable that will be invoked on the main UI thread
                                  with the result or exception when the task completes.
                                  Signature: `callback(result, error_or_none)`.
            """
            if not inspect.iscoroutine(coro):
                raise TypeError("Input must be a coroutine.")

            # Create a future in the worker thread's loop
            future = asyncio.run_coroutine_threadsafe(coro, self._loop)
            self._tasks.add(future)

            def _done_callback(fut: asyncio.Future):
                self._tasks.discard(fut)
                result = None
                error = None
                try:
                    result = fut.result()
                except asyncio.CancelledError:
                    error = AsyncBridgeError("Task cancelled.")
                except Exception as e:
                    error = e
                
                # Use QMetaObject.invokeMethod to safely call the signal emission on the main thread
                # This ensures the signal is emitted from the correct thread.
                QMetaObject.invokeMethod(self.task_finished, "emit",
                                         Qt.ConnectionType.QueuedConnection,
                                         Q_ARG(object, result),
                                         Q_ARG(object, error))
                
                # Also invoke the direct callback if provided, on the main thread
                if on_done_callback:
                    QMetaObject.invokeMethod(QApplication.instance(), on_done_callback,
                                             Qt.ConnectionType.QueuedConnection,
                                             Q_ARG(object, result),
                                             Q_ARG(object, error))

            future.add_done_callback(_done_callback)

    class AsyncWorkerThread(QThread):
        """
        A QThread that manages an asyncio event loop and an AsyncWorker.
        This is the actual thread that the asyncio loop runs on.
        """
        def __init__(self, parent: Optional[QObject] = None):
            super().__init__(parent)
            self.loop = None
            self.worker = None
            self._thread_started_event = threading.Event()

        def run(self):
            """Entry point for the thread. Initializes and runs the asyncio event loop."""
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)

            self.worker = AsyncWorker(self.loop)
            self.worker.moveToThread(self) # Worker object lives in this thread

            # Signal that the thread and loop are ready
            self._thread_started_event.set()

            # Run the event loop until stop() is called or tasks are done
            self.loop.run_forever()
            self.loop.close() # Clean up the loop when it stops

        def start_and_wait(self):
            """Starts the thread and waits until the event loop is ready."""
            self.start()
            self._thread_started_event.wait(timeout=5) # Wait up to 5 seconds for thread to start
            if not self._thread_started_event.is_set():
                raise AsyncBridgeError("AsyncWorkerThread failed to start event loop in time.")

        def stop_and_wait(self):
            """Stops the worker and the thread gracefully."""
            if self.worker:
                self.worker.stop()
            self.wait() # Wait for the thread to actually finish
            
    # Utility function to get the current QApplication instance
    def _qapp_instance():
        app = QApplication.instance()
        if app is None:
            raise RuntimeError("QApplication not initialized.")
        return app

    # Q_ARG helper for invokeMethod
    # Note: For complex types or custom classes, `Q_ARG` might not serialize correctly across threads
    # for `Qt.QueuedConnection`. Simple Python primitives, lists, dicts, and dataclasses work well.
    from PySide6.QtCore import QGenericArgument as Q_ARG
    ```
*   **Acceptance Checklist:**
    *   [ ] `AsyncWorker` class is implemented, inheriting from `QObject`.
    *   [ ] `AsyncWorker.task_finished` signal is defined.
    *   [ ] `AsyncWorker.run_task` correctly submits coroutines to its internal `asyncio` loop and uses `QMetaObject.invokeMethod` with `Qt.QueuedConnection` to emit `task_finished` on the main thread.
    *   [ ] `AsyncWorkerThread` is implemented, inheriting from `QThread`.
    *   [ ] `AsyncWorkerThread.run` correctly initializes and runs an `asyncio` event loop.
    *   [ ] `AsyncWorkerThread.start_and_wait` and `stop_and_wait` methods are implemented for controlled lifecycle management.
    *   [ ] Type hinting is complete and accurate.
    *   [ ] Handles `asyncio.CancelledError` and other potential exceptions.

#### **5. `app/core/application_core.py`** (Modified from Stage 1 Sample)

*   **File Path:** `app/core/application_core.py`
*   **Purpose & Goals:** The central Dependency Injection (DI) container. Manages the lifecycle and provides access to all major application services and managers, including the newly implemented `AsyncWorker`.
*   **Interfaces:**
    *   `initialize()`: Sets up DB connections, `AsyncWorkerThread`.
    *   `shutdown()`: Gracefully closes DB connections, stops `AsyncWorkerThread`.
    *   `get_session()`: Provides an `AsyncSession` context manager for database operations.
    *   `async_worker`: Property providing access to the `AsyncWorker` instance for submitting tasks.
    *   Placeholder properties for all services and managers (e.g., `product_service`, `sales_manager`).
*   **Interactions:**
    *   `app/main.py` calls `initialize()` and `shutdown()`.
    *   All services and managers get database sessions via `get_session()`.
    *   UI components call `async_worker.run_task()` to execute backend logic.
    *   Lazy-loads instances of all services (`app/services/`) and managers (`app/business_logic/managers/`).
*   **Code Skeleton:**
    ```python
    # File: app/core/application_core.py
    """
    The heart of the application's architecture: The Dependency Injection Container.

    The ApplicationCore class is a singleton-like object responsible for creating,
    managing, and providing access to all major application services and managers.
    It uses a lazy-initialization pattern to ensure resources are only created when
    they are first needed.
    """
    from __future__ import annotations
    from typing import TYPE_CHECKING, AsyncIterator, Dict, Any, Optional
    from contextlib import asynccontextmanager
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

    from app.core.config import Settings
    from app.core.exceptions import DatabaseConnectionError, CoreException
    from app.core.async_bridge import AsyncWorker, AsyncWorkerThread # NEW: Import AsyncWorker

    # Type checking block to avoid circular imports at runtime
    if TYPE_CHECKING:
        # Import all services and managers that will be lazy-loaded
        from app.services.product_service import ProductService
        from app.services.customer_service import CustomerService
        from app.services.inventory_service import InventoryService
        from app.services.sales_service import SalesService
        from app.services.payment_service import PaymentService
        from app.services.supplier_service import SupplierService
        from app.services.purchase_order_service import PurchaseOrderService
        from app.services.report_service import ReportService
        from app.services.user_service import UserService

        from app.business_logic.managers.product_manager import ProductManager
        from app.business_logic.managers.customer_manager import CustomerManager
        from app.business_logic.managers.inventory_manager import InventoryManager
        from app.business_logic.managers.sales_manager import SalesManager
        from app.business_logic.managers.gst_manager import GstManager
        from app.business_logic.managers.reporting_manager import ReportingManager
        from app.business_logic.managers.user_manager import UserManager


    class ApplicationCore:
        """
        Central DI container providing lazy-loaded access to services and managers.
        This class is the glue that holds the decoupled components of the system together.
        """

        def __init__(self, settings: Settings):
            """Initializes the core with application settings."""
            self.settings = settings
            self._engine = None
            self._session_factory = None
            
            self._managers: Dict[str, Any] = {}
            self._services: Dict[str, Any] = {}

            # NEW: Asynchronous Worker Setup
            self._async_worker_thread: Optional[AsyncWorkerThread] = None
            self._async_worker: Optional[AsyncWorker] = None

            # Store current user/company/outlet context (for simplicity in dev)
            self._current_company_id: Optional[uuid.UUID] = None
            self._current_outlet_id: Optional[uuid.UUID] = None
            self._current_user_id: Optional[uuid.UUID] = None


        async def initialize(self) -> None:
            """
            Initializes essential resources like the database connection pool and async worker.
            This method must be called once at application startup.
            """
            # Initialize database
            try:
                self._engine = create_async_engine(
                    self.settings.DATABASE_URL,
                    echo=self.settings.DEBUG, # Log SQL statements in debug mode
                    pool_size=10,
                    max_overflow=20,
                )
                # Verify connection
                async with self._engine.connect() as conn:
                    await conn.run_sync(lambda c: c.execute(sa.text("SELECT 1"))) # Use sa.text for literal SQL

                self._session_factory = async_sessionmaker(
                    self._engine, class_=AsyncSession, expire_on_commit=False
                )
            except Exception as e:
                raise DatabaseConnectionError(f"Failed to connect to database: {e}")

            # NEW: Start the AsyncWorker thread
            try:
                self._async_worker_thread = AsyncWorkerThread()
                self._async_worker_thread.start_and_wait() # Blocks until thread is ready
                if self._async_worker_thread.worker is None:
                    raise AsyncBridgeError("AsyncWorker not initialized in thread.")
                self._async_worker = self._async_worker_thread.worker
            except Exception as e:
                raise AsyncBridgeError(f"Failed to start async worker thread: {e}")

            # Populate initial context IDs from settings (for development)
            # In a real app, these would be set after user authentication
            import uuid
            try:
                self._current_company_id = uuid.UUID(self.settings.CURRENT_COMPANY_ID)
                self._current_outlet_id = uuid.UUID(self.settings.CURRENT_OUTLET_ID)
                self._current_user_id = uuid.UUID(self.settings.CURRENT_USER_ID)
            except ValueError as e:
                raise ConfigurationError(f"Invalid UUID format in settings for current context IDs: {e}")


        async def shutdown(self) -> None:
            """Gracefully disposes of resources, like the database connection pool and async worker."""
            print("Shutting down ApplicationCore resources...")
            if self._async_worker_thread:
                print("Stopping async worker thread...")
                self._async_worker_thread.stop_and_wait()
                print("Async worker thread stopped.")
            if self._engine:
                print("Disposing database engine...")
                await self._engine.dispose()
                print("Database engine disposed.")

        @asynccontextmanager
        async def get_session(self) -> AsyncSession:
            """
            Provides a database session for a single unit of work.
            Handles session lifecycle including commit, rollback, and closing.
            """
            if not self._session_factory:
                raise CoreException("Database not initialized. Call core.initialize() first.")
                
            session: AsyncSession = self._session_factory()
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
                
        @property
        def async_worker(self) -> AsyncWorker:
            """Provides access to the AsyncWorker instance."""
            if self._async_worker is None:
                raise CoreException("Async worker not initialized. Call core.initialize() first.")
            return self._async_worker

        # --- Context Properties (for use by Managers/Services) ---
        @property
        def current_company_id(self) -> uuid.UUID:
            """Returns the UUID of the currently active company."""
            if self._current_company_id is None:
                raise CoreException("Current company ID is not set.") # Or handle unauthenticated state
            return self._current_company_id

        @property
        def current_outlet_id(self) -> uuid.UUID:
            """Returns the UUID of the currently active outlet."""
            if self._current_outlet_id is None:
                raise CoreException("Current outlet ID is not set.")
            return self._current_outlet_id

        @property
        def current_user_id(self) -> uuid.UUID:
            """Returns the UUID of the currently logged-in user."""
            if self._current_user_id is None:
                raise CoreException("Current user ID is not set.")
            return self._current_user_id

        # --- Service Properties (lazy-loaded) ---
        @property
        def product_service(self) -> "ProductService":
            """Lazy-loaded singleton for ProductService."""
            if "product" not in self._services:
                from app.services.product_service import ProductService # Local import
                self._services["product"] = ProductService(self)
            return self._services["product"]

        @property
        def customer_service(self) -> "CustomerService":
            """Lazy-loaded singleton for CustomerService."""
            if "customer" not in self._services:
                from app.services.customer_service import CustomerService # Local import
                self._services["customer"] = CustomerService(self)
            return self._services["customer"]

        @property
        def inventory_service(self) -> "InventoryService":
            """Lazy-loaded singleton for InventoryService."""
            if "inventory" not in self._services:
                from app.services.inventory_service import InventoryService # Local import
                self._services["inventory"] = InventoryService(self)
            return self._services["inventory"]

        @property
        def sales_service(self) -> "SalesService":
            """Lazy-loaded singleton for SalesService."""
            if "sales" not in self._services:
                from app.services.sales_service import SalesService # Local import
                self._services["sales"] = SalesService(self)
            return self._services["sales"]

        @property
        def payment_service(self) -> "PaymentService":
            """Lazy-loaded singleton for PaymentService."""
            if "payment" not in self._services:
                from app.services.payment_service import PaymentService # Local import
                self._services["payment"] = PaymentService(self)
            return self._services["payment"]
        
        @property
        def supplier_service(self) -> "SupplierService":
            """Lazy-loaded singleton for SupplierService."""
            if "supplier" not in self._services:
                from app.services.supplier_service import SupplierService # Local import
                self._services["supplier"] = SupplierService(self)
            return self._services["supplier"]

        @property
        def purchase_order_service(self) -> "PurchaseOrderService":
            """Lazy-loaded singleton for PurchaseOrderService."""
            if "purchase_order" not in self._services:
                from app.services.purchase_order_service import PurchaseOrderService # Local import
                self._services["purchase_order"] = PurchaseOrderService(self)
            return self._services["purchase_order"]

        @property
        def report_service(self) -> "ReportService":
            """Lazy-loaded singleton for ReportService."""
            if "report" not in self._services:
                from app.services.report_service import ReportService # Local import
                self._services["report"] = ReportService(self)
            return self._services["report"]

        @property
        def user_service(self) -> "UserService":
            """Lazy-loaded singleton for UserService."""
            if "user" not in self._services:
                from app.services.user_service import UserService # Local import
                self._services["user"] = UserService(self)
            return self._services["user"]

        # --- Manager Properties (lazy-loaded) ---
        @property
        def product_manager(self) -> "ProductManager":
            """Lazy-loaded singleton for ProductManager."""
            if "product" not in self._managers:
                from app.business_logic.managers.product_manager import ProductManager # Local import
                self._managers["product"] = ProductManager(self)
            return self._managers["product"]

        @property
        def customer_manager(self) -> "CustomerManager":
            """Lazy-loaded singleton for CustomerManager."""
            if "customer" not in self._managers:
                from app.business_logic.managers.customer_manager import CustomerManager # Local import
                self._managers["customer"] = CustomerManager(self)
            return self._managers["customer"]

        @property
        def inventory_manager(self) -> "InventoryManager":
            """Lazy-loaded singleton for InventoryManager."""
            if "inventory" not in self._managers:
                from app.business_logic.managers.inventory_manager import InventoryManager # Local import
                self._managers["inventory"] = InventoryManager(self)
            return self._managers["inventory"]

        @property
        def sales_manager(self) -> "SalesManager":
            """Lazy-loaded singleton for SalesManager."""
            if "sales" not in self._managers:
                from app.business_logic.managers.sales_manager import SalesManager # Local import
                self._managers["sales"] = SalesManager(self)
            return self._managers["sales"]

        @property
        def gst_manager(self) -> "GstManager":
            """Lazy-loaded singleton for GstManager."""
            if "gst" not in self._managers:
                from app.business_logic.managers.gst_manager import GstManager # Local import
                self._managers["gst"] = GstManager(self)
            return self._managers["gst"]

        @property
        def reporting_manager(self) -> "ReportingManager":
            """Lazy-loaded singleton for ReportingManager."""
            if "reporting" not in self._managers:
                from app.business_logic.managers.reporting_manager import ReportingManager # Local import
                self._managers["reporting"] = ReportingManager(self)
            return self._managers["reporting"]

        @property
        def user_manager(self) -> "UserManager":
            """Lazy-loaded singleton for UserManager."""
            if "user" not in self._managers:
                from app.business_logic.managers.user_manager import UserManager # Local import
                self._managers["user"] = UserManager(self)
            return self._managers["user"]
    ```
*   **Acceptance Checklist:**
    *   [ ] `ApplicationCore` class is implemented, accepting `Settings` in its constructor.
    *   [ ] `initialize()` method correctly initializes the database engine, session factory, and the `AsyncWorkerThread`.
    *   [ ] `shutdown()` method gracefully disposes of the database engine and stops the `AsyncWorkerThread`.
    *   [ ] `get_session()` is an `asynccontextmanager` that provides `AsyncSession` instances and handles commit/rollback/close.
    *   [ ] `async_worker` property correctly provides access to the `AsyncWorker` instance.
    *   [ ] All current and future service and manager properties are defined with lazy-loading using local imports.
    *   [ ] `current_company_id`, `current_outlet_id`, `current_user_id` properties are added and initialized from settings.
    *   [ ] `SQLAchemy.text` is used for raw SQL in `initialize()`.

### **Phase 1.3: Database Schema & Persistence Layer (Models)**

This phase involves defining the complete database structure via SQLAlchemy ORM models, matching the `schema.sql` from the PRD.

#### **1. `scripts/database/schema.sql`**

*   **File Path:** `scripts/database/schema.sql`
*   **Purpose & Goals:** Contains the complete Data Definition Language (DDL) for the PostgreSQL database schema, including all tables, columns, data types, primary keys, foreign keys, constraints, and extensions. This is the single source of truth for the database structure.
*   **Interfaces:** Defines all database tables and relationships.
*   **Interactions:** Executed by `psql` during initial database setup (`alembic upgrade head` will indirectly use this or generate DDL based on ORM models). Alembic compares the ORM models to this schema to generate migrations.
*   **Code Skeleton:** (This is the *complete* SQL DDL from the PRD, already provided in a previous turn. I will indicate its inclusion.)
    ```sql
    -- File: scripts/database/schema.sql
    -- COMPLETE DDL SCRIPT AS PROVIDED IN THE PRD
    -- (Content omitted here for brevity in this plan, but it should be the full SQL script)

    -- Enable UUID generation
    CREATE EXTENSION IF NOT EXISTS "pgcrypto";

    -- === CORE BUSINESS TABLES ===

    CREATE TABLE companies (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        name VARCHAR(255) NOT NULL,
        registration_number VARCHAR(20) UNIQUE NOT NULL,
        gst_registration_number VARCHAR(20),
        address TEXT,
        phone VARCHAR(20),
        email VARCHAR(255),
        base_currency VARCHAR(3) NOT NULL DEFAULT 'SGD',
        is_active BOOLEAN NOT NULL DEFAULT true,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );

    CREATE TABLE outlets (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        company_id UUID NOT NULL REFERENCES companies(id),
        code VARCHAR(50) NOT NULL,
        name VARCHAR(255) NOT NULL,
        address TEXT,
        phone VARCHAR(20),
        is_active BOOLEAN NOT NULL DEFAULT true,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        UNIQUE(company_id, code)
    );

    CREATE TABLE users (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        company_id UUID NOT NULL REFERENCES companies(id),
        username VARCHAR(100) NOT NULL,
        email VARCHAR(255) NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        full_name VARCHAR(255),
        role VARCHAR(50) NOT NULL CHECK (role IN ('admin', 'manager', 'cashier')),
        is_active BOOLEAN NOT NULL DEFAULT true,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        UNIQUE(company_id, username),
        UNIQUE(company_id, email)
    );

    -- === PRODUCT & INVENTORY ===

    CREATE TABLE categories (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        company_id UUID NOT NULL REFERENCES companies(id),
        parent_id UUID REFERENCES categories(id) ON DELETE SET NULL,
        name VARCHAR(255) NOT NULL,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        UNIQUE(company_id, name)
    );

    CREATE TABLE products (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        company_id UUID NOT NULL REFERENCES companies(id),
        category_id UUID REFERENCES categories(id),
        sku VARCHAR(100) NOT NULL,
        barcode VARCHAR(100),
        name VARCHAR(255) NOT NULL,
        description TEXT,
        cost_price NUMERIC(19, 4) NOT NULL DEFAULT 0,
        selling_price NUMERIC(19, 4) NOT NULL,
        gst_rate NUMERIC(5, 2) NOT NULL DEFAULT 8.00, -- Current SG GST rate
        track_inventory BOOLEAN NOT NULL DEFAULT true,
        reorder_point INT NOT NULL DEFAULT 0,
        is_active BOOLEAN NOT NULL DEFAULT true,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        UNIQUE(company_id, sku)
    );

    CREATE TABLE inventory (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        company_id UUID NOT NULL REFERENCES companies(id),
        outlet_id UUID NOT NULL REFERENCES outlets(id),
        product_id UUID NOT NULL REFERENCES products(id),
        quantity_on_hand NUMERIC(15, 4) NOT NULL DEFAULT 0,
        last_updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        UNIQUE(company_id, outlet_id, product_id)
    );

    CREATE TABLE suppliers (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        company_id UUID NOT NULL REFERENCES companies(id),
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

    CREATE TABLE purchase_orders (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        company_id UUID NOT NULL REFERENCES companies(id),
        outlet_id UUID NOT NULL REFERENCES outlets(id),
        supplier_id UUID NOT NULL REFERENCES suppliers(id),
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

    CREATE TABLE purchase_order_items (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        purchase_order_id UUID NOT NULL REFERENCES purchase_orders(id),
        product_id UUID NOT NULL REFERENCES products(id),
        quantity_ordered NUMERIC(15, 4) NOT NULL,
        quantity_received NUMERIC(15, 4) NOT NULL DEFAULT 0,
        unit_cost NUMERIC(19, 4) NOT NULL,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        UNIQUE(purchase_order_id, product_id)
    );

    CREATE TABLE stock_movements (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        company_id UUID NOT NULL REFERENCES companies(id),
        outlet_id UUID NOT NULL REFERENCES outlets(id),
        product_id UUID NOT NULL REFERENCES products(id),
        movement_type VARCHAR(50) NOT NULL, -- e.g., 'SALE', 'RETURN', 'PURCHASE_RECEIPT', 'ADJUSTMENT_IN', 'ADJUSTMENT_OUT', 'TRANSFER_OUT', 'TRANSFER_IN'
        quantity_change NUMERIC(15, 4) NOT NULL, -- Positive for stock in, negative for stock out
        reference_id UUID, -- e.g., sales_transaction.id, purchase_order.id
        reference_type VARCHAR(50), -- e.g., 'SALES_TRANSACTION', 'PURCHASE_ORDER', 'STOCK_ADJUSTMENT'
        notes TEXT,
        created_by_user_id UUID REFERENCES users(id),
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );


    -- === SALES & TRANSACTIONS ===

    CREATE TABLE customers (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        company_id UUID NOT NULL REFERENCES companies(id),
        customer_code VARCHAR(50) NOT NULL,
        name VARCHAR(255) NOT NULL,
        email VARCHAR(255),
        phone VARCHAR(50),
        loyalty_points INT NOT NULL DEFAULT 0,
        credit_limit NUMERIC(19, 2) NOT NULL DEFAULT 0,
        is_active BOOLEAN NOT NULL DEFAULT true,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        UNIQUE(company_id, customer_code)
    );

    CREATE TABLE sales_transactions (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        company_id UUID NOT NULL REFERENCES companies(id),
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
        status VARCHAR(20) NOT NULL CHECK (status IN ('COMPLETED', 'VOIDED', 'HELD', 'REFUNDED')),
        notes TEXT,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        UNIQUE(company_id, transaction_number)
    );

    CREATE TABLE sales_transaction_items (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        sales_transaction_id UUID NOT NULL REFERENCES sales_transactions(id),
        product_id UUID NOT NULL REFERENCES products(id),
        quantity NUMERIC(15, 4) NOT NULL,
        unit_price NUMERIC(19, 4) NOT NULL, -- Price at time of sale
        cost_price NUMERIC(19, 4) NOT NULL, -- Cost at time of sale for margin analysis
        line_total NUMERIC(19, 2) NOT NULL,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        UNIQUE(sales_transaction_id, product_id)
    );

    CREATE TABLE payment_methods (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        company_id UUID NOT NULL REFERENCES companies(id),
        name VARCHAR(100) NOT NULL,
        type VARCHAR(50) NOT NULL, -- e.g., 'CASH', 'CARD', 'NETS', 'PAYNOW', 'CREDIT'
        is_active BOOLEAN NOT NULL DEFAULT true,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        UNIQUE(company_id, name)
    );

    CREATE TABLE payments (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        sales_transaction_id UUID NOT NULL REFERENCES sales_transactions(id),
        payment_method_id UUID NOT NULL REFERENCES payment_methods(id),
        amount NUMERIC(19, 2) NOT NULL,
        reference_number VARCHAR(100), -- For card approval codes, etc.
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );

    -- === ACCOUNTING & AUDITING ===
    -- This section implies the presence of journal_entries, chart_of_accounts etc.
    -- For now, we focus on the audit logs.

    CREATE TABLE audit_logs (
        id BIGSERIAL PRIMARY KEY,
        company_id UUID,
        user_id UUID REFERENCES users(id),
        action VARCHAR(50) NOT NULL, -- e.g., 'CREATE_PRODUCT', 'UPDATE_PRICE', 'LOGIN'
        table_name VARCHAR(100), -- Null for non-table actions like 'LOGIN'
        record_id UUID, -- Null for non-record-specific actions
        old_values JSONB, -- JSONB snapshot of the record BEFORE change
        new_values JSONB, -- JSONB snapshot of the record AFTER change
        ip_address INET,
        session_id UUID, -- To track a series of actions within a user session
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );

    -- Trigger function to update `updated_at` timestamps automatically
    CREATE OR REPLACE FUNCTION update_updated_at_column()
    RETURNS TRIGGER AS $$
    BEGIN
        NEW.updated_at = NOW();
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    -- Apply update_updated_at_column trigger to all tables that have updated_at
    DO $$
    DECLARE
        t text;
    BEGIN
        FOR t IN SELECT tablename FROM pg_tables WHERE schemaname = 'public' AND EXISTS (SELECT 1 FROM pg_attribute WHERE attrelid = tablename::regclass AND attname = 'updated_at')
        LOOP
            EXECUTE format('CREATE TRIGGER set_updated_at BEFORE UPDATE ON %I FOR EACH ROW EXECUTE FUNCTION update_updated_at_column()', t);
        END LOOP;
    END;
    $$ LANGUAGE plpgsql;


    -- Audit Trigger Function (for capturing old/new values, and user context)
    -- This advanced trigger requires the application to SET a session variable:
    -- SET sgpos.current_user_id = '<the-uuid-of-the-logged-in-user>';
    -- SET sgpos.current_session_id = '<the-uuid-of-the-current-session>';
    -- SET sgpos.current_ip_address = '<the-ip-address-of-the-client>';
    -- SET sgpos.current_company_id = '<the-uuid-of-the-current-company>';

    CREATE OR REPLACE FUNCTION log_changes()
    RETURNS TRIGGER AS $$
    DECLARE
        old_data JSONB;
        new_data JSONB;
        action_type VARCHAR(50);
        current_user UUID;
        current_session UUID;
        current_ip INET;
        current_company UUID;
    BEGIN
        BEGIN
            -- Attempt to retrieve session variables set by the application
            SELECT current_setting('sgpos.current_user_id', true)::uuid INTO current_user;
        EXCEPTION WHEN OTHERS THEN
            current_user := NULL;
        END;
        
        BEGIN
            SELECT current_setting('sgpos.current_session_id', true)::uuid INTO current_session;
        EXCEPTION WHEN OTHERS THEN
            current_session := NULL;
        END;

        BEGIN
            SELECT current_setting('sgpos.current_ip_address', true)::inet INTO current_ip;
        EXCEPTION WHEN OTHERS THEN
            current_ip := NULL;
        END;
        
        BEGIN
            SELECT current_setting('sgpos.current_company_id', true)::uuid INTO current_company;
        EXCEPTION WHEN OTHERS THEN
            current_company := NULL;
        END;

        IF TG_OP = 'INSERT' THEN
            new_data := to_jsonb(NEW);
            old_data := NULL;
            action_type := 'CREATE_' || UPPER(TG_TABLE_NAME);
        ELSIF TG_OP = 'UPDATE' THEN
            old_data := to_jsonb(OLD);
            new_data := to_jsonb(NEW);
            action_type := 'UPDATE_' || UPPER(TG_TABLE_NAME);
        ELSIF TG_OP = 'DELETE' THEN
            old_data := to_jsonb(OLD);
            new_data := NULL;
            action_type := 'DELETE_' || UPPER(TG_TABLE_NAME);
        ELSE
            RETURN NULL;
        END IF;

        INSERT INTO audit_logs (company_id, user_id, action, table_name, record_id, old_values, new_values, ip_address, session_id)
        VALUES (
            current_company,
            current_user,
            action_type,
            TG_TABLE_NAME,
            COALESCE(NEW.id, OLD.id), -- Use ID from NEW or OLD record
            old_data,
            new_data,
            current_ip,
            current_session
        );

        IF TG_OP = 'DELETE' THEN
            RETURN OLD;
        ELSE
            RETURN NEW;
        END IF;
    END;
    $$ LANGUAGE plpgsql;

    -- Example of how to apply the audit trigger (apply to critical tables)
    -- This should be applied for tables like products, sales_transactions, users, customers, etc.
    /*
    CREATE TRIGGER audit_products
    AFTER INSERT OR UPDATE OR DELETE ON products
    FOR EACH ROW EXECUTE FUNCTION log_changes();

    CREATE TRIGGER audit_sales_transactions
    AFTER INSERT OR UPDATE OR DELETE ON sales_transactions
    FOR EACH ROW EXECUTE FUNCTION log_changes();

    CREATE TRIGGER audit_users
    AFTER INSERT OR UPDATE OR DELETE ON users
    FOR EACH ROW EXECUTE FUNCTION log_changes();
    */
    ```
*   **Acceptance Checklist:**
    *   [ ] `scripts/database/schema.sql` is present and contains the complete DDL from the PRD.
    *   [ ] `pgcrypto` extension is enabled.
    *   [ ] All tables (`companies`, `outlets`, `users`, `categories`, `products`, `inventory`, `suppliers`, `purchase_orders`, `purchase_order_items`, `stock_movements`, `customers`, `sales_transactions`, `sales_transaction_items`, `payment_methods`, `payments`, `audit_logs`) are defined.
    *   [ ] `UUID`s are used for primary keys with `DEFAULT gen_random_uuid()`.
    *   [ ] `NUMERIC(19, 4)` or `(19, 2)` is used for all monetary values.
    *   [ ] `TIMESTAMPTZ` is used for all timestamp columns.
    *   [ ] All `FOREIGN KEY` constraints are correctly defined.
    *   [ ] `UNIQUE` constraints are applied as per schema (e.g., `company_id, sku`).
    *   [ ] `CHECK` constraints are used for status/role enums.
    *   [ ] `update_updated_at_column` function and its generic trigger application (`DO $$...`) are present.
    *   [ ] `log_changes` audit trigger function is present and correctly attempts to read session variables.
    *   [ ] Examples of `audit_products`, `audit_sales_transactions`, `audit_users` triggers are provided (commented out by default, to be activated by Alembic).

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

    metadata = MetaData(naming_convention=convention)
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
    *   [ ] `TimestampMixin` is defined with `created_at` and `updated_at` columns using `DateTime(timezone=True)`.
    *   [ ] `created_at` uses `server_default=func.now()`.
    *   [ ] `updated_at` uses `server_default=func.now()` and `onupdate=func.now()`.
    *   [ ] Docstrings are clear.

#### **3. `app/models/company.py`** (and other ORM model files)

*   **File Path:** `app/models/company.py` (and `user.py`, `product.py`, `inventory.py`, `customer.py`, `sales.py`, `payment.py`, `accounting.py`, `audit_log.py`)
*   **Purpose & Goals:** Defines the SQLAlchemy ORM models for all database tables, mapping Python classes to SQL tables and defining relationships between them. These models serve as the Pythonic interface to the persistence layer.
*   **Interfaces:** Each file exports its respective ORM classes (e.g., `Company`, `Outlet`). These classes will have properties corresponding to table columns and `relationship()` definitions for foreign keys.
*   **Interactions:**
    *   Import `Base` and `TimestampMixin` from `app/models/base.py`.
    *   `app/services/` (Data Access Layer) will import and use these ORM models for database operations.
    *   Alembic uses these models (via `Base.metadata`) to detect schema changes and generate migrations.
*   **Code Skeleton (for `app/models/company.py`, similar structure for others):**
    ```python
    # File: app/models/company.py
    """SQLAlchemy models for Company and Outlet entities."""
    import uuid
    from datetime import datetime
    import sqlalchemy as sa
    from sqlalchemy import Column, String, Boolean, ForeignKey, Text
    from sqlalchemy.dialects.postgresql import UUID, INET
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
        registration_number = Column(String(20), nullable=False, unique=True, doc="Company registration number (e.g., ACRA UEN)")
        gst_registration_number = Column(String(20), unique=True, doc="GST registration number (optional)")
        address = Column(Text, doc="Company's primary address")
        phone = Column(String(20), doc="Company's primary phone number")
        email = Column(String(255), doc="Company's primary email address")
        base_currency = Column(String(3), nullable=False, default='SGD', doc="Base currency for financial transactions")
        is_active = Column(Boolean, nullable=False, default=True, doc="Indicates if the company account is active")
        
        # Relationships
        outlets = relationship("Outlet", back_populates="company", cascade="all, delete-orphan", doc="Outlets belonging to this company")
        users = relationship("User", back_populates="company", cascade="all, delete-orphan", doc="Users associated with this company")
        products = relationship("Product", back_populates="company", cascade="all, delete-orphan", doc="Products defined by this company")
        customers = relationship("Customer", back_populates="company", cascade="all, delete-orphan", doc="Customers of this company")
        suppliers = relationship("Supplier", back_populates="company", cascade="all, delete-orphan", doc="Suppliers for this company")
        sales_transactions = relationship("SalesTransaction", back_populates="company", cascade="all, delete-orphan", doc="Sales transactions by this company")
        payment_methods = relationship("PaymentMethod", back_populates="company", cascade="all, delete-orphan", doc="Payment methods configured by this company")
        stock_movements = relationship("StockMovement", back_populates="company", cascade="all, delete-orphan", doc="Stock movements recorded by this company")
        # TODO: Add relationship to accounting entries and audit logs if they have company_id

    class Outlet(Base, TimestampMixin):
        """Represents a physical retail outlet or store."""
        __tablename__ = "outlets"
        
        id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, doc="Unique identifier for the outlet")
        company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True, doc="Foreign key to the owning company")
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
            sa.UniqueConstraint('company_id', 'name', name='uq_outlet_company_name') # Assuming outlet names are unique per company
        )
    ```

    **Code Skeleton (for `app/models/user.py`):**
    ```python
    # File: app/models/user.py
    """SQLAlchemy models for User entities."""
    import uuid
    from datetime import datetime
    import sqlalchemy as sa
    from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime
    from sqlalchemy.dialects.postgresql import UUID
    from sqlalchemy.orm import relationship

    from app.models.base import Base, TimestampMixin

    class User(Base, TimestampMixin):
        """Represents a user (employee) of the SG-POS system."""
        __tablename__ = "users"
        
        id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, doc="Unique identifier for the user")
        company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True, doc="Foreign key to the owning company")
        outlet_id = Column(UUID(as_uuid=True), ForeignKey("outlets.id"), nullable=True, index=True, doc="Foreign key to the assigned outlet (optional)")
        username = Column(String(100), nullable=False, doc="Unique username for login")
        email = Column(String(255), nullable=False, doc="User's email address")
        password_hash = Column(String(255), nullable=False, doc="Hashed password for authentication")
        full_name = Column(String(255), doc="User's full name")
        role = Column(String(50), nullable=False, doc="User's role (admin, manager, cashier)")
        is_active = Column(Boolean, nullable=False, default=True, doc="Indicates if the user account is active")

        # Relationships
        company = relationship("Company", back_populates="users", doc="The company this user belongs to")
        outlet = relationship("Outlet", back_populates="users", doc="The outlet this user is assigned to")
        sales_transactions = relationship("SalesTransaction", back_populates="cashier", doc="Sales transactions processed by this user")
        stock_movements_created = relationship("StockMovement", back_populates="user", doc="Stock movements created by this user")
        
        __table_args__ = (
            sa.UniqueConstraint('company_id', 'username', name='uq_user_company_username'),
            sa.UniqueConstraint('company_id', 'email', name='uq_user_company_email')
        )
    ```

    **Code Skeleton (for `app/models/product.py`):**
    ```python
    # File: app/models/product.py
    """SQLAlchemy models for Product and Category entities."""
    import uuid
    from datetime import datetime
    import sqlalchemy as sa
    from sqlalchemy import Column, String, Boolean, ForeignKey, Numeric, DateTime, Text, Integer
    from sqlalchemy.dialects.postgresql import UUID
    from sqlalchemy.orm import relationship

    from app.models.base import Base, TimestampMixin

    class Category(Base, TimestampMixin):
        """Represents a product category."""
        __tablename__ = "categories"

        id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, doc="Unique identifier for the category")
        company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True, doc="Foreign key to the owning company")
        parent_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=True, doc="Self-referencing foreign key for nested categories")
        name = Column(String(255), nullable=False, doc="Name of the category")
        is_active = Column(Boolean, nullable=False, default=True, doc="Indicates if the category is active")

        # Relationships
        company = relationship("Company", doc="The company this category belongs to")
        products = relationship("Product", back_populates="category", doc="Products belonging to this category")
        parent = relationship("Category", remote_side=[id], backref="children", doc="Parent category for nested categories")

        __table_args__ = (
            sa.UniqueConstraint('company_id', 'name', name='uq_category_company_name'),
        )

    class Product(Base, TimestampMixin):
        """Represents a single product for sale."""
        __tablename__ = "products"

        id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, doc="Unique identifier for the product")
        company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True, doc="Foreign key to the owning company")
        category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=True, index=True, doc="Foreign key to the product's category")
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
        inventory_items = relationship("Inventory", back_populates="product", cascade="all, delete-orphan", doc="Inventory records for this product across outlets")
        sales_transaction_items = relationship("SalesTransactionItem", back_populates="product", doc="Line items in sales transactions involving this product")
        purchase_order_items = relationship("PurchaseOrderItem", back_populates="product", doc="Line items in purchase orders involving this product")
        stock_movements = relationship("StockMovement", back_populates="product", doc="Stock movement records for this product")

        __table_args__ = (
            sa.UniqueConstraint('company_id', 'sku', name='uq_product_company_sku'),
            # TODO: Consider adding a unique constraint on barcode per company if needed
        )
    ```

    **Code Skeleton (for `app/models/inventory.py`):**
    ```python
    # File: app/models/inventory.py
    """SQLAlchemy models for Inventory, Suppliers, Purchase Orders, and Stock Movements."""
    import uuid
    from datetime import datetime
    import sqlalchemy as sa
    from sqlalchemy import Column, String, Boolean, ForeignKey, Numeric, DateTime, Text, Integer
    from sqlalchemy.dialects.postgresql import UUID
    from sqlalchemy.orm import relationship

    from app.models.base import Base, TimestampMixin

    class Inventory(Base, TimestampMixin):
        """Represents the current quantity on hand for a product at a specific outlet."""
        __tablename__ = "inventory"

        id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, doc="Unique identifier for the inventory record")
        company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True, doc="Foreign key to the owning company")
        outlet_id = Column(UUID(as_uuid=True), ForeignKey("outlets.id"), nullable=False, index=True, doc="Foreign key to the outlet where this inventory is held")
        product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False, index=True, doc="Foreign key to the product being tracked")
        quantity_on_hand = Column(Numeric(15, 4), nullable=False, default=0, doc="Current quantity of the product in stock")
        
        # Relationships
        company = relationship("Company", doc="The company this inventory belongs to")
        outlet = relationship("Outlet", back_populates="inventory_items", doc="The outlet where this inventory is located")
        product = relationship("Product", back_populates="inventory_items", doc="The product associated with this inventory record")

        __table_args__ = (
            sa.UniqueConstraint('company_id', 'outlet_id', 'product_id', name='uq_inventory_company_outlet_product'),
        )

    class Supplier(Base, TimestampMixin):
        """Represents a product supplier."""
        __tablename__ = "suppliers"

        id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, doc="Unique identifier for the supplier")
        company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True, doc="Foreign key to the owning company")
        name = Column(String(255), nullable=False, doc="Name of the supplier (unique per company)")
        contact_person = Column(String(255), doc="Main contact person at the supplier")
        email = Column(String(255), doc="Supplier's email address")
        phone = Column(String(50), doc="Supplier's phone number")
        address = Column(Text, doc="Supplier's address")
        is_active = Column(Boolean, nullable=False, default=True, doc="Indicates if the supplier is active")

        company = relationship("Company", back_populates="suppliers", doc="The company this supplier is associated with")
        purchase_orders = relationship("PurchaseOrder", back_populates="supplier", doc="Purchase orders placed with this supplier")

        __table_args__ = (
            sa.UniqueConstraint('company_id', 'name', name='uq_supplier_company_name'),
        )


    class PurchaseOrder(Base, TimestampMixin):
        """Represents a purchase order sent to a supplier."""
        __tablename__ = "purchase_orders"

        id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, doc="Unique identifier for the purchase order")
        company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True, doc="Foreign key to the owning company")
        outlet_id = Column(UUID(as_uuid=True), ForeignKey("outlets.id"), nullable=False, index=True, doc="Foreign key to the outlet requesting the order")
        supplier_id = Column(UUID(as_uuid=True), ForeignKey("suppliers.id"), nullable=False, index=True, doc="Foreign key to the supplier for this order")
        
        po_number = Column(String(50), nullable=False, unique=True, doc="Unique purchase order number (generated by system)")
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
        purchase_order_id = Column(UUID(as_uuid=True), ForeignKey("purchase_orders.id"), nullable=False, index=True, doc="Foreign key to the parent purchase order")
        product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False, index=True, doc="Foreign key to the product being ordered")
        
        quantity_ordered = Column(Numeric(15, 4), nullable=False, doc="Quantity of the product ordered")
        quantity_received = Column(Numeric(15, 4), nullable=False, default=0, doc="Quantity of the product received so far")
        unit_cost = Column(Numeric(19, 4), nullable=False, doc="Cost per unit of the product at the time of order")
        
        # Relationships
        purchase_order = relationship("PurchaseOrder", back_populates="items", doc="The purchase order this item belongs to")
        product = relationship("Product", doc="The product being ordered")

        __table_args__ = (
            sa.UniqueConstraint('purchase_order_id', 'product_id', name='uq_po_item_po_product'),
        )

    class StockMovement(Base, TimestampMixin):
        """Immutable log of all inventory changes for full auditability."""
        __tablename__ = "stock_movements"

        id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, doc="Unique identifier for the stock movement")
        company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True, doc="Foreign key to the owning company")
        outlet_id = Column(UUID(as_uuid=True), ForeignKey("outlets.id"), nullable=False, index=True, doc="Foreign key to the outlet where the movement occurred")
        product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False, index=True, doc="Foreign key to the product involved in the movement")
        
        movement_type = Column(String(50), nullable=False, doc="Type of stock movement (e.g., SALE, PURCHASE_RECEIPT, ADJUSTMENT_IN)")
        quantity_change = Column(Numeric(15, 4), nullable=False, doc="Change in quantity (+ for stock in, - for stock out)")
        
        reference_id = Column(UUID(as_uuid=True), nullable=True, doc="ID of the related transaction (e.g., sales_transaction.id, purchase_order.id)")
        reference_type = Column(String(50), nullable=True, doc="Type of the related transaction (e.g., 'SALES_TRANSACTION', 'PURCHASE_ORDER')")
        
        notes = Column(Text, doc="Notes or reason for the stock movement")
        created_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True, doc="Foreign key to the user who initiated the movement (for audit)")
        
        # Relationships
        company = relationship("Company", doc="The company this movement belongs to")
        outlet = relationship("Outlet", back_populates="stock_movements", doc="The outlet where this movement occurred")
        product = relationship("Product", back_populates="stock_movements", doc="The product affected by this movement")
        user = relationship("User", back_populates="stock_movements_created", doc="The user who created this stock movement record")
    ```

    **Code Skeleton (for `app/models/customer.py`):**
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
        company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True, doc="Foreign key to the owning company")
        customer_code = Column(String(50), nullable=False, doc="Unique identifier for the customer (e.g., loyalty card number)")
        name = Column(String(255), nullable=False, doc="Customer's full name")
        email = Column(String(255), doc="Customer's email address")
        phone = Column(String(50), doc="Customer's phone number")
        loyalty_points = Column(Integer, nullable=False, default=0, doc="Current loyalty points balance")
        credit_limit = Column(Numeric(19, 2), nullable=False, default=0, doc="Credit limit extended to the customer (if applicable)")
        is_active = Column(Boolean, nullable=False, default=True, doc="Indicates if the customer account is active")

        # Relationships
        company = relationship("Company", back_populates="customers", doc="The company this customer belongs to")
        sales_transactions = relationship("SalesTransaction", back_populates="customer", doc="Sales transactions made by this customer")

        __table_args__ = (
            sa.UniqueConstraint('company_id', 'customer_code', name='uq_customer_company_code'),
            # TODO: Consider adding a unique constraint on email per company if email is used as an identifier
        )
    ```

    **Code Skeleton (for `app/models/sales.py`):**
    ```python
    # File: app/models/sales.py
    """SQLAlchemy models for Sales Transactions and their Line Items."""
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
        company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True, doc="Foreign key to the owning company")
        outlet_id = Column(UUID(as_uuid=True), ForeignKey("outlets.id"), nullable=False, index=True, doc="Foreign key to the outlet where the transaction occurred")
        transaction_number = Column(String(50), nullable=False, unique=True, doc="Unique transaction number (e.g., INV-0001)")
        transaction_date = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, doc="Date and time of the transaction")
        
        customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=True, index=True, doc="Foreign key to the customer involved (optional)")
        cashier_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True, doc="Foreign key to the user (cashier) who processed the transaction")

        subtotal = Column(Numeric(19, 2), nullable=False, doc="Sum of prices of all items before tax and discount")
        tax_amount = Column(Numeric(19, 2), nullable=False, doc="Total tax collected on the transaction")
        discount_amount = Column(Numeric(19, 2), nullable=False, default=0, doc="Total discount applied to the transaction")
        rounding_adjustment = Column(Numeric(19, 2), nullable=False, default=0, doc="Small adjustment for cash rounding (if applicable)")
        total_amount = Column(Numeric(19, 2), nullable=False, doc="Final total amount of the transaction, including tax and discounts")

        status = Column(String(20), nullable=False, default='COMPLETED', doc="Status of the transaction (COMPLETED, VOIDED, HELD, REFUNDED)") # COMPLETED, VOIDED, HELD, REFUNDED
        notes = Column(Text, doc="Any notes or comments for the transaction")

        # Relationships
        company = relationship("Company", back_populates="sales_transactions", doc="The company this transaction belongs to")
        outlet = relationship("Outlet", back_populates="sales_transactions", doc="The outlet where this transaction occurred")
        customer = relationship("Customer", back_populates="sales_transactions", doc="The customer involved in this transaction")
        cashier = relationship("User", back_populates="sales_transactions", doc="The cashier who processed this transaction")
        items = relationship("SalesTransactionItem", back_populates="sales_transaction", cascade="all, delete-orphan", doc="Line items in this sales transaction")
        payments = relationship("Payment", back_populates="sales_transaction", cascade="all, delete-orphan", doc="Payments applied to this sales transaction")

        __table_args__ = (
            sa.UniqueConstraint('company_id', 'transaction_number', name='uq_sales_transaction_company_number'),
        )

    class SalesTransactionItem(Base, TimestampMixin):
        """Represents a single line item within a sales transaction."""
        __tablename__ = "sales_transaction_items"

        id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, doc="Unique identifier for the sales item")
        sales_transaction_id = Column(UUID(as_uuid=True), ForeignKey("sales_transactions.id"), nullable=False, index=True, doc="Foreign key to the parent sales transaction")
        
        product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False, index=True, doc="Foreign key to the product sold")
        # TODO: variant_id = Column(UUID(as_uuid=True), ForeignKey("product_variants.id"), nullable=True, doc="Foreign key to the specific product variant (if applicable)")
        
        quantity = Column(Numeric(15, 4), nullable=False, doc="Quantity of the product sold")
        unit_price = Column(Numeric(19, 4), nullable=False, doc="Selling price per unit at the time of sale")
        cost_price = Column(Numeric(19, 4), nullable=False, doc="Cost price per unit at the time of sale (for margin calculation)")
        line_total = Column(Numeric(19, 2), nullable=False, doc="Total amount for this line item (quantity * unit_price)")

        # Relationships
        sales_transaction = relationship("SalesTransaction", back_populates="items", doc="The sales transaction this item belongs to")
        product = relationship("Product", back_populates="sales_transaction_items", doc="The product sold in this line item")

        __table_args__ = (
            sa.UniqueConstraint('sales_transaction_id', 'product_id', name='uq_sales_item_transaction_product'),
            # TODO: If variants are added, this constraint might need to include variant_id
        )
    ```

    **Code Skeleton (for `app/models/payment.py`):**
    ```python
    # File: app/models/payment.py
    """SQLAlchemy models for Payments and Payment Methods."""
    import uuid
    from datetime import datetime
    import sqlalchemy as sa
    from sqlalchemy import Column, String, Boolean, ForeignKey, Numeric, DateTime
    from sqlalchemy.dialects.postgresql import UUID
    from sqlalchemy.orm import relationship

    from app.models.base import Base, TimestampMixin

    class PaymentMethod(Base, TimestampMixin):
        """Represents a payment method available to a company (e.g., Cash, NETS, Credit Card)."""
        __tablename__ = "payment_methods"

        id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, doc="Unique identifier for the payment method")
        company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True, doc="Foreign key to the owning company")
        name = Column(String(100), nullable=False, doc="Name of the payment method (e.g., 'Cash', 'Visa', 'PayNow')")
        type = Column(String(50), nullable=False, doc="Classification of payment method (e.g., 'CASH', 'CARD', 'NETS', 'PAYNOW')")
        is_active = Column(Boolean, nullable=False, default=True, doc="Indicates if the payment method is active and available")

        company = relationship("Company", back_populates="payment_methods", doc="The company this payment method belongs to")
        
        __table_args__ = (
            sa.UniqueConstraint('company_id', 'name', name='uq_payment_methods_company_name'),
            # TODO: Consider uniqueness on (company_id, type) if only one of each type is allowed
        )

    class Payment(Base, TimestampMixin):
        """Represents a single payment applied to a sales transaction."""
        __tablename__ = "payments"

        id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, doc="Unique identifier for the payment")
        sales_transaction_id = Column(UUID(as_uuid=True), ForeignKey("sales_transactions.id"), nullable=False, index=True, doc="Foreign key to the sales transaction this payment is for")
        payment_method_id = Column(UUID(as_uuid=True), ForeignKey("payment_methods.id"), nullable=False, index=True, doc="Foreign key to the payment method used")
        
        amount = Column(Numeric(19, 2), nullable=False, doc="Amount of the payment")
        reference_number = Column(String(100), doc="Reference number for the payment (e.g., card approval code, PayNow transaction ID)")
        
        # Relationships
        sales_transaction = relationship("SalesTransaction", back_populates="payments", doc="The sales transaction this payment belongs to")
        payment_method = relationship("PaymentMethod", doc="The method used for this payment")
    ```

    **Code Skeleton (for `app/models/accounting.py`):**
    ```python
    # File: app/models/accounting.py
    """SQLAlchemy models for core Accounting entities."""
    import uuid
    from datetime import datetime
    import sqlalchemy as sa
    from sqlalchemy import Column, String, Boolean, ForeignKey, Numeric, DateTime, Text
    from sqlalchemy.dialects.postgresql import UUID
    from sqlalchemy.orm import relationship

    from app.models.base import Base, TimestampMixin

    # TODO: Implement full Chart of Accounts if needed for complex accounting
    # class Account(Base, TimestampMixin):
    #     __tablename__ = "accounts"
    #     id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    #     company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    #     name = Column(String(255), nullable=False)
    #     account_type = Column(String(50), nullable=False) # e.g., 'ASSET', 'LIABILITY', 'EQUITY', 'REVENUE', 'EXPENSE'
    #     code = Column(String(20), nullable=False, unique=True)

    class JournalEntry(Base, TimestampMixin):
        """Represents a double-entry accounting journal entry."""
        __tablename__ = "journal_entries"

        id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, doc="Unique identifier for the journal entry")
        company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True, doc="Foreign key to the owning company")
        transaction_date = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, doc="Date of the journal entry")
        description = Column(Text, nullable=False, doc="Description of the transaction")
        # Reference to source transaction (e.g., SalesTransaction.id)
        # Allows tracing back the financial impact to its origin
        source_transaction_id = Column(UUID(as_uuid=True), nullable=True, index=True, doc="ID of the source transaction (e.g., Sales, PO)")
        source_transaction_type = Column(String(50), nullable=True, doc="Type of the source transaction (e.g., 'SALE', 'PURCHASE')")
        
        # Relationships
        journal_items = relationship("JournalItem", back_populates="journal_entry", cascade="all, delete-orphan", doc="Individual debit/credit lines for this journal entry")

    class JournalItem(Base, TimestampMixin):
        """Represents a single debit or credit line within a JournalEntry."""
        __tablename__ = "journal_items"

        id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, doc="Unique identifier for the journal item")
        journal_entry_id = Column(UUID(as_uuid=True), ForeignKey("journal_entries.id"), nullable=False, index=True, doc="Foreign key to the parent journal entry")
        # TODO: account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False, doc="Foreign key to the affected account")
        account_name = Column(String(255), nullable=False, doc="Name of the affected account (e.g., 'Cash', 'Sales Revenue', 'GST Payable')") # Placeholder if Account model not fully implemented
        debit = Column(Numeric(19, 2), nullable=False, default=0, doc="Debit amount for this line item")
        credit = Column(Numeric(19, 2), nullable=False, default=0, doc="Credit amount for this line item")
        
        # Relationships
        journal_entry = relationship("JournalEntry", back_populates="journal_items", doc="The journal entry this item belongs to")
        # TODO: account = relationship("Account", back_populates="journal_items") # If Account model is implemented
    ```

    **Code Skeleton (for `app/models/audit_log.py`):**
    ```python
    # File: app/models/audit_log.py
    """SQLAlchemy model for the Audit Logs."""
    import uuid
    from datetime import datetime
    import sqlalchemy as sa
    from sqlalchemy import Column, String, Boolean, ForeignKey, Numeric, DateTime, Text, BigInteger
    from sqlalchemy.dialects.postgresql import UUID, INET, JSONB
    from sqlalchemy.orm import relationship

    from app.models.base import Base # Audit logs don't use TimestampMixin for `updated_at` as they are immutable

    class AuditLog(Base):
        """
        Immutable log of all significant changes or actions within the system.
        Populated by database triggers and/or application logic.
        """
        __tablename__ = "audit_logs"

        id = Column(BigInteger, primary_key=True, doc="Unique identifier for the audit log entry (auto-incrementing)") # Using BigInteger for sequence
        company_id = Column(UUID(as_uuid=True), nullable=True, index=True, doc="ID of the company affected or context")
        user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True, doc="ID of the user who performed the action")
        action = Column(String(50), nullable=False, doc="Type of action (e.g., 'CREATE_PRODUCT', 'UPDATE_PRICE', 'LOGIN')")
        table_name = Column(String(100), nullable=True, doc="Name of the table affected (if applicable)")
        record_id = Column(UUID(as_uuid=True), nullable=True, doc="ID of the record affected (if applicable)")
        old_values = Column(JSONB, nullable=True, doc="JSONB snapshot of the record BEFORE the change")
        new_values = Column(JSONB, nullable=True, doc="JSONB snapshot of the record AFTER the change")
        ip_address = Column(INET, nullable=True, doc="IP address from where the action originated")
        session_id = Column(UUID(as_uuid=True), nullable=True, doc="ID of the user session (to group related actions)")
        created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, doc="Timestamp when the audit log entry was created")

        # Relationships
        user = relationship("User", doc="The user associated with this audit log entry")

        # No `updated_at` as audit logs are immutable.
    ```

*   **Acceptance Checklist (for each model file):**
    *   [ ] The file defines all ORM classes corresponding to the tables in `schema.sql`.
    *   [ ] Each model inherits from `Base` and `TimestampMixin` (if applicable).
    *   [ ] All columns match the `schema.sql` definition (name, type, `nullable`, `default`).
    *   [ ] `UUID(as_uuid=True)` is used for UUID columns.
    *   [ ] `Numeric` types are correctly defined for monetary values.
    *   [ ] `relationship()` definitions are correct (`back_populates`, `cascade`).
    *   [ ] `__table_args__` defines `UniqueConstraint` correctly.
    *   [ ] Docstrings are comprehensive for each class and column.

#### **4. Alembic Setup (`migrations/env.py`)**

*   **File Path:** `migrations/env.py`
*   **Purpose & Goals:** Alembic environment script. It configures how Alembic interacts with SQLAlchemy and the database for migrations. It's crucial for auto-generating migrations.
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
    # Import all your models so Alembic knows about them for autogenerate
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
        )

        with connectable.connect() as connection:
            context.configure(
                connection=connection, target_metadata=target_metadata
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
    *   [ ] All ORM model files are imported into `env.py` (e.g., `from app.models.company import *`).
    *   [ ] The script's `run_migrations_online()` and `run_migrations_offline()` logic is intact.

#### **5. Initial Migration Script**

*   **File Path:** `migrations/versions/<timestamp>_initial_schema_setup.py` (generated by Alembic)
*   **Purpose & Goals:** This file will contain the DDL generated by Alembic that creates all tables, constraints, and triggers defined in the SQLAlchemy models and `schema.sql`. It's the first version-controlled state of the database schema.
*   **Interactions:** Generated by `alembic revision --autogenerate`. Executed by `alembic upgrade head`.
*   **Code Skeleton:** (This file is generated, not hand-coded, but its creation is part of the plan.)
    ```python
    # File: migrations/versions/<timestamp>_initial_schema_setup.py
    """Initial schema setup"""
    from alembic import op
    import sqlalchemy as sa
    from sqlalchemy.dialects import postgresql

    # revision identifiers, used by Alembic.
    revision = '<generated_revision_id>'
    down_revision = None
    branch_labels = None
    depends_on = None


    def upgrade() -> None:
        # ### commands auto generated by Alembic - please adjust! ###
        # TODO: Verify ALL tables are created here, including their columns, types, and constraints.
        # This will be a large block of code generated by Alembic.
        # Example for `companies` table:
        op.create_table('companies',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        # ... other columns
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_companies')),
        sa.UniqueConstraint('registration_number', name=op.f('uq_companies_registration_number'))
        )
        # TODO: Add explicit DDL for triggers (update_updated_at_column, log_changes) and their application
        # Alembic won't autogenerate triggers. You'll need to add them manually using op.execute()
        # For example:
        # op.execute("""
        #     CREATE OR REPLACE FUNCTION update_updated_at_column()
        #     RETURNS TRIGGER AS $$
        #     BEGIN
        #         NEW.updated_at = NOW();
        #         RETURN NEW;
        #     END;
        #     $$ LANGUAGE plpgsql;
        # """)
        # op.execute("""
        #     CREATE TRIGGER set_updated_at BEFORE UPDATE ON companies FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
        # """)
        # Apply for audit_logs table, etc.
        # ### end Alembic commands ###


    def downgrade() -> None:
        # ### commands auto generated by Alembic - please adjust! ###
        # TODO: Drop tables in reverse order.
        op.drop_table('companies')
        # ### end Alembic commands ###
    ```
*   **Acceptance Checklist:**
    *   [ ] The migration script is generated by `alembic revision --autogenerate -m "Initial schema setup"`.
    *   [ ] The `upgrade()` function correctly defines DDL for ALL tables and their columns, types, constraints as per `schema.sql` and ORM models.
    *   [ ] The DDL for `update_updated_at_column()` function and its triggers (for all relevant tables) are **manually added** to the `upgrade()` function using `op.execute()`.
    *   [ ] The DDL for `log_changes()` audit trigger function and its applications are **manually added** to the `upgrade()` function using `op.execute()`.
    *   [ ] The `downgrade()` function correctly defines DDL to reverse the changes.
    *   [ ] `alembic upgrade head` runs successfully on a clean database, creating all tables and triggers.
    *   [ ] `alembic downgrade base` then `alembic upgrade head` runs successfully to confirm reversibility.

### **Phase 1.4: Main Application Entry Point**

This phase brings together the core components and starts the application.

#### **1. `app/main.py`**

*   **File Path:** `app/main.py`
*   **Purpose & Goals:** The application's entry point. It initializes the `QApplication`, the `ApplicationCore`, and starts the main window. It ensures graceful startup and shutdown.
*   **Interfaces:** `main()` function is the primary entry point.
*   **Interactions:**
    *   Creates `QApplication`.
    *   Instantiates `ApplicationCore` with `settings` from `app/core/config.py`.
    *   Calls `core.initialize()` (asynchronously).
    *   Creates `MainWindow` from `app/ui/main_window.py`.
    *   Starts the `QApplication` event loop.
    *   Handles fatal startup errors.
*   **Code Skeleton:**
    ```python
    # File: app/main.py
    """
    SG-POS Application Entry Point.

    This script initializes the core application components, sets up the asynchronous
    bridge, creates the main UI window, and starts the Qt event loop.
    """
    import sys
    import asyncio
    from PySide6.QtWidgets import QApplication, QMessageBox
    from PySide6.QtCore import QCoreApplication

    from app.core.config import settings
    from app.core.application_core import ApplicationCore
    from app.core.exceptions import CoreException, DatabaseConnectionError, AsyncBridgeError
    from app.ui.main_window import MainWindow

    def main():
        """Initializes and runs the SG-POS application."""
        # Ensure only one QApplication instance
        app = QCoreApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        else:
            print("QApplication already exists.")

        core: Optional[ApplicationCore] = None # Initialize as None

        try:
            # 1. Initialize the Application Core with settings
            # This reads the .env.dev file and prepares the configuration
            core = ApplicationCore(settings)
            
            # 2. Run async initialization for the core (e.g., connect to DB, start async worker)
            # A simple way to run an async function from a sync context for startup.
            asyncio.run(core.initialize())

            # 3. Create and show the main window
            # The `core` object is passed to the main window, making it available
            # to all child UI components for dependency injection.
            main_window = MainWindow(core)
            main_window.show()

            # 4. Start the Qt event loop
            return app.exec()

        except (CoreException, DatabaseConnectionError, AsyncBridgeError) as e:
            msg = f"Fatal Application Error: {e}\n\nCannot start SG-POS. Please check configuration and database connection."
            QMessageBox.critical(None, "SG-POS Startup Error", msg)
            print(f"FATAL: {msg}", file=sys.stderr)
            return 1 # Indicate an error exit code
        except Exception as e:
            msg = f"An unexpected error occurred during application startup: {e}"
            QMessageBox.critical(None, "SG-POS Unexpected Error", msg)
            print(f"FATAL: {msg}", file=sys.stderr)
            return 1
        finally:
            # Ensure graceful shutdown of core resources if initialized
            if core:
                # Need to run shutdown asynchronously from sync context
                # This needs to be carefully handled to not block Qt's exit
                # For simple cleanup, can run directly, but better to integrate with Qt's exit events.
                # For now, let's just make sure it's called.
                print("Attempting graceful shutdown of core...")
                try:
                    asyncio.run(core.shutdown()) # This might block if Qt is still running
                except Exception as e:
                    print(f"Error during core shutdown: {e}", file=sys.stderr)


    if __name__ == "__main__":
        sys.exit(main())
    ```
*   **Acceptance Checklist:**
    *   [ ] `main.py` correctly initializes `QApplication` (handles existing instance).
    *   [ ] It instantiates `ApplicationCore` and calls `core.initialize()` using `asyncio.run()`.
    *   [ ] It creates and shows an instance of `MainWindow`, passing the `core` object.
    *   [ ] It correctly starts the `QApplication` event loop.
    *   [ ] Includes robust error handling for startup failures, displaying a `QMessageBox`.
    *   [ ] Includes a placeholder for `core.shutdown()` to ensure resources are released.

#### **2. `app/ui/main_window.py`**

*   **File Path:** `app/ui/main_window.py`
*   **Purpose & Goals:** The main application window or shell. It hosts all other views (POS, Inventory, Reports, Settings) using a `QStackedWidget` and provides navigation (menu bar).
*   **Interfaces:** `MainWindow(QMainWindow)` class.
*   **Interactions:**
    *   Receives `ApplicationCore` instance in constructor.
    *   Will instantiate `QStackedWidget` to manage different views (`ProductView`, `CustomerView`, `POSView`, `InventoryView`, `ReportsView`, `SettingsView`).
    *   Will create a menu bar for navigation, connecting menu actions to `setCurrentWidget()` calls on the `QStackedWidget`.
    *   `closeEvent` should trigger `core.shutdown()` asynchronously.
*   **Code Skeleton:**
    ```python
    # File: app/ui/main_window.py
    """
    The main window of the SG-POS application.
    This QMainWindow acts as the shell, hosting different views like the POS screen,
    inventory management, etc., and providing navigation.
    """
    import asyncio
    import sys
    from typing import Optional, Any
    from PySide6.QtWidgets import (
        QMainWindow, QWidget, QVBoxLayout, QLabel,
        QStackedWidget, QMenuBar, QMenu, QMessageBox
    )
    from PySide6.QtCore import Slot, QEvent, QObject

    from app.core.application_core import ApplicationCore
    from app.core.async_bridge import AsyncWorker # For type hinting
    from app.core.exceptions import CoreException

    # Import all views that will be hosted
    # These will be fleshed out in subsequent stages
    # from app.ui.views.product_view import ProductView
    # from app.ui.views.customer_view import CustomerView
    # from app.ui.views.pos_view import POSView
    # from app.ui.views.inventory_view import InventoryView
    # from app.ui.views.reports_view import ReportsView
    # from app.ui.views.settings_view import SettingsView


    class MainWindow(QMainWindow):
        """The main application window."""

        def __init__(self, core: ApplicationCore):
            """
            Initializes the main window.
            
            Args:
                core: The central ApplicationCore instance.
            """
            super().__init__()
            self.core = core
            self.async_worker: AsyncWorker = core.async_worker # Get the async worker instance

            self.setWindowTitle("SG Point-of-Sale System")
            self.setGeometry(100, 100, 1280, 720)

            # Create a QStackedWidget to hold the different views
            self.stacked_widget = QStackedWidget()
            self.setCentralWidget(self.stacked_widget)

            # --- Initialize and add placeholder views for Stage 1 ---
            # TODO: Replace these with actual view instances from app/ui/views/
            # For now, just a blank welcome widget
            welcome_widget = QWidget()
            welcome_layout = QVBoxLayout(welcome_widget)
            welcome_label = QLabel("Welcome to SG-POS! (Stage 1 Foundation - Running)")
            welcome_label.setStyleSheet("font-size: 24px; color: #333; text-align: center;")
            welcome_layout.addWidget(welcome_label)
            self.stacked_widget.addWidget(welcome_widget)
            self.stacked_widget.setCurrentWidget(welcome_widget)

            # --- Connect the AsyncWorker's general task_finished signal ---
            # This is a global handler for unhandled async task results or errors
            self.async_worker.task_finished.connect(self._handle_async_task_result)

            # --- Create menu bar for navigation (will be populated in later stages) ---
            self._create_menu()

        def _create_menu(self):
            """Creates the main menu bar with navigation items."""
            menu_bar = self.menuBar()
            
            # File Menu
            file_menu = menu_bar.addMenu("&File")
            exit_action = file_menu.addAction("E&xit")
            exit_action.triggered.connect(self.close)

            # Data Management Menu (Populated in Stage 2)
            # data_menu = menu_bar.addMenu("&Data Management")
            # product_action = data_menu.addAction("Products")
            # product_action.triggered.connect(lambda: self.stacked_widget.setCurrentWidget(self.product_view))
            # customer_action = data_menu.addAction("Customers")
            # customer_action.triggered.connect(lambda: self.stacked_widget.setCurrentWidget(self.customer_view))

            # POS Menu (Populated in Stage 3)
            # pos_menu = menu_bar.addMenu("&POS")
            # pos_action = pos_menu.addAction("Sales")
            # pos_action.triggered.connect(lambda: self.stacked_widget.setCurrentWidget(self.pos_view))

            # Inventory Menu (Populated in Stage 4)
            # inventory_menu = menu_bar.addMenu("&Inventory")
            # inventory_action = inventory_menu.addAction("Stock Management")
            # inventory_action.triggered.connect(lambda: self.stacked_widget.setCurrentWidget(self.inventory_view))

            # Reports Menu (Populated in Stage 5)
            # reports_menu = menu_bar.addMenu("&Reports")
            # reports_action = reports_menu.addAction("Business Reports")
            # reports_action.triggered.connect(lambda: self.stacked_widget.setCurrentWidget(self.reports_view))

            # Settings Menu (Populated in Stage 5)
            # settings_menu = menu_bar.addMenu("&Settings")
            # settings_action = settings_menu.addAction("Application Settings")
            # settings_action.triggered.connect(lambda: self.stacked_widget.setCurrentWidget(self.settings_view))


        @Slot(object, object)
        def _handle_async_task_result(self, result: Any, error: Optional[Exception]):
            """
            Global handler for results/errors from async tasks that didn't have
            a specific `on_done_callback`. This can be used for general error reporting.
            Individual UI components should still use specific callbacks where needed.
            """
            if error:
                print(f"Unhandled async error: {error}", file=sys.stderr)
                # TODO: Implement more sophisticated global error logging/display
                # QMessageBox.critical(self, "Error", f"An unexpected background error occurred: {error}")

        def closeEvent(self, event: QEvent) -> None:
            """
            Handle window close event to gracefully shut down the application core.
            This ensures database connections and async threads are properly terminated.
            """
            print("Main window closing. Initiating ApplicationCore shutdown...")
            
            # Schedule the asynchronous shutdown on the async worker thread
            # and allow the Qt event loop to continue processing until shutdown is complete.
            # This is a safe way to handle async cleanup from a QWidget's closeEvent.
            async def shutdown_task():
                try:
                    await self.core.shutdown()
                    print("ApplicationCore shutdown complete.")
                except Exception as e:
                    print(f"Error during ApplicationCore shutdown: {e}", file=sys.stderr)
                    # Optionally show a message box for critical shutdown failures
                    QMetaObject.invokeMethod(self, "show_shutdown_error",
                                            Qt.ConnectionType.QueuedConnection,
                                            Q_ARG(str, str(e)))
                QMetaObject.invokeMethod(self, "accept_close_event",
                                         Qt.ConnectionType.QueuedConnection)

            self.async_worker.run_task(shutdown_task())
            
            # Ignore the close event for now, we'll accept it once async shutdown is done
            event.ignore()

        @Slot()
        def accept_close_event(self) -> None:
            """Slot to finally accept the close event after async shutdown completes."""
            QApplication.instance().quit() # Quits the QApplication gracefully

        @Slot(str)
        def show_shutdown_error(self, error_message: str) -> None:
            """Displays a critical error message if shutdown fails."""
            QMessageBox.critical(self, "Shutdown Error", f"Failed to gracefully shut down application:\n{error_message}")
    ```
*   **Acceptance Checklist:**
    *   [ ] `MainWindow` class inherits `QMainWindow`.
    *   [ ] Constructor accepts `ApplicationCore` instance.
    *   [ ] `QStackedWidget` is set as central widget.
    *   [ ] A simple "Welcome" widget is added and displayed initially.
    *   [ ] `self.async_worker` is correctly obtained from `core.async_worker`.
    *   [ ] `self.async_worker.task_finished` signal is connected to `_handle_async_task_result` for global error handling.
    *   [ ] `_create_menu` method is defined for future menu items.
    *   [ ] `closeEvent` is overridden to trigger `core.shutdown()` on the `async_worker` thread and *ignore* the event initially.
    *   [ ] `accept_close_event` slot is defined to quit the application after async shutdown.
    *   [ ] `Q_ARG` is imported and used correctly for `QMetaObject.invokeMethod`.

---

This completes the detailed execution plan for Stage 1. By following these steps, you will establish a robust, architecturally sound, and production-ready foundation for the entire SG-POS system, including the critical non-blocking asynchronous UI mechanism. This sets the stage for a smooth and efficient development of all subsequent features.

---

## **Stage 2: Core Data Entities - Products, Customers & Data Access**

**Objective:** To build the data management capabilities for the most fundamental business entities: Products and Customers. This involves creating the full Data Access Layer (`services`) and the basic UI for viewing and editing this data.

### **Phase 2.1: Data Transfer Objects (DTOs) for Core Entities**

#### **1. `app/business_logic/dto/product_dto.py`**

*   **File Path:** `app/business_logic/dto/product_dto.py`
*   **Purpose & Goals:** Defines the data contracts for product information exchanged between layers, ensuring structured and validated data.
*   **Interfaces:** `ProductBaseDTO`, `ProductCreateDTO`, `ProductUpdateDTO`, `ProductDTO`. All are Pydantic `BaseModel`s.
*   **Interactions:**
    *   `ProductManager` consumes `ProductCreateDTO`/`ProductUpdateDTO` from UI and returns `ProductDTO`.
    *   `ProductService` works with `ProductDTO` (or directly with ORM models mapped to/from DTOs).
    *   UI components (`ProductDialog`, `ProductView`) construct and consume these DTOs.
*   **Code Skeleton:**
    ```python
    # File: app/business_logic/dto/product_dto.py
    """
    Data Transfer Objects (DTOs) for the Product entity.

    These models define the data structure for passing product information between
    the different layers of the application, ensuring a clear and validated contract.
    """
    import uuid
    from decimal import Decimal
    from typing import Optional
    from pydantic import BaseModel, Field, validator

    class ProductBaseDTO(BaseModel):
        """Base DTO with common product fields."""
        sku: str = Field(..., min_length=1, max_length=100, description="Stock Keeping Unit")
        name: str = Field(..., min_length=1, max_length=255, description="Product name")
        description: Optional[str] = Field(None, description="Detailed description of the product")
        selling_price: Decimal = Field(..., gt=Decimal("0.00"), decimal_places=4, description="The retail price of the product")
        cost_price: Decimal = Field(..., ge=Decimal("0.00"), decimal_places=4, description="The cost of acquiring the product")
        gst_rate: Decimal = Field(Decimal("8.00"), ge=Decimal("0.00"), le=Decimal("100.00"), decimal_places=2, description="Goods and Services Tax rate (e.g., 8.00 for 8%)")
        track_inventory: bool = True
        is_active: bool = True
        category_id: Optional[uuid.UUID] = Field(None, description="UUID of the product's category")
        # supplier_id: Optional[uuid.UUID] = None # TODO: Add when Supplier module is implemented if needed here
        barcode: Optional[str] = Field(None, max_length=100, description="Product barcode (EAN, UPC, etc.)")
        reorder_point: int = Field(0, ge=0, description="Threshold quantity for reordering suggestions")

        # Pydantic validation: selling_price must be >= cost_price
        @validator('selling_price')
        def check_selling_price_not_less_than_cost_price(cls, v, values):
            if 'cost_price' in values and v < values['cost_price']:
                raise ValueError('Selling price cannot be less than cost price.')
            return v


    class ProductCreateDTO(ProductBaseDTO):
        """DTO for creating a new product."""
        # Inherits all fields and validations from ProductBaseDTO
        pass

    class ProductUpdateDTO(ProductBaseDTO):
        """DTO for updating an existing product."""
        # Inherits all fields and validations from ProductBaseDTO
        # Fields can be optional if partial updates are allowed (use Optional[Type] or exclude_unset=True)
        # For simplicity here, fields are required for update too, unless explicitly marked Optional.
        pass

    class ProductDTO(ProductBaseDTO):
        """DTO representing a full product record, including its unique ID."""
        id: uuid.UUID = Field(..., description="Unique identifier for the product")

        class Config:
            orm_mode = True # Allows creating DTO from a SQLAlchemy ORM model instance
            # from_attributes = True # Pydantic v2+ equivalent of orm_mode
    ```
*   **Acceptance Checklist:**
    *   [ ] `ProductBaseDTO`, `ProductCreateDTO`, `ProductUpdateDTO`, `ProductDTO` are defined.
    *   [ ] All product-related fields are included with correct Pydantic types and validation (e.g., `min_length`, `gt`, `ge`, `decimal_places`).
    *   [ ] `ProductDTO` includes the `id` field and `Config.orm_mode` (or `from_attributes=True`).
    *   [ ] `selling_price` validation (not less than `cost_price`) is implemented.
    *   [ ] Docstrings are clear.

#### **2. `app/business_logic/dto/customer_dto.py`**

*   **File Path:** `app/business_logic/dto/customer_dto.py`
*   **Purpose & Goals:** Defines the data contracts for customer information exchanged between layers.
*   **Interfaces:** `CustomerBaseDTO`, `CustomerCreateDTO`, `CustomerUpdateDTO`, `CustomerDTO`.
*   **Interactions:** Similar to product DTOs, used by `CustomerManager` and UI components.
*   **Code Skeleton:**
    ```python
    # File: app/business_logic/dto/customer_dto.py
    """Data Transfer Objects (DTOs) for the Customer entity."""
    import uuid
    from decimal import Decimal
    from typing import Optional
    from pydantic import BaseModel, Field, EmailStr

    class CustomerBaseDTO(BaseModel):
        """Base DTO with common customer fields."""
        customer_code: str = Field(..., min_length=1, max_length=50, description="Unique code for the customer")
        name: str = Field(..., min_length=1, max_length=255, description="Customer's full name")
        email: Optional[EmailStr] = Field(None, description="Customer's email address")
        phone: Optional[str] = Field(None, description="Customer's phone number")

    class CustomerCreateDTO(CustomerBaseDTO):
        """DTO for creating a new customer."""
        credit_limit: Decimal = Field(Decimal("0.00"), ge=0, decimal_places=2, description="Credit limit extended to the customer")

    class CustomerUpdateDTO(CustomerBaseDTO):
        """DTO for updating an existing customer."""
        # For updates, fields can be Optional if partial updates are common.
        # For now, keeping them required to match ProductUpdateDTO style.
        credit_limit: Decimal = Field(Decimal("0.00"), ge=0, decimal_places=2, description="Credit limit extended to the customer")
        is_active: bool = True # Assuming this is always updated or defaults to True

    class CustomerDTO(CustomerBaseDTO):
        """DTO representing a full customer record."""
        id: uuid.UUID = Field(..., description="Unique identifier for the customer")
        loyalty_points: int = Field(..., ge=0, description="Current loyalty points balance")
        credit_limit: Decimal = Field(..., ge=0, decimal_places=2, description="Credit limit extended to the customer")
        is_active: bool = True

        class Config:
            orm_mode = True # orm_mode is deprecated in Pydantic v2+, use from_attributes = True
            # from_attributes = True
    ```
*   **Acceptance Checklist:**
    *   [ ] `CustomerBaseDTO`, `CustomerCreateDTO`, `CustomerUpdateDTO`, `CustomerDTO` are defined.
    *   [ ] All customer-related fields are included with correct Pydantic types and validation.
    *   [ ] `CustomerDTO` includes the `id`, `loyalty_points`, `credit_limit`, `is_active` fields and `Config.orm_mode` (or `from_attributes=True`).
    *   [ ] Docstrings are clear.

### **Phase 2.2: Data Access Layer (`app/services/`)**

This phase implements the repositories for Products and Customers.

#### **1. `app/services/base_service.py`**

*   **File Path:** `app/services/base_service.py`
*   **Purpose & Goals:** Provides a consistent interface and reusable logic for common CRUD (Create, Read, Update, Delete) operations, reducing boilerplate code in concrete service implementations.
*   **Interfaces:** `BaseService(core: ApplicationCore, model: Type[ModelType])`. Methods: `async get_by_id(record_id)`, `async get_all()`, `async create(model_instance)`, `async update(model_instance)`, `async delete(record_id)`. All methods return `Result`.
*   **Interactions:**
    *   Inherited by all concrete service classes (e.g., `ProductService`, `CustomerService`).
    *   Uses `self.core.get_session()` for database interactions.
*   **Code Skeleton:**
    ```python
    # File: app/services/base_service.py
    """
    Abstract Base Class for all data services (Repositories).

    This provides a consistent interface and reusable logic for common CRUD
    operations, reducing boilerplate code in concrete service implementations.
    """
    from __future__ import annotations
    from typing import TYPE_CHECKING, Type, TypeVar, List
    from uuid import UUID
    import sqlalchemy as sa
    from sqlalchemy.future import select

    from app.core.result import Result, Success, Failure
    from app.core.exceptions import CoreException # For database specific errors

    if TYPE_CHECKING:
        from app.core.application_core import ApplicationCore
        from app.models.base import Base # Assuming Base is defined in app.models.base

    ModelType = TypeVar("ModelType", bound="Base")

    class BaseService:
        """
        Implements the Repository pattern for a given SQLAlchemy model.
        Provides generic CRUD operations.
        """
        def __init__(self, core: "ApplicationCore", model: Type[ModelType]):
            if not isinstance(model, type) or not issubclass(model, Base):
                raise ValueError("Model must be a SQLAlchemy declarative Base subclass.")
            self.core = core
            self.model = model

        async def get_by_id(self, record_id: UUID) -> Result[ModelType | None, str]:
            """
            Fetches a single record by its primary key (ID).
            Args:
                record_id: The UUID of the record to fetch.
            Returns:
                A Success containing the model instance or None if not found,
                or a Failure with an error message.
            """
            try:
                async with self.core.get_session() as session:
                    stmt = select(self.model).where(self.model.id == record_id)
                    result = await session.execute(stmt)
                    record = result.scalar_one_or_none()
                    return Success(record)
            except Exception as e:
                return Failure(f"Database error fetching {self.model.__tablename__} by ID: {e}")

        async def get_all(self, company_id: UUID, limit: int = 100, offset: int = 0) -> Result[List[ModelType], str]:
            """
            Fetches all records for the model with pagination, filtered by company_id.
            Args:
                company_id: The UUID of the company to filter by.
                limit: Maximum number of records to return.
                offset: Number of records to skip.
            Returns:
                A Success containing a list of model instances,
                or a Failure with an error message.
            """
            try:
                async with self.core.get_session() as session:
                    stmt = select(self.model).where(self.model.company_id == company_id).offset(offset).limit(limit)
                    result = await session.execute(stmt)
                    records = result.scalars().all()
                    return Success(records)
            except Exception as e:
                return Failure(f"Database error fetching all {self.model.__tablename__}: {e}")

        async def create(self, model_instance: ModelType) -> Result[ModelType, str]:
            """
            Saves a new model instance to the database.
            Args:
                model_instance: The ORM model instance to create.
            Returns:
                A Success containing the created model instance (with ID if newly generated),
                or a Failure with an error message.
            """
            try:
                async with self.core.get_session() as session:
                    session.add(model_instance)
                    await session.flush()  # Use flush to get generated IDs (e.g., UUID)
                    await session.refresh(model_instance) # Refresh to load default values from DB
                    return Success(model_instance)
            except sa.exc.IntegrityError as e:
                # Catch specific integrity errors for more user-friendly messages
                # Log full exception for debugging: print(f"Integrity Error: {e}")
                return Failure(f"Data integrity error creating {self.model.__tablename__}: Duplicate entry or missing reference.")
            except Exception as e:
                return Failure(f"Database error creating {self.model.__tablename__}: {e}")

        async def update(self, model_instance: ModelType) -> Result[ModelType, str]:
            """
            Updates an existing model instance in the database.
            Args:
                model_instance: The ORM model instance to update (must have ID set).
            Returns:
                A Success containing the updated model instance,
                or a Failure with an error message.
            """
            try:
                async with self.core.get_session() as session:
                    # Merge the detached instance into the current session if it's not already
                    session.add(model_instance) 
                    await session.flush()
                    await session.refresh(model_instance)
                    return Success(model_instance)
            except Exception as e:
                return Failure(f"Database error updating {self.model.__tablename__}: {e}")

        async def delete(self, record_id: UUID) -> Result[bool, str]:
            """
            Deletes a record by its ID.
            Args:
                record_id: The UUID of the record to delete.
            Returns:
                A Success indicating True if deleted, False if not found,
                or a Failure with an error message.
            """
            try:
                async with self.core.get_session() as session:
                    stmt = select(self.model).where(self.model.id == record_id)
                    result = await session.execute(stmt)
                    record = result.scalar_one_or_none()
                    if record:
                        await session.delete(record)
                        return Success(True)
                    return Success(False) # Record not found
            except sa.exc.IntegrityError as e:
                return Failure(f"Cannot delete {self.model.__tablename__}: It is referenced by other records. (Integrity error: {e})")
            except Exception as e:
                return Failure(f"Database error deleting {self.model.__tablename__}: {e}")
    ```
*   **Acceptance Checklist:**
    *   [ ] `BaseService` class is defined.
    *   [ ] Constructor takes `ApplicationCore` and `ModelType` as arguments.
    *   [ ] `get_by_id`, `get_all`, `create`, `update`, `delete` methods are implemented.
    *   [ ] All methods use `async with self.core.get_session()` for database interaction.
    *   [ ] Methods return `Result` objects (`Success` or `Failure`).
    *   [ ] `create` and `delete` methods handle `IntegrityError` for specific feedback.
    *   [ ] Type hinting is complete and accurate.
    *   [ ] Docstrings are comprehensive.

#### **2. `app/services/product_service.py`**

*   **File Path:** `app/services/product_service.py`
*   **Purpose & Goals:** Implements the Repository pattern for `Product` entities, encapsulating all database query logic specific to products.
*   **Interfaces:** `ProductService(core: ApplicationCore)`. Methods: `async get_by_sku(company_id, sku)`, `async search(company_id, term)`. Inherits CRUD from `BaseService`.
*   **Interactions:** Inherits from `BaseService`. Used by `ProductManager` to perform product-related database operations.
*   **Code Skeleton:**
    ```python
    # File: app/services/product_service.py
    """Data Access Service (Repository) for Product entities."""
    from __future__ import annotations
    from typing import TYPE_CHECKING, List
    from uuid import UUID
    import sqlalchemy as sa
    from sqlalchemy.future import select

    from app.core.result import Result, Success, Failure
    from app.models.product import Product # Import the Product ORM model
    from app.services.base_service import BaseService

    if TYPE_CHECKING:
        from app.core.application_core import ApplicationCore

    class ProductService(BaseService):
        """
        Handles all database interactions for the Product model.
        Inherits generic CRUD from BaseService.
        """

        def __init__(self, core: "ApplicationCore"):
            super().__init__(core, Product) # Initialize BaseService with the Product model

        async def get_by_sku(self, company_id: UUID, sku: str) -> Result[Product | None, str]:
            """
            Fetches a product by its unique SKU for a given company.
            Args:
                company_id: The UUID of the company.
                sku: The SKU of the product.
            Returns:
                A Success containing the Product ORM instance or None,
                or a Failure with an error message.
            """
            try:
                async with self.core.get_session() as session:
                    stmt = select(Product).where(
                        Product.company_id == company_id,
                        Product.sku == sku
                    )
                    result = await session.execute(stmt)
                    product = result.scalar_one_or_none()
                    return Success(product)
            except Exception as e:
                return Failure(f"Database error fetching product by SKU '{sku}': {e}")

        async def search(self, company_id: UUID, term: str, limit: int = 100, offset: int = 0) -> Result[List[Product], str]:
            """
            Searches for products by SKU, barcode, or name for a given company.
            Args:
                company_id: The UUID of the company.
                term: The search term.
                limit: Maximum number of records to return.
                offset: Number of records to skip.
            Returns:
                A Success containing a list of matching Product ORM instances,
                or a Failure with an error message.
            """
            try:
                async with self.core.get_session() as session:
                    search_pattern = f"%{term}%"
                    stmt = select(Product).where(
                        Product.company_id == company_id,
                        Product.is_active == True, # Only search active products
                        sa.or_(
                            Product.sku.ilike(search_pattern),
                            Product.barcode.ilike(search_pattern),
                            Product.name.ilike(search_pattern)
                        )
                    ).offset(offset).limit(limit)
                    result = await session.execute(stmt)
                    products = result.scalars().all()
                    return Success(products)
            except Exception as e:
                return Failure(f"Database error searching products: {e}")
    ```
*   **Acceptance Checklist:**
    *   [ ] `ProductService` inherits from `BaseService` and is initialized with the `Product` model.
    *   [ ] `get_by_sku` method is implemented.
    *   [ ] `search` method is implemented, supporting search by SKU, barcode, or name.
    *   [ ] All methods use `async with self.core.get_session()` and return `Result`.
    *   [ ] Type hinting is complete.

#### **3. `app/services/customer_service.py`**

*   **File Path:** `app/services/customer_service.py`
*   **Purpose & Goals:** Implements the Repository pattern for `Customer` entities.
*   **Interfaces:** `CustomerService(core: ApplicationCore)`. Methods: `async get_by_code(company_id, code)`, `async search(company_id, term)`. Inherits CRUD from `BaseService`.
*   **Interactions:** Inherits from `BaseService`. Used by `CustomerManager`.
*   **Code Skeleton:**
    ```python
    # File: app/services/customer_service.py
    """Data Access Service (Repository) for Customer entities."""
    from __future__ import annotations
    from typing import TYPE_CHECKING, List
    from uuid import UUID
    import sqlalchemy as sa
    from sqlalchemy.future import select

    from app.core.result import Result, Success, Failure
    from app.models.customer import Customer # Import the Customer ORM model
    from app.services.base_service import BaseService

    if TYPE_CHECKING:
        from app.core.application_core import ApplicationCore

    class CustomerService(BaseService):
        """
        Handles all database interactions for the Customer model.
        Inherits generic CRUD from BaseService.
        """

        def __init__(self, core: "ApplicationCore"):
            super().__init__(core, Customer) # Initialize BaseService with the Customer model

        async def get_by_code(self, company_id: UUID, code: str) -> Result[Customer | None, str]:
            """
            Fetches a customer by their unique code for a given company.
            Args:
                company_id: The UUID of the company.
                code: The customer's unique code.
            Returns:
                A Success containing the Customer ORM instance or None,
                or a Failure with an error message.
            """
            try:
                async with self.core.get_session() as session:
                    stmt = select(Customer).where(
                        Customer.company_id == company_id,
                        Customer.customer_code == code
                    )
                    result = await session.execute(stmt)
                    customer = result.scalar_one_or_none()
                    return Success(customer)
            except Exception as e:
                return Failure(f"Database error fetching customer by code '{code}': {e}")

        async def search(self, company_id: UUID, term: str, limit: int = 100, offset: int = 0) -> Result[List[Customer], str]:
            """
            Searches for customers by code, name, email, or phone for a given company.
            Args:
                company_id: The UUID of the company.
                term: The search term.
                limit: Maximum number of records to return.
                offset: Number of records to skip.
            Returns:
                A Success containing a list of matching Customer ORM instances,
                or a Failure with an error message.
            """
            try:
                async with self.core.get_session() as session:
                    search_pattern = f"%{term}%"
                    stmt = select(Customer).where(
                        Customer.company_id == company_id,
                        Customer.is_active == True, # Only search active customers
                        sa.or_(
                            Customer.customer_code.ilike(search_pattern),
                            Customer.name.ilike(search_pattern),
                            Customer.email.ilike(search_pattern),
                            Customer.phone.ilike(search_pattern)
                        )
                    ).offset(offset).limit(limit)
                    result = await session.execute(stmt)
                    customers = result.scalars().all()
                    return Success(customers)
            except Exception as e:
                return Failure(f"Database error searching customers: {e}")
    ```
*   **Acceptance Checklist:**
    *   [ ] `CustomerService` inherits from `BaseService` and is initialized with the `Customer` model.
    *   [ ] `get_by_code` method is implemented.
    *   [ ] `search` method is implemented, supporting search by code, name, email, or phone.
    *   [ ] All methods use `async with self.core.get_session()` and return `Result`.
    *   [ ] Type hinting is complete.

### **Phase 2.3: Business Logic Layer (`app/business_logic/`)**

This phase implements the managers for Products and Customers, which orchestrate operations using the services and enforce business rules.

#### **1. `app/business_logic/managers/base_manager.py`**

*   **File Path:** `app/business_logic/managers/base_manager.py`
*   **Purpose & Goals:** Provides a common base class for all business logic managers, giving them access to the `ApplicationCore` for dependency resolution.
*   **Interfaces:** `BaseManager(core: ApplicationCore)` class.
*   **Interactions:** All concrete manager classes will inherit from `BaseManager`.
*   **Code Skeleton:**
    ```python
    # File: app/business_logic/managers/base_manager.py
    """Abstract Base Class for all business logic managers."""
    from __future__ import annotations
    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from app.core.application_core import ApplicationCore

    class BaseManager:
        """
        Provides managers with access to the application core.
        All managers should inherit from this class.
        """
        def __init__(self, core: "ApplicationCore"):
            self.core = core
    ```
*   **Acceptance Checklist:**
    *   [ ] `BaseManager` class is defined.
    *   [ ] Its constructor accepts an `ApplicationCore` instance and stores it.
    *   [ ] Type hinting is correct.

#### **2. `app/business_logic/managers/product_manager.py`**

*   **File Path:** `app/business_logic/managers/product_manager.py`
*   **Purpose & Goals:** Orchestrates product-related workflows, enforces business rules, and coordinates with the data access layer (`ProductService`).
*   **Interfaces:** `ProductManager(core: ApplicationCore)`. Methods: `async create_product(company_id, dto)`, `async update_product(product_id, dto)`, `async get_product(product_id)`, `async search_products(company_id, term)`. All methods return `Result`.
*   **Interactions:**
    *   Lazy-loads `ProductService` via `self.core.product_service`.
    *   Consumes `ProductCreateDTO`/`ProductUpdateDTO` from UI, returns `ProductDTO`.
    *   Implements business validation (selling price vs. cost, duplicate SKU).
*   **Code Skeleton:**
    ```python
    # File: app/business_logic/managers/product_manager.py
    """
    Business Logic Manager for Product operations.

    This manager orchestrates product-related workflows, enforces business rules,
    and coordinates with the data access layer (ProductService).
    """
    from __future__ import annotations
    from typing import TYPE_CHECKING, List
    from uuid import UUID

    from app.core.result import Result, Success, Failure
    from app.business_logic.managers.base_manager import BaseManager
    from app.business_logic.dto.product_dto import ProductDTO, ProductCreateDTO, ProductUpdateDTO
    from app.models.product import Product # Import the ORM model

    if TYPE_CHECKING:
        from app.core.application_core import ApplicationCore
        from app.services.product_service import ProductService

    class ProductManager(BaseManager):
        """Orchestrates business logic for products."""

        @property
        def product_service(self) -> "ProductService":
            """Lazy-loads the ProductService instance from the core."""
            return self.core.product_service

        async def create_product(self, company_id: UUID, dto: ProductCreateDTO) -> Result[ProductDTO, str]:
            """
            Creates a new product after validating business rules.
            Rule: A product's selling price should not be less than its cost price.
            Rule: SKU must be unique for the company.
            Args:
                company_id: The UUID of the company creating the product.
                dto: The ProductCreateDTO containing product data.
            Returns:
                A Success with the created ProductDTO, or a Failure with an error message.
            """
            # Business rule: selling price validation (also handled by Pydantic, but good to double check here)
            if dto.selling_price < dto.cost_price:
                return Failure("Validation Error: Selling price cannot be less than cost price.")

            # Business rule: Check for duplicate SKU
            existing_product_result = await self.product_service.get_by_sku(company_id, dto.sku)
            if isinstance(existing_product_result, Failure):
                return existing_product_result # Propagate database error
            if existing_product_result.value is not None:
                return Failure(f"Business Rule Error: Product with SKU '{dto.sku}' already exists.")

            # Convert DTO to ORM model instance
            new_product = Product(company_id=company_id, **dto.dict())
            
            # Persist via service
            create_result = await self.product_service.create(new_product)
            if isinstance(create_result, Failure):
                return create_result # Propagate database error from service

            return Success(ProductDTO.from_orm(create_result.value))

        async def update_product(self, product_id: UUID, dto: ProductUpdateDTO) -> Result[ProductDTO, str]:
            """
            Updates an existing product after validating business rules.
            Args:
                product_id: The UUID of the product to update.
                dto: The ProductUpdateDTO containing updated product data.
            Returns:
                A Success with the updated ProductDTO, or a Failure with an error message.
            """
            # Business rule: selling price validation
            if dto.selling_price < dto.cost_price:
                return Failure("Validation Error: Selling price cannot be less than cost price.")

            # Retrieve existing product
            product_result = await self.product_service.get_by_id(product_id)
            if isinstance(product_result, Failure):
                return product_result
            
            product = product_result.value
            if not product:
                return Failure("Product not found.")

            # Business rule: If SKU is changed, check for duplication (only if new SKU is different from old)
            if dto.sku != product.sku:
                existing_product_result = await self.product_service.get_by_sku(product.company_id, dto.sku)
                if isinstance(existing_product_result, Failure):
                    return existing_product_result
                if existing_product_result.value is not None and existing_product_result.value.id != product_id:
                    return Failure(f"Business Rule Error: New SKU '{dto.sku}' is already in use by another product.")

            # Update fields from DTO (Pydantic's .dict(exclude_unset=True) can be useful for partial updates)
            for field, value in dto.dict().items(): # Assuming all fields are always present in ProductUpdateDTO
                setattr(product, field, value)

            # Persist update via service
            update_result = await self.product_service.update(product)
            if isinstance(update_result, Failure):
                return update_result # Propagate database error
            
            return Success(ProductDTO.from_orm(update_result.value))

        async def get_product(self, product_id: UUID) -> Result[ProductDTO, str]:
            """
            Retrieves a single product by its ID.
            Args:
                product_id: The UUID of the product.
            Returns:
                A Success with the ProductDTO, or a Failure if not found or a database error occurs.
            """
            result = await self.product_service.get_by_id(product_id)
            if isinstance(result, Failure):
                return result
            
            product = result.value
            if not product:
                return Failure("Product not found.")
                
            return Success(ProductDTO.from_orm(product))

        async def get_all_products(self, company_id: UUID, limit: int = 100, offset: int = 0) -> Result[List[ProductDTO], str]:
            """
            Retrieves all products for a given company.
            Args:
                company_id: The UUID of the company.
                limit: Max number of products to return.
                offset: Number of products to skip.
            Returns:
                A Success with a list of ProductDTOs, or a Failure.
            """
            result = await self.product_service.get_all(company_id, limit, offset)
            if isinstance(result, Failure):
                return result
            
            return Success([ProductDTO.from_orm(p) for p in result.value])
        
        async def search_products(self, company_id: UUID, term: str, limit: int = 100, offset: int = 0) -> Result[List[ProductDTO], str]:
            """
            Searches for products by SKU, barcode, or name for a given company.
            Args:
                company_id: The UUID of the company.
                term: The search term.
                limit: Max number of products to return.
                offset: Number of products to skip.
            Returns:
                A Success with a list of matching ProductDTOs, or a Failure.
            """
            result = await self.product_service.search(company_id, term, limit, offset)
            if isinstance(result, Failure):
                return result
            
            return Success([ProductDTO.from_orm(p) for p in result.value])

        async def deactivate_product(self, product_id: UUID) -> Result[bool, str]:
            """
            Deactivates a product (soft delete) by setting its is_active flag to False.
            Args:
                product_id: The UUID of the product to deactivate.
            Returns:
                A Success with True if deactivated, False if not found, or a Failure.
            """
            product_result = await self.product_service.get_by_id(product_id)
            if isinstance(product_result, Failure):
                return product_result
            
            product = product_result.value
            if not product:
                return Failure("Product not found.")
            
            product.is_active = False # Set the flag
            update_result = await self.product_service.update(product)
            if isinstance(update_result, Failure):
                return update_result
            
            return Success(True)

        # TODO: Add delete_product (hard delete, usually for non-production data or strict rules)
        # TODO: Add logic for managing product variants once ProductVariant model is defined.
        # TODO: Add logic for managing categories.
    ```
*   **Acceptance Checklist:**
    *   [ ] `ProductManager` inherits from `BaseManager`.
    *   [ ] `product_service` property lazy-loads from `self.core`.
    *   [ ] `create_product` method implemented with `selling_price` vs `cost_price` validation and duplicate SKU check.
    *   [ ] `update_product` method implemented with similar validations and handles SKU change correctly.
    *   [ ] `get_product`, `get_all_products`, `search_products`, `deactivate_product` methods are implemented.
    *   [ ] All methods consume DTOs, return `Result` objects, and map ORM models to DTOs for output.
    *   [ ] Type hinting is complete and accurate.
    *   [ ] Docstrings are comprehensive.

#### **3. `app/business_logic/managers/customer_manager.py`**

*   **File Path:** `app/business_logic/managers/customer_manager.py`
*   **Purpose & Goals:** Orchestrates customer-related workflows and enforces business rules.
*   **Interfaces:** `CustomerManager(core: ApplicationCore)`. Methods: `async create_customer(company_id, dto)`, `async update_customer(customer_id, dto)`, `async get_customer(customer_id)`, `async search_customers(company_id, term)`. All methods return `Result`.
*   **Interactions:** Lazy-loads `CustomerService`. Consumes/returns customer DTOs.
*   **Code Skeleton:**
    ```python
    # File: app/business_logic/managers/customer_manager.py
    """Business Logic Manager for Customer operations."""
    from __future__ import annotations
    from typing import TYPE_CHECKING, List
    from uuid import UUID

    from app.core.result import Result, Success, Failure
    from app.business_logic.managers.base_manager import BaseManager
    from app.business_logic.dto.customer_dto import CustomerDTO, CustomerCreateDTO, CustomerUpdateDTO

    if TYPE_CHECKING:
        from app.core.application_core import ApplicationCore
        from app.services.customer_service import CustomerService

    class CustomerManager(BaseManager):
        """Orchestrates business logic for customers."""

        @property
        def customer_service(self) -> "CustomerService":
            """Lazy-loads the CustomerService instance from the core."""
            return self.core.customer_service

        async def create_customer(self, company_id: UUID, dto: CustomerCreateDTO) -> Result[CustomerDTO, str]:
            """
            Creates a new customer.
            Business rule: Customer code must be unique for the company.
            Args:
                company_id: The UUID of the company.
                dto: The CustomerCreateDTO containing customer data.
            Returns:
                A Success with the created CustomerDTO, or a Failure with an error message.
            """
            # Business rule: Check for duplicate customer code
            existing_result = await self.customer_service.get_by_code(company_id, dto.customer_code)
            if isinstance(existing_result, Failure):
                return existing_result # Propagate database error
            if existing_result.value is not None:
                return Failure(f"Business Rule Error: Customer with code '{dto.customer_code}' already exists.")

            # TODO: Consider checking for duplicate email if emails are meant to be unique.

            from app.models.customer import Customer # Import ORM model locally
            new_customer = Customer(company_id=company_id, **dto.dict())
            
            create_result = await self.customer_service.create(new_customer)
            if isinstance(create_result, Failure):
                return create_result

            return Success(CustomerDTO.from_orm(create_result.value))

        async def update_customer(self, customer_id: UUID, dto: CustomerUpdateDTO) -> Result[CustomerDTO, str]:
            """
            Updates an existing customer.
            Args:
                customer_id: The UUID of the customer to update.
                dto: The CustomerUpdateDTO containing updated data.
            Returns:
                A Success with the updated CustomerDTO, or a Failure.
            """
            customer_result = await self.customer_service.get_by_id(customer_id)
            if isinstance(customer_result, Failure):
                return customer_result
            
            customer = customer_result.value
            if not customer:
                return Failure("Customer not found.")

            # Business rule: If customer code is changed, check for duplication
            if dto.customer_code != customer.customer_code:
                existing_result = await self.customer_service.get_by_code(customer.company_id, dto.customer_code)
                if isinstance(existing_result, Failure):
                    return existing_result
                if existing_result.value is not None and existing_result.value.id != customer_id:
                    return Failure(f"Business Rule Error: New customer code '{dto.customer_code}' is already in use by another customer.")

            # Update fields from DTO
            for field, value in dto.dict().items():
                setattr(customer, field, value)

            update_result = await self.customer_service.update(customer)
            if isinstance(update_result, Failure):
                return update_result
            
            return Success(CustomerDTO.from_orm(update_result.value))

        async def get_customer(self, customer_id: UUID) -> Result[CustomerDTO, str]:
            """Retrieves a single customer by ID."""
            result = await self.customer_service.get_by_id(customer_id)
            if isinstance(result, Failure):
                return result
            
            customer = result.value
            if not customer:
                return Failure("Customer not found.")
                
            return Success(CustomerDTO.from_orm(customer))

        async def get_all_customers(self, company_id: UUID, limit: int = 100, offset: int = 0) -> Result[List[CustomerDTO], str]:
            """Retrieves all customers for a given company."""
            result = await self.customer_service.get_all(company_id, limit, offset)
            if isinstance(result, Failure):
                return result
            
            return Success([CustomerDTO.from_orm(c) for c in result.value])
        
        async def search_customers(self, company_id: UUID, term: str, limit: int = 100, offset: int = 0) -> Result[List[CustomerDTO], str]:
            """Searches for customers by code, name, email, or phone."""
            result = await self.customer_service.search(company_id, term, limit, offset)
            if isinstance(result, Failure):
                return result
            
            return Success([CustomerDTO.from_orm(c) for c in result.value])

        async def deactivate_customer(self, customer_id: UUID) -> Result[bool, str]:
            """Deactivates a customer (soft delete)."""
            customer_result = await self.customer_service.get_by_id(customer_id)
            if isinstance(customer_result, Failure):
                return customer_result
            
            customer = customer_result.value
            if not customer:
                return Failure("Customer not found.")
            
            customer.is_active = False
            update_result = await self.customer_service.update(customer)
            if isinstance(update_result, Failure):
                return update_result
            
            return Success(True)

        # TODO: Implement add_loyalty_points_for_sale (moved here from Stage 4 part 1 sample as it's a core customer function)
        # This will be completed in Stage 4
        async def add_loyalty_points_for_sale(self, customer_id: UUID, sale_total: Decimal) -> Result[int, str]:
            """
            Calculates and adds loyalty points for a completed sale.
            Business Rule: 1 point for every S$10 spent.
            Args:
                customer_id: The UUID of the customer.
                sale_total: The total amount of the sale.
            Returns:
                A Success with the new loyalty point total, or a Failure.
            """
            # This logic will be fully fleshed out in Stage 4.
            # For now, it's a placeholder.
            return Failure("add_loyalty_points_for_sale not yet implemented.")
            # TODO: Full implementation in Stage 4
    ```
*   **Acceptance Checklist:**
    *   [ ] `CustomerManager` inherits from `BaseManager`.
    *   [ ] `customer_service` property lazy-loads from `self.core`.
    *   [ ] `create_customer` method implemented with duplicate code check.
    *   [ ] `update_customer` method implemented with similar validations.
    *   [ ] `get_customer`, `get_all_customers`, `search_customers`, `deactivate_customer` methods are implemented.
    *   [ ] All methods consume DTOs, return `Result` objects, and map ORM models to DTOs.
    *   [ ] `add_loyalty_points_for_sale` is a placeholder, as per the PMD.
    *   [ ] Type hinting is complete.

### **Phase 2.4: Presentation Layer (UI) for Core Entities (`app/ui/`)**

This phase creates the basic UI screens for managing products and customers.

#### **1. `app/ui/dialogs/product_dialog.py`**

*   **File Path:** `app/ui/dialogs/product_dialog.py`
*   **Purpose & Goals:** A `QDialog` for creating and editing Product entities. It collects user input, constructs DTOs, and sends them to the `ProductManager` via the `async_bridge` for processing.
*   **Interfaces:** `ProductDialog(core: ApplicationCore, product: ProductDTO | None = None)`. Returns `ProductCreateDTO` or `ProductUpdateDTO` from `get_dto()`.
*   **Interactions:**
    *   Receives `ApplicationCore` instance.
    *   Uses `self.core.async_worker.run_task()` to call `product_manager.create_product` or `update_product` asynchronously.
    *   Connects to `self.async_worker.task_finished` or uses a specific `on_done_callback` for results.
    *   Displays `QMessageBox` for success/failure.
*   **Code Skeleton:**
    ```python
    # File: app/ui/dialogs/product_dialog.py
    """A QDialog for creating and editing Product entities."""
    import asyncio
    from decimal import Decimal
    from typing import Optional, Any
    import uuid # Needed for placeholder if not fully integrated yet

    from PySide6.QtWidgets import (
        QDialog, QVBoxLayout, QFormLayout, QLineEdit,
        QDoubleSpinBox, QCheckBox, QDialogButtonBox, QMessageBox
    )
    from PySide6.QtCore import Slot, Signal, QObject

    from app.business_logic.dto.product_dto import ProductCreateDTO, ProductUpdateDTO, ProductDTO
    from app.core.application_core import ApplicationCore
    from app.core.result import Success, Failure
    from app.core.async_bridge import AsyncWorker # For type hinting

    class ProductDialog(QDialog):
        """A dialog for creating or editing a product."""

        product_operation_completed = Signal(bool, str) # Signal for ProductView to refresh

        def __init__(self, core: ApplicationCore, product: Optional[ProductDTO] = None, parent: Optional[QObject] = None):
            super().__init__(parent)
            self.core = core
            self.async_worker: AsyncWorker = core.async_worker # Get the async worker
            self.product = product
            self.is_edit_mode = product is not None

            self.setWindowTitle("Edit Product" if self.is_edit_mode else "Add New Product")
            self.setMinimumWidth(400)

            self._setup_ui()
            self._connect_signals()

            if self.is_edit_mode:
                self._populate_form()

        def _setup_ui(self):
            """Initializes the UI widgets and layout."""
            # --- Create Widgets ---
            self.sku_input = QLineEdit()
            self.name_input = QLineEdit()
            self.description_input = QLineEdit() # Assuming simple QLineEdit for description
            self.selling_price_input = QDoubleSpinBox()
            self.selling_price_input.setRange(0, 999999.99)
            self.selling_price_input.setDecimals(2)
            self.cost_price_input = QDoubleSpinBox()
            self.cost_price_input.setRange(0, 999999.99)
            self.cost_price_input.setDecimals(2)
            self.gst_rate_input = QDoubleSpinBox() # For GST rate
            self.gst_rate_input.setRange(0, 100.00)
            self.gst_rate_input.setDecimals(2)
            self.track_inventory_checkbox = QCheckBox("Track Inventory")
            self.is_active_checkbox = QCheckBox("Is Active")

            # --- Layout ---
            form_layout = QFormLayout()
            form_layout.addRow("SKU:", self.sku_input)
            form_layout.addRow("Name:", self.name_input)
            form_layout.addRow("Description:", self.description_input)
            form_layout.addRow("Selling Price (S$):", self.selling_price_input)
            form_layout.addRow("Cost Price (S$):", self.cost_price_input)
            form_layout.addRow("GST Rate (%):", self.gst_rate_input)
            form_layout.addRow(self.track_inventory_checkbox)
            form_layout.addRow(self.is_active_checkbox)
            
            # TODO: Add category selection (e.g., QComboBox populated from category_manager)
            # TODO: Add barcode input
            # TODO: Add reorder point input

            self.button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
            self.button_box.button(QDialogButtonBox.Save).setText("Save Product")
            
            main_layout = QVBoxLayout(self)
            main_layout.addLayout(form_layout)
            main_layout.addWidget(self.button_box)

            # Set defaults for new product
            if not self.is_edit_mode:
                self.gst_rate_input.setValue(8.00) # Default GST rate
                self.track_inventory_checkbox.setChecked(True)
                self.is_active_checkbox.setChecked(True)

        def _connect_signals(self):
            """Connects UI signals to slots."""
            self.button_box.accepted.connect(self._on_save_accepted)
            self.button_box.rejected.connect(self.reject)

        def _populate_form(self):
            """Populates the form fields with existing product data in edit mode."""
            if self.product:
                self.sku_input.setText(self.product.sku)
                self.name_input.setText(self.product.name)
                self.description_input.setText(self.product.description or "")
                self.selling_price_input.setValue(float(self.product.selling_price))
                self.cost_price_input.setValue(float(self.product.cost_price))
                self.gst_rate_input.setValue(float(self.product.gst_rate))
                self.track_inventory_checkbox.setChecked(self.product.track_inventory)
                self.is_active_checkbox.setChecked(self.product.is_active)
                # TODO: Populate category, barcode, reorder point

        def _get_dto(self) -> Union[ProductCreateDTO, ProductUpdateDTO]:
            """Constructs a DTO from the current form data."""
            common_data = {
                "sku": self.sku_input.text().strip(),
                "name": self.name_input.text().strip(),
                "description": self.description_input.text().strip() or None,
                "selling_price": Decimal(str(self.selling_price_input.value())),
                "cost_price": Decimal(str(self.cost_price_input.value())),
                "gst_rate": Decimal(str(self.gst_rate_input.value())),
                "track_inventory": self.track_inventory_checkbox.isChecked(),
                "is_active": self.is_active_checkbox.isChecked(),
                # TODO: Add category_id, barcode, reorder_point
            }
            if self.is_edit_mode:
                return ProductUpdateDTO(**common_data)
            else:
                return ProductCreateDTO(**common_data)

        @Slot()
        def _on_save_accepted(self):
            """Handles the save action, triggering the async operation."""
            dto = self._get_dto()
            company_id = self.core.current_company_id # Get current company ID from core

            try:
                if self.is_edit_mode:
                    coro = self.core.product_manager.update_product(self.product.id, dto)
                    success_msg = f"Product '{dto.name}' updated successfully!"
                    error_prefix = "Failed to update product:"
                else:
                    coro = self.core.product_manager.create_product(company_id, dto)
                    success_msg = f"Product '{dto.name}' created successfully!"
                    error_prefix = "Failed to create product:"

                # Use the async_bridge to run the task in the background
                self.button_box.button(QDialogButtonBox.Save).setEnabled(False) # Disable button during operation
                
                def _on_done(result: Any, error: Optional[Exception]):
                    self.button_box.button(QDialogButtonBox.Save).setEnabled(True) # Re-enable button
                    if error:
                        QMessageBox.critical(self, "Error", f"{error_prefix}\n{error}")
                        self.product_operation_completed.emit(False, str(error))
                    elif isinstance(result, Success):
                        QMessageBox.information(self, "Success", success_msg)
                        self.product_operation_completed.emit(True, success_msg)
                        self.accept() # Close the dialog on success
                    elif isinstance(result, Failure): # Business logic failure
                        QMessageBox.warning(self, "Validation Error", f"{error_prefix}\n{result.error}")
                        self.product_operation_completed.emit(False, result.error)
                    else: # Unexpected result type
                        QMessageBox.critical(self, "Internal Error", f"Unexpected result type from manager: {type(result)}")
                        self.product_operation_completed.emit(False, "An unexpected internal error occurred.")

                self.async_worker.run_task(coro, on_done_callback=_on_done)

            except Exception as e:
                QMessageBox.critical(self, "Application Error", f"An internal error prevented the operation:\n{e}")
                self.product_operation_completed.emit(False, f"Internal error: {e}")
                self.button_box.button(QDialogButtonBox.Save).setEnabled(True) # Re-enable in case of sync error
    ```
*   **Acceptance Checklist:**
    *   [ ] Constructor accepts `ApplicationCore` and an optional `ProductDTO`.
    *   [ ] `_setup_ui` creates form widgets (`QLineEdit`, `QDoubleSpinBox`, `QCheckBox`).
    *   [ ] `_connect_signals` connects `button_box.accepted` to `_on_save_accepted`.
    *   [ ] `_populate_form` correctly loads `ProductDTO` data into form fields in edit mode.
    *   [ ] `_get_dto` constructs `ProductCreateDTO` or `ProductUpdateDTO` from form data.
    *   [ ] `_on_save_accepted` calls `product_manager.create_product` or `update_product` via `self.async_worker.run_task()`.
    *   [ ] The `on_done_callback` correctly handles `Success` and `Failure` results using `QMessageBox` for feedback.
    *   [ ] Save button is disabled during async operation and re-enabled afterward.
    *   [ ] Dialog closes on successful operation (`self.accept()`).
    *   [ ] `product_operation_completed` signal is emitted correctly with success/failure status.

#### **2. `app/ui/views/product_view.py`**

*   **File Path:** `app/ui/views/product_view.py`
*   **Purpose & Goals:** Provides the main user interface for managing products, including listing, searching, adding, editing, and deactivating. It interacts with the `ProductManager` via the `async_bridge` and uses a `QAbstractTableModel` for dynamic display.
*   **Interfaces:** `ProductView(core: ApplicationCore)`.
*   **Interactions:**
    *   Receives `ApplicationCore` instance.
    *   Manages a `ProductTableModel` (a `QAbstractTableModel`).
    *   Calls `product_manager.get_all_products` and `search_products` via `async_worker.run_task()`.
    *   Launches `ProductDialog` for add/edit operations.
    *   Handles signals from `ProductDialog` to refresh its data.
*   **Code Skeleton:**
    ```python
    # File: app/ui/views/product_view.py
    """The main view for managing products."""
    import uuid
    from decimal import Decimal
    from typing import List, Any, Optional
    
    from PySide6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableView,
        QMessageBox, QLineEdit, QHeaderView, QSizePolicy
    )
    from PySide6.QtCore import Slot, Signal, QAbstractTableModel, QModelIndex, Qt, QObject

    from app.core.application_core import ApplicationCore
    from app.core.result import Success, Failure
    from app.business_logic.dto.product_dto import ProductDTO
    from app.ui.dialogs.product_dialog import ProductDialog
    from app.core.async_bridge import AsyncWorker

    class ProductTableModel(QAbstractTableModel):
        """A Qt Table Model for displaying ProductDTOs."""
        
        HEADERS = ["SKU", "Name", "Selling Price", "Cost Price", "GST Rate", "Active", "Track Inv."]

        def __init__(self, products: List[ProductDTO], parent: Optional[QObject] = None):
            super().__init__(parent)
            self._products = products

        def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
            return len(self._products)

        def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
            return len(self.HEADERS)

        def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
            if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
                return self.HEADERS[section]
            return None

        def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
            if not index.isValid():
                return None
            
            product = self._products[index.row()]
            col = index.column()

            if role == Qt.ItemDataRole.DisplayRole:
                if col == 0: return product.sku
                if col == 1: return product.name
                if col == 2: return f"S${product.selling_price:.2f}"
                if col == 3: return f"S${product.cost_price:.2f}"
                if col == 4: return f"{product.gst_rate:.2f}%"
                if col == 5: return "Yes" if product.is_active else "No"
                if col == 6: return "Yes" if product.track_inventory else "No"
            
            if role == Qt.ItemDataRole.TextAlignmentRole:
                if col in [2, 3, 4]: # Price/Rate columns
                    return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
                if col in [5, 6]: # Boolean columns
                    return Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter
            
            return None

        def get_product_at_row(self, row: int) -> Optional[ProductDTO]:
            """Returns the ProductDTO at the given row index."""
            if 0 <= row < len(self._products):
                return self._products[row]
            return None

        def refresh_data(self, new_products: List[ProductDTO]):
            """Updates the model with new data and notifies views."""
            self.beginResetModel()
            self._products = new_products
            self.endResetModel()

    class ProductView(QWidget):
        """A view widget to display and manage the product catalog."""
        
        def __init__(self, core: ApplicationCore, parent: Optional[QObject] = None):
            super().__init__(parent)
            self.core = core
            self.async_worker: AsyncWorker = core.async_worker

            self._setup_ui()
            self._connect_signals()
            self._load_products()

        def _setup_ui(self):
            """Initializes the UI widgets and layout."""
            # --- Search and Action Buttons ---
            top_layout = QHBoxLayout()
            self.search_input = QLineEdit()
            self.search_input.setPlaceholderText("Search products by SKU, name, or barcode...")
            self.add_button = QPushButton("Add New Product")
            self.edit_button = QPushButton("Edit Selected")
            self.delete_button = QPushButton("Deactivate Selected") # Soft delete

            top_layout.addWidget(self.search_input, 1) # Take more space
            top_layout.addStretch()
            top_layout.addWidget(self.add_button)
            top_layout.addWidget(self.edit_button)
            top_layout.addWidget(self.delete_button)
            
            # --- Product Table ---
            self.table_view = QTableView()
            self.product_model = ProductTableModel([]) # Initialize with empty data
            self.table_view.setModel(self.product_model)
            self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            self.table_view.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
            self.table_view.setSelectionMode(QTableView.SelectionMode.SingleSelection)
            self.table_view.setSortingEnabled(True) # Enable sorting if supported by model

            # --- Main Layout ---
            main_layout = QVBoxLayout(self)
            main_layout.addLayout(top_layout)
            main_layout.addWidget(self.table_view)

            self.setLayout(main_layout)
            self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)


        def _connect_signals(self):
            """Connects UI signals to slots."""
            self.add_button.clicked.connect(self._on_add_product)
            self.edit_button.clicked.connect(self._on_edit_product)
            self.delete_button.clicked.connect(self._on_deactivate_product)
            self.search_input.textChanged.connect(self._on_search_products)
            self.table_view.doubleClicked.connect(self._on_edit_product) # Double click to edit

        def _get_selected_product(self) -> Optional[ProductDTO]:
            """Helper to get the currently selected product from the table."""
            selected_indexes = self.table_view.selectionModel().selectedRows()
            if selected_indexes:
                row = selected_indexes[0].row()
                return self.product_model.get_product_at_row(row)
            return None

        @Slot()
        def _load_products(self, search_term: str = ""):
            """Loads product data asynchronously into the table model."""
            company_id = self.core.current_company_id

            def _on_done(result: Any, error: Optional[Exception]):
                if error:
                    QMessageBox.critical(self, "Load Error", f"Failed to load products: {error}")
                elif isinstance(result, Success):
                    self.product_model.refresh_data(result.value)
                elif isinstance(result, Failure):
                    QMessageBox.warning(self, "Load Failed", f"Could not load products: {result.error}")
            
            if search_term:
                coro = self.core.product_manager.search_products(company_id, search_term)
            else:
                coro = self.core.product_manager.get_all_products(company_id)
            
            self.async_worker.run_task(coro, on_done_callback=_on_done)

        @Slot()
        def _on_add_product(self):
            """Opens the dialog to add a new product."""
            dialog = ProductDialog(self.core, parent=self)
            dialog.product_operation_completed.connect(self._handle_product_dialog_result)
            dialog.exec() # This is a blocking call for the dialog, not the async operation

        @Slot()
        def _on_edit_product(self):
            """Opens the dialog to edit the selected product."""
            selected_product = self._get_selected_product()
            if not selected_product:
                QMessageBox.information(self, "No Selection", "Please select a product to edit.")
                return

            dialog = ProductDialog(self.core, product=selected_product, parent=self)
            dialog.product_operation_completed.connect(self._handle_product_dialog_result)
            dialog.exec()

        @Slot()
        def _on_deactivate_product(self):
            """Deactivates the selected product."""
            selected_product = self._get_selected_product()
            if not selected_product:
                QMessageBox.information(self, "No Selection", "Please select a product to deactivate.")
                return
            
            reply = QMessageBox.question(self, "Confirm Deactivation",
                                        f"Are you sure you want to deactivate product '{selected_product.name}' (SKU: {selected_product.sku})?",
                                        QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.No:
                return

            def _on_done(result: Any, error: Optional[Exception]):
                if error:
                    QMessageBox.critical(self, "Error", f"Failed to deactivate product: {error}")
                elif isinstance(result, Success) and result.value:
                    QMessageBox.information(self, "Success", f"Product '{selected_product.name}' deactivated.")
                    self._load_products() # Refresh the list
                elif isinstance(result, Failure):
                    QMessageBox.warning(self, "Deactivation Failed", f"Could not deactivate product: {result.error}")
                else: # Product not found or unexpected
                    QMessageBox.warning(self, "Deactivation Failed", "Product not found or unknown error.")
            
            coro = self.core.product_manager.deactivate_product(selected_product.id)
            self.async_worker.run_task(coro, on_done_callback=_on_done)


        @Slot(str)
        def _on_search_products(self, text: str):
            """Triggers product search based on input text."""
            self._load_products(search_term=text)

        @Slot(bool, str)
        def _handle_product_dialog_result(self, success: bool, message: str):
            """Slot to handle results from ProductDialog and refresh the view."""
            if success:
                self._load_products(search_term=self.search_input.text()) # Reload with current search filter
            # else: error message already handled by dialog
    ```
*   **Acceptance Checklist:**
    *   [ ] `ProductView` inherits `QWidget`.
    *   [ ] `ProductTableModel` (subclass of `QAbstractTableModel`) is correctly implemented to display `ProductDTO` data.
    *   [ ] `table_view` is set up with the `product_model`.
    *   [ ] UI elements (search input, buttons, table) are created and laid out.
    *   [ ] `_connect_signals` properly connects buttons to their slots and `search_input.textChanged` to search slot.
    *   [ ] `_load_products` calls `product_manager.get_all_products` or `search_products` via `self.async_worker.run_task()`.
    *   [ ] The `on_done_callback` for `_load_products` updates `product_model.refresh_data()` on success and shows `QMessageBox` on error.
    *   [ ] `_on_add_product` and `_on_edit_product` launch `ProductDialog`.
    *   [ ] `_on_deactivate_product` calls `product_manager.deactivate_product` via `async_worker.run_task()` with confirmation.
    *   [ ] `_handle_product_dialog_result` refreshes data after dialog operations.
    *   [ ] The view consistently handles `Result` objects and provides user feedback.

#### **3. `app/ui/dialogs/customer_dialog.py`**

*   **File Path:** `app/ui/dialogs/customer_dialog.py`
*   **Purpose & Goals:** A `QDialog` for creating and editing Customer entities, similar to `ProductDialog`.
*   **Interfaces:** `CustomerDialog(core: ApplicationCore, customer: CustomerDTO | None = None)`.
*   **Interactions:** Calls `customer_manager.create_customer` or `update_customer` via `async_worker.run_task()`.
*   **Code Skeleton:**
    ```python
    # File: app/ui/dialogs/customer_dialog.py
    """A QDialog for creating and editing Customer entities."""
    import asyncio
    from decimal import Decimal
    from typing import Optional, Any, Union
    import uuid # For placeholder if not fully integrated yet

    from PySide6.QtWidgets import (
        QDialog, QVBoxLayout, QFormLayout, QLineEdit,
        QDoubleSpinBox, QCheckBox, QDialogButtonBox, QMessageBox
    )
    from PySide6.QtCore import Slot, Signal, QObject

    from app.business_logic.dto.customer_dto import CustomerCreateDTO, CustomerUpdateDTO, CustomerDTO
    from app.core.application_core import ApplicationCore
    from app.core.result import Success, Failure
    from app.core.async_bridge import AsyncWorker

    class CustomerDialog(QDialog):
        """A dialog for creating or editing a customer."""

        customer_operation_completed = Signal(bool, str) # Signal for CustomerView to refresh

        def __init__(self, core: ApplicationCore, customer: Optional[CustomerDTO] = None, parent: Optional[QObject] = None):
            super().__init__(parent)
            self.core = core
            self.async_worker: AsyncWorker = core.async_worker
            self.customer = customer
            self.is_edit_mode = customer is not None

            self.setWindowTitle("Edit Customer" if self.is_edit_mode else "Add New Customer")
            self.setMinimumWidth(400)

            self._setup_ui()
            self._connect_signals()

            if self.is_edit_mode:
                self._populate_form()

        def _setup_ui(self):
            """Initializes the UI widgets and layout."""
            # --- Create Widgets ---
            self.customer_code_input = QLineEdit()
            self.name_input = QLineEdit()
            self.email_input = QLineEdit()
            self.phone_input = QLineEdit()
            self.credit_limit_input = QDoubleSpinBox()
            self.credit_limit_input.setRange(0, 999999.99)
            self.credit_limit_input.setDecimals(2)
            self.is_active_checkbox = QCheckBox("Is Active")

            # --- Layout ---
            form_layout = QFormLayout()
            form_layout.addRow("Customer Code:", self.customer_code_input)
            form_layout.addRow("Name:", self.name_input)
            form_layout.addRow("Email:", self.email_input)
            form_layout.addRow("Phone:", self.phone_input)
            form_layout.addRow("Credit Limit (S$):", self.credit_limit_input)
            form_layout.addRow(self.is_active_checkbox)
            
            self.button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
            self.button_box.button(QDialogButtonBox.Save).setText("Save Customer")
            
            main_layout = QVBoxLayout(self)
            main_layout.addLayout(form_layout)
            main_layout.addWidget(self.button_box)

            # Set defaults for new customer
            if not self.is_edit_mode:
                self.is_active_checkbox.setChecked(True)

        def _connect_signals(self):
            """Connects UI signals to slots."""
            self.button_box.accepted.connect(self._on_save_accepted)
            self.button_box.rejected.connect(self.reject)

        def _populate_form(self):
            """Populates the form fields with existing customer data in edit mode."""
            if self.customer:
                self.customer_code_input.setText(self.customer.customer_code)
                self.name_input.setText(self.customer.name)
                self.email_input.setText(self.customer.email or "")
                self.phone_input.setText(self.customer.phone or "")
                self.credit_limit_input.setValue(float(self.customer.credit_limit))
                self.is_active_checkbox.setChecked(self.customer.is_active)

        def _get_dto(self) -> Union[CustomerCreateDTO, CustomerUpdateDTO]:
            """Constructs a DTO from the current form data."""
            common_data = {
                "customer_code": self.customer_code_input.text().strip(),
                "name": self.name_input.text().strip(),
                "email": self.email_input.text().strip() or None,
                "phone": self.phone_input.text().strip() or None,
                "credit_limit": Decimal(str(self.credit_limit_input.value())),
            }
            if self.is_edit_mode:
                return CustomerUpdateDTO(**common_data, is_active=self.is_active_checkbox.isChecked())
            else:
                return CustomerCreateDTO(**common_data)

        @Slot()
        def _on_save_accepted(self):
            """Handles the save action, triggering the async operation."""
            dto = self._get_dto()
            company_id = self.core.current_company_id

            try:
                if self.is_edit_mode:
                    coro = self.core.customer_manager.update_customer(self.customer.id, dto)
                    success_msg = f"Customer '{dto.name}' updated successfully!"
                    error_prefix = "Failed to update customer:"
                else:
                    coro = self.core.customer_manager.create_customer(company_id, dto)
                    success_msg = f"Customer '{dto.name}' created successfully!"
                    error_prefix = "Failed to create customer:"

                self.button_box.button(QDialogButtonBox.Save).setEnabled(False)
                
                def _on_done(result: Any, error: Optional[Exception]):
                    self.button_box.button(QDialogButtonBox.Save).setEnabled(True)
                    if error:
                        QMessageBox.critical(self, "Error", f"{error_prefix}\n{error}")
                        self.customer_operation_completed.emit(False, str(error))
                    elif isinstance(result, Success):
                        QMessageBox.information(self, "Success", success_msg)
                        self.customer_operation_completed.emit(True, success_msg)
                        self.accept()
                    elif isinstance(result, Failure):
                        QMessageBox.warning(self, "Validation Error", f"{error_prefix}\n{result.error}")
                        self.customer_operation_completed.emit(False, result.error)
                    else:
                        QMessageBox.critical(self, "Internal Error", f"Unexpected result type from manager: {type(result)}")
                        self.customer_operation_completed.emit(False, "An unexpected internal error occurred.")

                self.async_worker.run_task(coro, on_done_callback=_on_done)

            except Exception as e:
                QMessageBox.critical(self, "Application Error", f"An internal error prevented the operation:\n{e}")
                self.customer_operation_completed.emit(False, f"Internal error: {e}")
                self.button_box.button(QDialogButtonBox.Save).setEnabled(True)
    ```
*   **Acceptance Checklist:**
    *   [ ] Constructor accepts `ApplicationCore` and an optional `CustomerDTO`.
    *   [ ] `_setup_ui` creates form widgets for customer details.
    *   [ ] `_connect_signals` connects `button_box.accepted` to `_on_save_accepted`.
    *   [ ] `_populate_form` correctly loads `CustomerDTO` data into form fields.
    *   [ ] `_get_dto` constructs `CustomerCreateDTO` or `CustomerUpdateDTO`.
    *   [ ] `_on_save_accepted` calls `customer_manager.create_customer` or `update_customer` via `self.async_worker.run_task()`.
    *   [ ] The `on_done_callback` correctly handles `Success` and `Failure` results using `QMessageBox`.
    *   [ ] Save button disabled/re-enabled correctly.
    *   [ ] Dialog closes on success.
    *   [ ] `customer_operation_completed` signal is emitted.

#### **4. `app/ui/views/customer_view.py`**

*   **File Path:** `app/ui/views/customer_view.py`
*   **Purpose & Goals:** Provides the main UI for managing customers, including listing, searching, adding, editing, and deactivating. Uses a `QAbstractTableModel`.
*   **Interfaces:** `CustomerView(core: ApplicationCore)`.
*   **Interactions:** Similar to `ProductView`, interacts with `CustomerManager` via `async_worker`. Launches `CustomerDialog`.
*   **Code Skeleton:**
    ```python
    # File: app/ui/views/customer_view.py
    """The main view for managing customers."""
    import uuid
    from decimal import Decimal
    from typing import List, Any, Optional
    
    from PySide6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableView,
        QMessageBox, QLineEdit, QHeaderView, QSizePolicy
    )
    from PySide6.QtCore import Slot, Signal, QAbstractTableModel, QModelIndex, Qt, QObject

    from app.core.application_core import ApplicationCore
    from app.core.result import Success, Failure
    from app.business_logic.dto.customer_dto import CustomerDTO
    from app.ui.dialogs.customer_dialog import CustomerDialog
    from app.core.async_bridge import AsyncWorker

    class CustomerTableModel(QAbstractTableModel):
        """A Qt Table Model for displaying CustomerDTOs."""
        
        HEADERS = ["Code", "Name", "Email", "Phone", "Loyalty Points", "Credit Limit", "Active"]

        def __init__(self, customers: List[CustomerDTO], parent: Optional[QObject] = None):
            super().__init__(parent)
            self._customers = customers

        def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
            return len(self._customers)

        def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
            return len(self.HEADERS)

        def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
            if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
                return self.HEADERS[section]
            return None

        def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
            if not index.isValid():
                return None
            
            customer = self._customers[index.row()]
            col = index.column()

            if role == Qt.ItemDataRole.DisplayRole:
                if col == 0: return customer.customer_code
                if col == 1: return customer.name
                if col == 2: return customer.email or "N/A"
                if col == 3: return customer.phone or "N/A"
                if col == 4: return str(customer.loyalty_points)
                if col == 5: return f"S${customer.credit_limit:.2f}"
                if col == 6: return "Yes" if customer.is_active else "No"
            
            if role == Qt.ItemDataRole.TextAlignmentRole:
                if col in [4, 5]: # Loyalty points, credit limit
                    return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
                if col == 6: # Active
                    return Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter
            
            return None

        def get_customer_at_row(self, row: int) -> Optional[CustomerDTO]:
            """Returns the CustomerDTO at the given row index."""
            if 0 <= row < len(self._customers):
                return self._customers[row]
            return None

        def refresh_data(self, new_customers: List[CustomerDTO]):
            """Updates the model with new data and notifies views."""
            self.beginResetModel()
            self._customers = new_customers
            self.endResetModel()

    class CustomerView(QWidget):
        """A view widget to display and manage the customer list."""
        
        def __init__(self, core: ApplicationCore, parent: Optional[QObject] = None):
            super().__init__(parent)
            self.core = core
            self.async_worker: AsyncWorker = core.async_worker

            self._setup_ui()
            self._connect_signals()
            self._load_customers()

        def _setup_ui(self):
            """Initializes the UI widgets and layout."""
            # --- Search and Action Buttons ---
            top_layout = QHBoxLayout()
            self.search_input = QLineEdit()
            self.search_input.setPlaceholderText("Search customers by code, name, email, or phone...")
            self.add_button = QPushButton("Add New Customer")
            self.edit_button = QPushButton("Edit Selected")
            self.delete_button = QPushButton("Deactivate Selected") # Soft delete

            top_layout.addWidget(self.search_input, 1)
            top_layout.addStretch()
            top_layout.addWidget(self.add_button)
            top_layout.addWidget(self.edit_button)
            top_layout.addWidget(self.delete_button)
            
            # --- Customer Table ---
            self.table_view = QTableView()
            self.customer_model = CustomerTableModel([])
            self.table_view.setModel(self.customer_model)
            self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            self.table_view.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
            self.table_view.setSelectionMode(QTableView.SelectionMode.SingleSelection)
            self.table_view.setSortingEnabled(True)

            # --- Main Layout ---
            main_layout = QVBoxLayout(self)
            main_layout.addLayout(top_layout)
            main_layout.addWidget(self.table_view)

            self.setLayout(main_layout)
            self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)


        def _connect_signals(self):
            """Connects UI signals to slots."""
            self.add_button.clicked.connect(self._on_add_customer)
            self.edit_button.clicked.connect(self._on_edit_customer)
            self.delete_button.clicked.connect(self._on_deactivate_customer)
            self.search_input.textChanged.connect(self._on_search_customers)
            self.table_view.doubleClicked.connect(self._on_edit_customer)

        def _get_selected_customer(self) -> Optional[CustomerDTO]:
            """Helper to get the currently selected customer from the table."""
            selected_indexes = self.table_view.selectionModel().selectedRows()
            if selected_indexes:
                row = selected_indexes[0].row()
                return self.customer_model.get_customer_at_row(row)
            return None

        @Slot()
        def _load_customers(self, search_term: str = ""):
            """Loads customer data asynchronously into the table model."""
            company_id = self.core.current_company_id

            def _on_done(result: Any, error: Optional[Exception]):
                if error:
                    QMessageBox.critical(self, "Load Error", f"Failed to load customers: {error}")
                elif isinstance(result, Success):
                    self.customer_model.refresh_data(result.value)
                elif isinstance(result, Failure):
                    QMessageBox.warning(self, "Load Failed", f"Could not load customers: {result.error}")
            
            if search_term:
                coro = self.core.customer_manager.search_customers(company_id, search_term)
            else:
                coro = self.core.customer_manager.get_all_customers(company_id)
            
            self.async_worker.run_task(coro, on_done_callback=_on_done)

        @Slot()
        def _on_add_customer(self):
            """Opens the dialog to add a new customer."""
            dialog = CustomerDialog(self.core, parent=self)
            dialog.customer_operation_completed.connect(self._handle_customer_dialog_result)
            dialog.exec()

        @Slot()
        def _on_edit_customer(self):
            """Opens the dialog to edit the selected customer."""
            selected_customer = self._get_selected_customer()
            if not selected_customer:
                QMessageBox.information(self, "No Selection", "Please select a customer to edit.")
                return

            dialog = CustomerDialog(self.core, customer=selected_customer, parent=self)
            dialog.customer_operation_completed.connect(self._handle_customer_dialog_result)
            dialog.exec()

        @Slot()
        def _on_deactivate_customer(self):
            """Deactivates the selected customer."""
            selected_customer = self._get_selected_customer()
            if not selected_customer:
                QMessageBox.information(self, "No Selection", "Please select a customer to deactivate.")
                return
            
            reply = QMessageBox.question(self, "Confirm Deactivation",
                                        f"Are you sure you want to deactivate customer '{selected_customer.name}' (Code: {selected_customer.customer_code})?",
                                        QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.No:
                return

            def _on_done(result: Any, error: Optional[Exception]):
                if error:
                    QMessageBox.critical(self, "Error", f"Failed to deactivate customer: {error}")
                elif isinstance(result, Success) and result.value:
                    QMessageBox.information(self, "Success", f"Customer '{selected_customer.name}' deactivated.")
                    self._load_customers()
                elif isinstance(result, Failure):
                    QMessageBox.warning(self, "Deactivation Failed", f"Could not deactivate customer: {result.error}")
                else:
                    QMessageBox.warning(self, "Deactivation Failed", "Customer not found or unknown error.")
            
            coro = self.core.customer_manager.deactivate_customer(selected_customer.id)
            self.async_worker.run_task(coro, on_done_callback=_on_done)

        @Slot(str)
        def _on_search_customers(self, text: str):
            """Triggers customer search based on input text."""
            self._load_customers(search_term=text)

        @Slot(bool, str)
        def _handle_customer_dialog_result(self, success: bool, message: str):
            """Slot to handle results from CustomerDialog and refresh the view."""
            if success:
                self._load_customers(search_term=self.search_input.text())
    ```
*   **Acceptance Checklist:**
    *   [ ] `CustomerView` inherits `QWidget`.
    *   [ ] `CustomerTableModel` (subclass of `QAbstractTableModel`) is correctly implemented.
    *   [ ] `table_view` is set up with the `customer_model`.
    *   [ ] UI elements are created and laid out.
    *   [ ] `_connect_signals` properly connects buttons and search input.
    *   [ ] `_load_customers` calls `customer_manager.get_all_customers` or `search_customers` via `self.async_worker.run_task()`.
    *   [ ] The `on_done_callback` updates `customer_model.refresh_data()` and shows `QMessageBox`.
    *   [ ] `_on_add_customer` and `_on_edit_customer` launch `CustomerDialog`.
    *   [ ] `_on_deactivate_customer` calls `customer_manager.deactivate_customer` with confirmation.
    *   [ ] `_handle_customer_dialog_result` refreshes data.

### **Phase 2.5: Updates to Existing Stage 1 Files**

#### **1. `app/ui/main_window.py`** (Modified from Stage 1)

*   **File Path:** `app/ui/main_window.py`
*   **Purpose & Goals:** To integrate the new `ProductView` and `CustomerView` into the main application window, making them accessible via the menu bar.
*   **Interactions:** Will instantiate `ProductView` and `CustomerView` and add them to the `QStackedWidget`. Menu actions will switch the current widget.
*   **Code Skeleton:**
    ```python
    # File: app/ui/main_window.py
    """
    The main window of the SG-POS application.
    This QMainWindow acts as the shell, hosting different views like the POS screen,
    inventory management, etc., and providing navigation.
    """
    import asyncio
    import sys
    from typing import Optional, Any
    from PySide6.QtWidgets import (
        QMainWindow, QWidget, QVBoxLayout, QLabel,
        QStackedWidget, QMenuBar, QMenu, QMessageBox
    )
    from PySide6.QtCore import Slot, QEvent, QObject

    from app.core.application_core import ApplicationCore
    from app.core.async_bridge import AsyncWorker # For type hinting
    from app.core.exceptions import CoreException

    # Import all views that will be hosted
    from app.ui.views.product_view import ProductView # NEW
    from app.ui.views.customer_view import CustomerView # NEW
    # from app.ui.views.pos_view import POSView # To be implemented in Stage 3
    # from app.ui.views.inventory_view import InventoryView # To be implemented in Stage 4
    # from app.ui.views.reports_view import ReportsView # To be implemented in Stage 5
    # from app.ui.views.settings_view import SettingsView # To be implemented in Stage 5


    class MainWindow(QMainWindow):
        """The main application window."""

        def __init__(self, core: ApplicationCore):
            """
            Initializes the main window.
            
            Args:
                core: The central ApplicationCore instance.
            """
            super().__init__()
            self.core = core
            self.async_worker: AsyncWorker = core.async_worker

            self.setWindowTitle("SG Point-of-Sale System")
            self.setGeometry(100, 100, 1280, 720)

            # Create a QStackedWidget to hold the different views
            self.stacked_widget = QStackedWidget()
            self.setCentralWidget(self.stacked_widget)

            # --- Initialize and add actual views for Stage 2 ---
            self.product_view = ProductView(self.core) # NEW
            self.customer_view = CustomerView(self.core) # NEW
            # TODO: Initialize other views as they are implemented in later stages
            # self.pos_view = POSView(self.core)
            # self.inventory_view = InventoryView(self.core)
            # self.reports_view = ReportsView(self.core)
            # self.settings_view = SettingsView(self.core)

            # Add views to the stack
            self.stacked_widget.addWidget(self.product_view) # NEW
            self.stacked_widget.addWidget(self.customer_view) # NEW
            # TODO: Add other views here
            
            # Show the product view by default
            self.stacked_widget.setCurrentWidget(self.product_view) # NEW: Start on a real view

            # --- Connect the AsyncWorker's general task_finished signal ---
            self.async_worker.task_finished.connect(self._handle_async_task_result)

            # --- Create menu bar for navigation ---
            self._create_menu()

        def _create_menu(self):
            """Creates the main menu bar with navigation items."""
            menu_bar = self.menuBar()
            
            # File Menu
            file_menu = menu_bar.addMenu("&File")
            exit_action = file_menu.addAction("E&xit")
            exit_action.triggered.connect(self.close)

            # Data Management Menu (Populated in Stage 2)
            data_menu = menu_bar.addMenu("&Data Management") # NEW
            product_action = data_menu.addAction("Products") # NEW
            product_action.triggered.connect(lambda: self.stacked_widget.setCurrentWidget(self.product_view)) # NEW
            customer_action = data_menu.addAction("Customers") # NEW
            customer_action.triggered.connect(lambda: self.stacked_widget.setCurrentWidget(self.customer_view)) # NEW

            # POS Menu (Populated in Stage 3)
            # pos_menu = menu_bar.addMenu("&POS")
            # pos_action = pos_menu.addAction("Sales")
            # pos_action.triggered.connect(lambda: self.stacked_widget.setCurrentWidget(self.pos_view))

            # Inventory Menu (Populated in Stage 4)
            # inventory_menu = menu_bar.addMenu("&Inventory")
            # inventory_action = inventory_menu.addAction("Stock Management")
            # inventory_action.triggered.connect(lambda: self.stacked_widget.setCurrentWidget(self.inventory_view))

            # Reports Menu (Populated in Stage 5)
            # reports_menu = menu_bar.addMenu("&Reports")
            # reports_action = reports_menu.addAction("Business Reports")
            # reports_action.triggered.connect(lambda: self.stacked_widget.setCurrentWidget(self.reports_view))

            # Settings Menu (Populated in Stage 5)
            # settings_menu = menu_bar.addMenu("&Settings")
            # settings_action = settings_menu.addAction("Application Settings")
            # settings_action.triggered.connect(lambda: self.stacked_widget.setCurrentWidget(self.settings_view))


        @Slot(object, object)
        def _handle_async_task_result(self, result: Any, error: Optional[Exception]):
            """
            Global handler for results/errors from async tasks that didn't have
            a specific `on_done_callback`. This can be used for general error reporting.
            Individual UI components should still use specific callbacks where needed.
            """
            if error:
                print(f"Unhandled async error: {error}", file=sys.stderr)
                # TODO: Implement more sophisticated global error logging/display
                # QMessageBox.critical(self, "Error", f"An unexpected background error occurred: {error}")

        def closeEvent(self, event: QEvent) -> None:
            """
            Handle window close event to gracefully shut down the application core.
            This ensures database connections and async threads are properly terminated.
            """
            print("Main window closing. Initiating ApplicationCore shutdown...")
            
            async def shutdown_task():
                try:
                    await self.core.shutdown()
                    print("ApplicationCore shutdown complete.")
                except Exception as e:
                    print(f"Error during ApplicationCore shutdown: {e}", file=sys.stderr)
                    QMetaObject.invokeMethod(self, "show_shutdown_error",
                                            Qt.ConnectionType.QueuedConnection,
                                            Q_ARG(str, str(e)))
                QMetaObject.invokeMethod(self, "accept_close_event",
                                         Qt.ConnectionType.QueuedConnection)

            self.async_worker.run_task(shutdown_task())
            
            event.ignore()

        @Slot()
        def accept_close_event(self) -> None:
            """Slot to finally accept the close event after async shutdown completes."""
            QApplication.instance().quit()

        @Slot(str)
        def show_shutdown_error(self, error_message: str) -> None:
            """Displays a critical error message if shutdown fails."""
            QMessageBox.critical(self, "Shutdown Error", f"Failed to gracefully shut down application:\n{error_message}")
    ```
*   **Acceptance Checklist:**
    *   [ ] `ProductView` and `CustomerView` are imported and instantiated.
    *   [ ] These views are added to the `stacked_widget`.
    *   [ ] "Data Management" menu is created in the menu bar.
    *   [ ] "Products" and "Customers" actions are added to the "Data Management" menu and correctly switch the `stacked_widget`'s current view.
    *   [ ] The initial view displayed is `product_view`.

---

This completes the detailed execution plan for Stage 2. You now have a working UI for managing products and customers, backed by a robust, layered, and asynchronous backend. The implemented code fixes the blocking UI issue by correctly utilizing the `async_bridge` pattern, a critical step towards production readiness.

---

## **Stage 3: The Transactional Core - The Sales Module**

**Objective:** To build the most critical feature of the POS system: the ability to conduct a complete sales transaction from start to finish. This includes atomicity, inventory deduction, and financial record-keeping.

### **Phase 3.1: Data Transfer Objects (DTOs) for Sales**

#### **1. `app/business_logic/dto/sales_dto.py`**

*   **File Path:** `app/business_logic/dto/sales_dto.py`
*   **Purpose & Goals:** Defines the data contracts for sales transactions, including cart items, payment information, and the structure of a finalized sale receipt.
*   **Interfaces:** `CartItemDTO`, `PaymentInfoDTO`, `SaleCreateDTO`, `FinalizedSaleDTO`. All are Pydantic `BaseModel`s.
*   **Interactions:**
    *   UI (`POSView`, `PaymentDialog`) constructs `SaleCreateDTO`.
    *   `SalesManager` consumes `SaleCreateDTO` and returns `FinalizedSaleDTO`.
    *   `SalesService` works with `SalesTransaction` ORM models derived from DTOs.
*   **Code Skeleton:**
    ```python
    # File: app/business_logic/dto/sales_dto.py
    """Data Transfer Objects for Sales operations."""
    import uuid
    from decimal import Decimal
    from typing import List, Optional
    from pydantic import BaseModel, Field

    class CartItemDTO(BaseModel):
        """DTO representing an item to be added to a sales transaction."""
        product_id: uuid.UUID = Field(..., description="UUID of the product being sold")
        quantity: Decimal = Field(..., gt=Decimal("0.00"), decimal_places=4, description="Quantity of the product sold")
        # Price can be optional; if not provided, fetch the current selling price from ProductManager.
        unit_price_override: Optional[Decimal] = Field(None, ge=Decimal("0.00"), decimal_places=4, description="Optional override for unit selling price")

    class PaymentInfoDTO(BaseModel):
        """DTO representing a payment to be applied to a sale."""
        payment_method_id: uuid.UUID = Field(..., description="UUID of the payment method used")
        amount: Decimal = Field(..., gt=Decimal("0.00"), decimal_places=2, description="Amount paid using this method")
        reference_number: Optional[str] = Field(None, max_length=100, description="Reference number (e.g., card approval code)")

    class SaleCreateDTO(BaseModel):
        """DTO for creating a new sales transaction."""
        company_id: uuid.UUID = Field(..., description="UUID of the company making the sale")
        outlet_id: uuid.UUID = Field(..., description="UUID of the outlet where the sale occurred")
        cashier_id: uuid.UUID = Field(..., description="UUID of the cashier processing the sale")
        customer_id: Optional[uuid.UUID] = Field(None, description="UUID of the customer (optional)")
        cart_items: List[CartItemDTO] = Field(..., min_items=1, description="List of items in the cart")
        payments: List[PaymentInfoDTO] = Field(..., min_items=1, description="List of payments applied to the sale")
        notes: Optional[str] = Field(None, description="Any notes for the sales transaction")

    class FinalizedSaleDTO(BaseModel):
        """DTO representing a completed sale, suitable for generating a receipt."""
        transaction_id: uuid.UUID = Field(..., description="UUID of the finalized sales transaction")
        transaction_number: str = Field(..., description="Unique transaction number")
        subtotal: Decimal = Field(..., decimal_places=2, description="Subtotal before tax and discount")
        tax_amount: Decimal = Field(..., decimal_places=2, description="Total tax amount")
        discount_amount: Decimal = Field(..., decimal_places=2, description="Total discount amount")
        rounding_adjustment: Decimal = Field(..., decimal_places=2, description="Rounding adjustment for total")
        total_

