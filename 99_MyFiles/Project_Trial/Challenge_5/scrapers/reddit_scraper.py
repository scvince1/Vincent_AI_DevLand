"""
Reddit scraper for SharkNinja consumer sentiment data.

Requires a Reddit application with API credentials:
  - Create an app at https://www.reddit.com/prefs/apps
  - Set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET environment variables
  - Or pass credentials directly to RedditScraper.__init__()
"""

import os
import logging
from datetime import datetime

import pandas as pd

logger = logging.getLogger(__name__)

try:
    import praw
    PRAW_AVAILABLE = True
except ImportError:
    PRAW_AVAILABLE = False
    logger.warning("praw not installed. Run: pip install praw")


class RedditScraper:
    """Scrapes Reddit posts and comments about SharkNinja products."""

    DEFAULT_SUBREDDITS = [
        "VacuumCleaners",
        "airfryer",
        "Blenders",
        "Coffee",
        "shark",
        "ninja",
        "homeautomation",
        "BuyItForLife",
        "HomeImprovement",
        "KitchenConfidential",
    ]
    DEFAULT_QUERIES = ["shark vacuum", "ninja air fryer", "sharkninja", "shark robot", "ninja blender", "ninja coffee"]

    def __init__(
        self,
        client_id: str | None = None,
        client_secret: str | None = None,
        user_agent: str = "SharkNinja Sentiment Analyzer v1.0",
    ):
        self.client_id = client_id or os.getenv("REDDIT_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("REDDIT_CLIENT_SECRET")
        self.user_agent = user_agent
        self._reddit = None

    def _get_client(self):
        if self._reddit:
            return self._reddit
        if not PRAW_AVAILABLE:
            raise RuntimeError("praw is not installed. Run: pip install praw")
        if not self.client_id or not self.client_secret:
            raise ValueError(
                "Reddit API credentials required. Set REDDIT_CLIENT_ID and "
                "REDDIT_CLIENT_SECRET environment variables, or pass them to "
                "RedditScraper.__init__()."
            )
        self._reddit = praw.Reddit(
            client_id=self.client_id,
            client_secret=self.client_secret,
            user_agent=self.user_agent,
        )
        return self._reddit

    def _infer_brand(self, text: str) -> str:
        text_lower = text.lower()
        if "shark" in text_lower:
            return "shark"
        if "ninja" in text_lower:
            return "ninja"
        return "unknown"

    def _infer_category(self, text: str) -> str:
        text_lower = text.lower()
        kw_map = {
            "robot_vacuum": ["robot vacuum", "robovac", "roomba", "rv2", "rv1", "av2"],
            "stick_vacuum": ["stick vac", "cordless vac", "iz4", "ix1", "hv3"],
            "hair_dryer": ["hair dryer", "blow dryer", "hyperair", "flexstyle", "hd4"],
            "air_fryer": ["air fryer", "air fry", "dz2", "af1", "ag6", "sf3"],
            "blender": ["blender", "blend", "bn7", "ss2", "tb4", "smoothie"],
            "coffee_maker": ["coffee", "brew", "cfp", "cm4", "cp3", "cfn"],
        }
        for cat, keywords in kw_map.items():
            if any(kw in text_lower for kw in keywords):
                return cat
        return "unknown"

    def scrape_subreddit(
        self, subreddit_name: str, query: str, limit: int = 100
    ) -> list[dict]:
        """
        Search a subreddit for posts matching the query.

        Parameters
        ----------
        subreddit_name : str
            Name of the subreddit (without r/).
        query : str
            Search query string.
        limit : int
            Maximum number of posts to retrieve.

        Returns
        -------
        list[dict]
            List of dicts conforming to the standard data schema.
        """
        try:
            reddit = self._get_client()
        except Exception as exc:
            logger.warning("Reddit client unavailable: %s", exc)
            return []

        records = []
        try:
            subreddit = reddit.subreddit(subreddit_name)
            for submission in subreddit.search(query, limit=limit):
                text = submission.selftext or submission.title
                if not text.strip():
                    continue
                brand = self._infer_brand(text + " " + submission.title)
                category = self._infer_category(text + " " + submission.title)
                records.append({
                    "id": f"reddit_{submission.id}",
                    "platform": "reddit",
                    "product_category": category,
                    "product_name": "Unknown",
                    "brand": brand,
                    "text": (submission.title + " " + text).strip()[:1000],
                    "rating": 0.0,
                    "date": datetime.utcfromtimestamp(submission.created_utc).strftime("%Y-%m-%d %H:%M:%S"),
                    "sentiment_score": 0.0,
                    "sentiment_label": "neutral",
                    "topics": "[]",
                    "engagement_score": submission.score,
                    "author": str(submission.author) if submission.author else "deleted",
                })
        except Exception as exc:
            logger.error("Error scraping r/%s: %s", subreddit_name, exc)

        logger.info("Scraped %d posts from r/%s (query: %s)", len(records), subreddit_name, query)
        return records

    def scrape_multiple(
        self,
        subreddits: list[str] | None = None,
        queries: list[str] | None = None,
        limit: int = 50,
    ) -> pd.DataFrame:
        """
        Scrape multiple subreddits with multiple queries.

        Returns an empty DataFrame with a warning if credentials are missing.
        """
        if subreddits is None:
            subreddits = self.DEFAULT_SUBREDDITS
        if queries is None:
            queries = self.DEFAULT_QUERIES

        all_records = []
        for sub in subreddits:
            for query in queries:
                records = self.scrape_subreddit(sub, query, limit=limit)
                all_records.extend(records)

        if not all_records:
            logger.warning("No records collected. Check Reddit API credentials.")
            return pd.DataFrame(columns=[
                "id", "platform", "product_category", "product_name", "brand",
                "text", "rating", "date", "sentiment_score", "sentiment_label",
                "topics", "engagement_score", "author",
            ])

        df = pd.DataFrame(all_records).drop_duplicates(subset=["id"])
        logger.info("Total Reddit records: %d", len(df))
        return df
