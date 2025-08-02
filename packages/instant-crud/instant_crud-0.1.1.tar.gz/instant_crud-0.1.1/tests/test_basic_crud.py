"""
Basic CRUD operation tests for instant-crud.
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from .conftest import User, Product, create_user_data, create_product_data


class TestBasicCRUD:
    """Test basic CRUD operations."""
    
    def test_create_user(self, client: TestClient):
        """Test creating a new user."""
        user_data = create_user_data()
        
        response = client.post("/users/", json=user_data)
        
        assert response.status_code == 201
        result = response.json()
        assert result["name"] == user_data["name"]
        assert result["email"] == user_data["email"]
        assert result["age"] == user_data["age"]
        assert "id" in result
        assert result["id"] is not None
    
    def test_create_user_invalid_data(self, client: TestClient):
        """Test creating user with invalid data."""
        invalid_data = {"name": "Test User"}  # Missing required email
        
        response = client.post("/users/", json=invalid_data)
        
        assert response.status_code == 422  # Validation error
    
    def test_get_user_by_id(self, client: TestClient, sample_users: list[User]):
        """Test getting a user by ID."""
        user = sample_users[0]
        
        response = client.get(f"/users/{user.id}")
        
        assert response.status_code == 200
        result = response.json()
        assert result["id"] == user.id
        assert result["name"] == user.name
        assert result["email"] == user.email
    
    def test_get_user_not_found(self, client: TestClient):
        """Test getting non-existent user."""
        response = client.get("/users/999")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_get_all_users(self, client: TestClient, sample_users: list[User]):
        """Test getting all users with pagination."""
        response = client.get("/users/")
        
        assert response.status_code == 200
        result = response.json()
        
        # Check pagination structure
        assert "items" in result
        assert "total" in result
        assert "skip" in result
        assert "limit" in result
        
        # Check data
        assert result["total"] == len(sample_users)
        assert len(result["items"]) == len(sample_users)
        
        # Check first user
        first_user = result["items"][0]
        assert "id" in first_user
        assert "name" in first_user
        assert "email" in first_user
    
    def test_get_all_users_with_pagination(self, client: TestClient, sample_users: list[User]):
        """Test pagination parameters."""
        # Test with limit
        response = client.get("/users/?skip=0&limit=2")
        
        assert response.status_code == 200
        result = response.json()
        assert len(result["items"]) == 2
        assert result["skip"] == 0
        assert result["limit"] == 2
        assert result["total"] == len(sample_users)
        
        # Test with skip
        response = client.get("/users/?skip=1&limit=2")
        
        assert response.status_code == 200
        result = response.json()
        assert len(result["items"]) == 2
        assert result["skip"] == 1
        assert result["limit"] == 2
    
    def test_update_user(self, client: TestClient, sample_users: list[User]):
        """Test updating a user."""
        user = sample_users[0]
        update_data = create_user_data(name="Updated Name", age=99)
        
        response = client.put(f"/users/{user.id}", json=update_data)
        
        assert response.status_code == 200
        result = response.json()
        assert result["id"] == user.id
        assert result["name"] == "Updated Name"
        assert result["age"] == 99
        assert result["email"] == update_data["email"]
    
    def test_update_user_not_found(self, client: TestClient):
        """Test updating non-existent user."""
        update_data = create_user_data()
        
        response = client.put("/users/999", json=update_data)
        
        assert response.status_code == 404
    
    def test_patch_user(self, client: TestClient, sample_users: list[User]):
        """Test partially updating a user."""
        user = sample_users[0]
        patch_data = {"name": "Patched Name"}
        
        response = client.patch(f"/users/{user.id}", json=patch_data)
        
        assert response.status_code == 200
        result = response.json()
        assert result["id"] == user.id
        assert result["name"] == "Patched Name"
        assert result["email"] == user.email  # Should remain unchanged
    
    def test_delete_user(self, client: TestClient, sample_users: list[User]):
        """Test deleting a user."""
        user = sample_users[0]
        
        response = client.delete(f"/users/{user.id}")
        
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        
        # Verify user is deleted
        response = client.get(f"/users/{user.id}")
        assert response.status_code == 404
    
    def test_delete_user_not_found(self, client: TestClient):
        """Test deleting non-existent user."""
        response = client.delete("/users/999")
        
        assert response.status_code == 404
    
    def test_count_users(self, client: TestClient, sample_users: list[User]):
        """Test counting users."""
        response = client.get("/users/count")
        
        assert response.status_code == 200
        count = response.json()
        assert count == len(sample_users)
    
    def test_count_users_empty(self, client: TestClient):
        """Test counting users when none exist."""
        response = client.get("/users/count")
        
        assert response.status_code == 200
        count = response.json()
        assert count == 0


class TestBatchOperations:
    """Test batch CRUD operations."""
    
    def test_create_multiple_users(self, client: TestClient):
        """Test creating multiple users."""
        users_data = [
            create_user_data(name="User 1", email="user1@example.com"),
            create_user_data(name="User 2", email="user2@example.com"),
            create_user_data(name="User 3", email="user3@example.com"),
        ]
        
        response = client.post("/users/batch", json=users_data)
        
        assert response.status_code == 201
        result = response.json()
        assert len(result) == 3
        
        for i, user in enumerate(result):
            assert user["name"] == users_data[i]["name"]
            assert user["email"] == users_data[i]["email"]
            assert "id" in user
    
    def test_delete_multiple_users(self, client: TestClient, sample_users: list[User]):
        """Test deleting multiple users."""
        user_ids = [user.id for user in sample_users[:2]]
        
        response = client.delete("/users/batch", json=user_ids)
        
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        assert result["deleted_count"] == 2
        assert len(result["not_found"]) == 0
        
        # Verify users are deleted
        for user_id in user_ids:
            response = client.get(f"/users/{user_id}")
            assert response.status_code == 404
    
    def test_delete_multiple_users_partial(self, client: TestClient, sample_users: list[User]):
        """Test deleting multiple users with some not found."""
        user_ids = [sample_users[0].id, 999, sample_users[1].id, 888]
        
        response = client.delete("/users/batch", json=user_ids)
        
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        assert result["deleted_count"] == 2
        assert set(result["not_found"]) == {999, 888}


class TestSearchOperations:
    """Test search operations."""
    
    def test_search_users_by_name(self, client: TestClient, sample_users: list[User]):
        """Test searching users by name."""
        response = client.get("/users/search?q=John")
        
        assert response.status_code == 200
        result = response.json()
        
        assert "items" in result
        assert "total" in result
        assert result["total"] > 0
        
        # Should find John Doe
        found_user = next((user for user in result["items"] if "John" in user["name"]), None)
        assert found_user is not None
    
    def test_search_users_by_email(self, client: TestClient, sample_users: list[User]):
        """Test searching users by email."""
        response = client.get("/users/search?q=jane@example.com")
        
        assert response.status_code == 200
        result = response.json()
        
        assert result["total"] > 0
        found_user = next((user for user in result["items"] if "jane@example.com" in user["email"]), None)
        assert found_user is not None
    
    def test_search_users_no_results(self, client: TestClient, sample_users: list[User]):
        """Test searching with no results."""
        response = client.get("/users/search?q=nonexistent")
        
        assert response.status_code == 200
        result = response.json()
        
        assert result["total"] == 0
        assert len(result["items"]) == 0
    
    def test_search_empty_query(self, client: TestClient):
        """Test searching with empty query."""
        response = client.get("/users/search?q=")
        
        assert response.status_code == 200
        result = response.json()
        
        assert result["total"] == 0
        assert len(result["items"]) == 0


class TestProductCRUD:
    """Test CRUD operations on Product model to verify multi-model support."""
    
    def test_create_product(self, client: TestClient):
        """Test creating a product."""
        product_data = create_product_data()
        
        response = client.post("/products/", json=product_data)
        
        assert response.status_code == 201
        result = response.json()
        assert result["name"] == product_data["name"]
        assert result["price"] == product_data["price"]
        assert "id" in result
    
    def test_get_all_products(self, client: TestClient, sample_products: list[Product]):
        """Test getting all products."""
        response = client.get("/products/")
        
        assert response.status_code == 200
        result = response.json()
        
        assert result["total"] == len(sample_products)
        assert len(result["items"]) == len(sample_products)
    
    def test_search_products(self, client: TestClient, sample_products: list[Product]):
        """Test searching products."""
        response = client.get("/products/search?q=Laptop")
        
        assert response.status_code == 200
        result = response.json()
        
        assert result["total"] > 0
        found_product = next((product for product in result["items"] if "Laptop" in product["name"]), None)
        assert found_product is not None