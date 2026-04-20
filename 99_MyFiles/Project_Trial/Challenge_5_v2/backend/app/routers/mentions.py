"""
Mentions endpoints — drill-through data access for all pages.
"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from backend.app.scrapers.base import BaseScraper
from backend.app.scrapers import get_scraper
from backend.models.schemas import (
    Brand,
    Category,
    Mention,
    MentionListResponse,
    SourcePlatform,
)

router = APIRouter(prefix="/api/mentions", tags=["mentions"])


@router.get("", response_model=MentionListResponse)
def list_mentions(
    platform: Optional[SourcePlatform] = Query(default=None),
    brand: Optional[Brand] = Query(default=None),
    category: Optional[Category] = Query(default=None),
    product_model: Optional[str] = Query(default=None),
    date_from: Optional[str] = Query(default=None),
    date_to: Optional[str] = Query(default=None),
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    topic_id: Optional[str] = Query(default=None),
    scraper: BaseScraper = Depends(get_scraper),
) -> MentionListResponse:
    """List mentions with optional filtering. Supports drill-through from all dashboard pages."""
    from datetime import datetime, timezone

    dt_from = None
    dt_to = None
    if date_from:
        try:
            dt_from = datetime.fromisoformat(date_from.replace("Z", "+00:00"))
        except ValueError:
            pass
    if date_to:
        try:
            dt_to = datetime.fromisoformat(date_to.replace("Z", "+00:00"))
        except ValueError:
            pass

    total = scraper.count(
        platform=platform.value if platform else None,
        brand=brand.value if brand else None,
        category=category.value if category else None,
        product_model=product_model,
        date_from=dt_from,
        date_to=dt_to,
        topic_id=topic_id,
    )
    items = scraper.fetch(
        platform=platform.value if platform else None,
        brand=brand.value if brand else None,
        category=category.value if category else None,
        product_model=product_model,
        date_from=dt_from,
        date_to=dt_to,
        limit=limit,
        offset=offset,
        topic_id=topic_id,
    )
    return MentionListResponse(total=total, items=items)


@router.get("/{mention_id}", response_model=Mention)
def get_mention(
    mention_id: str,
    scraper: BaseScraper = Depends(get_scraper),
) -> Mention:
    """Retrieve a single mention by ID."""
    all_mentions = scraper.fetch(limit=10000, offset=0)
    for m in all_mentions:
        if m.mention_id == mention_id:
            return m
    raise HTTPException(status_code=404, detail=f"Mention '{mention_id}' not found")
