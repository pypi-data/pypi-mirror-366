"""Utilities for instant-crud."""

from .exceptions import (
    ConfigurationError,
    InstantCRUDException,
    ModelNotFound,
    ValidationError,
)

__all__ = [
    "InstantCRUDException",
    "ModelNotFound",
    "ValidationError",
    "ConfigurationError",
]
