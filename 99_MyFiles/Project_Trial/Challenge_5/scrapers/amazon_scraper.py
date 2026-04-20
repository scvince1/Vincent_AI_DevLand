"""
Amazon review scraper (placeholder).

IMPORTANT NOTICE:
    Amazon scraping requires careful rate limiting and may violate Amazon's
    Terms of Service. For production use, integrate one of these instead:

    1. Amazon Product Advertising API (official, free for affiliates)
       https://affiliate-program.amazon.com/help/topic/t3

    2. Rainforest API (licensed data provider, paid)
       https://www.rainforestapi.com/

    3. ScrapeHero Cloud (licensed scraping service)
       https://www.scrapehero.com/

    The scrape_reviews() method in this class returns an empty list and logs
    a warning.  Replace the body with real API calls before going to production.
"""

import logging

logger = logging.getLogger(__name__)


class AmazonScraper:
    """
    Placeholder Amazon review scraper.

    All methods return empty results with appropriate warnings until a real
    data-access mechanism is configured.
    """

    def __init__(self):
        logger.info(
            "AmazonScraper initialized in placeholder mode. "
            "Configure a real data source before use."
        )

    def scrape_reviews(self, asin: str, max_pages: int = 5) -> list[dict]:
        """
        Placeholder: would scrape reviews for the given ASIN.

        Parameters
        ----------
        asin : str
            Amazon Standard Identification Number for the product.
        max_pages : int
            Maximum review pages to fetch.

        Returns
        -------
        list[dict]
            Always returns an empty list (placeholder).
        """
        logger.warning(
            "scrape_reviews() is a placeholder. "
            "To collect Amazon reviews, integrate the Amazon Product Advertising API "
            "or a licensed data provider such as Rainforest API. "
            "Direct scraping may violate Amazon ToS."
        )
        return []

    @staticmethod
    def get_sample_asins() -> dict:
        """
        Returns a dictionary of SharkNinja product ASINs for reference.

        These are representative ASINs. Verify on Amazon before use.
        """
        return {
            "Shark AI Ultra Robot Vacuum RV2502WD": "B09NWKD8G3",
            "Shark IQ Robot Self-Empty XL RV1001AE": "B07JBQM92Q",
            "Shark Matrix Robot Vacuum RV2310WD": "B09X8KFQJN",
            "Shark Stratos Cordless IX141": "B0BKQXMHZR",
            "Shark HyperAIR Blow Dryer HD430": "B09YBZ4S22",
            "Ninja Foodi 6-in-1 DualZone Air Fryer DZ201": "B08GFPNPSD",
            "Ninja Air Fryer Max XL AF161": "B07FDJMC9Q",
            "Ninja Professional Plus Blender BN701": "B08H3KQLH2",
            "Ninja DualBrew Pro CFP301": "B08JFXXJZB",
            "Ninja Specialty Coffee Maker CM401": "B01N2LVF73",
        }
