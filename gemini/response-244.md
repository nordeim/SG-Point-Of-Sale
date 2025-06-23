<think>
The user has provided a new, correct `pip list` output and has requested that I update the `pyproject.toml` file again. The process is the same as before, but the source data (the `pip list`) has changed.

**1. Task Breakdown & Analysis**

*   **Input:**
    1.  The *original* `pyproject.toml` file from the `project_codebase_files_set.md`. This is an important instruction, as I should not build upon my previous modification.
    2.  The new, correct output of `pip list`.
*   **Goal:** Create a new, complete `pyproject.toml` file with updated versions.
*   **Core Logic:**
    1.  Identify all packages listed under `[tool.poetry.dependencies]` and `[tool.poetry.group.dev.dependencies]` in the original `pyproject.toml`.
    2.  For each package, look up its version in the new `pip list`. The package names in `pyproject.toml` are case-insensitive and should be matched against the `pip list` output.
    3.  Update the version specifier in `pyproject.toml` to reflect the version from the `pip list`. I will use the caret `^` prefix for semantic versioning, as is standard practice with Poetry (e.g., `^6.9.1`). This allows for compatible updates but pins the major version.
    4.  Preserve all other sections of the file (`[tool.black]`, `[tool.ruff]`, etc.) without modification.
    5.  Handle discrepancies: If a package from `pyproject.toml` is not in the `pip list`, I will leave its version specifier unchanged as a safety measure.
    6.  Ignore extra packages from `pip list` that are not defined as direct dependencies in `pyproject.toml`.

**2. Execution Plan: Mapping Dependencies**

I will go through each dependency in the original `pyproject.toml` and find its corresponding version in the new `pip list`.

**`[tool.poetry.dependencies]` (Production):**
*   `PySide6`: `^6.9.0` -> `PySide6 6.9.1` -> Update to `^6.9.1`
*   `SQLAlchemy`: `^2.0.30` -> `SQLAlchemy 2.0.41` -> Update to `^2.0.41`
*   `alembic`: `^1.13.1` -> `alembic 1.16.2` -> Update to `^1.16.2`
*   `asyncpg`: `^0.29.0` -> `asyncpg 0.30.0` -> Update to `^0.30.0`
*   `greenlet`: `^3.0.3` -> `greenlet 3.2.3` -> Update to `^3.2.3`
*   `pydantic`: `^2.7.1` -> `pydantic 2.11.7` -> Update to `^2.11.7`
*   `pydantic-settings`: `^2.2.1` -> `pydantic-settings 2.10.0` -> Update to `^2.10.0`
*   `python-dotenv`: `^1.0.0` -> `python-dotenv 1.1.0` -> Update to `^1.1.0`
*   `bcrypt`: `^4.1.2` -> `bcrypt 4.3.0` -> Update to `^4.3.0`
*   `cryptography`: `^42.0.7` -> `cryptography 45.0.4` -> Update to `^45.0.4`
*   `structlog`: `^24.2.0` -> `structlog 25.4.0` -> Update to `^25.4.0`
*   `aiohttp`: `^3.9.5` -> `aiohttp 3.12.13` -> Update to `^3.12.13`
*   `reportlab`: `^4.1.0` -> `reportlab 4.4.2` -> Update to `^4.4.2`
*   `openpyxl`: `^3.1.2` -> `openpyxl 3.1.5` -> Update to `^3.1.5`
*   `qrcode`: `^7.4.2` -> `qrcode 8.2` -> Update to `^8.2`

**`[tool.poetry.group.dev.dependencies]` (Development):**
*   `psycopg2-binary`: `^2.9.10` -> `psycopg2-binary 2.9.10` -> No change needed, version matches.
*   `aiosqlite`: `^0.20.0` -> `aiosqlite 0.21.0` -> Update to `^0.21.0`
*   `pytest`: `^8.2.0` -> `pytest 8.4.1` -> Update to `^8.4.1`
*   `pytest-qt`: `^4.2.0` -> `pytest-qt 4.4.0` -> Update to `^4.4.0`
*   `pytest-asyncio`: `^0.23.0` -> `pytest-asyncio 1.0.0` -> Update to `^1.0.0`
*   `pytest-cov`: `^5.0.0` -> `pytest-cov 6.2.1` -> Update to `^6.2.1`
*   `factory-boy`: `^3.3.0` -> `factory-boy 3.3.3` -> Update to `^3.3.3`
*   `black`: `^24.4.2` -> `black 25.1.0` -> Update to `^25.1.0`
*   `ruff`: `^0.4.4` -> `ruff 0.12.0` -> Update to `^0.12.0`
*   `mypy`: `^1.10.0` -> `mypy 1.16.1` -> Update to `^1.16.1`
*   `pre-commit`: `^3.7.0` -> `pre-commit 4.2.0` -> Update to `^4.2.0`
*   `Sphinx`: `^7.3.1` -> `Sphinx 8.2.3` -> Update to `^8.2.3`
*   `myst-parser`: `^2.0.0` -> `myst-parser 4.0.1` -> Update to `^4.0.1`
*   `sphinx-rtd-theme`: `^2.0.0` -> `sphinx-rtd-theme 3.0.2` -> Update to `^3.0.2`
*   `ipython`: `^8.24.0` -> `ipython 9.3.0` -> Update to `^9.3.0`

**3. Final Code Generation**

I will now construct the complete `pyproject.toml` file with these version changes. I will be careful to preserve the structure, comments, and all other sections. The `SQLAlchemy` dependency has an `extras` key, which must be preserved. The `qrcode` dependency also has an `extras` key. I will maintain this structure.

The plan is sound and directly addresses the user's request with the new data. I will now generate the final output.Of course. I will create a complete and updated replacement for your `pyproject.toml` file, using the original file as a base and meticulously updating the package versions to match your new, correct `pip list` output.

My process guarantees:
*   **Completeness:** The entire `pyproject.toml` file will be provided.
*   **Accuracy:** All package versions found in your new `pip list` will be accurately reflected.
*   **Preservation:** All comments, formatting, and tool configurations (`[tool.black]`, `[tool.ruff]`, etc.) from the original file will be preserved.

Here is the complete, updated replacement file for `pyproject.toml`:

```toml
# pyproject.toml
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
python = ">=3.11,<3.14"

# --- Core Production Dependencies ---
# These are the essential packages required for the application to run in production.

# GUI Framework
PySide6 = "^6.9.1"         # The core Qt6 bindings for Python.

# Database & ORM
SQLAlchemy = {version = "^2.0.41", extras = ["asyncio"]} # The industry-standard ORM, with asyncio support.
alembic = "^1.16.2"        # For database schema migrations.
asyncpg = "^0.30.0"        # High-performance asyncio driver for PostgreSQL.
greenlet = "^3.2.3"        # Required for SQLAlchemy's async bridge.

# Data Validation & Settings
pydantic = "^2.11.7"        # For Data Transfer Objects (DTOs) and core validation.
pydantic-settings = "^2.10.0" # Added for settings management with Pydantic v2.
python-dotenv = "^1.1.0"   # For loading environment variables from .env files.

# Security
bcrypt = "^4.3.0"          # For secure password hashing.
cryptography = "^45.0.4"   # For any custom encryption needs.

# Logging
structlog = "^25.4.0"       # For structured, context-aware logging.

# External Integrations & Utilities
aiohttp = "^3.12.13"         # Asynchronous HTTP client for API integrations.
reportlab = "^4.4.2"       # For generating PDF receipts and reports.
openpyxl = "^3.1.5"        # For exporting data to Excel (.xlsx) files.
qrcode = {version = "^8.2", extras = ["pil"]} # For generating QR codes (e.g., for PayNow).


# --- Development Group Dependencies ---
# These packages are only installed in development environments (`poetry install --with dev`).
# This keeps the production installation lean and clean.
[tool.poetry.group.dev.dependencies]
psycopg2-binary = "^2.9.10" # Synchronous driver for Alembic
aiosqlite = "^0.21.0"      # Async driver for SQLite test database

# Testing Framework
pytest = "^8.4.1"             # The primary testing framework.
pytest-qt = "^4.4.0"          # For testing PySide6 UI components.
pytest-asyncio = "^1.0.0"    # For testing asyncio code.
pytest-cov = "^6.2.1"         # For measuring test coverage.
factory-boy = "^3.3.3"        # For creating test data fixtures.

# Code Quality & Formatting
black = "^25.1.0"            # The uncompromising code formatter.
ruff = "^0.12.0"               # An extremely fast Python linter, replacing flake8, isort, etc.
mypy = "^1.16.1"              # Static type checker for Python.
pre-commit = "^4.2.0"         # For managing and maintaining pre-commit hooks.

# Documentation
Sphinx = "^8.2.3"             # The standard documentation generator for Python projects.
myst-parser = "^4.0.1"        # To write Sphinx documentation in Markdown.
sphinx-rtd-theme = "^3.0.2"   # A popular theme for Sphinx docs.

# Interactive Development
ipython = "^9.3.0"           # A better interactive Python shell.


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

---
https://aistudio.google.com/app/prompts?state=%7B%22ids%22:%5B%221QHPuQ2OmdJqV6C6LfjDiePbLBUJZt8BL%22%5D,%22action%22:%22open%22,%22userId%22:%22108686197475781557359%22,%22resourceKeys%22:%7B%7D%7D&usp=sharing, https://drive.google.com/file/d/1WE7SP2KKstgtv-ic3NpKSV06F42uPZ-b/view?usp=sharing, https://drive.google.com/file/d/1ogzzUdmf1E20GNgAp7l5BPxOzYedBuyx/view?usp=sharing, https://drive.google.com/file/d/1rTViMCAfPJNou719v2qYziZ8o3aJ1UDg/view?usp=sharing, https://drive.google.com/file/d/1vfl0VUd-qB5sPz6YMsEp5hJFwyQiyxgJ/view?usp=sharing, https://drive.google.com/file/d/1vncax4DJ4L6LFuboaXx0UDMZsbc_kiiv/view?usp=sharing, https://drive.google.com/file/d/1x46nXSW7b8WZxVMaklB3vTTpW0aHMBJT/view?usp=sharing

