"""
Base service class for instant-crud library.
Simplified version of BaseGenericDbService with core CRUD operations.
"""

import logging
from collections.abc import Sequence
from typing import Any, Optional, TypeVar

from pydantic import BaseModel
from sqlmodel import Session, SQLModel

from instant_crud.core.strings import Strings

from ..config.settings import SettingsManager
from ..response.pagination import PaginationResponseBuilder

T = TypeVar("T", bound=SQLModel)  # More specific type bound


class BaseService[T: SQLModel]:
    """
    Base service for CRUD operations.
    Provides core functionality for database operations with pagination support.
    """

    def __init__(
        self,
        session: Session,
        model_class: type[T],
        pagination_builder: PaginationResponseBuilder | None = None,
        logger: logging.Logger | None = None,
        suppress_exceptions: bool = False,
    ):
        """
        Initialize base service.

        Args:
            session: Database session
            model_class: SQLModel class
            pagination_builder: Optional pagination builder
            logger: Optional logger instance
            suppress_exceptions: If True, suppress exceptions and return defaults
        """
        self.session = session
        self.model_class = model_class
        self.pagination_builder = pagination_builder
        self.suppress_exceptions = suppress_exceptions

        # Configure logger
        if logger:
            self.logger = logger
        else:
            self.logger = logging.getLogger(
                f"{self.__class__.__name__}_{model_class.__name__}"
            )

        # Get settings
        self.settings = SettingsManager.get_settings()

    def _is_sqlmodel_table(self) -> bool:
        """Check if the model class is a proper SQLModel table."""
        return (
            hasattr(self.model_class, "__table__")
            and getattr(self.model_class, "__table__", None) is not None
            and hasattr(self.model_class, "__tablename__")
        )

    def _get_searchable_columns(self) -> list[str]:
        """Get list of searchable string columns from the model."""
        search_columns = []

        if not self._is_sqlmodel_table():
            return search_columns

        # Usa getattr per accedere a __table__ in modo sicuro
        table = getattr(self.model_class, "__table__", None)
        if table is not None and hasattr(table, "columns"):
            for column in table.columns:
                if str(column.type).startswith(("VARCHAR", "TEXT", "String")):
                    search_columns.append(column.name)

        return search_columns

    def _log_operation(self, operation: str, **kwargs):
        """Log operation with parameters."""
        if self.logger:
            self.logger.info(Strings.SERVICES_BASE_OPERATION, operation, kwargs)

    def _log_error(self, message: str, *args) -> None:
        """Log error message."""
        if self.logger:
            self.logger.error(message, *args)

    def _log_info(self, message: str, *args) -> None:
        """Log info message."""
        if self.logger:
            self.logger.info(message, *args)

    def _handle_exception(
        self, e: Exception, operation: str, default_return: Any = None
    ) -> Any:
        """
        Handle exceptions based on suppress_exceptions setting.

        Args:
            e: Exception that occurred
            operation: Name of operation that failed
            default_return: Default value to return if suppressing exceptions

        Returns:
            Default return value or raises exception
        """
        self._log_error(f"Error in {operation}: {str(e)}")

        if self.suppress_exceptions:
            return default_return
        else:
            raise e

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        order_by: str | None = None,
        desc_order: bool = False,
        **filters,
    ) -> list[T]:
        """
        Get all objects with pagination and filters.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            order_by: Field to order by
            desc_order: If True, order descending
            **filters: Filters to apply

        Returns:
            list of objects
        """
        try:
            query = self.session.query(self.model_class)

            # Apply filters
            for field, value in filters.items():
                if hasattr(self.model_class, field):
                    query = query.filter(getattr(self.model_class, field) == value)

            # Apply ordering
            if order_by and hasattr(self.model_class, order_by):
                order_column = getattr(self.model_class, order_by)
                if desc_order:
                    query = query.order_by(order_column.desc())
                else:
                    query = query.order_by(order_column)

            # Apply pagination
            return query.offset(skip).limit(limit).all()

        except Exception as e:
            return self._handle_exception(e, "get_all", [])

    def get_all_paginated(
        self,
        skip: int = 0,
        limit: int = 100,
        order_by: str | None = None,
        desc_order: bool = False,
        **filters,
    ) -> dict[str, Any]:
        """
        Get all objects with pagination information.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            order_by: Field to order by
            desc_order: If True, order descending
            **filters: Filters to apply

        Returns:
            Dictionary with items and pagination info
        """
        try:
            # Get total count
            total = self.count(**filters)

            # Get items
            items = self.get_all(
                skip=skip,
                limit=limit,
                order_by=order_by,
                desc_order=desc_order,
                **filters,
            )

            # Build pagination response
            if self.pagination_builder:
                return self.pagination_builder.build_response(
                    items=items, total=total, skip=skip, limit=limit
                )
            else:
                # Default format
                return {"items": items, "total": total, "skip": skip, "limit": limit}

        except Exception as e:
            return self._handle_exception(
                e,
                "get_all_paginated",
                {"items": [], "total": 0, "skip": skip, "limit": limit},
            )

    def get_by_id(self, id: Any) -> T | None:
        """
        Get object by ID.

        Args:
            id: Object ID

        Returns:
            Object or None if not found
        """
        try:
            return self.session.get(self.model_class, id)
        except Exception as e:
            return self._handle_exception(e, "get_by_id", None)

    def create(
        self, data: dict[str, Any] | BaseModel, is_pydantic: bool = False
    ) -> T | None:
        """
        Create new object.

        Args:
            data: Data for new object
            is_pydantic: If True, data is a Pydantic model

        Returns:
            Created object
        """
        try:
            # Convert data to dict if Pydantic model
            if is_pydantic and isinstance(data, BaseModel):
                data_dict = data.model_dump()
            elif isinstance(data, dict):
                data_dict = data
            else:
                # Fallback: try to convert to dict if it has model_dump method
                if hasattr(data, "model_dump") and callable(data.model_dump):
                    data_dict = data.model_dump()
                else:
                    data_dict = dict(data) if hasattr(data, "__iter__") else {}

            # Create object
            obj = self.model_class(**data_dict)
            self.session.add(obj)
            self.session.commit()
            self.session.refresh(obj)

            self._log_info(
                f"Created {self.model_class.__name__} with id {getattr(obj, 'id', 'N/A')}"
            )
            return obj

        except Exception as e:
            self.session.rollback()
            return self._handle_exception(e, "create", None)

    def create_many(
        self,
        data_list: Sequence[
            dict[str, Any] | BaseModel
        ],  # Changed from list to Sequence
        is_pydantic: bool = False,
    ) -> list[T]:
        """
        Create multiple objects.

        Args:
            data_list: Sequence of data for new objects (supports both list and other sequences)
            is_pydantic: If True, data items are Pydantic models

        Returns:
            list of created objects
        """
        try:
            created_objects = []

            for data in data_list:
                # Convert data to dict if Pydantic model
                if is_pydantic and isinstance(data, BaseModel):
                    data_dict = data.model_dump()
                elif isinstance(data, dict):
                    data_dict = data
                else:
                    # Fallback: try to convert to dict if it has model_dump method
                    if hasattr(data, "model_dump") and callable(data.model_dump):
                        data_dict = data.model_dump()
                    else:
                        data_dict = dict(data) if hasattr(data, "__iter__") else {}

                obj = self.model_class(**data_dict)
                self.session.add(obj)
                created_objects.append(obj)

            self.session.commit()

            # Refresh all objects
            for obj in created_objects:
                self.session.refresh(obj)

            self._log_info(
                f"Created {len(created_objects)} {self.model_class.__name__} objects"
            )
            return created_objects

        except Exception as e:
            self.session.rollback()
            return self._handle_exception(e, "create_many", [])

    def update(
        self,
        id: Any,
        update_data: dict[str, Any] | BaseModel,
        is_pydantic: bool = False,
    ) -> T | None:
        """
        Update object by ID.

        Args:
            id: Object ID
            update_data: Data to update
            is_pydantic: If True, update_data is a Pydantic model

        Returns:
            Updated object or None
        """
        try:
            obj = self.get_by_id(id)
            if not obj:
                return None

            # Convert data to dict if Pydantic model
            if is_pydantic and isinstance(update_data, BaseModel):
                data_dict = update_data.model_dump()
            elif isinstance(update_data, dict):
                data_dict = update_data
            else:
                # Fallback: try to convert to dict if it has model_dump method
                if hasattr(update_data, "model_dump") and callable(
                    update_data.model_dump
                ):
                    data_dict = update_data.model_dump()
                else:
                    data_dict = (
                        dict(update_data) if hasattr(update_data, "__iter__") else {}
                    )

            # Update object attributes
            for key, value in data_dict.items():
                if hasattr(obj, key):
                    setattr(obj, key, value)

            self.session.commit()
            self.session.refresh(obj)

            self._log_info(f"Updated {self.model_class.__name__} with id {id}")
            return obj

        except Exception as e:
            self.session.rollback()
            return self._handle_exception(e, "update", None)

    def patch(
        self,
        id: Any,
        patch_data: dict[str, Any] | BaseModel,
        is_pydantic: bool = False,
    ) -> T | None:
        """
        Partially update object by ID.

        Args:
            id: Object ID
            patch_data: Partial data to update
            is_pydantic: If True, patch_data is a Pydantic model

        Returns:
            Updated object or None
        """
        # For now, patch is the same as update
        return self.update(id, patch_data, is_pydantic)

    def delete(self, id: Any) -> dict[str, bool]:
        """
        Delete object by ID.

        Args:
            id: Object ID

        Returns:
            Dictionary with success status
        """
        try:
            obj = self.get_by_id(id)
            if not obj:
                return {"success": False}

            self.session.delete(obj)
            self.session.commit()

            self._log_info(f"Deleted {self.model_class.__name__} with id {id}")
            return {"success": True}

        except Exception as e:
            self.session.rollback()
            return self._handle_exception(e, "delete", {"success": False})

    def delete_many(self, ids: list[Any]) -> dict[str, Any]:
        """
        Delete multiple objects by IDs.

        Args:
            ids: list of object IDs

        Returns:
            Dictionary with deletion results
        """
        try:
            deleted_count = 0
            not_found = []

            for obj_id in ids:
                obj = self.get_by_id(obj_id)
                if obj:
                    self.session.delete(obj)
                    deleted_count += 1
                else:
                    not_found.append(obj_id)

            self.session.commit()

            self._log_info(
                f"Deleted {deleted_count} {self.model_class.__name__} objects"
            )

            return {
                "success": True,
                "deleted_count": deleted_count,
                "not_found": not_found,
            }

        except Exception as e:
            self.session.rollback()
            return self._handle_exception(
                e,
                "delete_many",
                {"success": False, "deleted_count": 0, "not_found": ids},
            )

    def count(self, **filters) -> int:
        """
        Count objects matching filters.

        Args:
            **filters: Filters to apply

        Returns:
            Number of objects
        """
        try:
            query = self.session.query(self.model_class)

            # Apply filters
            for field, value in filters.items():
                if hasattr(self.model_class, field):
                    query = query.filter(getattr(self.model_class, field) == value)

            return query.count()

        except Exception as e:
            return self._handle_exception(e, "count", 0)

    def search(
        self,
        query_text: str,
        search_columns: Optional[list[str]] = None,
        skip: int = 0,
        limit: int = 100,
        order_by: str | None = None,
        desc_order: bool = False,
        **filters,
    ) -> list[T]:
        """
        Search objects by text query.

        Args:
            query_text: Text to search for
            search_columns: Columns to search in
            skip: Number of records to skip
            limit: Maximum number of records to return
            order_by: Field to order by
            desc_order: If True, order descending
            **filters: Additional filters to apply

        Returns:
            list of matching objects
        """
        try:
            if not query_text.strip():
                return []

            query = self.session.query(self.model_class)

            # Determine search columns
            if not search_columns:
                search_columns = self._get_searchable_columns()

            # Build search criteria
            search_criteria = []
            for col_name in search_columns:
                if hasattr(self.model_class, col_name):
                    column = getattr(self.model_class, col_name)
                    search_criteria.append(column.ilike(f"%{query_text}%"))

            if search_criteria:
                from sqlalchemy import or_

                query = query.filter(or_(*search_criteria))

            # Apply additional filters
            for field, value in filters.items():
                if hasattr(self.model_class, field):
                    query = query.filter(getattr(self.model_class, field) == value)

            # Apply ordering
            if order_by and hasattr(self.model_class, order_by):
                order_column = getattr(self.model_class, order_by)
                if desc_order:
                    query = query.order_by(order_column.desc())
                else:
                    query = query.order_by(order_column)

            # Apply pagination
            return query.offset(skip).limit(limit).all()

        except Exception as e:
            return self._handle_exception(e, "search", [])

    def search_paginated(
        self,
        query_text: str,
        search_columns: list[str] | None = None,
        skip: int = 0,
        limit: int = 100,
        order_by: str | None = None,
        desc_order: bool = False,
        **filters,
    ) -> dict[str, Any]:
        """
        Search objects with pagination information.

        Args:
            query_text: Text to search for
            search_columns: Columns to search in
            skip: Number of records to skip
            limit: Maximum number of records to return
            order_by: Field to order by
            desc_order: If True, order descending
            **filters: Additional filters to apply

        Returns:
            Dictionary with search results and pagination info
        """
        try:
            if not query_text.strip():
                return {"items": [], "total": 0, "skip": skip, "limit": limit}

            # Get search results
            items = self.search(
                query_text=query_text,
                search_columns=search_columns,
                skip=skip,
                limit=limit,
                order_by=order_by,
                desc_order=desc_order,
                **filters,
            )

            # Count total results (without pagination)
            total_query = self.session.query(self.model_class)

            # Determine search columns
            if not search_columns:
                search_columns = self._get_searchable_columns()

            # Build search criteria for count
            search_criteria = []
            for col_name in search_columns:
                if hasattr(self.model_class, col_name):
                    column = getattr(self.model_class, col_name)
                    search_criteria.append(column.ilike(f"%{query_text}%"))

            if search_criteria:
                from sqlalchemy import or_

                total_query = total_query.filter(or_(*search_criteria))

            # Apply additional filters for count
            for field, value in filters.items():
                if hasattr(self.model_class, field):
                    total_query = total_query.filter(
                        getattr(self.model_class, field) == value
                    )

            total = total_query.count()

            # Build pagination response
            if self.pagination_builder:
                return self.pagination_builder.build_response(
                    items=items, total=total, skip=skip, limit=limit
                )
            else:
                return {"items": items, "total": total, "skip": skip, "limit": limit}

        except Exception as e:
            return self._handle_exception(
                e,
                "search_paginated",
                {"items": [], "total": 0, "skip": skip, "limit": limit},
            )
