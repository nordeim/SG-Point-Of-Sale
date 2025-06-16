# File: app/models/__init__.py
"""
Models Package Initialization

This file makes the `app/models` directory a Python package and conveniently
imports all ORM model classes into its namespace. This allows for cleaner imports
in other parts of the application (e.g., `from app.models import Product`).
"""
from .base import Base, TimestampMixin
from .company import Company, Outlet
from .user import User, Role, Permission, RolePermission, UserRole
from .product import Category, Supplier, Product, ProductVariant
from .inventory import Inventory, StockMovement, PurchaseOrder, PurchaseOrderItem
from .customer import Customer
from .sales import SalesTransaction, SalesTransactionItem, PaymentMethod, Payment
from .accounting import ChartOfAccount, JournalEntry, JournalEntryLine
from .audit_log import AuditLog

__all__ = [
    "Base",
    "TimestampMixin",
    "Company",
    "Outlet",
    "User",
    "Role",
    "Permission",
    "RolePermission",
    "UserRole",
    "Category",
    "Supplier",
    "Product",
    "ProductVariant",
    "Inventory",
    "StockMovement",
    "PurchaseOrder",
    "PurchaseOrderItem",
    "Customer",
    "SalesTransaction",
    "SalesTransactionItem",
    "PaymentMethod",
    "Payment",
    "ChartOfAccount",
    "JournalEntry",
    "JournalEntryLine",
    "AuditLog",
]
