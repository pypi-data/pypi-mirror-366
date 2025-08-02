"""
Core factory for creating CRUD routers and services.
Main entry point for instant-crud library functionality.
"""

import logging
from collections.abc import Callable
from typing import Any, TypeVar

from fastapi import APIRouter
from pydantic import BaseModel
from sqlmodel import Session, SQLModel

from instant_crud.core.strings import Strings

from ..config.settings import InstantCRUDSettings, SettingsManager
from ..response.pagination import create_pagination_builder
from ..routers.crud_router import CRUDRouter
from ..services.base_service import BaseService

T = TypeVar("T", bound=SQLModel)


class CRUDFactory:
    """
    Factory for creating CRUD routers and services.

    Main entry point for instant-crud functionality.
    Manages configuration, pagination, authentication, and router creation.
    """

    def __init__(
        self,
        get_session: Callable[[], Session] | None = None,
        get_current_user: Callable | None = None,
        get_user_with_roles: Callable | None = None,
        settings: InstantCRUDSettings | None = None,
        config_file: str | None = None,
    ):
        """
        Initialize CRUD factory.

        Args:
            get_session: Function to get database session
            get_current_user: Function to get current authenticated user
            get_user_with_roles: Function to get user with role information
            settings: Custom settings instance
            config_file: Path to configuration file
        """
        # Configuration
        if settings:
            self.settings = settings
        else:
            self.settings = SettingsManager.get_settings(config_file)

        # Validate required dependencies
        # if get_session is None:
        #     raise ValueError("get_session function is required")

        # Dependencies
        self.get_session = get_session
        self.get_current_user = get_current_user

        self.get_user_with_roles = get_user_with_roles or get_current_user

        # Pagination builder
        pagination_config = self.settings.get_pagination_config()
        self.pagination_builder = create_pagination_builder(pagination_config)

        # Logger
        self.logger = logging.getLogger("instant_crud.factory")

        # Registry for created routers
        self._routers: dict[str, CRUDRouter] = {}
        self._registered_models: list[dict[str, Any]] = []

    def create_crud_router(
        self,
        model: type[T],
        create_schema: type[BaseModel] | None = None,
        read_schema: type[BaseModel] | None = None,
        prefix: str | None = None,
        tags: list[str] | None = None,
        search_fields: list[str] | None = None,
        export_enabled: bool | None = None,
        auth_enabled: bool | None = None,
        read_only: bool = False,
        service_class: type[BaseService] | None = None,
        **kwargs,
    ) -> APIRouter:
        """
        Create CRUD router for a model.

        Args:
            model: SQLModel class
            create_schema: Pydantic schema for creation (auto-generated if None)
            read_schema: Pydantic schema for reading (auto-generated if None)
            prefix: URL prefix (auto-generated if None)
            tags: OpenAPI tags (auto-generated if None)
            search_fields: Fields to search in (auto-detected if None)
            export_enabled: Enable export endpoints (uses global setting if None)
            auth_enabled: Enable authentication (uses global setting if None)
            read_only: If True, only create read endpoints
            service_class: Custom service class (uses BaseService if None)
            **kwargs: Additional router configuration

        Returns:
            FastAPI APIRouter instance
        """
        # Auto-generate schemas if not provided
        if create_schema is None:
            create_schema = self._generate_create_schema(model)

        if read_schema is None:
            read_schema = self._generate_read_schema(model)

        # Auto-generate configuration
        if prefix is None:
            prefix = f"/{self._get_model_name_plural(model)}"

        if tags is None:
            tags = [self._get_model_display_name(model)]

        if search_fields is None:
            search_fields = self._auto_detect_search_fields(model)

        # Use global settings for optional parameters
        if export_enabled is None:
            export_enabled = self.settings.enable_export

        if auth_enabled is None:
            auth_enabled = self.settings.enable_auth

        # Default service class
        if service_class is None:
            service_class = BaseService
        if self.get_session is None:
            raise ValueError(
                "get_session function is required when creating routers. "
                "Provide it in CRUDFactory() or when calling create_crud_router()"
            )
        # Determine dependencies based on auth settings
        dependencies = self._get_dependencies(auth_enabled)

        # Validate that get_session is available
        if not self.get_session:
            raise ValueError(
                "get_session function is required when creating routers. "
                "Provide it in CRUDFactory() or when calling create_crud_router()"
            )

        # Create CRUD router
        crud_router = CRUDRouter(
            model=model,
            create_schema=create_schema,
            read_schema=read_schema,
            service_class=service_class,
            prefix=prefix,
            tags=tags,
            get_session=self.get_session,  # Ora è sicuro che non sia None
            get_current_user_dependency=dependencies["current_user"],
            get_user_with_roles_dependency=dependencies["user_with_roles"],
            pagination_builder=self.pagination_builder,
            search_fields=search_fields,
            export_enabled=export_enabled,
            read_only=read_only,
            settings=self.settings,
            **kwargs,
        )

        # Register router
        self._routers[prefix] = crud_router

        self.logger.info(Strings.CORE_FACTORY_CRUD_ROUTER_CREATED, model.__name__, prefix)

        return crud_router.router

    def create_service(
        self,
        model: type[T],
        session: Session,
        service_class: type[BaseService] | None = None,
        **kwargs,
    ) -> BaseService[T]:
        """
        Create service instance for a model.

        Args:
            model: SQLModel class
            session: Database session
            service_class: Custom service class (uses BaseService if None)
            **kwargs: Additional service configuration

        Returns:
            Service instance
        """
        if service_class is None:
            service_class = BaseService

        return service_class(
            session=session,
            model_class=model,
            pagination_builder=self.pagination_builder,
            logger=logging.getLogger(f"instant_crud.service.{model.__name__}"),
            **kwargs,
        )

    def register_model(self, model: type[T], **router_kwargs) -> None:
        """
        Register a model for delayed router creation.
        Used by the @auto_crud_api decorator.

        Args:
            model: SQLModel class
            **router_kwargs: Router configuration
        """
        self._registered_models.append({"model": model, "config": router_kwargs})

        self.logger.info(Strings.CORE_FACTORY_MODEL_REGISTERED, model.__name__)

    def create_routers_for_registered_models(self) -> list[APIRouter]:
        """
        Create routers for all registered models.

        Returns:
            List of created APIRouter instances
        """
        routers = []

        for model_info in self._registered_models:
            router = self.create_crud_router(
                model=model_info["model"], **model_info["config"]
            )
            routers.append(router)

        self.logger.info(Strings.CORE_FACTORY_ROUTERS_CREATED, len(routers))
        return routers

    def get_router(self, prefix: str) -> CRUDRouter | None:
        """
        Get router by prefix.

        Args:
            prefix: Router URL prefix

        Returns:
            CRUDRouter instance or None
        """
        return self._routers.get(prefix)

    def get_all_routers(self) -> dict[str, CRUDRouter]:
        """
        Get all created routers.

        Returns:
            Dictionary mapping prefixes to routers
        """
        return self._routers.copy()

    def _generate_create_schema(self, model: type[T]) -> type[BaseModel]:
        """
        Auto-generate create schema from model.

        Args:
            model: SQLModel class

        Returns:
            Pydantic BaseModel class for creation
        """
        # For now, use the model itself as schema
        # In future versions, we could generate optimized schemas
        # that exclude auto-generated fields like ID, timestamps, etc.
        return model

    def _generate_read_schema(self, model: type[T]) -> type[BaseModel]:
        """
        Auto-generate read schema from model.

        Args:
            model: SQLModel class

        Returns:
            Pydantic BaseModel class for reading
        """
        # For now, use the model itself as schema
        return model

    def _get_model_name_plural(self, model: type[T]) -> str:
        """
        Get plural form of model name for URL prefix.

        Args:
            model: SQLModel class

        Returns:
            Plural model name in lowercase
        """
        name = model.__name__.lower()

        # Simple pluralization rules
        if name.endswith("y"):
            return name[:-1] + "ies"
        elif name.endswith(("s", "sh", "ch", "x", "z")):
            return name + "es"
        else:
            return name + "s"

    def _get_model_display_name(self, model: type[T]) -> str:
        """
        Get display name for model (used in OpenAPI tags).

        Args:
            model: SQLModel class

        Returns:
            Display name for the model
        """
        # Convert CamelCase to Title Case
        name = model.__name__

        # Add spaces before uppercase letters
        result = []
        for i, char in enumerate(name):
            if i > 0 and char.isupper():
                result.append(" ")
            result.append(char)

        return "".join(result)

    def _auto_detect_search_fields(self, model: type[T]) -> list[str]:
        """
        Auto-detect searchable fields in model.

        Args:
            model: SQLModel class

        Returns:
            List of field names suitable for text search
        """
        search_fields = []

        # Usa getattr per accedere a __table__ in modo sicuro
        table = getattr(model, "__table__", None)
        if table is not None and hasattr(table, "columns"):
            for column in table.columns:
                # Include string/text columns for search
                if str(column.type).startswith(("VARCHAR", "TEXT", "String")):
                    search_fields.append(column.name)

        return search_fields

    def _get_dependencies(self, auth_enabled: bool) -> dict[str, Callable | None]:
        """
        Get dependency functions based on authentication settings.

        Args:
            auth_enabled: Whether authentication is enabled

        Returns:
            Dictionary with dependency functions
        """
        if auth_enabled:
            return {
                "current_user": self.get_current_user,
                "user_with_roles": self.get_user_with_roles,
            }
        else:
            return {"current_user": None, "user_with_roles": None}

    def set_session_function(self, get_session_func):
        """Set the session function after factory creation."""
        self.get_session = get_session_func


# Global factory instance
_default_factory: CRUDFactory | None = None


def get_default_factory(
    get_session: Callable[[], Session] | None = None,
    get_current_user: Callable | None = None,
    get_user_with_roles: Callable | None = None,
    config_file: str | None = None,
) -> CRUDFactory:
    """
    Get or create default factory instance.
    """
    global _default_factory

    if _default_factory is None:
        _default_factory = CRUDFactory(
            get_session=get_session,  # Può essere None per i decorator
            get_current_user=get_current_user,
            get_user_with_roles=get_user_with_roles,
            config_file=config_file,
        )

    return _default_factory


def reset_default_factory() -> None:
    """Reset default factory instance. Useful for testing."""
    global _default_factory
    _default_factory = None
