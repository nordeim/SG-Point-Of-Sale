A well-structured `pyproject.toml` is the backbone of a modern Python project. It centralizes configuration, defines dependencies with precision, and ensures a reproducible development environment for every contributor.

Here is a complete and meticulously crafted `pyproject.toml` file for the SG-POS project, built using [Poetry](https://python-poetry.org/). This file is not just a list of dependencies; it's a comprehensive configuration hub that defines the project's metadata, dependencies, development tools, and code quality standards, all in one place.

I have included extensive comments to explain the rationale behind each section and choice, making it a self-documenting guide for any developer joining the project.

---

### **`pyproject.toml` for SG-POS System**

```toml
# ==============================================================================
# pyproject.toml for the SG Point-of-Sale (SG-POS) System
# ------------------------------------------------------------------------------
# This file manages the entire project's metadata, dependencies, and development
# tool configurations using the Poetry build system. It is the single source of
# truth for setting up the development environment.
#
# For more information on the TOML format: https://toml.io
# For more information on Poetry: https://python-poetry.org
# ==============================================================================

[tool.poetry]
# --- Project Metadata ---
# This information is used for packaging the application and for display on
# package indexes like PyPI if the project is ever published.
name = "sg-pos-system"
version = "1.0.0"
description = "An enterprise-grade, open-source Point-of-Sale system, meticulously engineered for Singapore's SMB retail landscape."
authors = ["Your Name <you@example.com>"]
license = "MIT"
readme = "README.md"
homepage = "https://github.com/your-org/sg-pos-system"
repository = "https://github.com/your-org/sg-pos-system"
documentation = "https://github.com/your-org/sg-pos-system/blob/main/docs/index.md"
keywords = ["pos", "point-of-sale", "retail", "singapore", "gst", "pyside6", "qt6", "python"]

# --- Python Version Constraint ---
# Specifies that this project is compatible with Python 3.11 and any later minor versions,
# but not Python 4.0. This aligns with the PRD's technology stack choice.
[tool.poetry.dependencies]
python = "^3.11"

# --- Core Production Dependencies ---
# These are the essential packages required for the application to run in production.

# GUI Framework
PySide6 = "^6.6.0"         # The core Qt6 bindings for Python.

# Database & ORM
SQLAlchemy = {version = "^2.0.23", extras = ["asyncio"]} # The industry-standard ORM, with asyncio support.
alembic = "^1.12.1"        # For database schema migrations.
asyncpg = "^0.29.0"        # High-performance asyncio driver for PostgreSQL.

# Data Validation & Settings
pydantic = "^2.5.2"        # For Data Transfer Objects (DTOs) and settings management.
python-dotenv = "^1.0.0"   # For loading environment variables from .env files.

# Security
bcrypt = "^4.0.1"          # For secure password hashing.
cryptography = "^41.0.5"   # For any custom encryption needs.

# Logging
structlog = "^23.2.0"       # For structured, context-aware logging.

# External Integrations & Utilities
aiohttp = "^3.8.6"         # Asynchronous HTTP client for API integrations.
reportlab = "^4.0.4"       # For generating PDF receipts and reports.
openpyxl = "^3.1.2"        # For exporting data to Excel (.xlsx) files.
qrcode = {version = "^7.4.2", extras = ["pil"]} # For generating QR codes (e.g., for PayNow).


# --- Development Group Dependencies ---
# These packages are only installed in development environments (`poetry install --with dev`).
# This keeps the production installation lean and clean.
[tool.poetry.group.dev.dependencies]
# Testing Framework
pytest = "^7.4.3"             # The primary testing framework.
pytest-qt = "^4.2.0"          # For testing PySide6 UI components.
pytest-asyncio = "^0.21.1"    # For testing asyncio code.
pytest-cov = "^4.1.0"         # For measuring test coverage.
factory-boy = "^3.3.0"        # For creating test data fixtures.

# Code Quality & Formatting
black = "^23.11.0"            # The uncompromising code formatter.
ruff = "^0.1.6"               # An extremely fast Python linter, replacing flake8, isort, etc.
mypy = "^1.7.0"               # Static type checker for Python.
pre-commit = "^3.5.0"         # For managing and maintaining pre-commit hooks.

# Documentation
Sphinx = "^7.2.6"             # The standard documentation generator for Python projects.
myst-parser = "^2.0.0"        # To write Sphinx documentation in Markdown.
sphinx-rtd-theme = "^1.3.0"   # A popular theme for Sphinx docs.

# Interactive Development
ipython = "^8.17.2"           # A better interactive Python shell.


# ==============================================================================
# Tool Configurations
# ------------------------------------------------------------------------------
# Centralizing tool configurations here makes the project easier to manage.
# ==============================================================================

# --- Black (Code Formatter) Configuration ---
[tool.black]
line-length = 88
target-version = ['py311']
include = '\.pyi?$'
exclude = '''
/(
    \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | _build
  | buck-out
  | build
  | dist
  | migrations
)/
'''

# --- Ruff (Linter) Configuration ---
# Ruff is configured to be strict and to replace multiple older tools.
[tool.ruff]
line-length = 88
target-version = "py311"

# Select a broad range of rules to enforce high code quality.
# See all rules here: https://docs.astral.sh/ruff/rules/
select = [
    "E",  # pycodestyle errors
    "W",  # pycodestyle warnings
    "F",  # pyflakes
    "I",  # isort (import sorting)
    "B",  # flake8-bugbear (finds likely bugs)
    "C4", # flake8-comprehensions
    "UP", # pyupgrade (modernizes syntax)
    "S",  # bandit (security linter)
    "SIM",# flake8-simplify
]
ignore = ["E501"] # Ignored by black formatter anyway.

[tool.ruff.mccabe]
max-complexity = 10 # Keep functions simple and readable.

# --- MyPy (Static Type Checker) Configuration ---
# Enforces strict type checking for robust code.
[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_calls = true
strict_optional = true
show_error_codes = true
exclude = ["migrations/"]


# --- Pytest Configuration ---
[tool.pytest.ini_options]
minversion = "7.0"
addopts = "-ra -q --cov=app --cov-report=term-missing"
testpaths = ["tests"]
python_files = "test_*.py"
asyncio_mode = "auto" # Automatically handle asyncio tests.
qt_api = "pyside6"    # Specify the Qt binding for pytest-qt.


# ==============================================================================
# Build System Configuration
# ------------------------------------------------------------------------------
# This section is required by PEP 517 and tells tools like pip how to build
# the project package. For Poetry, this is standard boilerplate.
# ==============================================================================

[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"
```

### **How to Use This File**

This `pyproject.toml` file is the heart of your project's setup. Here's a quick guide for a new developer:

1.  **Installation:** A developer clones the repository. The only commands they need to run to get a fully functional development environment are:
    ```bash
    # Install all dependencies, including dev tools
    poetry install --with dev
    
    # Activate the virtual environment created by Poetry
    poetry shell
    ```
    Poetry reads this `pyproject.toml` file, resolves all dependencies, and installs them into an isolated virtual environment.

2.  **Code Quality:** All the configured tools can be run easily:
    ```bash
    # Format the code
    poetry run black .

    # Lint and auto-fix the code
    poetry run ruff . --fix

    # Run static type checking
    poetry run mypy app
    ```
    These commands are typically integrated into a `pre-commit` hook, so they run automatically before a developer commits their code, ensuring all code entering the repository meets our high standards.

3.  **Running Tests:**
    ```bash
    # Run the full test suite
    poetry run pytest
    ```
    Pytest will automatically pick up its configuration from the `[tool.pytest.ini_options]` section.

This file provides a powerful, centralized, and self-documenting foundation for the SG-POS project, ensuring consistency and quality from the very first line of code written.

---
https://drive.google.com/file/d/1--N5SVasJwyuD2sAG_PkHP_EU8maFUIG/view?usp=sharing, https://drive.google.com/file/d/1-aPjGdazXcN4sMP1Rrxu3ZL-_r77se25/view?usp=sharing, https://drive.google.com/file/d/155prVF-weYwj2SYGTz6kgmQCWr54fe1i/view?usp=sharing, https://drive.google.com/file/d/1B8QfYknf2XcufBlNqy85reIlayDz3A4G/view?usp=sharing, https://drive.google.com/file/d/1DWDcoki0DxrojFQII5TXKEQmkb_1lmAZ/view?usp=sharing, https://drive.google.com/file/d/1GOx8Ip7IiCAJJAh5_uTn1z_attqC-UYX/view?usp=sharing, https://drive.google.com/file/d/1I-oK7zzhWFuxkh2M8RWTNyLXTN63ZAbV/view?usp=sharing, https://drive.google.com/file/d/1LtDhg_B1t059pE3AKsb0DnRlIvaRHG1W/view?usp=sharing, https://drive.google.com/file/d/1O7dMCCPrlwVdFbbZTN-X_hKHrWJcvRwO/view?usp=sharing, https://drive.google.com/file/d/1OYbolRDSNyB4s1iI6kaxL00EcIgZvuLK/view?usp=sharing, https://drive.google.com/file/d/1PcgJkam4NW0VyCRt3KtAj_QtCy3_Va3M/view?usp=sharing, https://drive.google.com/file/d/1Py5ksEK0rg5SNBcnUEo8fGUlKldAGC2R/view?usp=sharing, https://drive.google.com/file/d/1RqS06J2HqHsSyQiK4GYM8wmAX6z5TzFW/view?usp=sharing, https://drive.google.com/file/d/1UsRkTO-P3XZRsU4r6p-5Vqqpfm5VZ26K/view?usp=sharing, https://drive.google.com/file/d/1W6fKS9oWjpV3wsE1x6SxwE0adjfjvJ16/view?usp=sharing, https://drive.google.com/file/d/1Wn2QYlW05N9ei6WzG1uDe8Ac96Dc_wqB/view?usp=sharing, https://drive.google.com/file/d/1_xoWQs6uf9579WhZJ4ej6pkEREIAIJRh/view?usp=sharing, https://drive.google.com/file/d/1f5_aeEDRkwvOZCLKAz2ZFpwahqxHBtio/view?usp=sharing, https://aistudio.google.com/app/prompts?state=%7B%22ids%22:%5B%221gx_oZ2wveunWKD2wA8376-_VkH-4cB0T%22%5D,%22action%22:%22open%22,%22userId%22:%22114616170952591381046%22,%22resourceKeys%22:%7B%7D%7D&usp=sharing, https://drive.google.com/file/d/1hilLbpA8KFwBdWXB710RoqnPT_ra8hQS/view?usp=sharing, https://drive.google.com/file/d/1nKpXi0YMRulUyQmu-3OYkYCv60d-2xS7/view?usp=sharing, https://drive.google.com/file/d/1ohbdiNg0wYF_FDgycsgb4r27ZGX9FkFM/view?usp=sharing, https://drive.google.com/file/d/1r-iHHzDEvyg-s8jAIelE7AKDoU16_N2Q/view?usp=sharing, https://drive.google.com/file/d/1yiWwDOe7C0969ePNJti0kqznH2faVlbn/view?usp=sharing
