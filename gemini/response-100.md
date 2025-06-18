<think>
The user wants me to create a complete, updated replacement for the `README.md` file.

This is a documentation generation task, similar to the previous one, but focused on the primary, user-facing `README.md`. It needs to be comprehensive, accurate, and self-contained. I must synthesize information from my previous analyses and the provided draft README into a new, polished document.

**Constraint Checklist & Confidence Score:**
1.  **Complete updated replacement for `README.md`**: Yes. This is the main goal.
2.  **Describe current codebase accurately**: Yes. My recent analysis makes me well-prepared for this.
3.  **Add/update section for file hierarchy**: Yes. I have this information ready.
4.  **Add/update section for flowchart diagram**: Yes. The Mermaid diagram I created before will be perfect here.
5.  **Add/update section to list and describe files**: Yes. I will expand on the file hierarchy section.
6.  **Add/update section for current features and roadmap**: Yes. I have a clear understanding of what's working, what's a placeholder, and what the logical next steps are. I will create a detailed list.
7.  **Add/update clear and detailed deployment guide**: Yes. I need to write this from scratch, covering both the application setup and the Docker database setup, starting from a `git clone`.
8.  **Add/update user guide section**: Yes. I'll provide a step-by-step guide on how to perform key actions in the running application.
9.  **Fill in details from the draft**: Yes, I will use the draft as a base for structure and tone, but replace/update its content to be accurate.
10. **Self-contained document**: Yes. No "see other document" references.
11. **No references to older versions**: Yes.
12. **Describe recent code changes**: I'll frame the "Current Features & Status" section to implicitly reflect the most recent state of the code I've analyzed. For example, instead of saying "a change was made", I'll describe the feature as it currently exists.

**Mental Sandbox/Simulation:**

*   **Structure of the new `README.md`**: I'll follow a logical flow for a project README.
    1.  **Header**: Logo, title, tagline, badges. I can reuse this from the draft.
    2.  **Table of Contents**: Essential for a long README.
    3.  **Introduction**: What is SG-POS? High-level pitch. (From draft, refined).
    4.  **Current Features & Status**: A detailed table showing what's functional, partially implemented, or a placeholder. This addresses the "describe recent changes" point by reflecting the *current* state.
    5.  **Architectural Deep Dive**:
        *   Briefly explain the layered architecture philosophy.
        *   **Module Interaction Flowchart**: Embed the Mermaid diagram and explain it. This covers user request #2.
    6.  **Codebase Deep Dive**:
        *   **Project File Hierarchy**: Show the tree structure. This covers user request #1.
        *   **Key File & Directory Descriptions**: A detailed list explaining the purpose of each major file/folder. This covers user request #3.
    7.  **Technology Stack**: A table listing the tech used. (From draft, validated).
    8.  **Developer Setup & Deployment Guide**: This will be a major section. I'll write clear, numbered steps. This covers user request #5.
        *   Prerequisites (Git, Python, Poetry, Docker).
        *   Step 1: Clone.
        *   Step 2: Configure Environment (`.env.dev`).
        *   Step 3: Start Database (Docker).
        *   Step 4: Install Dependencies (Poetry).
        *   Step 5: Run Migrations (Alembic).
        *   Step 6: Run Application.
    9.  **User Guide**: This is also a major section, aimed at a non-developer running the app. This covers user request #6.
        *   How to launch the app.
        *   Navigating the UI.
        *   Detailed steps for key workflows:
            *   Making a sale.
            *   Adding a customer.
            *   Performing a stock adjustment.
            *   Creating a Purchase Order.
            *   Viewing a report.
    10. **Project Roadmap**: Divided into "Immediate Goals" and "Long-Term Goals". This covers user request #4.
    11. **How to Contribute**: A call to action for other developers. (From draft, refined).
    12. **License**: Standard MIT license section. (From draft, validated).

*   **Content Generation Strategy**:
    *   **Reuse and Refine**: I'll take the validated parts from the draft (`Introduction`, `Tech Stack`, `License`) and my previous `Code Review` document (`Architecture`, `Flowchart`, `File Hierarchy`, `Roadmap ideas`).
    *   **Expand and Detail**: The "Deployment Guide" and "User Guide" sections need to be written with a fresh perspective, assuming the reader has just cloned the repo. I'll make the steps explicit and easy to follow.
    *   **Accuracy Check**: For the "Current Features & Status" section, I'll draw directly from my detailed findings. For example, I'll list "User Management" as functional because the UI dialogs and backend manager are now correctly implemented, while "Product Management" will be listed as partially functional since the UI view isn't complete.
    *   **Self-Contained**: I will ensure all information is present within this single file. Instead of saying "The architecture is layered", I'll briefly explain *what* the layers are.

*   **Final Polish**: After generating the content, I'll review it for clarity, flow, and formatting. Markdown tables, code blocks, and headings will be crucial for readability. The tone should be professional, welcoming, and informative.

This plan covers all user requirements comprehensively. I am confident I can produce a high-quality, complete, and accurate `README.md` file.Of course. I have synthesized my detailed analysis of the entire codebase into a complete and accurate replacement for the `README.md` file. This new version reflects the current state of the project, incorporates all the requested sections, and is structured to be a comprehensive, self-contained guide for developers and users alike.

Here is the complete replacement `README.md` file.

***

# README.md

```md
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
    <img src="https://img.shields.io/badge/Status-Active%20Development-green" alt="Project Status">
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
    *   [Immediate Goals](#immediate-goals)
    *   [Long-Term Goals](#long-term-goals)
*   [9. How to Contribute](#9-how-to-contribute)
*   [10. License](#10-license)

---

## **1. Introduction: What is SG-POS?**

**SG-POS** is a free and open-source Point-of-Sale system, engineered from the ground up to address the specific operational and regulatory challenges faced by Small to Medium-sized Businesses (SMBs) in Singapore. It aims to provide the power and polish of expensive enterprise systems in an accessible, modern, and maintainable package.

This project is built with an obsessive focus on quality, both in the user experience and, most importantly, in the engineering. It serves not only as a functional tool but also as a reference implementation for professional-grade Python application architecture, featuring a non-blocking UI, a clean, layered design, and robust data integrity practices.

---

## **2. Current Features & Status**

The application is in a state of active development. The core architecture is stable and robust, and many key workflows are fully implemented and functional.

| Feature Area                      | Status                  | Notes                                                                                                                              |
| --------------------------------- | ----------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| **Sales & Checkout**              | ✅ **Functional**       | Core sales processing, cart management, split-tender payment collection, and receipt data generation are fully working.                |
| **Customer Management**           | ✅ **Functional**       | Full CRUD (Create, Read, Update, Deactivate) operations for customers are implemented via the `CustomerView` and `CustomerDialog`.     |
| **User & Role Management**        | ✅ **Functional**       | `SettingsView` provides full CRUD operations for users, including multi-role assignment via a dedicated `UserDialog`.                    |
| **Inventory Management**          | ✅ **Functional**       | `InventoryView` provides a live stock summary, stock movement history, and filtering capabilities. Stock adjustments are fully functional. |
| **Purchase Orders**               | ✅ **Functional**       | Creation of new Purchase Orders via the `PurchaseOrderDialog` is fully implemented, including supplier and product lookups.            |
| **Reporting & Analytics**         | ✅ **Functional**       | The backend `ReportingManager` and `GstManager` correctly generate data for all implemented reports (Sales, GST, Inventory Valuation). |
| **Product Management**            | 🟡 **Partially Implemented** | Full backend logic and a `ProductDialog` for creating/editing products are functional. The main `ProductView` table is not yet implemented. |
| **Company Information**           | 🟡 **Partially Implemented** | The UI for viewing/editing company info exists in `SettingsView`, but the save logic is not yet implemented.                     |
| **Stock Receiving**               | 🔴 **Placeholder**      | The UI button for receiving items against a Purchase Order exists but is not yet functional.                                       |
| **Report Exporting**              | 🔴 **Placeholder**      | UI buttons for exporting reports to PDF/CSV exist but are not yet functional.                                                    |

---

## **3. Architectural Deep Dive**

SG-POS is built on a set of robust architectural principles designed for maintainability, testability, and scalability.

### The Layered Architecture

Our architecture strictly separates the application into four logical layers, ensuring that each part of the codebase has a single, well-defined responsibility:

1.  **Presentation Layer (`app/ui`):** Built with PySide6, this layer is responsible *only* for what the user sees and how they interact with it. It contains no business logic.
2.  **Business Logic Layer (`app/business_logic`):** The brain of the application. **Managers** orchestrate workflows and enforce business rules, using **DTOs** (Data Transfer Objects) as data contracts.
3.  **Data Access Layer (`app/services`):** Implements the Repository Pattern. It provides a clean, abstract API for all database operations, hiding SQL complexity.
4.  **Persistence Layer (`app/models`):** Defines the database schema using SQLAlchemy ORM models, which map directly to PostgreSQL tables.

### Module Interaction Flowchart

The flow of control and data is unidirectional and decoupled, ensuring a responsive UI and testable components. The `ApplicationCore` acts as a Dependency Injection (DI) container, providing services and managers to the components that need them.

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

---

## **4. Codebase Deep Dive**

A well-organized file structure is paramount for navigating and maintaining a complex codebase. The SG-POS project adheres to a standard, logical layout that reinforces the architectural layers.

### Project File Hierarchy

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
│   ├── business_logic/       # Business Logic Layer: The "brains" of the app
│   ├── models/               # Persistence Layer: SQLAlchemy ORM models
│   ├── services/             # Data Access Layer (Repository Pattern)
│   └── ui/                   # Presentation Layer: All GUI components (PySide6)
│
├── migrations/               # Stores Alembic-generated database migration scripts
│
├── scripts/
│   └── database/
│       ├── schema.sql          # The complete, hand-written SQL schema (source of truth)
│
└── tests/                    # Contains all unit, integration, and UI tests
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
| `app/ui/dialogs/`                | **Interactive Dialogs.** Contains dialog windows for specific operations like making a payment or adding a user. |
| `scripts/database/schema.sql`    | **Schema Source of Truth.** A complete, readable SQL script defining the entire database structure.      |

---

## **5. Technology Stack**

This project uses a modern, professional-grade technology stack chosen for performance, reliability, and developer productivity.

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

This guide provides step-by-step instructions to set up a complete local development environment for the SG-POS application.

### Prerequisites

*   **Git:** For version control. [Install Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git).
*   **Python 3.11+:** Make sure it's installed and available in your system's `PATH`. [Install Python](https://www.python.org/downloads/).
*   **Poetry:** For managing dependencies. See the [official installation guide](https://python-poetry.org/docs/#installation).
*   **Docker & Docker Compose:** To run the PostgreSQL database in a container. [Install Docker Desktop](https://www.docker.com/products/docker-desktop/).

### Step-by-Step Setup Guide

#### **Step 1: Clone the Repository**
Open your terminal or command prompt and clone the project from GitHub.

```bash
git clone https://github.com/your-org/sg-pos-system.git
cd sg-pos-system
```

#### **Step 2: Configure Environment Variables**
The application uses a `.env.dev` file for local configuration. You can create one by copying the provided template. The default values are suitable for local development and match the Docker configuration.

```bash
cp .env.example .env.dev
```

#### **Step 3: Start the Database Server**
This command will download the PostgreSQL image (if not already present), create a container named `sgpos_dev_db`, and run it in the background. The database will be accessible on `localhost:5432`.

```bash
docker compose -f docker-compose.dev.yml up -d
```
*   **To check if the database is running:** `docker ps` (You should see `sgpos_dev_db`).
*   **To view logs:** `docker logs sgpos_dev_db`.
*   **To stop the database:** `docker compose -f docker-compose.dev.yml down`.

#### **Step 4: Install Project Dependencies**
Poetry will read the `pyproject.toml` file, create a dedicated virtual environment for the project, and install all necessary production and development packages.

```bash
poetry install
```

#### **Step 5: Activate the Virtual Environment**
To run the application or any project-specific commands, you must first activate the virtual environment created by Poetry.

```bash
poetry shell
```
Your terminal prompt should now indicate that you are inside the project's virtual environment.

#### **Step 6: Run Database Migrations**
This crucial step connects to the running Docker database and creates all the necessary tables and relationships defined in the `app/models` directory.

```bash
alembic upgrade head
```
You should see output from Alembic indicating that it is applying the migrations.

#### **Step 7: Run the Application**
With the database running and dependencies installed, you are now ready to launch the SG-POS system.

```bash
python app/main.py
```
The main application window should appear on your screen.

---

## **7. User Guide: Running the Application**

Once the application is running, here is a brief guide on how to perform common tasks.

*   **Main Window & Navigation:** The application opens to the main `POSView`, ready for a sale. Use the menu bar at the top of the window (`File`, `POS`, `Data Management`, `Inventory`, etc.) to switch between the different sections of the application.

*   **Making a Sale:**
    1.  In the `POSView`, use the **Product** search bar on the right to find an item by its SKU or name.
    2.  Click **"Add to Cart"**. The item will appear in the "Current Sale Items" list on the left. You can double-click the quantity in the table to change it.
    3.  When all items are added, click the large green **"PAY"** button.
    4.  In the `PaymentDialog`, select a payment method, enter an amount, and click **"Add Payment"**. Repeat for split-tender payments.
    5.  Once the "Balance" is zero or less, click **"Finalize Sale"** to complete the transaction.

*   **Managing Customers:**
    1.  Navigate to `Data Management > Customers`.
    2.  Click **"Add New Customer"** to open a dialog for creating a new customer.
    3.  Select a customer from the table and click **"Edit Selected"** to update their details.
    4.  Use the search bar at the top to filter the customer list.

*   **Managing Users:**
    1.  Navigate to `Settings > Application Settings` and go to the "User Management" tab.
    2.  Click **"Add New User"** to open a dialog where you can set their username, password, and assign one or more roles.
    3.  Select a user and click **"Edit Selected User"** to modify their details.

*   **Performing a Stock Adjustment:**
    1.  Navigate to `Inventory > Stock Management`.
    2.  Click the **"Adjust Stock"** button.
    3.  In the dialog, search for products to add them to the adjustment list.
    4.  Enter the physically counted quantity in the "Counted Quantity" column for each item. The variance will be calculated automatically.
    5.  Add a reason for the adjustment in the notes box and click **"Submit Adjustment"**.

---

## **8. Project Roadmap**

### Immediate Goals

These tasks focus on fixing bugs, completing existing features, and improving developer experience.

*   [ ] **Complete Product View:** Implement a functional `QAbstractTableModel` and data loading logic for `app/ui/views/product_view.py` to display the product catalog.
*   [ ] **Implement Stock Receiving:** Build the UI and backend logic to receive items against an existing Purchase Order, automatically updating stock levels.
*   [ ] **Implement Report Exporting:** Add functionality to the "Export PDF" and "Export CSV" buttons in the `ReportsView` using libraries like `reportlab` and `openpyxl`.
*   [ ] **Implement Company Info Saving:** Connect the "Save Company Information" button in `SettingsView` to a `CompanyManager` method to persist changes.
*   [ ] **Enhance Test Coverage:** Increase unit and integration test coverage, especially for the business logic managers.
*   [ ] **Create Contribution Docs:** Finalize and polish the `CONTRIBUTING.md` and `CODE_OF_CONDUCT.md` files.

### Long-Term Goals

These are larger features that build on the stable foundation.

*   [ ] **Advanced Promotions Module:** Implement logic for complex discounts (e.g., "Buy One Get One", tiered discounts, customer-group-specific pricing).
*   [ ] **Multi-Location Inventory:** Build features for transferring stock between different outlets, including transfer orders and in-transit tracking.
*   [ ] **Accounting Integration:** Add functionality to export sales and purchase data to formats compatible with common accounting software like Xero and QuickBooks.
*   [ ] **E-commerce Connector:** Develop an integration with platforms like Shopify or WooCommerce to sync products, orders, and inventory levels.
*   [ ] **Cloud Backend (v2.0):** Architect a cloud-based version of the backend to support a mobile companion app, web-based reporting dashboard, and centralized data management for multi-outlet businesses.

---

## **9. How to Contribute**

We welcome contributions from the community! Whether you're fixing a bug, adding a new feature, or improving documentation, your help is valued.

**Our contribution workflow is simple:**

1.  **Find an issue:** Look for issues tagged with `good first issue` or `help wanted` on our GitHub Issues page.
2.  **Fork the repository:** Create your own copy of the project.
3.  **Create a feature branch:** `git checkout -b feature/your-awesome-feature`.
4.  **Make your changes:** Write your code and make sure to add corresponding tests.
5.  **Run all checks:** Before pushing, ensure your code passes all quality checks: `pytest`, `black .`, `ruff . --fix`, `mypy app`.
6.  **Submit a Pull Request (PR):** Push your branch to your fork and open a PR against our `main` branch.
7.  **Code Review:** Your PR will be reviewed by the maintainers.

*(A detailed CONTRIBUTING.md file is in the repo).*

---

## **10. License**

This project is licensed under the **MIT License**. See the `LICENSE` file for full details. You are free to use, modify, and distribute this software, but it is provided "as is" without warranty.
```

---
https://drive.google.com/file/d/1dnSP22Pzt3sjhTNHJcPpvKoihYG-somP/view?usp=sharing, https://aistudio.google.com/app/prompts?state=%7B%22ids%22:%5B%221fo0QcoydHcYD6h_b6-9HapceFSj7xnKT%22%5D,%22action%22:%22open%22,%22userId%22:%22108686197475781557359%22,%22resourceKeys%22:%7B%7D%7D&usp=sharing, https://drive.google.com/file/d/1koyl7FAKLkppdi5iIUCwrJtbPLgb6YGM/view?usp=sharing

