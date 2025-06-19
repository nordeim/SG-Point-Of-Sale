# File: migrations/env.py
import sys
import os 
from logging.config import fileConfig
import asyncio

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from sqlalchemy import text 

from alembic import context

from dotenv import load_dotenv

# Add the project's root directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Load environment variables from .env.dev file
load_dotenv(os.path.join(project_root, '.env.dev'))

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

from app.models.base import Base
from app.models import *

target_metadata = Base.metadata

# FIX: Check if we are in a test environment using SQLite by inspecting the URL
# that pytest will place in the config. If not present, fall back to the env var.
db_url_from_config = config.get_main_option("sqlalchemy.url")
is_test_mode = db_url_from_config and "sqlite" in db_url_from_config

if is_test_mode:
    # For SQLite, we don't use a schema.
    target_metadata.schema = None
    alembic_db_url = db_url_from_config
else:
    # For PostgreSQL, use the production/development URL and driver
    db_url_from_env = os.environ.get("DATABASE_URL")
    if not db_url_from_env:
        raise Exception("DATABASE_URL not set for non-test environment.")
        
    if db_url_from_env.startswith("postgresql+asyncpg"):
        alembic_db_url = db_url_from_env.replace("postgresql+asyncpg", "postgresql+psycopg2", 1)
    else:
        alembic_db_url = db_url_from_env

# Set the URL for Alembic to use
config.set_main_option("sqlalchemy.url", alembic_db_url)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    context.configure(
        url=alembic_db_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        version_table_schema=target_metadata.schema
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    """Helper function to run the migrations within a context."""
    # Re-check test mode here as well for safety
    is_test = connection.engine.dialect.name == "sqlite"
    
    current_target_metadata = Base.metadata
    if is_test:
        current_target_metadata.schema = None

    context.configure(
        connection=connection,
        target_metadata=current_target_metadata,
        version_table_schema=current_target_metadata.schema
    )

    with context.begin_transaction():
        if not is_test and current_target_metadata.schema:
            context.execute(text(f"CREATE SCHEMA IF NOT EXISTS {current_target_metadata.schema}"))
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        do_run_migrations(connection)

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
