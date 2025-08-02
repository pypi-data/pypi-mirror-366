"""
Advanced usage example for instant-crud library.

This example shows:
1. Custom pagination configuration
2. Manual router creation with factory
3. Authentication integration
4. Custom search fields
5. Export functionality
6. Different response formats
"""

import json
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Field, Session, SQLModel, create_engine

from instant_crud import CRUDFactory, InstantCRUDSettings, crud_config

# Database setup
DATABASE_URL = "sqlite:///./advanced_example.db"
engine = create_engine(DATABASE_URL, echo=True)


def get_session():
    """Get database session."""
    with Session(engine) as session:
        yield session


# Authentication setup (simplified for example)
security = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Mock authentication - in real app, validate JWT token."""
    # For demo purposes, accept any token
    if credentials.credentials == "test-token":
        return {"id": 1, "username": "testuser", "email": "test@example.com"}

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_user_with_roles(current_user=Depends(get_current_user)):
    """Get user with roles for admin operations."""
    # Add roles to user (mock implementation)
    current_user["roles"] = ["admin", "user"]
    return current_user


# Models with custom configuration
@crud_config(
    search_fields=["title", "content", "author"], export_enabled=True, auth_enabled=True
)
class Article(SQLModel, table=True):
    """Article model with custom CRUD configuration."""

    __table_args__ = {"extend_existing": True}
    id: Optional[int] = Field(primary_key=True)
    title: str = Field(description="Article title")
    content: str = Field(description="Article content")
    author: str = Field(description="Article author")
    published: bool = Field(default=False, description="Whether article is published")
    views: int = Field(default=0, description="Number of views")
    tags: Optional[str] = Field(default=None, description="Article tags (JSON)")


class Comment(SQLModel, table=True):
    """Comment model."""

    __table_args__ = {"extend_existing": True}
    id: Optional[int] = Field(primary_key=True)
    article_id: int = Field(foreign_key="article.id", description="Related article ID")
    author: str = Field(description="Comment author")
    content: str = Field(description="Comment content")
    approved: bool = Field(default=False, description="Whether comment is approved")


class Author(SQLModel, table=True):
    """Author model with read-only API."""

    __table_args__ = {"extend_existing": True}
    id: int | None = Field(primary_key=True)
    name: str = Field(description="Author name")
    email: str = Field(unique=True, description="Author email")
    bio: str | None = Field(default=None, description="Author biography")
    article_count: int = Field(default=0, description="Number of articles")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create database tables and sample data on startup."""
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        # Check if data exists
        existing_articles = session.query(Article).first()
        if not existing_articles:
            # Sample data
            authors = [
                Author(
                    name="Alice Johnson",
                    email="alice@example.com",
                    bio="Tech writer",
                    article_count=5,
                ),
                Author(
                    name="Bob Smith",
                    email="bob@example.com",
                    bio="Software engineer",
                    article_count=3,
                ),
            ]

            articles = [
                Article(
                    title="Introduction to FastAPI",
                    content="FastAPI is a modern web framework for building APIs with Python...",
                    author="Alice Johnson",
                    published=True,
                    views=150,
                    tags='["python", "fastapi", "api"]',
                ),
                Article(
                    title="Building REST APIs with instant-crud",
                    content="instant-crud makes it easy to generate CRUD APIs...",
                    author="Alice Johnson",
                    published=True,
                    views=89,
                    tags='["python", "crud", "automation"]',
                ),
                Article(
                    title="Advanced Database Patterns",
                    content="Learn advanced patterns for database design...",
                    author="Bob Smith",
                    published=False,
                    views=12,
                    tags='["database", "patterns", "design"]',
                ),
            ]

            comments = [
                Comment(
                    article_id=1,
                    author="Reader1",
                    content="Great article!",
                    approved=True,
                ),
                Comment(
                    article_id=1,
                    author="Reader2",
                    content="Very helpful, thanks!",
                    approved=True,
                ),
                Comment(
                    article_id=2,
                    author="Developer",
                    content="instant-crud looks amazing!",
                    approved=False,
                ),
            ]

            for items in [authors, articles, comments]:
                for item in items:
                    session.add(item)

            session.commit()
            print("✅ Advanced example data created!")

    yield


# Custom pagination configuration
pagination_config = {
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

# Save pagination config to file for demo
with open("pagination_config.json", "w") as f:
    json.dump(pagination_config, f, indent=2)


# Custom settings
settings = InstantCRUDSettings(
    debug=True,
    api_prefix="/api/v1",
    default_page_size=10,
    max_page_size=100,
    enable_export=True,
    enable_auth=True,
    config_file="pagination_config.json",
)


# Create FastAPI app
app = FastAPI(
    title="Advanced Instant CRUD Example",
    version="1.0.0",
    description="Advanced example with authentication, custom pagination, and export features",
    lifespan=lifespan,
)


# Create CRUD factory with custom settings
factory = CRUDFactory(
    get_session=get_session,
    get_current_user=get_current_user,
    get_user_with_roles=get_user_with_roles,
    settings=settings,
)

# Create routers manually for fine control
article_router = factory.create_crud_router(
    model=Article,
    prefix="/articles",
    tags=["Articles"],
    search_fields=["title", "content", "author"],
    export_enabled=True,
    auth_enabled=True,
)

comment_router = factory.create_crud_router(
    model=Comment,
    prefix="/comments",
    tags=["Comments"],
    search_fields=["content", "author"],
    export_enabled=False,
    auth_enabled=True,
)

author_router = factory.create_crud_router(
    model=Author,
    prefix="/authors",
    tags=["Authors"],
    search_fields=["name", "bio"],
    export_enabled=True,
    auth_enabled=False,  # Public read access
    read_only=True,
)

# Include routers
app.include_router(article_router, prefix="/api/v1")
app.include_router(comment_router, prefix="/api/v1")
app.include_router(author_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Advanced Instant CRUD Example API",
        "version": "1.0.0",
        "features": [
            "JWT Authentication (use 'test-token')",
            "Custom page-based pagination",
            "Export functionality (Excel, CSV, PDF)",
            "Advanced search capabilities",
            "Role-based access control",
        ],
        "endpoints": {
            "articles": "/api/v1/articles (authenticated)",
            "comments": "/api/v1/comments (authenticated)",
            "authors": "/api/v1/authors (public, read-only)",
            "docs": "/docs",
        },
        "authentication": {
            "type": "Bearer Token",
            "test_token": "test-token",
            "header": "Authorization: Bearer test-token",
        },
    }


@app.get("/examples")
async def api_examples():
    """API usage examples."""
    return {
        "authentication": {
            "description": "Include Bearer token in Authorization header",
            "example": "Authorization: Bearer test-token",
        },
        "endpoints": {
            "list_articles": {
                "method": "GET",
                "url": "/api/v1/articles",
                "description": "List articles with page-based pagination",
                "example_response": {
                    "data": ["...articles..."],
                    "pagination": {
                        "current_page": 1,
                        "per_page": 10,
                        "total_pages": 3,
                        "total_count": 25,
                        "has_next": True,
                        "has_prev": False,
                    },
                },
            },
            "search_articles": {
                "method": "GET",
                "url": "/api/v1/articles/search?q=FastAPI",
                "description": "Search articles by title, content, or author",
            },
            "create_article": {
                "method": "POST",
                "url": "/api/v1/articles",
                "headers": {"Authorization": "Bearer test-token"},
                "body": {
                    "title": "My Article",
                    "content": "Article content here...",
                    "author": "John Doe",
                    "published": True,
                    "tags": '["python", "tutorial"]',
                },
            },
            "export_articles": {
                "method": "GET",
                "url": "/api/v1/articles/export/excel",
                "description": "Export articles to Excel file",
            },
            "export_to_pdf": {
                "method": "GET",
                "url": "/api/v1/articles/export/pdf?title=Articles Report",
                "description": "Export articles to PDF report",
            },
        },
        "curl_examples": [
            "curl -H 'Authorization: Bearer test-token' http://localhost:8000/api/v1/articles",
            "curl -H 'Authorization: Bearer test-token' http://localhost:8000/api/v1/articles/search?q=FastAPI",
            "curl -H 'Authorization: Bearer test-token' http://localhost:8000/api/v1/articles/export/excel",
            'curl -X POST -H \'Authorization: Bearer test-token\' -H \'Content-Type: application/json\' -d \'{"title":"Test","content":"Content","author":"Me"}\' http://localhost:8000/api/v1/articles',
        ],
    }


if __name__ == "__main__":
    import uvicorn

    print("🚀 Starting Advanced Instant CRUD Example...")
    print("📖 API Documentation: http://localhost:8001/docs")
    print("🔐 Authentication: Use 'test-token' as Bearer token")
    print("📄 Page-based pagination enabled")
    print("📊 Export features available")
    print("\n🧪 Test with authentication:")
    print(
        "  curl -H 'Authorization: Bearer test-token' http://localhost:8001/api/v1/articles"
    )
    print(
        "  curl -H 'Authorization: Bearer test-token' http://localhost:8001/api/v1/articles/export/excel"
    )

    uvicorn.run(
        "advanced_usage:app", host="0.0.0.0", port=8001, reload=True, log_level="info"
    )
