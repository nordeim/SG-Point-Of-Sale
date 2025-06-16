# **SG-POS System: UAT Deployment & Environment Setup Guide**

**Document Version:** 1.0  
**Date:** June 16, 2025  
**Author:** CodeNavigator AI  
**Audience:** System Administrators, DevOps Engineers, QA Team Leads

## **Table of Contents**

1.  [**Introduction**](#1-introduction)
    *   1.1. Purpose of This Document
    *   1.2. UAT Environment Architecture Overview
2.  [**Part 1: Server and Environment Prerequisites**](#part-1-server-and-environment-prerequisites)
    *   2.1. Server Specifications
    *   2.2. Required Software & Dependencies
    *   2.3. Network and Firewall Configuration
3.  [**Part 2: Database Setup - Production-Grade PostgreSQL**](#part-2-database-setup---production-grade-postgresql)
    *   3.1. Installing PostgreSQL
    *   3.2. Initial Database Hardening
    *   3.3. Creating the UAT Database and User
4.  [**Part 3: Application Deployment**](#part-3-application-deployment)
    *   4.1. Cloning the Application Repository
    *   4.2. Python Environment Setup with Poetry
    *   4.3. Application Configuration (`.env.uat`)
    *   4.4. Database Schema Migration and Seeding
5.  [**Part 4: Running and Managing the Application**](#part-4-running-and-managing-the-application)
    *   5.1. Running the Application for a UAT Session
    *   5.2. Running as a System Service (Optional, for persistent UAT)
    *   5.3. Log Monitoring and Troubleshooting
6.  [**Part 5: Verification and Handover**](#part-5-verification-and-handover)
    *   6.1. UAT Environment Sanity Checklist
    *   6.2. Access Credentials and Handover to QA Team
7.  [**Appendix**](#7-appendix)
    *   A.1. Sample `.env.uat` Configuration File
    *   A.2. Troubleshooting Common Issues

---

## **1. Introduction**

### 1.1. Purpose of This Document

This guide provides comprehensive, step-by-step instructions for deploying the SG Point-of-Sale (SG-POS) System into a dedicated **User Acceptance Testing (UAT)** environment. This environment is designed to be a stable, production-like replica where business stakeholders, end-users, and the QA team can conduct final testing before a production release.

Adherence to these instructions is critical to ensure a consistent, secure, and reliable testing environment that accurately mirrors the intended production setup. This document is intended for personnel with system administration experience on Linux-based operating systems.

### 1.2. UAT Environment Architecture Overview

The UAT environment consists of two primary components, which can be deployed on a single server or on separate dedicated servers for higher fidelity testing. For most UAT scenarios, a single, robust server is sufficient.

1.  **Application Server:** A machine that hosts the SG-POS Python application. For a desktop application like SG-POS, this will be the "client" machine where testers will physically or remotely access the GUI.
2.  **Database Server:** A server running a production-grade PostgreSQL 15+ database instance, which will store all application data.

**Deployment Model for this Guide:**
This guide will assume a **single-server deployment model**, where both the PostgreSQL database and the SG-POS application reside on the same server. This is a common and cost-effective setup for UAT. Instructions will be provided for Ubuntu 22.04 LTS, but can be adapted for other modern Linux distributions (e.g., RHEL, CentOS).

```mermaid
graph TD
    subgraph "UAT Server (Ubuntu 22.04 LTS)"
        subgraph "SG-POS Application Environment"
            A[Python 3.11+ via pyenv]
            B[Poetry for Dependency Management]
            C[SG-POS Application Codebase]
        end
        
        subgraph "Database Environment"
            D[(PostgreSQL 15+ Server)]
            E[sgpos_uat Database]
        end
        
        C -- "Connects via localhost to" --> E
    end

    UAT_Tester(UAT Tester) -- "Accesses GUI via VNC / Remote Desktop / Physical Access" --> C
```

---

## **Part 1: Server and Environment Prerequisites**

Before beginning the deployment, ensure the target server meets the following requirements.

### 2.1. Server Specifications

*   **Operating System:** Ubuntu 22.04 LTS (or a compatible modern Linux distribution).
*   **CPU:** 2+ vCPUs (4+ recommended for smoother GUI performance).
*   **RAM:** 4 GB minimum (8 GB recommended).
*   **Storage:** 20 GB+ SSD storage.
*   **User Access:** A non-root user with `sudo` privileges. This guide will assume the user is named `uat_admin`.

### 2.2. Required Software & Dependencies

The following software must be installed on the UAT server. We will install these in the subsequent steps.

*   **Core Build Tools:** `build-essential`, `libssl-dev`, `zlib1g-dev`, `libbz2-dev`, `libreadline-dev`, `libsqlite3-dev`, `wget`, `curl`, `llvm`, `libncurses5-dev`, `xz-utils`, `tk-dev`, `libxml2-dev`, `libxmlsec1-dev`, `libffi-dev`, `liblzma-dev`.
*   **Git:** For cloning the application repository.
*   **pyenv:** For managing Python versions in isolation, a best practice to avoid conflicts with the system's default Python.
*   **Poetry:** For managing Python project dependencies.
*   **PostgreSQL:** The database server and client tools.
*   **Desktop Environment (for GUI access):** A lightweight desktop environment (e.g., XFCE4) and a remote access tool (e.g., TigerVNC) are required for testers to interact with the PySide6 application.

### 2.3. Network and Firewall Configuration

*   **Inbound Ports:**
    *   **SSH (Port 22):** Must be open to allow administrative access. It is highly recommended to restrict access to specific trusted IP addresses.
    *   **VNC (Port 5901+):** If using VNC for remote GUI access, the corresponding port must be open and restricted to tester IP addresses.
*   **Outbound Ports:** The server must have general outbound access to the internet (Ports 80, 443) to download software packages and clone the Git repository.
*   **Firewall:** It is strongly recommended to use `ufw` (Uncomplicated Firewall) to manage these rules.

**Action: Initial Firewall Setup**
```bash
# Allow SSH access (replace 'from any' with 'from your_ip' for better security)
sudo ufw allow from any to any port 22 proto tcp

# Allow VNC access for the first user display :1 (replace 'from any' with 'from trusted_ips')
sudo ufw allow from any to any port 5901 proto tcp

# Enable the firewall
sudo ufw enable
```

---

## **Part 2: Database Setup - Production-Grade PostgreSQL**

This section details the installation and secure configuration of the PostgreSQL database server.

### 3.1. Installing PostgreSQL

We will install PostgreSQL from its official repository to ensure we have the latest stable and secure version.

**Action: Update Server and Install PostgreSQL**
```bash
# 1. Update package lists and upgrade existing packages
sudo apt update && sudo apt upgrade -y

# 2. Install prerequisite packages
sudo apt install -y gnupg2 wget

# 3. Import the PostgreSQL repository signing key
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -

# 4. Add the PostgreSQL repository to your system's sources list
echo "deb http://apt.postgresql.org/pub/repos/apt/ $(lsb_release -cs)-pgdg main" | sudo tee /etc/apt/sources.list.d/pgdg.list

# 5. Update package lists again to include the new repository
sudo apt update

# 6. Install the PostgreSQL server and its contributions package
sudo apt install -y postgresql-15 postgresql-contrib-15
```

**Verification:**
```bash
# Check that the PostgreSQL service is active and running
sudo systemctl status postgresql
# You should see 'active (exited)'. This is normal.
```

### 3.2. Initial Database Hardening

A default PostgreSQL installation is only accessible from the local machine. While our deployment model is single-server, it's good practice to review the configuration. For UAT, the default local access is sufficient and secure.

### 3.3. Creating the UAT Database and User

For security, the application must not connect as the `postgres` superuser. We will create a dedicated database and user for the UAT environment.

**Action: Create Database and User**
```bash
# 1. Switch to the 'postgres' system user
sudo -i -u postgres

# 2. Start the PostgreSQL interactive terminal
psql

# 3. Create a dedicated user for the UAT application.
# IMPORTANT: Replace 'a_very_strong_uat_password' with a strong, unique password.
# Store this password securely as it will be used in the .env.uat file.
CREATE ROLE sgpos_uat_user WITH LOGIN PASSWORD 'a_very_strong_uat_password';

# 4. Create the UAT database and assign the new user as its owner.
CREATE DATABASE sgpos_uat OWNER sgpos_uat_user;

# 5. Exit the psql terminal and the postgres user session
\q
exit
```

**Verification:**
```bash
# From your 'uat_admin' user session, try to connect to the new database as the new user
psql -h localhost -U sgpos_uat_user -d sgpos_uat
# You will be prompted for the password. If you can connect successfully, the setup is correct.
# Type '\q' to exit.
```

---

## **Part 3: Application Deployment**

This section details the process of getting the application code onto the server, setting up the Python environment, and configuring it to connect to the database.

### 4.1. Cloning the Application Repository

**Action: Install Git and Clone the Repository**
```bash
# 1. Install Git
sudo apt install -y git

# 2. Clone the project repository into the uat_admin's home directory
# Replace <repo_url> with the actual URL of your GitHub repository
cd ~
git clone <repo_url> sg-pos-system
cd sg-pos-system
```

### 4.2. Python Environment Setup with Poetry

We will use `pyenv` to install Python 3.11 and `poetry` to manage the project dependencies, ensuring a clean and isolated environment.

**Action: Install `pyenv` and Project Dependencies**
```bash
# 1. Install pyenv prerequisites
sudo apt install -y build-essential libssl-dev zlib1g-dev libbz2-dev \
libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev xz-utils \
tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev

# 2. Install pyenv using the official installer script
curl https://pyenv.run | bash

# 3. Add pyenv to the shell environment.
# This appends the necessary configuration to your ~/.bashrc file.
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc

# 4. Apply the changes to the current shell session
# IMPORTANT: You must either source the file or log out and log back in.
exec "$SHELL"

# 5. Verify pyenv installation
pyenv --version

# 6. Install Python 3.11.x (or the latest 3.11 patch version)
pyenv install 3.11

# 7. Set the local Python version for the project directory.
# This creates a .python-version file that pyenv and poetry will automatically use.
cd ~/sg-pos-system
pyenv local 3.11

# 8. Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# 9. Add Poetry to your PATH in .bashrc (the installer provides this command)
# The exact path may vary slightly, check the installer output.
echo 'export PATH="/home/uat_admin/.local/bin:$PATH"' >> ~/.bashrc

# 10. Apply the changes again to the current shell session
exec "$SHELL"

# 11. Verify Poetry installation
poetry --version

# 12. Configure Poetry to create virtual environments inside the project directory
cd ~/sg-pos-system
poetry config virtualenvs.in-project true

# 13. Install all project dependencies (including dev dependencies for potential debugging)
poetry install
```

### 4.3. Application Configuration (`.env.uat`)

We need to create a dedicated environment configuration file for UAT.

**Action: Create and Configure `.env.uat`**
```bash
# 1. Navigate to the project directory
cd ~/sg-pos-system

# 2. Copy the example environment file to a new .env.uat file
cp .env.example .env.uat

# 3. Edit the .env.uat file with the correct UAT settings
nano .env.uat
```

**File Content for `.env.uat`:**
Edit the file to match the following, replacing `a_very_strong_uat_password` with the password you created in Step 3.3.

```env
# SG-POS UAT Environment Configuration

# --- PostgreSQL Database Configuration ---
POSTGRES_USER=sgpos_uat_user
POSTGRES_PASSWORD=a_very_strong_uat_password
POSTGRES_DB=sgpos_uat

# --- Application Configuration ---
DATABASE_URL="postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@localhost:5432/${POSTGRES_DB}"

# Application-level settings
APP_ENV=uat
DEBUG=False
LOG_LEVEL=INFO
SECRET_KEY=a_strong_and_unique_secret_key_for_uat

# --- Context IDs for UAT (can be pre-seeded entities) ---
CURRENT_COMPANY_ID=... # Replace with the UUID of a seeded UAT company
CURRENT_OUTLET_ID=...  # Replace with the UUID of a seeded UAT outlet
CURRENT_USER_ID=...    # Replace with the UUID of a seeded UAT user
```

### 4.4. Database Schema Migration and Seeding

With the application configured, we apply the database schema and populate it with initial data for testing.

**Action: Run Migrations and Seed Data**
```bash
# 1. Ensure you are in the project directory
cd ~/sg-pos-system

# 2. Activate the Poetry environment if not already active.
# The 'exec "$SHELL"' commands should have handled this, but this is a good check.
# This is equivalent to `poetry shell` in older versions.
source .venv/bin/activate

# 3. Apply all database migrations to create the schema.
# This uses the settings in alembic.ini and the DATABASE_URL from .env.uat (loaded by env.py).
# We need to tell our config loader to use .env.uat instead of .env.dev.
# For simplicity, we can temporarily rename .env.uat to .env.dev for the migration
mv .env.uat .env.dev
alembic upgrade head
mv .env.dev .env.uat # Rename back

# 4. (Optional but Recommended) Seed the database with UAT-specific data.
# This script should be designed to create a baseline set of products, users,
# customers, and suppliers for testers.
# We also need to point our config loader to the UAT file.
# The most robust way is to modify the config loader temporarily or use env vars.
# Let's use an environment variable for clarity.
export DOTENV_FILE=.env.uat
python scripts/database/seed_data.py
unset DOTENV_FILE # Unset the variable
```

**Note on Configuration:** For a more robust setup, `app/core/config.py` could be modified to read `DOTENV_FILE` from the environment to determine which `.env` file to load, removing the need for renaming files.

---

## **Part 4: Running and Managing the Application**

### 5.1. Running the Application for a UAT Session

Testers will need GUI access. This typically involves installing a lightweight desktop environment and a VNC server.

**Action: Setup GUI and VNC Server**
```bash
# 1. Install XFCE4 desktop environment and TigerVNC server
sudo apt install -y xfce4 xfce4-goodies tigervnc-standalone-server

# 2. Configure VNC server password for the first time for the uat_admin user
# You will be prompted to set a password. This is what testers will use to connect.
vncserver

# 3. Kill the initial VNC server instance to configure it
vncserver -kill :1

# 4. Configure the VNC server to start the XFCE4 desktop
# Create and edit the xstartup file
nano ~/.vnc/xstartup

# Make the file content look exactly like this:
#!/bin/bash
xrdb $HOME/.Xresources
startxfce4 &

# 5. Make the xstartup file executable
chmod +x ~/.vnc/xstartup

# 6. Start the VNC server again, specifying screen geometry
vncserver -geometry 1920x1080 -depth 24
```

**Action: Running the SG-POS Application**

1.  **For the Administrator:** You can now connect to the server using a VNC client (e.g., TigerVNC Viewer, RealVNC) at the address `your_server_ip:1`.
2.  **Inside the VNC session (remote desktop):**
    *   Open a Terminal emulator.
    *   Navigate to the project directory: `cd ~/sg-pos-system`
    *   Activate the Poetry environment: `source .venv/bin/activate`
    *   Set the environment file variable: `export DOTENV_FILE=.env.uat`
    *   Launch the application: `python app/main.py`

The SG-POS application GUI should now appear on the remote desktop, ready for testing.

### 5.2. Running as a System Service (Optional, for persistent UAT)

For a more stable UAT environment where the application doesn't need to be manually started, you can create a `.desktop` file.

**Action: Create a Desktop Shortcut**
```bash
# Create a .desktop file
nano ~/Desktop/sg-pos-uat.desktop

# Add the following content:
[Desktop Entry]
Version=1.0
Type=Application
Name=SG-POS UAT
Comment=SG Point-of-Sale UAT Environment
Exec=bash -c "cd /home/uat_admin/sg-pos-system && source .venv/bin/activate && export DOTENV_FILE=.env.uat && python app/main.py"
Icon=/path/to/your/app_icon.png # Optional: specify an icon
Terminal=false
StartupNotify=true

# Make the shortcut executable
chmod +x ~/Desktop/sg-pos-uat.desktop
```
Testers can now simply double-click this icon on the remote desktop to launch the application.

### 5.3. Log Monitoring and Troubleshooting

*   **Application Logs:** Logs will be printed to the terminal where the application was launched. For more persistent logging, the application should be configured to log to a file (e.g., in `app/core/logging_setup.py`).
*   **Troubleshooting:**
    *   If the GUI does not appear, check for PySide6 or Qt-related errors in the terminal. Ensure all dependencies from `poetry install` were successful.
    *   If there are database connection errors, verify the credentials and URL in `.env.uat` and ensure the PostgreSQL service is running (`sudo systemctl status postgresql`).

---

## **Part 5: Verification and Handover**

### 6.1. UAT Environment Sanity Checklist

Before handing over the environment to the QA team, verify the following:

*   [✔] The server is accessible via SSH.
*   [✔] The VNC server is running and accessible from a tester's machine.
*   [✔] The PostgreSQL database `sgpos_uat` exists and is owned by `sgpos_uat_user`.
*   [✔] The `alembic_version` table exists in the `sgpos_uat` database and shows the latest migration revision.
*   [✔] The `sg-pos-uat.desktop` shortcut successfully launches the application.
*   [✔] The application launches without any immediate errors in the terminal.
*   [✔] The application's main window appears, and it is possible to navigate to different views (Products, Customers, etc.).
*   [✔] Data seeded in Step 4.4 is visible in the application's UI.

### 6.2. Access Credentials and Handover to QA Team

Provide the following information securely to the QA and UAT teams:

*   **Server IP Address:** `xxx.xxx.xxx.xxx`
*   **SSH User:** `uat_admin`
*   **VNC Access:** `your_server_ip:1`
*   **VNC Password:** The password set in Step 5.1.
*   **Application Test User Credentials:** Usernames and passwords for seeded test accounts (e.g., `cashier_chloe`, `manager_darren`) as created by the `seed_data.py` script.

The environment is now ready for User Acceptance Testing.

---

## **7. Appendix**

### A.1. Sample `.env.uat` Configuration File

```env
# SG-POS UAT Environment Configuration

# --- PostgreSQL Database Configuration ---
POSTGRES_USER=sgpos_uat_user
POSTGRES_PASSWORD=a_very_strong_uat_password
POSTGRES_DB=sgpos_uat

# --- Application Configuration ---
DATABASE_URL="postgresql+asyncpg://sgpos_uat_user:a_very_strong_uat_password@localhost:5432/sgpos_uat"

# Application-level settings
APP_ENV=uat
DEBUG=False
LOG_LEVEL=INFO
SECRET_KEY=a_strong_and_unique_secret_key_for_uat_phase_1

# --- Context IDs for UAT (can be pre-seeded entities) ---
# These should match UUIDs created by your seed_data.py script
CURRENT_COMPANY_ID=f47ac10b-58cc-4372-a567-0e02b2c3d479
CURRENT_OUTLET_ID=e1b2c3d4-a567-4890-b1c2-d3e4f5a6b7c8
CURRENT_USER_ID=98a7b6c5-d4e3-4f2a-b1c0-d9e8f7a6b5c4
```

### A.2. Troubleshooting Common Issues

*   **`ModuleNotFoundError` when running `python app/main.py`:** Ensure the Poetry virtual environment is activated (`source .venv/bin/activate`).
*   **`psycopg2.OperationalError: connection to server ... failed`:** Verify that the PostgreSQL server is running (`sudo systemctl status postgresql`) and that the credentials in `.env.uat` are correct.
*   **VNC Connection Refused:** Ensure the firewall rule for port 5901 is active (`sudo ufw status`) and that you are connecting to the correct IP address and display number (e.g., `ip_address:1`).
*   **Alembic Errors:** If `alembic upgrade head` fails, ensure the database is clean (`DROP SCHEMA sgpos CASCADE; CREATE SCHEMA sgpos;`) and that all previous steps (especially `poetry install` and environment activation) were completed successfully.

