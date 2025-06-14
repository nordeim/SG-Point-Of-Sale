You are a deep-thinking AI agent recognized for and exemplary in modern UI design and production quality code generation. You may use an extremely long chain of thoughts to deeply consider the problem and deliberate with yourself via systematic reasoning processes to help come to a correct or most optimal solution before answering. You will carefully explore various options before choosing the best option for producing your final answer. You will thoroughly explore various implementation options before choosing the most optimal option or approach to implement a given request. To produce error-free results or code output, you will come up with a detailed execution plan based on your chosen best option or most optimal solution, then cautiously execute according to the plan to complete your given task. You will double-check and validate any code changes before implementing. You should enclose your thoughts and internal monologue inside <think> </think> tags, and then provide your solution or response to the problem. This is a meta-instruction about how you should operate for subsequent prompts.

**Your Goal:**
Produce a detailed `Product Requirements Document` in markdown format. The application "SG Point-of-Sale (POS) system" is a comprehensive, cross-platform desktop application designed to meet the typical retail needs of small to medium-sized businesses (SMBs) in Singapore. Built with Python and leveraging the power of PySide6 for a modern user interface and PostgreSQL for robust data management, it offers professional-grade retail tool tailored to Singapore's regulatory environment. The application should be architected from the ground up to handle real-world business complexity. Use at least 6000 words for a detailed PRD that includes a database schema design, codebase file hierarchy diagram, application modules and user interation diagram, listing and description of key application modules and files. The PRD should also include a comprehensive description of technology stack to be used and a section on the setup of such environment separately for development and production environments. The PRD should exhibit a well-thought-out design and plan that leaves no ambiguity for the building of the actual codebase.

The codebase should exhibit a high degree of quality, characterized by a clean, layered architecture, a robust asynchronous processing model, strong data integrity mechanisms, and consistent adherence to best practices like Dependency Injection, Data Transfer Objects (DTOs), and the Result pattern. Implemented features, including multi-currency support, are well-integrated and architecturally sound. The project should provide a solid, scalable foundation for future development.

## Architectural Consideration

### 1. Layered Architecture & Separation of Concerns

The project's file structure and class implementations strictly adhere to well documented layered architecture.
*   **Presentation Layer (`app/ui`)**: Contains only UI-related code (PySide6 widgets, dialogs, models). It correctly delegates all business logic and data requests to the Business Logic Layer via the `ApplicationCore`.
*   **Business Logic Layer (`app/business_logic/`, `app/accounting/` managers)**: This layer is clean and well-defined. The "Manager" classes successfully orchestrate complex business workflows (e.g., `PaymentManager._build_payment_je`) by coordinating multiple services without containing any direct database or UI code. This validates the separation of concerns.
*   **Data Access Layer (`app/services/`)**: The "Service" classes effectively implement the Repository pattern. They are the sole point of interaction with the SQLAlchemy ORM, abstracting all query logic away from the business layer.
*   **Persistence Layer (`app/models/`, `scripts/`)**: The SQLAlchemy ORM models accurately represent the database schema, and the database itself (defined in `schema.sql`) enforces data integrity through constraints and triggers, as documented.

#### 2. Dependency Management & `ApplicationCore` Refactoring

The most significant recent change was the refactoring of the dependency injection mechanism. 

*   **Lazy Initialization**: The `ApplicationCore` class has been successfully transformed. The monolithic `startup` block is gone, replaced by elegant `@property` methods for every manager. This correctly implements on-demand, lazy initialization.
*   **Unified Constructor Signature**: Every single manager class (e.g., `CustomerManager`, `PaymentManager`, `GSTManager`) now correctly implements a simplified `__init__(self, app_core: "ApplicationCore")` constructor. They source all their dependencies from the `app_core` instance. This change has been applied consistently across the entire codebase.
*   **Decoupling Achieved**: The primary goal of the refactoring—decoupling the `ApplicationCore` from the managers' specific dependencies—has been fully achieved. The system is now significantly more modular and easier to maintain.

### 3. Asynchronous Model

The application's asynchronous architecture is sound and correctly implemented.
*   The `app/main.py` script correctly establishes a separate thread for the `asyncio` event loop, preventing any I/O operations from blocking the main GUI thread.
*   The `schedule_task_from_qt` bridge function is used consistently throughout the UI layer (e.g., in `ReportsWidget`, `ChartOfAccountsWidget`) to safely trigger background tasks.
*   UI updates from background tasks are correctly marshaled back to the main thread using `QMetaObject.invokeMethod`, ensuring thread safety. The successful startup log confirms this entire mechanism is functioning as designed.
