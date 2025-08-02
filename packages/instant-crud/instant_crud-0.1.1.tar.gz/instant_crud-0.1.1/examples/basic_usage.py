"""
Basic usage example for instant-crud library.

This example shows how to:
1. Define SQLModel classes
2. Use @auto_crud_api decorator
3. Create a FastAPI app with automatic CRUD endpoints
4. Test the generated API
"""

import os
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlmodel import Field, Session, SQLModel, create_engine

from instant_crud.core.factory import CRUDFactory

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


# Now import instant_crud
try:
    from instant_crud import auto_crud_api
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running from the project root and the package is installed")
    sys.exit(1)

# Database setup (SQLite for simplicity)
DATABASE_URL = "sqlite:///./example.db"
engine = create_engine(DATABASE_URL, echo=True)


def get_session():
    """Get database session."""
    return Session(engine)


# Define models with auto CRUD API
@auto_crud_api(prefix="/users", tags=["Users"])
class User(
    SQLModel,
    table=True,
):
    """User model with automatic CRUD API."""

    __table_args__ = {"extend_existing": True}
    id: int | None = Field(primary_key=True)
    name: str = Field(description="User's full name")
    email: str = Field(unique=True, description="User's email address")
    age: int | None = Field(default=None, ge=0, le=150, description="User's age")
    is_active: bool = Field(default=True, description="Whether user is active")


@auto_crud_api(prefix="/products", tags=["Products"])
class Product(SQLModel, table=True):
    """Product model with automatic CRUD API."""

    __table_args__ = {"extend_existing": True}
    id: int | None = Field(primary_key=True)
    name: str = Field(description="Product name")
    description: str | None = Field(default=None, description="Product description")
    price: float = Field(gt=0, description="Product price")
    in_stock: bool = Field(default=True, description="Whether product is in stock")
    category: str | None = Field(default=None, description="Product category")


@auto_crud_api(prefix="/categories", tags=["Categories"], read_only=True)
class Category(SQLModel, table=True):
    """Category model with read-only CRUD API."""

    __table_args__ = {"extend_existing": True}
    id: int | None = Field(primary_key=True)
    name: str = Field(unique=True, description="Category name")
    description: str | None = Field(default=None, description="Category description")


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Create database tables on startup."""
    SQLModel.metadata.create_all(engine)

    # Add some sample data
    with Session(engine) as session:
        # Check if data already exists
        existing_users = session.query(User).first()
        if not existing_users:
            # Add sample users
            sample_users = [
                User(id=1, name="John Doe", email="john@example.com", age=30),
                User(id=2, name="Jane Smith", email="jane@example.com", age=25),
                User(
                    id=3,
                    name="Bob Johnson",
                    email="bob@example.com",
                    age=35,
                    is_active=False,
                ),
            ]

            # Add sample products
            sample_products = [
                Product(
                    id=1,
                    name="Laptop",
                    description="High-performance laptop",
                    price=999.99,
                    category="Electronics",
                ),
                Product(
                    id=2,
                    name="Mouse",
                    description="Wireless mouse",
                    price=29.99,
                    category="Electronics",
                ),
                Product(
                    id=3,
                    name="Coffee Mug",
                    description="Ceramic coffee mug",
                    price=9.99,
                    category="Kitchen",
                ),
                Product(
                    id=4,
                    name="Book",
                    description="Programming book",
                    price=39.99,
                    in_stock=False,
                    category="Books",
                ),
            ]

            # Add sample categories
            sample_categories = [
                Category(
                    id=1,
                    name="Electronics",
                    description="Electronic devices and accessories",
                ),
                Category(
                    id=2, name="Kitchen", description="Kitchen items and appliances"
                ),
                Category(
                    id=3, name="Books", description="Books and educational materials"
                ),
            ]

            for item in sample_users + sample_products + sample_categories:
                session.add(item)

            session.commit()
            print("✅ Sample data created!")

    yield

    print("🔽 Application shutdown")


# Create FastAPI app
app = FastAPI(
    title="Instant CRUD Example API",
    version="1.0.0",
    description="Example API built with instant-crud library",
    lifespan=lifespan,
)


# Setup instant-crud with configuration
factory = CRUDFactory(
    get_session=get_session,
    # No auth for this simple example
    get_current_user=None,
    get_user_with_roles=None,
)

# Create routers for all models decorated with @auto_crud_api
routers = factory.create_routers_for_registered_models()

# Include all routers in the app
for router in routers:
    app.include_router(router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Welcome to Instant CRUD Example API!",
        "version": "1.0.0",
        "endpoints": {
            "users": "/api/v1/users",
            "products": "/api/v1/products",
            "categories": "/api/v1/categories (read-only)",
            "docs": "/docs",
            "openapi": "/openapi.json",
        },
        "features": [
            "Automatic CRUD operations",
            "Built-in pagination",
            "Search functionality",
            "Batch operations",
            "OpenAPI documentation",
        ],
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "instant-crud-example"}


if __name__ == "__main__":
    import uvicorn

    print("🚀 Starting Instant CRUD Example API...")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("🔍 OpenAPI Schema: http://localhost:8000/openapi.json")
    print("\n🎯 Available endpoints:")
    print("  - GET  /api/v1/users         - List users")
    print("  - POST /api/v1/users         - Create user")
    print("  - GET  /api/v1/users/{id}    - Get user by ID")
    print("  - PUT  /api/v1/users/{id}    - Update user")
    print("  - DELETE /api/v1/users/{id}  - Delete user")
    print("  - GET  /api/v1/users/search  - Search users")
    print("  - GET  /api/v1/users/count   - Count users")
    print("\n  📦 Same endpoints available for /products")
    print("  📚 Read-only endpoints for /categories")
    print("\n🧪 Test commands:")
    print("  curl http://localhost:8000/api/v1/users")
    print(
        '  curl -X POST http://localhost:8000/api/v1/users -H \'Content-Type: application/json\' -d \'{"name":"Test User","email":"test@example.com"}\''
    )
    print("  curl http://localhost:8000/api/v1/users/search?q=John")

    uvicorn.run(
        "basic_usage:app", host="0.0.0.0", port=8000, reload=True, log_level="info"
    )
