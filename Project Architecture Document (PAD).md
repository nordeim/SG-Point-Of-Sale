# Project Architecture Overview Document

| Document ID: | SG-POS-ARCH-2025-01          | Version:      | 1.0                          |
| :----------- | :--------------------------- | :------------ | :--------------------------- |
| Project:     | SG Point-of-Sale System    | Date:         | 2024-06-22                   |
| Prepared By: | CodeNavigator (AI Assistant) | Status:       | **Active**                   |
| Subject:     | A comprehensive, in-depth technical overview of the SG-POS application architecture, codebase structure, and key operational workflows. |

## **1.0 Executive Summary**

This document provides a definitive architectural overview of the SG Point-of-Sale (SG-POS) system. It is intended for software engineers, architects, and technical project managers involved in the development, maintenance, and quality assurance of the application. Its purpose is to serve as the single source of truth for understanding the system's design principles, component interactions, and data flow.

The SG-POS system is engineered as a professional-grade, multi-layered desktop application. It is built on a modern technology stack, including Python 3.11+, PySide6 (Qt6), and PostgreSQL, managed via Poetry. The architecture is explicitly designed to be **robust, maintainable, and scalable**, prioritizing clear separation of concerns, data integrity, and a non-blocking user experience.

Key architectural pillars of the system include:
1.  **Strict Layered Architecture:** A clean separation between the Presentation (UI), Business Logic, Data Access, and Persistence layers.
2.  **Dependency Injection (DI):** A central `ApplicationCore` acts as a service locator and DI container, decoupling components and simplifying the management of dependencies like database sessions and managers.
3.  **Asynchronous Operations:** A robust `Async Bridge` ensures that all I/O-bound operations (especially database queries) are executed on a background thread, guaranteeing a responsive, non-blocking UI.
4.  **Explicit Error Handling:** The use of a `Result` monad (Success/Failure) for all business and service layer operations provides a predictable and robust way to handle foreseeable errors without relying on exceptions for control flow.
5.  **Atomic & Transaction-Aware Services:** A recent, major refactoring has made the entire Data Access Layer fully transaction-aware. This allows the Business Logic Layer to orchestrate complex, multi-step database operations as single, atomic units of work, which is critical for maintaining data integrity during workflows like finalizing a sale.

This document will dissect these principles, providing detailed diagrams and descriptions of each component, to create a deep and actionable understanding of the codebase.

## **2.0 Architectural Vision & Principles**

The architecture of SG-POS is not accidental; it is a deliberate implementation of established software engineering principles chosen to meet the demands of an enterprise-grade application.

*   **Maintainability:** The highest priority. The strict layering and separation of concerns mean that a developer can work on the UI without understanding the intricacies of database transactions, and vice-versa. This reduces cognitive load and minimizes the risk of introducing bugs.
*   **Testability:** The architecture is designed for automated testing. By decoupling business logic from the UI and database, individual components (especially the "managers" in the business logic layer) can be tested in isolation. The project's testing strategy, using an in-memory SQLite database and `factory-boy` for data generation, confirms this design goal.
*   **Scalability:** While currently a desktop application, the separation of the backend logic (business, service, and persistence layers) from the UI means the core application could be repurposed to power a web API or a mobile application in the future with minimal changes to the core business rules.
*   **Robustness & Data Integrity:** This is non-negotiable for a system handling sales and financial data. The architecture enforces this through:
    *   **Atomic Transactions:** As demonstrated by the recent refactoring, complex operations that modify multiple tables (e.g., `sales_transactions`, `inventory`, `stock_movements`) are guaranteed to either all succeed or all fail, preventing inconsistent database states.
    *   **Pydantic DTOs:** Using strongly-typed Data Transfer Objects for communication between layers ensures that data is always valid and conforms to an expected "shape" before being processed.
    *   **Result Pattern:** Explicitly handling potential failures (e.g., "Insufficient Stock," "Duplicate SKU") at the function-call level makes the system's behavior predictable and prevents unexpected crashes.

## **3.0 Core Components & Layered Architecture**

The entire application is organized into four distinct layers. This separation is the most fundamental concept in the codebase.

### **3.1 High-Level Interaction Diagram**

The following diagram illustrates the strict, unidirectional flow of control and data between the layers. The UI never talks directly to the database; it only communicates with the Business Logic Layer.

```mermaid
graph TD
    subgraph "Presentation Layer (app/ui)"
        UI[UI Views & Dialogs<br><em>(e.g., POSView, ProductDialog)</em>]
    end

    subgraph "Business Logic Layer (app/business_logic)"
        Managers[Managers<br><em>(e.g., SalesManager)</em>]
        DTOs[Data Transfer Objects (DTOs)<br><em>(e.g., SaleCreateDTO)</em>]
    end

    subgraph "Data Access Layer (app/services)"
        Services[Services (Repositories)<br><em>(e.g., SalesService)</em>]
    end

    subgraph "Persistence Layer (app/models)"
        Models[ORM Models<br><em>(e.g., SalesTransaction)</em>]
    end
    
    subgraph "Infrastructure (app/core)"
        Core[ApplicationCore<br><em>(DI Container)</em>]
        AsyncBridge[Async Bridge]
        Result[Result Pattern]
    end

    subgraph "External Systems"
        DB[(PostgreSQL Database)]
    end

    %% Define the interactions
    UI -- "1. User action with DTO" --> Core;
    Core -- "2. Routes call to appropriate Manager" --> Managers;
    Managers -- "3. Uses DTO for input, enforces rules" --> DTOs;
    Managers -- "4. Calls one or more Services" --> Services;
    Services -- "5. Executes queries using Models" --> Models;
    Models -- "6. Maps to Database Tables" --> DB;
    DB -- "7. Returns data" --> Models;
    Models -- "8. Returns ORM objects" --> Services;
    Services -- "9. Returns ORM objects or raw data" --> Managers;
    Managers -- "10. Converts result to DTO" --> DTOs;
    Managers -- "11. Returns Result<DTO> to Core" --> Core;
    Core -- "12. Signals UI to update" --> UI;
    
    %% Connect Infrastructure
    UI -- "Uses for async calls" --> AsyncBridge;
    AsyncBridge -- "Manages" --> Core;
```

### **3.2 Layer Deep Dive**

#### **3.2.1 Presentation Layer (`app/ui`)**

*   **Responsibility:** To display information to the user and to capture user input. This layer is intentionally "dumb" and contains no business logic.
*   **Key Components:**
    *   **`MainWindow`:** The main application shell. It contains the `QStackedWidget` that holds all the different views and the main `QMenuBar` for navigation. It implements lazy-loading for all non-essential views to ensure a fast application startup.
    *   **Views (`app/ui/views`):** These are the main screens of the application (e.g., `POSView`, `ProductView`, `DashboardView`). Each view is a `QWidget` responsible for a specific functional area. They interact with the `ApplicationCore` to fetch data and trigger operations.
    *   **Dialogs (`app/ui/dialogs`):** These are modal or non-modal windows for specific, focused tasks like creating a new product (`ProductDialog`) or processing a payment (`PaymentDialog`). They follow the same pattern of packaging user input into a DTO and passing it to a manager.
    *   **Widgets (`app/ui/widgets`):** Reusable, custom UI components that enhance user experience and reduce code duplication.
        *   `ManagedTableView`: A critical UX component that wraps a `QTableView`. It standardizes the display of loading states ("Loading data...") and empty states ("No products found."), providing clear feedback to the user during asynchronous data loads.
        *   `KpiWidget`: A simple but effective widget used in the `DashboardView` to display a key performance indicator with a title and a large value.
*   **Asynchronous Interaction:** The UI's responsiveness is guaranteed by the `Async Bridge`. When a user clicks a button that triggers a database operation, the view calls a manager method via the `core.async_worker.run_task()`. It provides a callback function (e.g., `_on_done`). The UI is immediately free. Once the background task completes, the `Async Bridge` ensures the callback is safely executed back on the main UI thread to display the result (e.g., show a "Success" `QMessageBox` or refresh a table).

#### **3.2.2 Business Logic Layer (`app/business_logic`)**

*   **Responsibility:** To be the brain of the application. This layer enforces all business rules, orchestrates complex workflows, and acts as the intermediary between the UI and the data layer.
*   **Key Components:**
    *   **Managers (`app/business_logic/managers`):** Each manager (e.g., `SalesManager`, `InventoryManager`, `ProductManager`) is responsible for a specific business domain.
        *   **Orchestration:** A single manager method can coordinate multiple services. For example, `SalesManager.finalize_sale()` calls the `InventoryManager` to deduct stock and the `CustomerManager` to add loyalty points, all within a single database transaction it controls.
        *   **Business Rules:** This is where rules like "a product's SKU must be unique" or "payment must be sufficient" are checked before any data is sent to the services.
        *   **Transaction Control:** Managers are responsible for defining the boundaries of an atomic unit of work. They start a session via `async with self.core.get_session() as session:` and pass this single session object to all service calls that need to be part of that transaction.
    *   **Data Transfer Objects (DTOs) (`app/business_logic/dto`):** These are Pydantic models that define the data contracts between layers.
        *   **Decoupling:** The UI only needs to know how to create a `ProductCreateDTO`; it doesn't need to know anything about the `Product` ORM model. This decouples the UI from the database schema.
        *   **Validation:** Pydantic automatically validates incoming data. If the UI tries to create a product with a selling price that is not a valid number, Pydantic will raise a `ValidationError` before it even reaches the manager's logic, providing an early failure mechanism.
        *   **Clarity:** DTOs make the expected data for any operation explicit and self-documenting.

#### **3.2.3 Data Access Layer (`app/services`)**

*   **Responsibility:** To execute database operations. This layer implements the **Repository Pattern**, where each service is a repository for a specific ORM model. Its job is to abstract away the details of SQLAlchemy and SQL.
*   **Key Components:**
    *   **`BaseService`:** A foundational class that provides generic CRUD (Create, Read, Update, Delete) methods (`get_by_id`, `get_all`, `create`, etc.). This drastically reduces boilerplate code in the concrete services.
    *   **Concrete Services (e.g., `ProductService`, `CustomerService`):** These inherit from `BaseService` and add more specific query methods, such as `ProductService.get_by_sku()` or `CustomerService.search()`.
    *   **Transaction-Awareness:** A crucial feature implemented during the recent refactoring. Every service method now accepts an optional `session: AsyncSession` argument. The internal `_get_session_context` helper will use this provided session if it exists, or create a new one if it doesn't. This allows a manager to pass a single session down to multiple service calls, ensuring they all operate within the same atomic transaction.

#### **3.2.4 Persistence Layer (`app/models`)**

*   **Responsibility:** To define the application's data structure as a set of Python classes that map to database tables. This is the single source of truth for the database schema.
*   **Key Components:**
    *   **`Base` and `TimestampMixin` (`app/models/base.py`):** The declarative base for all ORM models. It configures the `sgpos` schema and a standard naming convention. The `TimestampMixin` automatically adds `created_at` and `updated_at` columns to models that use it. A key feature is that it conditionally sets the schema to `None` when the `SGPOS_TEST_MODE` environment variable is set, allowing the same models to work seamlessly with schema-less SQLite during tests.
    *   **ORM Models (`app/models/*.py`):** Each file defines the models for a specific domain (e.g., `product.py`, `sales.py`). These classes use standard SQLAlchemy `Column` and `relationship` declarations to define the tables, columns, data types, foreign keys, and relationships (one-to-many, many-to-one).

#### **3.2.5 Core Infrastructure (`app/core`)**

*   **Responsibility:** To provide the architectural glue and cross-cutting concerns that support all other layers.
*   **Key Components:**
    *   **`ApplicationCore`:** The heart of the application. It acts as a DI container and service locator. It is instantiated once in `main.py` and passed to the `MainWindow` and all views. It is responsible for:
        *   Initializing and managing the database engine and session factory.
        *   Starting and stopping the `AsyncWorkerThread`.
        *   Providing lazy-loaded properties for every manager and service (e.g., `core.sales_manager`), so components are only created when first accessed.
    *   **`Async Bridge` (`async_bridge.py`):** A critical component for a responsive desktop application. It creates a dedicated `QThread` to run the `asyncio` event loop. The `AsyncWorker` object lives in this thread and accepts coroutines for execution. It uses Qt's signal/slot mechanism to safely communicate results back to the main UI thread, preventing any direct, unsafe cross-thread calls.
    *   **`Result` Pattern (`result.py`):** Defines the `Success` and `Failure` wrapper classes. By forcing functions to return `Result[SomeValue, ErrorString]`, the architecture makes error handling explicit. The caller *must* check if the result is a `Success` or `Failure`, leading to more robust code than traditional `try...except` blocks for predictable errors.
    *   **`Settings` (`config.py`):** A Pydantic `BaseSettings` model that loads all configuration from environment variables and the `.env.dev` file. This provides strongly-typed, validated configuration at application startup.

## **4.0 Data Flow & Key Workflows**

Understanding how the layers interact is best done by tracing a complete user workflow.

### **4.1 Workflow: Finalizing a Sale (The Critical Path)**

This workflow was the subject of the recent major refactoring and now represents the gold standard for operations in this application.

1.  **UI (`POSView` -> `PaymentDialog`):** The user clicks "PAY", then "Finalize Sale". The `PaymentDialog` collects all necessary information (cart items from the `CartTableModel`, payment details) and packages it into a `SaleCreateDTO`.
2.  **Async Bridge:** The `POSView` calls `self.core.sales_manager.finalize_sale(dto)` via the `self.core.async_worker.run_task()` method, providing an `_on_done` callback function. Control immediately returns to the UI, which remains responsive.
3.  **Business Logic (`SalesManager.finalize_sale`):** Now running on the background thread.
    a.  **Pre-computation:** It fetches all `Product` models for the items in the cart to get authoritative data like `cost_price` and `gst_rate`.
    b.  **Calculation:** It calculates the sale totals (`subtotal`, `tax_amount`, `total_amount`) and validates that the payment is sufficient.
    c.  **Transaction Start:** It opens an atomic transaction block: `async with self.core.get_session() as session:`.
    d.  **Orchestration (within transaction):**
        i.  It calls `self.inventory_manager.deduct_stock_for_sale(...)`, passing the `session` object. The `InventoryManager` in turn calls `InventoryService.adjust_stock_level(...)`, also passing the same `session`.
        ii. It calls `self.customer_manager.add_loyalty_points_for_sale(...)`, again passing the `session`.
        iii. It constructs the `SalesTransaction`, `SalesTransactionItem`, and `Payment` ORM objects.
        iv. It calls `self.sales_service.create_full_transaction(sale, session)`.
    e.  **Persistence (`SalesService`):** The service adds the `SalesTransaction` object graph to the session and calls `session.flush()`. This sends all `INSERT` and `UPDATE` statements to the database but does not yet commit them.
    f.  **Post-Persistence (within transaction):** The `SalesManager` now has the persisted ORM objects. It uses the pre-computed data from step 3b and the persisted data to manually construct a `FinalizedSaleDTO`. This is the crucial step that avoids all lazy-loading errors.
    g.  **Transaction End:** The `async with` block concludes, and the `ApplicationCore` automatically calls `session.commit()`. All changes are now permanently saved to the database. If any step had failed, an exception would have been raised, and `session.rollback()` would have been called instead, leaving the database untouched.
4.  **Async Bridge:** The `Result[FinalizedSaleDTO, str]` is returned from the manager. The bridge's `callback_ready` signal is emitted, carrying the result back to the main thread.
5.  **UI (`POSView._on_done`):** The callback function executes on the UI thread. It checks if the result is a `Success` or `Failure` and displays the appropriate `QMessageBox` to the user.

### **4.2 Workflow: Searching for a Product**

This shows a simpler, read-only data flow.

1.  **UI (`ProductView`):** The user types in the `search_input` `QLineEdit`. The `textChanged` signal is connected to a `QTimer` to debounce the input.
2.  **UI (`ProductView._load_products`):** After 350ms of no typing, the timer's `timeout` signal calls this slot.
    a.  It shows the loading state: `self.managed_table.show_loading()`.
    b.  It calls `self.core.product_manager.search_products(...)` via the `async_worker`.
3.  **Business Logic (`ProductManager.search_products`):**
    a.  It calls `self.product_service.search(term)`.
    b.  Upon receiving the list of `Product` ORM objects from the service, it converts each one into a `ProductDTO`.
    c.  It returns `Success([ProductDTO, ...])`.
4.  **UI (`ProductView._on_done`):** The callback receives the list of `ProductDTO`s.
    a.  It passes this list to the `ProductTableModel.refresh_data()`, which notifies the `QTableView` to update itself.
    b.  It calls `self.managed_table.show_table()` (or `show_empty()` if the list is empty) to hide the loading message and display the results.

## **5.0 Database Schema & Migrations**

*   **Schema (`sgpos`):** All application tables are logically grouped within the `sgpos` PostgreSQL schema. This isolates the application's data and prevents conflicts with other potential schemas in the same database instance.
*   **Migrations (`migrations/`):** The project uses Alembic to manage database schema evolution.
    *   `env.py`: The Alembic environment is configured to read the `DATABASE_URL` from the `.env.dev` file. It cleverly replaces the `asyncpg` driver with `psycopg2` for compatibility with Alembic's synchronous operations. It also correctly handles the schema setting for both PostgreSQL and SQLite (for tests).
    *   `versions/d5a6759ef2f7_...`: This initial migration script is a hand-corrected, authoritative version that creates the entire database schema from scratch. It correctly orders table creation to satisfy foreign key constraints and includes all necessary columns, indexes, and CHECK constraints to match the ORM models perfectly.
*   **Reference (`scripts/database/schema.sql`):** This file provides a complete, raw SQL definition of the target database schema. It serves as an excellent, quick reference for database administrators or for developers wanting to understand the final table structures without interpreting Python code.

## **6.0 Testing Strategy**

The project has a robust and professional testing strategy centered around `pytest`.

*   **Isolation (`conftest.py`):** The test environment is completely isolated from the development database. The `db_engine` fixture creates an **in-memory SQLite database** for each test session (`pytest` run). This ensures tests are fast and have no side effects.
*   **Data Fixtures (`conftest.py`, `factories.py`):**
    *   The `db_session` fixture provides a clean, transaction-wrapped session for every single test function. It automatically rolls back the transaction after the test, guaranteeing that each test starts with a clean slate.
    *   `factories.py` uses the `factory-boy` library to define factories for creating ORM model instances. This makes setting up test data clean, readable, and maintainable.
*   **Structure (`tests/unit`):** The unit test directory mirrors the `app` directory structure, making it easy to locate tests for a specific component (e.g., tests for `app/business_logic/managers/sales_manager.py` are in `tests/unit/business_logic/managers/test_sales_manager.py`).
*   **Test Focus:** The current tests correctly focus on the most critical and complex part of the application: the **Business Logic Layer (Managers)**. By testing the managers, the tests inherently cover the interactions with the service and persistence layers, validating entire workflows.

## **7.0 Code Quality & Tooling**

The project maintains a high standard of code quality through a suite of integrated tools configured in `pyproject.toml`.

*   **Dependency Management (`Poetry`):** Poetry provides deterministic dependency resolution via the `poetry.lock` file, ensuring that every developer and deployment environment uses the exact same versions of all packages, eliminating "works on my machine" issues. It also manages the project's virtual environment.
*   **Code Formatting (`Black`):** The "uncompromising code formatter" is used to enforce a single, consistent code style across the entire project. This eliminates debates about style and makes the code easier to read.
*   **Linting (`Ruff`):** An extremely fast and powerful linter that replaces multiple older tools (like `flake8` and `isort`). It is configured to catch a wide range of potential bugs, style issues, and security vulnerabilities.
*   **Static Type Checking (`MyPy`):** The configuration for MyPy is set to be very strict (`disallow_untyped_defs`, `strict_optional`). This forces developers to be explicit about data types, which helps catch a huge class of bugs before the code is even run and dramatically improves code readability and maintainability.

## **8.0 Project Structure Deep Dive**

This section details the purpose of each file and directory in the project root.

### **8.1 File Structure Diagram**

```
sg-pos-system/
├── app/                        # Primary Application Code
│   ├── core/                   #   - DI, Async Bridge, Config, Result Pattern
│   ├── business_logic/         #   - Managers & DTOs (The "Brain")
│   ├── services/               #   - Repositories (Database Queries)
│   ├── models/                 #   - SQLAlchemy ORM Models (DB Schema)
│   └── ui/                     #   - PySide6 UI Code (Views, Dialogs)
├── migrations/                 # Alembic Database Migration Scripts
├── scripts/                    # Helper scripts (e.g., Seeding DB)
├── tests/                      # Automated Test Suite (Pytest)
├── .env.example                # Environment Variable Template
├── .gitignore                  # Git Ignore Configuration
├── alembic.ini                 # Alembic Configuration
├── docker-compose.dev.yml      # Docker Service for PostgreSQL DB
├── pyproject.toml              # Poetry Project Definition & Dependencies
└── README.md                   # Main Project Documentation
```

### **8.2 File & Directory Descriptions**

| Path                             | Description                                                                                              |
| -------------------------------- | -------------------------------------------------------------------------------------------------------- |
| `pyproject.toml`                 | **Central Configuration.** Defines all dependencies, project metadata, and configurations for `pytest`, `black`, `ruff`, and `mypy`. The single source of truth for project setup.     |
| `docker-compose.dev.yml`         | **Database Service.** Defines and configures the PostgreSQL container for local development, reading environment variables from `.env.dev`.        |
| `alembic.ini` / `migrations/`    | **Database Schema Management.** Configuration and auto-generated scripts for evolving the database schema. The `migrations/env.py` file is key to making this process work for both PostgreSQL and SQLite. |
| **`app/`**                       | **Application Source Root.** Contains all the core application code, organized by architectural layer. |
| `app/main.py`                    | **Entry Point.** The script that starts the application. It initializes `ApplicationCore`, creates the `MainWindow`, and begins the Qt event loop.        |
| `app/core/`                      | **The Architectural Core.** The most critical, non-domain-specific code. Contains the DI container, async bridge, and configuration loader. |
| `app/models/`                    | **Persistence Layer.** Defines all SQLAlchemy ORM models, representing the database schema in Python. |
| `app/services/`                  | **Data Access Layer.** Implements the Repository pattern. Contains all database query logic, abstracting SQLAlchemy from the rest of the app. |
| `app/business_logic/managers/`   | **Business Logic Layer.** The "brain" of the application, orchestrating workflows and enforcing business rules. |
| `app/business_logic/dto/`        | **Data Contracts.** Contains all Pydantic models (DTOs) for validated, type-safe data transfer between the UI and the Business Logic layers. |
| `app/ui/`                        | **Presentation Layer.** Contains all PySide6 code, including main views, dialogs, and reusable widgets. This layer is kept clean of any business logic. |
| **`tests/`**                     | **Automated Tests.** Contains the entire `pytest` suite. |
| `tests/conftest.py`              | **Test Setup.** Configures the in-memory SQLite database and provides the `test_core` fixture for dependency injection into tests. |
| `tests/factories.py`             | **Test Data.** Defines `factory-boy` classes for easily creating test data, making tests cleaner and more readable. |
| **`scripts/`**                   | **Developer Utilities.** Holds standalone scripts for development tasks. |
| `scripts/database/schema.sql`    | **DB Reference.** A raw SQL snapshot of the complete, correct database schema. |
| `scripts/database/seed_data.py`  | **DB Population.** A script to populate a fresh database with the essential data (default company, admin user) needed to run the application. |

## **9.0 Conclusion**

The SG-POS system is a well-architected, robust, and maintainable application. Its design emphasizes a clean separation of concerns, which not only facilitates current development and debugging but also positions the project for future scalability and feature expansion. The recent successful refactoring of its transactional logic has significantly hardened the codebase, resolving critical bugs and bringing the implementation into closer alignment with its architectural vision. This document provides a clear and comprehensive map of that vision and its execution within the codebase.

---
https://aistudio.google.com/app/prompts?state=%7B%22ids%22:%5B%221QHPuQ2OmdJqV6C6LfjDiePbLBUJZt8BL%22%5D,%22action%22:%22open%22,%22userId%22:%22108686197475781557359%22,%22resourceKeys%22:%7B%7D%7D&usp=sharing, https://drive.google.com/file/d/1WE7SP2KKstgtv-ic3NpKSV06F42uPZ-b/view?usp=sharing, https://drive.google.com/file/d/1ogzzUdmf1E20GNgAp7l5BPxOzYedBuyx/view?usp=sharing, https://drive.google.com/file/d/1rTViMCAfPJNou719v2qYziZ8o3aJ1UDg/view?usp=sharing, https://drive.google.com/file/d/1vfl0VUd-qB5sPz6YMsEp5hJFwyQiyxgJ/view?usp=sharing, https://drive.google.com/file/d/1vncax4DJ4L6LFuboaXx0UDMZsbc_kiiv/view?usp=sharing, https://drive.google.com/file/d/1x46nXSW7b8WZxVMaklB3vTTpW0aHMBJT/view?usp=sharing

