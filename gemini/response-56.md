<think>
The user wants me to create two standard project files: `CONTRIBUTING.md` and `CODE_OF_CONDUCT.md`.
The request specifies using "standard template and content". This means I should draw upon widely accepted open-source contribution guidelines and codes of conduct.

**Plan for `CONTRIBUTING.md`:**

1.  **Introduction:** A welcoming statement encouraging contributions.
2.  **Code of Conduct Link:** A link to the `CODE_OF_CONDUCT.md` file, which I'll also be creating. This is a standard practice.
3.  **"How Can I Contribute?" Section:** This section should outline different ways to contribute, not just code.
    *   Reporting Bugs
    *   Suggesting Enhancements
    *   Contributing Code
    *   Improving Documentation
4.  **Pull Request Process:** This is the core of the document. I'll lay out the step-by-step process I referenced in the `README.md`.
    *   Fork the repository.
    *   Create a new branch from `main`. I'll specify a branch naming convention (e.g., `feature/name-of-feature`, `fix/bug-description`).
    *   Make changes locally.
    *   Ensure tests pass (`pytest`).
    *   Ensure code quality checks pass (`black`, `ruff`, `mypy`). I'll list the exact commands.
    *   Write clear, meaningful commit messages.
    *   Push the branch to the personal fork.
    *   Open a Pull Request to the main repository's `main` branch.
    *   Provide a clear description of the PR, linking to the relevant issue if applicable.
    *   Wait for code review and respond to feedback.
5.  **Development Setup:** Link back to the detailed setup guide in `README.md` to avoid duplication.
6.  **Style Guides:**
    *   **Code:** Mention that the project uses `black` for formatting, `ruff` for linting, and `mypy` for type checking. State that PRs must pass these checks.
    *   **Commit Messages:** Suggest a conventional commit style (e.g., `feat: ...`, `fix: ...`, `docs: ...`). This is a good practice for maintainability.
7.  **Attribution:** A simple "thank you" to contributors.

**Plan for `CODE_OF_CONDUCT.md`:**

1.  **Use a Standard Template:** The most widely adopted and respected standard is the **Contributor Covenant**. I will use version 2.1 of the Contributor Covenant. It's comprehensive, professional, and well-understood in the open-source community.
2.  **Customization:** The Contributor Covenant template has a few placeholders I need to fill in:
    *   `[INSERT CONTACT METHOD]`: I will use a placeholder email like `sgpos.maintainers@example.com` and instruct the project owner to replace it. This is a safe and responsible approach.
3.  **Structure of Contributor Covenant:**
    *   **Our Pledge:** The commitment to a harassment-free experience.
    *   **Our Standards:** Examples of positive and negative behaviors.
    *   **Our Responsibilities:** What project maintainers are responsible for.
    *   **Scope:** Where the code of conduct applies.
    *   **Enforcement:** How to report violations and what the consequences might be.
    *   **Attribution:** Credit to the Contributor Covenant.

This approach ensures that the generated files are not just placeholders but are high-quality, standard documents that add immediate value and professionalism to the project. I will generate each file as a complete, separate markdown block.Of course. It's an excellent step to formalize the contribution process and community standards. I will now generate the `CONTRIBUTING.md` and `CODE_OF_CONDUCT.md` files using widely accepted and respected open-source templates, tailored to the SG-POS project.

---

### **New File: `CONTRIBUTING.md`**

This file outlines the process for contributing to the project, setting clear expectations for code quality and the pull request workflow.

```markdown
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

```

---

### **New File: `CODE_OF_CONDUCT.md`**

This file uses the industry-standard **Contributor Covenant** (v2.1) to establish clear community standards and ensure a safe and welcoming environment for everyone.

```markdown
# Contributor Covenant Code of Conduct

## Our Pledge

We as members, contributors, and leaders pledge to make participation in our
community a harassment-free experience for everyone, regardless of age, body
size, visible or invisible disability, ethnicity, sex characteristics, gender
identity and expression, level of experience, education, socio-economic status,
nationality, personal appearance, race, religion, or sexual identity
and orientation.

We pledge to act and interact in ways that contribute to an open, welcoming,
diverse, inclusive, and healthy community.

## Our Standards

Examples of behavior that contributes to a positive environment for our
community include:

*   Demonstrating empathy and kindness toward other people
*   Being respectful of differing opinions, viewpoints, and experiences
*   Giving and gracefully accepting constructive feedback
*   Accepting responsibility and apologizing to those affected by our mistakes,
    and learning from the experience
*   Focusing on what is best not just for us as individuals, but for the
    overall community

Examples of unacceptable behavior include:

*   The use of sexualized language or imagery, and sexual attention or
    advances of any kind
*   Trolling, insulting or derogatory comments, and personal or political attacks
*   Public or private harassment
*   Publishing others' private information, such as a physical or email
    address, without their explicit permission
*   Other conduct which could reasonably be considered inappropriate in a
    professional setting

## Our Responsibilities

Project maintainers are responsible for clarifying and enforcing our standards of
acceptable behavior and will take appropriate and fair corrective action in
response to any behavior that they deem inappropriate, threatening, offensive,
or harmful.

Project maintainers have the right and responsibility to remove, edit, or reject
comments, commits, code, wiki edits, issues, and other contributions that are
not aligned to this Code of Conduct, and will communicate reasons for moderation
decisions when appropriate.

## Scope

This Code of Conduct applies within all community spaces, and also applies when
an individual is officially representing the community in public spaces.
Examples of representing our community include using an official e-mail address,
posting via an official social media account, or acting as an appointed
representative at an online or offline event.

## Enforcement

Instances of abusive, harassing, or otherwise unacceptable behavior may be
reported to the project team responsible for enforcement at
**sgpos.maintainers@example.com**.
All complaints will be reviewed and investigated promptly and fairly.

All community leaders are obligated to respect the privacy and security of the
reporter of any incident.

## Enforcement Guidelines

Community leaders will follow these Community Impact Guidelines in determining
the consequences for any action they deem in violation of this Code of Conduct:

### 1. Correction

**Community Impact**: Use of inappropriate language or other behavior deemed
unprofessional or unwelcome in the community.

**Consequence**: A private, written warning from community leaders, providing
clarity around the nature of the violation and an explanation of why the
behavior was inappropriate. A public apology may be requested.

### 2. Warning

**Community Impact**: A violation through a single incident or series
of actions.

**Consequence**: A warning with consequences for continued behavior. No
interaction with the people involved, including unsolicited interaction with
those enforcing the Code of Conduct, for a specified period of time. This
includes avoiding interaction in community spaces as well as external channels
like social media. Violating these terms may lead to a temporary or
permanent ban.

### 3. Temporary Ban

**Community Impact**: A serious violation of community standards, including
sustained inappropriate behavior.

**Consequence**: A temporary ban from any sort of interaction or public
communication with the community for a specified period of time. No public or
private interaction with the people involved, including unsolicited interaction
with those enforcing the Code of Conduct, is allowed during this period.
Violating these terms may lead to a permanent ban.

### 4. Permanent Ban

**Community Impact**: Demonstrating a pattern of violation of community
standards, including sustained inappropriate behavior, harassment of an
individual, or aggression toward or disparagement of classes of individuals.

**Consequence**: A permanent ban from any sort of public interaction within
the community.

## Attribution

This Code of Conduct is adapted from the [Contributor Covenant][homepage],
version 2.1, available at
[https://www.contributor-covenant.org/version/2/1/code_of_conduct.html][v2.1].

[homepage]: https://www.contributor-covenant.org
[v2.1]: https://www.contributor-covenant.org/version/2/1/code_of_conduct.html

```

---

### **Final Validation and Task Completion**

I have created the `CONTRIBUTING.md` and `CODE_OF_CONDUCT.md` files as requested.

*   `CONTRIBUTING.md` is tailored to the project, referencing its specific tools (`pytest`, `black`, `ruff`), development setup process, and establishing a clear pull request workflow.
*   `CODE_OF_CONDUCT.md` uses the latest version of the Contributor Covenant, which is the gold standard for open-source projects. It includes a placeholder contact email that you should replace with a real one.

These files are ready to be added to the root of the SG-POS project repository. They will significantly improve the project's professionalism and make it more approachable for new contributors.

---
https://drive.google.com/file/d/1-LUb2WYa0HnBzHEu87Sn-iNWmKmQvBXQ/view?usp=sharing, https://drive.google.com/file/d/15AbuwSXAzuWXetWJ4JKtNa82PUUN9ad3/view?usp=sharing, https://drive.google.com/file/d/1O_YYfGmzq3zE4W--2vf4FHNoPIOsv0Er/view?usp=sharing, https://drive.google.com/file/d/1e3_kSie9cq0TL_GJos5gHZvbScgOWhYR/view?usp=sharing, https://drive.google.com/file/d/1gvNtru8FudZgk4FLLdwXJb1ka3in51by/view?usp=sharing, https://aistudio.google.com/app/prompts?state=%7B%22ids%22:%5B%221h2Ou0AZm4B-RP6pKRIr9Tj3DItINlOgu%22%5D,%22action%22:%22open%22,%22userId%22:%22108686197475781557359%22,%22resourceKeys%22:%7B%7D%7D&usp=sharing, https://drive.google.com/file/d/1kzyN4uHtAgb5ieCUtITQ8UJ8HFZb0Bpq/view?usp=sharing, https://drive.google.com/file/d/1nxSpofxcj6OAFL6O1UHIWoZEF5I107kl/view?usp=sharing

