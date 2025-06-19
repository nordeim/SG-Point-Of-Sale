# Project Architecture Overview Document.md

## 1. Executive Summary

This document provides a comprehensive architectural overview of the **SG Point-of-Sale (SG-POS) System**, a professional-grade desktop application engineered for the specific operational and regulatory needs of Small-to-Medium Businesses (SMBs) in Singapore. The system is designed with an explicit focus on maintainability, scalability, and robustness, serving as both a functional business tool and a reference for modern Python application architecture.

At its core, SG-POS is built upon a clean, **classically layered architecture** that strictly separates concerns into four distinct tiers: Presentation (UI), Business Logic, Data Access, and Persistence. This design is augmented by modern development principles:

*   **Asynchronous by Design**: The entire backend is built on Python's `asyncio`, while the user interface, built with PySide6 (Qt6), remains fully responsive and non-blocking. A sophisticated `AsyncBridge` component seamlessly manages communication between the synchronous UI thread and the asynchronous backend worker thread.
*   **Dependency Injection (DI)**: A central `ApplicationCore` class acts as a service locator and DI container, managing the lifecycle and provision of all backend components (managers and services) in a lazy-loaded fashion. This decouples components and simplifies testing and maintenance.
*   **Explicit Error Handling**: The system eschews exceptions for predictable business logic failures, instead employing a functional `Result` pattern (`Success`/`Failure`). This leads to more readable, robust, and explicit control flow.
*   **Data Integrity and Atomicity**: Business operations that span multiple database tables (e.g., finalizing a sale which involves creating transactions, updating inventory, and recording payments) are orchestrated within atomic database transactions, ensuring the system remains in a consistent state.

The technology stack is a curated selection of industry-standard, high-quality tools:

*   **GUI**: PySide6 (Qt6)
*   **Database**: PostgreSQL
*   **Backend**: Python 3.11+ with `asyncio`
*   **ORM**: SQLAlchemy 2.0 (async)
*   **Data Validation**: Pydantic
*   **Migrations**: Alembic
*   **Tooling**: Poetry, Black, Ruff, MyPy

This document will dissect the system layer by layer, from the top-level project structure down to the intricate details of its core components, providing a definitive guide for any developer looking to understand, maintain, or extend the SG-POS codebase.

---

## 2. Architectural Vision & Principles

The architecture of SG-POS is not accidental; it is a deliberate implementation of proven software design patterns aimed at creating a professional, long-lasting application. The following principles are the pillars upon which the system is built.

### 2.1. The Layered Architecture

The codebase is strictly partitioned into four layers. Data and control flow primarily in one direction (Presentation -> Business Logic -> Data Access -> Persistence), and each layer is only aware of the layer directly beneath it.

1.  **Presentation Layer (`app/ui`)**: This is the "face" of the application. It is composed entirely of PySide6 (Qt) widgets, views, and dialogs. Its sole responsibility is to display data to the user and capture user input. **Crucially, this layer contains no business logic.** When a user performs an action (e.g., clicks a "Save" button), the UI's role is simply to gather the necessary data from its input fields, package it, and hand it off to the Business Logic Layer via the `AsyncBridge`.

2.  **Business Logic Layer (`app/business_logic`)**: This is the "brain" of the application. It contains all the business rules, policies, and decision-making logic. It is composed of:
    *   **Managers (`managers/`)**: These are high-level orchestrators that correspond to specific business use cases (e.g., `SalesManager`, `InventoryManager`). A manager coordinates with one or more services from the Data Access Layer to execute a complete workflow, ensuring all steps are performed atomically within a single database transaction.
    *   **Data Transfer Objects (DTOs) (`dto/`)**: These are Pydantic models that act as clean, validated data contracts. They define the shape of data moving between the Presentation and Business Logic layers, decoupling the UI from the underlying database models.

3.  **Data Access Layer (`app/services`)**: This layer implements the **Repository Pattern**. It is the only part of the application that directly communicates with the database. Each service (e.g., `ProductService`, `CustomerService`) corresponds to a specific ORM model (or a closely related group of models) and provides a clean API for all Create, Read, Update, and Delete (CRUD) operations. It encapsulates the complexity of writing SQLAlchemy queries, presenting the Business Logic Layer with a simple, object-oriented interface to the data.

4.  **Persistence Layer (`app/models`)**: This is the lowest layer, defining the database schema through SQLAlchemy ORM classes. Each class maps directly to a table in the PostgreSQL database and defines its columns and relationships. This layer provides an object-oriented view of the database structure.

### 2.2. Asynchronous by Design & The Non-Blocking UI

A responsive user interface is non-negotiable for a modern desktop application. Any operation that might take time (database queries, file I/O, network requests) cannot run on the main UI thread, as this would cause the application to "freeze." SG-POS solves this with a robust asynchronous architecture.

*   The entire backend (Business Logic and Data Access layers) is written using `async`/`await` syntax.
*   A dedicated background **Worker Thread** runs its own `asyncio` event loop.
*   The **`AsyncBridge` (`app/core/async_bridge.py`)** is the critical component that facilitates communication. When the UI needs to perform a backend operation, it submits the corresponding coroutine to the `AsyncBridge`. The bridge runs the coroutine on the worker thread's event loop.
*   When the operation is complete, the worker thread uses Qt's thread-safe **signal and slot mechanism** to send the result back to the main UI thread. A callback function (slot) on the main thread then safely updates the UI with the result.

This ensures the UI remains fluid and responsive at all times, even during complex database operations.

### 2.3. Dependency Injection and Inversion of Control

To avoid tight coupling and hard-coded dependencies, SG-POS uses the Dependency Injection (DI) pattern. The `ApplicationCore` class (`app/core/application_core.py`) acts as a central DI container.

*   **Initialization**: On startup, `main.py` creates a single instance of `ApplicationCore`.
*   **Provisioning**: The `ApplicationCore` is passed to the `MainWindow` and subsequently to all views and dialogs.
*   **Lazy Loading**: When a component (like `ProductView`) needs a manager (like `ProductManager`), it requests it from the core via a property (`self.core.product_manager`). The `ApplicationCore` instantiates the manager (and any services it depends on) on the first request and caches it for future use.

This pattern, also known as Inversion of Control (IoC), means that components don't create their own dependencies; they are "injected" from an external source (the core). This makes components easier to test (as dependencies can be mocked) and easier to maintain.

### 2.4. Data Integrity & Explicit Error Handling

*   **Atomic Transactions**: Business workflows often involve multiple steps. For example, finalizing a sale requires creating a `SalesTransaction` record, multiple `SalesTransactionItem` records, multiple `Payment` records, and updating `Inventory` levels. The `SalesManager` ensures all these database operations occur within a single, atomic transaction managed by its `async with self.core.get_session() as session:` block. If any step fails, the entire transaction is rolled back, leaving the database in a clean, consistent state.

*   **The `Result` Pattern**: For predictable failures (e.g., "user not found," "SKU already exists," "insufficient stock"), the application avoids using exceptions for control flow. Instead, all manager and service methods return a `Result` object, which is either a `Success(value)` or a `Failure(error)`. The calling code must explicitly check the type of the result and handle both cases. This makes the code more robust and self-documenting, as the possible failure paths are clear from the function's signature and implementation.

---

## 3. Visual Architecture Diagram

The following diagram illustrates the layered architecture and the flow of control and data for a representative user action: **creating a new product**.

```mermaid
graph TD
    subgraph Legend
        direction LR
        L1(Presentation)
        L2(Business Logic)
        L3(Data Access)
        L4(Persistence)
        L5(Core/Bridge)
        L6(Database)
        style L1 fill:#cde4ff,stroke:#333
        style L2 fill:#f8cecc,stroke:#333
        style L3 fill:#fff2cc,stroke:#333
        style L4 fill:#dae8fc,stroke:#333
        style L5 fill:#e1d5e7,stroke:#333
        style L6 fill:#d5e8d4,stroke:#333
    end

    subgraph "Main UI Thread"
        direction TB
        UI_Dialog[ProductDialog<br>(app/ui/dialogs/product_dialog.py)]
        style UI_Dialog fill:#cde4ff,stroke:#333
    end

    subgraph "Core Components"
        direction TB
        AsyncBridge[AsyncBridge<br>(app/core/async_bridge.py)]
        Core[ApplicationCore<br>(app/core/application_core.py)]
        style AsyncBridge fill:#e1d5e7,stroke:#333
        style Core fill:#e1d5e7,stroke:#333
    end

    subgraph "Backend Worker Thread"
        direction TB
        Manager[ProductManager<br>(app/business_logic/managers/product_manager.py)]
        Service[ProductService<br>(app/services/product_service.py)]
        Model[Product ORM Model<br>(app/models/product.py)]
        style Manager fill:#f8cecc,stroke:#333
        style Service fill:#fff2cc,stroke:#333
        style Model fill:#dae8fc,stroke:#333
    end
    
    subgraph "External"
        Postgres[PostgreSQL DB]
        style Postgres fill:#d5e8d4,stroke:#333
    end
    
    %% Connections
    UI_Dialog -- "1. User clicks 'Save'. Gathers data into ProductCreateDTO." --> AsyncBridge;
    AsyncBridge -- "2. Calls manager.create_product(dto) on worker thread" --> Manager;
    Manager -- "3. Validates DTO and business rules (e.g., checks for duplicate SKU)" --> Service;
    Service -- "4. Constructs Product ORM model" --> Model;
    Model -- "5. Maps object attributes to table columns" --> Postgres;
    Service -- "6. Executes SQL INSERT statement via SQLAlchemy" --> Postgres;
    Postgres -- "7. Returns newly inserted row" --> Service;
    Service -- "8. Returns Success(Product ORM object)" --> Manager;
    Manager -- "9. Converts ORM object to ProductDTO" --> AsyncBridge;
    AsyncBridge -- "10. Emits 'callback_ready' signal with Success(ProductDTO) to main thread" --> UI_Dialog;
    UI_Dialog -- "11. Callback executes, shows success message, and closes."

    %% Dependency Provisioning
    Core -- "Provides 'product_manager'" --> UI_Dialog;
    Core -- "Provides 'product_service'" --> Manager;
```

---

## 4. Codebase Structure & Key Files

The project's file structure is organized logically to reflect its architecture, making it intuitive to navigate and locate specific components.

### 4.1. File Structure Diagram

```
sg-pos-system/
│
├── .env.example              # Environment variable template
├── .gitignore                # Git ignore patterns
├── alembic.ini               # Alembic (database migration) configuration
├── docker-compose.dev.yml    # Docker configuration for local PostgreSQL database
├── pyproject.toml            # Central project definition (dependencies, tools, metadata)
│
├── app/                      # PRIMARY APPLICATION SOURCE CODE
│   ├── __init__.py
│   ├── main.py               # Application entry point
│   │
│   ├── core/                 # Architectural backbone: DI, async bridge, config, result pattern
│   │   ├── __init__.py
│   │   ├── application_core.py
│   │   ├── async_bridge.py
│   │   ├── config.py
│   │   ├── exceptions.py
│   │   └── result.py
│   │
│   ├── business_logic/       # Business Logic Layer
│   │   ├── __init__.py
│   │   ├── dto/              # Data Transfer Objects (Pydantic models)
│   │   └── managers/         # Business rule and workflow orchestrators
│   │
│   ├── models/               # Persistence Layer
│   │   ├── __init__.py
│   │   ├── base.py           # Base model for SQLAlchemy ORM
│   │   └── ... (e.g., product.py, customer.py) # Individual ORM models
│   │
│   ├── services/             # Data Access Layer (Repositories)
│   │   ├── __init__.py
│   │   ├── base_service.py   # Base service with generic CRUD
│   │   └── ... (e.g., product_service.py) # Specific data services
│   │
│   └── ui/                   # Presentation Layer
│       ├── __init__.py
│       ├── dialogs/          # Modal dialog windows
│       ├── resources/        # QSS stylesheets, icons
│       ├── views/            # Main application screens/views
│       └── widgets/          # Reusable custom widgets
│
├── migrations/               # Alembic-generated database migration scripts
│   ├── versions/
│   └── env.py                # Alembic runtime environment configuration
│
├── scripts/
│   └── database/
│       ├── schema.sql        # Reference SQL schema (source of truth for DB structure)
│       └── seed_data.py      # Script to populate a fresh DB with essential data
│
└── tests/                    # Unit, integration, and UI tests
    ├── __init__.py
    ├── conftest.py           # Pytest fixtures and configuration
    ├── integration/
    └── unit/
```

### 4.2. Folder and Key File Descriptions

#### Top-Level Files

*   `pyproject.toml`: The single source of truth for the project's identity and dependencies. Managed by Poetry, it defines project metadata (name, version), production and development dependencies, and configurations for tools like `black`, `ruff`, `mypy`, and `pytest`.
*   `docker-compose.dev.yml`: A crucial file for developer onboarding. It defines the PostgreSQL database service, allowing any developer with Docker to spin up the required database instance with a single command, ensuring a consistent development environment.
*   `alembic.ini`: The configuration file for Alembic. It points to the `migrations` script location and specifies how to connect to the database. It is configured to read the `DATABASE_URL` from the environment.
*   `.env.example` & `.env.dev`: The `.env.example` serves as a template for required environment variables. Developers copy it to `.env.dev`, which is used by `docker-compose.dev.yml` to configure the database container and by `app/core/config.py` to configure the application itself.

#### `app/` Directory (The Application)

*   `main.py`: The executable entry point of the SG-POS application. It performs the initial setup: creates the `QApplication`, initializes the `ApplicationCore`, creates the `MainWindow`, and starts the Qt event loop. It also includes top-level exception handling to gracefully manage and report catastrophic startup failures.

*   `app/core/`: The architectural heart of the system.
    *   `application_core.py`: Implements the Dependency Injection container. It is responsible for initializing and managing the lifecycle of all backend components, including the database engine and the async worker. Its properties provide lazy-loaded access to all managers and services.
    *   `async_bridge.py`: Provides the `AsyncWorkerThread` and `AsyncWorker` classes that form a robust, thread-safe bridge between the synchronous Qt world and the asynchronous backend.
    *   `config.py`: Defines the `Settings` Pydantic model, which loads and validates all configuration from environment variables and the `.env.dev` file.
    *   `result.py`: Defines the `Success` and `Failure` classes used for the `Result` error handling pattern.

*   `app/models/`: The Persistence Layer.
    *   `base.py`: Defines the SQLAlchemy `declarative_base` that all other models inherit from. It critically specifies the `sgpos` database schema and a common `TimestampMixin`.
    *   Other files (`product.py`, `customer.py`, etc.) contain the ORM class definitions, mapping Python objects to database tables and defining inter-table relationships.

*   `app/services/`: The Data Access Layer.
    *   `base_service.py`: A generic `BaseService` class that implements the Repository pattern, providing standard `get_by_id`, `get_all`, `create`, `update`, and `delete` methods, reducing boilerplate in concrete services.
    *   Other files (`product_service.py`, etc.) inherit from `BaseService` and add methods for more specific data-retrieval needs (e.g., `ProductService.search`).

*   `app/business_logic/`: The Business Logic Layer.
    *   `managers/`: Contains the high-level orchestrators (`ProductManager`, `SalesManager`, etc.). These classes encapsulate all the business rules and complex workflows.
    *   `dto/`: Contains all Pydantic-based Data Transfer Objects. These models ensure that data passed between the UI and the business logic layer is structured and validated.

*   `app/ui/`: The Presentation Layer.
    *   `main_window.py`: Defines the main application `QMainWindow`, which contains the menu bar and the `QStackedWidget` for switching between different views. Implements lazy loading of views for faster startup.
    *   `views/`: Contains the primary, full-screen widgets that represent the main modules of the application (e.g., `POSView`, `InventoryView`).
    *   `dialogs/`: Contains `QDialog` subclasses used for modal interactions, such as creating a new customer (`CustomerDialog`) or collecting a payment (`PaymentDialog`).
    *   `widgets/`: Intended for smaller, reusable custom widgets (e.g., a custom search bar), though currently empty.

#### Other Directories

*   `migrations/`: This directory is managed by Alembic. It contains `env.py` (the runtime configuration for migrations) and a `versions/` subdirectory holding the individual, auto-generated migration scripts.
*   `scripts/`: Holds utility scripts not part of the main application runtime.
    *   `database/schema.sql`: A complete, hand-written SQL schema. This is an invaluable piece of documentation, serving as the ultimate source of truth for the database design.
    *   `database/seed_data.py`: An essential script for development. After creating a fresh database with Alembic, this script populates it with the necessary prerequisite data (default company, user, roles) so the application can run.
*   `tests/`: The designated location for the project's test suite, structured for `pytest` discovery.

---

## 5. Deep Dive into Core Components

This section dissects the most important modules and patterns within the `app/` directory, providing a granular understanding of how the system functions internally.

### 5.1. The `core` Subsystem: The Application's Engine

The `app/core/` directory is the most critical part of the architecture. It provides the foundational services that enable the entire layered design to function.

#### `ApplicationCore`: The DI Container and Lifecycle Manager

The `ApplicationCore` class is the central hub of the backend.

*   **Initialization (`initialize` method)**: This is a synchronous method called from `main.py`. It orchestrates the entire startup sequence:
    1.  It creates and starts the `AsyncWorkerThread`.
    2.  It waits for the thread to confirm that its internal `asyncio` event loop is running.
    3.  It establishes the signal/slot connection between the `AsyncWorker`'s `callback_ready` signal and the `CallbackExecutor` on the main thread.
    4.  It then uses `run_task_and_wait` to execute the `_initialize_async_components` coroutine on the worker thread. This async method creates the SQLAlchemy database engine (`create_async_engine`), tests the connection, and prepares the `async_sessionmaker`.
    5.  Finally, it loads the placeholder "current user/company" UUIDs from the settings.

*   **Dependency Provisioning (Lazy-Loaded Properties)**: The class uses Python's `@property` decorator to provide lazy-loaded access to every manager and service. For example, the first time `core.product_manager` is accessed:
    1.  The code inside the `product_manager` property method runs.
    2.  It checks if an instance exists in the internal `_managers` dictionary.
    3.  If not, it imports `ProductManager`, creates an instance (`ProductManager(self)`), and stores it in the dictionary.
    4.  It returns the instance.
    Subsequent calls will find the cached instance and return it immediately. This is highly efficient and ensures single instances of these components throughout the application's lifecycle.

*   **Session Management (`get_session`)**: This is an `asynccontextmanager`. It provides a standardized, safe way for managers to acquire a database session. The `try...except...finally` block guarantees that the session is always committed on success, rolled back on failure, and closed afterward, preventing resource leaks and ensuring transactional integrity.

#### `AsyncBridge`: The Key to a Responsive UI

The `async_bridge.py` module is the elegant solution to the classic problem of mixing a synchronous GUI framework with an asynchronous backend.

*   **`AsyncWorkerThread`**: A `QThread` subclass whose only job is to start, run, and stop an `asyncio` event loop in the background. This isolates all blocking/async operations from the main UI thread.

*   **`AsyncWorker`**: A `QObject` that lives inside the `AsyncWorkerThread`.
    *   It receives coroutines from the main thread via its `run_task` method.
    *   `run_task` uses `loop.call_soon_threadsafe` to safely schedule the coroutine's execution on the worker's event loop.
    *   When the task completes, its `_on_task_completed` method is called (still on the worker thread).
    *   This method then **emits the `callback_ready` signal**, passing the callback function and its results (value or error) as arguments. Because this is a Qt signal, it is safely marshaled across the thread boundary to the main UI thread.

*   **`CallbackExecutor`**: A simple `QObject` living on the main thread. Its `execute` slot is connected to the `AsyncWorker`'s `callback_ready` signal. When the signal is received, `execute` runs the original callback function with the results. This completes the loop, allowing UI updates to happen safely on the main thread.

#### `Result` Pattern: Explicit and Robust Error Handling

The `Result` type, a `Union[Success[T], Failure[E]]`, is used universally by the business logic and data access layers. This provides several advantages over traditional exception-based error handling for predictable failures:

*   **Explicitness**: It forces the calling code to handle the failure case. You cannot simply access the `value` of a `Success` without first checking if the result *is* a `Success`.
*   **Type Safety**: The generic `TypeVar`s `T` and `E` allow for static analysis tools like MyPy to understand what types to expect in success and failure scenarios.
*   **Clean Control Flow**: It avoids littering the code with `try...except` blocks for non-exceptional situations (like a user entering an SKU that doesn't exist). The flow is a simple `if isinstance(result, Success): ... else: ...`.

### 5.2. The `models` (Persistence) Layer

This layer defines the "shape" of the business data. The models are well-structured, with clear naming and comprehensive relationships.

*   **`base.py`**: The use of a common `Base` with schema-aware `MetaData` is excellent practice for PostgreSQL, ensuring all tables are created within the `sgpos` schema. The `TimestampMixin` is a great DRY (Don't Repeat Yourself) approach for adding `created_at` and `updated_at` columns.
*   **Relationships**: The relationships between models are correctly defined using `relationship()` with `back_populates`. This creates a bi-directional, object-oriented navigation path (e.g., from a `Company` object, you can access `company.users`, and from a `User` object, you can access `user.company`).
*   **Cascades**: The use of `cascade="all, delete-orphan"` on relationships like `Company.users` is appropriate. It means that when a company is deleted, all of its associated users are automatically deleted as well, maintaining database integrity.
*   **Constraint Naming**: The `alembic.ini` and `migrations/env.py` are configured with a naming convention, and the models reflect this (e.g., `uq_user_company_username`). This makes database schemas more readable and maintainable.
*   **Specific Fixes Noted**: The presence of comments like `FIX: Corrected foreign_keys and primaryjoin syntax` in `accounting.py` indicates that the developer has thoughtfully resolved complex relationship challenges, particularly for polymorphic-style associations (linking a `JournalEntry` to different source documents like `SalesTransaction`).

### 5.3. The `services` (Data Access) Layer

This layer successfully abstracts away all database interaction logic.

*   **`BaseService`**: This abstract class provides a generic implementation for common CRUD operations. By inheriting from it, concrete services like `ProductService` instantly gain `get_by_id`, `get_all`, etc., without any boilerplate code.
*   **Specific Queries**: Services add methods for more complex or specific queries. A great example is `ProductService.search`, which builds a dynamic `ILIKE` query across multiple columns (`sku`, `name`, `barcode`). This is the correct place for such logic, keeping the manager clean.
*   **Session Management**: Services do not manage their own sessions. They either use the `ApplicationCore`'s session factory for simple queries or, more importantly, accept an active `AsyncSession` from a manager when participating in a larger transaction. This is a key element of the atomic transaction pattern.

### 5.4. The `business_logic` Layer: Orchestration and Rules

This is where the application's intelligence resides.

#### Data Transfer Objects (`dto/`)

The DTOs are well-defined using Pydantic, providing both data structure definition and runtime validation.
*   **Separation of Concerns**: There are distinct DTOs for creation, updates, and data retrieval (e.g., `ProductCreateDTO`, `ProductUpdateDTO`, `ProductDTO`). This is an excellent pattern. `ProductCreateDTO` doesn't have an `id` (as it doesn't exist yet), while `ProductUpdateDTO` might have different validation rules. `ProductDTO` represents the full object returned to the UI.
*   **Decoupling**: DTOs are the contract between the UI and the backend. The UI only needs to know how to create a `ProductCreateDTO`; it has no knowledge of the `Product` ORM model. This means the database schema can be changed without breaking the UI, as long as the manager can still map the DTO to the new model.

#### Managers (`managers/`)

The managers are the true orchestrators. A detailed trace of the most complex workflow, `SalesManager.finalize_sale`, reveals the power of this architecture:

1.  **Input**: The method receives a single, validated `SaleCreateDTO` from the UI.
2.  **Pre-computation**: Before starting a database transaction, it performs initial calculations and fetches necessary data, like the full `Product` objects for all items in the cart. This "fail-fast" approach prevents unnecessary database work if, for instance, a product doesn't exist.
3.  **Atomic Transaction**: It enters an `async with self.core.get_session() as session:` block. Everything inside this block is part of a single, atomic unit of work.
4.  **Orchestration**:
    *   It calls `self.inventory_manager.deduct_stock_for_sale(...)`, passing the active `session`. The `InventoryManager` performs its logic (adjusting stock, logging movements) within the *same transaction*.
    *   It constructs the `SalesTransaction` ORM object and its related `SalesTransactionItem` and `Payment` children.
    *   It calls `self.sales_service.create_full_transaction(...)`, again passing the active `session`. The service persists the entire object graph.
    *   It calls `self.customer_manager.add_loyalty_points_for_sale(...)` if a customer is involved.
5.  **Commit/Rollback**: If all steps succeed, the context manager commits the transaction when the block exits. If *any* step raises an exception (e.g., `deduct_stock_for_sale` returns a `Failure` which is then raised as an exception to trigger the rollback), the context manager automatically rolls back the entire transaction. No partial data is ever saved.
6.  **Output**: It constructs and returns a `FinalizedSaleDTO`, providing the UI with all the data needed to display a receipt, without exposing any internal ORM objects.

This workflow is a textbook example of a clean, robust, and transactional business logic implementation.

### 5.5. The `ui` (Presentation) Layer

The UI layer is well-structured and effectively leverages the backend architecture.

*   **Lazy Loading**: The `MainWindow`'s `_show_view` method is a simple but effective lazy-loading mechanism. It ensures that memory-intensive views are only created when first requested, significantly improving initial application startup time.

*   **View/Dialog Structure**: A typical view like `ProductView` follows a consistent pattern:
    1.  **`__init__`**: Initializes UI widgets, sets up a `QTimer` for debounced searching, and connects signals.
    2.  **`_setup_ui`**: Contains the boilerplate code for creating and laying out widgets.
    3.  **`_connect_signals`**: Connects button clicks and other UI events to slot methods. The search input's `textChanged` signal is cleverly connected to the `QTimer`'s `start` method, and the timer's `timeout` signal is connected to the actual data loading slot. This is a classic and effective way to implement debouncing to avoid spamming the backend with search requests on every keystroke.
    4.  **Action Slots (`_on_add_product`, etc.)**: These slots handle user actions. They open dialogs or prepare for backend calls.
    5.  **Async Call Logic (`_load_products`)**: This slot is responsible for calling the backend. It disables UI elements to prevent concurrent actions, constructs the appropriate coroutine (e.g., `self.core.product_manager.search_products(...)`), and passes it to the `async_worker.run_task` method along with a callback (`_on_done`).
    6.  **Callback Logic (`_on_done`)**: This method receives the `Result` from the backend. It re-enables the UI, checks if the result is a `Success` or `Failure`, and updates the UI accordingly (e.g., populating the table model with new data or showing a `QMessageBox` with an error).

*   **Table Models**: The use of custom subclasses of `QAbstractTableModel` (e.g., `ProductTableModel`) is the correct Qt approach for displaying data. It completely decouples the `QTableView` widget from the data source. The model emits the appropriate signals (`beginResetModel`, `dataChanged`, etc.) to notify the view of changes, allowing Qt to efficiently repaint only what's necessary.

## 6. Database & Migrations

The database schema and migration setup are professional and robust.

*   **`schema.sql`**: Having a complete, hand-written SQL file is excellent for documentation and for quickly setting up a database for other purposes (e.g., a reporting replica). It clearly defines all tables, columns, constraints, and indexes.
*   **Alembic (`migrations/`)**: The project correctly uses Alembic for managing schema evolution.
    *   The `env.py` script is correctly configured. It dynamically loads the `DATABASE_URL` from the `.env.dev` file and, most importantly, **replaces the `asyncpg` driver with `psycopg2`**. This is a critical step because Alembic operates synchronously and cannot use an asyncio driver.
    *   The `target_metadata` is correctly set to `Base.metadata` from `app/models/base.py`, allowing Alembic's autogenerate feature to detect changes in the ORM models.
    *   The `version_table_schema` is configured, ensuring that Alembic's own version tracking table is created inside the `sgpos` schema, keeping the database's public schema clean.

*   **Seeding (`scripts/database/seed_data.py`)**: The seed script is essential for developer productivity. It creates the foundational data (Company, Outlet, Admin User, Admin Role) with the static UUIDs defined in the environment configuration. This ensures that any developer can set up the project and have a working, login-able application immediately after running the setup steps.

## 7. Development & Quality Tooling

The project's `pyproject.toml` demonstrates a strong commitment to code quality and modern development practices.

*   **Poetry**: Used for dependency management and packaging. This guarantees that all developers and deployment environments use the exact same versions of all packages, preventing "works on my machine" issues.
*   **Black**: The uncompromising code formatter. Its use ensures a consistent code style across the entire project, eliminating arguments about formatting and improving readability.
*   **Ruff**: An extremely fast linter that replaces a whole suite of older tools (like `flake8`, `isort`, `pyupgrade`). Its configuration in `pyproject.toml` selects a strict set of rules, enforcing high code quality.
*   **MyPy**: The standard for static type checking in Python. The configuration is set to be strict (`disallow_untyped_defs`, `disallow_incomplete_defs`, etc.), which helps catch a wide class of bugs before the code is even run and dramatically improves code comprehensibility.
*   **Pytest**: The chosen testing framework. The configuration sets up defaults for test discovery (`testpaths`), code coverage (`--cov=app`), and integration with `pytest-qt` and `pytest-asyncio`. While the test files themselves are not present, the infrastructure is ready.

## 8. Potential Improvements & Recommendations

While the codebase is exceptionally well-architected, here are a few strategic recommendations for future enhancement:

1.  **Implement a Comprehensive Test Suite**: This is the highest priority. The architecture is highly testable, but the tests are not yet written.
    *   **Unit Tests**: For DTOs, simple helper functions, and individual methods within managers/services that contain complex logic. Dependencies should be mocked.
    *   **Integration Tests**: For testing the interaction between managers and services against a real test database. These tests would validate the entire backend workflow, from a manager call down to the database and back. `pytest-asyncio` is essential here.
    *   **UI Tests**: `pytest-qt` can be used to test UI interactions, ensuring that signals are emitted correctly and slots respond as expected.

2.  **Enhance UI Feedback for Async Operations**: While the UI is non-blocking, the user experience could be improved by providing more visual feedback.
    *   Consider implementing a global "loading" indicator or overlay that can be shown during backend operations.
    *   Disable not just the action button but all relevant form fields while an operation is in progress to prevent inconsistent state.
    *   A status bar at the bottom of the `MainWindow` could display messages like "Loading products..." or "Sale finalized successfully."

3.  **Refine Configuration Management**: The current use of static UUIDs in `.env.dev` for the "current user" context is perfect for development. For a real-world deployment, this would need to be replaced with a proper authentication system.
    *   Implement a login dialog at startup.
    *   Upon successful login, the `ApplicationCore` should be updated with the authenticated user's ID, company ID, and a selected outlet ID.

4.  **Centralize Table Model Logic**: There is some repetition in the `QAbstractTableModel` implementations across the different views. It might be beneficial to create a generic `BaseTableModel` that handles common logic like header data and can be subclassed with a simple configuration object defining the columns and data-mapping functions.

5.  **Audit Logging Strategy**: The `schema.sql` proposes a trigger-based audit logging system. This is a valid approach but has pros and cons.
    *   **Pro**: It's transparent to the application code.
    *   **Con**: It can be brittle, relies on database-specific features, and makes it harder to capture rich application-level context.
    *   **Alternative**: Integrate audit logging directly into the `BaseManager` or `BaseService`. After a successful `create` or `update`, a method could be called to log the change, capturing both the data `diff` and rich context (e.g., the specific use case being executed) that is unavailable at the database trigger level.

---
https://drive.google.com/file/d/11EUoGcc2Ooz7rfBtNPup3kDYyQbLzGCY/view?usp=sharing, https://aistudio.google.com/app/prompts?state=%7B%22ids%22:%5B%2212VGvhlsO4bTWDpTQADljLQwnQ51SA7pp%22%5D,%22action%22:%22open%22,%22userId%22:%22103961307342447084491%22,%22resourceKeys%22:%7B%7D%7D&usp=sharing, https://drive.google.com/file/d/1pBPMY3TTXyX-bu7qSeEHZ3QqivmAujF9/view?usp=sharing

