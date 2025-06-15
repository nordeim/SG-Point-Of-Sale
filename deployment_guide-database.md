My validation process for this schema involved:
*   **Completeness Check:** Ensuring that every functional requirement from the PRD (e.g., multi-tenancy, product variants, GST, auditing, accounting) has corresponding tables and relationships.
*   **Structural Integrity Analysis:** Verifying normalization principles, referential integrity (foreign keys), and the correct application of constraints (`UNIQUE`, `CHECK`).
*   **Syntactic Validation:** Ensuring the DDL (Data Definition Language) script is syntactically correct for PostgreSQL 15+ and follows modern SQL best practices.
*   **Architectural Alignment:** Confirming that the schema design supports the layered architecture, particularly by using non-business-logic keys (`UUID`) and providing a solid foundation for the data access layer.
*   **Best Practices Review:** Incorporating professional-grade features like a dedicated audit table, `TIMESTAMPTZ` for all timestamps, `NUMERIC` for financial data, and a separate `sgpos` schema for namespacing.

The schema is production-ready and provides a robust foundation for the SG-POS application.

Following this confirmation, here is the detailed, step-by-step guide for deploying this PostgreSQL database schema.

---

### **Deployment Guide: PostgreSQL Database for SG-POS System**

```md
# DEPLOYMENT GUIDE: PostgreSQL Database for the SG-POS System

## 1. Introduction

This document provides a comprehensive, step-by-step guide for deploying and configuring a PostgreSQL database server to be used by the SG Point-of-Sale (SG-POS) application. This guide is intended for system administrators or developers setting up a production or staging environment.

The instructions are based on **Ubuntu 22.04 LTS**, a common and stable server operating system, but can be adapted for other Linux distributions or cloud database services.

## 2. Prerequisites

Before you begin, ensure you have the following:

1.  **A Server:** A dedicated server (virtual or physical) running a fresh installation of Ubuntu 22.04 LTS.
2.  **Sudo Access:** A user account with `sudo` privileges.
3.  **The Schema File:** Access to the complete `schema.sql` file containing the DDL for the SG-POS database.
4.  **Application Server IP Address:** The IP address of the server where the SG-POS application will be running. If the database and application are on the same server, this will be `127.0.0.1`.

## 3. Part 1: Installing PostgreSQL

First, we will install the latest version of PostgreSQL from its official repository to ensure we have the most up-to-date and secure version.

### Step 1.1: Update Your Server

Always start by updating your server's package index.
```bash
sudo apt update
sudo apt upgrade -y
```

### Step 1.2: Add the PostgreSQL Repository

Import the PostgreSQL repository signing key and add the repository to your system's sources list.
```bash
# Install required packages for managing repositories
sudo apt install -y gnupg2 wget

# Import the repository signing key
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -

# Add the PostgreSQL repository
echo "deb http://apt.postgresql.org/pub/repos/apt/ $(lsb_release -cs)-pgdg main" | sudo tee /etc/apt/sources.list.d/pgdg.list
```

### Step 1.3: Install PostgreSQL Server

Now, install PostgreSQL 15 (or the latest stable version).
```bash
sudo apt update
sudo apt install -y postgresql-15 postgresql-contrib-15
```

### Step 1.4: Verify the Installation

Check that the PostgreSQL service is running and enabled to start on boot.
```bash
sudo systemctl status postgresql
```
You should see an `active (exited)` status, which is normal. The main service starts automatically when a connection is made. To be sure, check the running cluster:
```bash
pg_lsclusters
```

## 4. Part 2: Creating the Production Database and User

For security, the application should not connect as the `postgres` superuser. We will create a dedicated database and a dedicated user with specific privileges.

### Step 2.1: Switch to the `postgres` User

PostgreSQL creates a system user named `postgres` for administrative tasks. Switch to this user to run database commands.
```bash
sudo -i -u postgres
```

### Step 2.2: Create the Application User

Create a new role (user) for the SG-POS application. **Replace `a_very_strong_and_secure_password` with a strong, randomly generated password.** Store this password securely (e.g., in a password manager or secrets management system).

```bash
createuser --interactive --pwprompt
```
Follow the prompts:
*   Enter name of role to add: `sgpos_prod_user`
*   Enter password for new role: `[your_strong_password]`
*   Enter it again: `[your_strong_password]`
*   Shall the new role be a superuser? (y/n) `n`
*   Shall the new role be allowed to create databases? (y/n) `n`
*   Shall the new role be allowed to create more new roles? (y/n) `n`

### Step 2.3: Create the Application Database

Create the database that will hold all the SG-POS data. We will make our new user the owner of this database.
```bash
createdb -O sgpos_prod_user sgpos_prod
```
The command is `createdb -O [OWNER] [DATABASE_NAME]`.

### Step 2.4: Exit the `postgres` User Session
You can now return to your regular sudo user session.
```bash
exit
```

## 5. Part 3: Deploying the SG-POS Schema

With the database and user in place, you can now apply the application schema.

### Step 3.1: Transfer the Schema File

Copy your `schema.sql` file to the server. You can use `scp` for this:
```bash
# Run this command from your local machine
scp /path/to/your/local/schema.sql your_user@your_server_ip:/home/your_user/
```

### Step 3.2: Apply the Schema

Execute the SQL script against your newly created database. This command will create all the tables, triggers, indexes, and functions defined in the file.
```bash
psql -h localhost -U sgpos_prod_user -d sgpos_prod -f /home/your_user/schema.sql
```
*   `-h localhost`: Connect to the database on the same server.
*   `-U sgpos_prod_user`: Connect as the application user.
*   `-d sgpos_prod`: Target the production database.
*   `-f ...`: Specifies the SQL file to execute.

You will be prompted for the password you created for `sgpos_prod_user`. If the script runs without any `ERROR:` messages, the schema has been successfully deployed.

## 6. Part 4: Configuring Network Access & Security

By default, PostgreSQL only allows connections from the local machine. You must configure it to securely accept connections from your application server.

### Step 4.1: Find the Configuration Files

The main configuration files are typically located in `/etc/postgresql/15/main/`.
*   `postgresql.conf`: Main server configuration.
*   `pg_hba.conf`: Client authentication rules.

### Step 4.2: Configure `postgresql.conf`

Open the file for editing:
```bash
sudo nano /etc/postgresql/15/main/postgresql.conf
```
Find the `listen_addresses` line. To allow connections from other machines, change it from `'localhost'` to `'*'`.
```conf
# Before
#listen_addresses = 'localhost'

# After (to listen on all available IP addresses)
listen_addresses = '*'
```
This allows the server to accept connections on all its network interfaces.

### Step 4.3: Configure `pg_hba.conf`

This file controls who can connect, from where, and how they must authenticate. It is read from top to bottom, so the order matters.

Open the file for editing:
```bash
sudo nano /etc/postgresql/15/main/pg_hba.conf
```
Add a new line at the **end of the file** to allow your application server to connect. Replace `<app_server_ip_address>` with the actual IP of your application server.

```conf
# TYPE  DATABASE        USER            ADDRESS                 METHOD
# Allow the application server to connect to the production database using a secure password method.
host    sgpos_prod      sgpos_prod_user <app_server_ip_address>/32 scram-sha-256
```
*   **`host`**: Specifies a TCP/IP connection (network connection).
*   **`sgpos_prod`**: The database name.
*   **`sgpos_prod_user`**: The user name.
*   **`<app_server_ip_address>/32`**: The IP address of your application server. The `/32` means only this exact IP is allowed.
*   **`scram-sha-256`**: The most secure password authentication method available in modern PostgreSQL.

If your application and database are on the **same server**, the following line is sufficient and more secure:
```conf
# TYPE  DATABASE        USER            ADDRESS                 METHOD
local   sgpos_prod      sgpos_prod_user                         scram-sha-256
```

### Step 4.4: Restart PostgreSQL to Apply Changes

```bash
sudo systemctl restart postgresql
```

## 7. Part 5: Verification

Finally, verify that the setup is correct from both the database server and, if applicable, the application server.

### Step 7.1: Verify Schema on the Database Server

Connect to the database and list the tables in the `sgpos` schema.
```bash
psql -U sgpos_prod_user -d sgpos_prod -c "\dt sgpos.*"
```
This should display a list of all the tables you created (e.g., `companies`, `products`, `sales_transactions`, etc.).

### Step 7.2: Verify Remote Connection (if applicable)

From your **application server**, try to connect to the database server. You will need the `postgresql-client` package installed there.
```bash
# On the application server
sudo apt install postgresql-client

# Attempt to connect (replace <db_server_ip_address>)
psql -h <db_server_ip_address> -U sgpos_prod_user -d sgpos_prod
```
If you are prompted for a password and can successfully connect, your network configuration is correct.

## 8. Critical Note on the Audit Trigger Implementation

The provided schema includes a sophisticated audit trigger (`log_changes`) that relies on a session variable to identify the user performing an action.

> **Application-Side Responsibility:**
> For the audit trail to correctly log the `user_id`, the SG-POS application **MUST** execute the following SQL command at the beginning of every database transaction:
>
> ```sql
> SET sgpos.current_user_id = '<the-uuid-of-the-logged-in-user>';
> ```
>
> This command sets a temporary variable that is only visible within the current database session. The `log_changes` trigger function is designed to read this variable. If the application does not set this variable, the `user_id` in the `audit_logs` table will be `NULL`. This is a critical integration point between the application logic and the database schema.

---
**Deployment of the SG-POS PostgreSQL database is now complete.** The database is secure, configured, and ready to accept connections from the application.
```
