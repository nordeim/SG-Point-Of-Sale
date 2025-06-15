# Comprehensive Project Understanding: The SG Point-of-Sale (SG-POS) System

## 1. Introduction: The SG-POS System at a Glance

The SG Point-of-Sale (SG-POS) System is envisioned as an enterprise-grade, open-source, cross-platform desktop application meticulously engineered to cater to the distinct operational and regulatory demands of Small to Medium-sized Businesses (SMBs) within Singapore's vibrant retail sector. This ambitious project aims to deliver a robust, modern, and user-centric POS solution that directly addresses the shortcomings of existing market offerings.

### 1.1. The Problem SG-POS Solves

Current POS solutions available to Singaporean SMBs often present a compromise:
*   **Generic International Systems:** While feature-rich and aesthetically pleasing, they frequently fall short on native Singapore-specific compliance (e.g., Goods & Services Tax - GST, PayNow integration) and can be prohibitively expensive. GST capabilities often feel like an afterthought, requiring manual workarounds.
*   **Legacy Local Systems:** These might handle local regulations but are typically built on outdated technologies, resulting in sluggish performance, clunky user interfaces, inherent security vulnerabilities, and a severe lack of modern integration capabilities. Maintenance and scaling become significant hurdles.
*   **Basic Tablet-Based Apps:** User-friendly and quick to deploy, yet they often lack the depth required for sophisticated inventory management, multi-outlet operations, or comprehensive financial reporting crucial for serious retail businesses.

SG-POS is strategically positioned to bridge these gaps. It aspires to be a professional-grade tool for discerning SMBs, marrying a deep understanding of Singapore's unique business environment with world-class software architecture and modern technological prowess.

### 1.2. Vision and Mission

*   **Vision:** To emerge as the most trusted and efficient digital backbone for Singapore's SMB retail sector, empowering businesses to flourish through streamlined operations, actionable insights, and effortless regulatory compliance.
*   **Mission:** To deliver an affordable, user-centric, and world-class POS system that seamlessly integrates sales, inventory, and financial management, meticulously tailored to the specific nuances of the Singaporean business landscape.

### 1.3. Target Market and User Personas

The system is designed for Singapore-based SMBs operating with 1-10 outlets and an employee count ranging from 2 to 50. Key user personas include:

*   **Chloe, the Cashier:** Seeks speed, ease of use, and error prevention in daily transactions.
*   **Darren, the Store Manager:** Requires real-time visibility into sales and stock across multiple stores, with a desire for automation in tasks like reordering.
*   **Mei, the Accountant:** Needs simplified, one-click generation of IRAS-compliant reports and seamless integration with accounting software.
*   **Mr. Tan, the Owner:** Demands clear, actionable reports and insights to drive strategic business decisions regarding pricing, inventory, and expansion.

### 1.4. Key Differentiators

SG-POS distinguishes itself through:
*   **Native GST & Regulatory Compliance:** Built from the ground up for IRAS guidelines, not as an afterthought.
*   **Enterprise-Grade Architecture:** A professional, scalable, and maintainable codebase.
*   **Modern Technology Stack:** Leverages contemporary and robust technologies.
*   **Offline-First Sync:** Combines desktop reliability with eventual cloud benefits, ensuring continuous operations.

## 2. Core Functional Requirements

The SG-POS system is designed to provide a comprehensive suite of functionalities critical for modern retail operations:

*   **Sales & Checkout:**
    *   **Flawless Speed:** Instant barcode scanning and product search for swift customer service.
    *   **Flexible Payments:** Support for split tender, accommodating various payment methods including cash, NETS, PayNow, and credit/debit cards.
    *   **Returns & Exchanges:** Streamlined processing by referencing original receipt numbers.
    *   **Offline Processing:** Core sales functions remain operational without internet connectivity, with transactions securely queued for later synchronization.
*   **Inventory Management:**
    *   **Real-time Stock Deduction:** Automatic inventory updates upon sales completion across all terminals.
    *   **Automated Reorder Alerts:** Proactive notifications when stock levels drop below predefined reorder points.
    *   **Consolidated Stock View:** Ability to view inventory levels across multiple outlets from a central dashboard.
    *   **Purchase Order Management:** Creation, tracking, and receiving of goods against purchase orders.
    *   **Stock Takes & Adjustments:** Tools for accurate inventory reconciliation with an audit trail.
*   **Customer Relationship Management (CRM):**
    *   **Tiered Loyalty Programs:** Configurable loyalty tiers with differential point accrual and redemption mechanisms.
    *   **Detailed Profiles:** Comprehensive customer information and purchase history tracking.
*   **Singapore-Specific Compliance:**
    *   **GST Act & IRAS IAF:** Accurate GST calculation (standard, zero-rated, exempt rates) and generation of IRAS-compliant GST F5 reports and Audit Files (IAF).
    *   **Personal Data Protection Act (PDPA):** Implementation of explicit consent, data encryption at rest, role-based access controls, and features supporting data access/deletion requests.
    *   **Peppol e-Invoicing:** Capability to format and send B2B invoices in the Peppol BIS Billing 3.0 SG format via the Peppol network.
    *   **Payment Services Act:** Adherence to regulations by integrating with licensed Payment Service Providers (e.g., Stripe, NETS) via secure terminals/APIs, ensuring no cardholder data is stored on the POS system.
*   **Reporting & Analytics:**
    *   **Real-time Dashboard:** Customizable KPIs like daily revenue, average transaction value, and top-selling products.
    *   **In-depth Reports:** Comparison of staff performance, sales trends, product profitability, and more.
    *   **Exportability:** Reports can be exported to PDF and CSV formats for external analysis or accounting integration.

## 3. Non-Functional Requirements (NFRs)

Beyond core features, the project places significant emphasis on non-functional aspects to ensure a high-quality, resilient application:

*   **Performance:**
    *   Core UI interactions: <200ms responsiveness.
    *   Standard sales transaction completion: <2 seconds.
    *   Reports (up to 1 year data): <15 seconds generation time.
*   **Reliability:**
    *   System Uptime: ≥99.9% during business hours (8 AM - 10 PM SGT).
    *   Graceful handling of network disconnects (offline mode) and atomic database transactions.
*   **Security:**
    *   Data Encryption: All sensitive data (passwords, PII) encrypted at rest and in transit.
    *   Role-Based Access Control (RBAC): Enforced at both UI and API levels.
    *   Vulnerability Protection: Guarding against SQL Injection and other common vulnerabilities.
*   **Scalability:**
    *   Concurrent Terminals: Support for up to 50 concurrent terminals in a single-store setup.
    *   Data Longevity: Database schema designed to handle 5+ years of transaction data without significant performance degradation.
*   **Usability:**
    *   Training Time: A new cashier should be proficient in standard sales within 30 minutes.
    *   Navigation: Full keyboard navigability throughout the system.

## 4. Architectural Principles and Design

The SG-POS system's architecture is a cornerstone of its design, explicitly prioritizing long-term maintainability, developer productivity, and system robustness. It adheres to a set of core principles and patterns.

### 4.1. Architectural Philosophy & Guiding Principles

*   **Separation of Concerns (SoC):** A strict layered architecture ensures each component has a single, well-defined responsibility, preventing tight coupling and improving modularity and maintainability.
*   **Dependency Inversion Principle (DIP):** High-level business logic is decoupled from low-level data access specifics. Both depend on abstractions (interfaces/protocols), facilitated by Dependency Injection, making the system inherently testable.
*   **Explicit Over Implicit:** Preferring clear, self-documenting patterns. This includes the **Result Pattern** for predictable error handling and **Data Transfer Objects (DTOs)** for explicit data contracts between layers, enhancing code readability and robustness.
*   **Asynchronous First:** All I/O-bound operations (database, network, file system) are designed to be asynchronous, running in a background thread to prevent UI freezing and ensure a fluid user experience.
*   **Testability as a First-Class Citizen:** The architecture inherently supports comprehensive testing, from isolated unit tests to integrated end-to-end scenarios, by promoting decoupled components and well-defined interfaces.

### 4.2. High-Level System Architecture (C4 Model)

The system is conceptualized using the C4 Model, starting from a broad overview and progressively detailing components.

*   **System Context (Level 1):** The SG-POS Desktop Application interacts directly with users (Cashiers, Managers) and integrates with external systems like Payment Gateways (e.g., Stripe, NETS), Accounting Systems (e.g., Xero, QuickBooks), and (future) IRAS APIs for compliance.
*   **Container Diagram (Level 2):** Zooming into the client machine, the `Presentation Layer (PySide6 GUI)` handles user interaction, delegating actions to the `Business & Data Layers (Python Code)`. This Python backend then interacts with a `PostgreSQL Database` for all data persistence.

### 4.3. Layered Architecture Deep Dive

The architecture is composed of four distinct layers, each with clearly defined responsibilities and strict boundaries:

1.  **Presentation Layer (`app/ui/`)**:
    *   **Responsibility:** User interface rendering, capturing user input, and displaying data. It is "dumb," devoid of business logic.
    *   **Technologies:** PySide6 (Widgets, Qt Models, Signals & Slots).
    *   **Interaction:** Communicates exclusively with the `ApplicationCore` to delegate actions and receive data updates. It consumes DTOs and produces user input.

2.  **Business Logic Layer (`app/business_logic/`)**:
    *   **Responsibility:** Orchestrates business workflows and enforces business rules. This is the application's core.
    *   **Components:** High-level `Managers` (e.g., `SalesManager`), `Validators`, and `Calculators` (e.g., `GSTCalculator`).
    *   **Interaction:** Uses `ApplicationCore` to access Data Access Layer services. Consumes DTOs from the UI/other managers and produces DTOs or `Result` objects.

3.  **Data Access Layer (`app/services/`)**:
    *   **Responsibility:** Provides a clean, abstract API for data persistence, implementing the **Repository Pattern**.
    *   **Components:** `Services` or `Repositories` (e.g., `ProductService`, `CustomerRepository`) offering CRUD-like methods.
    *   **Interaction:** Used by the Business Logic Layer. Translates business objects/DTOs into database operations using SQLAlchemy ORM.

4.  **Persistence Layer (`app/models/` & Database Engine)**:
    *   **Responsibility:** Defines data structures (SQLAlchemy models) and manages physical storage (PostgreSQL).
    *   **Components:** SQLAlchemy ORM Models mapping to database tables, PostgreSQL database server, and Alembic for schema migrations.

### 4.4. Communication Flow Between Layers

The flow is strictly top-down: `UI -> ApplicationCore -> Business Manager -> Data Service -> ORM Model -> Database`. Results and data typically flow back up the chain. This unidirectional flow maintains strict separation and predictability.

### 4.5. Core Architectural Patterns in Practice

*   **Dependency Injection (DI): The `ApplicationCore`**:
    *   Acts as the central DI container and service locator.
    *   Instantiated once, provides lazy-loaded access to all services and managers via `@property` accessors.
    *   Manages database engine and session factory, offering an `asynccontextmanager` for database sessions.
    *   Example: `self.app_core.sales_manager` provides a `SalesManager` instance.

*   **The Result Pattern: Explicit Error Handling**:
    *   Implemented via `Result`, `Success`, and `Failure` classes in `app/core/result.py`.
    *   Methods return a `Result` object (either `Success[T]` with a value or `Failure[E]` with an error) instead of raising exceptions for anticipated business errors.
    *   This forces explicit error handling by the calling code, leading to more robust and readable logic.

*   **Data Transfer Objects (DTOs): Clean Data Contracts**:
    *   Pydantic models are used to define validated data structures for communication between layers (e.g., `ProductCreateDTO` from UI to `SalesManager`).
    *   Prevents "leaky abstractions" by avoiding direct exposure of database ORM models to business or UI layers.
    *   Ensures data integrity and type safety at layer boundaries.

*   **Asynchronous Model: The UI/Async Bridge**:
    *   Maintains UI responsiveness by running I/O-bound tasks in a separate `asyncio` event loop on a dedicated `QThread` (`AsyncWorker`).
    *   The Qt `QApplication` event loop runs exclusively on the main thread for UI updates.
    *   Communication between the two threads is thread-safe, typically using `QMetaObject.invokeMethod` with `Qt.QueuedConnection` to safely update UI from background tasks.
    *   A function like `schedule_task_from_qt(coro, on_done_callback)` submits coroutines and schedules UI thread callbacks.

## 5. Technology Stack

The SG-POS project leverages a modern, professional-grade technology stack carefully selected for reliability, performance, and maintainability:

*   **Language:** Python 3.11+ - Chosen for its strong typing features, vast ecosystem, and suitability for complex business logic.
*   **GUI Framework:** PySide6 (Qt 6) - Provides a robust, high-performance, and cross-platform native desktop UI.
*   **Database:** PostgreSQL 15+ - A highly reliable, ACID-compliant, and scalable relational database, ideal for financial data.
*   **ORM:** SQLAlchemy 2.0 - The industry-standard ORM, offering powerful features and excellent asynchronous support.
*   **DB Migrations:** Alembic - The de facto standard for managing SQLAlchemy database schema versions systematically.
*   **Asynchronous I/O:** `asyncio` - Python's native library for non-blocking I/O operations, critical for a responsive application.
*   **Data Validation:** Pydantic 2.x - Enforces strong data contracts (DTOs) with a clear, declarative syntax, essential for data integrity.
*   **Testing:** Pytest (with `pytest-qt`, `pytest-asyncio`, `pytest-cov`) - A powerful and flexible testing framework with a rich plugin ecosystem covering unit, integration, and UI testing.
*   **Packaging:** Poetry - Manages dependencies and builds reproducible environments, streamlining development setup.
*   **Code Quality:** Black (Formatter), Ruff (Linter), MyPy (Static Type Checker) - A comprehensive suite to ensure consistent code style, fast linting, and rigorous static type safety for long-term maintainability.
*   **HTTP Client:** `aiohttp` - For asynchronous HTTP requests, crucial for external API integrations.
*   **PDF Generation:** `reportlab` - For generating PDF receipts and reports.
*   **Excel Export:** `openpyxl` - For exporting data to XLSX files.
*   **QR Code Generation:** `qrcode` - With PIL extra for image processing, useful for PayNow or other QR-based transactions.
*   **Security:** `bcrypt` and `cryptography` - For secure password hashing and other encryption needs.
*   **Logging:** `structlog` - For structured, context-aware logging, improving observability.
*   **Environment Variables:** `python-dotenv` - For loading environment variables from `.env` files, facilitating local development.
*   **Interactive Shell:** `ipython` - A better interactive Python shell for development and debugging.
*   **Documentation:** Sphinx, myst-parser, sphinx-rtd-theme - For generating professional project documentation.

The `pyproject.toml` file explicitly manages these dependencies, ensuring a consistent and reproducible development environment. The Python version constraint is `^3.11` (meaning `>=3.11.0, <3.14.0`), reinforcing the commitment to modern Python features.

## 6. Database Design and Persistence

The database is the bedrock of the SG-POS system's data integrity, carefully designed to support the application's functional and non-functional requirements.

### 6.1. Schema Principles

*   **Primary Keys:** All primary keys are `UUID`s (`DEFAULT gen_random_uuid()`), chosen to avoid conflicts in distributed or multi-master scenarios and to decouple keys from business meaning.
*   **Foreign Keys:** Referential integrity is strictly enforced with `FOREIGN KEY` constraints, with `ON DELETE RESTRICT` as the default to prevent accidental data loss.
*   **Data Types:** `NUMERIC(precision, scale)` is uniformly used for all monetary values to prevent floating-point inaccuracies. `TIMESTAMPTZ` is used for all timestamps to ensure timezone correctness and consistency.
*   **Auditing:** Critical tables include `created_at` and `updated_at` columns, complemented by a dedicated `audit_logs` table for comprehensive, immutable change tracking.
*   **Soft Deletes:** Key entities (e.g., `products`, `customers`) utilize an `is_active` flag instead of hard deletion, preserving historical data integrity.

### 6.2. Key Tables Overview (Conceptual)

The schema includes essential tables such as:
*   `companies`: For multi-tenancy support.
*   `users`: For system users with roles (`admin`, `manager`, `cashier`).
*   `categories`, `products`, `inventory`: For robust product and stock management.
*   `customers`: For customer relationship management.
*   `sales_transactions`, `sales_transaction_items`, `payments`: The core transactional data.
*   `audit_logs`: A central table for all significant data changes.

### 6.3. Data Integrity & Constraints

*   **CHECK Constraints:** Used to enforce valid values for `enum`-like fields (e.g., `role`, `status`).
*   **Triggers:** An `update_updated_at` trigger will automatically update the `updated_at` column on record modification. A critical audit trigger (`log_changes`) will be attached to key tables to populate the `audit_logs` table automatically.

### 6.4. Auditing Strategy

The `audit_logs` table captures `old_values` and `new_values` as `JSONB` snapshots, along with `action` type, `table_name`, `record_id`, `ip_address`, and `created_at`.
A critical aspect of this strategy is the **application-side responsibility**: the SG-POS application **MUST** execute `SET sgpos.current_user_id = '<the-uuid-of-the-logged-in-user>';` at the beginning of every database transaction. This session variable is read by the audit trigger to correctly log the `user_id` for each action. Failure to set this variable will result in `NULL` `user_id` values in the audit logs.

## 7. Codebase File Hierarchy and Key Modules

The project's file hierarchy is designed for scalability and directly mirrors the layered architectural design, providing a clear and predictable structure.

```
sg-pos-system/
├── app/
│   ├── main.py                     # Application entry point
│   ├── core/                       # Core Infrastructure (DI, config, result, async_bridge)
│   ├── models/                     # SQLAlchemy ORM Models (Persistence Layer)
│   ├── services/                   # Data Access Layer (Repositories)
│   ├── business_logic/             # Business Logic Layer
│   │   ├── managers/               # High-level business orchestrators
│   │   └── dto/                    # Data Transfer Objects (Pydantic models)
│   ├── ui/                         # Presentation Layer (PySide6 widgets, views, dialogs)
│   ├── integrations/               # External API connectors
│   └── utils/                      # Shared utility functions
├── tests/                          # Test suite (unit, integration, e2e)
├── scripts/                        # Utility & DB scripts (e.g., schema.sql, seed_data.py)
├── migrations/                     # Alembic migration scripts
├── docs/                           # Project documentation
├── .env.example                    # Template for environment variables
├── pyproject.toml                  # Poetry project definition
└── README.md
```

### 7.1. Rationale for the Structure

*   **Logical Mapping:** Top-level directories within `app/` (e.g., `core`, `models`, `services`, `business_logic`, `ui`) directly correspond to the architectural layers, making navigation intuitive.
*   **Decoupling:** Clear separation of DTOs within `business_logic/dto` reinforces their role as the data contract between layers, ensuring the UI and services interact through well-defined interfaces.
*   **Granular UI:** The `ui` directory is sub-divided into `widgets` (reusable components), `views` (main application screens), and `dialogs` (modal forms) to manage UI complexity effectively.
*   **Test Alignment:** The `tests` directory mirrors the `app/` structure, facilitating easy identification of tests for specific modules and maintaining a clear distinction between unit and integration tests.

### 7.2. Key Module Specifications

*   **`app/core/application_core.py`:** The central Dependency Injection container, responsible for instantiating the database engine, session factory, and providing lazy-loaded access to all business managers and data services. It's the `app_core` instance passed throughout the application.
*   **`app/business_logic/managers/sales_manager.py`:** Orchestrates the entire sales process, coordinating with `InventoryManager`, `CustomerManager`, and `PaymentManager` to finalize a sale atomically, handle stock deduction, loyalty points, and payment processing. All methods return `Result` objects.
*   **`app/services/product_service.py`:** Implements the Repository pattern for product data, encapsulating all direct database interactions (CRUD operations for products). It translates between SQLAlchemy ORM models and DTOs, returning `Result` objects.
*   **`app/ui/views/pos_view.py`:** The main UI for cashiers. It manages product search, cart display, and triggers business logic via `ApplicationCore` by calling methods on managers, displaying results asynchronously.
*   **`app/ui/dialogs/payment_dialog.py`:** A modal dialog for handling multi-tender payments, gathering payment details from the cashier and interacting with the `SalesManager` to finalize the financial aspects of a transaction.

## 8. Development Workflow and Tooling

The project adheres to a structured development workflow supported by modern tools to ensure efficiency and high code quality.

### 8.1. Local Development Environment Setup

The setup process is streamlined using Docker Compose for the database and Poetry for dependency management:
1.  **Clone Repository:** `git clone <repo_url> sg-pos-system && cd sg-pos-system`
2.  **Start Database:** `docker compose up -d db` (starts PostgreSQL 15 container).
3.  **Install Dependencies:** `poetry install` (creates virtual environment, installs production and development packages).
4.  **Activate Environment:** `poetry shell` (activates the isolated Python environment).
5.  **Run Migrations:** `alembic upgrade head` (initializes database schema).
6.  **Seed Data (Optional):** `python scripts/database/seed_data.py` (populates with sample data).
7.  **Run Application:** `python app/main.py` (launches the GUI).
8.  **Run Tests:** `pytest` (executes the comprehensive test suite). `pytest --cov=app --cov-report=html` provides code coverage.

### 8.2. Code Quality Tools

The `pyproject.toml` configuration centralizes strict code quality enforcement:
*   **Black:** Auto-formats code to a consistent style (`line-length = 88`).
*   **Ruff:** An extremely fast linter, replacing multiple tools (flake8, isort, bugbear, etc.), enforcing a broad range of high-quality rules.
*   **MyPy:** Static type checker enforcing strict type checking (`disallow_untyped_defs`, `strict_optional`).
*   **Pre-commit:** Manages pre-commit hooks to ensure code quality checks run automatically before every commit.

### 8.3. Git Flow Strategy

A standardized Git Flow strategy is adopted:
*   `main` branch: Stable, production-ready code.
*   `develop` branch: Primary integration branch for completed features.
*   Feature branches: Created from `develop` for every new task (`feature/PROJ-123-feature-name`).
*   Pull Requests (PRs): Required to merge feature branches into `develop`, subject to code reviews.
*   Code Reviews: Mandatory approval by at least one peer/lead, checking against Acceptance Checklists.

### 8.4. Continuous Integration (CI/CD) Strategy

A robust CI pipeline (GitHub Actions) runs on every push and pull request:
*   **Lint & Format:** Checks `black` and `ruff` adherence.
*   **Static Analysis:** Runs `mypy`.
*   **Run Tests:** Executes the full `pytest` suite against a test database.
*   **Build Docker Image:** Builds and tags a production Docker image on the `main` branch.
A "Release" workflow is triggered on new tags, pushing images to a container registry and optionally initiating deployments.

## 9. Project Management and Teams

The project adopts an Agile methodology with two-week sprints, emphasizing clear communication, structured tasks, and rigorous quality gates.

### 9.1. Development Methodology: Agile with Sprints

*   **Sprint Planning:** PM and team leads select tasks (files to be built) for each two-week sprint.
*   **Daily Stand-ups:** Brief daily meetings to review progress, plan for the day, and identify blockers.
*   **Sprint Review:** End-of-sprint demonstration of working software.
*   **Sprint Retrospective:** Team discussion on improvements for the next sprint.

### 9.2. Definition of Done

A task is considered **DONE** only when:
1.  All functional requirements are met.
2.  All items in the Acceptance Checklist for the file are completed.
3.  The code has been reviewed and approved by a peer.
4.  The Pull Request has been successfully merged into the `develop` branch.
5.  The Continuous Integration (CI) pipeline passes.

### 9.3. Team Structure and Dependencies

Teams can be structured around architectural layers:
*   **Backend Team:** Focuses on `services` and `business_logic` layers (data access, business rules).
*   **Frontend Team:** Focuses on `ui` layer (widgets, dialogs, views), consuming backend interfaces.
*   **QA & Testing Team:** Develops unit, integration, and E2E tests in parallel with feature development.

Cross-stage dependencies are managed by defining **DTOs as contracts** before UI work begins, enabling parallel development. The `ApplicationCore` facilitates this decoupling by centralizing dependency provision.

## 10. Deployment Considerations

The deployment guide provides a detailed, step-by-step process for setting up the PostgreSQL database in a production or staging environment.

### 10.1. PostgreSQL Database Deployment

*   **Installation:** Instructions for Ubuntu 22.04 LTS, emphasizing adding the official PostgreSQL repository for the latest version (15+).
*   **User and Database Creation:** Secure practice of creating a dedicated `sgpos_prod_user` with a strong password and minimal privileges, owning the `sgpos_prod` database.
*   **Schema Application:** Using `psql -h localhost -U sgpos_prod_user -d sgpos_prod -f schema.sql` to apply the DDL script.
*   **Network Access Configuration:** Modifying `postgresql.conf` (`listen_addresses = '*'`) and `pg_hba.conf` to securely allow connections from the application server using `scram-sha-256` authentication. This involves adding `host sgpos_prod sgpos_prod_user <app_server_ip_address>/32 scram-sha-256`.
*   **Verification:** Steps to confirm successful installation, schema deployment, and remote connectivity.

### 10.2. Production Environment Setup Philosophy

*   **12-Factor App Principles:** Configuration via environment variables, stateless application containers.
*   **Server Requirements:** Defined minimum CPU (4+ cores) and RAM (8GB minimum).
*   **Deployment Method:** Primarily Docker, with a multi-stage `Dockerfile` and `docker-compose.prod.yml`.
*   **Secrets Management:** Secrets (DB passwords, API keys) injected via environment variables.
*   **Managed Database:** Recommendation for managed PostgreSQL services (AWS RDS, DigitalOcean) for automated backups and scaling.
*   **Process Management:** Docker daemon or `systemd` for container/application management.
*   **Logging:** Structured JSON logs to `stdout`, forwarded to centralized logging services.

## 11. Future Vision and Roadmap

The project has a clear phased roadmap for future development:
*   **v1.0 (MVP):** Current focus - Core Sales, Inventory, Basic CRM, GST F5, local payment integrations.
*   **v1.1 (Post-Launch):** Integrated E-commerce Connector (Shopify), advanced promotions, mobile dashboard companion app.
*   **v1.2:** AI-driven inventory forecasting, enhanced CRM with email marketing, multi-outlet dashboard consolidation.
*   **v2.0 (Long-term Vision):** Full cloud-native backend, plugin/marketplace API for third-party developers.

## 12. Risks and Mitigation Strategies

Key risks and their mitigation strategies have been identified:
*   **Scope Creep:** Mitigated by strict adherence to the PRD and formal change request processes.
*   **Performance Issues at Scale:** Addressed by proactive performance testing, database indexing/query optimization, and a caching layer.
*   **Changes in IRAS GST Regulations:** GST rates and rules stored in configuration, and the `GSTManager` module designed for easy updates.
*   **Third-Party Payment Gateway Failure:** Mitigated by implementing the Circuit Breaker pattern, supporting multiple gateways for failover, and a robust offline mode for cash sales.

---

This comprehensive understanding of the SG-POS project, synthesizing information across the PRD, PAD, PMD, deployment guide, and `pyproject.toml`, provides a solid foundation for initiating the codebase development. The project's commitment to robust architecture, meticulous design, and structured development processes positions it for successful implementation and long-term maintainability.
