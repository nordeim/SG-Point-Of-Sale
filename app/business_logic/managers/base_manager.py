# File: app/business_logic/managers/base_manager.py
"""Abstract Base Class for all business logic managers."""
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.core.application_core import ApplicationCore

class BaseManager:
    """
    Provides managers with access to the application core.
    All managers should inherit from this class.
    """
    def __init__(self, core: "ApplicationCore"):
        self.core = core
