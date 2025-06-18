<p align="center">
  <img src="https://raw.githubusercontent.com/nordeim/SG-Point-Of-Sale/refs/heads/main/POS_home_screen.png" alt="SG-POS System Logo" width="600"/>
</p>

<h1 align="center">SG Point-of-Sale (SG-POS) System</h1>

<p align="center">
  <strong>An enterprise-grade, open-source Point-of-Sale system, meticulously engineered for Singapore's SMB retail landscape.</strong>
</p>

<p align="center">
  <!-- Badges -->
  <a href="#">
    <img src="https://img.shields.io/badge/Status-In%20Development-orange" alt="Project Status">
  </a>
  <a href="https://github.com/your-org/sg-pos-system/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License: MIT">
  </a>
  <a href="https://www.python.org/">
    <img src="https://img.shields.io/badge/Python-3.11+-3776AB.svg" alt="Python 3.11+">
  </a>
  <a href="https://www.qt.io/">
    <img src="https://img.shields.io/badge/UI-PySide6%20(Qt6)-41CD52.svg" alt="PySide6">
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

*   [1. Introduction: What is SG-POS?](#1-introduction-what-is-sg-pos)
*   [2. Current Features & Status](#2-current-features--status)
*   [3. Architectural Deep Dive](#3-architectural-deep-dive)
    *   [The Layered Architecture](#the-layered-architecture)
    *   [Module Interaction Flowchart](#module-interaction-flowchart)
*   [4. Codebase Deep Dive](#4-codebase-deep-dive)
    *   [Project File Hierarchy](#project-file-hierarchy)
    *   [Key File & Directory Descriptions](#key-file--directory-descriptions)
*   [5. Technology Stack](#5-technology-stack)
*   [6. Developer Setup & Deployment Guide](#6-developer-setup--deployment-guide)
    *   [Prerequisites](#prerequisites)
    *   [Step-by-Step Setup Guide](#step-by-step-setup-guide)
*   [7. User Guide: Running the Application](#7-user-guide-running-the-application)
*   [8. Project Roadmap](#8-project-roadmap)
    *   [Immediate Goals (v1.0.1)](#immediate-goals-v101)
    *   [Long-Term Goals (v1.1+)](#long-term-goals-v11)
*   [9. How to Contribute](#9-how-to-contribute)
*   [10. License](#10-license)

---

## **1. Introduction: What is SG-POS?**

**SG-POS** is a free and open-source Point-of-Sale system, engineered from the ground up to address the specific operational and regulatory challenges faced by Small to Medium-sized Businesses (SMBs) in Singapore. It aims to provide the power and polish of expensive enterprise systems in an accessible, modern, and maintainable package.

This project is built with an obsessive focus on quality, both in the user experience and, most importantly, in the engineering. It serves not only as a functional tool but also as a reference implementation for professional-grade Python application architecture.

---

## **2. Current Features & Status**

The application is currently in a feature-complete skeleton state, with the core architecture and many key workflows fully implemented.

| Feature Area                      | Status                  | Notes                                                                                                         |
| --------------------------------- | ----------------------- | ------------------------------------------------------------------------------------------------------------- |
| **Sales & Checkout**              | ✅ **Functional**       | Core sales processing, cart management, and payment collection via the `POSView` and `PaymentDialog` are working. |
| **Customer Management**           | ✅ **Functional**       | Full CRUD (Create, Read, Update, Deactivate) operations for customers are implemented in `CustomerView`.      |
| **Inventory Management**          | ✅ **Functional**       | `InventoryView` provides a stock summary, PO management, and stock movement history.                          |
| **Purchase Orders & Stock-ins**   | ✅ **Functional**       | Creation of Purchase Orders and stock adjustments are fully implemented via dialogs.                          |
| **Reporting & Analytics**         | ✅ **Functional**       | The backend `ReportingManager` and `GstManager` correctly generate data for all implemented reports.          |
| **User & Company Settings**       | 🟡 **Partially Implemented** | `SettingsView` can display company and user info. Role assignment logic is a backend `TODO`.                |
| **Product Management**            | 🔴 **Placeholder**      | The `ProductView` UI is a placeholder. The backend logic is complete, but the UI is not yet functional.     |

---

## **3. Architectural Deep Dive**

SG-POS is built on a set of robust architectural principles designed for maintainability and scalability.

### The Layered Architecture

Our architecture strictly separates the application into four logical layers:

1.  **Presentation Layer (`app/ui`):** Built with PySide6, this layer is responsible *only* for what the user sees and how they interact with it. It contains no business logic.
2.  **Business Logic Layer (`app/business_logic`):** The brain of the application. `Managers` orchestrate workflows and enforce business rules, using `DTOs` (Data Transfer Objects) as data contracts.
3.  **Data Access Layer (`app/services`):** Implements the Repository Pattern. It provides a clean, abstract API (e.g., `product_service.get_by_sku()`) for database operations, hiding SQL complexity.
4.  **Persistence Layer (`app/models`):** Defines the database schema using SQLAlchemy ORM models, which map directly to PostgreSQL tables.

### Module Interaction Flowchart

The flow of control and data is unidirectional and decoupled, ensuring a responsive UI and testable components. The `ApplicationCore` acts as a Dependency Injection (DI) container, providing services and managers to the components that need them.

```mermaid
graph TD
    subgraph "User Interface (app/ui)"
        direction TB
        A[Views & Dialogs] -- "1. User Action" --> B{Async Bridge};
    end

    subgraph "Business Logic (app/business_logic)"
        direction TB
        C[Managers] --> D[Data Transfer Objects (DTOs)];
    end

    subgraph "Data Access (app/services)"
        direction TB
        E[Services (Repositories)];
    end

    subgraph "Data Model (app/models)"
        direction TB
        F[ORM Models (SQLAlchemy)];
    end
    
    subgraph "Database"
        direction TB
        G[PostgreSQL];
    end

    subgraph "Application Core (app/core)"
        direction TB
        H[ApplicationCore (DI Container)] -- Manages --> I[Async Worker];
    end

    %% Interactions
    B -- "2. Submits Task to Worker Thread" --> I;
    I -- "3. Executes Task" --> C;
    H -- Provides Dependencies --> C;
    C -- "4. Orchestrates Logic" --> E;
    E -- "5. Queries Database" --> F;
    F -- "6. Maps to" --> G;
    E -- "7. Returns ORM Models" --> C;
    C -- "8. Converts to DTOs" --> D;
    C -- "9. Returns Result(DTO)" --> I;
    I -- "10. Signals Result" --> B;
    B -- "11. Delivers to UI Callback" --> A;

```
---

## **4. Codebase Deep Dive**

### Project File Hierarchy

```
sg-pos-system/
├── app/
│   ├── core/
│   ├── models/
│   ├── services/
│   ├── business_logic/
│   │   ├── dto/
│   │   └── managers/
│   ├── ui/
│   │   ├── dialogs/
│   │   ├── resources/
│   │   ├── views/
│   │   └── widgets/
│   ├── integrations/
│   └── main.py
├── migrations/
│   ├── versions/
│   └── env.py
├── scripts/
│   └── database/
├── tests/
├── .env.example
├── alembic.ini
├── docker-compose.dev.yml
└── pyproject.toml
```

### Key File & Directory Descriptions

| Path                             | Description                                                                                              |
| -------------------------------- | -------------------------------------------------------------------------------------------------------- |
| `pyproject.toml`                 | **Project Definition.** Manages all dependencies, project metadata, and development tool configurations.     |
| `docker-compose.dev.yml`         | **Database Service.** Defines and configures the PostgreSQL database container for local development.        |
| `alembic.ini` / `migrations/`    | **Database Migrations.** Configuration and scripts for managing database schema evolution using Alembic. |
| `app/main.py`                    | **Application Entry Point.** Initializes the application core, the UI, and starts the event loop.        |
| `app/core/`                      | **The Backbone.** Contains the `ApplicationCore` (DI container), `async_bridge`, `config`, and `Result` pattern. |
| `app/models/`                    | **Persistence Layer.** Defines all SQLAlchemy ORM models, mirroring the database tables.               |
| `app/services/`                  | **Data Access Layer.** Implements the Repository pattern; contains all database query logic.         |
| `app/business_logic/managers/`   | **Business Logic Layer.** Orchestrates workflows, enforces business rules, and makes decisions.        |
| `app/business_logic/dto/`        | **Data Contracts.** Pydantic models that define the structure of data passed between layers.           |
| `app/ui/views/`                  | **Main UI Screens.** The primary user-facing views like the POS screen, inventory, and settings panels. |
| `app/ui/dialogs/`                | **Interactive Dialogs.** Contains dialog windows for specific operations like making a payment or a PO. |

---

## **5. Technology Stack**

This project uses a modern, professional-grade technology stack.

| Category          | Technology                                         | Rationale                                                                                                   |
| ----------------- | -------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| **Language**      | Python 3.11+                                       | Modern features, performance improvements, and strong ecosystem.                                            |
| **GUI Framework** | PySide6 (Qt 6)                                     | The gold standard for professional, high-performance, cross-platform desktop applications in Python.        |
| **Database**      | PostgreSQL 16+                                     | Unmatched reliability, scalability, and feature set for handling critical business and financial data.      |
| **ORM**           | SQLAlchemy 2.0                                     | Industry-leading Object-Relational Mapper with powerful features and excellent async support.               |
| **DB Migrations** | Alembic                                            | The standard for managing database schema changes with SQLAlchemy.                                          |
| **Async**         | `asyncio`                                          | Python's native library for writing concurrent code, essential for a responsive application.                |
| **Testing**       | `pytest`, `pytest-qt`, `pytest-asyncio`            | A powerful and flexible testing ecosystem that covers all aspects of our application (core, UI, async).      |
| **Packaging**     | Poetry                                             | Modern, reliable dependency management and packaging that guarantees reproducible environments.             |
| **Code Quality**  | Black (Formatter), Ruff (Linter), MyPy (Type Checker)| A trifecta of tools to enforce code style, catch bugs early, and ensure long-term maintainability.          |

---

## **6. Developer Setup & Deployment Guide**

This guide provides step-by-step instructions to set up a complete local development environment.

### Prerequisites

*   **Git:** For version control.
*   **Python 3.11+:** Make sure it's installed and available in your `PATH`.
*   **Poetry:** For managing dependencies. See the [official installation guide](https://python-poetry.org/docs/#installation).
*   **Docker & Docker Compose:** To run the PostgreSQL database locally without needing to install it on your system.

### Step-by-Step Setup Guide

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/your-org/sg-pos-system.git
    cd sg-pos-system
    ```

2.  **Configure Environment Variables**
    Copy the example environment file. No changes are needed for a standard local setup.
    ```bash
    cp .env.example .env.dev
    ```

3.  **Start the Database Server**
    This command downloads the PostgreSQL image (if not present) and starts the database container in the background.
    ```bash
    docker compose -f docker-compose.dev.yml up -d
    ```
    You can check if the database is ready by running `docker logs sgpos_dev_db`.

4.  **Install Project Dependencies**
    Poetry will read the `pyproject.toml` file, create a virtual environment, and install all necessary production and development packages.
    ```bash
    poetry install
    ```

5.  **Activate the Virtual Environment**
    All subsequent commands must be run inside this environment to use the installed packages.
    ```bash
    poetry shell
    ```

6.  **Run Database Migrations**
    This command connects to the database and creates all the tables defined in `app/models`.
    ```bash
    alembic upgrade head
    ```

7.  **Run the Application**
    You are now ready to launch the POS system.
    ```bash
    python app/main.py
    ```

---

## **7. User Guide: Running the Application**

Once the application is running, here is a brief guide on how to use it:

*   **Main Window:** The application opens to the main `POSView`, ready for a sale.
*   **Navigation:** Use the menu bar at the top of the window (`File`, `POS`, `Data Management`, `Inventory`, etc.) to switch between different sections of the application.
*   **Making a Sale:**
    1.  In the `POSView`, use the "Product" search bar on the right to find an item by its SKU.
    2.  Click "Add to Cart". The item will appear in the "Current Sale Items" list on the left.
    3.  When all items are added, click the green "PAY" button.
    4.  In the `PaymentDialog`, add one or more payment methods until the balance is zero.
    5.  Click "Finalize Sale" to complete the transaction.
*   **Managing Data:** Navigate to `Data Management > Customers` or `Inventory > Current Stock` to view, add, and edit data. Most views follow a similar pattern of a search bar, an action button (`Add`, `Edit`), and a table displaying the data.

---

## **8. Project Roadmap**

### Immediate Goals (v1.0.1)

These tasks focus on fixing bugs, completing existing features, and improving developer experience.

*   [ ] **Fix Product Dialog:** Implement the asynchronous save logic in `app/ui/dialogs/product_dialog.py`.
*   [ ] **Complete User Roles:** Implement the role assignment logic in `app/business_logic/managers/user_manager.py`.
*   [ ] **Implement Product View:** Build a functional `QAbstractTableModel` and data loading logic for `app/ui/views/product_view.py`.
*   [ ] **Align Database Migrations:** Correct the initial Alembic migration file to match the latest ORM models, especially in `journal_entries`.
*   [ ] **Create Contribution Docs:** Write the `CONTRIBUTING.md` and `CODE_OF_CONDUCT.md` files.

### Long-Term Goals (v1.1+)

These are larger features that build on the stable foundation.

*   [ ] **Advanced Promotions Module:** Implement logic for complex discounts (e.g., "Buy One Get One", tiered discounts).
*   [ ] **Multi-Location Inventory:** Build features for transferring stock between different outlets.
*   [ ] **Accounting Integration:** Add functionality to export sales and purchase data to formats compatible with Xero and QuickBooks.
*   [ ] **E-commerce Connector:** Develop an integration with Shopify to sync products and inventory levels.
*   [ ] **Cloud Backend (v2.0):** Architect a cloud-based version of the backend to support a mobile companion app and centralized data management for multi-outlet businesses.

---

## **9. How to Contribute**

We welcome contributions from the community! Whether you're fixing a bug, adding a new feature, or improving documentation, your help is valued.

**Our contribution workflow is simple:**

1.  **Find an issue:** Look for issues tagged with `good first issue` or `help wanted` on our GitHub Issues page.
2.  **Fork the repository:** Create your own copy of the project.
3.  **Create a feature branch:** `git checkout -b feature/your-awesome-feature`.
4.  **Make your changes:** Write your code and make sure to add corresponding tests.
5.  **Run all checks:** Before pushing, ensure your code passes all quality checks: `pytest`, `black .`, `ruff .`, `mypy app`.
6.  **Submit a Pull Request (PR):** Push your branch to your fork and open a PR against our `main` branch.
7.  **Code Review:** Your PR will be reviewed by the maintainers.

*(A detailed CONTRIBUTING.md file is in the repo).*

---

## **10. License**

This project is licensed under the **MIT License**. See the `LICENSE` file for full details. You are free to use, modify, and distribute this software, but it is provided "as is" without warranty.
