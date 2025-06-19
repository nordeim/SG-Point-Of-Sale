# File: tests/conftest.py
"""
Pytest configuration and fixtures for the entire test suite.
"""
import pytest
import asyncio
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from alembic.config import Config
from alembic import command
import os

from app.core.config import settings
from app.core.application_core import ApplicationCore
from app.models.base import Base
from tests import factories # Import the entire factories module

# --- Test Database Setup ---

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def test_db_url() -> str:
    """Provides a URL for an in-memory SQLite database for testing."""
    return "sqlite+aiosqlite:///:memory:"

@pytest.fixture(scope="session")
async def db_engine(test_db_url: str):
    """Creates an async engine for the test database."""
    engine = create_async_engine(test_db_url)
    yield engine
    await engine.dispose()

@pytest.fixture(scope="session", autouse=True)
async def setup_database(db_engine):
    """
    Sets up the database schema for the entire test session.
    The autouse=True flag ensures this fixture runs for every test session.
    """
    alembic_cfg = Config("alembic.ini")
    Base.metadata.schema = None 
    alembic_cfg.set_main_option("sqlalchemy.url", str(db_engine.url))

    command.upgrade(alembic_cfg, "head")
    yield
    Base.metadata.schema = "sgpos" 


@pytest.fixture
async def db_session(setup_database, db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Provides a clean database session for each test function."""
    session_factory = async_sessionmaker(db_engine, expire_on_commit=False)

    async with session_factory() as session:
        # FIX: Associate the active test session with all factory_boy factories
        factories.CompanyFactory._meta.sqlalchemy_session = session
        factories.OutletFactory._meta.sqlalchemy_session = session
        factories.UserFactory._meta.sqlalchemy_session = session
        factories.RoleFactory._meta.sqlalchemy_session = session
        factories.ProductFactory._meta.sqlalchemy_session = session
        factories.CustomerFactory._meta.sqlalchemy_session = session
        factories.PaymentMethodFactory._meta.sqlalchemy_session = session
        factories.SupplierFactory._meta.sqlalchemy_session = session

        yield session
        
        # Clean up database state after the test
        await session.rollback()
        for table in reversed(Base.metadata.sorted_tables):
            await session.execute(table.delete())
        await session.commit()
        await session.close()


# --- Application Core Fixture ---

@pytest.fixture
def test_settings(test_db_url: str) -> settings:
    """Overrides production settings with test-specific ones."""
    settings.DATABASE_URL = test_db_url
    return settings

@pytest.fixture
async def test_core(test_settings, db_session, monkeypatch) -> ApplicationCore:
    """
    Provides a fully initialized ApplicationCore instance connected
    to the isolated in-memory test database, using monkeypatching for robustness.
    """
    core = ApplicationCore(test_settings)
    
    test_session_factory = async_sessionmaker(db_session.bind, expire_on_commit=False)
    monkeypatch.setattr(core, "_session_factory", test_session_factory)
    monkeypatch.setattr(core, "_engine", db_session.bind)
    
    yield core
