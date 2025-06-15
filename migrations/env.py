# File: migrations/env.py
import sys
import os 
from logging.config import fileConfig
import asyncio # Import asyncio for the new run_migrations_online

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from sqlalchemy import text 

from alembic import context

# NEW: Import load_dotenv from python-dotenv
from dotenv import load_dotenv

# Add the project's root directory to sys.path
# This allows 'app' modules to be imported correctly regardless of
# where the alembic command is executed from.
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# NEW: Load environment variables from .env.dev file
# This must be done BEFORE alembic tries to read config values
load_dotenv(os.path.join(project_root, '.env.dev'))

# This is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
from app.models.base import Base # IMPORTANT: Import your Base

# IMPORT ALL YOUR ORM MODELS HERE SO ALEMBIC CAN DETECT THEM FOR AUTOGENERATE
# Using '*' imports all classes defined in these modules.
from app.models.company import *
from app.models.user import *
from app.models.product import *
from app.models.inventory import *
from app.models.customer import *
from app.models.sales import *
from app.models.accounting import *
from app.models.audit_log import *


target_metadata = Base.metadata # IMPORTANT: Set this to your Base.metadata

# Retrieve DATABASE_URL explicitly from environment after dotenv loads it
db_url = os.environ.get("DATABASE_URL")
if db_url is None:
    raise Exception("DATABASE_URL environment variable is not set. Please ensure .env.dev is configured correctly or the variable is in your environment.")

# Modify the DATABASE_URL to use psycopg2 (synchronous driver) for Alembic.
# This avoids the "MissingGreenlet" error as Alembic runs synchronously.
# The application itself will continue to use asyncpg.
if db_url.startswith("postgresql+asyncpg"):
    alembic_db_url = db_url.replace("postgresql+asyncpg", "postgresql+psycopg2", 1) # Only replace first occurrence
else:
    alembic_db_url = db_url # Use as is if it's not asyncpg

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a database to begin with.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    # Use the explicitly loaded alembic_db_url instead of config.get_main_option
    context.configure(
        url=alembic_db_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # IMPORTANT: Tell Alembic to manage its version table within the 'sgpos' schema
        version_table_schema=target_metadata.schema if target_metadata and target_metadata.schema else None
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    """Helper function to run the migrations within a context."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        # IMPORTANT: Tell Alembic to manage its version table within the 'sgpos' schema
        version_table_schema=target_metadata.schema if target_metadata and target_metadata.schema else None
    )

    with context.begin_transaction():
        # Ensure the schema exists before running migrations
        context.execute(text(f"CREATE SCHEMA IF NOT EXISTS {target_metadata.schema}"))
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.
    This online migration is now async to support creating an async engine.
    """
    # Create an engine and connect to the database.
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        url=alembic_db_url
    )

    with connectable.connect() as connection:
        do_run_migrations(connection)

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
