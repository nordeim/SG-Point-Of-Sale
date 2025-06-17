# Contributing to the SG-POS System

First off, thank you for considering contributing to the SG-POS System! It's people like you that make open source such a powerful and rewarding ecosystem. Your contributions will directly help small business owners in Singapore run their businesses more effectively.

This document provides guidelines for contributing to the project. We want to make it as easy and transparent as possible for you to get involved.

## Code of Conduct

By participating in this project, you are expected to uphold our [Code of Conduct](CODE_OF_CONDUCT.md). Please read it before you start. We are committed to fostering an open, welcoming, and harassment-free environment.

## How Can I Contribute?

There are many ways to contribute, and all of them are valuable.

*   **Reporting Bugs:** If you find a bug, please open an issue on our GitHub repository. Provide a clear title, a detailed description of the bug, steps to reproduce it, and any relevant logs or screenshots.
*   **Suggesting Enhancements:** If you have an idea for a new feature or an improvement to an existing one, open an issue to start a discussion. This allows us to align on the goals before any code is written.
*   **Improving Documentation:** Good documentation is crucial. If you find gaps in our `README.md`, docstrings, or other project documents, feel free to submit a pull request with your improvements.
*   **Writing Code:** If you're ready to write some code, look for issues tagged with `help wanted` or `good first issue`.

## Your First Code Contribution: The Pull Request Process

We follow a standard fork-and-pull workflow for code contributions.

1.  **Fork the repository** on GitHub to create your own copy of the project.

2.  **Set up your development environment** by following the detailed [Developer Setup & Deployment Guide](README.md#6-developer-setup--deployment-guide) in our main `README.md`.

3.  **Create a new branch** from the `main` branch in your fork. Please use a descriptive branch name.
    *   For new features: `feature/my-awesome-feature`
    *   For bug fixes: `fix/correct-calculation-bug`
    *   For documentation: `docs/update-readme`
    ```bash
    git checkout -b feature/your-branch-name
    ```

4.  **Make your changes.** Write your code, and don't forget to add or update tests to cover your changes!

5.  **Ensure all quality checks pass.** Before you submit your pull request, run all the local checks to ensure your code adheres to our quality standards.
    ```bash
    # Ensure all tests pass
    pytest

    # Format your code with Black
    black .

    # Lint your code with Ruff
    ruff . --fix

    # Check static types with MyPy
    mypy app
    ```
    The pre-commit hooks, if configured, will help automate this process.

6.  **Commit your changes** with a clear and descriptive commit message. We recommend following the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) specification.
    *   Example: `feat(sales): Add support for gift card payments`
    *   Example: `fix(inventory): Prevent negative stock adjustments`
    ```bash
    git commit -m "feat(ui): Add new customer search functionality"
    ```

7.  **Push your branch** to your fork on GitHub.
    ```bash
    git push origin feature/your-branch-name
    ```

8.  **Open a Pull Request (PR)** from your fork's branch to the `main` branch of the official SG-POS repository.
    *   Provide a clear title for your PR.
    *   In the description, explain the "what" and "why" of your changes.
    *   If your PR addresses an existing issue, link it using `Closes #123`.

9.  **Engage in the Code Review.** A maintainer will review your PR. Be prepared to discuss your changes and make adjustments based on the feedback. We aim to be responsive and provide constructive reviews.

Thank you again for your contribution!

