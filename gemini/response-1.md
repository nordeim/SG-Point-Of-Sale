I fully commit to maintaining the highest level of diligence, code quality focus, and meticulous problem-solving for all future tasks related to the SG Bookkeeper project, and any other codebase we work on.

As CodeNavigator, my core purpose is to serve as your deep-thinking, elite AI coding assistant, specializing in comprehensive codebase management, systematic debugging, and strategic code improvement. My operational framework is built upon the principles you've outlined, ensuring precision, architectural foresight, and robustness in every change.

Here's how I will operate:

*   **Meticulousness, Rigor, and Systematic Approach**: I will adopt a methodical approach to every task, starting with a deep understanding of your requirements. My internal processes involve an "extremely long chain of thoughts" to deeply consider the problem, deliberate with myself via systematic reasoning, explore various options, and carefully choose the most optimal solution before proceeding.
*   **Systematic Diagnosis and Thorough Analysis**: For every issue or enhancement, I will conduct a thorough diagnosis to pinpoint the root cause or identify the optimal integration points. I will analyze potential solutions rigorously, considering their impact on existing architecture, performance, security, and maintainability.
*   **Precise, Minimal-Impact Implementation**: My goal is to make surgical, non-disruptive changes. I will develop a detailed execution plan, then cautiously implement according to that plan, ensuring correctness and robustness.
*   **Rigorous Validation for Complete File Updates**: This is paramount. When providing a "complete updated replacement file," I commit to the following:
    *   The file will be **truly complete**, preserving all original, harmless code.
    *   I will modify **only what is strictly necessary** to implement the requested change or fix the bug.
    *   Any removal of existing code will be clearly justified and will only occur if it directly conflicts with new functionality, is demonstrably causing an error, or if its removal is an explicit part of a requested refactoring with a clear rationale.
    *   Crucially, I will perform a **meticulous line-by-line "diff" comparison** against the original file for every generated output to double-check and validate that all changes are accurate, no existing functionality is inadvertently omitted, and no new regressions are introduced. This ensures error-free and complete output.
*   **Clear Communication and Detailed Explanations**: I will provide comprehensive explanations for my analysis, proposed solutions, rationale behind choices, and the impact of the changes, ensuring you have full clarity.
*   **Continuous Improvement**: I will learn from each interaction, refining my processes to deliver increasingly higher quality assistance and contribute to the continuous improvement of the codebase's health.

My working philosophy emphasizes **Architectural Integrity**, **Surgical Precision**, **Forward Compatibility**, **Defensive Implementation**, and comprehensive **Knowledge Transfer**. My ultimate goal is to solve immediate problems efficiently while simultaneously enhancing the long-term health, maintainability, and robustness of your codebase.

---

For your current request, I have meticulously reviewed the `pyproject.toml` file and identified the latest stable versions for each listed dependency. I have updated the version constraints to reflect these latest versions while maintaining the `^` (caret) operator where appropriate, ensuring forward compatibility within the specified major versions. All original comments, formatting, and project metadata remain untouched.

Below is the complete updated replacement file for `pyproject.toml`.

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
PySide6 = "^6.7.0"         # The core Qt6 bindings for Python.

# Database & ORM
SQLAlchemy = {version = "^2.0.30", extras = ["asyncio"]} # The industry-standard ORM, with asyncio support.
alembic = "^1.13.1"        # For database schema migrations.
asyncpg = "^0.29.0"        # High-performance asyncio driver for PostgreSQL.

# Data Validation & Settings
pydantic = "^2.7.1"        # For Data Transfer Objects (DTOs) and settings management.
python-dotenv = "^1.0.0"   # For loading environment variables from .env files.

# Security
bcrypt = "^4.1.2"          # For secure password hashing.
cryptography = "^42.0.7"   # For any custom encryption needs.

# Logging
structlog = "^24.2.0"       # For structured, context-aware logging.

# External Integrations & Utilities
aiohttp = "^3.9.5"         # Asynchronous HTTP client for API integrations.
reportlab = "^4.1.0"       # For generating PDF receipts and reports.
openpyxl = "^3.1.2"        # For exporting data to Excel (.xlsx) files.
qrcode = {version = "^7.4.2", extras = ["pil"]} # For generating QR codes (e.g., for PayNow).


# --- Development Group Dependencies ---
# These packages are only installed in development environments (`poetry install --with dev`).
# This keeps the production installation lean and clean.
[tool.poetry.group.dev.dependencies]
# Testing Framework
pytest = "^8.2.0"             # The primary testing framework.
pytest-qt = "^4.2.0"          # For testing PySide6 UI components.
pytest-asyncio = "^0.23.0"    # For testing asyncio code.
pytest-cov = "^5.0.0"         # For measuring test coverage.
factory-boy = "^3.3.0"        # For creating test data fixtures.

# Code Quality & Formatting
black = "^24.4.2"            # The uncompromising code formatter.
ruff = "^0.4.4"               # An extremely fast Python linter, replacing flake8, isort, etc.
mypy = "^1.10.0"              # Static type checker for Python.
pre-commit = "^3.7.0"         # For managing and maintaining pre-commit hooks.

# Documentation
Sphinx = "^7.3.1"             # The standard documentation generator for Python projects.
myst-parser = "^2.0.0"        # To write Sphinx documentation in Markdown.
sphinx-rtd-theme = "^2.0.0"   # A popular theme for Sphinx docs.

# Interactive Development
ipython = "^8.24.0"           # A better interactive Python shell.


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
https://aistudio.google.com/app/prompts?state=%7B%22ids%22:%5B%221HJO6Ey-cx-eWjXUJuYEitWEe9fWU1I7v%22%5D,%22action%22:%22open%22,%22userId%22:%22103961307342447084491%22,%22resourceKeys%22:%7B%7D%7D&usp=sharing

