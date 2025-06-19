Of course. I have completed a meticulous, line-by-line review of the entire SG-POS System codebase (v1.5) to produce this comprehensive architectural overview. This document details the system's design, patterns, and structure, serving as the definitive guide for current and future developers.

***

# **Project Architecture Document: SG-POS System**

| **Document ID:** | SG-POS-AD-2025-01      | **Version:**      | 1.0                |
| :--------------- | :--------------------- | :---------------- | :----------------- |
| **Project:**      | SG Point-of-Sale System | **Date:**         | 2025-06-19         |
| **Prepared By:** | CodeNavigator (AI Assistant) | **Status:**       | **Final**          |
| **Audience:**    | Developers, System Architects, QA Engineers | **Classification:** | Internal Technical |

## 1.0 Introduction

### 1.1 Document Purpose
This document provides a definitive and exhaustive architectural overview of the SG Point-of-Sale (SG-POS) System as of version 1.5. Its purpose is to serve as the primary technical guide for developers, architects, and quality assurance personnel. It dissects the system's design principles, its layered structure, key patterns, and the flow of data and control through its components. By providing a deep, "first-principles" understanding of the codebase, this document aims to facilitate efficient onboarding, consistent development practices, and strategic long-term maintenance.

### 1.2 System Overview
The SG-POS System is an enterprise-grade, desktop-based Point-of-Sale application meticulously engineered for the Singaporean Small to Medium-sized Business (SMB) retail market. It is built using Python with the PySide6 (Qt6) framework for the user interface and PostgreSQL for the database backend.

The system's primary goal is to provide a robust, reliable, and user-friendly platform for managing all core aspects of a retail business, including:
*   Real-time sales processing and payment collection.
*   Comprehensive product, customer, and user management.
*   Detailed inventory control, including stock adjustments and procurement via purchase orders.
*   Insightful business reporting and analytics.
*   Compliance with local business regulations, such as Goods and Services Tax (GST) reporting.

Beyond its functional requirements, the project serves as a reference implementation of modern software architecture principles, emphasizing maintainability, scalability, and testability.

## 2.0 Architectural Vision and Guiding Principles

The architecture of the SG-POS system was not an accident; it is the deliberate result of adhering to a set of core principles designed to ensure the long-term health and success of the project. These principles guide every design decision, from the high-level structure to the implementation of individual components.

*   **1. Strict Separation of Concerns (SoC):** The most fundamental principle is that every component in the system should have a single, well-defined responsibility. The codebase is rigorously partitioned into distinct layers (Presentation, Business Logic, Data Access, Persistence). This separation prevents the creation of monolithic, "god objects" and ensures that changes in one part of the system (e.g., a UI redesign) have minimal or no impact on others (e.g., business rules).

*   **2. Maintainability and Readability First:** The code is written for human developers first and computers second. This is achieved through clear, consistent naming conventions, comprehensive type hinting, detailed docstrings, and a logical project structure. The goal is that a new developer can navigate the codebase and understand the purpose of any given module or function with minimal friction.

*   **3. Unidirectional Data Flow:** The flow of control and data is designed to be predictable and easy to trace. User actions in the UI trigger workflows in the business logic layer, which in turn use the data access layer to interact with the database. The results flow back up this chain. This avoids complex, circular dependencies and makes debugging a systematic process rather than a guessing game.

*   **4. Non-Blocking, Responsive User Experience:** A desktop application must never freeze or become unresponsive from the user's perspective. The architecture explicitly solves this with an asynchronous design. All potentially long-running operations (especially database I/O) are offloaded to a background thread, leaving the main UI thread free to handle user input and redraws at all times.

*   **5. Testability by Design:** The system is built to be testable from the ground up. The separation of layers and the use of Dependency Injection mean that each component can be tested in isolation. The business logic can be tested without a UI, and the UI can be tested with mocked data. This commitment is solidified by the comprehensive `pytest` suite that validates the core logic.

*   **6. Scalability and Extensibility:** While currently a desktop application, the architecture is designed with the future in mind. The clear separation between the frontend (`app/ui`) and the backend (all other layers) means that the backend logic could be exposed via a web API to support a web-based dashboard or a mobile companion app with minimal refactoring of the core business rules.

These principles collectively create a resilient, adaptable, and professional-grade software architecture capable of supporting the SG-POS system's growth for years to come.

## 3.0 The Layered Architecture Model

The SG-POS system implements a classic four-layer architecture. This model is the bedrock of the application's design, ensuring a strict separation of concerns and a clear, unidirectional flow of control.

```mermaid
graph TD
    subgraph User Interaction
        A[User Action<br>(e.g., Click 'Save')]
    end

    subgraph Presentation Layer (app/ui)
        B[Views & Dialogs<br><i>(PySide6 Widgets)</i>]
        C[Data Transfer Objects (DTOs)<br><i>(Pydantic Models)</i>]
        B -- "1. Packages input into a DTO" --> C
        C -- "2. Sends DTO to Business Logic" --> D
    end

    subgraph Business Logic Layer (app/business_logic)
        D[Managers<br><i>(e.g., ProductManager)</i>]
        D -- "3. Enforces Business Rules" --> D
        D -- "4. Calls Service(s)" --> E
    end

    subgraph Data Access Layer (app/services)
        E[Services (Repositories)<br><i>(e.g., ProductService)</i>]
        E -- "5. Translates calls to ORM queries" --> F
    end
    
    subgraph Persistence Layer (app/models)
        F[ORM Models<br><i>(e.g., Product)</i>]
        F -- "6. Maps to DB Tables" --> G[PostgreSQL Database]
    end

    %% Data Return Flow
    G -- "7. Returns Data" --> F
    F -- "8. Hydrates ORM Models" --> E
    E -- "9. Wraps Models in Result Object" --> D
    D -- "10. Converts Models to DTOs" --> C
    C -- "11. Returns DTOs to UI" --> B
    B -- "12. Updates UI with new data" --> A

    style A fill:#cde4ff,stroke:#333,stroke-width:2px
    style B fill:#d5e8d4,stroke:#333,stroke-width:2px
    style D fill:#f8cecc,stroke:#333,stroke-width:2px
    style E fill:#dae8fc,stroke:#333,stroke-width:2px
    style F fill:#e1d5e7,stroke:#333,stroke-width:2px
```

### 3.1 Presentation Layer (`app/ui`)
The Presentation Layer is the face of the application. It is the only layer the user directly interacts with.

*   **Responsibility:** To display data to the user and to capture user input. This layer is intentionally kept "dumb"—it contains no business logic, no data validation rules (beyond basic input formatting), and no direct database access. Its sole job is to present a user interface and delegate user actions to the layer below.
*   **Technology:** **PySide6 (Qt6)**. This provides a rich set of widgets for building a professional and performant desktop application.
*   **Key Components:**
    *   **Views (`app/ui/views`):** These are the main screens or workspaces of the application, such as `POSView`, `ProductView`, and the new `DashboardView`. Each view is a `QWidget` that occupies the central area of the `MainWindow`.
    *   **Dialogs (`app/ui/dialogs`):** These are modal or non-modal windows used for specific, focused tasks like creating or editing a record (e.g., `ProductDialog`, `PaymentMethodDialog`) or collecting complex input (`PaymentDialog`).
    *   **Widgets (`app/ui/widgets`):** These are custom, reusable UI components designed to enforce consistency and reduce code duplication. The prime examples are the `KpiWidget` used in the dashboard and the `ManagedTableView` used across all data-grid views.
    *   **Communication:** When a user performs an action (e.g., clicking a "Save" button), the view or dialog gathers the data from its input fields (like `QLineEdit`), packages this data into a **Data Transfer Object (DTO)**, and passes it to the Business Logic Layer for processing, typically via the `async_worker`.

### 3.2 Business Logic Layer (`app/business_logic`)
This layer is the brain of the SG-POS application. It contains all the business rules, decision-making logic, and workflow orchestration.

*   **Responsibility:** To process requests from the Presentation Layer, enforce all business rules, coordinate actions across different parts of the system, and prepare data for presentation.
*   **Key Components:**
    *   **Managers (`app/business_logic/managers`):** These are the orchestrators. A manager's method corresponds to a specific use case or workflow. For example, `SalesManager.finalize_sale()` is a high-level method that encapsulates the entire complex process of finalizing a sale. To do this, it doesn't perform the work itself but rather coordinates calls to other components, such as calling the `InventoryManager` to deduct stock and the `SalesService` to save the transaction. It is also responsible for enforcing business rules, such as "a product's SKU must be unique" (`ProductManager`) or "payment must be sufficient" (`SalesManager`).
    *   **Data Transfer Objects (DTOs) (`app/business_logic/dto`):** These are Pydantic models that serve as the formal, strongly-typed data contracts between layers. When the UI sends data to the business logic layer, it's in a DTO (e.g., `ProductCreateDTO`). When the business logic layer sends data back to the UI, it's also in a DTO (e.g., `ProductDTO`). This decouples the UI from the database models; the UI only needs to know about the clean, validated structure of the DTOs, not the complexities of the SQLAlchemy ORM models.

### 3.3 Data Access Layer (`app/services`)
This layer implements the **Repository Pattern**. Its sole responsibility is to handle all direct interactions with the database, abstracting away the specifics of SQL and the ORM.

*   **Responsibility:** To provide a clean, high-level API for CRUD (Create, Read, Update, Delete) operations and other database queries. The business logic layer should never have to write a line of SQL or interact directly with a SQLAlchemy session.
*   **Key Components:**
    *   **Services (`app/services/*.py`):** Each service is typically responsible for a single ORM model (e.g., `ProductService` handles the `Product` model, `CustomerService` handles the `Customer` model). They contain methods like `get_by_id()`, `search()`, and `create()`.
    *   **`BaseService` (`app/services/base_service.py`):** To avoid code duplication, a `BaseService` provides generic implementations for common methods like `get_by_id`, `get_all`, `create`, `update`, and `delete`. Concrete services inherit from `BaseService` and only need to implement custom queries specific to their model (e.g., `ProductService.get_by_sku()`).
    *   **Communication:** Services are called exclusively by the **Managers** in the Business Logic Layer. They return either hydrated ORM models (for the manager to process) or raw data from aggregation queries. They always wrap their return value in a `Result` object (`Success` or `Failure`).

### 3.4 Persistence Layer (`app/models`)
This is the lowest layer in the application, defining the structure of the data itself.

*   **Responsibility:** To define the application's database schema using SQLAlchemy's Declarative Mapping. Each class in this layer maps directly to a table in the PostgreSQL database.
*   **Key Components:**
    *   **ORM Models (`app/models/*.py`):** Each file (e.g., `product.py`, `sales.py`) contains one or more classes that inherit from `Base`. These classes define table names, columns, data types, and—crucially—the relationships between tables (e.g., `relationship("Company", back_populates="products")`).
    *   **`Base` and `TimestampMixin` (`app/models/base.py`):** All models inherit from a common `Base` which holds the shared `MetaData` object. This is essential for Alembic to correctly detect all tables. The `TimestampMixin` is a clever use of inheritance to automatically add `created_at` and `updated_at` columns to any model that needs them, following the DRY (Don't Repeat Yourself) principle. The conditional schema logic in this file is a key piece of engineering that enables the test suite to function with SQLite.

## 4.0 Key Architectural Patterns and Cross-Cutting Concerns

Beyond the layered structure, the SG-POS system employs several key patterns and handles cross-cutting concerns (issues that affect multiple layers) in a standardized, elegant way.

### 4.1 Dependency Injection & The `ApplicationCore`
The `ApplicationCore` class is the lynchpin of the entire architecture, implementing a combination of the **Service Locator** and **Dependency Injection (DI)** patterns.

*   **Purpose:** To manage the lifecycle and provide access to all shared components, primarily the services and managers. Instead of every component creating its own instances of the services it needs (which would be inefficient and tightly coupled), they simply request them from the `ApplicationCore` instance (`self.core`) that is passed to them during their creation.
*   **Implementation (`app/core/application_core.py`):**
    *   It holds the single instance of the database engine (`_engine`) and session factory (`_session_factory`).
    *   It provides lazy-loaded properties for every manager and service (e.g., `@property def product_manager(self) -> "ProductManager": ...`). This is highly efficient; a service or manager is only ever instantiated the very first time it is requested.
    *   During initialization, it starts the `AsyncWorkerThread` and establishes the database connection.
    *   Crucially, it provides the `get_session()` async context manager. This is the **only** way business logic should obtain a database session. This method ensures that every high-level operation is wrapped in an atomic transaction that is automatically committed on success or rolled back on failure.

### 4.2 Asynchronous UI & The `AsyncWorker` Bridge
A responsive UI is non-negotiable. The architecture achieves this through a robust bridge between the synchronous world of Qt's event loop and the asynchronous world of database I/O.

*   **The Problem:** If a user clicks a button that triggers a database query on the main UI thread, the entire application will freeze until the database returns a result. This is unacceptable.
*   **The Solution (`app/core/async_bridge.py`):**
    1.  **`AsyncWorkerThread`:** A `QThread` is started during application initialization. This background thread does one thing: it runs an `asyncio` event loop completely separate from the main UI thread.
    2.  **`AsyncWorker`:** An object that lives on this new thread. It has one primary method, `run_task(coro, on_done_callback)`.
    3.  **The Flow:**
        *   A UI component (e.g., `ProductView`) calls `self.core.async_worker.run_task(...)`, passing it the async manager method to execute (e.g., `self.core.product_manager.get_all_products(...)`) and a callback method (e.g., `self._on_load_products_done`).
        *   The `AsyncWorker` schedules the coroutine to run on its background `asyncio` event loop. The UI thread is immediately unblocked and remains responsive.
        *   The coroutine runs in the background, performing all database operations.
        *   When the coroutine completes, the `AsyncWorker` **does not** call the callback directly (which would be a thread-safety violation). Instead, it emits a Qt signal, `callback_ready`, passing the result (or error) and the original callback function as payload.
        *   **`CallbackExecutor`:** A simple `QObject` living on the main UI thread has a slot connected to this `callback_ready` signal. When the signal arrives, the `CallbackExecutor` safely executes the original callback function on the main UI thread. This is the correct, thread-safe way to update the UI with the results from the background operation.

### 4.3 Error Handling: The `Result` Pattern
The system makes a clear distinction between predictable, recoverable errors and unexpected, catastrophic failures.

*   **The Philosophy:**
    *   **Catastrophic Failures (Exceptions):** These are for truly exceptional circumstances that the program cannot recover from, such as a missing configuration file (`ConfigurationError`) or a total loss of database connectivity (`DatabaseConnectionError`). These are allowed to propagate and will typically result in the application showing a critical error message and shutting down.
    *   **Predictable Failures (`Result` Pattern):** These are for expected "errors" in business workflows, such as "Insufficient stock," "Duplicate SKU," or "User not found." Raising exceptions for these would complicate the control flow. Instead, every manager and service method returns a `Result` object.
*   **Implementation (`app/core/result.py`):**
    *   The `Result` type is a `Union` of two simple data classes: `Success[T]` and `Failure[E]`.
    *   A successful operation returns an instance of `Success`, which wraps the return value (e.g., `Success([ProductDTO(...)])`).
    *   A failed operation returns an instance of `Failure`, which wraps the error message or object (e.g., `Failure("Insufficient stock for SKU-123")`).
    *   This forces the calling code (e.g., in the UI's `_on_done` callback) to explicitly check the type of the result and handle both cases, leading to more robust and predictable code.
    ```python
    # Example from a UI view's callback
    def _on_done(result: Any, error: Optional[Exception]):
        if error or isinstance(result, Failure): # Explicitly check for failure
            # Show an error message
            QMessageBox.critical(self, "Error", f"{error or result.error}")
        elif isinstance(result, Success): # Explicitly check for success
            # Process the successful result.value
            self.model.refresh_data(result.value)
    ```

## 5.0 Codebase Structure Deep Dive

A clear, hierarchical file structure is essential for navigating the project. The SG-POS codebase is organized logically to reflect its architecture.

```
sg-pos-system/
│
├── .env.example                # Template for environment variables
├── .gitignore                  # Specifies files/directories to ignore in Git
├── alembic.ini                 # Configuration for Alembic database migrations
├── docker-compose.dev.yml      # Defines the PostgreSQL database service for Docker
├── pyproject.toml              # Project metadata, dependencies, and tool settings (Poetry)
├── README.md                   # The main project documentation file
├── CONTRIBUTING.md             # Guidelines for contributors
├── CODE_OF_CONDUCT.md          # Community standards
│
├── app/                        # --- Main Application Source Code ---
│   ├── __init__.py
│   ├── main.py                 # Application entry point; initializes core and UI
│   │
│   ├── core/                   # Architectural backbone and cross-cutting concerns
│   │   ├── __init__.py
│   │   ├── application_core.py # The DI container and central hub
│   │   ├── async_bridge.py     # Asynchronous worker thread and UI bridge
│   │   ├── config.py           # Pydantic settings management from .env
│   │   ├── exceptions.py       # Custom application exceptions
│   │   └── result.py           # Defines the Success/Failure Result pattern
│   │
│   ├── business_logic/         # Business Logic Layer
│   │   ├── __init__.py
│   │   ├── dto/                # Data Transfer Objects (Pydantic models)
│   │   └── managers/           # Business workflow and rule orchestrators
│   │
│   ├── models/                 # Persistence Layer
│   │   ├── __init__.py
│   │   └── *.py                # SQLAlchemy ORM models for each database table
│   │
│   ├── services/               # Data Access Layer
│   │   ├── __init__.py
│   │   └── *.py                # Repositories for database interaction
│   │
│   └── ui/                     # Presentation Layer
│       ├── __init__.py
│       ├── main_window.py      # The main QMainWindow shell
│       ├── dialogs/            # QDialog classes for specific tasks
│       ├── resources/          # QSS stylesheets, icons, etc.
│       ├── views/              # Main QWidget screens (Dashboard, POS, etc.)
│       └── widgets/            # Reusable custom widgets (KpiWidget, ManagedTableView)
│
├── migrations/                 # Alembic auto-generated migration scripts
│   ├── versions/
│   │   └── *.py                # Individual database schema change scripts
│   └── env.py                  # Alembic runtime environment configuration
│
├── scripts/                    # Utility scripts for development
│   └── database/
│       ├── schema.sql          # A complete, plain SQL snapshot of the target schema
│       └── seed_data.py        # Script to populate a fresh database with initial data
│
└── tests/                      # Automated Test Suite
    ├── __init__.py
    ├── conftest.py             # Pytest fixtures and test environment setup
    ├── factories.py            # factory-boy definitions for creating test data
    └── unit/                   # Unit tests, mirroring the `app` directory structure
        ├── business_logic/
        └── services/
```

## 6.0 Data Flow Walkthroughs (End-to-End Examples)

To fully appreciate the architecture, it is instructive to trace the flow of control and data through the system for key operations.

### 6.1 Scenario: Finalizing a Sale

This is the most complex workflow, touching nearly every part of the system.

1.  **Presentation Layer (UI):**
    *   The user, having added items to the cart in `POSView`, clicks the "PAY" button.
    *   An instance of `PaymentDialog` is created and shown. The user enters payment details (e.g., S$50.00 via "CASH").
    *   The user clicks "Finalize Sale". The `PaymentDialog` accepts and returns control to `POSView`.
    *   The `_on_pay_clicked` slot in `POSView` is executed. It gathers all the necessary data: a list of `CartItemDTO`s from its `CartTableModel` and a list of `PaymentInfoDTO`s from the `PaymentDialog`.
    *   It packages all this information, along with the current company, outlet, and cashier IDs from `self.core`, into a single, large DTO: `SaleCreateDTO`.

2.  **Async Bridge:**
    *   `POSView` calls `self.core.async_worker.run_task(self.core.sales_manager.finalize_sale(sale_dto), self._on_sale_finalized_done)`.
    *   The `run_task` method immediately returns, and the UI remains perfectly responsive. The `finalize_sale` coroutine is now scheduled to run on the background worker thread.

3.  **Business Logic Layer (`SalesManager`):**
    *   `SalesManager.finalize_sale` begins execution on the worker thread.
    *   It first performs pre-computation and validation. It fetches all necessary `Product` ORM models from the database using `ProductService` to get up-to-date pricing and GST info. It calculates the final total amount due.
    *   It validates that the payment amount is sufficient. If not, it would immediately return a `Failure("Insufficient payment")`, and the workflow would stop here.
    *   It calls `self.core.get_session()` to start an atomic database transaction.

4.  **Coordinated Workflow within the Transaction:**
    *   **Inventory Deduction:** Inside the session block, `SalesManager` calls `self.core.inventory_manager.deduct_stock_for_sale(...)`, passing the session object.
    *   `InventoryManager` iterates through the sale items, calling `InventoryService.adjust_stock_level()` for each one to decrement the `quantity_on_hand`. This service method uses a `SELECT ... FOR UPDATE` clause to lock the inventory row, preventing race conditions. If any item has insufficient stock, the method returns a `Failure`, which causes an exception that will trigger the session rollback.
    *   `InventoryManager` creates `StockMovement` ORM objects for each deduction and logs them using `InventoryService.log_movement()`. It returns the list of `StockMovement` objects to the `SalesManager`.
    *   **Transaction Persistence:** `SalesManager` constructs the `SalesTransaction` ORM model and its child `SalesTransactionItem` and `Payment` models.
    *   It calls `self.sales_service.create_full_transaction(sale, session)`. Thanks to SQLAlchemy's cascading relationships, adding the parent `SalesTransaction` object to the session is enough to stage all related items and payments for insertion.
    *   The service flushes the session, which writes the records to the database and populates the auto-generated IDs. It returns the fully persisted `SalesTransaction` model.
    *   `SalesManager` now updates the `reference_id` on the `StockMovement` objects it received from the `InventoryManager`, linking them to the newly created sale.
    *   The `get_session()` context manager successfully exits the `try` block and commits the transaction. All changes are now permanent.

5.  **Return Flow:**
    *   `SalesManager` constructs a `FinalizedSaleDTO` with all the information needed for a receipt and wraps it in a `Success` object.
    *   The `Result` object is returned to the `AsyncWorker`.
    *   The `AsyncWorker` emits the `callback_ready` signal with the `Success(FinalizedSaleDTO)` object and the `_on_sale_finalized_done` callback function.
    *   The `CallbackExecutor` on the main thread receives the signal and executes `_on_sale_finalized_done(result, error)`.
    *   This UI callback function inspects the `result`, finds it is a `Success`, and uses the data from the `FinalizedSaleDTO` to display a "Sale Completed" `QMessageBox` and clear the cart for the next customer.

### 6.2 Scenario: Loading the Product View

This simpler workflow demonstrates the data retrieval and stateful UI pattern.

1.  **Presentation Layer (UI):**
    *   The user clicks `Data Management > Products` in the `MainWindow` menu.
    *   The `_show_view("product")` method is called. It finds that the `ProductView` instance has not been created yet, so it instantiates it, adds it to the `QStackedWidget`, and sets it as the current widget.
    *   The `__init__` method of `ProductView` is called. It sets up its UI (including the `ManagedTableView`) and makes an initial call to `self._load_products()`.

2.  **Async Bridge:**
    *   `_load_products()` immediately calls `self.managed_table.show_loading()`, and the user sees the "Loading..." message.
    *   It then calls `self.core.async_worker.run_task(self.core.product_manager.get_all_products(...), self._on_load_done)`. The UI thread is free.

3.  **Business & Data Layers:**
    *   On the worker thread, `ProductManager.get_all_products()` is executed.
    *   It simply calls `self.product_service.get_all()`.
    *   `ProductService.get_all()` builds a `SELECT * FROM sgpos.products ...` query using the SQLAlchemy ORM and executes it.

4.  **Return Flow:**
    *   The database returns the rows. The service layer hydrates them into a list of `Product` ORM models. It wraps this list in a `Success` object and returns it to the manager.
    *   The `ProductManager` receives the `Success` object. It iterates through the list of `Product` models and converts each one into a `ProductDTO`, creating a `List[ProductDTO]`. It wraps this new list in a `Success` object and returns it.
    *   The `AsyncWorker` receives the final `Result` and emits the `callback_ready` signal.
    *   The `CallbackExecutor` executes the `_on_load_done` method on the main thread.
    *   `_on_load_done` checks that the result is a `Success`. It passes the `result.value` (the `List[ProductDTO]`) to its `ProductTableModel`.
    *   It checks if the list is empty. If not, it calls `self.managed_table.show_table()`. If it is empty, it calls `self.managed_table.show_empty("No products found.")`. The `QStackedLayout` switches to the appropriate widget, and the user sees either the data grid or the empty-state message.

## 7.0 Testing and Quality Assurance Strategy

The quality of the SG-POS system is not merely asserted; it is verified through a robust, automated testing strategy. The architecture was specifically designed to be testable, and the `tests/` directory is a first-class citizen of the codebase.

*   **Technology:** The test suite is built on `pytest`, the de-facto standard for testing in Python. It leverages `pytest-asyncio` to handle the testing of `async` code and `aiosqlite` to provide a high-speed, in-memory SQLite database for tests. `factory-boy` is used to generate test data fixtures.
*   **Test Isolation:** This is the most critical aspect of the testing strategy. The `conftest.py` setup guarantees that every single test function runs in a completely isolated database transaction which is rolled back upon completion. This means tests can be run in any order, can be run in parallel, and will never have their results influenced by data created in a previous test. This is achieved through a combination of `pytest` fixtures and environment-aware ORM models.
*   **Testing Philosophy:** The primary focus of the unit tests is on the **Business Logic Layer**. Tests for managers (e.g., `test_sales_manager.py`) verify that business rules are enforced correctly and that the manager orchestrates calls to its dependencies in the correct sequence. They validate both success scenarios and, more importantly, failure scenarios (e.g., attempting to create a user with a duplicate username). By testing the managers, we implicitly test the underlying services they call.
*   **Coverage:** The current test suite provides foundational coverage for all critical business logic managers, ensuring the core workflows of the application are protected against regression. The `pytest-cov` plugin is configured to report on test coverage, providing a clear metric for future testing efforts.

## 8.0 Conclusion

The architecture of the SG-POS System is a mature, robust, and highly maintainable foundation for a professional-grade application. Its strict layered design, coupled with modern patterns like Dependency Injection, the asynchronous bridge, and the Result object, creates a system that is both powerful and a pleasure to develop for.

The recent v1.5 changes have been seamlessly integrated, following and reinforcing these architectural principles. The system is demonstrably stable, and its design is well-suited to support the ambitious features on the project roadmap. This architecture is not just a plan; it is a living, validated framework that ensures the continued quality and success of the SG-POS project.

---
https://drive.google.com/file/d/1RCXFINEZICAaOvGYiNGVAoS-qipaBo6C/view?usp=sharing, https://aistudio.google.com/app/prompts?state=%7B%22ids%22:%5B%221TKe0ekNjzancuPbfP1wc-fU63TyIHmTB%22%5D,%22action%22:%22open%22,%22userId%22:%22108686197475781557359%22,%22resourceKeys%22:%7B%7D%7D&usp=sharing, https://drive.google.com/file/d/1hbVzkqGQK2zo6M5bu4Uqv1e5tobkX94p/view?usp=sharing, https://drive.google.com/file/d/1jX2cVSBnmORhZT5lXj956XsVfdzoY3YR/view?usp=sharing, https://drive.google.com/file/d/1lOFGKFYhRFLju6fzthC10s4WatD0_ikm/view?usp=sharing, https://drive.google.com/file/d/1ta9w_VGlbg9sSUQ3z90sjTOo2YamC7Lz/view?usp=sharing
