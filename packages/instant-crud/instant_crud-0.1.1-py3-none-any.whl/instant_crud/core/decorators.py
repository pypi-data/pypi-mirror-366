"""
Decorators for instant-crud library.
Provides @auto_crud_api decorator for automatic CRUD API generation.
"""

from typing import Any, Callable, Dict, List, Optional, Type, TypeVar

from pydantic import BaseModel
from sqlmodel import SQLModel

from .factory import get_default_factory

T = TypeVar("T", bound=SQLModel)


def auto_crud_api(
    prefix: Optional[str] = None,
    tags: Optional[List[str]] = None,
    create_schema: Optional[Type[BaseModel]] = None,
    read_schema: Optional[Type[BaseModel]] = None,
    search_fields: Optional[List[str]] = None,
    export_enabled: Optional[bool] = None,
    auth_enabled: Optional[bool] = None,
    read_only: bool = False,
    **kwargs,
) -> Callable[[Type[T]], Type[T]]:
    """
    Decorator to automatically generate CRUD API for a SQLModel.
    
    Usage:
        @auto_crud_api(prefix="/users", tags=["Users"])
        class User(SQLModel, table=True):
            id: Optional[int] = Field(primary_key=True)
            name: str
            email: str
    
    Args:
        prefix: URL prefix for the API routes (auto-generated if None)
        tags: OpenAPI tags for documentation (auto-generated if None)
        create_schema: Pydantic schema for creation (auto-generated if None)
        read_schema: Pydantic schema for reading (auto-generated if None)
        search_fields: Fields to enable search on (auto-detected if None)
        export_enabled: Enable export endpoints (uses global setting if None)
        auth_enabled: Enable authentication (uses global setting if None)
        read_only: If True, only generate read endpoints
        **kwargs: Additional router configuration
        
    Returns:
        Decorated class (unchanged)
    """
    def decorator(model_class: Type[T]) -> Type[T]:
        # Get default factory
        factory = get_default_factory()

        # Register model for router creation
        factory.register_model(
            model=model_class,
            prefix=prefix,
            tags=tags,
            create_schema=create_schema,
            read_schema=read_schema,
            search_fields=search_fields,
            export_enabled=export_enabled,
            auth_enabled=auth_enabled,
            read_only=read_only,
            **kwargs
        )

        return model_class

    return decorator


def crud_config(
    search_fields: Optional[List[str]] = None,
    export_enabled: Optional[bool] = None,
    auth_enabled: Optional[bool] = None,
    read_only: bool = False,
    **kwargs
) -> Callable[[Type[T]], Type[T]]:
    """
    Decorator to configure CRUD behavior without auto-generating routes.
    
    This decorator only adds metadata to the model class.
    Use with create_crud_router() for explicit router creation.
    
    Usage:
        @crud_config(search_fields=["name", "email"], read_only=True)
        class User(SQLModel, table=True):
            id: Optional[int] = Field(primary_key=True)
            name: str
            email: str
    
    Args:
        search_fields: Fields to enable search on
        export_enabled: Enable export endpoints
        auth_enabled: Enable authentication
        read_only: If True, only generate read endpoints
        **kwargs: Additional configuration
        
    Returns:
        Decorated class with CRUD metadata
    """
    def decorator(model_class: Type[T]) -> Type[T]:
        # Add CRUD configuration as class attribute
        crud_metadata = {
            "search_fields": search_fields,
            "export_enabled": export_enabled,
            "auth_enabled": auth_enabled,
            "read_only": read_only,
            **kwargs
        }
        
        setattr(model_class, "__crud_config__", crud_metadata)
        
        return model_class
    
    return decorator


def get_crud_config(model_class: Type[T]) -> Dict[str, Any]:
    """
    Get CRUD configuration from a model class.
    
    Args:
        model_class: SQLModel class
        
    Returns:
        Dictionary with CRUD configuration
    """
    return getattr(model_class, "__crud_config__", {})


# Convenience aliases
crud_api = auto_crud_api  # Shorter alias
api = auto_crud_api       # Even shorter alias
