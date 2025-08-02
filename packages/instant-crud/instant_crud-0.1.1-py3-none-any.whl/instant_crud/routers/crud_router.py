"""
Generic CRUD router for instant-crud library.
Fixed version with proper dependency injection.
"""

from typing import Any, Callable, Dict, List, Optional, Sequence, Type, TypeVar, Union

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query, status
from fastapi.params import Depends as DependsType
from pydantic import BaseModel
from sqlmodel import Session, SQLModel

from ..config.settings import InstantCRUDSettings
from ..response.pagination import PaginationResponseBuilder
from ..services.base_service import BaseService

T = TypeVar("T", bound=SQLModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
ReadSchemaType = TypeVar("ReadSchemaType", bound=BaseModel)


class CRUDRouter:
    """
    Generic CRUD router for SQLModel entities.

    Automatically generates REST endpoints for:
    - GET /items (list with pagination)
    - GET /items/{id} (get by ID)
    - POST /items (create)
    - PUT /items/{id} (update)
    - PATCH /items/{id} (partial update)
    - DELETE /items/{id} (delete)
    - GET /items/search (search)
    - GET /items/count (count)
    """

    def __init__(
        self,
        model: Type[T],
        create_schema: Type[CreateSchemaType],
        read_schema: Type[ReadSchemaType],
        service_class: Type[BaseService],
        prefix: str,
        tags: Optional[Sequence[str]],
        get_session: Callable[[], Session],
        get_current_user_dependency: Optional[Callable] = None,
        get_user_with_roles_dependency: Optional[Callable] = None,
        pagination_builder: Optional[PaginationResponseBuilder] = None,
        search_fields: Optional[List[str]] = None,
        export_enabled: bool = True,
        read_only: bool = False,
        settings: Optional[InstantCRUDSettings] = None,
        **kwargs,
    ):
        """Initialize CRUD router."""
        self.model = model
        self.create_schema = create_schema
        self.read_schema = read_schema
        self.service_class = service_class
        self.prefix = prefix
        self.tags = list(tags) if tags else []
        self.get_session = get_session
        self.get_current_user_dependency = get_current_user_dependency
        self.get_user_with_roles_dependency = get_user_with_roles_dependency
        self.pagination_builder = pagination_builder
        self.search_fields = search_fields or []
        self.export_enabled = export_enabled
        self.read_only = read_only
        self.settings = settings

        # Create FastAPI router
        router_tags: Optional[List[Union[str, Any]]] = None
        if tags:
            router_tags = list(tags)

        self.router = APIRouter(prefix=prefix, tags=router_tags)

        # Configure routes
        self._configure_routes()

    def _configure_routes(self) -> None:
        """Configure all CRUD routes."""
        self._add_read_routes()

        if not self.read_only:
            self._add_write_routes()

    def _add_read_routes(self) -> None:
        """Add read-only routes."""
        # Get all items (paginated)
        self.router.add_api_route(
            "/",
            self._create_get_items_endpoint(),
            methods=["GET"],
            response_model=Dict[str, Any],
            summary=f"Get all {self.model.__name__} items",
            dependencies=self._get_read_dependencies(),
        )

        # Get item by ID
        self.router.add_api_route(
            "/{item_id}",
            self._create_get_item_endpoint(),
            methods=["GET"],
            response_model=self.read_schema,
            summary=f"Get {self.model.__name__} by ID",
            dependencies=self._get_read_dependencies(),
        )

        # Search items
        self.router.add_api_route(
            "/search",
            self._create_search_items_endpoint(),
            methods=["GET"],
            response_model=Dict[str, Any],
            summary=f"Search {self.model.__name__} items",
            dependencies=self._get_read_dependencies(),
        )

        # Count items
        self.router.add_api_route(
            "/count",
            self._create_count_items_endpoint(),
            methods=["GET"],
            response_model=int,
            summary=f"Count {self.model.__name__} items",
            dependencies=self._get_read_dependencies(),
        )

    def _add_write_routes(self) -> None:
        """Add write routes."""
        # Create item
        self.router.add_api_route(
            "/",
            self._create_create_item_endpoint(),
            methods=["POST"],
            response_model=self.read_schema,
            summary=f"Create {self.model.__name__}",
            status_code=status.HTTP_201_CREATED,
            dependencies=self._get_write_dependencies(),
        )

        # Create multiple items
        self.router.add_api_route(
            "/batch",
            self._create_create_items_endpoint(),
            methods=["POST"],
            response_model=List[self.read_schema],
            summary=f"Create multiple {self.model.__name__} items",
            status_code=status.HTTP_201_CREATED,
            dependencies=self._get_write_dependencies(),
        )

        # Update item
        self.router.add_api_route(
            "/{item_id}",
            self._create_update_item_endpoint(),
            methods=["PUT"],
            response_model=self.read_schema,
            summary=f"Update {self.model.__name__}",
            dependencies=self._get_write_dependencies(),
        )

        # Patch item
        self.router.add_api_route(
            "/{item_id}",
            self._create_patch_item_endpoint(),
            methods=["PATCH"],
            response_model=self.read_schema,
            summary=f"Partially update {self.model.__name__}",
            dependencies=self._get_write_dependencies(),
        )

        # Delete item
        self.router.add_api_route(
            "/{item_id}",
            self._create_delete_item_endpoint(),
            methods=["DELETE"],
            response_model=Dict[str, bool],
            summary=f"Delete {self.model.__name__}",
            dependencies=self._get_write_dependencies(),
        )

        # Delete multiple items
        self.router.add_api_route(
            "/batch",
            self._create_delete_items_endpoint(),
            methods=["DELETE"],
            response_model=Dict[str, Any],
            summary=f"Delete multiple {self.model.__name__} items",
            dependencies=self._get_write_dependencies(),
        )

    def _get_service(self, session: Session) -> BaseService[T]:
        """Get service instance."""
        return self.service_class(
            session=session,
            model_class=self.model,
            pagination_builder=self.pagination_builder,
        )

    def _get_read_dependencies(self) -> List[DependsType]:
        """Get dependencies for read operations."""
        deps = []
        if self.get_current_user_dependency:
            deps.append(Depends(self.get_current_user_dependency))
        return deps

    def _get_write_dependencies(self) -> List[DependsType]:
        """Get dependencies for write operations."""
        deps = []
        if self.get_user_with_roles_dependency:
            deps.append(Depends(self.get_user_with_roles_dependency))
        elif self.get_current_user_dependency:
            deps.append(Depends(self.get_current_user_dependency))
        return deps

    # Endpoint factory methods - these create the actual endpoint functions

    def _create_get_items_endpoint(self):
        """Create get items endpoint function."""

        def get_items(
            skip: int = Query(0, ge=0, description="Number of items to skip"),
            limit: int = Query(
                100, ge=1, le=1000, description="Number of items to return"
            ),
            order_by: Optional[str] = Query(None, description="Field to order by"),
            desc_order: bool = Query(False, description="Order descending"),
            session: Session = Depends(self.get_session),
        ) -> Dict[str, Any]:
            """Get all items with pagination."""
            service = self._get_service(session)

            # Apply settings limits
            if self.settings:
                limit = min(limit, self.settings.max_page_size)

            return service.get_all_paginated(
                skip=skip,
                limit=limit,
                order_by=order_by,
                desc_order=desc_order,
            )

        return get_items

    def _create_get_item_endpoint(self):
        """Create get item endpoint function."""

        def get_item(
            item_id: int = Path(..., description="Item ID"),
            session: Session = Depends(self.get_session),
        ) -> ReadSchemaType:
            """Get item by ID."""
            service = self._get_service(session)
            item = service.get_by_id(item_id)

            if not item:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"{self.model.__name__} not found",
                )

            return item

        return get_item

    def _create_search_items_endpoint(self):
        """Create search items endpoint function."""

        def search_items(
            q: str = Query(..., description="Search query"),
            skip: int = Query(0, ge=0, description="Number of items to skip"),
            limit: int = Query(
                100, ge=1, le=1000, description="Number of items to return"
            ),
            order_by: Optional[str] = Query(None, description="Field to order by"),
            desc_order: bool = Query(False, description="Order descending"),
            session: Session = Depends(self.get_session),
        ) -> Dict[str, Any]:
            """Search items."""
            service = self._get_service(session)

            # Apply settings limits
            if self.settings:
                limit = min(limit, self.settings.max_page_size)

            return service.search_paginated(
                query_text=q,
                search_columns=self.search_fields,
                skip=skip,
                limit=limit,
                order_by=order_by,
                desc_order=desc_order,
            )

        return search_items

    def _create_count_items_endpoint(self):
        """Create count items endpoint function."""

        def count_items(
            session: Session = Depends(self.get_session),
        ) -> int:
            """Count items."""
            service = self._get_service(session)
            return service.count()

        return count_items

    def _create_create_item_endpoint(self):
        """Create create item endpoint function."""

        def create_item(
            item: CreateSchemaType = Body(..., description="Item to create"),
            session: Session = Depends(self.get_session),
        ) -> ReadSchemaType:
            """Create new item."""
            service = self._get_service(session)
            created_item = service.create(item, is_pydantic=True)

            if not created_item:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create item",
                )

            return created_item

        return create_item

    def _create_create_items_endpoint(self):
        """Create create items endpoint function."""

        def create_items(
            items: List[CreateSchemaType] = Body(..., description="Items to create"),
            session: Session = Depends(self.get_session),
        ) -> List[ReadSchemaType]:
            """Create multiple items."""
            service = self._get_service(session)
            created_items = service.create_many(items, is_pydantic=True)

            if not created_items:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create items",
                )

            return created_items

        return create_items

    def _create_update_item_endpoint(self):
        """Create update item endpoint function."""

        def update_item(
            item_id: int = Path(..., description="Item ID"),
            item: CreateSchemaType = Body(..., description="Updated item data"),
            session: Session = Depends(self.get_session),
        ) -> ReadSchemaType:
            """Update item."""
            service = self._get_service(session)
            updated_item = service.update(item_id, item, is_pydantic=True)

            if not updated_item:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"{self.model.__name__} not found",
                )

            return updated_item

        return update_item

    def _create_patch_item_endpoint(self):
        """Create patch item endpoint function."""

        def patch_item(
            item_id: int = Path(..., description="Item ID"),
            item: Dict[str, Any] = Body(..., description="Partial item data"),
            session: Session = Depends(self.get_session),
        ) -> ReadSchemaType:
            """Partially update item."""
            service = self._get_service(session)
            updated_item = service.patch(item_id, item, is_pydantic=False)

            if not updated_item:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"{self.model.__name__} not found",
                )

            return updated_item

        return patch_item

    def _create_delete_item_endpoint(self):
        """Create delete item endpoint function."""

        def delete_item(
            item_id: int = Path(..., description="Item ID"),
            session: Session = Depends(self.get_session),
        ) -> Dict[str, bool]:
            """Delete item."""
            service = self._get_service(session)
            result = service.delete(item_id)

            if not result.get("success", False):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"{self.model.__name__} not found",
                )

            return result

        return delete_item

    def _create_delete_items_endpoint(self):
        """Create delete items endpoint function."""

        def delete_items(
            ids: List[int] = Body(..., description="List of item IDs to delete"),
            session: Session = Depends(self.get_session),
        ) -> Dict[str, Any]:
            """Delete multiple items."""
            service = self._get_service(session)
            return service.delete_many(ids)

        return delete_items
