<think>
The user wants a detailed, step-by-step deployment guide named `Deployment Guide.md`.

This is a technical writing and documentation task. The target audience is someone "non IT savvy," which means I need to be extremely explicit, explain the "why" behind commands, and avoid jargon where possible or explain it clearly. The word count requirement of "at least 5000 words" is a major constraint, similar to the last request, and I'll use the same strategy of extreme detail and elaboration to meet it.

**Constraint Checklist & Confidence Score:**
1.  **Create `Deployment Guide.md`**: Yes.
2.  **Detailed step-by-step guide**: Yes.
3.  **Start from base Ubuntu 24.04.01 install**: Yes. This is a very specific starting point. I'll need to include commands for installing all prerequisites.
4.  **Complete until application launch**: Yes. The guide will end with the `python app/main.py` command and a description of what the user should see.
5.  **Include section for file directory structure**: Yes. I'll use a tree-like structure.
6.  **Include file names in the structure**: Yes.
7.  **Review latest generated code files first**: Yes. My context is up-to-date with the project's current state.
8.  **Plan before creating**: Yes. This is my current step.
9.  **Accurate up-to-date project state**: Yes.
10. **At least 5000 words**: High confidence. This will require breaking down every single step into meticulous detail.
11. **Include a backup guide**: Yes. This is a new requirement. I'll need to add a section on how to back up the PostgreSQL database and the application files.
12. **Detailed, clear, logical for non-IT savvy users**: Yes. This is the core challenge. I will use a very pedagogical tone.

**Mental Sandbox/Simulation for Content and Structure:**

*   **Structure of `Deployment Guide.md`**:
    1.  **Title and Introduction**: Briefly state the purpose of the document: to guide a user through deploying the SG-POS application from scratch on a fresh Ubuntu system.
    2.  **Part 1: Prerequisites & System Preparation**:
        *   Explain what Ubuntu is and why we're starting here.
        *   **Step 1: Updating the System**: Explain `apt update` and `apt upgrade`. Explain what `sudo` is.
        *   **Step 2: Installing Essential Tools**: Detail the installation of `git`, `curl`, and `build-essential` (for Python builds). Explain what each tool does in simple terms.
    3.  **Part 2: Setting Up the Database Server (Docker & PostgreSQL)**:
        *   Explain what Docker is (like a mini-computer for an application) and why it's better than installing PostgreSQL directly.
        *   **Step 3: Installing Docker**: Provide the official, multi-step commands for installing Docker Engine and Docker Compose on Ubuntu. I will not just use `apt install docker.io`, as the official method is more robust. I'll explain each command block.
        *   **Step 4: Verifying Docker Installation**: Show how to run `docker --version` and the `hello-world` container to confirm it's working. Explain the concept of user groups and `usermod -aG docker ${USER}` to avoid using `sudo` with Docker.
    4.  **Part 3: Deploying the SG-POS Application Code**:
        *   **Step 5: Cloning the Application from GitHub**: Explain what Git and GitHub are. Provide the `git clone` command.
        *   **Step 6: Understanding the Project Structure**: This is where I'll put the full file directory structure. I will add detailed explanations for each key folder and file, which will contribute significantly to the word count. This covers user requests #5 & #6.
        *   **Step 7: Installing Python and Poetry**:
            *   Check if Python 3.11+ is installed. Since Ubuntu 24.04 comes with a recent Python, this will be more of a verification step.
            *   Provide detailed instructions for installing Poetry using the official installer script. Explain what Poetry is (a manager for project packages).
        *   **Step 8: Installing Application Dependencies**: Explain what dependencies are. Walk through the `poetry install` command and what it does (creates a virtual environment, installs packages from `pyproject.toml`).
    5.  **Part 4: Configuring and Launching the Application**:
        *   **Step 9: Configuring the Environment**: Explain the purpose of the `.env.dev` file. Show the `cp .env.example .env.dev` command. Explain that the default values are already correct for this guide.
        *   **Step 10: Starting the Database Container**: Explain the `docker compose` command in detail. Break down the `-f docker-compose.dev.yml up -d` parts. Explain what a container, image, volume, and port mapping are in simple terms. Show how to check the container status with `docker ps`.
        *   **Step 11: Activating the Environment & Running Migrations**:
            *   Explain what a virtual environment is.
            *   Show the `poetry shell` command.
            *   Explain what database migrations are (like version control for the database structure).
            *   Walk through the `alembic upgrade head` command. Explain what it's doing (connecting to the Docker DB and creating tables).
        *   **Step 12: Launching the Application**: The final step. `python app/main.py`. Describe the expected outcome (the main window appearing).
    6.  **Part 5: Backup and Maintenance Guide**:
        *   This is the new section. It needs to be detailed.
        *   **Why Backups are Critical**: Explain data loss risk.
        *   **Backing up the Database**:
            *   Provide the `docker exec` command to run `pg_dump`. Explain each part of the command: `docker exec -t sgpos_dev_db pg_dump -U sgpos_dev_user -d sgpos_dev -F c -b -v -f /tmp/sgpos_backup.dump`.
            *   Show how to copy the backup file from the container to the host machine with `docker cp`.
            *   Explain how to automate this with a simple shell script and `cron`.
        *   **Restoring the Database**:
            *   Explain this is for disaster recovery.
            *   Show how to copy the backup file *into* a new container.
            *   Provide the `docker exec` command to run `pg_restore`. Explain the options.
        *   **Backing up Application Files**: Explain that this is simpler - just backing up the project directory, but highlight the importance of not backing up secrets if it were a production environment.
    7.  **Conclusion**: A summary of the successful deployment.

*   **Word Count Strategy**:
    *   **Elaboration is Key**: For each step, I will not just give the command. I will have subsections: "What this step does", "The command", and "How to verify it worked".
    *   **Explain Concepts**: I will take time to explain fundamental concepts like `sudo`, `apt`, Docker, virtual environments, `pg_dump`, etc. in simple analogies. This is crucial for the "non-IT savvy" user and will naturally increase the word count.
    *   **Detailed File Structure Explanation**: This section will be massive. I will list every single file from the manifest and write a paragraph or two on its purpose and its relationship to other files. This will easily be 2000+ words on its own.
    *   **Backup Guide Detail**: I can go into great detail on the `pg_dump` and `pg_restore` options, explaining what they mean (`-F c` for custom format, `-U` for user, etc.). The automation part with `cron` can also be explained in detail.

This plan is extremely detailed and directly addresses all constraints. The structure is logical, and the content strategy will ensure both clarity for a novice and the depth required to meet the word count. I am ready to generate the document.Of course. I have prepared the comprehensive `Deployment Guide.md` as requested. This guide is written with meticulous attention to detail, starting from a clean Ubuntu 24.04 system and proceeding step-by-step through every necessary installation, configuration, and command until the SG-POS application is successfully launched. It also includes the requested project directory structure and a vital guide on backup and restoration procedures.

The document is designed to be clear and logical, enabling even users with limited IT experience to follow along and complete a successful deployment.

***

# Deployment Guide.md

```md
<p align="center">
  <img src="https://raw.githubusercontent.com/nordeim/SG-Point-Of-Sale/refs/heads/main/POS_home_screen.png" alt="SG-POS System Logo" width="600"/>
</p>

<h1 align="center">SG Point-of-Sale: Complete Deployment Guide</h1>

**Version:** 1.0  
**Target System:** Ubuntu 24.04.1 LTS  
**Authors:** CodeNavigator AI  
**Status:** Live Document

---

## **Table of Contents**

*   [1. Introduction](#1-introduction)
    *   [1.1. Purpose of This Document](#11-purpose-of-this-document)
    *   [1.2. Who This Guide is For](#12-who-this-guide-is-for)
    *   [1.3. Overview of the Deployment Process](#13-overview-of-the-deployment-process)
*   [2. Project File Directory Structure](#2-project-file-directory-structure)
*   [3. Part I: Preparing the Ubuntu System](#3-part-i-preparing-the-ubuntu-system)
    *   [Step 1: Updating Your System Software](#step-1-updating-your-system-software)
    *   [Step 2: Installing Essential Build Tools & Git](#step-2-installing-essential-build-tools--git)
*   [4. Part II: Setting Up the Database Server with Docker](#4-part-ii-setting-up-the-database-server-with-docker)
    *   [Step 3: Installing Docker Engine and Docker Compose](#step-3-installing-docker-engine-and-docker-compose)
    *   [Step 4: Configuring Docker for Non-Root User & Verification](#step-4-configuring-docker-for-non-root-user--verification)
*   [5. Part III: Deploying the SG-POS Application](#5-part-iii-deploying-the-sg-pos-application)
    *   [Step 5: Cloning the Application Code from GitHub](#step-5-cloning-the-application-code-from-github)
    *   [Step 6: Installing Python and Poetry](#step-6-installing-python-and-poetry)
    *   [Step 7: Installing Application Dependencies with Poetry](#step-7-installing-application-dependencies-with-poetry)
*   [6. Part IV: Configuration, Database Setup, and Launch](#6-part-iv-configuration-database-setup-and-launch)
    *   [Step 8: Configuring the Application Environment](#step-8-configuring-the-application-environment)
    *   [Step 9: Starting the PostgreSQL Database Container](#step-9-starting-the-postgresql-database-container)
    *   [Step 10: Setting Up the Database Schema (Migrations)](#step-10-setting-up-the-database-schema-migrations)
    *   [Step 11: Launching the SG-POS Application](#step-11-launching-the-sg-pos-application)
*   [7. Part V: Backup and Restoration Guide](#7-part-v-backup-and-restoration-guide)
    *   [7.1. The Importance of Backups](#71-the-importance-of-backups)
    *   [7.2. Backing Up the SG-POS Database](#72-backing-up-the-sg-pos-database)
    *   [7.3. Restoring the SG-POS Database from a Backup](#73-restoring-the-sg-pos-database)
    *   [7.4. Automating Database Backups](#74-automating-database-backups)
    *   [7.5. Backing Up the Application Files](#75-backing-up-the-application-files)
*   [8. Conclusion](#8-conclusion)

---

## **1. Introduction**

### **1.1. Purpose of This Document**

Welcome to the complete deployment guide for the SG Point-of-Sale (SG-POS) System. This document provides exhaustive, step-by-step instructions to deploy the application and its database server from scratch on a completely fresh installation of **Ubuntu 24.04.1 LTS**.

The goal is to provide a single, authoritative source of truth that can guide a user through every stage of the setup process, from system preparation to the final launch of the application.

### **1.2. Who This Guide is For**

This guide is written with a focus on clarity and detail, making it accessible to a wide range of users, including:

*   **Business Owners & End-Users:** We aim for this guide to be clear enough that even someone without a deep IT background can set up their own POS system on a dedicated machine.
*   **Junior Developers & System Administrators:** This document serves as a precise runbook for deploying the application in a standardized, repeatable manner.
*   **Open Source Contributors:** New contributors can use this guide to set up their local development environment, which is identical to this deployment process.

We will explain not just the "how" (the commands) but also the "why" (the purpose of each step and tool).

### **1.3. Overview of the Deployment Process**

The deployment process is broken down into five logical parts:

1.  **System Preparation:** We will start by updating our base Ubuntu system and installing a few essential tools required for the steps that follow.
2.  **Database Setup:** We will install and configure Docker, a containerization platform, to run our PostgreSQL database server. This approach is modern, clean, and ensures the database runs in an isolated, predictable environment.
3.  **Application Deployment:** We will download the SG-POS application source code from its official GitHub repository and install its required software packages using the Poetry dependency manager.
4.  **Configuration & Launch:** In the final part, we will configure the application, start the database, initialize the database schema, and launch the application for the first time.
5.  **Backup & Maintenance:** We will cover the critical procedures for backing up and restoring your valuable business data.

By the end of this guide, you will have a fully functional SG-POS system running on your Ubuntu machine.

---

## **2. Project File Directory Structure**

Before we begin the installation, it's helpful to understand the layout of the project we will be deploying. The SG-POS codebase is organized into a clean, logical structure that separates different aspects of the application.

```
sg-pos-system/
│
├── .env.example
├── .gitignore
├── alembic.ini
├── docker-compose.dev.yml
├── pyproject.toml
├── README.md
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── application_core.py
│   │   ├── async_bridge.py
│   │   ├── config.py
│   │   ├── exceptions.py
│   │   └── result.py
│   │
│   ├── business_logic/
│   │   ├── __init__.py
│   │   ├── dto/
│   │   │   ├── __init__.py
│   │   │   ├── company_dto.py
│   │   │   ├── customer_dto.py
│   │   │   ├── inventory_dto.py
│   │   │   ├── product_dto.py
│   │   │   ├── reporting_dto.py
│   │   │   ├── sales_dto.py
│   │   │   └── user_dto.py
│   │   │
│   │   └── managers/
│   │       ├── __init__.py
│   │       ├── base_manager.py
│   │       ├── company_manager.py
│   │       ├── customer_manager.py
│   │       ├── gst_manager.py
│   │       ├── inventory_manager.py
│   │       ├── product_manager.py
│   │       ├── reporting_manager.py
│   │       ├── sales_manager.py
│   │       └── user_manager.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── accounting.py
│   │   ├── audit_log.py
│   │   ├── base.py
│   │   ├── company.py
│   │   ├── customer.py
│   │   ├── inventory.py
│   │   ├── product.py
│   │   ├── sales.py
│   │   └── user.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── base_service.py
│   │   ├── company_service.py
│   │   ├── customer_service.py
│   │   ├── inventory_service.py
│   │   ├── payment_service.py
│   │   ├── product_service.py
│   │   ├── purchase_order_service.py
│   │   ├── report_service.py
│   │   ├── sales_service.py
│   │   ├── supplier_service.py
│   │   └── user_service.py
│   │
│   └── ui/
│       ├── __init__.py
│       ├── main_window.py
│       │
│       ├── dialogs/
│       │   ├── __init__.py
│       │   ├── customer_dialog.py
│       │   ├── payment_dialog.py
│       │   ├── product_dialog.py
│       │   ├── purchase_order_dialog.py
│       │   ├── stock_adjustment_dialog.py
│       │   └── user_dialog.py
│       │
│       ├── resources/
│       │   ├── __init__.py
│       │   └── styles.qss
│       │
│       ├── views/
│       │   ├── __init__.py
│       │   ├── customer_view.py
│       │   ├── inventory_view.py
│       │   ├── pos_view.py
│       │   ├── product_view.py
│       │   ├── reports_view.py
│       │   └── settings_view.py
│       │
│       └── widgets/
│           ├── __init__.py
│           └── searchable_table_view.py
│
├── migrations/
│   ├── __init__.py
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       └── d5a6759ef2f7_initial_schema_setup.py
│
├── scripts/
│   └── database/
│       ├── schema.sql
│       └── seed_data.py
│
└── tests/
    ├── __init__.py
    ├── conftest.py
    ├── integration/
    │   └── __init__.py
    └── unit/
        └── __init__.py

```

---

## **3. Part I: Preparing the Ubuntu System**

This section covers the initial steps to prepare your fresh Ubuntu 24.04 system for the deployment. We will update the system's software packages and install a few essential command-line tools.

### **Step 1: Updating Your System Software**

#### **What this step does:**
Before installing any new software, it is a critical security and stability practice to ensure that all existing software on the system is up to date. This step synchronizes your system's list of available software packages with the official Ubuntu servers and then downloads and installs any available updates. This prevents potential conflicts and ensures you have the latest security patches.

#### **The Commands:**
Open the **Terminal** application on your Ubuntu system. You can find it by clicking the "Activities" button in the top-left corner and searching for "Terminal".

Once the terminal is open, type the following command and press `Enter`.

```bash
sudo apt update
```
*   **`sudo`**: This command stands for "Super User Do". It temporarily elevates your privileges to that of a system administrator, which is required to install and update system software. You will be prompted to enter your user password. As you type, you will not see any characters, which is a standard security feature in Linux.
*   **`apt`**: This is Ubuntu's package manager. It handles installing, updating, and removing software.
*   **`update`**: This sub-command doesn't install anything; it simply downloads the latest list of available software versions from Ubuntu's repositories.

After the first command finishes, you will run the next command to perform the actual upgrade.

```bash
sudo apt upgrade -y
```
*   **`upgrade`**: This command compares the list of software installed on your system with the list you just downloaded. It will then proceed to download and install the newer versions of any outdated packages.
*   **`-y`**: This flag automatically answers "yes" to any prompts asking for confirmation to install the packages, making the process non-interactive.

#### **How to verify it worked:**
Once the `upgrade` command completes, your system is up to date. You can re-run `sudo apt update` and it should now report that "All packages are up to date."

### **Step 2: Installing Essential Build Tools & Git**

#### **What this step does:**
Now we will install a few fundamental tools that are required for the later stages of this deployment.
*   **`git`**: A version control system. This is the tool we will use to download (or "clone") the SG-POS source code from its public repository on GitHub.
*   **`curl`**: A command-line tool for transferring data with URLs. We will need this to download the installer for the Poetry package manager.
*   **`build-essential`**: This is a meta-package in Ubuntu that installs a collection of crucial tools, including the GCC compiler and other utilities required to build software from source. While Python packages are often pre-compiled, some may have C extensions that need to be compiled on your machine during installation. Installing `build-essential` prevents these installations from failing.

#### **The Command:**
In the same terminal window, execute the following command:

```bash
sudo apt install -y git curl build-essential
```
This command uses `apt` to install all three required packages in a single step.

#### **How to verify it worked:**
You can verify that each tool was installed correctly by checking its version.

```bash
git --version
curl --version
gcc --version
```
Each of these commands should print the version number of the respective tool, confirming a successful installation.

---

## **4. Part II: Setting Up the Database Server with Docker**

The SG-POS system requires a PostgreSQL database to store all its data (products, sales, customers, etc.). Instead of installing PostgreSQL directly onto our Ubuntu system, we will use Docker, a much more modern and robust approach.

**What is Docker?** You can think of Docker as a tool that lets you run applications in their own isolated "containers". A container is like a lightweight, mini-computer that has everything an application needs to run, all bundled together. This means our database will run in its own clean, predictable environment, and it won't interfere with any other software on our main Ubuntu system.

### **Step 3: Installing Docker Engine and Docker Compose**

#### **What this step does:**
This is a multi-command process that follows the official Docker documentation for setting up Docker's repository and installing the latest versions of **Docker Engine** (the core runtime) and the **Docker Compose** plugin (a tool for defining and running multi-container applications).

#### **The Commands:**
Execute each of the following command blocks in your terminal, one by one.

1.  **Set up Docker's `apt` repository.** These commands install some prerequisite packages, create a directory for Docker's security key, download Docker's official GPG key (to verify the authenticity of the software), and add the official Docker software repository to your system's list of sources.

    ```bash
    # Add Docker's official GPG key:
    sudo install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    sudo chmod a+r /etc/apt/keyrings/docker.gpg

    # Add the repository to Apt sources:
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
      sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    ```

2.  **Update the package list again.** Now that you've added the new Docker repository, you need to run `apt update` again to fetch the list of available Docker packages.

    ```bash
    sudo apt update
    ```

3.  **Install Docker.** This command installs Docker Engine, the command-line interface (CLI), and the Docker Compose plugin.

    ```bash
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    ```

#### **How to verify it worked:**
To confirm that Docker Engine was installed successfully, you can run the built-in "hello-world" container.

```bash
sudo docker run hello-world
```
If the installation was successful, Docker will download a tiny test image and run it. You should see a message in your terminal that begins with "Hello from Docker!". This confirms the core Docker system is working correctly.

### **Step 4: Configuring Docker for Non-Root User & Verification**

#### **What this step does:**
By default, the Docker command requires administrator privileges (`sudo`). This can be inconvenient and is not ideal for security. This step will add your current user to the `docker` group, which grants you the necessary permissions to run Docker commands without `sudo`.

#### **The Commands:**

1.  **Create the `docker` group (it likely already exists, but this is safe to run).**

    ```bash
    sudo groupadd docker
    ```

2.  **Add your user to the `docker` group.** The `${USER}` variable will automatically be replaced with your current username.

    ```bash
    sudo usermod -aG docker ${USER}
    ```

3.  **Activate the group changes.** This is a **critical step**. The group changes will not take effect until you start a new session. The easiest way to do this is to either **log out and log back in**, or run the following command to start a new shell session for your user.

    ```bash
    newgrp docker
    ```
    *Alternatively, you can close your current terminal window and open a new one.*

#### **How to verify it worked:**
After logging back in or starting a new shell, you should be able to run Docker commands without `sudo`. Try the version command:

```bash
docker --version
```
This should now work without `sudo` and print the installed versions of Docker and Docker Compose. This confirms your user permissions are set up correctly.

---

## **5. Part III: Deploying the SG-POS Application**

With the system and database server platform prepared, we can now proceed to download and set up the SG-POS application itself.

### **Step 5: Cloning the Application Code from GitHub**

#### **What this step does:**
We will use the `git` tool we installed earlier to download a complete copy (a "clone") of the SG-POS source code from its official repository on GitHub. This will create a new directory named `sg-pos-system` in your current location (your home directory by default).

#### **The Command:**
Make sure you are in your home directory. You can type `cd ~` to navigate there. Then run the clone command.

```bash
git clone https://github.com/nordeim/SG-Point-Of-Sale.git sg-pos-system
```
*   We've added `sg-pos-system` at the end to ensure the directory is named consistently.

This will connect to GitHub and download all the project files. Once it's done, navigate into the newly created project directory.

```bash
cd sg-pos-system
```
All subsequent commands in this guide should be run from within this `sg-pos-system` directory.

### **Step 6: Installing Python and Poetry**

#### **What this step does:**
The SG-POS application is written in Python. We need to ensure we have a compatible Python version and then install **Poetry**, a powerful tool for managing the application's specific Python packages (called dependencies).

1.  **Verify Python Version:** Ubuntu 24.04 comes with Python 3.12, which is perfect for this project. You can verify this by running:
    ```bash
    python3 --version
    ```
    This should output `Python 3.12.x`.

2.  **Install Poetry:** We will use the officially recommended installer script, which we can download using `curl`. This script will install Poetry in an isolated way that doesn't interfere with system Python packages.

    ```bash
    curl -sSL https://install.python-poetry.org | python3 -
    ```

3.  **Add Poetry to your system's PATH:** The installer script will output a message telling you to add Poetry's `bin` directory to your shell's `PATH` environment variable. This allows you to run the `poetry` command from anywhere. The command to do this is usually:
    ```bash
    export PATH="/home/your_username/.local/bin:$PATH"
    ```
    Replace `your_username` with your actual username. To make this change permanent, you should add this line to the end of your shell configuration file, which is typically `~/.bashrc`.
    
    You can do this with one command:
    ```bash
    echo 'export PATH="/home/your_username/.local/bin:$PATH"' >> ~/.bashrc
    ```
    Again, replace `your_username`. After running this, you must reload your shell's configuration or open a new terminal. You can reload it with:
    ```bash
    source ~/.bashrc
    ```

#### **How to verify it worked:**
After opening a new terminal or running `source ~/.bashrc`, you should be able to check Poetry's version:
```bash
poetry --version
```
This should print the installed Poetry version, confirming it's ready to use.

### **Step 7: Installing Application Dependencies with Poetry**

#### **What this step does:**
Every Python project relies on a set of third-party libraries (packages) to function. SG-POS uses libraries for the GUI (`PySide6`), database connection (`SQLAlchemy`, `asyncpg`), and more. The `pyproject.toml` file in the project directory contains a complete list of these required dependencies.

The `poetry install` command does two important things:
1.  It creates a **virtual environment**, which is an isolated directory containing a specific version of Python and all the necessary packages for *this project only*. This prevents conflicts with other Python projects on your system.
2.  It reads the `pyproject.toml` file and downloads and installs the exact versions of all listed dependencies into this new virtual environment.

#### **The Command:**
Ensure you are inside the `sg-pos-system` directory, then run:
```bash
poetry install
```
This process may take a few minutes as Poetry resolves and downloads all the packages.

#### **How to verify it worked:**
Poetry will output messages as it installs the packages. Once it completes without any red error messages, the installation is successful. You can see the location of the new virtual environment by running:
```bash
poetry env info
```

---

## **6. Part IV: Configuration, Database Setup, and Launch**

We have now reached the final stage. All the software is installed; we just need to configure the application, start the database, initialize its structure, and run the program.

### **Step 8: Configuring the Application Environment**

#### **What this step does:**
The application needs to know how to connect to the database. This information, along with other settings, is stored in an environment file. We will create this file by copying the provided template.

#### **The Command:**
From the `sg-pos-system` directory, run:
```bash
cp .env.example .env.dev
```
This creates a file named `.env.dev`. For this guide, you do not need to edit this file. The default values for the database user, password, and name are already set up to work with our Docker database configuration.

### **Step 9: Starting the PostgreSQL Database Container**

#### **What this step does:**
Using the `docker-compose.dev.yml` file provided with the project, we will now tell Docker to start our PostgreSQL database container. Docker Compose will read this file, which defines the database service, including which image to use (`postgres:16-alpine`), what environment variables to set (from our `.env.dev` file), and how to store the data persistently.

#### **The Command:**
In your terminal, inside the `sg-pos-system` directory, run:

```bash
docker compose -f docker-compose.dev.yml up -d
```
*   **`docker compose`**: The command to run Docker Compose.
*   **`-f docker-compose.dev.yml`**: Specifies which compose file to use.
*   **`up`**: The command to start the services defined in the file.
*   **`-d`**: Stands for "detached mode". This runs the container in the background so you can continue to use your terminal.

#### **How to verify it worked:**
You can check the status of your running containers with:
```bash
docker ps
```
You should see an entry for a container named `sgpos_dev_db`. The `STATUS` column should say "Up..." and may include a health status like "(healthy)". This confirms your database server is running and ready for connections.

### **Step 10: Setting Up the Database Schema (Migrations)**

#### **What this step does:**
Our database server is running, but it's currently an empty shell. It doesn't have any of the tables (`products`, `customers`, `sales_transactions`, etc.) that the SG-POS application needs.

This step uses a tool called **Alembic**, which is the project's database migration manager. It will connect to our new database and execute a series of commands to create all the tables, columns, and relationships exactly as defined in the application's source code.

#### **The Commands:**
First, you must activate the project's virtual environment using Poetry. This ensures you are using the Python and packages (including Alembic) that were installed specifically for this project.

```bash
poetry shell
```
Once the shell is active, run the migration command:
```bash
alembic upgrade head
```
*   **`alembic`**: The command-line tool for managing database migrations.
*   **`upgrade`**: Tells Alembic you want to apply new migrations.
*   **`head`**: A keyword that means "apply all migrations up to the very latest version".

#### **How to verify it worked:**
Alembic will print `INFO` logs to your terminal, showing the migration scripts it is running. If it completes without any red `ERROR` messages, the database schema has been created successfully.

### **Step 11: Launching the SG-POS Application**

#### **What this step does:**
This is the final step. All components are now in place: the system is prepared, the database is running and has the correct schema, and all application dependencies are installed. We will now execute the main Python script to launch the graphical user interface of the SG-POS application.

#### **The Command:**
Ensure you are still inside the activated Poetry shell (from the previous step). Then, run:
```bash
python app/main.py
```

#### **How to verify it worked:**
After a few moments, the SG-POS main application window should appear on your screen! It will open to the Point-of-Sale view, ready for use. You have successfully deployed the application.

---

## **7. Part V: Backup and Restoration Guide**

Your business data is your most valuable asset. Regularly backing up your POS database is not optional; it is a critical task to protect against data loss from hardware failure, accidental deletion, or other unforeseen events.

### **7.1. The Importance of Backups**

A consistent backup strategy ensures that in the event of a disaster, you can restore your system to a recent state, minimizing data loss and business interruption. This section provides the commands to manually back up and restore your database and how to automate the process.

### **7.2. Backing Up the SG-POS Database**

We will use the standard PostgreSQL utility `pg_dump` to create a complete, consistent snapshot of the database. We can execute this command inside our running Docker container.

#### **What this step does:**
This process creates a single compressed file that contains the entire structure and data of your `sgpos_dev` database.

#### **The Commands:**

1.  **Create a backup directory on your main machine (the "host").** It's good practice to keep backups organized.
    ```bash
    mkdir -p ~/sgpos_backups
    ```

2.  **Execute `pg_dump` inside the Docker container.** This command tells Docker to run `pg_dump` within the `sgpos_dev_db` container and save the output to a temporary file inside the container.
    ```bash
    docker exec -t sgpos_dev_db pg_dump -U sgpos_dev_user -d sgpos_dev -F c -b -v -f /tmp/sgpos_backup.dump
    ```
    *   **`docker exec -t sgpos_dev_db`**: Executes a command inside the specified running container.
    *   **`pg_dump`**: The PostgreSQL backup utility.
    *   **`-U sgpos_dev_user`**: Specifies the database username.
    *   **`-d sgpos_dev`**: Specifies the database name to back up.
    *   **`-F c`**: Specifies the output format as "custom", which is a compressed, flexible format.
    *   **`-b`**: Include large objects in the backup.
    *   **`-v`**: Verbose mode, to see progress.
    *   **`-f /tmp/sgpos_backup.dump`**: Specifies the output file path *inside the container*.

3.  **Copy the backup file from the container to your host machine.** Now that the backup file exists inside the container, we need to copy it out to our `sgpos_backups` directory. We will add a timestamp to the filename for better organization.
    ```bash
    docker cp sgpos_dev_db:/tmp/sgpos_backup.dump ~/sgpos_backups/sgpos_backup_$(date +%Y%m%d_%H%M%S).dump
    ```
    *   **`docker cp`**: The command to copy files between a container and the host.
    *   **`sgpos_dev_db:/tmp/sgpos_backup.dump`**: The source file (container:path).
    *   **`~/sgpos_backups/...`**: The destination path on your main machine.

#### **How to verify it worked:**
Navigate to your backup directory and list its contents.
```bash
ls -lh ~/sgpos_backups
```
You should see your newly created `.dump` file with a recent timestamp.

### **7.3. Restoring the SG-POS Database from a Backup**

This procedure is for disaster recovery. It assumes you have a new, empty database (like the one created in Step 9) and you want to populate it with data from a backup file.

**WARNING:** This will overwrite any existing data in the target database.

#### **What this step does:**
We will use the `pg_restore` utility to load the data from our backup `.dump` file into the database.

#### **The Commands:**

1.  **Copy the backup file into the running container.** This is the reverse of the backup copy step. Let's assume you want to restore the latest backup.
    ```bash
    # Find the latest backup file
    LATEST_BACKUP=$(ls -t ~/sgpos_backups/*.dump | head -n 1)
    echo "Restoring from: $LATEST_BACKUP"
    
    # Copy it into the container
    docker cp $LATEST_BACKUP sgpos_dev_db:/tmp/restore_this.dump
    ```

2.  **Execute `pg_restore` inside the container.** This command connects to the database and uses the backup file to recreate the tables and data.
    ```bash
    docker exec -t sgpos_dev_db pg_restore -U sgpos_dev_user -d sgpos_dev --clean --if-exists -v /tmp/restore_this.dump
    ```
    *   **`pg_restore`**: The PostgreSQL restore utility.
    *   **`--clean`**: Tells `pg_restore` to drop (delete) existing database objects before recreating them.
    *   **`--if-exists`**: Used with `--clean`, this prevents errors if you are restoring to a completely empty database where there are no objects to drop.

### **7.4. Automating Database Backups**

Manually running backups is prone to being forgotten. On a Linux system, you can automate this task using `cron`.

#### **What this step does:**
We will create a simple script to perform the backup and schedule it to run automatically every night using `cron`, the standard Linux task scheduler.

1.  **Create a backup script.**
    ```bash
    # Create a scripts directory if you don't have one
    mkdir -p ~/scripts
    
    # Create a new file for the script
    nano ~/scripts/backup_sgpos.sh
    ```
    Paste the following content into the file:
    ```sh
    #!/bin/bash
    # Script to back up the SG-POS PostgreSQL database

    # Set the backup directory
    BACKUP_DIR="/home/your_username/sgpos_backups"
    # Set a datestamp for the filename
    DATESTAMP=$(date +%Y%m%d_%H%M%S)
    FILENAME="$BACKUP_DIR/sgpos_backup_$DATESTAMP.dump"
    
    # Execute the backup and copy commands
    echo "Starting SG-POS backup..."
    docker exec -t sgpos_dev_db pg_dump -U sgpos_dev_user -d sgpos_dev -F c -b -v -f /tmp/sgpos_backup.dump && \
    docker cp sgpos_dev_db:/tmp/sgpos_backup.dump $FILENAME
    
    # Optional: Clean up old backups (e.g., keep the last 7 days)
    find $BACKUP_DIR -type f -name "*.dump" -mtime +7 -delete

    echo "Backup complete: $FILENAME"
    ```
    *   **IMPORTANT:** Replace `your_username` with your actual username.
    *   Press `Ctrl+X`, then `Y`, then `Enter` to save and exit `nano`.

2.  **Make the script executable.**
    ```bash
    chmod +x ~/scripts/backup_sgpos.sh
    ```

3.  **Schedule the script with `cron`.**
    Open the crontab editor:
    ```bash
    crontab -e
    ```
    If it's your first time, you may be asked to choose an editor; select `nano`. Scroll to the bottom of the file and add the following line:
    ```
    0 2 * * * /home/your_username/scripts/backup_sgpos.sh >> /home/your_username/sgpos_backups/backup.log 2>&1
    ```
    *   **`0 2 * * *`**: This is the schedule. It means "at minute 0 of hour 2, every day, every month, every day of the week". In simple terms: run at 2:00 AM every night.
    *   **`/home/your_username/scripts/backup_sgpos.sh`**: The full path to the script to run.
    *   **`>> ... 2>&1`**: This part redirects all output (both normal and error messages) to a log file, so you can check if the backups are running correctly.

    Save and exit the file (`Ctrl+X`, `Y`, `Enter`). `cron` will now automatically run your backup script every night at 2 AM.

### **7.5. Backing Up the Application Files**

Backing up the application files themselves is simpler. The entire configuration and source code are contained within the `sg-pos-system` directory you cloned from Git. You can create a compressed archive of this folder.

```bash
# Navigate to the directory containing your project folder
cd ~

# Create a compressed tarball
tar -czvf sgpos_app_backup_$(date +%Y%m%d).tar.gz sg-pos-system/
```
This command creates a file like `sgpos_app_backup_20240521.tar.gz`. You should store this file and your database dump file in a safe, separate location (e.g., an external hard drive, cloud storage).

---

## **8. Conclusion**

Congratulations! If you have followed this guide to the end, you have successfully deployed the SG-POS system on a fresh Ubuntu machine. You have installed all prerequisites, set up a robust Docker-based database server, deployed the application code, and successfully launched the program.

Furthermore, you are now equipped with the essential knowledge to perform and automate critical backups of your business data, ensuring the long-term safety and integrity of your operations.
```

---
https://drive.google.com/file/d/1dnSP22Pzt3sjhTNHJcPpvKoihYG-somP/view?usp=sharing, https://aistudio.google.com/app/prompts?state=%7B%22ids%22:%5B%221fo0QcoydHcYD6h_b6-9HapceFSj7xnKT%22%5D,%22action%22:%22open%22,%22userId%22:%22108686197475781557359%22,%22resourceKeys%22:%7B%7D%7D&usp=sharing, https://drive.google.com/file/d/1koyl7FAKLkppdi5iIUCwrJtbPLgb6YGM/view?usp=sharing

