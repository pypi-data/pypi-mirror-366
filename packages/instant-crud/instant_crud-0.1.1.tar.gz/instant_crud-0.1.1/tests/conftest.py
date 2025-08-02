"""
Pytest configuration and fixtures for instant-crud tests.
"""

import pytest
from typing import Generator, Optional
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine, Field
from sqlalchemy.pool import StaticPool

from instant_crud import CRUDFactory, auto_crud_api, get_settings, reset_settings


# Test database setup
DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


def get_session() -> Session:
    """Get database session for testing."""
    return Session(engine)


@pytest.fixture
def session() -> Generator[Session, None, None]:
    """Database session fixture."""
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)


# Mock authentication functions
def get_current_user():
    """Mock current user for testing."""
    return {"id": 1, "username": "testuser"}


def get_user_with_roles():
    """Mock user with roles for testing."""
    return {"id": 1, "username": "testuser", "roles": ["admin"]}


@pytest.fixture
def crud_factory() -> CRUDFactory:
    """CRUD factory fixture."""
    # Reset settings before each test
    reset_settings()
    
    return CRUDFactory(
        get_session=get_session,
        get_current_user=get_current_user,
        get_user_with_roles=get_user_with_roles,
    )


# Test models
class User(SQLModel, table=True):
    """Test user model."""
    id: Optional[int] = Field(primary_key=True)
    name: str
    email: str
    age: Optional[int] = None
    is_active: bool = True


@auto_crud_api(prefix="/users", tags=["Users"])
class AutoUser(SQLModel, table=True):
    """Test user model with auto CRUD API."""
    __tablename__ = "auto_users"
    
    id: Optional[int] = Field(primary_key=True)
    name: str
    email: str
    age: Optional[int] = None
    is_active: bool = True


class Product(SQLModel, table=True):
    """Test product model."""
    id: Optional[int] = Field(primary_key=True)
    name: str
    description: Optional[str] = None
    price: float
    in_stock: bool = True


@pytest.fixture
def test_models():
    """Fixture with test models."""
    return {
        "User": User,
        "AutoUser": AutoUser,
        "Product": Product,
    }


@pytest.fixture
def app(crud_factory: CRUDFactory) -> FastAPI:
    """FastAPI app fixture."""
    app = FastAPI(title="Test API", version="1.0.0")
    
    # Create routers manually
    user_router = crud_factory.create_crud_router(
        model=User,
        prefix="/users",
        tags=["Users"],
        search_fields=["name", "email"]
    )
    
    product_router = crud_factory.create_crud_router(
        model=Product,
        prefix="/products",
        tags=["Products"],
        search_fields=["name", "description"]
    )
    
    # Include routers
    app.include_router(user_router)
    app.include_router(product_router)
    
    # Create routers for auto-registered models
    auto_routers = crud_factory.create_routers_for_registered_models()
    for router in auto_routers:
        app.include_router(router)
    
    return app


@pytest.fixture
def client(app: FastAPI, session: Session) -> TestClient:
    """Test client fixture."""
    # Create tables
    SQLModel.metadata.create_all(engine)
    
    # Override get_session dependency
    def override_get_session():
        return session
    
    app.dependency_overrides[get_session] = override_get_session
    
    return TestClient(app)


@pytest.fixture
def sample_users(session: Session) -> list[User]:
    """Create sample users for testing."""
    users = [
        User(name="John Doe", email="john@example.com", age=30),
        User(name="Jane Smith", email="jane@example.com", age=25),
        User(name="Bob Johnson", email="bob@example.com", age=35, is_active=False),
    ]
    
    for user in users:
        session.add(user)
    session.commit()
    
    for user in users:
        session.refresh(user)
    
    return users


@pytest.fixture
def sample_products(session: Session) -> list[Product]:
    """Create sample products for testing."""
    products = [
        Product(name="Laptop", description="High-performance laptop", price=999.99),
        Product(name="Mouse", description="Wireless mouse", price=29.99),
        Product(name="Keyboard", description="Mechanical keyboard", price=79.99, in_stock=False),
    ]
    
    for product in products:
        session.add(product)
    session.commit()
    
    for product in products:
        session.refresh(product)
    
    return products


@pytest.fixture(autouse=True)
def cleanup():
    """Cleanup after each test."""
    yield
    # Reset global state
    reset_settings()
    from instant_crud.core.factory import reset_default_factory
    reset_default_factory()


# Test data factories
def create_user_data(**kwargs):
    """Create user data for testing."""
    default_data = {
        "name": "Test User",
        "email": "test@example.com",
        "age": 25,
        "is_active": True,
    }
    default_data.update(kwargs)
    return default_data


def create_product_data(**kwargs):
    """Create product data for testing."""
    default_data = {
        "name": "Test Product",
        "description": "A test product",
        "price": 99.99,
        "in_stock": True,
    }
    default_data.update(kwargs)
    return default_data


# Configuration fixtures
@pytest.fixture
def pagination_config():
    """Sample pagination configuration."""
    return {
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
                "has_prev_key": "has_prev"
            }
        }
    }


@pytest.fixture
def custom_pagination_config():
    """Custom pagination configuration."""
    return {
        "response_format": "custom",
        "formats": {
            "custom": {
                "template": {
                    "results": "{{items}}",
                    "meta": {
                        "count": "{{total}}",
                        "page": "{{current_page}}",
                        "size": "{{per_page}}"
                    }
                }
            }
        }
    }


# Parametrized fixtures for different configurations
@pytest.fixture(params=["offset_based", "page_based"])
def pagination_format(request):
    """Parametrized pagination format fixture."""
    return request.param