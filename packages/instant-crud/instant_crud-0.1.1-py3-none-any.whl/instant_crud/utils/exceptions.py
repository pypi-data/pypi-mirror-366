"""
Custom exceptions for instant-crud.
"""


class InstantCRUDException(Exception):
    """Base exception for instant-crud."""


class ModelNotFound(InstantCRUDException):
    """Raised when model is not found."""


class ValidationError(InstantCRUDException):
    """Raised when validation fails."""


class ConfigurationError(InstantCRUDException):
    """Raised when configuration is invalid."""
