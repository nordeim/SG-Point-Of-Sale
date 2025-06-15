# File: migrations/env.py
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from sqlalchemy import text # Import text for executing literal SQL if needed

from alembic import context

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
from app.models.payment import *
from app.models.accounting import *
from app.models.audit_log import *


target_metadata = Base.metadata # IMPORTANT: Set this to your Base.metadata

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
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # IMPORTANT: Tell Alembic to manage its version table within the 'sgpos' schema
        version_table_schema=target_metadata.schema if target_metadata and target_metadata.schema else None
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        url=config.get_main_option("sqlalchemy.url") # Pass URL explicitly
    )

    with connectable.connect() as connection:
        # Create the 'sgpos' schema if it doesn't exist before running migrations.
        # This ensures the schema is present for Alembic's version table and other objects.
        connection.execute(text(f"CREATE SCHEMA IF NOT EXISTS {target_metadata.schema}"))
        connection.execute(text(f"SET search_path TO {target_metadata.schema}"))

        context.configure(
            connection=connection, 
            target_metadata=target_metadata,
            # IMPORTANT: Tell Alembic to manage its version table within the 'sgpos' schema
            version_table_schema=target_metadata.schema if target_metadata and target_metadata.schema else None
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
