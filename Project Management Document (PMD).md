A project's success is often determined by the clarity of its plan and the effectiveness of its management. For a team of fresh developers, having a structured, incremental, and highly detailed guide is not just helpful—it is essential.

This document is intentionally verbose and detailed, designed to leave no room for ambiguity. Use it as your single source of truth to coordinate your teams, track progress, and ensure the final product meets the highest standards of quality we have designed.

---

# **Project Management Document (PMD): SG Point-of-Sale System**

**Version:** 1.0  
**Author:** AI Lead Architect  
**Audience:** Project Manager & Development Team Leads

## **Table of Contents**

1.  [**Introduction: How to Use This Document**](#1-introduction-how-to-use-this-document)
2.  [**Part 1: The Project Management Philosophy**](#part-1-the-project-management-philosophy)
    *   2.1. Development Methodology: Agile with Sprints
    *   2.2. Version Control: The Git Flow Strategy
    *   2.3. The "Definition of Done": Our Quality Standard
    *   2.4. Communication & Collaboration Plan
3.  [**Part 2: The 5-Stage Development Plan**](#part-2-the-5-stage-development-plan)
    *   [**Stage 1: The Foundation - Core Services & Database Setup**](#stage-1-the-foundation---core-services--database-setup)
    *   [**Stage 2: Core Data Entities - Products, Customers & Data Access**](#stage-2-core-data-entities---products-customers--data-access)
    *   [**Stage 3: The Transactional Core - The Sales Module**](#stage-3-the-transactional-core---the-sales-module)
    *   [**Stage 4: Expanding Operations - Inventory & Advanced CRM**](#stage-4-expanding-operations---inventory--advanced-crm)
    *   [**Stage 5: Business Intelligence & Final Polish - Reporting, GST & Settings**](#stage-5-business-intelligence--final-polish---reporting-gst--settings)
4.  [**Part 3: Managing Teams & Dependencies**](#part-3-managing-teams--dependencies)
    *   4.1. Team Structure & Responsibilities
    *   4.2. Managing Cross-Stage Dependencies
5.  [**Part 4: Conclusion & Next Steps**](#part-4-conclusion--next-steps)

---

## **1. Introduction: How to Use This Document**

Welcome, Project Manager. This document is your comprehensive guide to successfully leading the development of the SG-POS system. It is designed to be your primary tool for planning, assigning tasks, and verifying the quality of work delivered by your development teams.

**Think of this document as the "constitution" for our project.** It provides the structure, rules, and blueprints that everyone will follow. Its primary purpose is to translate our high-level architectural design into a series of concrete, actionable, and verifiable steps.

**How to use it:**

1.  **Understand the Philosophy (Part 1):** Before diving into tasks, familiarize yourself with our project's methodology. This section explains *how* we will work together.
2.  **Follow the 5 Stages (Part 2):** The project is broken down into five major stages. Treat each stage as a major milestone. While some work can be parallelized, the stages are designed to be completed in sequence, as each one builds upon the last.
3.  **Assign Tasks by File (Sections within Part 2):** Within each stage, you will find a list of specific files to be created. You can assign one or more files to a developer or a pair of developers.
4.  **Use Checklists for Acceptance:** The **Acceptance Checklist** for each file is your most powerful tool. It is your non-technical way of confirming that a developer's work is truly complete and meets our project's quality standards. Before you approve a developer's pull request or mark a task as "done," ensure every item on the checklist is ticked.

This document is designed to empower you to manage a technical project effectively, even without a deep coding background. Your role is to ensure the team adheres to this plan, to facilitate communication, and to use the checklists to validate that the work meets the high standards we have set.

---

## **Part 1: The Project Management Philosophy**

To ensure a smooth and efficient development process, especially with fresh developers, we will adopt a structured yet flexible methodology.

### 2.1. Development Methodology: Agile with Sprints

We will use an Agile approach, specifically working in **two-week sprints**.

*   **Sprint Planning:** At the start of each sprint, you (as PM), along with the team leads, will select a set of tasks (files to be built) from the current development stage to be completed within that sprint.
*   **Daily Stand-ups:** A brief, 15-minute meeting each morning where every developer answers three questions:
    1.  What did I complete yesterday?
    2.  What will I work on today?
    3.  Are there any blockers preventing me from making progress?
    *Your role is to listen for blockers and help remove them.*
*   **Sprint Review:** At the end of the sprint, the team demonstrates the working software they have built. For example, at the end of a sprint in Stage 3, a team might demonstrate the ability to add an item to the cart in the UI.
*   **Sprint Retrospective:** A meeting where the team discusses what went well, what didn't, and what can be improved for the next sprint.

### 2.2. Version Control: The Git Flow Strategy

We will use a standardized Git workflow to keep our codebase clean and stable.

1.  **`main` branch:** This branch represents the stable, production-ready code. No one ever commits directly to `main`.
2.  **`develop` branch:** This is the primary integration branch. It contains the latest completed features.
3.  **Feature branches:** For every new task (e.g., creating the `product_service.py` file), a developer will create a new branch from `develop` (e.g., `feature/PROJ-123-product-service`).
4.  **Pull Requests (PRs):** When a feature is complete, the developer opens a Pull Request to merge their feature branch back into `develop`.
5.  **Code Reviews:** Every PR must be reviewed and approved by at least one other developer (a peer or a lead) before it can be merged. The review will check against the Acceptance Checklist for that file.

*Your role is to ensure that no code gets into the `develop` branch without a PR and a successful code review.*

### 2.3. The "Definition of Done": Our Quality Standard

A task is not "done" when the code is written. A task is **DONE** only when:

1.  All functional requirements for that module/file are met.
2.  All items in the **Acceptance Checklist** for that file are completed.
3.  The code has been reviewed and approved by a peer.
4.  The associated PullRequest has been successfully merged into the `develop` branch.
5.  The Continuous Integration (CI) pipeline (which runs tests automatically) passes for that code.

### 2.4. Communication & Collaboration Plan

*   **Project Management Tool:** Jira or a similar tool (e.g., Trello, Asana) will be used to track all tasks (user stories, files to be built).
*   **Daily Communication:** Slack or Microsoft Teams will be used for day-to-day questions and collaboration.
*   **Documentation:** All architectural decisions and documentation reside in this PMD and the project's `docs/` folder. This is our single source of truth.

---

## **Part 2: The 5-Stage Development Plan**

This is the core of the project plan. We will build the SG-POS system in five logical stages.

### **Stage 1: The Foundation - Core Services & Database Setup**

**Objective:** To establish the skeleton of the application, set up the core architectural patterns, and create a stable foundation upon which all future features will be built. At the end of this stage, we will have a runnable (but empty) application that can connect to a database.

**Rationale:** Just like building a house, we must lay a solid foundation before we can put up walls. This stage creates the core plumbing—Dependency Injection, configuration, error handling, and the database connection—that every other part of the system will rely on. Completing this first ensures that all subsequent development happens within a consistent and stable architectural framework.

**Key Outcomes:**
*   A fully defined and version-controlled database schema.
*   A working `ApplicationCore` for Dependency Injection.
*   A runnable, empty main application window.
*   A successful CI pipeline that runs on every code change.
*   A fully containerized development environment using Docker Compose.

---
#### **Module Breakdown & Acceptance Checklists for Stage 1**

##### **1. Project Scaffolding & Setup**

*   **File Paths:** `pyproject.toml`, `.gitignore`, `README.md`, `docker-compose.dev.yml`, `.env.example`, `alembic.ini`, `migrations/`
*   **Purpose:** To define the project's dependencies, tools, and local development environment. This is the absolute first step.
*   **Acceptance Checklist:**
    *   [ ] `pyproject.toml` is complete with all production and development dependencies as specified in the PRD.
    *   [ ] `docker-compose.dev.yml` successfully starts a PostgreSQL 15 container.
    *   [ ] The project's directory structure is created (see script below).
    *   [ ] Alembic is configured and can connect to the Dockerized database.
    *   [ ] An initial, empty migration can be created and applied (`alembic upgrade head`).
    *   [ ] The `README.md` contains instructions for the development setup.

##### **Bash Script to Create Directory Structure (for `1. Project Scaffolding & Setup`)**

This script should be run in the empty project root folder to create the entire directory and file skeleton.

```bash
#!/bin/bash
# SG-POS Project Directory Structure Creation Script
echo "Creating SG-POS project structure..."

# Top-level directories
mkdir -p app docs migrations/versions resources scripts/database tests/unit tests/integration

# App Layer Directories
mkdir -p app/core app/models app/services app/business_logic/managers app/business_logic/dto app/ui/views app/ui/widgets app/ui/dialogs app/ui/resources/icons app/integrations

# Create __init__.py files to define Python packages
find app -type d -exec touch {}/__init__.py \;
find tests -type d -exec touch {}/__init__.py \;

# Create key placeholder files for Stage 1
touch app/main.py
touch app/core/application_core.py
touch app/core/config.py
touch app/core/exceptions.py
touch app/core/result.py
touch app/core/async_bridge.py
touch app/models/base.py
touch app/ui/main_window.py
touch app/ui/resources/styles.qss
touch tests/conftest.py
touch .env.example
touch pyproject.toml
touch README.md
touch alembic.ini
touch .gitignore
touch docker-compose.dev.yml
touch scripts/database/schema.sql

echo "Project structure created successfully."
```

##### **2. Core Application Infrastructure (`app/core/`)**

*   **File: `app/core/config.py`**
    *   **Purpose:** To manage all application configuration from environment variables and `.env` files.
    *   **Interfaces:** Provides a `Settings` class (using Pydantic) that can be accessed via `app_core.config`. Attributes like `config.DATABASE_URL` will be strongly typed.
    *   **Acceptance Checklist:**
        *   [ ] `Settings` class is implemented using Pydantic's `BaseSettings`.
        *   [ ] It correctly loads variables from a `.env` file for local development.
        *   [ ] It includes variables for `DATABASE_URL`, `LOG_LEVEL`, and `SECRET_KEY`.
        *   [ ] Unit tests exist to verify that variables are loaded correctly.

*   **File: `app/core/result.py`**
    *   **Purpose:** To define the `Result`, `Success`, and `Failure` classes for explicit error handling.
    *   **Interfaces:** Defines the `Result` type hint and the `Success` and `Failure` data classes.
    *   **Acceptance Checklist:**
        *   [ ] `Success(Generic[T])` and `Failure(Generic[E])` data classes are implemented.
        *   [ ] `Result` type alias `Union[Success[T], Failure[E]]` is defined.
        *   [ ] The code is fully type-hinted and passes MyPy checks.

*   **File: `app/core/application_core.py`**
    *   **Purpose:** To serve as the central Dependency Injection container.
    *   **Interfaces:** Provides lazy-loaded `@property` accessors for all future managers and services (e.g., `app_core.sales_manager`). It will be initialized with a `Config` object.
    *   **Acceptance Checklist:**
        *   [ ] The `ApplicationCore` class is implemented.
        *   [ ] The `__init__` method accepts a `Config` object.
        *   [ ] It initializes the database engine and session factory.
        *   [ ] At least two placeholder properties (e.g., for `product_service` and `sales_manager`) are implemented to demonstrate the lazy-loading pattern.

##### **3. Database Schema & Persistence Layer (`app/models/` & `migrations/`)**

*   **Files:** `scripts/database/schema.sql`, all files in `app/models/`, and the first Alembic migration script.
*   **Purpose:** To define the entire database structure in both a raw SQL file and as SQLAlchemy ORM models, and to create the initial versioned migration.
*   **Interfaces:** The SQLAlchemy models define the Pythonic interface to the database tables. They will be used exclusively by the Data Access Layer (`services`).
*   **Acceptance Checklist:**
    *   [ ] The `scripts/database/schema.sql` file contains the complete, tested DDL from the PRD.
    *   [ ] Every table in the schema has a corresponding SQLAlchemy ORM class in a file under `app/models/`.
    *   [ ] All relationships (one-to-many, many-to-many) are correctly defined in the models with `relationship()` and `ForeignKey`.
    *   [ ] An initial Alembic migration is created (`alembic revision --autogenerate`) that reflects the full schema.
    *   [ ] Running `alembic upgrade head` on a clean database successfully creates all tables.
    *   [ ] All models inherit from a `Base` and a `TimestampMixin` for `created_at`/`updated_at` fields.

##### **4. Main Application Entry Point (`app/main.py` & `app/ui/main_window.py`)**

*   **Purpose:** To create the main application loop and display an empty main window. This proves the foundation is runnable.
*   **Interfaces:** `main.py` is the executable entry point. `MainWindow` is the top-level Qt widget.
*   **Acceptance Checklist:**
    *   [ ] `main.py` correctly initializes a `QApplication`.
    *   [ ] It instantiates the `ApplicationCore`.
    *   [ ] It creates and shows an instance of `MainWindow`.
    *   [ ] `MainWindow` is a `QMainWindow` subclass.
    *   [ ] Running `python app/main.py` opens a blank window with the title "SG-POS System" and does not crash.

---

### **Stage 2: Core Data Entities - Products, Customers & Data Access**

**Objective:** To build the data management capabilities for the most fundamental business entities: Products and Customers. This involves creating the full Data Access Layer (`services`) and the basic UI for viewing and editing this data.

**Rationale:** Before we can process a sale, we need to have products to sell and customers to sell to. This stage focuses on building the "rolodex" and "catalog" functionalities of the system. It establishes the critical pattern of `UI -> Manager -> Service -> Database` for all future CRUD (Create, Read,Update, Delete) operations.

**Key Outcomes:**
*   Functional services (repositories) for Products and Customers.
*   Business logic managers for Products and Customers.
*   Basic UI screens where a user can view, add, edit, and delete products and customers.
*   A fully tested and robust data access layer.

---
#### **Module Breakdown & Acceptance Checklists for Stage 2**

##### **1. Data Access Layer for Core Entities (`app/services/`)**

*   **Files:** `app/services/product_service.py`, `app/services/customer_service.py`
*   **Purpose:** To implement the Repository pattern for products and customers, encapsulating all database query logic.
*   **Interfaces:**
    *   `ProductService`: `async get_by_id(id)`, `async get_by_sku(sku)`, `async search(term)`, `async save(product_dto)`.
    *   `CustomerService`: `async get_by_id(id)`, `async get_by_code(code)`, `async search(term)`, `async save(customer_dto)`.
    *   All methods will consume and produce DTOs and return a `Result` object.
*   **Acceptance Checklist:**
    *   [ ] Each service has methods for creating, retrieving single records, updating, and searching.
    *   [ ] All database queries are executed through the `ApplicationCore`'s session manager.
    *   [ ] Methods correctly map data from ORM models to DTOs before returning.
    *   [ ] All public methods are fully type-hinted and return a `Result` object.
    *   [ ] Unit tests exist for every method, mocking the database session to test the query logic in isolation. Integration tests exist to verify against a real test database.

##### **2. Business Logic Layer for Core Entities (`app/business_logic/`)**

*   **Files:** `app/business_logic/managers/product_manager.py`, `app/business_logic/managers/customer_manager.py`, `app/business_logic/dto/product_dto.py`, `app/business_logic/dto/customer_dto.py`
*   **Purpose:** To orchestrate the business logic for managing products and customers.
*   **Interfaces:**
    *   `ProductManager`: `async create_product(dto)`, `async update_product(id, dto)`.
    *   `CustomerManager`: `async create_customer(dto)`, `async update_customer(id, dto)`.
    *   These managers will contain business validation (e.g., "a product's selling price cannot be lower than its cost price").
*   **Acceptance Checklist:**
    *   [ ] DTOs for Product and Customer (e.g., `ProductDTO`, `ProductCreateDTO`) are defined using Pydantic.
    *   [ ] Managers use the corresponding services from the `ApplicationCore` to interact with the database.
    *   [ ] Business rules (e.g., checking for duplicate SKUs) are implemented in the managers, not the services.
    *   [ ] All public methods return a `Result` object.
    *   [ ] Unit tests exist for the managers, mocking the service layer to test the business logic in isolation.

##### **3. Presentation Layer (UI) for Core Entities (`app/ui/`)**

*   **Files:** `app/ui/views/product_view.py`, `app/ui/views/customer_view.py`, `app/ui/dialogs/product_dialog.py`, `app/ui/dialogs/customer_dialog.py`
*   **Purpose:** To provide the user interface for managing products and customers.
*   **Interfaces:**
    *   The "View" widgets will contain a table to display entities and buttons for "Add," "Edit," "Delete."
    *   The "Dialog" widgets will be modal forms for creating or editing a single entity.
*   **Acceptance Checklist:**
    *   [ ] A user can open the Product view and see a table of all products.
    *   [ ] Clicking "Add" opens the `ProductDialog`.
    *   [ ] Filling out the dialog and clicking "Save" calls the `product_manager.create_product` method.
    *   [ ] The UI correctly handles both `Success` and `Failure` results from the manager (i.e., it shows a success message or an error popup).
    *   [ ] The same CRUD functionality is implemented for the Customer view.
    *   [ ] All UI interactions with business logic happen asynchronously via the `async_bridge`.

---

### **Stage 3: The Transactional Core - The Sales Module**

**Objective:** To build the most critical feature of the POS system: the ability to conduct a complete sales transaction from start to finish.

**Rationale:** With products and customers manageable, the next logical step is to build the primary workflow that uses them. This stage is complex and will require integrating multiple components built in previous stages. It delivers the first piece of core business value.

**Key Outcomes:**
*   A functional Point-of-Sale UI.
*   The ability to add items to a cart, apply payments, and finalize a sale.
*   Real-time deduction of inventory upon sale completion.
*   Creation of immutable financial records for each transaction.
*   Generation and printing of a basic sales receipt.

---
#### **Module Breakdown & Acceptance Checklists for Stage 3**

##### **1. Sales & Payment Data Models (`app/models/sales.py`, `app/models/payment.py`)**

*   **Purpose:** To define the database schema for sales, line items, and payments.
*   **Acceptance Checklist:**
    *   [ ] SQLAlchemy models `SalesTransaction`, `SalesTransactionItem`, `PaymentMethod`, and `Payment` are implemented as per the schema.
    *   [ ] All relationships are correctly defined (e.g., a transaction has many items and many payments).
    *   [ ] A new Alembic migration is created and applied to add these tables to the database.

##### **2. Sales & Payment Data Access Layer (`app/services/`)**

*   **Files:** `app/services/sales_service.py`, `app/services/payment_service.py`
*   **Purpose:** To handle all database operations for sales and payments.
*   **Interfaces:**
    *   `SalesService`: `async create_transaction_with_items(...)`. This method must handle the atomic creation of a `SalesTransaction` and all its `SalesTransactionItem` children within a single database transaction.
    *   `PaymentService`: `async save_payment(...)`.
*   **Acceptance Checklist:**
    *   [ ] Services are implemented with methods for creating and retrieving sales and payment data.
    *   [ ] The `create_transaction_with_items` method correctly uses a database transaction to ensure atomicity.
    *   [ ] Full suite of unit and integration tests are written.

##### **3. Sales Business Logic (`app/business_logic/`)**

*   **Files:** `app/business_logic/managers/sales_manager.py`, `app/business_logic/managers/payment_manager.py`, `app/business_logic/dto/sales_dto.py`
*   **Purpose:** To orchestrate the entire sales workflow.
*   **Interfaces:**
    *   `SalesManager`: `async finalize_sale(cart_dto) -> Result[ReceiptDTO, SaleError]`. This is the core method. It will coordinate with the `InventoryManager`, `CustomerManager`, and `PaymentManager`.
    *   `PaymentManager`: `async process_payment(payment_details) -> Result[ProcessedPayment, PaymentError]`. This manager could contain logic for interacting with an external payment gateway in the future.
*   **Acceptance Checklist:**
    *   [ ] `SalesManager` correctly calls `InventoryManager.check_availability` before proceeding.
    *   [ ] `SalesManager.finalize_sale` correctly orchestrates the following within a single unit of work:
        1.  Saves the sales transaction record via `SalesService`.
        2.  Saves the payment records via `PaymentService`.
        3.  Adjusts stock levels via `InventoryManager`.
        4.  (If applicable) Updates customer loyalty points via `CustomerManager`.
    *   [ ] All potential failure points (e.g., insufficient stock, payment failed) are handled and return a `Failure` result.
    *   [ ] A comprehensive set of unit tests covers all success and failure scenarios.

##### **4. Point-of-Sale UI (`app/ui/views/pos_view.py`, `app/ui/dialogs/payment_dialog.py`)**

*   **Purpose:** To provide the front-end interface for the cashier.
*   **Interfaces:** A `POSView` that allows searching/scanning products, adding them to a cart (a table view), seeing a running total, and clicking a "Pay" button. The "Pay" button launches the `PaymentDialog`.
*   **Acceptance Checklist:**
    *   [ ] User can search for a product and add it to the cart table.
    *   [ ] The cart table updates the subtotal, GST, and total in real-time.
    *   [ ] Clicking "Pay" opens the `PaymentDialog`.
    *   [ ] The `PaymentDialog` allows the user to enter amounts for different payment methods.
    *   [ ] Submitting the payment dialog calls `sales_manager.finalize_sale`.
    *   [ ] The UI provides clear feedback for both successful and failed transactions.
    *   [ ] A basic receipt can be printed or displayed on screen upon successful completion.

---

### **Stage 4: Expanding Operations - Inventory & Advanced CRM**

**Objective:** To build out the full inventory management and advanced customer relationship management modules.

**Rationale:** With the core sales loop functional, we can now build the supporting operational modules. Full inventory management is the next highest priority for most retailers, followed by tools to manage and reward loyal customers.

**Key Outcomes:**
*   A fully functional inventory management UI for stock takes, adjustments, and transfers.
*   Purchase order management workflow.
*   A functional CRM UI for managing customer details and viewing purchase history.
*   Implementation of the customer loyalty program.

---
#### **Module Breakdown & Acceptance Checklists for Stage 4**

##### **1. Advanced Inventory Management (`app/business_logic/managers/inventory_manager.py`)**

*   **Purpose:** To add advanced inventory workflows beyond simple stock deduction.
*   **Interfaces:**
    *   `async perform_stock_take(counts_dto) -> Result[VarianceReport, Error]`.
    *   `async create_purchase_order(po_dto) -> Result[PurchaseOrder, Error]`.
    *   `async receive_goods(po_id, received_items_dto)`.
*   **Acceptance Checklist:**
    *   [ ] Manager logic for stock adjustments (positive and negative) is implemented, creating `StockMovement` records.
    *   [ ] Logic for purchase order creation and receiving goods is implemented, which results in positive `StockMovement` records.
    *   [ ] Reorder point logic is implemented, allowing the manager to generate a list of products that need reordering.
    *   [ ] All operations are fully unit tested.

##### **2. Inventory Management UI (`app/ui/views/inventory_view.py`)**

*   **Purpose:** To provide the user interface for all inventory operations.
*   **Interfaces:** A main view with a filterable table of all inventory items. Buttons to launch dialogs for "New Purchase Order," "Adjust Stock," and "Perform Stock Take."
*   **Acceptance Checklist:**
    *   [ ] User can view all products with their current `quantity_on_hand`.
    *   [ ] User can create, view, and update purchase orders.
    *   [ ] User can receive goods against a purchase order, which correctly updates stock levels.
    *   [ ] User can perform a stock adjustment for any product, providing a reason, which is correctly audited.

##### **3. Advanced CRM & Loyalty (`app/business_logic/managers/customer_manager.py`)**

*   **Purpose:** To implement the logic for the customer loyalty program.
*   **Interfaces:**
    *   `async add_loyalty_points(customer_id, transaction_id)`.
    *   `async redeem_loyalty_points(customer_id, points_to_redeem) -> Result[discount_value, Error]`.
*   **Acceptance Checklist:**
    *   [ ] The `SalesManager` is updated to call `CustomerManager.add_loyalty_points` when a sale is finalized for a registered customer.
    *   [ ] The logic for calculating points based on purchase value is implemented.
    *   [ ] The logic for redeeming points (e.g., converting points to a dollar discount) is implemented and validated.
    *   [ ] All loyalty point transactions are logged for auditing.

##### **4. Advanced Customer UI (`app/ui/views/customer_view.py`)**

*   **Purpose:** To enhance the customer view with loyalty information and detailed history.
*   **Interfaces:** The customer detail view is updated to show loyalty point balance and a full transaction history.
*   **Acceptance Checklist:**
    *   [ ] When viewing a customer, their current loyalty point balance is displayed.
    *   [ ] A table or list shows every sales transaction associated with that customer.
    *   [ ] The POS screen is updated to allow for the application of loyalty points as a form of discount/payment.

---

### **Stage 5: Business Intelligence & Final Polish - Reporting, GST & Settings**

**Objective:** To build the reporting and analytics features that provide business insights, ensure full regulatory compliance, and add the final layer of professional polish to the application.

**Rationale:** With all core operational workflows complete, the final stage focuses on delivering value-added features. Reporting turns data into information, GST compliance is a must-have for the Singapore market, and a robust settings module makes the application adaptable and professional.

**Key Outcomes:**
*   A comprehensive reporting dashboard.
*   Generation of IRAS-compliant GST reports.
*   A complete settings/administration module for configuring the application.
*   Final UI theming and polish.

---
#### **Module Breakdown & Acceptance Checklists for Stage 5**

##### **1. Reporting Engine (`app/business_logic/managers/reporting_manager.py`, `app/services/report_service.py`)**

*   **Purpose:** To generate all key business reports.
*   **Interfaces:**
    *   `ReportingManager`: `async generate_sales_summary(date_range)`, `async generate_inventory_valuation_report()`, `async generate_staff_performance_report(...)`.
    *   `ReportService`: Contains complex, optimized SQL queries for data aggregation needed by the manager.
*   **Acceptance Checklist:**
    *   [ ] The `ReportService` is implemented with efficient data aggregation queries. It should avoid fetching raw data and processing it in Python where possible.
    *   [ ] The `ReportingManager` can generate the following key reports:
        *   Daily Sales Summary (X/Z Report)
        *   Product Performance Report (by quantity and revenue)
        *   Inventory Valuation Report
    *   [ ] Reports can be exported to PDF and CSV formats.

##### **2. GST Compliance Module (`app/business_logic/managers/gst_manager.py`)**

*   **Purpose:** To handle all GST-related logic and reporting.
*   **Interfaces:** `async generate_gst_f5_report(quarter_start_date, quarter_end_date) -> Result[GstReportDTO, Error]`.
*   **Acceptance Checklist:**
    *   [ ] The manager correctly aggregates total sales and purchases, separating them into standard-rated, zero-rated, and exempt categories.
    *   [ ] It correctly calculates the output tax and claimable input tax.
    *   [ ] The final report data structure matches the fields required for the IRAS GST Form 5.
    *   [ ] The module is unit tested against a variety of transaction scenarios to ensure calculation accuracy.

##### **3. Reporting & GST UI (`app/ui/views/reporting_view.py`)**

*   **Purpose:** The UI for viewing reports and generating GST filings.
*   **Interfaces:** A view that allows users to select a report type, set parameters (like date ranges), and view the generated report in a table or chart.
*   **Acceptance Checklist:**
    *   [ ] User can select from a list of available reports.
    *   [ ] User can specify date ranges and other relevant filters.
    *   [ ] The generated report is displayed clearly in the UI.
    *   [ ] "Export to PDF" and "Export to CSV" buttons are functional.
    *   [ ] The GST F5 generation screen is intuitive and produces the correct data for filing.

##### **4. Settings & Administration Module (`app/ui/views/settings_view.py`)**

*   **Purpose:** To allow administrators to configure the application.
*   **Interfaces:** A settings view, likely with multiple tabs for different categories (Company Info, Outlets, Users, Roles & Permissions, Payment Methods, Tax Rates).
*   **Acceptance Checklist:**
    *   [ ] An admin user can update company information.
    *   [ ] An admin user can create/edit/deactivate users and assign them to roles.
    *   [ ] An admin user can configure payment methods.
    *   [ ] All settings are correctly persisted to the database.
    *   [ ] The UI is polished, with consistent styling applied across the entire application.

---

## **Part 3: Managing Teams & Dependencies**

### 4.1. Team Structure & Responsibilities

For maximum efficiency, you can structure your teams around our architectural layers, especially after Stage 1 is complete.

*   **Backend Team:** Focuses on the `services` and `business_logic` layers. They are responsible for data access, business rule implementation, and creating the APIs (methods on managers) that the frontend team will consume.
*   **Frontend Team:** Focuses on the `ui` layer. They are responsible for building the widgets, dialogs, and views. They consume the interfaces provided by the Backend Team.
*   **QA & Testing Team:** Works in parallel, writing unit tests, integration tests, and end-to-end tests for the features being developed in each sprint.

### 4.2. Managing Cross-Stage Dependencies

*   **The Contract is Key:** The most critical dependency between the Frontend and Backend teams is the **DTO (Data Transfer Object)**. Before any UI work begins for a feature, the DTOs that will be used for input and output must be defined and agreed upon by both teams. This can be done in a shared file in `app/business_logic/dto/`.
*   **Parallel Development:** Once Stage 1 is complete, work can be parallelized. For example, in Stage 3:
    *   The **Backend Team** can build the `SalesManager` and `SalesService`, initially testing them with unit and integration tests (no UI required).
    *   The **Frontend Team** can build the `POSView` and `PaymentDialog`, initially using *mock* or *dummy* data that matches the agreed-upon DTOs.
    *   Once both are ready, they can be integrated. This approach significantly speeds up development.

---

## **Part 4: Conclusion & Next Steps**

This Project Management Document provides a clear, structured, and phased roadmap for the development of the SG-POS system. By following these stages, defining tasks based on the specified files, and rigorously adhering to the acceptance checklists, you can effectively manage your team of developers towards a successful project outcome.

Your primary role as Project Manager will be to:
1.  **Plan Sprints:** Break down the work in each stage into two-week sprints.
2.  **Assign Tasks:** Assign specific files/modules to developers or teams.
3.  **Monitor Progress:** Use daily stand-ups and your project management tool to track progress.
4.  **Enforce Quality:** Use the Acceptance Checklists as your guide during code reviews and sprint demos.
5.  **Remove Blockers:** Facilitate communication between teams and provide the resources they need to succeed.

This plan is ambitious but achievable. By building from a solid foundation and adding functionality in logical, value-driven increments, we will create a truly exceptional product for the Singaporean market.
