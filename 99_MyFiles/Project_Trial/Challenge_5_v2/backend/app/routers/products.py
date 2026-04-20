"""
Product endpoints — Page 2 Product Analysis.
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import PlainTextResponse

from backend.app.aggregations import compute_product_aspects, compute_timeseries
from backend.app.forecast import compute_forecast, EXPLAIN_TEXT
from backend.app.scrapers.base import BaseScraper
from backend.app.scrapers import get_scraper
from backend.models.schemas import (
    AspectTrend,
    Brand,
    Category,
    ForecastResponse,
    Mention,
    ProductAspectResponse,
    ProductSummary,
    TimeseriesResponse,
)

router = APIRouter(prefix="/api/products", tags=["products"])


@router.get("", response_model=List[ProductSummary])
def list_products(
    brand: Optional[Brand] = Query(default=None),
    category: Optional[Category] = Query(default=None),
    scraper: BaseScraper = Depends(get_scraper),
) -> List[ProductSummary]:
    """List all products with summary stats (brand, category, overall score, mention count)."""
    all_mentions = scraper.fetch(limit=10000, offset=0)
    filtered = [
        m for m in all_mentions
        if (brand is None or m.brand == brand)
        and (category is None or m.category == category)
        and m.product_model
    ]

    from collections import defaultdict
    product_data: dict = defaultdict(lambda: {"brand": None, "category": None, "scores": [], "count": 0})

    for m in filtered:
        key = m.product_model
        product_data[key]["brand"] = m.brand
        product_data[key]["category"] = m.category
        product_data[key]["scores"].append(m.derived.compound_score)
        product_data[key]["count"] += 1

    results = []
    for model, data in sorted(product_data.items()):
        scores = data["scores"]
        avg = sum(scores) / len(scores) if scores else 0.0
        results.append(ProductSummary(
            brand=data["brand"],
            category=data["category"],
            product_model=model,
            overall_score=round(avg, 4),
            mention_count=data["count"],
        ))

    return sorted(results, key=lambda p: p.mention_count, reverse=True)


@router.get("/{product_model}/aspects", response_model=ProductAspectResponse)
def get_product_aspects(
    product_model: str,
    scraper: BaseScraper = Depends(get_scraper),
) -> ProductAspectResponse:
    """Per-product aspect breakdown with trend and severity."""
    all_mentions = scraper.fetch(limit=10000, offset=0)
    product_mentions = [
        m for m in all_mentions
        if m.product_model and product_model.lower() in m.product_model.lower()
    ]

    if not product_mentions:
        raise HTTPException(status_code=404, detail=f"No mentions found for product '{product_model}'")

    # Derive brand/category from most common value
    from collections import Counter
    brands = Counter(m.brand for m in product_mentions)
    categories = Counter(m.category for m in product_mentions)
    top_brand = brands.most_common(1)[0][0]
    top_category = categories.most_common(1)[0][0]

    aspect_data = compute_product_aspects(product_mentions)
    aspects = [
        AspectTrend(
            aspect=a["aspect"],
            mention_count=a["mention_count"],
            avg_score=a["avg_score"],
            trend_delta=a["trend_delta"],
            severity=a["severity"],
            sparkline=a["sparkline"],
        )
        for a in aspect_data
    ]

    # Top 5 exemplar mentions sorted by |compound| for traceability
    exemplars = sorted(product_mentions, key=lambda m: abs(m.derived.compound_score), reverse=True)[:5]

    return ProductAspectResponse(
        product_model=product_model,
        brand=top_brand,
        category=top_category,
        aspects=aspects,
        exemplar_mentions=exemplars,
    )


@router.get("/{product_model}/timeseries", response_model=TimeseriesResponse)
def get_product_timeseries(
    product_model: str,
    scraper: BaseScraper = Depends(get_scraper),
) -> TimeseriesResponse:
    """Per-product daily sentiment timeseries."""
    all_mentions = scraper.fetch(limit=10000, offset=0)
    product_mentions = [
        m for m in all_mentions
        if m.product_model and product_model.lower() in m.product_model.lower()
    ]

    if not product_mentions:
        raise HTTPException(status_code=404, detail=f"No mentions found for product '{product_model}'")

    return compute_timeseries(product_mentions)


@router.get("/{product_model}/forecast", response_model=ForecastResponse)
def get_product_forecast(
    product_model: str,
    explain: bool = Query(
        default=False,
        description="Return formula documentation instead of forecast data",
    ),
    scraper: BaseScraper = Depends(get_scraper),
):
    """
    4-week forward sentiment forecast using exponentially-weighted linear projection.

    Use ?explain=true to return the formula documentation instead of forecast data.

    Method: heuristic projection, NOT an LLM simulation. See forecast.py for full formula.
    low_confidence=true when mention_count < 50 OR window_days < 14.
    """
    if explain:
        return PlainTextResponse(content=EXPLAIN_TEXT or "No documentation available.")

    all_mentions = scraper.fetch(limit=10000, offset=0)
    product_mentions = [
        m for m in all_mentions
        if m.product_model and product_model.lower() in m.product_model.lower()
    ]

    if not product_mentions:
        raise HTTPException(status_code=404, detail=f"No mentions found for product '{product_model}'")

    return compute_forecast(product_mentions, product_model)
