# File: scripts/database/seed_data.py
"""
A script to seed the database with initial, essential data for development.

This script should be run once after running `alembic upgrade head` on a fresh database.
It creates the default Company, Outlet, and an Admin User with the specific UUIDs
defined in the `.env.example` file, making the application immediately usable
with the default configuration.
"""
import asyncio
import uuid
from decimal import Decimal
import bcrypt
import os
import sys
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.future import select

# Add project root to sys.path to allow imports from app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from app.core.config import settings
from app.models import Base, Company, Outlet, User, Role, UserRole

# --- Static UUIDs from .env.example for consistency ---
COMPANY_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
OUTLET_ID = uuid.UUID("00000000-0000-0000-0000-000000000002")
USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000003")

def hash_password(password: str) -> str:
    """Hashes a password using bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

async def seed_database():
    """Connects to the database and inserts the initial seed data."""
    print("--- Starting Database Seeding ---")
    
    # Use a non-asyncpg URL for this simple script if needed, but asyncpg is fine
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    SessionFactory = async_sessionmaker(engine, expire_on_commit=False)

    async with SessionFactory() as session:
        # Check if company already exists
        company_check = await session.get(Company, COMPANY_ID)
        if company_check:
            print(f"Company with ID {COMPANY_ID} already exists. Seeding aborted.")
            return

        print("Creating initial data...")

        # 1. Create Company
        default_company = Company(
            id=COMPANY_ID,
            name="SG-POS Default Company",
            registration_number="202500001X",
            gst_registration_number="M90360001X",
            address="123 Orchard Road, Singapore 238839",
            phone="+65 6734 1234",
            email="contact@sgpos-default.com",
            is_active=True
        )
        session.add(default_company)
        print(f"  - Company: {default_company.name}")

        # 2. Create Outlet
        main_outlet = Outlet(
            id=OUTLET_ID,
            company_id=COMPANY_ID,
            code="MAIN",
            name="Main Outlet",
            address="123 Orchard Road, Singapore 238839",
            is_active=True
        )
        session.add(main_outlet)
        print(f"  - Outlet: {main_outlet.name}")
        
        # 3. Create Admin Role
        admin_role = Role(
            company_id=COMPANY_ID,
            name="Admin",
            description="Has full access to all system features.",
            is_system_role=True
        )
        session.add(admin_role)
        print(f"  - Role: {admin_role.name}")
        
        # 4. Create Admin User
        admin_user = User(
            id=USER_ID,
            company_id=COMPANY_ID,
            username="admin",
            email="admin@sgpos-default.com",
            password_hash=hash_password("admin123"), # Use a simple default for local dev
            full_name="Default Admin",
            is_active=True
        )
        session.add(admin_user)
        print(f"  - User: {admin_user.username} (Password: admin123)")

        # We need to flush to get the IDs for the junction table
        await session.flush()

        # 5. Assign Admin Role to Admin User for the Main Outlet
        user_role_assignment = UserRole(
            user_id=admin_user.id,
            role_id=admin_role.id,
            outlet_id=main_outlet.id
        )
        session.add(user_role_assignment)
        print(f"  - Assigned '{admin_role.name}' role to '{admin_user.username}' at '{main_outlet.name}'")

        try:
            await session.commit()
            print("\n--- Seeding Successful ---")
            print("Database now contains the default data required to run the application.")
        except Exception as e:
            print(f"\n--- ERROR: Seeding failed. Rolling back. ---")
            print(f"Error details: {e}")
            await session.rollback()
        finally:
            await engine.dispose()

if __name__ == "__main__":
    asyncio.run(seed_database())
