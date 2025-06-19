# File: tests/factories.py
"""
factory-boy classes for creating test data.
"""
import factory
from factory.alchemy import SQLAlchemyModelFactory
from decimal import Decimal
import uuid

from app.models import (
    Company, Outlet, User, Role, Product, Customer, PaymentMethod, Supplier
)

# Note: The session is now configured and injected by the `db_session`
# fixture in `tests/conftest.py`.

class CompanyFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Company
        sqlalchemy_session_persistence = "flush"

    id = factory.LazyFunction(uuid.uuid4)
    name = factory.Faker('company')
    registration_number = factory.Sequence(lambda n: f"UEN{n:08d}")
    is_active = True

class OutletFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Outlet
        sqlalchemy_session_persistence = "flush"

    id = factory.LazyFunction(uuid.uuid4)
    company = factory.SubFactory(CompanyFactory)
    code = factory.Sequence(lambda n: f"OUTLET-{n}")
    name = factory.Faker('word')
    is_active = True

class UserFactory(SQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session_persistence = "flush"

    id = factory.LazyFunction(uuid.uuid4)
    company = factory.SubFactory(CompanyFactory)
    username = factory.Faker('user_name')
    email = factory.Faker('email')
    password_hash = "a_fake_hash"
    is_active = True

class RoleFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Role
        sqlalchemy_session_persistence = "flush"
    
    id = factory.LazyFunction(uuid.uuid4)
    company = factory.SubFactory(CompanyFactory)
    name = factory.Sequence(lambda n: f"Role {n}")
    is_system_role = False

class ProductFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Product
        sqlalchemy_session_persistence = "flush"

    id = factory.LazyFunction(uuid.uuid4)
    company = factory.SubFactory(CompanyFactory)
    sku = factory.Sequence(lambda n: f"SKU{n:04d}")
    name = factory.Faker('word')
    cost_price = Decimal("10.00")
    selling_price = Decimal("20.00")
    gst_rate = Decimal("9.00")
    track_inventory = True
    is_active = True

class CustomerFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Customer
        sqlalchemy_session_persistence = "flush"
    
    id = factory.LazyFunction(uuid.uuid4)
    company = factory.SubFactory(CompanyFactory)
    customer_code = factory.Sequence(lambda n: f"CUST-{n:04d}")
    name = factory.Faker('name')
    is_active = True

class PaymentMethodFactory(SQLAlchemyModelFactory):
    class Meta:
        model = PaymentMethod
        sqlalchemy_session_persistence = "flush"
    
    id = factory.LazyFunction(uuid.uuid4)
    company = factory.SubFactory(CompanyFactory)
    name = factory.Sequence(lambda n: f"Method {n}")
    type = "CASH"
    is_active = True

class SupplierFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Supplier
        sqlalchemy_session_persistence = "flush"
    
    id = factory.LazyFunction(uuid.uuid4)
    company = factory.SubFactory(CompanyFactory)
    name = factory.Faker('company')
    is_active = True
