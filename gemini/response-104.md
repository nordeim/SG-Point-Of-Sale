<think>
The user wants a step-by-step guide on how to apply the corrected migration file to an actual database.

This is a procedural documentation task. The user has an updated migration script and needs to know the exact commands and workflow to use it to update their database schema. I need to consider the different states the database might be in:

1.  **State A: A completely fresh, empty database.** This is the simplest case.
2.  **State B: A database that was already created using the *old, flawed* migration.** This is the more complex and realistic scenario for someone who has been following the project. They need to "reset" and re-apply the correct schema.
3.  **State C: A database with manually created tables or other inconsistencies.** This is a recovery scenario.

The user's request is general ("how to update the actual database schema"), so I should provide a guide that is robust and covers the most likely scenarios, especially State B. The guide must be clear, safe, and explain the consequences of each action (e.g., dropping tables means data loss).

**Mental Sandbox/Simulation & Plan:**

1.  **Structure the Guide:**
    *   **Introduction**: Briefly state the goal: to use the corrected Alembic script to ensure the database schema is perfectly aligned with the application models.
    *   **Prerequisites**: List what the user needs before starting (a working development environment as per the deployment guide, the updated migration file in place, a running Docker container for the database).
    *   **Crucial Warning about Data Loss**: Start with a big, bold warning. The process of resetting a flawed initial migration involves dropping all existing tables, which means **all data will be erased**. This is critical information.
    *   **Step-by-Step Guide**: This will be the core of the response. I'll break it down into clear, actionable steps.
    *   **Verification Step**: Show how to verify the schema is correct after the process.
    *   **Troubleshooting**: Briefly mention common issues and solutions.

2.  **Detailed Step-by-Step Plan:**

    *   **Step 1: Backup Your Database (Safety First!)**
        *   **Why**: Emphasize that this is a destructive operation. A backup is the only safety net.
        *   **How**: Provide the exact `docker exec pg_dump` and `docker cp` commands from the deployment guide I created earlier. This reinforces good practice and ensures the user has a way to revert if something goes wrong.

    *   **Step 2: Prepare the Environment**
        *   **Why**: Explain that all Alembic and application commands must be run from the correct directory and within the project's virtual environment.
        *   **How**:
            *   `cd /path/to/sg-pos-system`
            *   `poetry shell`
            *   Explain what `poetry shell` does again for clarity.

    *   **Step 3: Reset the Database to a Clean State**
        *   This is the most critical part for users in State B or C.
        *   **Option A (Recommended & Simplest): Drop All Tables.** I'll recommend this as the cleanest approach.
            *   **Why**: Explain that since the initial migration history (`alembic_version` table) is based on a flawed script, it's best to start from a truly blank slate to avoid conflicts.
            *   **How**: I'll provide a Python script or a sequence of `psql` commands run via `docker exec` to drop the entire `sgpos` schema. This is more robust than just running `alembic downgrade base`.
                ```bash
                docker exec -it sgpos_dev_db psql -U sgpos_dev_user -d sgpos_dev
                ```
                Then inside psql:
                ```sql
                DROP SCHEMA sgpos CASCADE;
                CREATE SCHEMA sgpos;
                \q
                ```
                I will explain each of these commands. The `CASCADE` is key.

    *   **Step 4: Apply the Corrected Migration**
        *   **Why**: Now that the database is clean, we can apply the single, correct initial migration script.
        *   **How**:
            *   `alembic stamp head` - I should explain this command carefully. It tells Alembic to "pretend" that the database is already at the latest version without running the migrations. This is useful if you create the schema manually, but in this case, we need to apply the migration. So, `stamp` is the wrong command here.
            *   The correct command is `alembic upgrade head`. Since we just dropped the schema, the `alembic_version` table is also gone. `alembic upgrade head` will see a blank slate, create the `alembic_version` table, and run our single `d5a6759ef2f7` migration.
            *   **Command**: `alembic upgrade head`
            *   **Explanation**: I'll describe what this does: connects to the DB, sees no version table, creates it, runs the `upgrade()` function in our corrected script, creates all tables, and then records `d5a6759ef2f7` in the `alembic_version` table as the current schema version.

    *   **Step 5: Verify the Schema**
        *   **Why**: It's important to confirm the operation was successful.
        *   **How**: I can show a few `psql` commands to inspect the database.
            *   Connect to the DB: `docker exec -it sgpos_dev_db psql -U sgpos_dev_user -d sgpos_dev`
            *   List tables in the schema: `\dt sgpos.*`
            *   Describe a specific table to check its columns and constraints: `\d sgpos.stock_movements`. I'll point out that the user should see the `reference_type` column, which was a key fix.
            *   Check the migration version: `SELECT * FROM sgpos.alembic_version;`. The user should see the `d5a6759ef2f7` revision hash.

3.  **Refinement and Tone**:
    *   The tone must be authoritative but also very cautious. The user is performing a potentially destructive operation.
    *   I will use formatting like blockquotes, bold text, and code blocks to make the warnings and commands stand out.
    *   I'll start the whole guide with a large warning block.
    *   I will explicitly state that this guide assumes the user has the corrected migration file in place.

This plan is comprehensive, safe, and addresses the user's need directly. It accounts for the likely state of the user's database and provides a clean path to get to the desired state. I'm ready to generate the guide.Of course. Based on your request, here is a detailed, step-by-step guide on how to use the corrected initial migration file to update your database schema.

This guide assumes you have already replaced the original `migrations/versions/d5a6759ef2f7_initial_schema_setup.py` with the new, corrected version I provided. The process involves resetting your current database to apply the corrected schema from a clean slate.

***

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

