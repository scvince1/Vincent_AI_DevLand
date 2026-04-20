"""
Topic Explorer endpoints — Page 4.
"""
from typing import Optional

from fastapi import APIRouter, Depends, Query

from backend.app.aggregations import compute_comparative_topics, compute_topics
from backend.app.scrapers.base import BaseScraper
from backend.app.scrapers import get_scraper
from backend.models.schemas import (
    Brand,
    Category,
    ComparativeTopicResponse,
    TopicExplorerResponse,
)

router = APIRouter(prefix="/api/topics", tags=["topics"])


@router.get("", response_model=TopicExplorerResponse)
def get_topics(
    brand: Optional[Brand] = Query(default=None),
    category: Optional[Category] = Query(default=None),
    scraper: BaseScraper = Depends(get_scraper),
) -> TopicExplorerResponse:
    """
    Emerging topics clustered by aspect, sorted by momentum.
    Each topic includes exemplar quotes for evidence traceability.
    """
    all_mentions = scraper.fetch(limit=10000, offset=0)
    filtered = [
        m for m in all_mentions
        if (brand is None or m.brand == brand)
        and (category is None or m.category == category)
    ]
    return compute_topics(filtered)


@router.get("/comparative", response_model=ComparativeTopicResponse)
def get_comparative_topics(
    brand_a: Brand = Query(..., description="First brand for comparison"),
    brand_b: Brand = Query(..., description="Second brand for comparison"),
    category: Optional[Category] = Query(default=None),
    scraper: BaseScraper = Depends(get_scraper),
) -> ComparativeTopicResponse:
    """
    Share-of-aspect comparison between two brands.
    Shows which aspects each brand dominates in consumer conversation.
    """
    all_mentions = scraper.fetch(limit=10000, offset=0)
    filtered = [
        m for m in all_mentions
        if m.brand in (brand_a, brand_b)
        and (category is None or m.category == category)
    ]
    return compute_comparative_topics(filtered, brand_a, brand_b)
