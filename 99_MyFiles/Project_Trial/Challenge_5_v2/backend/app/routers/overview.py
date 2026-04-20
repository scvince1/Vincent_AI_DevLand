"""
Overview endpoints — Page 1 KPIs, timeseries, and share of voice.
"""
from typing import Optional

from fastapi import APIRouter, Depends, Query

from backend.app.aggregations import (
    compute_overview_kpis,
    compute_share_of_voice,
    compute_timeseries,
)
from backend.app.scrapers.base import BaseScraper
from backend.app.scrapers import get_scraper
from backend.models.schemas import (
    Brand,
    Category,
    OverviewKPIs,
    ShareOfVoiceResponse,
    TimeseriesResponse,
)

router = APIRouter(prefix="/api/overview", tags=["overview"])


@router.get("/kpis", response_model=OverviewKPIs)
def get_kpis(
    brand: Optional[Brand] = Query(default=None),
    category: Optional[Category] = Query(default=None),
    scraper: BaseScraper = Depends(get_scraper),
) -> OverviewKPIs:
    """Top-line KPIs: total mentions, overall sentiment score, WoW delta, rising aspects."""
    all_mentions = scraper.fetch(limit=10000, offset=0)
    filtered = [
        m for m in all_mentions
        if (brand is None or m.brand == brand)
        and (category is None or m.category == category)
    ]
    return compute_overview_kpis(filtered, all_mentions)


@router.get("/timeseries", response_model=TimeseriesResponse)
def get_timeseries(
    brand: Optional[Brand] = Query(default=None),
    category: Optional[Category] = Query(default=None),
    scraper: BaseScraper = Depends(get_scraper),
) -> TimeseriesResponse:
    """Daily sentiment timeseries, filterable by brand/category."""
    all_mentions = scraper.fetch(limit=10000, offset=0)
    filtered = [
        m for m in all_mentions
        if (brand is None or m.brand == brand)
        and (category is None or m.category == category)
    ]
    return compute_timeseries(filtered, brand=brand, category=category)


@router.get("/share_of_voice", response_model=ShareOfVoiceResponse)
def get_share_of_voice(
    category: Optional[Category] = Query(default=None),
    scraper: BaseScraper = Depends(get_scraper),
) -> ShareOfVoiceResponse:
    """Share-of-voice by brand. Optionally filtered by category."""
    all_mentions = scraper.fetch(limit=10000, offset=0)
    filtered = [
        m for m in all_mentions
        if (category is None or m.category == category)
    ]
    return compute_share_of_voice(filtered)
