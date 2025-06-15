# File: app/core/exceptions.py
"""
Defines custom exception classes for the application.

While the Result pattern is used for predictable business errors, exceptions
are still used for unexpected, catastrophic system failures (e.g., database
is unreachable, configuration is missing).
"""

class CoreException(Exception):
    """Base exception for all application-specific errors."""
    pass

class ConfigurationError(CoreException):
    """Raised when there is an error in the application configuration."""
    pass

class DatabaseConnectionError(CoreException):
    """Raised when the application cannot connect to the database."""
    pass

class AsyncBridgeError(CoreException):
    """Raised when there is an error in the asynchronous bridge setup or operation."""
    pass

# TODO: Add more specific exceptions as needed for different domains (e.g., SalesError, InventoryError)
# These would typically be subclasses of a higher-level business exception,
# distinct from CoreException. For example:
# class BusinessError(CoreException): pass
# class InsufficientStockError(BusinessError): pass
