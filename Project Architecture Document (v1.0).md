<p align="center">
  <img src="https://raw.githubusercontent.com/nordeim/SG-Point-Of-Sale/refs/heads/main/POS_home_screen.png" alt="SG-POS System Logo" width="600"/>
</p>

<h1 align="center">SG Point-of-Sale: Project Architecture Document</h1>

**Version:** 1.0  
**Date:** 2024-05-21  
**Authors:** CodeNavigator AI  
**Status:** Live Document

---

## **1. Executive Summary**

This document provides a comprehensive architectural overview of the **SG Point-of-Sale (SG-POS) System**, an enterprise-grade, open-source desktop application meticulously engineered for the operational and regulatory landscape of Singapore's Small to Medium-sized Businesses (SMBs). The project's primary goal is to deliver the power, reliability, and feature set of expensive, proprietary POS systems in an accessible, modern, and maintainable package.

The architecture is the cornerstone of the SG-POS project, built with an unwavering commitment to professional software engineering principles. It is designed not only to be a functional product but also to serve as a reference implementation for building robust, scalable, and responsive Python desktop applications.

At its heart, the SG-POS system employs a **classic, strictly-enforced layered architecture**. This design philosophy separates the application into four distinct, decoupled layers: Presentation (UI), Business Logic, Data Access, and Persistence. This separation is the key to the system's maintainability, testability, and overall quality.

To ensure a fluid and responsive user experience—a non-negotiable requirement for a point-of-sale system—the architecture implements a sophisticated **asynchronous bridge**. This bridge seamlessly connects the synchronous Qt GUI event loop with a dedicated backend `asyncio` event loop. All I/O-bound operations, such as database queries, are offloaded to this background worker thread, guaranteeing that the user interface never freezes, even during intensive operations.

Data integrity and clarity are enforced through the use of **Data Transfer Objects (DTOs)**, which act as immutable data contracts between the layers. All database interactions are funneled through a **Repository Pattern**, which abstracts away the complexity of SQL and provides a clean, high-level API for data manipulation.

The entire system is orchestrated by a central **Dependency Injection (DI) container**, the `ApplicationCore`. This core component manages the lifecycle of all services and business logic managers, providing them to the parts of the application that need them via a lazy-loading mechanism. This approach minimizes coupling and simplifies the management of dependencies.

In summary, the SG-POS architecture is a professional-grade blueprint for a modern desktop application. It prioritizes **responsiveness, maintainability, testability, and scalability**. While the current implementation is a feature-complete skeleton with some functional gaps, the underlying architectural foundation is exceptionally sound and ready to support the system's continued development and future growth.

---

## **2. Core Architectural Principles & Philosophy**

The design and implementation of the SG-POS system are guided by a set of fundamental architectural principles. These are not merely suggestions but are strictly enforced across the codebase to ensure long-term quality and stability.

### 2.1. The Layered Architecture (Separation of Concerns)

The most critical principle is the strict separation of the application into four distinct layers. This model ensures that each part of the codebase has a single, well-defined responsibility.

*   **Presentation Layer (`app/ui`):** This layer's sole responsibility is to present data to the user and to capture user input. It is built with PySide6 (Qt6) and contains all windows, dialogs, views, and widgets. Crucially, this layer contains **no business logic**. It does not know how to calculate tax, how to check for stock, or how to save a customer to the database. It only knows how to display information and emit signals based on user actions (e.g., "the 'Save' button was clicked").

*   **Business Logic Layer (`app/business_logic`):** This is the "brain" of the application. It contains all the business rules, decision-making, and process orchestration. It is composed of **Managers** (e.g., `SalesManager`, `ProductManager`) that define high-level workflows. For example, the `SalesManager`'s `finalize_sale` method orchestrates everything that needs to happen when a sale is completed: validating the payment, calculating totals, deducting stock, and creating the sales record. This layer communicates with the layers above and below it using **Data Transfer Objects (DTOs)**.

*   **Data Access Layer (`app/services`):** This layer implements the **Repository Pattern**. Its only job is to handle communication with the database. It abstracts away the specifics of SQLAlchemy and SQL queries, providing a clean, object-oriented API for data manipulation (e.g., `product_service.get_by_id(uuid)`). It translates data between the domain objects (used by the Business Logic Layer) and the ORM models (used by the Persistence Layer).

*   **Persistence Layer (`app/models`):** This layer defines the application's data structure. It contains all the SQLAlchemy ORM models, which are Python classes that map directly to the PostgreSQL database tables. This layer is passive; it only defines the "shape" of the data and its relationships.

### 2.2. Unidirectional Data & Control Flow

To maintain loose coupling, the flow of data and control is strictly unidirectional. A request is initiated in the Presentation Layer, flows down through the Business Logic and Data Access layers to the database, and the result flows back up the same path.

*   A higher layer can call a lower layer (e.g., UI calls Business Logic).
*   A lower layer **must never** call a higher layer (e.g., a Service must not know about the UI).

This prevents circular dependencies and makes the system far easier to reason about, debug, and test.

### 2.3. Asynchronous, Non-Blocking UI

A point-of-sale application must be instantly responsive. A cashier cannot wait for the UI to unfreeze. The SG-POS architecture achieves this with a robust async bridge (`app/core/async_bridge.py`).

*   The main GUI runs in the main thread's Qt event loop.
*   All potentially blocking operations (database access, network requests, complex calculations) are executed in a separate worker thread that runs its own `asyncio` event loop.
*   The UI submits tasks to this worker thread and immediately returns, keeping the interface fluid.
*   When the task is complete, the worker thread uses Qt's thread-safe signal/slot mechanism to send the result back to the main thread, which can then safely update the UI.

### 2.4. Dependency Injection (DI) & Inversion of Control (IoC)

Instead of components creating their own dependencies (e.g., `SalesManager` creating an instance of `ProductService`), dependencies are "injected" from an external source. This is the principle of Inversion of Control.

*   The `app/core/application_core.py` module acts as the central **DI Container**.
*   It is responsible for creating and managing the lifecycle of all services and managers.
*   Components request their dependencies from the `ApplicationCore` (e.g., `self.core.product_manager`).
*   This approach makes components highly decoupled and easy to test in isolation, as dependencies can be replaced with mocks (fake objects) during testing. It also uses a lazy-loading pattern, so services are only instantiated on their first use, improving startup time.

### 2.5. Data Contracts via Data Transfer Objects (DTOs)

To ensure clear and stable communication between the layers, the system uses Pydantic-based Data Transfer Objects (`app/business_logic/dto/`).

*   A DTO is a simple object that does nothing but hold data. It has no methods that perform business logic.
*   When the UI needs to create a product, it doesn't pass a dozen individual arguments to the Business Logic Layer. Instead, it populates a `ProductCreateDTO` and passes that single object.
*   When the Business Logic Layer returns product data, it returns a `ProductDTO`.
*   This enforces a strict contract. The DTO defines exactly what data is expected and what will be returned. Pydantic also provides automatic data validation, catching errors early.

---

## **3. High-Level Architecture Diagram & Data Flow**

The following diagram illustrates the interaction between the architectural layers and key components. The flow demonstrates a typical user-initiated action, such as creating a new customer.

```mermaid
graph TD
    subgraph "Main Thread (GUI)"
        direction LR
        A[User Action on UI<br>(e.g., Clicks 'Save' in CustomerDialog)] --> B[Presentation Layer<br>app/ui/dialogs/customer_dialog.py];
        B --> C{Async Bridge (run_task)<br>app/core/async_bridge.py};
        F[UI Callback<br>(e.g., _on_done)] --> G[Update UI<br>(e.g., Show success message, close dialog)];
    end

    subgraph "Worker Thread (Backend)"
        direction TB
        D[Business Logic Layer<br>app/business_logic/managers/customer_manager.py] -- Calls --> E[Data Access Layer<br>app/services/customer_service.py];
        E -- Uses ORM Models --> H[Persistence Layer<br>app/models/customer.py];
    end
    
    subgraph "Database Server"
        I[PostgreSQL Database];
    end

    subgraph "Core Components (DI)"
        J[ApplicationCore<br>app/core/application_core.py];
    end

    %% Flow of Control and Data
    C -- "1. Submits 'create_customer' Coroutine to Worker" --> D;
    J -- "Provides Service Dependency" --> D;
    H -- "Maps to Table" --> I;
    E -- "2. Executes SQL INSERT" --> I;
    I -- "3. Returns Saved Record" --> E;
    E -- "4. Returns ORM Model" --> D;
    D -- "5. Converts Model to DTO, wraps in Result" --> C;
    C -- "6. Emits 'callback_ready' Signal to Main Thread" --> F;

    style A fill:#cde4ff
    style G fill:#d5e8d4
```

### **Data Flow Explanation (Create Customer Workflow):**

1.  **User Action:** The user fills out the `CustomerDialog` and clicks the "Save Customer" button. The dialog's `_on_save_accepted` slot is triggered.
2.  **DTO Creation:** The dialog gathers the data from its input fields and constructs a `CustomerCreateDTO`.
3.  **Task Submission:** The dialog calls `self.core.async_worker.run_task()`, passing it two things:
    *   The coroutine to execute: `self.core.customer_manager.create_customer(dto)`.
    *   A callback function to run on completion: `self._handle_customer_dialog_result`.
    The UI thread is now free and the dialog remains responsive.
4.  **Business Logic Execution (Worker Thread):**
    *   The `CustomerManager` receives the `CustomerCreateDTO`.
    *   It performs business rule validation (e.g., checking if a customer with the same code already exists). To do this, it requests the `CustomerService` from the `ApplicationCore`.
    *   It calls `self.customer_service.get_by_code()`.
5.  **Data Access Execution (Worker Thread):**
    *   The `CustomerService` translates the request into a SQLAlchemy query.
    *   It interacts with the `Customer` ORM model.
    *   It executes the `SELECT` query against the PostgreSQL database.
6.  **Persistence & Return:**
    *   Assuming the validation passes, the `CustomerManager` converts the `CustomerCreateDTO` into a `Customer` ORM model instance.
    *   It calls `self.customer_service.create(customer_model)`, which executes an `INSERT` statement.
    *   The database returns the newly created record.
    *   The `CustomerService` returns the saved `Customer` model back to the `CustomerManager`.
7.  **Result Wrapping:** The `CustomerManager` converts the returned `Customer` model into a `CustomerDTO` and wraps it in a `Success` object (e.g., `Success(customer_dto)`). This `Result` object is returned.
8.  **Callback Invocation:**
    *   The `AsyncBridge` receives the `Success` object.
    *   It emits a Qt signal, `callback_ready`, passing the `_handle_customer_dialog_result` function and the `Success` object as payload.
    *   Because signals are thread-safe, this communication crosses the thread boundary safely.
9.  **UI Update (Main Thread):**
    *   The `CallbackExecutor` object in the main thread receives the signal.
    *   It executes `_handle_customer_dialog_result(result, error)`.
    *   This function inspects the `Result` object, sees it's a `Success`, and updates the UI accordingly—for example, by refreshing the customer table and showing a success message.

---

## **4. File & Directory Structure Analysis**

A well-organized file structure is paramount for navigating and maintaining a complex codebase. The SG-POS project adheres to a standard, logical layout that reinforces the architectural layers.

```
sg-pos-system/
│
├── .env.example              # Template for environment variables
├── .gitignore                # Specifies intentionally untracked files to ignore
├── alembic.ini               # Configuration file for Alembic database migrations
├── docker-compose.dev.yml    # Docker Compose file for setting up the local dev database
├── pyproject.toml            # Central project definition file (dependencies, tools, metadata)
│
├── app/                      # Root directory for all application source code
│   ├── __init__.py
│   ├── main.py               # Main application entry point
│   │
│   ├── core/                 # The architectural backbone of the application
│   │   ├── __init__.py
│   │   ├── application_core.py # The DI Container and central orchestrator
│   │   ├── async_bridge.py     # Manages the Qt/asyncio bridge for a responsive UI
│   │   ├── config.py           # Pydantic-based settings management from .env files
│   │   ├── exceptions.py       # Custom application-wide exception classes
│   │   └── result.py           # Defines the Success/Failure Result monad for error handling
│   │
│   ├── business_logic/       # Business Logic Layer: The "brains" of the app
│   │   ├── __init__.py
│   │   ├── dto/                # Data Transfer Objects (Pydantic models)
│   │   └── managers/           # Orchestrates business workflows and rules
│   │
│   ├── models/               # Persistence Layer: SQLAlchemy ORM models
│   │   ├── __init__.py         # Imports all models for easy access
│   │   ├── base.py             # Declarative base and TimestampMixin for all models
│   │   └── ... (e.g., product.py, user.py)
│   │
│   ├── services/             # Data Access Layer (Repository Pattern)
│   │   ├── __init__.py
│   │   ├── base_service.py     # Base class with generic CRUD operations
│   │   └── ... (e.g., product_service.py, user_service.py)
│   │
│   └── ui/                   # Presentation Layer: All GUI components (PySide6)
│       ├── __init__.py
│       ├── main_window.py      # The main QMainWindow shell of the application
│       ├── dialogs/            # Pop-up dialogs for specific tasks (e.g., payment)
│       ├── resources/          # Static assets like stylesheets (.qss) and icons
│       ├── views/              # Main feature panels/screens (e.g., POS, Inventory)
│       └── widgets/            # Reusable custom UI widgets
│
├── migrations/               # Stores Alembic-generated database migration scripts
│   ├── versions/
│   └── env.py                # Alembic's runtime configuration script
│
├── scripts/
│   └── database/
│       ├── schema.sql          # The complete, hand-written SQL schema (source of truth)
│       └── seed_data.py        # Script for populating the database with initial data
│
└── tests/                    # Contains all unit, integration, and UI tests
    ├── __init__.py
    ├── conftest.py           # Pytest fixtures and configuration
    ├── integration/
    └── unit/
```

### **Purpose of Key Directories & Files:**

*   **`pyproject.toml`:** The single source of truth for project metadata, dependencies (production and development), and tool configurations (`pytest`, `black`, `ruff`, `mypy`). It's the first file to consult to understand the project's technology stack.
*   **`docker-compose.dev.yml`:** Defines the local development environment's services. In this case, it specifies a PostgreSQL database, ensuring that every developer runs the exact same database version without needing to install it manually. It links to the `.env.dev` file for configuration.
*   **`app/main.py`:** The executable entry point. Its job is minimal but crucial: instantiate the `ApplicationCore`, initialize it, create the `MainWindow`, show it, and start the Qt application event loop. It also contains top-level exception handling to catch critical startup failures.
*   **`app/core/`:** This is the most important directory for understanding the architecture.
    *   **`application_core.py`:** The DI container. It's the "heart" that connects all other parts of the application.
    *   **`async_bridge.py`:** The "lungs" of the application, ensuring it remains responsive by managing the two concurrent event loops (Qt and asyncio).
*   **`app/models/`:** Defines the "shape" of the business data. Each file corresponds to a domain concept (e.g., `product.py`, `sales.py`) and contains the SQLAlchemy ORM classes that map to database tables.
*   **`app/services/`:** Implements the "how" of data retrieval and persistence. This layer contains all the SQL/SQLAlchemy query logic, abstracting it away from the rest of the application. The `base_service.py` is key, as it provides generic `get_by_id`, `get_all`, `create`, `update`, and `delete` methods, reducing boilerplate in the concrete services.
*   **`app/business_logic/`:** This layer defines the "rules" of the business.
    *   **`managers/`:** These classes orchestrate complex operations that may involve multiple services. For example, `SalesManager` uses `ProductService`, `InventoryService`, and `SalesService` to complete a single transaction.
    *   **`dto/`:** These Pydantic models are the data "contracts" that ensure type-safe and structured data is passed between the UI, managers, and services.
*   **`app/ui/`:** Contains everything the user sees and interacts with.
    *   **`main_window.py`:** The main application frame, containing the menu bar and the `QStackedWidget` that holds all other views. It implements lazy-loading for views to speed up application startup.
    *   **`views/`:** These are the large, primary widgets that correspond to the main features accessible from the menu (e.g., `POSView`, `InventoryView`).
    *   **`dialogs/`:** These are smaller, modal or non-modal windows that pop up to perform a specific, focused task, like adding a new customer or processing a payment.
*   **`migrations/`:** This directory is managed by Alembic. It contains the Python scripts that represent incremental changes to the database schema. This is essential for evolving the database structure in a controlled and versioned manner.

---

## **5. Deep Dive into Architectural Layers**

### 5.1. The Core Layer (`app/core`)

The `core` package is the architectural foundation upon which the entire application is built. It provides the essential services for dependency management, asynchronous execution, configuration, and error handling.

#### **`application_core.py` - The Dependency Injection Container**

The `ApplicationCore` class is the central hub of the application, implementing the Dependency Injection (DI) and Inversion of Control (IoC) principles. Its primary role is to create, manage, and provide access to all major components, such as business logic managers and data access services.

**Key Responsibilities & Features:**

*   **Lifecycle Management:** The `initialize()` and `shutdown()` methods manage the entire application's lifecycle. `initialize()` starts the async worker thread and establishes the database connection pool. `shutdown()` gracefully closes these resources, ensuring no connections are left dangling.
*   **Lazy Loading:** Services and managers are not instantiated when `ApplicationCore` is created. Instead, they are created on-demand the first time they are accessed via a property. This is implemented using a simple caching pattern (e.g., `if "product" not in self._services: ...`). This technique significantly improves application startup time, as only the essential components are loaded initially.
*   **Session Management:** The `get_session()` method provides a uniform, safe way to interact with the database. It's an `asynccontextmanager` that yields a SQLAlchemy `AsyncSession` from the session factory. It automatically handles `commit()` on success and `rollback()` on any exception within the `async with` block, ensuring that database transactions are always atomic. This is a cornerstone of the application's data integrity.
*   **Centralized Dependency Access:** Any component that holds a reference to the `core` object can access any service or manager (e.g., `self.core.product_manager`, `self.core.sales_service`). This decouples the components from each other; they only need to know about the core, not about every other component they might interact with.
*   **Context Provision:** It holds application-wide context, such as the `current_company_id`, `current_outlet_id`, and `current_user_id`. In the current implementation, these are loaded from settings, but in a production environment, they would be determined after user login and session validation.

#### **`async_bridge.py` - The Engine of Responsiveness**

This module is arguably the most critical piece of the architecture for ensuring a high-quality user experience. It solves the fundamental problem of integrating a synchronous GUI framework (Qt) with an asynchronous I/O model (`asyncio`).

**The Problem It Solves:**
If a database query were executed directly on the main GUI thread, the entire application would freeze until the query returned. For a query that takes 500ms, this is a noticeable and unacceptable stutter.

**The Solution Implemented:**

1.  **`AsyncWorkerThread` (`QThread`):** A dedicated `QThread` is started during application initialization. Its `run()` method does one thing: it creates and runs a new `asyncio` event loop `run_forever()`. This creates a separate, parallel universe for all backend operations.
2.  **`AsyncWorker` (`QObject`):** An instance of this class is created and "lives" inside the `AsyncWorkerThread`. It holds a reference to the thread's `asyncio` loop. It exposes two key methods:
    *   `run_task(coro, on_done_callback)`: This is the primary method used by the UI. It takes a coroutine (`coro`) and a callback function. It uses the thread-safe `loop.call_soon_threadsafe()` to schedule the coroutine for execution on the worker's event loop. This call is non-blocking.
    *   `run_task_and_wait(coro)`: Used for synchronous initialization tasks where the main thread *must* wait for a result before proceeding. It uses `asyncio.run_coroutine_threadsafe()` which returns a `Future`, and then blocks on `future.result()`.
3.  **Thread-Safe Communication (The `CallbackExecutor` Pattern):** This is the most elegant part of the implementation.
    *   The `AsyncWorker` has a Qt signal: `callback_ready = Signal(object, object, object)`.
    *   When a task finishes in the worker thread, the `_on_task_completed` method is called. Instead of directly invoking the Python `on_done_callback` (which would be unsafe across threads), it **emits the `callback_ready` signal**, passing the callback function itself and its results (`result`, `error`) as payload.
    *   In the `ApplicationCore`, a `CallbackExecutor` `QObject` was created and lives in the **main GUI thread**. This executor's `execute` slot is connected to the `AsyncWorker`'s `callback_ready` signal.
    *   When the signal is emitted from the worker thread, Qt's event loop automatically queues the invocation of the connected slot on the receiver's thread. Thus, `CallbackExecutor.execute()` runs safely on the main GUI thread.
    *   This slot then finally executes the original `on_done_callback` function, which can now safely manipulate UI elements.

#### **`result.py` - Explicit Error Handling**

This module implements a simple but powerful functional programming concept: the **Result monad**. Instead of using exceptions for predictable failures (e.g., "user not found," "invalid SKU"), methods return either a `Success(value)` object or a `Failure(error)` object.

**Benefits:**

*   **Explicitness:** The function signature makes it clear that the operation can fail (e.g., `-> Result[UserDTO, str]`). The calling code is forced to handle the failure case, preventing unhandled exceptions.
*   **Clean Control Flow:** It avoids littering the code with `try...except` blocks for business logic errors, which are better reserved for truly exceptional circumstances (e.g., database connection lost).
*   **Data Integrity:** It allows a chain of operations to be safely executed. If any step returns a `Failure`, the subsequent steps can be skipped, and the failure is propagated up the call stack.

### 5.2. The Persistence Layer (`app/models`)

This layer is the declarative foundation of the application's data. It uses SQLAlchemy's ORM to map Python classes to database tables.

**Key Features:**

*   **Centralized Schema (`sgpos`):** All tables are explicitly defined within the `sgpos` schema via the `MetaData` object in `base.py`. This is excellent practice for namespacing application tables and avoiding conflicts in a shared database.
*   **Base Model and Mixin:** The `base.py` file defines a common `Base` for all models and a `TimestampMixin` that automatically adds `created_at` and `updated_at` columns. The `onupdate=func.now()` is a standard and efficient way to handle update timestamps at the database level.
*   **Rich Relationships:** The models make extensive use of SQLAlchemy's `relationship()` to define the connections between entities (e.g., one-to-many, many-to-one). The use of `back_populates` ensures that these relationships are bidirectional and always in sync.
*   **Data Integrity:** The models correctly use database constraints to enforce data integrity at the lowest level:
    *   `ForeignKey` constraints with `ondelete` policies (`RESTRICT`, `CASCADE`).
    *   `UniqueConstraint` for business keys (e.g., a user's `username` must be unique within a `company_id`).
    *   `CheckConstraint` for enumerated types (e.g., `status` must be one of 'DRAFT', 'SENT', etc.).
*   **UUIDs as Primary Keys:** The use of `UUID` for all primary keys is a modern and robust choice. It prevents key clashes in distributed systems and obscures information compared to sequential integer IDs.

### 5.3. The Data Access Layer (`app/services`)

This layer acts as the "gatekeeper" to the database, implementing the Repository Pattern.

**Key Features:**

*   **`BaseService`:** This base class is a powerful abstraction. It provides generic implementations for common Create, Read, Update, Delete (CRUD) operations. This dramatically reduces boilerplate code in the concrete service classes. A service like `ProductService` can inherit these methods for free.
*   **Abstraction:** The Business Logic Layer does not need to know about SQLAlchemy sessions, engines, or query syntax. It simply calls high-level methods like `customer_service.create(customer_object)`. This makes the business logic cleaner and easier to test.
*   **Specific Queries:** Concrete services (`ProductService`, `SalesService`, etc.) are responsible for implementing more complex, domain-specific queries that don't fit the generic CRUD pattern. For example, `ReportService` contains highly specialized aggregation queries using SQLAlchemy Core for maximum performance.
*   **Transaction Propagation:** Crucially, methods that are part of a larger business transaction (like `SalesService.create_full_transaction`) are designed to accept an existing `AsyncSession` from the calling manager. This allows the manager to control the transaction boundary, ensuring that multiple service calls can be wrapped in a single, atomic operation.

### 5.4. The Business Logic Layer (`app/business_logic`)

This is where the application's intelligence resides.

**Key Features:**

*   **Orchestration via Managers:** Managers (`BaseManager` subclasses) are responsible for orchestrating workflows. The `SalesManager.finalize_sale` method is the prime example. It doesn't perform the database operations itself; it directs the various services (`InventoryService`, `SalesService`, etc.) to do the work in the correct order and within a single transaction.
*   **Enforcement of Business Rules:** This is the layer where business rules are validated. For instance, before creating a product, `ProductManager` explicitly calls `product_service.get_by_sku()` to ensure the SKU isn't already in use. This logic correctly lives here, not in the UI or the service layer.
*   **DTO Transformation:** The managers are responsible for the transformation between ORM models and DTOs.
    *   **Inbound:** They receive DTOs from the presentation layer (e.g., `ProductCreateDTO`).
    *   **Internal:** They convert these DTOs into ORM models to be passed to the service layer (`Product` model).
    *   **Outbound:** They receive ORM models back from the services and convert them into DTOs (`ProductDTO`) before returning them up the call stack. This ensures the UI layer remains completely decoupled from the database models.

### 5.5. The Presentation Layer (`app/ui`)

This layer is built to be as "dumb" as possible, focusing exclusively on presentation and user interaction.

**Key Features:**

*   **Model-View-Controller (MVC) Variant:** The architecture follows a pattern similar to MVC.
    *   **Model:** The `QAbstractTableModel` subclasses (e.g., `CartTableModel`, `CustomerTableModel`) act as the model. They hold the data for display.
    *   **View:** The Qt widgets (`QTableView`, `QLineEdit`, etc.) are the view.
    *   **Controller:** The view/dialog classes themselves (`POSView`, `CustomerDialog`) act as the controller, handling user input (via slots) and telling the `ApplicationCore` what to do.
*   **Lazy Loading of Views:** The `MainWindow` implements an efficient lazy-loading pattern. It only creates the `POSView` at startup. All other views (`ProductView`, `InventoryView`, etc.) are only instantiated from their class definitions the first time the user navigates to them. This makes the application launch faster.
*   **Decoupling with Table Models:** The use of `QAbstractTableModel` is a key strength. For example, `CustomerView` does not directly interact with its `QTableView`. Instead, it tells its `CustomerTableModel` to `refresh_data(new_customer_list)`. The model then notifies the table view to redraw itself. This decouples the data management from the display widget.
*   **Signal/Slot Mechanism:** The UI is driven by Qt's signal/slot mechanism. User actions (button clicks, text changes) emit signals, which are connected to slots (handler methods). This is a clean, event-driven approach that is a hallmark of Qt development. As described earlier, it's also the mechanism used for safe cross-thread communication.

---

## **6. Database Management**

The project employs a professional approach to managing its database schema.

*   **Alembic for Migrations:** The use of Alembic is the industry standard for managing SQLAlchemy schema migrations. The `migrations/versions/` directory contains a versioned history of every change made to the database. The `alembic upgrade head` command brings any developer's database to the latest version, and `alembic downgrade` can revert changes, providing a controlled, repeatable process for schema evolution. The `env.py` file is correctly configured to use a synchronous `psycopg2` driver for migrations while the main application uses the asynchronous `asyncpg` driver.
*   **`schema.sql` as Source of Truth:** The hand-written `scripts/database/schema.sql` file is an excellent addition. It serves as a clear, comprehensive, and database-agnostic definition of the entire schema, including indexes, comments, and check constraints. It's often easier to review a single SQL file to understand the full database structure than to piece it together from multiple ORM model files.

---

## **7. Conclusion**

The SG-POS System is architected with a level of rigor and foresight typically found in mature, large-scale enterprise applications. Its strict adherence to a layered design, coupled with a robust asynchronous execution model and clean dependency injection, provides a powerful and flexible foundation.

**Key Strengths:**

*   **Maintainability:** The strict separation of concerns means a change in one layer (e.g., optimizing a database query in a service) has minimal or no impact on other layers.
*   **Testability:** Each layer can be tested in isolation. Managers can be tested by mocking service-layer responses, and services can be tested against a real test database without needing the UI.
*   **Responsiveness:** The async architecture guarantees a fluid user experience, which is paramount for the application's target use case.
*   **Scalability:** The architecture is well-suited for future growth. New features can be added by creating new managers, services, and views without disrupting existing ones. The multi-tenant design (`company_id`) hints at a potential for a future SaaS offering.

While the current codebase has some incomplete features and minor bugs, these are implementation-level details. The architectural blueprint itself is sound, professional, and poised to support the project's ambitious goals.

---
https://drive.google.com/file/d/1dnSP22Pzt3sjhTNHJcPpvKoihYG-somP/view?usp=sharing, https://aistudio.google.com/app/prompts?state=%7B%22ids%22:%5B%221fo0QcoydHcYD6h_b6-9HapceFSj7xnKT%22%5D,%22action%22:%22open%22,%22userId%22:%22108686197475781557359%22,%22resourceKeys%22:%7B%7D%7D&usp=sharing, https://drive.google.com/file/d/1koyl7FAKLkppdi5iIUCwrJtbPLgb6YGM/view?usp=sharing

