"""
Alerts & Insights endpoints — Page 5.
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from backend.app.aggregations import compute_alerts
from backend.app.scrapers.base import BaseScraper
from backend.app.scrapers import get_scraper
from backend.models.schemas import (
    AlertAcknowledgeResponse,
    AlertListResponse,
    Brand,
    Category,
    SourcePlatform,
)

router = APIRouter(prefix="/api/alerts", tags=["alerts"])

# In-memory acknowledged set (resets on restart — MVP simplification)
_acknowledged: set = set()


@router.get("", response_model=AlertListResponse)
def list_alerts(
    brand: Optional[Brand] = Query(default=None),
    category: Optional[Category] = Query(default=None),
    acknowledged: Optional[bool] = Query(
        default=None,
        description="Filter by acknowledged state. ?acknowledged=false for active, ?acknowledged=true for history",
    ),
    platforms: Optional[List[SourcePlatform]] = Query(
        default=None,
        description="Filter alerts to those involving any of the specified platforms",
    ),
    scraper: BaseScraper = Depends(get_scraper),
) -> AlertListResponse:
    """
    Rising negative aspect alerts sorted by severity.
    Use ?acknowledged=false for active alerts, ?acknowledged=true for history.
    Use ?platforms=reddit&platforms=amazon to filter by source platform.
    """
    all_mentions = scraper.fetch(limit=10000, offset=0)
    filtered = [
        m for m in all_mentions
        if (brand is None or m.brand == brand)
        and (category is None or m.category == category)
    ]
    alerts = compute_alerts(filtered)

    # Apply acknowledged state to each alert
    for alert in alerts:
        alert.acknowledged = alert.alert_id in _acknowledged

    # Filter by acknowledged param if provided
    if acknowledged is not None:
        alerts = [a for a in alerts if a.acknowledged == acknowledged]

    # Filter by platforms if provided
    if platforms:
        platform_set = set(platforms)
        alerts = [a for a in alerts if platform_set.intersection(set(a.platforms))]

    return AlertListResponse(total=len(alerts), items=alerts)


@router.patch("/{alert_id}/acknowledge", response_model=AlertAcknowledgeResponse)
def acknowledge_alert(
    alert_id: str,
    scraper: BaseScraper = Depends(get_scraper),
) -> AlertAcknowledgeResponse:
    """Mark an alert as acknowledged."""
    all_mentions = scraper.fetch(limit=10000, offset=0)
    alerts = compute_alerts(all_mentions)
    alert_ids = {a.alert_id for a in alerts}

    if alert_id not in alert_ids:
        raise HTTPException(status_code=404, detail=f"Alert '{alert_id}' not found")

    _acknowledged.add(alert_id)
    return AlertAcknowledgeResponse(alert_id=alert_id, acknowledged=True)
