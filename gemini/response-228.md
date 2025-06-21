Of course. I have received your instructions and will proceed with the requested tasks meticulously.

### **Phase 1: Startup Log Validation**

I will begin by validating the application startup log.

*   **Initial Connection:** The first six log entries (`20:50:46,851` to `20:50:46,857`) show a standard SQLAlchemy `asyncpg` driver connection sequence to the PostgreSQL database. It correctly checks the version, schema, and string conformity. The `SELECT 1` followed by a `ROLLBACK` is the successful execution of the `_initialize_async_components` test connection in `ApplicationCore`, confirming the database is reachable. **This is normal and correct.**
*   **User Interaction Simulation:** The subsequent `SELECT` statements (`20:50:52,385` onwards) correspond to user actions in the UI, such as searching for a customer and then products. The use of `ILIKE` and parameterized queries (`$1::UUID`, `$2::VARCHAR`) demonstrates correct, safe query construction. The note `[cached since...]` indicates SQLAlchemy's statement caching is functioning as expected. **This is normal and correct.**
*   **Core Transaction Validation (`finalize_sale`):** The final, large block of logs starting at `20:51:08,316` is the most critical.
    *   `BEGIN (implicit)`: A transaction is correctly initiated.
    *   `SELECT...FOR UPDATE`: The code correctly locks inventory rows to prevent race conditions.
    *   `UPDATE sgpos.inventory` and `INSERT INTO sgpos.stock_movements`: Stock is correctly adjusted and logged.
    *   `INSERT INTO sgpos.sales_transactions`, `INSERT INTO sgpos.payments`, `INSERT INTO sgpos.sales_transaction_items`: The entire sale and its related entities are inserted into the database.
    *   `SELECT sgpos.sales_transactions...` and `SELECT sgpos.sales_transaction_items...`: These are the `session.refresh()` calls, correctly placed *inside* the transaction block.
    *   `COMMIT`: The entire unit of work is committed atomically.
    *   `Shutting down core resources...`: The application was closed gracefully.

**Conclusion:** The log is **clean** and shows **no errors**. Most importantly, it demonstrates that the fix for the `greenlet_spawn` error was **successful**. The entire sales finalization process now occurs within a single, atomic transaction, and all necessary data is loaded before the session is closed, which aligns perfectly with the analysis in the provided `Code Change Regression Analysis Report.md`.

### **Phase 2: Codebase Review and Validation**

I will now proceed with a thorough line-by-line review of the provided codebase files. I have ingested the file structure, the list of recently impacted files, and the detailed regression analysis report. My review confirms that the changes described in the report have been implemented correctly and consistently. The service layer is now fully transaction-aware, the manager layer correctly propagates the session context, and the final `SalesManager` logic properly decouples the ORM objects from the final DTO creation, preventing the `greenlet_spawn` error. The codebase is architecturally sound and robust.

### **Phase 3: Architecture Overview Document Generation**

Based on my comprehensive review, I have generated the requested `Project Architecture Overview Document.md`.

---

# **Project Architecture Overview Document**

| **Document ID:** | SG-POS-AOD-2025-01       | **Version:** | 1.0                |
| :--------------- | :----------------------- | :----------- | :----------------- |
| **Project:**     | SG Point-of-Sale System  | **Date:**    | 2025-06-21         |
| **Prepared By:** | CodeNavigator (AI Assistant) | **Status:**  | **Complete**       |

## 1.0 Executive Summary

This document provides a definitive architectural overview of the SG Point-of-Sale (SG-POS) system. It is intended for developers, architects, and technical stakeholders to gain a deep and comprehensive understanding of the system's design principles, structure, and data flow. The architecture is explicitly designed to support an enterprise-grade desktop application, prioritizing **maintainability, scalability, testability, and a responsive, non-blocking user experience.**

The SG-POS system is built upon a set of foundational principles:

1.  **Strict Layered Architecture:** A clear separation of concerns into four distinct layers (Presentation, Business Logic, Data Access, Persistence) to ensure low coupling and high cohesion.
2.  **Dependency Injection (DI) & Centralized Core:** A single `ApplicationCore` acts as a service locator and DI container, managing the lifecycle and providing access to all application services and managers.
3.  **Asynchronous by Default:** The entire backend is built on Python's `asyncio`, with a robust `AsyncBridge` to the synchronous Qt front-end, guaranteeing that the UI never freezes during I/O-bound operations like database access.
4.  **Explicit Error Handling:** The use of a `Result` monad (`Success`/`Failure`) for all business and data access operations replaces traditional exception handling for predictable errors, leading to more robust and readable code.
5.  **Atomic and Consistent Transactions:** Leveraging SQLAlchemy's "Unit of Work" pattern, all complex business operations are executed within a single, atomic database transaction, ensuring data integrity even in the face of errors.

This document will dissect each of these principles, illustrate the overall architecture with a detailed system diagram, provide a thorough breakdown of the codebase structure, and analyze the specific responsibilities and interactions of each layer.

## 2.0 Core Architectural Principles

The stability and quality of the SG-POS system are a direct result of its adherence to several key architectural patterns.

### 2.1 The Layered Architecture

The codebase is strictly divided into four horizontal layers. Data and control flow primarily in one direction (from Presentation down to Persistence, and results back up), preventing circular dependencies and creating a clear, manageable structure.

*   **L1: Presentation Layer (`app/ui/`)**: This is the "face" of the application, built with **PySide6 (Qt6)**. Its sole responsibility is to display data to the user and capture user input. It contains **no business logic**. When a user performs an action (e.g., clicks "Save"), this layer constructs a **Data Transfer Object (DTO)** and passes it to the Business Logic Layer for processing via the `ApplicationCore`.
*   **L2: Business Logic Layer (`app/business_logic/`)**: This is the "brain" of the application. It is composed of **Managers** (e.g., `SalesManager`, `ProductManager`) that orchestrate complex business workflows. They enforce all business rules (e.g., "a product's SKU must be unique," "a sale's payment must cover the total due"). Managers are the only components that can coordinate between different services. For example, `SalesManager` calls both `InventoryService` and `CustomerService` to finalize a sale. This layer communicates with the Presentation Layer and the Data Access Layer using clean, strongly-typed DTOs.
*   **L3: Data Access Layer (`app/services/`)**: This layer implements the **Repository Pattern**. It contains a collection of **Services** (e.g., `ProductService`, `CustomerService`) that encapsulate all database query logic for a specific entity. Its responsibility is to translate abstract requests (e.g., `get_product_by_id`) into concrete SQLAlchemy queries. It completely hides the complexity of the database from the Business Logic Layer. A crucial aspect of this layer is that all its methods are **transaction-aware**, designed to be executed within a session provided by a Manager.
*   **L4: Persistence Layer (`app/models/`)**: This is the foundational layer that maps directly to the PostgreSQL database schema. It contains all **SQLAlchemy ORM models** (e.g., `Product`, `SalesTransaction`). This is the only part of the application that has direct knowledge of database table names, columns, relationships, and constraints.

### 2.2 Dependency Injection & The Application Core

The `app.core.application_core.ApplicationCore` class is the heart of the system's architecture. It functions as a sophisticated **Dependency Injection (DI) container** and **Service Locator**.

*   **Lifecycle Management:** It is responsible for initializing and shutting down all core resources, including the database engine and the `AsyncBridge`.
*   **Lazy Loading:** It provides lazy-loaded access to every Manager and Service in the application via Python properties (e.g., `core.product_manager`). This means resources are only created on their first use, improving startup performance and breaking potential import cycles.
*   **Centralized Access:** By passing the `core` instance to UI views and managers, the entire application has a single, consistent entry point for accessing backend functionality, rather than importing services and managers directly, which would lead to tight coupling.

### 2.3 Asynchronous UI & The Async Bridge

A key feature for a high-quality user experience in a data-intensive desktop application is a **non-blocking UI**. The SG-POS system achieves this through a custom `app.core.async_bridge.AsyncWorkerThread`.

*   **The Problem:** Qt's event loop runs on the main thread. If a database query or any other long-running I/O operation is executed on the main thread, the UI will freeze until the operation completes.
*   **The Solution:**
    1.  An `AsyncWorkerThread` is started, which runs a separate `asyncio` event loop in a background thread.
    2.  All business logic and data access code is `async` and is executed on this worker thread.
    3.  When the UI needs to perform an action, it calls `core.async_worker.run_task(coro, on_done_callback)`. This safely schedules the coroutine (`coro`) to run on the background thread's event loop.
    4.  When the coroutine completes, the `AsyncWorker` emits a Qt **signal** (`callback_ready`) containing the result and the `on_done_callback` function.
    5.  This signal is received by a `QObject` on the main thread (`CallbackExecutor`), which then safely executes the callback, allowing the UI to be updated with the result without any risk of race conditions or crashes.

This pattern ensures the application remains fluid and responsive at all times, regardless of the complexity of the backend operations.

### 2.4 The Result Pattern for Error Handling

Instead of relying on Python exceptions for predictable business errors (e.g., "duplicate SKU," "insufficient stock"), the application uses a `Result` monad defined in `app.core.result`.

*   Every method in the Business Logic and Data Access layers returns `Result[T, E]`, which is a union of `Success[T]` or `Failure[E]`.
*   A `Success` object wraps the successful return value.
*   A `Failure` object wraps a clean, user-friendly error string or object.
*   This forces the calling code to explicitly check for and handle the failure case (e.g., `if isinstance(result, Failure): ...`), making the error handling paths explicit and preventing unexpected crashes from unhandled business rule violations. Exceptions are reserved only for truly exceptional, unrecoverable system errors (e.g., database is offline).

### 2.5 Atomic Operations with the Unit of Work Pattern

The resolution of the `greenlet_spawn` bug highlighted the critical importance of the **Unit of Work** pattern, which is now correctly and robustly implemented.

*   **The Goal:** Ensure that a complex business operation, like finalizing a sale, either succeeds completely or fails completely, leaving the database in a consistent state (i.e., it is **atomic**).
*   **The Implementation:**
    1.  A top-level manager method (e.g., `SalesManager.finalize_sale`) initiates a database session using a context manager: `async with self.core.get_session() as session:`.
    2.  This `session` object is then passed down to every single subsequent service or manager call within that block (e.g., `inventory_manager.deduct_stock_for_sale(..., session=session)`).
    3.  All database operations performed by these downstream methods use the *same* session, effectively enlisting them in a single transaction.
    4.  SQLAlchemy's session tracks all changes made to ORM objects (inserts, updates, deletes) in memory.
    5.  Only upon exiting the `async with` block without an error does `session.commit()` get called, writing all the changes to the database at once. If any error occurs anywhere in the block, `session.rollback()` is called automatically, discarding all changes.

This pattern is the bedrock of the application's data integrity.

## 3.0 Architectural Flow Diagram

The following diagram illustrates the high-level interaction between the application's components, centered around the `ApplicationCore`.

```mermaid
graph TD
    subgraph "User Interface (UI Thread)"
        A[Presentation Layer<br>app/ui]
    end
    
    subgraph "Backend (Worker Thread)"
        B[Business Logic Layer<br>app/business_logic]
        C[Data Access Layer<br>app/services]
        D[Persistence Layer<br>app/models]
    end

    subgraph "System Core"
        CORE[ApplicationCore<br>app/core]
        BRIDGE[Async Bridge<br>app/core/async_bridge]
    end

    subgraph "External Systems"
        DB[(PostgreSQL Database)]
    end

    A -- "1. User Action (triggers coroutine via AsyncWorker)" --> BRIDGE
    BRIDGE -- "2. Executes coroutine on Worker Thread" --> B
    CORE -- "3. Injects Services & Managers" --> B
    B -- "4. Calls Service Methods" --> C
    C -- "5. Uses ORM Models" --> D
    D -- "6. Maps to DB Schema" --> DB
    C -- "7. Executes Queries" --> DB
    DB -- "8. Returns Data" --> C
    C -- "9. Returns ORM/Result" --> B
    B -- "10. Returns DTO/Result" --> BRIDGE
    BRIDGE -- "11. Emits Signal to UI Thread" --> A
    A -- "12. Updates UI via Callback"

    style CORE fill:#f9f,stroke:#333,stroke-width:2px
    style BRIDGE fill:#ccf,stroke:#333,stroke-width:2px
```

## 4.0 Codebase Structure Deep Dive

### 4.1 File Hierarchy Diagram

```
sg-pos-system/
│
├── .env.example                # Environment variable template
├── .gitignore                  # Git ignore rules
├── alembic.ini                 # Alembic migration config
├── docker-compose.dev.yml      # Docker service for PostgreSQL DB
├── pyproject.toml              # Project dependencies and tool config (Poetry)
│
├── app/                        # Main Application Source Code
│   ├── __init__.py
│   ├── main.py                 # Application Entry Point
│   │
│   ├── core/                   # 1. Architectural Backbone
│   │   ├── application_core.py #    - DI Container / Service Locator
│   │   ├── async_bridge.py     #    - Qt/Asyncio Threading Bridge
│   │   ├── config.py           #    - Settings Management (Pydantic)
│   │   ├── exceptions.py       #    - Custom System Exceptions
│   │   └── result.py           #    - Success/Failure Result Monad
│   │
│   ├── models/                 # 2. Persistence Layer (SQLAlchemy ORM)
│   │   ├── base.py             #    - Declarative Base & TimestampMixin
│   │   ├── product.py          #    - Product, Category, Supplier Models
│   │   ├── sales.py            #    - SalesTransaction, Payment Models
│   │   └── ...                 #    - (Other model files)
│   │
│   ├── services/               # 3. Data Access Layer (Repositories)
│   │   ├── base_service.py     #    - Base class for CRUD operations
│   │   ├── product_service.py  #    - Queries for Product entities
│   │   └── ...                 #    - (Other service files)
│   │
│   ├── business_logic/         # 4. Business Logic Layer
│   │   ├── dto/                #    - Data Transfer Objects (Pydantic)
│   │   └── managers/           #    - Business Workflow Orchestrators
│   │
│   └── ui/                     # 5. Presentation Layer (PySide6)
│       ├── main_window.py      #    - Main QMainWindow hosting views
│       ├── views/              #    - Major screens (Dashboard, POS, etc.)
│       ├── dialogs/            #    - Modal dialogs (e.g., Add Product)
│       └── widgets/            #    - Reusable custom UI components
│
├── migrations/                 # Alembic Database Migration Scripts
│
├── scripts/                    # Development Utility Scripts
│
└── tests/                      # Automated Test Suite
    ├── conftest.py             # Pytest fixtures (DB setup)
    ├── factories.py            # Test data generation (factory-boy)
    └── unit/                   # Unit tests mirroring `app` structure
```

### 4.2 Key Directory & File Analysis

| Path | Purpose & Key Responsibilities |
| :--- | :--- |
| `pyproject.toml` | **Single Source of Truth for Dependencies & Tooling.** Defines project metadata, production dependencies (`SQLAlchemy`, `PySide6`), and development dependencies (`pytest`). Centralizes configuration for `black`, `ruff`, `mypy`, and `pytest`, ensuring consistent quality checks for all developers. |
| `app/main.py` | **Application Entry Point.** This is the executable script. Its primary roles are to initialize the `ApplicationCore`, create the main `MainWindow`, start the Qt application event loop (`app.exec()`), and handle graceful shutdown. |
| `app/core/application_core.py` | **The DI Container.** The most critical architectural component. It manages the database connection pool, starts the async worker thread, and provides lazy-loaded access to all services and managers. It is the glue that connects the application layers. |
| `app/core/async_bridge.py` | **The UI Responsiveness Engine.** Implements the `AsyncWorkerThread` pattern to run all `async` backend code on a separate thread, preventing the GUI from freezing. It uses Qt Signals to safely communicate results back to the UI thread for display. |
| `app/models/base.py` | **ORM Foundation.** Defines the `declarative_base` for all SQLAlchemy models. Crucially, it sets the `sgpos` schema for PostgreSQL and includes the `TimestampMixin` for automatic `created_at` and `updated_at` columns. |
| `app/services/base_service.py` | **Repository Pattern Foundation.** Implements generic, reusable CRUD (Create, Read, Update, Delete) methods. Its `_get_session_context` helper is the key to the application's robust transaction management. |
| `app/business_logic/dto/` | **Data Contracts.** This directory contains all Pydantic models that define the data structures passed between the UI and the business logic layer. They ensure that data is validated, strongly-typed, and that the layers remain decoupled. |
| `app/ui/main_window.py` | **The Application Shell.** This `QMainWindow` hosts the `QStackedWidget` which manages all the different views. It implements a **lazy-loading** pattern, creating views only when they are first requested, which significantly speeds up initial application startup. |
| `app/ui/widgets/managed_table_view.py` | **A Key UX Component.** A custom composite widget that wraps a `QTableView`. It provides a consistent user experience across the application by automatically handling the display of "Loading..." and "No data found" states, making the UI feel more polished and professional. |
| `tests/conftest.py` | **Test Environment Orchestrator.** Configures `pytest` to set up and tear down a clean, isolated, in-memory SQLite database for every single test function. This ensures that tests are fast, reliable, and do not depend on an external database or interfere with each other. |

## 5.0 Layer-by-Layer Analysis

### 5.1 Persistence Layer (`app/models/`)

This layer is the application's foundation, providing an object-oriented interface to the database.

*   **ORM:** It uses SQLAlchemy's Declarative Mapping to define Python classes that map directly to database tables.
*   **Base & Schema:** All models inherit from `Base` defined in `app/models/base.py`. This base correctly configures the `sgpos` schema for all tables in PostgreSQL, while allowing the schema to be disabled for testing with SQLite.
*   **Relationships:** Relationships between entities are explicitly defined using `sqlalchemy.orm.relationship`. This allows the ORM to handle complex joins and data loading. For example, `SalesTransaction` has relationships to `Customer`, `User`, `SalesTransactionItem`, and `Payment`, correctly modeling the real-world connections.
*   **Data Integrity:** Constraints are defined directly in the models (e.g., `UniqueConstraint`, `CheckConstraint`, `ForeignKey`), ensuring that data integrity is enforced at the database level, which is the most reliable place. The `ondelete` policies (e.g., `CASCADE`, `RESTRICT`) are carefully chosen to maintain referential integrity.
*   **Example (`app/models/sales.py`):** The `SalesTransaction` model clearly defines its columns (`id`, `company_id`, `total_amount`, etc.) and its relationships (`items`, `payments`, `customer`). The `__table_args__` correctly defines a unique constraint on the transaction number per company and a check constraint to ensure the `status` column only contains valid values from the `SalesTransactionStatus` enum.

### 5.2 Data Access Layer (`app/services/`)

This layer acts as a clean, testable boundary between the business logic and the database.

*   **Repository Pattern:** Each service class (e.g., `ProductService`) acts as a repository for its corresponding ORM model (`Product`). It exposes methods that represent data operations (e.g., `get_by_sku`, `search`).
*   **BaseService:** The `app/services/base_service.py` provides a generic implementation for common CRUD operations, reducing boilerplate code in the concrete services.
*   **Transaction-Awareness:** This is the key feature implemented to fix the `greenlet_spawn` bug. Every public method in `BaseService` and its subclasses now accepts an optional `session: AsyncSession` parameter. The `_get_session_context` helper intelligently uses this passed-in session if it exists, or creates a new one-off session if it doesn't. This allows manager-level workflows to execute a series of service calls within a single, atomic transaction.
*   **Abstraction:** This layer successfully abstracts away the underlying ORM. The business logic layer does not know or care if `get_by_id` is implemented with `session.get()` or a `select()` statement; it only cares about the result.
*   **Example (`app/services/purchase_order_service.py`):** The `get_all_with_supplier` method demonstrates a specific, optimized query. It uses `joinedload(self.model.supplier)` to tell SQLAlchemy to fetch the purchase orders and their related suppliers in a single, efficient SQL query, preventing the N+1 query problem.

### 5.3 Business Logic Layer (`app/business_logic/`)

This is where the application's rules and processes are defined and executed.

*   **Managers:** Managers (inheriting from `BaseManager`) are the primary orchestrators. They contain the "how-to" for business processes. They are the only components allowed to communicate with multiple services to complete a workflow.
*   **Data Transfer Objects (DTOs):** The `dto/` directory is crucial for decoupling. Pydantic `BaseModel`s are used to define the exact shape of data required for an operation (`...CreateDTO`, `...UpdateDTO`) and the shape of data returned to the UI (`...DTO`). This provides automatic validation and a clear, self-documenting API between the UI and the backend. For example, `ProductCreateDTO` ensures that a new product must have a `selling_price` greater than zero before any business logic is even run.
*   **Orchestration Case Study (`SalesManager.finalize_sale`):**
    1.  It receives a `SaleCreateDTO` from the UI.
    2.  It performs pre-computation and validation (calculating totals, checking payment sufficiency).
    3.  It initiates a single atomic transaction block (`async with self.core.get_session() as session:`).
    4.  **Inside the transaction**, it calls `inventory_manager.deduct_stock_for_sale`, passing the `session`.
    5.  It constructs the `SalesTransaction` ORM object and its related `items` and `payments`.
    6.  It calls `sales_service.create_full_transaction`, passing the `session` to persist everything.
    7.  It calls `customer_manager.add_loyalty_points_for_sale`, again passing the same `session`.
    8.  It gathers all the necessary data for the receipt from the now-persisted ORM objects.
    9.  **After the transaction commits**, it constructs and returns a `FinalizedSaleDTO` using the pure data gathered, ensuring no "expired" ORM objects are accessed.

### 5.4 Presentation Layer (`app/ui/`)

This layer is built with a focus on user experience, responsiveness, and reusability.

*   **Structure:** The UI is well-structured into `views` (major screens), `dialogs` (modal windows for specific tasks), and `widgets` (reusable components).
*   **Lazy Loading:** `MainWindow` uses a dictionary to cache view instances, creating them only on first access. This is a best practice that dramatically improves the application's initial startup time.
*   **Responsiveness:** As detailed in the `AsyncBridge` section, every button click that triggers a backend operation does so asynchronously, ensuring the UI remains fluid.
*   **Stateful Feedback (`ManagedTableView`):** The `app/ui/widgets/managed_table_view.py` widget is a prime example of good UX design. Instead of simply showing an empty table while data loads, it uses a `QStackedLayout` to explicitly show a "Loading..." message, and if no data is returned, it shows a user-friendly "No data found" message. This provides clear, consistent feedback to the user and is used in all major data views (`ProductView`, `CustomerView`, etc.).
*   **Decoupling:** The UI layer is completely decoupled from the backend's implementation details. It communicates solely through DTOs and knows nothing about the database or services. This means the backend could be swapped out for a REST API without requiring major changes to the UI code.

## 6.0 Database Schema and Migrations

The project employs a robust and professional strategy for managing the database schema.

*   **`schema.sql`:** This file serves as a complete, human-readable snapshot of the target database schema. While not used directly by the application, it is an invaluable tool for documentation, manual database setup, and understanding the overall structure at a glance.
*   **Alembic (`migrations/`):** The application uses Alembic for automated, version-controlled schema migrations. This is the standard for any production-grade application. It allows developers to safely evolve the database schema over time without losing data.
    *   The `migrations/versions/` directory contains Python scripts, each representing an incremental change to the schema.
    *   The `env.py` file is the heart of the migration process. It has been correctly configured to read the database URL from the environment and, critically, to handle both PostgreSQL (with a schema) for production and SQLite (without a schema) for testing. This allows the same migration scripts to work in both environments.
*   **`seed_data.py`:** This script provides a standardized way to populate a fresh database with the essential data needed to run the application (e.g., a default company, an admin user, default payment methods). This is crucial for setting up new development or testing environments quickly.

## 7.0 Testing Strategy

The project's testing strategy is built for speed, reliability, and isolation.

*   **Framework:** `pytest` is used as the test runner, with `pytest-asyncio` to handle `async` test functions.
*   **Database Isolation:** The masterstroke of the testing setup is in `tests/conftest.py`. It configures an **in-memory SQLite database** for the test suite.
    1.  An environment variable (`SGPOS_TEST_MODE`) is set to signal to the application core (specifically `app/models/base.py`) that it should *not* use the `sgpos` schema.
    2.  Before each test function runs, the `db_session` fixture creates a new transaction.
    3.  The test function executes against this transaction.
    4.  After the test completes, the transaction is **rolled back**, effectively wiping the database clean.
    5.  This ensures that every single test runs in a completely isolated environment and that tests do not interfere with one another.
*   **Data Generation:** `factory-boy` is used in `tests/factories.py` to create test data. This allows tests to quickly and easily set up the specific data they need (e.g., `ProductFactory(is_active=False)`) without verbose manual object creation.
*   **Test Structure:** The `tests/unit/` directory mirrors the `app/` directory structure, making it easy to find the tests corresponding to a specific piece of application code. The tests themselves follow a clear **Arrange-Act-Assert** pattern, making them easy to read and understand.

## 8.0 Conclusion

The SG Point-of-Sale system exhibits a mature, robust, and well-considered architecture. The strict layering, dependency injection, and asynchronous design patterns provide a solid foundation for a scalable and maintainable enterprise application. The recent refactoring to resolve the `greenlet_spawn` bug has further hardened the data access and transaction management patterns, bringing them in line with industry best practices. The comprehensive testing strategy ensures that future development can proceed with a high degree of confidence. The codebase is a strong example of professional Python application engineering.

---
https://aistudio.google.com/app/prompts?state=%7B%22ids%22:%5B%221-0cd2T3QCbEo9-BuF3E34Vxd5N1MyXxL%22%5D,%22action%22:%22open%22,%22userId%22:%22103961307342447084491%22,%22resourceKeys%22:%7B%7D%7D&usp=sharing, https://drive.google.com/file/d/16cdZU41g8TlnPThn56mUbSiy8Nj7T972/view?usp=sharing, https://drive.google.com/file/d/1TVvj8eTWvXbeDJYzeaEPE1Djr08tT21H/view?usp=sharing, https://drive.google.com/file/d/1_LwDASE6wayDCndst3vn09eiWjCExoCR/view?usp=sharing, https://drive.google.com/file/d/1gguoJbh_lGpUUGgcht9ysjD6caWMZUa7/view?usp=sharing, https://drive.google.com/file/d/1vMzJ5FDqg18_TGMitmeskTQg1vvGChOk/view?usp=sharing, https://drive.google.com/file/d/1xj34_a4v8iKjBD5Yb4PHy057i_2yZuKy/view?usp=sharing

