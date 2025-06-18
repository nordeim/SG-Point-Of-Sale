### **Guide: Applying the Corrected Database Schema**

#### **1. Introduction & Goal**

The purpose of this guide is to update your SG-POS database to a state that perfectly matches the application's code (`app/models/`). You have a corrected initial migration script (`d5a6759ef2f7_initial_schema_setup.py`), and this guide will walk you through the process of using it to build the correct database schema.

This process is necessary because the original, auto-generated migration script had errors and omissions. To prevent future conflicts and ensure data integrity, we will "reset" the database and apply the single, correct migration.

---

### **⚠️ IMPORTANT: WARNING ABOUT DATA LOSS**

> **This procedure is DESTRUCTIVE and will permanently ERASE all data in your existing SG-POS database.**
>
> The steps below involve dropping all existing tables to ensure a clean application of the corrected schema. This is the safest and most reliable method to resolve inconsistencies from the original flawed migration.
>
> **Before you proceed, you MUST back up your database if it contains any data you wish to keep.** The first step in this guide is a mandatory backup procedure. Do not skip it.

---

#### **2. Prerequisites**

Before you begin, please ensure you have the following:

1.  **A Working Environment:** You have already followed the `Deployment Guide.md` and have a functional setup with Docker, Poetry, and all project dependencies installed.
2.  **The Corrected Migration File:** You have replaced the old `migrations/versions/d5a6759ef2f7_initial_schema_setup.py` with the new, corrected version.
3.  **A Running Database Container:** Your `sgpos_dev_db` Docker container is running. You can check this by running `docker ps`. If it's not running, start it from your project directory with `docker compose -f docker-compose.dev.yml up -d`.

---

#### **Step 1: Back Up Your Database (Mandatory Safety Step)**

Even if you think your database is empty or only contains test data, performing a backup is a critical habit. This is your only safety net.

*   **Action:** Create a full backup of your current database.
*   **Commands:**
    1.  Open your terminal and navigate to a safe location outside the project directory, like your home folder (`cd ~`).
    2.  Create a dedicated directory for your backups if you haven't already.
        ```bash
        mkdir -p sgpos_backups
        ```
    3.  Execute the backup command. This command runs the `pg_dump` utility inside your database container and then copies the resulting backup file to your host machine.
        ```bash
        docker exec -t sgpos_dev_db pg_dump -U sgpos_dev_user -d sgpos_dev -F c -f /tmp/pre_fix_backup.dump && docker cp sgpos_dev_db:/tmp/pre_fix_backup.dump ~/sgpos_backups/
        ```
*   **Verification:** Check that the backup file exists.
    ```bash
    ls -lh ~/sgpos_backups/pre_fix_backup.dump
    ```
    You should see the file listed. You can now proceed with confidence, knowing you have a recovery point.

---

#### **Step 2: Prepare Your Terminal Environment**

All `alembic` commands must be run from within the project's directory and inside its specific virtual environment.

*   **Action:** Navigate to the project directory and activate the Poetry shell.
*   **Commands:**
    ```bash
    # Navigate to your project directory (adjust path if necessary)
    cd /path/to/your/sg-pos-system
    
    # Activate the virtual environment
    poetry shell
    ```
*   **Verification:** Your terminal prompt should now be prefixed with the name of the virtual environment (e.g., `(sg-pos-system-py3.12)`). This confirms you are in the correct environment.

---

#### **Step 3: Reset the Database Schema**

To avoid any conflicts with Alembic's version history (which was based on the old, flawed migration), the cleanest approach is to completely drop the existing schema and create a new, empty one.

*   **Action:** Connect to the PostgreSQL database and drop the `sgpos` schema.
*   **Commands:**
    1.  Execute this command to open an interactive `psql` session inside your database container.
        ```bash
        docker exec -it sgpos_dev_db psql -U sgpos_dev_user -d sgpos_dev
        ```
        Your terminal prompt will change to `sgpos_dev=>`, indicating you are connected to the database.
    2.  Inside the `psql` session, type the following SQL command and press Enter. The `CASCADE` keyword tells PostgreSQL to also drop all objects within the schema (like tables and indexes).
        ```sql
        DROP SCHEMA sgpos CASCADE;
        ```
        The database will respond with `DROP SCHEMA`.
    3.  Now, create a new, empty schema with the same name.
        ```sql
        CREATE SCHEMA sgpos;
        ```
        The database will respond with `CREATE SCHEMA`.
    4.  Exit the `psql` session by typing `\q` and pressing Enter.
        ```sql
        \q
        ```
*   **Verification:** Your database is now in a clean state, containing nothing but an empty `sgpos` schema, ready for the correct migration to be applied.

---

#### **Step 4: Apply the Corrected Migration**

Now we will use Alembic to build the database schema from scratch using our single, corrected migration file.

*   **Action:** Run the `alembic upgrade` command.
*   **Command:** Make sure you are still in the activated Poetry shell from Step 2.
    ```bash
    alembic upgrade head
    ```
*   **What is happening?**
    1.  Alembic connects to the database.
    2.  It looks for its version tracking table (`alembic_version`) inside the `sgpos` schema. Since we just dropped the schema, it won't find one.
    3.  It creates a new `alembic_version` table.
    4.  It sees that the database is at a "base" state (no revisions applied) and that the latest revision available is `d5a6759ef2f7`.
    5.  It executes the `upgrade()` function within your corrected `migrations/versions/d5a6759ef2f7_initial_schema_setup.py` file.
    6.  This creates all the tables, columns, constraints, and indexes in the correct dependency order.
    7.  Once the `upgrade()` function completes successfully, Alembic inserts a row into the `alembic_version` table with the value `d5a6759ef2f7`, marking the database as up-to-date.
*   **Verification:** The command should complete without any errors, displaying `INFO` logs for each table and index it creates.

---

#### **Step 5: Verify the New Schema**

Finally, let's connect to the database one more time to manually inspect the results and confirm that our fixes are in place.

*   **Action:** Connect to the database with `psql` and run a few inspection commands.
*   **Commands:**
    1.  Connect again:
        ```bash
        docker exec -it sgpos_dev_db psql -U sgpos_dev_user -d sgpos_dev
        ```
    2.  **Check the migration version.** This is the most important verification.
        ```sql
        SELECT * FROM sgpos.alembic_version;
        ```
        The output should show a single row with `d5a6759ef2f7` in the `version_num` column.
    3.  **List all tables** in the `sgpos` schema to see that they were all created.
        ```sql
        \dt sgpos.*
        ```
        You should see a list containing `companies`, `products`, `sales_transactions`, etc.
    4.  **Inspect a corrected table.** Let's check `stock_movements` to ensure the `reference_type` column was added.
        ```sql
        \d sgpos.stock_movements
        ```
        In the output list of columns, you should now see `reference_type | character varying(50)`.

---

#### **Conclusion**

You have successfully reset your database and applied the corrected initial schema. Your database structure is now in perfect alignment with the application's ORM models, resolving the critical schema mismatch issue and providing a stable foundation for future development and migrations. You can now launch the application as usual:

```bash
python app/main.py
```

