"""
TikTok data collector (placeholder).

IMPORTANT NOTICE:
    TikTok data collection for research purposes requires access to the
    TikTok Research API.  Apply at:
        https://developers.tiktok.com/products/research-api/

    The methods in this class return empty results with appropriate warnings
    until a valid Research API access token is configured.

    Commercial use also requires compliance with TikTok's Terms of Service
    and applicable data protection regulations (GDPR, CCPA, etc.).
"""

import logging

logger = logging.getLogger(__name__)


class TikTokScraper:
    """
    Placeholder TikTok data collector.

    All methods return empty results until TikTok Research API access
    is configured.
    """

    RESEARCH_API_BASE = "https://open.tiktokapis.com/v2/"

    def __init__(self, access_token: str | None = None):
        """
        Parameters
        ----------
        access_token : str, optional
            TikTok Research API access token.  Obtain by applying at
            https://developers.tiktok.com/products/research-api/
        """
        self.access_token = access_token
        if not access_token:
            logger.warning(
                "TikTokScraper: no access_token provided. "
                "All methods will return empty results. "
                "Apply for TikTok Research API access at "
                "https://developers.tiktok.com/products/research-api/"
            )

    def search_videos(self, query: str, max_results: int = 100) -> list[dict]:
        """
        Placeholder: search for TikTok videos matching the query.

        Parameters
        ----------
        query : str
            Hashtag or keyword search string (e.g., "sharkvacuum", "ninjaairfryer").
        max_results : int
            Maximum number of video records to return.

        Returns
        -------
        list[dict]
            Always returns an empty list (placeholder).
        """
        logger.warning(
            "search_videos() is a placeholder. "
            "Configure TikTok Research API access to enable real data collection. "
            "Query attempted: %s",
            query,
        )
        return []

    def extract_comments(self, video_id: str) -> list[dict]:
        """
        Placeholder: extract comments from a TikTok video.

        Parameters
        ----------
        video_id : str
            TikTok video identifier.

        Returns
        -------
        list[dict]
            Always returns an empty list (placeholder).
        """
        logger.warning(
            "extract_comments() is a placeholder. "
            "Configure TikTok Research API access to enable real data collection. "
            "Video ID attempted: %s",
            video_id,
        )
        return []

    def search_sharkninja_content(self, limit_per_query: int = 50) -> list[dict]:
        """
        Convenience method that searches for all major SharkNinja hashtags.

        Returns a combined list of video records (empty until API is configured).
        """
        queries = [
            "sharkvacuum", "sharkrobotvacuum", "sharkiq",
            "ninjaairfryer", "ninjacoffee", "ninjablender",
            "sharkninja", "robotvacuum", "airfryer",
        ]
        all_results = []
        for q in queries:
            results = self.search_videos(q, max_results=limit_per_query)
            all_results.extend(results)
        return all_results
