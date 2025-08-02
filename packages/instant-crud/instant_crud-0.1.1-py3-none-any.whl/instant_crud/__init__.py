# src/instant_crud/__init__.py
"""
instant-crud: Generate REST APIs instantly from SQLModel definitions.

Main exports for easy importing.
"""

from .config.settings import InstantCRUDSettings, SettingsManager
from .core.decorators import api, auto_crud_api, crud_api, crud_config, get_crud_config
from .core.factory import CRUDFactory, get_default_factory, reset_default_factory
from .response.pagination import PaginationResponseBuilder, create_pagination_builder
from .routers.crud_router import CRUDRouter
from .services.base_service import BaseService

# Version
__version__ = "0.1.0"

# Main exports
__all__ = [
    # Decorators
    "auto_crud_api",
    "crud_api",
    "api",
    "crud_config",
    "get_crud_config",
    # Factory
    "CRUDFactory",
    "get_default_factory",
    "reset_default_factory",
    # Configuration
    "InstantCRUDSettings",
    "SettingsManager",
    # Components
    "BaseService",
    "CRUDRouter",
    "PaginationResponseBuilder",
    "create_pagination_builder",
    # Version
    "__version__",
]

# Convenience imports for quick start


def setup(
    get_session=None,
    get_current_user=None,
    get_user_with_roles=None,
    config_file=None,
):
    """
    Quick setup function for instant-crud.

    Args:
        get_session: Function to get database session
        get_current_user: Function to get current user
        get_user_with_roles: Function to get user with roles
        config_file: Path to configuration file

    Returns:
        Configured CRUDFactory instance
    """
    return CRUDFactory(
        get_session=get_session,
        get_current_user=get_current_user,
        get_user_with_roles=get_user_with_roles,
        config_file=config_file,
    )
