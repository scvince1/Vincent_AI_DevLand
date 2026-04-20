"""
Platform comparison endpoints — Page 3.
"""
from typing import Optional

from fastapi import APIRouter, Depends, Query

from backend.app.aggregations import compute_platform_comparison
from backend.app.scrapers.base import BaseScraper
from backend.app.scrapers import get_scraper
from backend.models.schemas import Brand, Category, PlatformComparisonResponse

router = APIRouter(prefix="/api/platforms", tags=["platforms"])


@router.get("/comparison", response_model=PlatformComparisonResponse)
def get_platform_comparison(
    brand: Optional[Brand] = Query(default=None),
    category: Optional[Category] = Query(default=None),
    product_model: Optional[str] = Query(default=None),
    scraper: BaseScraper = Depends(get_scraper),
) -> PlatformComparisonResponse:
    """
    Cross-platform aspect sentiment grid.
    Rows = platforms, columns = aspects. Cell = sentiment score + mention volume.
    """
    all_mentions = scraper.fetch(limit=10000, offset=0)
    filtered = [
        m for m in all_mentions
        if (brand is None or m.brand == brand)
        and (category is None or m.category == category)
        and (product_model is None or (
            m.product_model and product_model.lower() in m.product_model.lower()
        ))
    ]
    return compute_platform_comparison(filtered)
