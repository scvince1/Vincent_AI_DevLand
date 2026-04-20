"""
BaseScraper ABC — defines the interface all scrapers must implement.
Routers depend ONLY on this ABC, never on concrete implementations.
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional

from backend.models.schemas import Mention


class BaseScraper(ABC):
    """Abstract base class for all data scrapers."""

    @abstractmethod
    def fetch(
        self,
        platform: Optional[str] = None,
        brand: Optional[str] = None,
        category: Optional[str] = None,
        product_model: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0,
        topic_id: Optional[str] = None,
    ) -> List[Mention]:
        """Fetch and return a list of Mention objects matching the given filters."""
        ...

    @abstractmethod
    def count(
        self,
        platform: Optional[str] = None,
        brand: Optional[str] = None,
        category: Optional[str] = None,
        product_model: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        topic_id: Optional[str] = None,
    ) -> int:
        """Return the total count of mentions matching the given filters (no pagination)."""
        ...
