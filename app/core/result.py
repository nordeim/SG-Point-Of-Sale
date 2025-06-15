# File: app/core/result.py
"""
Defines the Result pattern for explicit error handling.

This module provides a functional approach to error handling, avoiding the use
of exceptions for predictable business logic failures. All service and manager
methods should return a Result object.
"""
from typing import TypeVar, Generic, Union, Optional, final
from dataclasses import dataclass

# Generic TypeVars for Success (T) and Failure (E) values.
T = TypeVar('T')
E = TypeVar('E')

@final
@dataclass(frozen=True)
class Success(Generic[T]):
    """Represents a successful operation with a return value."""
    value: T

@final
@dataclass(frozen=True)
class Failure(Generic[E]):
    """Represents a failed operation with an error object."""
    error: E

# The Result type is a union of a Success or a Failure.
Result = Union[Success[T], Failure[E]]
