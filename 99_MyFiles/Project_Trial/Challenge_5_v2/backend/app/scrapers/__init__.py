"""
Scraper factory — returns a BaseScraper implementation based on config.

SCRAPER_ADAPTER env var controls which implementation is used:
  - "csv" (default): reads from backend/data/ CSV fixtures
  - "reddit": live Reddit posts via PRAW OAuth (needs REDDIT_CLIENT_ID/SECRET/USER_AGENT)
  - "hn": Hacker News posts via Algolia search API (no auth required)
  - "cpsc": CPSC recall records via SaferProducts.gov REST API (no auth required)
  - "ucsd": UCSD Amazon Appliances offline corpus (YELLOW LIGHT — internal demo only)

Routers call get_scraper() via FastAPI Depends — they never import a concrete adapter directly.
"""
import os

from backend.app.scrapers.base import BaseScraper

_scraper_instance: BaseScraper | None = None


def get_scraper() -> BaseScraper:
    """
    Factory function for FastAPI Depends.
    Returns a singleton BaseScraper instance.
    """
    global _scraper_instance
    if _scraper_instance is not None:
        return _scraper_instance

    adapter = os.environ.get("SCRAPER_ADAPTER", "csv").lower().strip()

    if adapter == "csv":
        from backend.app.scrapers.csv_adapter import CSVAdapter
        _scraper_instance = CSVAdapter(data_dir="backend/data/")
    elif adapter == "reddit":
        from backend.app.scrapers.reddit_adapter import RedditScraper
        _scraper_instance = RedditScraper()
    elif adapter == "hn":
        from backend.app.scrapers.hn_adapter import HackerNewsScraper
        _scraper_instance = HackerNewsScraper()
    elif adapter == "cpsc":
        from backend.app.scrapers.cpsc_adapter import CPSCScraper
        _scraper_instance = CPSCScraper()
    elif adapter == "ucsd":
        from backend.app.scrapers.ucsd_adapter import UCSDAdapter
        _scraper_instance = UCSDAdapter()
    else:
        raise ValueError(
            f"Unknown SCRAPER_ADAPTER: '{adapter}'. "
            "Supported: 'csv', 'reddit', 'hn', 'cpsc', 'ucsd'"
        )

    return _scraper_instance
