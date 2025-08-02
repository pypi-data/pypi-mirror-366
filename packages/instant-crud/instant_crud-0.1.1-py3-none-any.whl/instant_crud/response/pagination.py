"""
Pagination response builder for different response formats.
Supports offset-based, page-based, cursor-based, and custom formats.
"""

import math
from typing import Any, Dict, List, Optional, TypeVar

from jinja2 import Template

T = TypeVar("T")


class PaginationResponseBuilder:
    """
    Builder for pagination responses supporting multiple formats.

    Supports:
    - offset_based: {items, total, skip, limit}
    - page_based: {data, pagination: {current_page, per_page, total_pages, ...}}
    - cursor_based: {results, meta: {count, next, previous}}
    - custom: User-defined template
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize pagination builder.

        Args:
            config: Configuration dictionary with format definitions
        """
        self.config = config
        self.format_type = config.get("response_format", "offset_based")
        self.formats = config.get("formats", {})

        # Validate configuration
        self._validate_config()

    def _validate_config(self) -> None:
        """Validate pagination configuration."""
        if self.format_type not in [
            "offset_based",
            "page_based",
            "cursor_based",
            "custom",
        ]:
            raise ValueError(f"Unsupported pagination format: {self.format_type}")

        if self.format_type != "custom" and self.format_type not in self.formats:
            raise ValueError(f"Configuration missing for format: {self.format_type}")

    def build_response(
        self,
        items: List[T],
        total: int,
        skip: int = 0,
        limit: int = 100,
        cursor_next: Optional[str] = None,
        cursor_prev: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Build pagination response based on configured format.

        Args:
            items: List of items for current page
            total: Total number of items
            skip: Number of items skipped (offset)
            limit: Number of items per page
            cursor_next: Next cursor for cursor-based pagination
            cursor_prev: Previous cursor for cursor-based pagination

        Returns:
            Formatted pagination response
        """
        if self.format_type == "offset_based":
            return self._build_offset_response(items, total, skip, limit)
        elif self.format_type == "page_based":
            return self._build_page_response(items, total, skip, limit)
        elif self.format_type == "cursor_based":
            return self._build_cursor_response(items, total, cursor_next, cursor_prev)
        elif self.format_type == "custom":
            return self._build_custom_response(
                items, total, skip, limit, cursor_next, cursor_prev
            )
        else:
            raise ValueError(f"Unknown format type: {self.format_type}")

    def _build_offset_response(
        self, items: List[T], total: int, skip: int, limit: int
    ) -> Dict[str, Any]:
        """Build offset-based pagination response."""
        config = self.formats["offset_based"]

        return {
            config["items_key"]: items,
            config["total_key"]: total,
            config["skip_key"]: skip,
            config["limit_key"]: limit,
        }

    def _build_page_response(
        self, items: List[T], total: int, skip: int, limit: int
    ) -> Dict[str, Any]:
        """Build page-based pagination response."""
        config = self.formats["page_based"]

        # Calculate page information
        current_page = (skip // limit) + 1 if limit > 0 else 1
        total_pages = math.ceil(total / limit) if limit > 0 else 1
        has_next = current_page < total_pages
        has_prev = current_page > 1

        response: Dict[str, Any] = {config["items_key"]: items}

        pagination_data: Dict[str, Any] = {
            config["current_page_key"]: current_page,
            config["per_page_key"]: limit,
            config["total_pages_key"]: total_pages,
            config["total_count_key"]: total,
            config["has_next_key"]: has_next,
            config["has_prev_key"]: has_prev,
        }

        # Add wrapper key if specified
        if "wrapper_key" in config:
            response[config["wrapper_key"]] = pagination_data
        else:
            response.update(pagination_data)

        return response

    def _build_cursor_response(
        self,
        items: List[T],
        total: int,
        cursor_next: Optional[str] = None,
        cursor_prev: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Build cursor-based pagination response."""
        config = self.formats["cursor_based"]

        response: Dict[str, Any] = {config["items_key"]: items}

        meta_data: Dict[str, Any] = {
            config["count_key"]: total,
        }

        # Add cursors if provided
        if cursor_next:
            meta_data[config["next_key"]] = cursor_next
        if cursor_prev:
            meta_data[config["previous_key"]] = cursor_prev

        # Add wrapper key if specified
        if "wrapper_key" in config:
            response[config["wrapper_key"]] = meta_data
        else:
            response.update(meta_data)

        return response

    def _build_custom_response(
        self,
        items: List[T],
        total: int,
        skip: int,
        limit: int,
        cursor_next: Optional[str] = None,
        cursor_prev: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Build custom pagination response using Jinja2 template."""
        if "template" not in self.formats.get("custom", {}):
            raise ValueError("Custom format requires 'template' configuration")

        template_config = self.formats["custom"]["template"]

        # Calculate page information for template variables
        current_page = (skip // limit) + 1 if limit > 0 else 1
        total_pages = math.ceil(total / limit) if limit > 0 else 1
        has_next = current_page < total_pages
        has_prev = current_page > 1

        # Template variables
        template_vars = {
            "items": items,
            "total": total,
            "skip": skip,
            "limit": limit,
            "current_page": current_page,
            "per_page": limit,
            "total_pages": total_pages,
            "has_next": has_next,
            "has_prev": has_prev,
            "cursor_next": cursor_next,
            "cursor_prev": cursor_prev,
        }

        # Process template
        return self._process_template(template_config, template_vars)

    def _process_template(self, template_obj: Any, variables: Dict[str, Any]) -> Any:
        """
        Process template object recursively.

        Args:
            template_obj: Template object (dict, list, string, or other)
            variables: Variables for template substitution

        Returns:
            Processed template result
        """
        if isinstance(template_obj, dict):
            result: Dict[str, Any] = {}
            for key, value in template_obj.items():
                # Process key (in case it's a template)
                processed_key = self._process_template_value(key, variables)
                # Process value recursively
                result[processed_key] = self._process_template(value, variables)
            return result
        elif isinstance(template_obj, list):
            return [self._process_template(item, variables) for item in template_obj]
        else:
            return self._process_template_value(template_obj, variables)

    def _process_template_value(self, value: Any, variables: Dict[str, Any]) -> Any:
        """
        Process individual template value.

        Args:
            value: Value to process
            variables: Template variables

        Returns:
            Processed value
        """
        if isinstance(value, str) and "{{" in value and "}}" in value:
            try:
                template = Template(value)
                result = template.render(**variables)

                # Try to convert back to original type if possible
                if value.strip() == f"{{{{{result.strip()}}}}}":
                    # Direct variable substitution, return actual value
                    return variables.get(result.strip(), result)

                return result
            except Exception:
                # If template processing fails, return original value
                return value

        return value

    def get_page_info(
        self, total: int, skip: int = 0, limit: int = 100
    ) -> Dict[str, Any]:
        """
        Get page information without building full response.

        Args:
            total: Total number of items
            skip: Number of items skipped
            limit: Number of items per page

        Returns:
            Dictionary with page information
        """
        current_page = (skip // limit) + 1 if limit > 0 else 1
        total_pages = math.ceil(total / limit) if limit > 0 else 1

        return {
            "current_page": current_page,
            "per_page": limit,
            "total_pages": total_pages,
            "total_count": total,
            "has_next": current_page < total_pages,
            "has_prev": current_page > 1,
            "skip": skip,
            "limit": limit,
        }


def create_pagination_builder(
    config: Optional[Dict[str, Any]] = None,
) -> PaginationResponseBuilder:
    """
    Create pagination builder with default or custom configuration.

    Args:
        config: Optional custom configuration

    Returns:
        PaginationResponseBuilder instance
    """
    if config is None:
        # Default offset-based configuration
        config = {
            "response_format": "offset_based",
            "formats": {
                "offset_based": {
                    "items_key": "items",
                    "total_key": "total",
                    "skip_key": "skip",
                    "limit_key": "limit",
                }
            },
        }

    return PaginationResponseBuilder(config)
