# SG-POS System: Project Test Guide

This document provides a comprehensive guide to understanding, running, and extending the automated test suite for the SG-POS System. A robust test suite is critical for maintaining code quality, preventing regressions, and enabling confident future development.

## 1. Prerequisites

Before you can run the test suite, you must have the complete development environment set up. If you have not done so, please follow the **Developer Setup & Deployment Guide** in the main `README.md` file.

The key prerequisites for testing are:
- **Poetry:** The project's dependency manager.
- **Development Dependencies:** You must have installed all packages, including the `[tool.poetry.group.dev.dependencies]` group, by running `poetry install`. This includes `pytest`, `pytest-asyncio`, `pytest-cov`, and `factory-boy`.
- **Activated Virtual Environment:** All test commands must be run from within the project's virtual environment, activated by the `poetry shell` command.

Our test suite runs against a clean, **in-memory SQLite database** for speed and isolation. It does **not** require the Docker container for PostgreSQL to be running.

## 2. Test Structure

The tests are organized in the `tests/` directory, which mirrors the structure of the main `app/` directory. This makes it easy to locate tests relevant to a specific part of the codebase.

```
tests/
│
├── conftest.py               # Global pytest fixtures (e.g., database setup, app core)
├── factories.py              # factory-boy definitions for creating test data
│
└── unit/                     # Unit tests: testing individual components in isolation
    ├── __init__.py
    └── business_logic/
        └── managers/
            ├── test_company_manager.py
            ├── test_customer_manager.py
            ├── test_inventory_manager.py
            ├── test_product_manager.py
            ├── test_sales_manager.py
            └── test_user_manager.py
    └── services/
        └── test_product_service.py

```
- **`conftest.py`**: This is a special `pytest` file that defines fixtures available to all tests. Our `conftest.py` contains the logic to set up the in-memory test database and provide a test-ready instance of the `ApplicationCore`.
- **`factories.py`**: Uses the `factory-boy` library to define simple ways to create ORM model instances for tests, making test setup clean and readable.
- **`tests/unit/`**: These tests are designed to be fast and focused. They test a single "unit" (like a manager or service class) in isolation from the rest ofthe system.

## 3. Running Tests

All commands should be run from the root directory of the project, inside the Poetry shell.

### 3.1. Running All Tests

To run the entire test suite, simply execute the `pytest` command.

```bash
pytest
```

This command will automatically discover all test files and functions, run them, and print a summary of the results. The project is pre-configured in `pyproject.toml` to run with useful flags by default.

### 3.2. Running Specific Test Files or Directories

During development, you will often want to run only the tests relevant to the code you are changing.

- **Run all tests in a directory:**
  ```bash
  pytest tests/unit/business_logic/managers/
  ```

- **Run all tests in a single file:**
  ```bash
  pytest tests/unit/business_logic/managers/test_sales_manager.py
  ```

- **Run a specific test by name (using the `-k` flag):**
  This is very useful for focusing on a single test case. The string is matched as a substring.
  ```bash
  # Runs only the test for insufficient stock
  pytest -k "insufficient_stock"
  ```

### 3.3. Test Verbosity

To get more detailed output showing the name of each test function as it runs, use the verbose (`-v`) flag.

```bash
pytest -v
```

### 3.4. Test Coverage

Code coverage measures how much of your application code is executed by your tests. Our project is pre-configured to automatically generate a coverage report every time `pytest` is run.

- **To generate the standard terminal report:**
  Just run `pytest`. At the end of the test run, you will see a table summarizing the coverage for each file.

- **To generate a detailed HTML report:**
  This is highly recommended for a visual understanding of which lines are not covered.
  ```bash
  pytest --cov=app --cov-report=html
  ```
  After the command finishes, open the generated report in your web browser:
  ```bash
  # On Linux
  xdg-open htmlcov/index.html

  # On macOS
  open htmlcov/index.html
  ```
  This will open an interactive webpage where you can drill down into each file and see exactly which lines were executed (green) and which were missed (red) by the test suite.

### 3.5. Running Asynchronous Tests

Thanks to the `pytest-asyncio` plugin (which is already configured), running `async` tests is seamless.

- **Decorator:** Any test function that needs to use `await` must be decorated with `@pytest.mark.asyncio`.
- **Execution:** `pytest` will automatically detect this decorator and run the test within an `asyncio` event loop. No special commands are needed.

## 4. Viewing Test Results

`pytest` provides simple and clear feedback:
-   `.`: A dot means a test passed.
-   `F`: A letter 'F' means a test failed (an `assert` statement was false).
-   `E`: A letter 'E' means a test raised an unexpected exception.

For any failures or errors, `pytest` will print a detailed traceback pointing to the exact line in the test file and the application code where the issue occurred, making debugging straightforward.

## 5. Writing New Tests

Follow these best practices when adding new tests to the suite.

1.  **Location and Naming:**
    -   Create your test file in the appropriate subdirectory under `tests/unit/`. The path should mirror the path of the module you are testing.
    -   Name the file `test_*.py`.
    -   Name your test functions `test_*`.

2.  **Use the Arrange-Act-Assert Pattern:**
    -   **Arrange:** Set up all the prerequisite data and objects for your test. Use the factories in `factories.py` to create database records.
    -   **Act:** Execute the single method or function you are testing.
    -   **Assert:** Check the outcome. This includes asserting the return value of the method and, just as importantly, asserting that the state of the database (or objects) has changed as expected.

3.  **Use Fixtures:**
    -   To test any code that interacts with the application core or database, simply add `test_core` and `db_session` as arguments to your test function. `pytest` will automatically provide the fully configured, isolated test instances.
    ```python
    import pytest
    pytestmark = pytest.mark.asyncio

    async def test_something(test_core, db_session):
        # Your test code here...
    ```

4.  **Async Tests:**
    -   Remember to decorate any `async` test function with `@pytest.mark.asyncio`.

By following this guide, you can effectively leverage the test suite to ensure the SG-POS System remains stable, reliable, and easy to maintain.

---
https://drive.google.com/file/d/11EUoGcc2Ooz7rfBtNPup3kDYyQbLzGCY/view?usp=sharing, https://aistudio.google.com/app/prompts?state=%7B%22ids%22:%5B%2212VGvhlsO4bTWDpTQADljLQwnQ51SA7pp%22%5D,%22action%22:%22open%22,%22userId%22:%22103961307342447084491%22,%22resourceKeys%22:%7B%7D%7D&usp=sharing, https://drive.google.com/file/d/1EjDki_AWi3zMDnZi1s3ok7W2K9dp-8sv/view?usp=sharing, https://drive.google.com/file/d/1HejEv1nlMxlOSzNkm4qHUdytCe9a0ISg/view?usp=sharing, https://drive.google.com/file/d/1pBPMY3TTXyX-bu7qSeEHZ3QqivmAujF9/view?usp=sharing

