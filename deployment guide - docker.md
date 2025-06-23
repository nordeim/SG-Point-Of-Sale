I will create a `docker-compose.dev.yml` file and a comprehensive guide. The philosophy here is to containerize the *services* the application depends on (like the database), while allowing the GUI application itself to be run *natively* on the developer's host machine. This provides the best of both worlds: a consistent backend and a fast, native development experience for the UI with seamless IDE integration and debugging.

---

### **`docker-compose.dev.yml`**

This file is designed to set up and run the PostgreSQL database required for local development of the SG-POS application.

```yml
# SG-POS System: Docker Compose for Development Environment
# --------------------------------------------------------
# This file sets up the necessary backend services for local development.
# The main PySide6 application should be run natively on your host machine
# to connect to these services.
#
# Usage:
# 1. Ensure you have a `.env.dev` file in the project root.
# 2. Run: docker compose -f docker-compose.dev.yml up -d
# 3. To stop: docker compose -f docker-compose.dev.yml down
# 4. To wipe data: docker compose -f docker-compose.dev.yml down -v
#
version: '3.8'

services:
  # PostgreSQL Database Service
  # ---------------------------
  # This service provides the primary database for the application.
  db:
    # Use the official PostgreSQL 16 image with the Alpine base for a smaller footprint.
    image: postgres:16-alpine

    # A friendly name for the container to easily identify it.
    container_name: sgpos_dev_db

    # The `env_file` directive loads environment variables from the specified file.
    # This is where we configure the PostgreSQL user, password, and database name.
    env_file:
      - .env.dev

    # The `ports` mapping exposes the container's port 5432 to the host machine's port 5432.
    # This allows your natively-run Python application to connect to the database via `localhost:5432`.
    ports:
      - "5432:5432"

    # The `volumes` mapping creates a persistent, named volume for the database data.
    # This ensures your data is saved even if you stop and remove the container.
    volumes:
      - postgres_dev_data:/var/lib/postgresql/data

    # A healthcheck to ensure the database is running and ready to accept connections
    # before other services (if any) might try to connect. The application itself
    # should have its own retry logic, but this is good practice.
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 10s

    # `restart: unless-stopped` ensures the database container automatically restarts
    # if it crashes, unless you manually stop it. This is convenient for development.
    restart: unless-stopped

# Named Volumes
# -------------
# This top-level key defines the named volume used by the `db` service.
# Using a named volume makes it easier to manage the data lifecycle.
volumes:
  postgres_dev_data:
    # The driver is 'local', meaning the data will be stored in a Docker-managed
    # directory on your host machine.
    driver: local
```

---

### **Docker-Based Development Environment Guide**

```md
# 🐳 Docker-Based Development Environment Guide

Welcome to the SG-POS development environment! This guide will walk you through setting up a consistent and isolated development environment using Docker and Docker Compose.

## **The Philosophy: Why We Use Docker This Way**

For a desktop GUI application like SG-POS, we follow a hybrid development model for the best possible developer experience:

1.  **Containerize the Backend Services:** All stateful services that our application depends on, primarily the **PostgreSQL database**, are run inside Docker containers.
2.  **Run the GUI Application Natively:** The main Python/PySide6 application is run directly on your host machine (Windows, macOS, or Linux).

This approach gives us several key advantages:
*   **Consistency:** Every developer runs the exact same version of PostgreSQL, configured identically. This eliminates "it works on my machine" bugs related to database versions or configurations.
*   **Isolation:** The database runs in its own isolated environment, so it won't interfere with any other PostgreSQL instances you might have installed on your system.
*   **Simplicity:** You don't need to manually install, configure, and manage a PostgreSQL server on your local machine. Docker handles everything.
*   **Superior UI Development Experience:** Running the GUI application natively allows for seamless integration with your IDE (VS Code, PyCharm), including powerful debugging tools, faster launch times, and direct access to your machine's graphics hardware. Trying to forward a GUI from a Docker container is complex and often slow.

## **Prerequisites**

Before you begin, make sure you have the following software installed on your system:

1.  **Docker Desktop:** The engine that runs containers.
    *   [Install Docker for Windows](https://docs.docker.com/desktop/install/windows-install/)
    *   [Install Docker for macOS](https://docs.docker.com/desktop/install/mac-install/)
    *   [Install Docker for Linux](https://docs.docker.com/engine/install/)
2.  **Docker Compose:** This tool is used to define and run multi-container Docker applications. It is included by default with Docker Desktop. If you installed Docker Engine on Linux separately, you might need to [install the Compose plugin](https://docs.docker.com/compose/install/).

Verify your installation by running:
```bash
docker --version
docker compose version
```

## **Step 1: Configure Your Environment**

The Docker Compose setup is configured using environment variables. You'll need to create a local environment file for this.

1.  **Create the Environment File:** In the root directory of the project, you'll find a file named `.env.example`. Make a copy of this file and name it `.env.dev`:

    ```bash
    # On macOS or Linux
    cp .env.example .env.dev

    # On Windows (Command Prompt)
    copy .env.example .env.dev
    ```

2.  **Populate `.env.dev`:** Open the new `.env.dev` file in your code editor. It will contain the configuration for the PostgreSQL container. It should look something like this:

    ```env
    # .env.dev

    # PostgreSQL Database Configuration
    # These variables will be used by the Docker container to initialize the database.
    POSTGRES_USER=sgpos_dev_user
    POSTGRES_PASSWORD=a_very_secure_password_for_dev
    POSTGRES_DB=sgpos_dev

    # --- Application Configuration ---
    # The natively-run Python app will also read this file.
    # The DATABASE_URL must point to 'localhost' to connect to the Docker container.
    DATABASE_URL="postgresql+asyncpg://sgpos_dev_user:a_very_secure_password_for_dev@localhost:5432/sgpos_dev"
    
    # Other development settings
    APP_ENV=development
    DEBUG=True
    LOG_LEVEL=DEBUG
    SECRET_KEY=a_super_secret_dev_key_that_is_not_for_production
    ```
    **Important:** You can change the `POSTGRES_PASSWORD` to something of your choice, but ensure it matches the password in the `DATABASE_URL`. For local development, the provided values are fine.

## **Step 2: Launch the Development Environment**

Now that your configuration is ready, you can start the backend services.

1.  **Open a terminal** in the root directory of the project.
2.  **Run the following command:**

    ```bash
    docker compose -f docker-compose.dev.yml up -d
    ```

    Let's break down this command:
    *   `docker compose`: The command-line tool for managing multi-container applications.
    *   `-f docker-compose.dev.yml`: This explicitly tells Docker Compose to use our development-specific configuration file.
    *   `up`: This command creates and starts the containers defined in the file.
    *   `-d`: (Detached mode) This runs the containers in the background and leaves your terminal free.

Docker will now download the `postgres:16-alpine` image (if you don't have it already) and start the container. The first time you run this, it may take a minute or two. Subsequent starts will be much faster.

## **Step 3: Verify the Environment is Running**

You can check that everything started correctly.

1.  **Check Container Status:**

    ```bash
    docker compose -f docker-compose.dev.yml ps
    ```
    You should see an output similar to this, showing the `sgpos_dev_db` container is `running` and `healthy`:

    ```
    NAME             IMAGE                  COMMAND                  SERVICE   STATUS              PORTS
    sgpos_dev_db     postgres:16-alpine     "docker-entrypoint.s…"   db        running (healthy)   0.0.0.0:5432->5432/tcp
    ```

2.  **Connect with a Database Tool (Optional but Recommended):**
    You can now connect to your new database instance using any standard SQL client (like DBeaver, TablePlus, or pgAdmin). Use the following connection details:
    *   **Host:** `localhost`
    *   **Port:** `5432`
    *   **Database:** `sgpos_dev`
    *   **Username:** `sgpos_dev_user`
    *   **Password:** (The password you set in your `.env.dev` file)

    Successfully connecting confirms that your database is up, running, and accessible from your host machine.

## **Final Step: Run the SG-POS Application**

With the database running in Docker, you can now proceed with the standard setup for the Python application as outlined in the main project README or PRD:

```bash
# Make sure you are in the project root directory

# 1. Install Python dependencies if you haven't already
poetry install

# 2. Activate the virtual environment
poetry shell

# 3. Run database migrations to create the tables in your new Dockerized DB
alembic upgrade head

# 4. Run the application
python app/main.py
```

Your Python application, running natively, will now connect to the PostgreSQL database running inside the Docker container.

## **Common Docker Commands for Development**

Here are some useful commands for managing your development environment. Remember to always use `-f docker-compose.dev.yml` to specify the correct file.

*   **Stop the environment:**
    *Stops the containers but does not remove them or their data.*
    ```bash
    docker compose -f docker-compose.dev.yml stop
    ```

*   **Stop and remove the containers:**
    *The persistent data in the volume (`postgres_dev_data`) will be kept.*
    ```bash
    docker compose -f docker-compose.dev.yml down
    ```

*   **View logs for a service:**
    *This is very useful for debugging database issues.*
    ```bash
    # Follow the logs in real-time
    docker compose -f docker-compose.dev.yml logs -f db
    ```

*   **Destroy the environment COMPLETELY (including all data):**
    *This is useful when you want a completely fresh start. **Warning: This will delete your entire development database.**
    ```bash
    docker compose -f docker-compose.dev.yml down -v
    ```

Congratulations! You now have a robust, isolated, and reproducible development environment for the SG-POS project.
```
