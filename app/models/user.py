# File: app/models/user.py
"""SQLAlchemy models for User, Role, and Permission entities."""
import uuid
from datetime import datetime
import sqlalchemy as sa
from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin

class User(Base, TimestampMixin):
    """Represents a user (employee) of the SG-POS system."""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, doc="Unique identifier for the user")
    company_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.companies.id", ondelete="RESTRICT"), nullable=False, index=True, doc="Foreign key to the owning company")
    username = Column(String(100), nullable=False, doc="Unique username for login")
    email = Column(String(255), nullable=False, doc="User's email address")
    password_hash = Column(String(255), nullable=False, doc="Hashed password using bcrypt")
    full_name = Column(String(255), doc="User's full name")
    is_active = Column(Boolean, nullable=False, default=True, doc="Indicates if the user account is active")
    last_login_at = Column(DateTime(timezone=True), doc="Timestamp of the user's last successful login")
    
    # Relationships
    company = relationship("Company", back_populates="users", doc="The company this user belongs to")
    user_roles = relationship("UserRole", back_populates="user", cascade="all, delete-orphan", doc="Roles assigned to this user")
    sales_transactions = relationship("SalesTransaction", back_populates="cashier", doc="Sales transactions processed by this user")
    stock_movements_created = relationship("StockMovement", back_populates="user", doc="Stock movements created by this user")
    journal_entries_created = relationship("JournalEntry", back_populates="created_by_user", doc="Journal entries created by this user")
    audit_logs = relationship("AuditLog", back_populates="user", doc="Audit logs associated with this user")

    __table_args__ = (
        sa.UniqueConstraint('company_id', 'username', name='uq_user_company_username'),
        sa.UniqueConstraint('company_id', 'email', name='uq_user_company_email')
    )

class Role(Base):
    """Defines user roles (e.g., Admin, Manager, Cashier)."""
    __tablename__ = "roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, doc="Unique identifier for the role")
    company_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.companies.id", ondelete="RESTRICT"), nullable=False, doc="Foreign key to the owning company")
    name = Column(String(50), nullable=False, doc="Name of the role (unique per company)")
    description = Column(Text, doc="Description of the role's responsibilities")
    is_system_role = Column(Boolean, nullable=False, default=False, doc="True for built-in roles that cannot be deleted or modified by users")
    
    # Relationships
    company = relationship("Company", back_populates="roles", doc="The company this role belongs to")
    role_permissions = relationship("RolePermission", back_populates="role", cascade="all, delete-orphan", doc="Permissions assigned to this role")
    user_roles = relationship("UserRole", back_populates="role", cascade="all, delete-orphan", doc="Users assigned to this role")

    __table_args__ = (
        sa.UniqueConstraint('company_id', 'name', name='uq_role_company_name'),
    )

class Permission(Base):
    """Defines granular permissions within the system."""
    __tablename__ = "permissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, doc="Unique identifier for the permission")
    action = Column(String(100), nullable=False, doc="The action permitted (e.g., 'CREATE', 'READ', 'UPDATE', 'DELETE')")
    resource = Column(String(100), nullable=False, doc="The resource or module the action applies to (e.g., 'PRODUCT', 'SALE_TRANSACTION')")
    description = Column(Text, doc="Description of what this permission allows")

    # Relationships
    role_permissions = relationship("RolePermission", back_populates="permission", cascade="all, delete-orphan", doc="Roles that have this permission")

    __table_args__ = (
        sa.UniqueConstraint('action', 'resource', name='uq_permission_action_resource'),
    )

class RolePermission(Base):
    """Junction table linking roles to their permissions."""
    __tablename__ = "role_permissions"

    role_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.roles.id", ondelete="CASCADE"), primary_key=True, doc="Foreign key to the role")
    permission_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.permissions.id", ondelete="CASCADE"), primary_key=True, doc="Foreign key to the permission")

    # Relationships
    role = relationship("Role", back_populates="role_permissions", doc="The role associated with this permission")
    permission = relationship("Permission", back_populates="role_permissions", doc="The permission associated with this role")

class UserRole(Base):
    """Assigns roles to users, potentially on a per-outlet basis."""
    __tablename__ = "user_roles"

    user_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.users.id", ondelete="CASCADE"), primary_key=True, doc="Foreign key to the user")
    role_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.roles.id", ondelete="CASCADE"), primary_key=True, doc="Foreign key to the role")
    outlet_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.outlets.id", ondelete="CASCADE"), primary_key=True, doc="Foreign key to the assigned outlet (part of composite PK)")

    # Relationships
    user = relationship("User", back_populates="user_roles", doc="The user assigned to this role")
    role = relationship("Role", back_populates="user_roles", doc="The role assigned to this user")
    outlet = relationship("Outlet", doc="The outlet this role assignment is specific to")
