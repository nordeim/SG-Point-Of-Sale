# File: app/ui/utils.py
"""
Provides common utility functions for the UI layer.
"""
from __future__ import annotations
from typing import Any, Optional

from app.core.result import Failure

def format_error_for_user(error_obj: Any) -> str:
    """
    Formats an exception or Failure object into a user-friendly string.

    Args:
        error_obj: The error to format. Can be an Exception, a Failure, or any other object.

    Returns:
        A clean, human-readable error message.
    """
    if isinstance(error_obj, Failure):
        # The .error attribute of a Failure object is expected to be a clean string
        # from the business logic layer.
        return str(error_obj.error)
    if isinstance(error_obj, Exception):
        # For raw, unexpected exceptions, provide a generic but clean message.
        # The full exception should be logged elsewhere for developers.
        # print(f"DEBUG: An unexpected exception occurred: {error_obj}") # For developer logs
        return "An unexpected technical error occurred. Please contact support if the problem persists."
    return "An unknown error occurred."
