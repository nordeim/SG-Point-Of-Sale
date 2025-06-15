# File: app/models/accounting.py
"""SQLAlchemy models for core Accounting entities (Chart of Accounts, Journal Entries, Journal Entry Lines)."""
import uuid
from datetime import date, datetime
import sqlalchemy as sa
from sqlalchemy import Column, String, Boolean, ForeignKey, Numeric, DateTime, Text, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin

class ChartOfAccount(Base, TimestampMixin):
    """Represents a single account in the Chart of Accounts."""
    __tablename__ = "chart_of_accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, doc="Unique identifier for the account")
    company_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.companies.id"), nullable=False, index=True, doc="Foreign key to the owning company")
    account_code = Column(String(20), nullable=False, doc="Unique alphanumeric code for the account")
    account_name = Column(String(255), nullable=False, doc="Descriptive name of the account")
    account_type = Column(String(50), nullable=False, doc="Type of account (ASSET, LIABILITY, EQUITY, REVENUE, EXPENSE)")
    parent_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.chart_of_accounts.id"), nullable=True, doc="Self-referencing foreign key for hierarchical accounts")
    is_active = Column(Boolean, nullable=False, default=True, doc="Indicates if the account is active for use")

    # Relationships
    company = relationship("Company", back_populates="chart_of_accounts", doc="The company this account belongs to")
    parent_account = relationship("ChartOfAccount", remote_side=[id], backref="children_accounts", doc="Parent account for hierarchical structure")
    journal_entry_lines = relationship("JournalEntryLine", back_populates="account", doc="Journal entry lines posted to this account")

    __table_args__ = (
        sa.UniqueConstraint('company_id', 'account_code', name='uq_coa_company_code'),
        sa.CheckConstraint("account_type IN ('ASSET', 'LIABILITY', 'EQUITY', 'REVENUE', 'EXPENSE')", name="chk_account_type")
    )

class JournalEntry(Base, TimestampMixin):
    """Represents a double-entry accounting journal entry."""
    __tablename__ = "journal_entries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, doc="Unique identifier for the journal entry")
    company_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.companies.id"), nullable=False, index=True, doc="Foreign key to the owning company")
    entry_number = Column(String(50), nullable=False, doc="Unique internal journal entry number (e.g., JE-0001)")
    entry_date = Column(Date, nullable=False, doc="Date of the journal entry (YYYY-MM-DD)")
    description = Column(Text, nullable=False, doc="Description of the transaction")
    # Reference to source transaction (e.g., SalesTransaction.id)
    source_transaction_id = Column(UUID(as_uuid=True), nullable=True, index=True, doc="ID of the source transaction (e.g., Sales, PO)")
    source_transaction_type = Column(String(50), nullable=True, doc="Type of the source transaction (e.g., 'SALE', 'PURCHASE')")
    status = Column(String(20), nullable=False, default='POSTED', doc="Status of the journal entry (DRAFT, POSTED, VOID)")
    created_by_user_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.users.id"), nullable=False, index=True, doc="Foreign key to the user who created this entry")
    
    # Relationships
    company = relationship("Company", back_populates="journal_entries", doc="The company this journal entry belongs to")
    created_by_user = relationship("User", back_populates="journal_entries_created", doc="The user who created this journal entry")
    journal_entry_lines = relationship("JournalEntryLine", back_populates="journal_entry", cascade="all, delete-orphan", doc="Individual debit/credit lines for this journal entry")
    # Link to SalesTransaction if this JE originates from a sale (using primaryjoin for ambiguous FK)
    sales_transaction = relationship("SalesTransaction", foreign_keys=[source_transaction_id], primaryjoin="and_(SalesTransaction.id == JournalEntry.source_transaction_id, JournalEntry.source_transaction_type == 'SALE')", doc="The sales transaction this journal entry originates from")

    __table_args__ = (
        sa.UniqueConstraint('company_id', 'entry_number', name='uq_journal_entry_company_number'),
        sa.CheckConstraint("status IN ('DRAFT', 'POSTED', 'VOID')", name="chk_journal_entry_status")
    )

class JournalEntryLine(Base, TimestampMixin): # Journal lines can have updated_at for later adjustments/corrections
    """Represents a single debit or credit line within a JournalEntry."""
    __tablename__ = "journal_entry_lines"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, doc="Unique identifier for the journal item")
    journal_entry_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.journal_entries.id", ondelete="CASCADE"), nullable=False, index=True, doc="Foreign key to the parent journal entry")
    account_id = Column(UUID(as_uuid=True), ForeignKey("sgpos.chart_of_accounts.id"), nullable=False, index=True, doc="Foreign key to the affected account")
    debit_amount = Column(Numeric(19, 2), nullable=False, default=0, doc="Debit amount for this line item")
    credit_amount = Column(Numeric(19, 2), nullable=False, default=0, doc="Credit amount for this line item")
    description = Column(Text, doc="Specific description for this line item")
    
    # Relationships
    journal_entry = relationship("JournalEntry", back_populates="journal_entry_lines", doc="The journal entry this item belongs to")
    account = relationship("ChartOfAccount", back_populates="journal_entry_lines", doc="The account affected by this journal entry line")

    __table_args__ = (
        sa.CheckConstraint(
            "(debit_amount > 0 AND credit_amount = 0) OR (credit_amount > 0 AND debit_amount = 0) OR (debit_amount = 0 AND credit_amount = 0)",
            name="chk_debit_or_credit"
        ), # ADDED A TRAILING COMMA HERE TO MAKE IT A PROPER SINGLE-ELEMENT TUPLE
    )
