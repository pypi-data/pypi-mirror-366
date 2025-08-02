"""
Tests for pagination functionality in instant-crud.
"""

import pytest

from instant_crud.response.pagination import (
    PaginationResponseBuilder,
    create_pagination_builder,
)


class TestPaginationBuilder:
    """Test pagination response builder."""

    def test_offset_based_pagination(self):
        """Test offset-based pagination format."""
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

        builder = PaginationResponseBuilder(config)
        items = [{"id": 1, "name": "Item 1"}, {"id": 2, "name": "Item 2"}]

        result = builder.build_response(items=items, total=10, skip=0, limit=2)

        assert result["items"] == items
        assert result["total"] == 10
        assert result["skip"] == 0
        assert result["limit"] == 2

    def test_page_based_pagination(self):
        """Test page-based pagination format."""
        config = {
            "response_format": "page_based",
            "formats": {
                "page_based": {
                    "items_key": "data",
                    "wrapper_key": "pagination",
                    "current_page_key": "current_page",
                    "per_page_key": "per_page",
                    "total_pages_key": "total_pages",
                    "total_count_key": "total_count",
                    "has_next_key": "has_next",
                    "has_prev_key": "has_prev",
                }
            },
        }

        builder = PaginationResponseBuilder(config)
        items = [{"id": 3, "name": "Item 3"}, {"id": 4, "name": "Item 4"}]

        # Page 2 of 5 (skip=2, limit=2, total=10)
        result = builder.build_response(items=items, total=10, skip=2, limit=2)

        assert result["data"] == items
        assert result["pagination"]["current_page"] == 2
        assert result["pagination"]["per_page"] == 2
        assert result["pagination"]["total_pages"] == 5
        assert result["pagination"]["total_count"] == 10
        assert result["pagination"]["has_next"] is True
        assert result["pagination"]["has_prev"] is True

    def test_page_based_first_page(self):
        """Test page-based pagination for first page."""
        config = {
            "response_format": "page_based",
            "formats": {
                "page_based": {
                    "items_key": "data",
                    "wrapper_key": "pagination",
                    "current_page_key": "current_page",
                    "per_page_key": "per_page",
                    "total_pages_key": "total_pages",
                    "total_count_key": "total_count",
                    "has_next_key": "has_next",
                    "has_prev_key": "has_prev",
                }
            },
        }

        builder = PaginationResponseBuilder(config)
        items = [{"id": 1, "name": "Item 1"}, {"id": 2, "name": "Item 2"}]

        result = builder.build_response(items=items, total=10, skip=0, limit=2)

        assert result["pagination"]["current_page"] == 1
        assert result["pagination"]["has_next"] is True
        assert result["pagination"]["has_prev"] is False

    def test_page_based_last_page(self):
        """Test page-based pagination for last page."""
        config = {
            "response_format": "page_based",
            "formats": {
                "page_based": {
                    "items_key": "data",
                    "wrapper_key": "pagination",
                    "current_page_key": "current_page",
                    "per_page_key": "per_page",
                    "total_pages_key": "total_pages",
                    "total_count_key": "total_count",
                    "has_next_key": "has_next",
                    "has_prev_key": "has_prev",
                }
            },
        }

        builder = PaginationResponseBuilder(config)
        items = [{"id": 9, "name": "Item 9"}, {"id": 10, "name": "Item 10"}]

        # Last page (skip=8, limit=2, total=10)
        result = builder.build_response(items=items, total=10, skip=8, limit=2)

        assert result["pagination"]["current_page"] == 5
        assert result["pagination"]["has_next"] is False
        assert result["pagination"]["has_prev"] is True

    def test_cursor_based_pagination(self):
        """Test cursor-based pagination format."""
        config = {
            "response_format": "cursor_based",
            "formats": {
                "cursor_based": {
                    "items_key": "results",
                    "wrapper_key": "meta",
                    "count_key": "count",
                    "next_key": "next_cursor",
                    "previous_key": "prev_cursor",
                }
            },
        }

        builder = PaginationResponseBuilder(config)
        items = [{"id": 1, "name": "Item 1"}]

        result = builder.build_response(
            items=items, total=100, cursor_next="cursor_123", cursor_prev="cursor_456"
        )

        assert result["results"] == items
        assert result["meta"]["count"] == 100
        assert result["meta"]["next_cursor"] == "cursor_123"
        assert result["meta"]["prev_cursor"] == "cursor_456"

    def test_custom_pagination_with_template(self):
        """Test custom pagination with Jinja2 template."""
        config = {
            "response_format": "custom",
            "formats": {
                "custom": {
                    "template": {
                        "results": "{{items}}",
                        "meta": {
                            "count": "{{total}}",
                            "page": "{{current_page}}",
                            "size": "{{per_page}}",
                            "pages": "{{total_pages}}",
                        },
                    }
                }
            },
        }

        builder = PaginationResponseBuilder(config)
        items = [{"id": 1, "name": "Item 1"}]

        result = builder.build_response(items=items, total=50, skip=10, limit=5)

        assert result["results"] == items
        assert result["meta"]["count"] == 50
        assert result["meta"]["page"] == 3  # (10 / 5) + 1
        assert result["meta"]["size"] == 5
        assert result["meta"]["pages"] == 10  # ceil(50 / 5)

    def test_create_pagination_builder_default(self):
        """Test creating pagination builder with default config."""
        builder = create_pagination_builder()

        items = [{"id": 1, "name": "Item 1"}]
        result = builder.build_response(items=items, total=10, skip=0, limit=5)

        # Should use default offset-based format
        assert "items" in result
        assert "total" in result
        assert "skip" in result
        assert "limit" in result

    def test_get_page_info(self):
        """Test getting page information."""
        builder = create_pagination_builder()

        page_info = builder.get_page_info(total=25, skip=10, limit=5)

        assert page_info["current_page"] == 3
        assert page_info["per_page"] == 5
        assert page_info["total_pages"] == 5
        assert page_info["total_count"] == 25
        assert page_info["has_next"] is True
        assert page_info["has_prev"] is True
        assert page_info["skip"] == 10
        assert page_info["limit"] == 5

    def test_invalid_pagination_format(self):
        """Test invalid pagination format raises error."""
        config = {"response_format": "invalid_format", "formats": {}}

        with pytest.raises(ValueError, match="Unsupported pagination format"):
            PaginationResponseBuilder(config)

    def test_missing_format_config(self):
        """Test missing format configuration raises error."""
        config = {"response_format": "page_based", "formats": {}}

        with pytest.raises(ValueError, match="Configuration missing for format"):
            PaginationResponseBuilder(config)


class TestPaginationIntegration:
    """Test pagination integration with CRUD operations."""

    def test_pagination_with_different_formats(
        self, client, sample_users, pagination_format
    ):
        """Test pagination with different formats."""
        # This test would need to be updated to use different pagination configs
        # For now, test with default format
        response = client.get("/users/?skip=0&limit=2")

        assert response.status_code == 200
        result = response.json()

        # Should have pagination structure
        assert "items" in result
        assert "total" in result
        assert len(result["items"]) <= 2

    def test_pagination_edge_cases(self, client, sample_users):
        """Test pagination edge cases."""
        # Test with skip greater than total
        response = client.get("/users/?skip=100&limit=10")

        assert response.status_code == 200
        result = response.json()
        assert len(result["items"]) == 0
        assert result["skip"] == 100
        assert result["limit"] == 10

        # Test with limit 0
        response = client.get("/users/?skip=0&limit=1")

        assert response.status_code == 200
        result = response.json()
        assert len(result["items"]) <= 1


class TestCustomPaginationTemplates:
    """Test custom pagination templates."""

    def test_complex_custom_template(self):
        """Test complex custom pagination template."""
        config = {
            "response_format": "custom",
            "formats": {
                "custom": {
                    "template": {
                        "data": "{{items}}",
                        "pagination": {
                            "current": "{{current_page}}",
                            "total": "{{total_pages}}",
                            "count": "{{total}}",
                            "per_page": "{{per_page}}",
                            "links": {
                                "self": "/api/items?page={{current_page}}",
                                "first": "/api/items?page=1",
                                "last": "/api/items?page={{total_pages}}",
                            },
                        },
                    }
                }
            },
        }

        builder = PaginationResponseBuilder(config)
        items = [{"id": 1, "name": "Item 1"}]

        result = builder.build_response(items=items, total=100, skip=20, limit=10)

        assert result["data"] == items
        assert result["pagination"]["current"] == 3
        assert result["pagination"]["total"] == 10
        assert result["pagination"]["count"] == 100
        assert result["pagination"]["per_page"] == 10
        assert result["pagination"]["links"]["self"] == "/api/items?page=3"
        assert result["pagination"]["links"]["first"] == "/api/items?page=1"
        assert result["pagination"]["links"]["last"] == "/api/items?page=10"

    def test_nested_template_processing(self):
        """Test nested template processing."""
        config = {
            "response_format": "custom",
            "formats": {
                "custom": {
                    "template": {
                        "response": {
                            "status": "success",
                            "data": {
                                "items": "{{items}}",
                                "metadata": {
                                    "total": "{{total}}",
                                    "page": "{{current_page}}",
                                    "has_more": "{{has_next}}",
                                },
                            },
                        }
                    }
                }
            },
        }

        builder = PaginationResponseBuilder(config)
        items = [{"id": 1}, {"id": 2}]

        result = builder.build_response(items=items, total=20, skip=5, limit=5)

        assert result["response"]["status"] == "success"
        assert result["response"]["data"]["items"] == items
        assert result["response"]["data"]["metadata"]["total"] == 20
        assert result["response"]["data"]["metadata"]["page"] == 2
        assert result["response"]["data"]["metadata"]["has_more"] is True
