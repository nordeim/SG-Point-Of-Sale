# **Architecture Design Document: The SG-POS Blueprint**

| **Document ID:** | ARCH-DESIGN-GUIDE-2025-02 |
| :-------------- | :------------------------ |
| **Version:**    | 2.0 (Enhanced)            |
| **Date:**       | 2025-06-21                |
| **Audience:**   | Technical Leads, Architects, Developers |
| **Purpose:**    | To define and promote a set of architecture principles, patterns, and best practices for building maintainable, enterprise-grade applications. This document is based on the proven, hardened design of the SG-POS System and is intended as a standard for future projects to prevent common but critical architectural pitfalls. |

---

## **1. Introduction**

This document articulates the architectural principles, design patterns, and best practices that have been validated and hardened throughout the development of the SG Point-of-Sale (SG-POS) System. The goal is to serve as a comprehensive, reusable blueprint for future projects seeking to achieve high maintainability, scalability, reliability, and testability.

Modern applications, especially those combining synchronous user interfaces with asynchronous backends, are susceptible to a class of subtle, hard-to-debug runtime errors related to state management, threading, and data consistency. The architecture described herein is specifically designed to mitigate these risks by enforcing strict patterns of data flow and state management.

Adhering to these guidelines is not merely a suggestion; it is a strategy for building robust, enterprise-grade applications with predictable quality and long-term sustainability. This document codifies not just the successful design choices but also the critical lessons learned from overcoming complex bugs, ensuring future projects can benefit from this hard-won experience.

---

## **2. Core Architectural Principles**

The foundation of the SG-POS Blueprint rests on six inviolable principles.

### **2.1. Strict Separation of Concerns (SoC) & The Layered Model**

**Definition:**  
Every component in the codebase must have a single, well-defined responsibility. To enforce this, the application is divided into four distinct horizontal layers. Communication between layers is strictly controlled, flowing in a single direction. This is the most important principle for managing complexity.

**The Four Layers:**

1.  **L1: Presentation Layer (`app/ui`)**
    *   **Responsibility:** To render the user interface and capture user interaction. It is the "face" of the application.
    *   **Composition:** Contains views (main screens), dialogs (modal windows), and reusable widgets. Built with a robust framework like PySide6.
    *   **Proscription:** This layer contains **zero** business logic. It does not know how to calculate tax, validate inventory, or even what a "unique SKU" means. Its sole job is to collect data (e.g., from a form) and delegate the action to the Business Logic Layer, typically by constructing a Data Transfer Object (DTO).

2.  **L2: Business Logic Layer (`app/business_logic`)**
    *   **Responsibility:** To be the "brain" of the application. It orchestrates business processes, enforces rules, and makes decisions.
    *   **Composition:** Contains **Managers** (e.g., `SalesManager`), which orchestrate workflows, and **Data Transfer Objects** (DTOs), which serve as validated data contracts.
    *   **Proscription:** This layer does not interact directly with the database or ORM. It delegates all persistence and query operations to the Data Access Layer. It is the only layer that can coordinate actions across multiple business domains (e.g., a `SalesManager` can invoke both the `InventoryManager` and `CustomerManager`).

3.  **L3: Data Access Layer (`app/services`)**
    *   **Responsibility:** To abstract all data persistence mechanisms. It implements the **Repository Pattern**.
    *   **Composition:** Contains **Services** (e.g., `ProductService`), where each service corresponds to a single database entity or aggregate root.
    *   **Proscription:** This layer contains **zero** business logic. A service method should not know *why* it's fetching data, only *how* to fetch it efficiently and correctly. It must not call other services; that is the job of a manager.

4.  **L4: Persistence Layer (`app/models`)**
    *   **Responsibility:** To define the application's data schema as code.
    *   **Composition:** Contains all ORM model classes (e.g., SQLAlchemy models) that map directly to database tables, columns, relationships, and constraints.
    *   **Proscription:** This layer is purely declarative. It contains no methods or logic beyond the schema definition itself.

### **2.2. Explicit State Management & Data Hydration**

**Definition:**  
Data that crosses an architectural boundary, especially from a stateful layer (like the ORM) to another, must be **fully materialized and explicit**. Relying on implicit, "magical" data fetching (i.e., lazy loading) is the primary source of complex runtime bugs in an asynchronous environment.

**Best Practices:**

*   **No Lazy-Loading Across Async Boundaries:** An ORM object passed from a database session into a DTO or another asynchronous task must be considered "detached." Never rely on accessing a relationship (e.g., `sale.items`) that might trigger a lazy load after the original database transaction has closed.
*   **Eagerly Load What You Need:** When querying for data that will be used by another layer, use eager-loading strategies (`selectinload` in SQLAlchemy) to fetch all required objects and their necessary relationships in a single, predictable set of queries.
*   **Decouple Before Returning:** The "Unit of Work" is not complete until the data required by the caller has been safely extracted from the session-bound ORM objects into pure, session-independent data structures (like dictionaries or DTOs). The final `return` statement from an orchestrating manager method should, whenever possible, return a DTO, not a live ORM object.

### **2.3. Unidirectional Data & Control Flow**

**Pattern:**  
Control and data must flow in a single, predictable direction: `UI → Business Logic → Data Access → Persistence`. Results (data) flow back in the reverse order.

**Practices:**
*   A Service **never** calls a Manager.
*   A Manager **never** calls a UI component.
*   The UI **only** ever calls a Manager (via the `ApplicationCore`).
*   This strict, unidirectional flow prevents circular dependencies and makes the application's behavior easy to reason about and debug.

### **2.4. Non-Blocking, Responsive User Experience**

**Requirement:**  
The application must never freeze. Every user action, from a button click to a key press, must receive immediate feedback.

**Solution:**
*   All I/O-bound and CPU-intensive operations (database queries, file exports, complex calculations) **must** be executed on a background thread.
*   The **Async Bridge** pattern is mandatory. A dedicated worker thread runs an `asyncio` event loop for all backend logic.
*   Communication from the UI thread to the worker thread is achieved by submitting a coroutine for execution.
*   Communication from the worker thread back to the UI thread **must only** be done via a thread-safe signaling mechanism (e.g., `PySide6.QtCore.Signal`). The UI then updates itself in a slot connected to that signal. This is the only safe way to modify UI elements from a background operation.

### **2.5. Dependency Injection (DI) & The Application Core**

**Pattern:**  
The creation and lifecycle of core dependencies (services, managers, database connections) must be centralized in a single DI container, represented by the `ApplicationCore`.

**Practices:**
*   The `ApplicationCore` is the single source of truth for accessing backend functionality.
*   UI components are given a reference to the `core` upon initialization. They do not import managers or services directly.
*   Managers and services are lazy-loaded via properties on the `core` object. This improves startup performance and prevents circular import issues.
*   This pattern makes components easier to test, as the `core` and its dependencies can be easily mocked or replaced with test doubles.

### **2.6. Testability by Design**

**Principle:**  
A component is not considered "done" until it is covered by reliable, automated tests. The architecture must be designed from the ground up to support this.

**Practices:**
*   The strict layering and use of DI are the primary enablers of testability.
*   The test environment **must** be fully isolated from production systems. Using an in-memory database (like SQLite for unit tests) and a containerized database for integration tests is a required practice.
*   Tests must be transactional and isolated from one another. Each test should run in its own transaction that is rolled back upon completion, ensuring a clean slate for the next test.
*   The test suite should mirror the application's structure to make tests easy to locate.

---

## **3. Key Design Patterns & Anti-Patterns**

This section details the specific patterns that should be implemented and the anti-patterns that must be avoided.

### **3.1. The Unit of Work Orchestration Pattern**

This is the most critical pattern for ensuring data integrity and avoiding the runtime errors experienced in the SG-POS project.

*   **The Manager's Role (The Orchestrator):**
    *   A manager method that performs a complex, multi-step business operation **must** define the transaction boundary using `async with self.core.get_session() as session:`.
    *   It is responsible for passing this single `session` object to every downstream service or manager call.
    *   It is responsible for orchestrating the entire flow: validating input, calling services, handling results, and preparing the final data for the UI.
    *   The `commit` or `rollback` is handled implicitly and automatically by the `async with` context manager.

*   **The Service's Role (The Worker):**
    *   A service method **must** be transaction-aware by accepting an optional `session` parameter.
    *   When a session is provided, the service method **must** use it directly without creating a new transaction or session.
    *   A service method should be simple and focused on a single data operation (e.g., `find_by_id`, `persist_object`). It should not contain complex orchestration logic.

*   **Anti-Pattern: The Transactional Service Method:** Avoid writing service methods that create their own transactions and then perform multiple distinct operations. This logic belongs in a manager.

### **3.2. The DTO as a Decoupling Checkpoint**

DTOs are more than just data containers; they are a critical tool for decoupling and preventing state-related bugs.

*   **Best Practice: Manual DTO Construction for Complex Objects:**
    While `from_orm` is convenient, it is dangerous when used with ORM objects that have nested relationships that might be lazy-loaded. The most robust pattern is to manually construct the DTO from data that is guaranteed to be in memory.

*   **Example (from SG-POS `SalesManager`):** The final, correct implementation did not rely on `from_orm` for the `SalesTransactionItemDTO`. Instead, it did the following:
    1.  At the start of the transaction, it fetched all `Product` data into a dictionary (`calculated_totals["items_with_details"]`).
    2.  After the `SalesTransactionItem` objects were persisted, it looped through them.
    3.  For each persisted item, it created the DTO by combining the persisted data (e.g., `quantity`, `line_total`) with the product data from the dictionary (`product_name`, `sku`).

    ```python
    # The robust pattern for creating the items DTO list
    final_items_dto = []
    persisted_items_map = {item.product_id: item for item in persisted_sale.items}
    for item_detail in calculated_totals["items_with_details"]:
        persisted_item = persisted_items_map[item_detail["product_id"]]
        final_items_dto.append(
            SalesTransactionItemDTO(
                product_name=item_detail["product_name"],
                sku=item_detail["sku"],
                quantity=persisted_item.quantity,
                # ... other fields
            )
        )
    ```
    This pattern completely eliminates the possibility of a lazy-load error during DTO creation.

### **3.3. Architectural Anti-Patterns to Avoid (Lessons Learned)**

*   **Anti-Pattern: The Fragile `refresh()`**
    *   **Description:** Using `session.refresh()` liberally to try to solve state management issues.
    *   **Problem:** As seen in `SalesService`, a chain of `refresh` calls can lead to unpredictable behavior and trigger the very lazy-load issues it's meant to prevent. It adds unnecessary database round-trips and complexity.
    *   **Solution:** Avoid `refresh()` where possible. If you need to load relationships on an existing object, use an explicit `SELECT` statement with `selectinload`. If you just need the data for a DTO, use the manual construction pattern described above.

*   **Anti-Pattern: Leaky Service Abstractions**
    *   **Description:** A component from one layer directly calls a component from a non-adjacent layer, or a component from one domain calls a low-level component from another domain.
    *   **Problem:** The `AttributeError` in `SalesManager` was caused by this. It tried to call `self.customer_service` directly, violating the established pattern of `Manager -> Manager`. This creates tight coupling and makes the system harder to understand and refactor.
    *   **Solution:** Strictly enforce the manager-to-manager and manager-to-service communication paths.

*   **Anti-Pattern: Implicit Reliance on Lazy-Loading**
    *   **Description:** The root cause of all the `greenlet_spawn` errors. This is any code that accesses a SQLAlchemy relationship attribute and *assumes* the data will be there, without having explicitly eager-loaded it first.
    *   **Problem:** In an async context, this assumption is fatal. The implicit database query triggered by the lazy load will not be in a valid async context, causing a hard crash.
    *   **Solution:** Assume **all** relationships are unloaded unless you have explicitly loaded them with `selectinload` in the query that fetched the parent object. **Treat ORM objects as if they are "expired" the moment they are passed out of the method that queried them.**

---

## **4. Conclusion**

This document provides a battle-hardened architectural blueprint derived from the real-world development and debugging of a complex enterprise application. The principles of strict layering, explicit state management, and robust transaction orchestration are not theoretical ideals; they are the practical solutions to the most challenging bugs encountered in modern asynchronous software development.

By adopting these principles and patterns, future projects can proactively avoid entire classes of subtle, time-consuming errors, leading to faster development cycles, higher-quality products, and more maintainable codebases. This document should be considered the foundational standard for technical design and code review within the organization.
