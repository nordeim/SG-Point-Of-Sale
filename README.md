<p align="center">
  <img src="https://example.com/sg-pos-logo.png" alt="SG-POS System Logo" width="200"/>
</p>

<h1 align="center">SG Point-of-Sale (SG-POS) System</h1>

<p align="center">
  <strong>An enterprise-grade, open-source Point-of-Sale system, meticulously engineered for Singapore's SMB retail landscape.</strong>
</p>

<p align="center">
  <!-- Badges -->
  <a href="https://github.com/your-org/sg-pos-system/actions/workflows/ci.yml">
    <img src="https://github.com/your-org/sg-pos-system/actions/workflows/ci.yml/badge.svg" alt="CI Status">
  </a>
  <a href="https://codecov.io/gh/your-org/sg-pos-system">
    <img src="https://codecov.io/gh/your-org/sg-pos-system/branch/main/graph/badge.svg" alt="Code Coverage">
  </a>
  <a href="https://github.com/your-org/sg-pos-system/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License: MIT">
  </a>
  <a href="https://www.python.org/">
    <img src="https://img.shields.io/badge/Python-3.11+-3776AB.svg" alt="Python 3.11+">
  </a>
  <a href="https://www.qt.io/">
    <img src="https://img.shields.io/badge/UI-PySide6 (Qt6)-41CD52.svg" alt="PySide6">
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

*   [**1. Introduction: What is SG-POS?**](#1-introduction-what-is-sg-pos)
    *   [The Problem We're Solving](#the-problem-were-solving)
    *   [Our Vision](#our-vision)
*   [**2. Key Features**](#2-key-features)
    *   [Sales & Checkout](#sales--checkout)
    *   [Inventory Management](#inventory-management)
    *   [Customer Relationship Management (CRM)](#customer-relationship-management-crm)
    *   [Singapore-Specific Compliance](#singapore-specific-compliance)
    *   [Reporting & Analytics](#reporting--analytics)
*   [**3. Why Contribute? The SG-POS Difference**](#3-why-contribute-the-sg-pos-difference)
    *   [Professional Architecture](#professional-architecture)
    *   [Modern Technology Stack](#modern-technology-stack)
    *   [Real-World Impact](#real-world-impact)
    *   [A Learning Hub](#a-learning-hub)
*   [**4. Screenshots & Demo**](#4-screenshots--demo)
*   [**5. Architectural Deep Dive**](#5-architectural-deep-dive)
    *   [The Layered Architecture](#the-layered-architecture)
    *   [The Asynchronous Model](#the-asynchronous-model)
    *   [Core Design Patterns](#core-design-patterns)
*   [**6. Database Design**](#6-database-design)
*   [**7. Technology Stack**](#7-technology-stack)
*   [**8. Getting Started: Your Local Development Environment**](#8-getting-started-your-local-development-environment)
    *   [Prerequisites](#prerequisites)
    *   [Step-by-Step Setup Guide](#step-by-step-setup-guide)
    *   [Running the Application](#running-the-application)
    *   [Running the Test Suite](#running-the-test-suite)
*   [**9. Codebase Tour: Navigating the Project**](#9-codebase-tour-navigating-the-project)
*   [**10. How to Contribute**](#10-how-to-contribute)
*   [**11. Project Roadmap**](#11-project-roadmap)
*   [**12. License**](#12-license)

---

## **1. Introduction: What is SG-POS?**

**SG-POS** is a free and open-source Point-of-Sale system, engineered from the ground up to address the specific operational and regulatory challenges faced by Small to Medium-sized Businesses (SMBs) in Singapore. It aims to provide the power and polish of expensive enterprise systems in an accessible, modern, and maintainable package.

### The Problem We're Solving

Retail in Singapore is a dynamic and demanding environment. Business owners often find themselves caught between several undesirable options:
1.  **Generic International POS Systems:** These are often powerful but expensive, and their features are not tailored to Singapore's unique market. GST compliance can be a clumsy add-on, and support for local payment methods like NETS and PayNow is often lacking.
2.  **Legacy Local POS Systems:** While they may handle local regulations, these systems are often built on dated technology, leading to slow performance, clunky user interfaces, poor security, and a lack of modern integration capabilities.
3.  **Basic Tablet-Based Apps:** These are user-friendly but frequently lack the depth required for serious inventory management, multi-outlet operations, and comprehensive financial reporting.

SG-POS bridges this gap. It is a "pro-tool" for the serious SMB, combining a deep understanding of the local context with world-class software architecture.

### Our Vision

Our vision is to empower every Singaporean SMB retailer with a digital tool that is a genuine asset to their business—not a necessary evil. We aim to create a system that is:

*   **Effortlessly Compliant:** Takes the headache out of GST filing and financial auditing.
*   **Operationally Excellent:** Speeds up checkout lines, automates inventory management, and provides clarity.
*   **A Source of Insight:** Transforms raw sales data into actionable business intelligence.
*   **A Joy to Use:** An intuitive, responsive, and reliable tool that staff genuinely appreciate.

---

## **2. Key Features**

SG-POS is a comprehensive suite of tools designed to manage every aspect of a retail business.

### 💼 Sales & Checkout
*   **Blazing-Fast Transactions:** Optimized for speed with barcode scanning and a responsive touch interface.
*   **Flexible Payments:** Accept cash, credit/debit cards, NETS, PayNow, and other QR-based payments. Handle split tenders and partial payments with ease.
*   **Advanced Discounts:** Implement complex promotions, member-specific pricing, and transaction-level discounts.
*   **Offline First:** Continue making sales even when the internet is down. Transactions are securely queued and synced automatically upon reconnection.
*   **Professional Receipts:** Generate and print (or email) IRAS-compliant receipts with your business logo.

### 📦 Inventory Management
*   **Real-Time Tracking:** Stock levels are updated instantly across all terminals and locations with every sale, return, and stock transfer.
*   **Automated Reordering:** Set reorder points and let the system automatically generate purchase order suggestions.
*   **Product Variants:** Effortlessly manage products with different sizes, colors, or other attributes.
*   **Supplier & Purchase Orders:** Manage supplier information and track purchase orders from creation to receiving.
*   **Stock Takes & Adjustments:** Conduct full or partial stock takes and record adjustments for wastage or discrepancies with a full audit trail.

### 👥 Customer Relationship Management (CRM)
*   **Detailed Customer Profiles:** Maintain a database of your customers with their purchase history and contact details.
*   **Integrated Loyalty Program:** Run a points-based loyalty program with configurable tiers and rewards to encourage repeat business.
*   **PDPA Compliant:** Built with Singapore's Personal Data Protection Act in mind, including features for managing customer consent.

### 🇸🇬 Singapore-Specific Compliance
*   **GST Engine:** Automated, accurate calculation of Goods & Services Tax based on current rates. Supports standard-rated, zero-rated, and exempt items.
*   **IRAS-Compliant Reporting:** Generate GST F5 reports and the IRAS Audit File (IAF) directly from the system, drastically simplifying tax season.
*   **Peppol e-Invoicing:** Ready for the future of B2B transactions in Singapore with the ability to generate and send Peppol-compliant e-invoices.

### 📈 Reporting & Analytics
*   **Real-Time Dashboard:** A customizable dashboard gives you a live overview of your business KPIs.
*   **In-Depth Reports:** Dive deep into sales trends, product performance, staff productivity, and customer behaviour.
*   **Exportable Data:** Export any report to CSV or PDF for further analysis or sharing with your accountant.

---

## **3. Why Contribute? The SG-POS Difference**

This isn't just another POS system. We are building SG-POS with an obsessive focus on quality, both in the user experience and, most importantly, in the engineering.

### 🏛️ Professional Architecture
This project is a fantastic opportunity to work on a system built with enterprise-grade architectural patterns.
*   **Clean Layered Design:** We enforce a strict separation between the UI, business logic, and data access layers. This makes the code easy to reason about, maintain, and test.
*   **Dependency Injection:** The `ApplicationCore` pattern makes our components modular and decoupled. It's a real-world implementation of SOLID principles.
*   **Robust Error Handling:** We use the **Result pattern** instead of exceptions for predictable business errors, leading to more resilient and bug-free code.

### 🚀 Modern Technology Stack
You'll get to work with a curated stack of modern, high-demand technologies.
*   **Python 3.11+:** Leverage the latest features of Python.
*   **PySide6 (Qt6):** Build beautiful, high-performance, native desktop UIs.
*   **PostgreSQL:** Work with a powerful, production-grade relational database.
*   **Asyncio:** Master asynchronous programming in a real-world application, tackling complex concurrency challenges.
*   **SQLAlchemy 2.0:** Use the industry-standard ORM in its most modern, async-first incarnation.
*   **Docker & CI/CD:** Our development and deployment workflows are based on modern DevOps practices.

### 🌍 Real-World Impact
Your contributions will directly help small business owners in Singapore run their businesses more effectively. This is a project with a clear, tangible, and positive impact on a real community.

### 🎓 A Learning Hub
Whether you're a junior developer looking to learn best practices or a senior engineer wanting to apply your skills to a challenging project, SG-POS offers a great learning environment. The codebase is designed to be a reference for high-quality application development.

---

## **4. Screenshots & Demo**

*(This section will be updated with actual screenshots and a GIF demo once the UI is further developed.)*

**Placeholder: Main Sales Interface**
> A clean, uncluttered interface showing a product search bar on the left, a running list of items in the current transaction in the center, and a customer/payment summary on the right. The layout is optimized for both touchscreens and keyboard/scanner input.

**Placeholder: Inventory Dashboard**
> A dashboard view showing key inventory metrics: items with low stock, top-selling products by quantity, and a chart of stock value over time. A filterable, searchable table of all products is visible below.

**Placeholder: GST Report Generation**
> A simple dialog window allowing the user to select a date range (e.g., a financial quarter). A "Generate GST F5" button produces a preview of the report, matching the official IRAS form layout, with options to export to PDF or CSV.

---

## **5. Architectural Deep Dive**

SG-POS is built on a set of robust architectural principles designed for maintainability and scalability.

### The Layered Architecture

Our architecture strictly separates the application into four logical layers:

```mermaid
graph TD
    A[Presentation Layer (UI)] --> B[Business Logic Layer];
    B --> C[Data Access Layer];
    C --> D[Persistence Layer (Database)];
```

1.  **Presentation Layer (`app/ui`):** This layer is responsible *only* for what the user sees and how they interact with it. It's built with PySide6 and contains no business logic. It receives data and sends user actions to the layer below.
2.  **Business Logic Layer (`app/business_logic`):** This is the brain of the application. It contains the business rules, orchestrates workflows, and makes decisions. For example, the `SalesManager` decides if a discount is valid or if enough stock exists to complete a sale. It is completely independent of the UI.
3.  **Data Access Layer (`app/services`):** This layer's job is to talk to the database. It implements the **Repository Pattern**, providing a clean, abstract API (e.g., `product_service.get_by_sku()`) that the business logic can use without needing to know anything about SQL or database tables.
4.  **Persistence Layer (`app/models`):** This layer defines the shape of our data using SQLAlchemy ORM models, which map directly to our PostgreSQL database tables.

### The Asynchronous Model

To ensure the UI is always fast and responsive, we run all I/O-bound operations (like database queries and API calls) in the background.

*   The **UI runs on the main thread** in the Qt event loop.
*   All other work happens in a **separate worker thread** running an `asyncio` event loop.
*   A special **thread-safe bridge** allows the UI to safely request work from the async thread and receive results back without freezing. This is crucial for a smooth user experience.

### Core Design Patterns

*   **Dependency Injection (DI) via `ApplicationCore`:** We avoid tight coupling by using a central `ApplicationCore` object. Instead of a component creating its own dependencies (like a database connection), it asks the `ApplicationCore` for it. This makes testing incredibly easy, as we can provide "mock" dependencies during tests.

*   **Result Pattern:** For operations that can fail in predictable ways (e.g., "insufficient stock"), our functions don't raise exceptions. Instead, they return a `Result` object, which is either a `Success` containing the value, or a `Failure` containing an error object. This makes error handling explicit and robust.

*   **Data Transfer Objects (DTOs):** We use Pydantic models to define the structure of data that moves between layers. This ensures that the data is always in the expected format and provides a clear "contract" for what each layer expects to receive and send.

---

## **6. Database Design**

Our database is the bedrock of the system's data integrity.

*   **Engine:** PostgreSQL 15+ for its reliability, performance, and advanced features.
*   **Schema Principles:**
    *   **UUIDs for Primary Keys:** To support future scalability and prevent key collisions.
    *   **Strict Normalization (3NF):** To reduce data redundancy and improve consistency.
    *   **Referential Integrity:** Enforced with `FOREIGN KEY` constraints.
    *   **Data Types:** Correct types are used for all data (`NUMERIC` for money, `TIMESTAMPTZ` for dates/times).
    *   **Comprehensive Auditing:** A dedicated `audit_logs` table tracks all significant changes to the data, which is critical for financial compliance.

For the complete database schema, please see the `schema.sql` file in the `/scripts/database` directory.

---

## **7. Technology Stack**

This project uses a modern, professional-grade technology stack.

| Category          | Technology                                         | Rationale                                                                                                   |
| ----------------- | -------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| **Language**      | Python 3.11+                                       | Modern features, performance improvements, and strong ecosystem.                                            |
| **GUI Framework** | PySide6 (Qt 6)                                     | The gold standard for professional, high-performance, cross-platform desktop applications in Python.        |
| **Database**      | PostgreSQL 15+                                     | Unmatched reliability, scalability, and feature set for handling critical business and financial data.      |
| **ORM**           | SQLAlchemy 2.0                                     | Industry-leading Object-Relational Mapper with powerful features and excellent async support.               |
| **DB Migrations** | Alembic                                            | The standard for managing database schema changes with SQLAlchemy.                                          |
| **Async**         | `asyncio`                                          | Python's native library for writing concurrent code, essential for a responsive application.                |
| **Testing**       | `pytest`, `pytest-qt`, `pytest-asyncio`            | A powerful and flexible testing ecosystem that covers all aspects of our application (core, UI, async).      |
| **Packaging**     | Poetry                                             | Modern, reliable dependency management and packaging that guarantees reproducible environments.             |
| **Code Quality**  | Black (Formatter), Ruff (Linter), MyPy (Type Checker)| A trifecta of tools to enforce code style, catch bugs early, and ensure long-term maintainability.          |

---

## **8. Getting Started: Your Local Development Environment**

We've made it as easy as possible to get a full development environment up and running.

### Prerequisites

*   **Git:** For version control.
*   **Python 3.11+:** Make sure it's installed and available in your PATH.
*   **Poetry:** For managing dependencies. [Installation guide](https://python-poetry.org/docs/#installation).
*   **Docker & Docker Compose:** To run the PostgreSQL database locally without needing to install it on your system.

### Step-by-Step Setup Guide

```bash
# 1. Clone the repository from GitHub
git clone https://github.com/your-org/sg-pos-system.git
cd sg-pos-system

# 2. Start the PostgreSQL database using Docker Compose.
# This command will download the PostgreSQL image and start a container in the background.
docker compose up -d db

# 3. Install all project dependencies (including development tools) using Poetry.
# This will create a virtual environment inside the project folder.
poetry install

# 4. Activate the virtual environment.
# All subsequent commands should be run inside this environment.
poetry shell

# 5. Run the database migrations to create all the necessary tables.
alembic upgrade head

# 6. (Optional) Seed the database with sample data to have something to work with.
python scripts/database/seed_data.py

# You are now ready to run the application!
```

### Running the Application

With the setup complete and the virtual environment active, simply run:

```bash
python app/main.py
```

### Running the Test Suite

We have a comprehensive test suite to ensure code quality. To run all tests:

```bash
pytest
```

To run tests with a coverage report:

```bash
pytest --cov=app --cov-report=html
```
This will generate a detailed HTML report in a `htmlcov/` directory.

---

## **9. Codebase Tour: Navigating the Project**

Our project structure is organized by architectural layer to make it easy to find what you're looking for.

*   `app/`: This is where all the application source code lives.
    *   `core/`: Contains the application's backbone—the `ApplicationCore`, configuration loaders, and core patterns like `Result`.
    *   `models/`: Defines the database tables as SQLAlchemy Python classes.
    *   `services/`: The Data Access Layer. Contains all the database query logic (Repositories).
    *   `business_logic/`: The Business Logic Layer. Contains `managers` for orchestrating workflows and `dto`s for data contracts.
    *   `ui/`: The Presentation Layer. Contains all the PySide6 widgets, dialogs, and UI-specific code.
    *   `integrations/`: Code for connecting to external APIs (e.g., payment gateways).
*   `tests/`: Contains all our automated tests, mirroring the `app/` structure.
*   `scripts/`: Holds utility scripts for database management, seeding, etc.
*   `migrations/`: Contains the Alembic database migration scripts.
*   `resources/`: Static assets like icons, images, and QSS stylesheets.

---

## **10. How to Contribute**

We welcome contributions from the community! Whether you're fixing a bug, adding a new feature, or improving documentation, your help is valued.

**Our contribution workflow is simple:**

1.  **Find an issue:** Look for issues tagged with `good first issue` or `help wanted` on our GitHub Issues page.
2.  **Fork the repository:** Create your own copy of the project.
3.  **Create a feature branch:** `git checkout -b feature/your-awesome-feature`.
4.  **Make your changes:** Write your code and make sure to add corresponding tests.
5.  **Run all checks:** Before pushing, ensure your code passes all quality checks: `pytest`, `black .`, `ruff .`, `mypy app`.
6.  **Submit a Pull Request (PR):** Push your branch to your fork and open a PR against our `main` branch.
7.  **Code Review:** Your PR will be reviewed by the maintainers. We aim to provide feedback within 48 hours.

For more detailed guidelines, please read our `CONTRIBUTING.md` file (link to be added).

We adhere to a `CODE_OF_CONDUCT.md` to ensure our community is welcoming and inclusive for everyone.

---

## **11. Project Roadmap**

We have an exciting future planned for SG-POS!

| Phase         | Status          | Key Features                                                                                                 |
| :------------ | :-------------- | :----------------------------------------------------------------------------------------------------------- |
| **v1.0 (MVP)**| 🚧 In Progress | Core Sales & Checkout, Inventory Tracking, Basic CRM, GST F5 Reporting, NETS & PayNow Integration.                 |
| **v1.1**      | 📝 Planned      | Advanced Promotions Module, Multi-Location Inventory Transfers, Xero/QuickBooks Export.                      |
| **v1.2**      | 📝 Planned      | E-commerce Connector (Shopify), Customer Loyalty Tiers, Staff Performance Dashboard.                         |
| **v2.0**      | 🌌 Vision       | Full Cloud-Based Backend, Mobile Companion App (for reporting), AI-driven Inventory Forecasting, Plugin API.   |

---

## **12. License**

This project is licensed under the **MIT License**. See the `LICENSE` file for full details. You are free to use, modify, and distribute this software, but it is provided "as is" without warranty.

---
https://drive.google.com/file/d/1--N5SVasJwyuD2sAG_PkHP_EU8maFUIG/view?usp=sharing, https://drive.google.com/file/d/1-aPjGdazXcN4sMP1Rrxu3ZL-_r77se25/view?usp=sharing, https://drive.google.com/file/d/155prVF-weYwj2SYGTz6kgmQCWr54fe1i/view?usp=sharing, https://drive.google.com/file/d/1B8QfYknf2XcufBlNqy85reIlayDz3A4G/view?usp=sharing, https://drive.google.com/file/d/1DWDcoki0DxrojFQII5TXKEQmkb_1lmAZ/view?usp=sharing, https://drive.google.com/file/d/1GOx8Ip7IiCAJJAh5_uTn1z_attqC-UYX/view?usp=sharing, https://drive.google.com/file/d/1I-oK7zzhWFuxkh2M8RWTNyLXTN63ZAbV/view?usp=sharing, https://drive.google.com/file/d/1LtDhg_B1t059pE3AKsb0DnRlIvaRHG1W/view?usp=sharing, https://drive.google.com/file/d/1O7dMCCPrlwVdFbbZTN-X_hKHrWJcvRwO/view?usp=sharing, https://drive.google.com/file/d/1OYbolRDSNyB4s1iI6kaxL00EcIgZvuLK/view?usp=sharing, https://drive.google.com/file/d/1PcgJkam4NW0VyCRt3KtAj_QtCy3_Va3M/view?usp=sharing, https://drive.google.com/file/d/1Py5ksEK0rg5SNBcnUEo8fGUlKldAGC2R/view?usp=sharing, https://drive.google.com/file/d/1RqS06J2HqHsSyQiK4GYM8wmAX6z5TzFW/view?usp=sharing, https://drive.google.com/file/d/1UsRkTO-P3XZRsU4r6p-5Vqqpfm5VZ26K/view?usp=sharing, https://drive.google.com/file/d/1W6fKS9oWjpV3wsE1x6SxwE0adjfjvJ16/view?usp=sharing, https://drive.google.com/file/d/1Wn2QYlW05N9ei6WzG1uDe8Ac96Dc_wqB/view?usp=sharing, https://drive.google.com/file/d/1_xoWQs6uf9579WhZJ4ej6pkEREIAIJRh/view?usp=sharing, https://drive.google.com/file/d/1f5_aeEDRkwvOZCLKAz2ZFpwahqxHBtio/view?usp=sharing, https://aistudio.google.com/app/prompts?state=%7B%22ids%22:%5B%221gx_oZ2wveunWKD2wA8376-_VkH-4cB0T%22%5D,%22action%22:%22open%22,%22userId%22:%22114616170952591381046%22,%22resourceKeys%22:%7B%7D%7D&usp=sharing, https://drive.google.com/file/d/1hilLbpA8KFwBdWXB710RoqnPT_ra8hQS/view?usp=sharing, https://drive.google.com/file/d/1nKpXi0YMRulUyQmu-3OYkYCv60d-2xS7/view?usp=sharing, https://drive.google.com/file/d/1ohbdiNg0wYF_FDgycsgb4r27ZGX9FkFM/view?usp=sharing, https://drive.google.com/file/d/1r-iHHzDEvyg-s8jAIelE7AKDoU16_N2Q/view?usp=sharing, https://drive.google.com/file/d/1yiWwDOe7C0969ePNJti0kqznH2faVlbn/view?usp=sharing
