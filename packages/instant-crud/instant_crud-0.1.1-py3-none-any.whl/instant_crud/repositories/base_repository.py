"""
Base repository interface for instant-crud.
Minimal implementation to avoid import errors.
"""

from abc import ABC, abstractmethod
from typing import Generic, List, Optional, Dict, Any, TypeVar

T = TypeVar("T")


class BaseRepository(Generic[T], ABC):
    """Base repository interface."""

    @abstractmethod
    def get_all(self, **kwargs) -> List[T]:
        """Get all items."""

    @abstractmethod
    def get_by_id(self, id: Any) -> Optional[T]:
        """Get item by ID."""

    @abstractmethod
    def create(self, data: Dict[str, Any]) -> T:
        """Create new item."""

    @abstractmethod
    def update(self, id: Any, data: Dict[str, Any]) -> Optional[T]:
        """Update item."""

    @abstractmethod
    def delete(self, id: Any) -> bool:
        """Delete item."""
