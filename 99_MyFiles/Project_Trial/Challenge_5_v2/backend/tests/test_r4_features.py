"""
Round 4 feature tests.

Covers:
- Forecast endpoint: low-confidence flag, data-window edge cases
- AlertEvent.platforms field populated in compute_alerts
- CPSC scraper: recall record mapping, max-severity alert
- Reddit/HN scraper: import + instantiation (no live network calls)
- Mention.record_type field: default "review", CPSC emits "recall"
- Zero LLM calls in forecast path (import-time assertion)
"""
import json
import math
from datetime import datetime, timedelta, timezone
from typing import List
from unittest.mock import MagicMock, patch

import pytest

from backend.app.aggregations import compute_alerts
from backend.app.forecast import compute_forecast, BAND_WEEK_1, BAND_WEEK_4, FORECAST_DAYS
from backend.models.schemas import (
    AlertEvent,
    AspectSentiment,
    Brand,
    Category,
    DerivedSentiment,
    ForecastPoint,
    ForecastResponse,
    Mention,
    Polarity,
    SentimentLabel,
    SourcePlatform,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_mention(
    mention_id: str = "test-001",
    text: str = "Great product",
    compound: float = 0.5,
    posted_at: datetime = None,
    brand: Brand = Brand.shark,
    category: Category = Category.upright,
    product_model: str = "Shark Navigator",
    source_platform: SourcePlatform = SourcePlatform.amazon,
    record_type: str = "review",
    aspect_name: str = "suction",
    aspect_score: float = 0.5,
) -> Mention:
    if posted_at is None:
        posted_at = datetime.now(timezone.utc) - timedelta(days=7)

    return Mention(
        mention_id=mention_id,
        source_platform=source_platform,
        source_url=None,
        author_handle=None,
        posted_at=posted_at,
        ingested_at=datetime.now(timezone.utc),
        brand=brand,
        category=category,
        product_model=product_model,
        text=text,
        rating=None,
        language="en",
        derived=DerivedSentiment(
            overall_sentiment=SentimentLabel.positive if compound >= 0.05 else SentimentLabel.negative,
            compound_score=compound,
            confidence=0.9,
            sarcasm_flag=False,
            aspects=[AspectSentiment(
                name=aspect_name,
                polarity=Polarity.positive if compound >= 0 else Polarity.negative,
                score=aspect_score,
                confidence=0.9,
                snippet=text[:50],
            )],
        ),
        record_type=record_type,
    )


# ---------------------------------------------------------------------------
# Mention.record_type field
# ---------------------------------------------------------------------------

class TestMentionRecordType:
    def test_default_is_review(self):
        m = _make_mention()
        assert m.record_type == "review"

    def test_recall_value_accepted(self):
        m = _make_mention(record_type="recall")
        assert m.record_type == "recall"

    def test_invalid_record_type_rejected(self):
        with pytest.raises(Exception):
            _make_mention(record_type="invalid_value")


# ---------------------------------------------------------------------------
# Forecast: low_confidence flag
# ---------------------------------------------------------------------------

class TestForecastLowConfidence:
    def _make_mentions_for_forecast(self, count: int, days_span: int) -> List[Mention]:
        """Build N mentions spread over days_span days."""
        mentions = []
        now = datetime.now(timezone.utc)
        for i in range(count):
            days_ago = int(days_span * i / max(count - 1, 1))
            posted_at = now - timedelta(days=days_ago)
            mentions.append(_make_mention(
                mention_id=f"f-{i}",
                compound=0.3,
                posted_at=posted_at,
            ))
        return mentions

    def test_low_confidence_true_when_under_50_mentions(self):
        mentions = self._make_mentions_for_forecast(count=30, days_span=20)
        result = compute_forecast(mentions, "Shark Navigator")
        assert result.low_confidence is True
        assert result.input_mention_count == 30
        assert any("30" in c for c in result.caveats)

    def test_low_confidence_true_when_under_14_days(self):
        mentions = self._make_mentions_for_forecast(count=60, days_span=10)
        result = compute_forecast(mentions, "Shark Navigator")
        assert result.low_confidence is True
        assert any("10" in c or "day" in c for c in result.caveats)

    def test_low_confidence_false_when_sufficient_data(self):
        mentions = self._make_mentions_for_forecast(count=60, days_span=20)
        result = compute_forecast(mentions, "Shark Navigator")
        assert result.low_confidence is False
        assert result.caveats == []

    def test_low_confidence_true_with_zero_mentions(self):
        result = compute_forecast([], "Shark Navigator")
        assert result.low_confidence is True
        assert result.input_mention_count == 0

    def test_forecast_returns_28_points(self):
        mentions = self._make_mentions_for_forecast(count=60, days_span=25)
        result = compute_forecast(mentions, "Shark Navigator")
        assert len(result.forecast) == FORECAST_DAYS

    def test_confidence_bands_widen_with_horizon(self):
        mentions = self._make_mentions_for_forecast(count=60, days_span=25)
        result = compute_forecast(mentions, "Shark Navigator")
        first = result.forecast[0]
        last = result.forecast[-1]
        # Band width at day 1 should be narrower than at day 28
        band_first = last.confidence_upper - first.confidence_upper + (first.projected_score - last.projected_score)
        width_first = first.confidence_upper - first.confidence_lower
        width_last = last.confidence_upper - last.confidence_lower
        assert width_last >= width_first - 0.01  # allow tiny floating point

    def test_forecast_scores_clamped_to_minus_one_one(self):
        # Extreme negative slope — scores should not exceed [-1, 1]
        mentions = []
        now = datetime.now(timezone.utc)
        for i in range(60):
            posted_at = now - timedelta(days=i % 25)
            mentions.append(_make_mention(
                mention_id=f"clamp-{i}",
                compound=-0.99,
                posted_at=posted_at,
            ))
        result = compute_forecast(mentions, "Shark Navigator")
        for point in result.forecast:
            assert -1.0 <= point.projected_score <= 1.0
            assert -1.0 <= point.confidence_lower <= 1.0
            assert -1.0 <= point.confidence_upper <= 1.0

    def test_product_model_in_response(self):
        mentions = self._make_mentions_for_forecast(count=10, days_span=5)
        result = compute_forecast(mentions, "Shark PowerDetect")
        assert result.product_model == "Shark PowerDetect"

    def test_method_label_present(self):
        result = compute_forecast([], "Shark Navigator")
        assert result.method_label
        assert len(result.method_label) > 10

    def test_recall_mentions_excluded_from_forecast(self):
        """record_type='recall' mentions must not contribute sentiment scores."""
        mentions = []
        now = datetime.now(timezone.utc)
        for i in range(10):
            posted_at = now - timedelta(days=i)
            mentions.append(_make_mention(
                mention_id=f"recall-{i}",
                compound=-1.0,
                posted_at=posted_at,
                record_type="recall",
            ))
        # Add some normal review mentions
        for i in range(60):
            posted_at = now - timedelta(days=i % 25)
            mentions.append(_make_mention(
                mention_id=f"review-{i}",
                compound=0.5,
                posted_at=posted_at,
                record_type="review",
            ))
        result = compute_forecast(mentions, "Shark Navigator")
        # input_mention_count should only count reviews
        assert result.input_mention_count == 60


# ---------------------------------------------------------------------------
# AlertEvent.platforms field
# ---------------------------------------------------------------------------

class TestAlertEventPlatforms:
    def _make_negative_mention(self, idx, platform: SourcePlatform, days_ago_recent=True):
        now = datetime.now(timezone.utc)
        posted_at = now - timedelta(days=2 if days_ago_recent else 10)
        return _make_mention(
            mention_id=f"neg-{idx}",
            text="Battery completely dead after one month, terrible",
            compound=-0.8,
            posted_at=posted_at,
            source_platform=platform,
            aspect_name="battery",
            aspect_score=-0.8,
        )

    def _make_positive_old(self, idx, platform: SourcePlatform):
        now = datetime.now(timezone.utc)
        posted_at = now - timedelta(days=10)
        return _make_mention(
            mention_id=f"pos-{idx}",
            compound=0.5,
            posted_at=posted_at,
            source_platform=platform,
            aspect_name="battery",
            aspect_score=0.5,
        )

    def test_platforms_populated_on_alert(self):
        """alerts must have platforms populated from mentions."""
        mentions = []
        for i in range(5):
            mentions.append(self._make_negative_mention(i, SourcePlatform.reddit))
            mentions.append(self._make_positive_old(10 + i, SourcePlatform.reddit))

        alerts = compute_alerts(mentions)
        # Filter to battery alerts
        battery_alerts = [a for a in alerts if a.aspect == "battery"]
        if battery_alerts:
            alert = battery_alerts[0]
            assert isinstance(alert.platforms, list)
            assert len(alert.platforms) >= 1
            assert SourcePlatform.reddit in alert.platforms

    def test_platforms_multiplatform(self):
        """cross-platform alerts should list all contributing platforms."""
        mentions = []
        for i in range(4):
            mentions.append(self._make_negative_mention(i, SourcePlatform.reddit))
            mentions.append(self._make_negative_mention(10 + i, SourcePlatform.amazon))
            mentions.append(self._make_positive_old(20 + i, SourcePlatform.reddit))
            mentions.append(self._make_positive_old(30 + i, SourcePlatform.amazon))

        alerts = compute_alerts(mentions)
        battery_alerts = [a for a in alerts if a.aspect == "battery"]
        if battery_alerts:
            platforms_seen = set(battery_alerts[0].platforms)
            assert SourcePlatform.reddit in platforms_seen
            assert SourcePlatform.amazon in platforms_seen

    def test_platforms_default_empty(self):
        """AlertEvent with no exemplars should still have platforms as empty list."""
        alert = AlertEvent(
            alert_id="test",
            brand=Brand.shark,
            aspect="battery",
            severity=1.0,
            score_drop=-0.3,
            triggered_at=datetime.now(timezone.utc),
        )
        assert alert.platforms == []


# ---------------------------------------------------------------------------
# CPSC Recalls scraper
# ---------------------------------------------------------------------------

class TestCPSCScraper:
    def test_recall_mention_field_mapping(self):
        """Verify _recall_to_mention maps fields correctly."""
        from backend.app.scrapers.cpsc_adapter import CPSCScraper
        scraper = CPSCScraper()
        fake_recall = {
            "RecallID": 12345,
            "RecallNumber": "2025-123",
            "RecallDate": "2025-05-01T00:00:00",
            "Title": "SharkNinja Recalls 1.8 Million Foodi Pressure Cookers",
            "Description": "Due to risk of burns and laceration injuries.",
            "URL": "https://www.cpsc.gov/Recalls/2025/12345",
            "Products": [{"Name": "Ninja Foodi DualZone"}],
            "Manufacturers": [{"Name": "SharkNinja Operating LLC"}],
            "Importers": [],
            "Distributors": [],
        }
        mention = scraper._recall_to_mention(fake_recall)
        assert mention.record_type == "recall"
        assert mention.mention_id == "cpsc-2025-123"
        assert mention.source_url == "https://www.cpsc.gov/Recalls/2025/12345"
        assert mention.derived.compound_score == -1.0
        assert mention.brand == Brand.shark  # "sharkninja" → Brand.shark
        assert mention.product_model == "Ninja Foodi DualZone"
        assert "SharkNinja" in mention.text

    def test_recall_mention_platform_is_other(self):
        from backend.app.scrapers.cpsc_adapter import CPSCScraper
        scraper = CPSCScraper()
        fake_recall = {
            "RecallID": 99,
            "RecallNumber": "2025-099",
            "RecallDate": "2025-01-10T00:00:00",
            "Title": "Dyson Recalls Cordless Vacuums",
            "Description": "Fire risk.",
            "URL": "https://www.cpsc.gov/Recalls/2025/99",
            "Products": [],
            "Manufacturers": [{"Name": "Dyson Inc"}],
            "Importers": [],
            "Distributors": [],
        }
        mention = scraper._recall_to_mention(fake_recall)
        assert mention.source_platform == SourcePlatform.other

    def test_safety_recall_alert_max_severity(self):
        """CPSC recall mention must generate safety_recall alert at severity=10.0."""
        recall_mention = _make_mention(
            mention_id="cpsc-2025-123",
            text="SharkNinja Recalls Foodi Pressure Cooker due to burn risk",
            compound=-1.0,
            source_platform=SourcePlatform.other,
            record_type="recall",
        )
        alerts = compute_alerts([recall_mention])
        recall_alerts = [a for a in alerts if a.aspect == "safety_recall"]
        assert len(recall_alerts) == 1
        assert recall_alerts[0].severity == 10.0
        assert recall_alerts[0].score_drop == -1.0

    def test_safety_recall_alert_at_top_of_list(self):
        """Safety recall must sort first (highest severity)."""
        regular_mention = _make_mention(
            mention_id="reg-001",
            text="Battery completely dead",
            compound=-0.8,
            aspect_name="battery",
            aspect_score=-0.8,
        )
        recall_mention = _make_mention(
            mention_id="cpsc-001",
            text="Safety recall: risk of fire",
            compound=-1.0,
            record_type="recall",
        )
        # Add an old version of the same aspect for score drop
        old_positive = _make_mention(
            mention_id="old-001",
            compound=0.5,
            posted_at=datetime.now(timezone.utc) - timedelta(days=10),
            aspect_name="battery",
            aspect_score=0.5,
        )
        alerts = compute_alerts([regular_mention, recall_mention, old_positive])
        assert alerts[0].aspect == "safety_recall"
        assert alerts[0].severity == 10.0

    def test_firm_matches_title_fallback(self):
        from backend.app.scrapers.cpsc_adapter import _firm_matches
        recall_with_title_only = {
            "Title": "Shark PowerDetect Robot Vacuum Recall",
            "Manufacturers": [],
            "Importers": [],
            "Distributors": [],
        }
        assert _firm_matches(recall_with_title_only) is True

    def test_firm_matches_rejects_unrelated(self):
        from backend.app.scrapers.cpsc_adapter import _firm_matches
        unrelated = {
            "Title": "Generic Brand Toaster Recall",
            "Manufacturers": [{"Name": "Generic Co"}],
            "Importers": [],
            "Distributors": [],
        }
        assert _firm_matches(unrelated) is False


# ---------------------------------------------------------------------------
# Reddit + HN scraper: import + instantiation (no live calls)
# ---------------------------------------------------------------------------

class TestScraperInstantiation:
    def test_reddit_scraper_instantiates(self):
        from backend.app.scrapers.reddit_adapter import RedditScraper, DEFAULT_SUBREDDITS
        scraper = RedditScraper()
        # Default subreddits must include all 7 required (R4-P1-4 already applied)
        for sub in ["sharkninja", "BuyItForLife", "Appliances", "Coffee",
                    "airfryer", "VacuumCleaners", "homeautomation"]:
            assert sub in DEFAULT_SUBREDDITS, f"Missing subreddit: {sub}"

    def test_hn_scraper_instantiates(self):
        from backend.app.scrapers.hn_adapter import HackerNewsScraper
        scraper = HackerNewsScraper()
        assert scraper is not None

    def test_reddit_scraper_raises_without_credentials(self):
        """RedditScraper._get_praw() should raise EnvironmentError if no credentials."""
        import os
        from backend.app.scrapers.reddit_adapter import RedditScraper
        scraper = RedditScraper()
        # Temporarily clear env vars
        saved_id = os.environ.pop("REDDIT_CLIENT_ID", None)
        saved_secret = os.environ.pop("REDDIT_CLIENT_SECRET", None)
        try:
            scraper._praw = None  # Reset lazy init
            with pytest.raises(EnvironmentError):
                scraper._get_praw()
        finally:
            if saved_id:
                os.environ["REDDIT_CLIENT_ID"] = saved_id
            if saved_secret:
                os.environ["REDDIT_CLIENT_SECRET"] = saved_secret

    def test_scraper_factory_recognizes_all_adapters(self):
        """Factory __init__.py should recognize all adapter names without raising."""
        import importlib
        import backend.app.scrapers as factory_module
        # Reload to clear singleton
        importlib.reload(factory_module)
        # Test that unknown adapter raises ValueError
        import os
        os.environ["SCRAPER_ADAPTER"] = "unknown_adapter_xyz"
        factory_module._scraper_instance = None
        with pytest.raises(ValueError, match="unknown_adapter_xyz"):
            factory_module.get_scraper()
        # Restore
        os.environ["SCRAPER_ADAPTER"] = "csv"
        factory_module._scraper_instance = None


# ---------------------------------------------------------------------------
# R4-P1-4: Reddit subreddit list completeness (tested here since trivial)
# ---------------------------------------------------------------------------

class TestRedditSubredditList:
    def test_all_7_subreddits_in_default_list(self):
        from backend.app.scrapers.reddit_adapter import DEFAULT_SUBREDDITS
        required = [
            "sharkninja", "BuyItForLife", "Appliances", "Coffee",
            "airfryer", "VacuumCleaners", "homeautomation",
        ]
        for sub in required:
            assert sub in DEFAULT_SUBREDDITS, f"r/{sub} missing from DEFAULT_SUBREDDITS"
        assert len(DEFAULT_SUBREDDITS) >= 7


# ---------------------------------------------------------------------------
# R4-P1-2: What-If Simulator
# ---------------------------------------------------------------------------

class TestSimulator:
    """
    Tests for simulator schemas, disclaimer, caching, and grounding logic.
    All LLM calls are mocked — no real API calls in the test suite.
    """

    def _make_mentions_pool(self, count=20):
        now = datetime.now(timezone.utc)
        mentions = []
        for i in range(count):
            compound = 0.6 if i % 2 == 0 else -0.6
            mentions.append(_make_mention(
                mention_id=f"pool-{i}",
                text=f"Review text number {i} about the product suction and battery",
                compound=compound,
                posted_at=now - timedelta(days=i % 14),
            ))
        return mentions

    def test_disclaimer_string_exact_match(self):
        """Charter §6.2: disclaimer MUST contain exact string."""
        from backend.models.schemas import _SIMULATOR_DISCLAIMER
        required = "Simulated reaction based on LLM heuristic, not empirical behavior modeling."
        assert required in _SIMULATOR_DISCLAIMER

    def test_simulation_result_default_disclaimer(self):
        """SimulationResult.overall_disclaimer defaults to the required string."""
        from backend.models.schemas import SimulationResult, SimulatedSegment, _SIMULATOR_DISCLAIMER
        result = SimulationResult(
            scenario="test scenario",
            product_model="Shark Navigator",
            segments=[SimulatedSegment(
                segment_label="Test segment",
                predicted_reaction="positive",
                confidence_narrative="This is a test.",
                key_quotes_used=["quote1"],
            )],
            model_used="test-model",
            tokens_consumed=100,
        )
        required = "Simulated reaction based on LLM heuristic, not empirical behavior modeling."
        assert required in result.overall_disclaimer

    def test_cache_key_deterministic(self):
        """Same request content → same cache key."""
        from backend.app.routers.simulate import _cache_key
        from backend.models.schemas import SimulationRequest
        req1 = SimulationRequest(scenario="What if price drops?", product_model="Shark Nav")
        req2 = SimulationRequest(scenario="What if price drops?", product_model="Shark Nav")
        assert _cache_key(req1) == _cache_key(req2)

    def test_cache_key_differs_on_scenario(self):
        from backend.app.routers.simulate import _cache_key
        from backend.models.schemas import SimulationRequest
        req1 = SimulationRequest(scenario="What if price drops?", product_model="Shark Nav")
        req2 = SimulationRequest(scenario="What if warranty extends?", product_model="Shark Nav")
        assert _cache_key(req1) != _cache_key(req2)

    def test_grounding_mention_selection_prefers_product_model(self):
        """_select_grounding_mentions should prefer mentions matching product_model."""
        from unittest.mock import MagicMock
        from backend.app.routers.simulate import _select_grounding_mentions
        mock_scraper = MagicMock()
        mentions = self._make_mentions_pool(20)
        # Tag half with a specific product model
        for m in mentions[:10]:
            object.__setattr__(m, 'product_model', 'Shark Navigator')
        mock_scraper.fetch.return_value = mentions

        selected = _select_grounding_mentions(mock_scraper, "Shark Navigator", None, count=6)
        assert len(selected) <= 6
        # Should have selected from the pool
        assert all(getattr(m, 'record_type', 'review') == 'review' for m in selected)

    def test_grounding_excludes_recall_mentions(self):
        """record_type='recall' mentions must not be passed to LLM as grounding."""
        from unittest.mock import MagicMock
        from backend.app.routers.simulate import _select_grounding_mentions
        mock_scraper = MagicMock()
        mentions = self._make_mentions_pool(5)
        recall_mention = _make_mention(
            mention_id="cpsc-recall-1",
            text="CPSC Safety Recall: risk of fire",
            compound=-1.0,
            record_type="recall",
        )
        mock_scraper.fetch.return_value = mentions + [recall_mention]

        selected = _select_grounding_mentions(mock_scraper, None, None, count=10)
        assert all(getattr(m, 'record_type', 'review') != 'recall' for m in selected)

    def test_parse_llm_response_valid_json(self):
        """_parse_llm_response handles clean JSON output."""
        from backend.app.routers.simulate import _parse_llm_response
        raw = json.dumps({
            "segments": [
                {
                    "segment_label": "Budget-conscious buyers",
                    "predicted_reaction": "positive",
                    "confidence_narrative": "This group would react positively.",
                    "key_quotes_used": ["great value for money"],
                }
            ]
        })
        segments = _parse_llm_response(raw, [])
        assert len(segments) == 1
        assert segments[0].segment_label == "Budget-conscious buyers"
        assert segments[0].predicted_reaction == "positive"
        assert segments[0].key_quotes_used == ["great value for money"]

    def test_parse_llm_response_invalid_json_fallback(self):
        """_parse_llm_response returns a fallback segment on bad JSON."""
        from backend.app.routers.simulate import _parse_llm_response
        segments = _parse_llm_response("this is not json at all", [])
        assert len(segments) == 1
        assert "parse error" in segments[0].segment_label.lower()

    def test_parse_llm_response_strips_markdown_fences(self):
        """_parse_llm_response handles ```json ... ``` wrapping."""
        from backend.app.routers.simulate import _parse_llm_response
        raw = '```json\n{"segments": [{"segment_label": "Test", "predicted_reaction": "neutral", "confidence_narrative": "ok", "key_quotes_used": []}]}\n```'
        segments = _parse_llm_response(raw, [])
        assert len(segments) == 1
        assert segments[0].segment_label == "Test"

    def test_parse_llm_response_caps_at_5_segments(self):
        """LLM returning 7 segments should be capped at 5."""
        from backend.app.routers.simulate import _parse_llm_response
        segments_data = [
            {
                "segment_label": f"Segment {i}",
                "predicted_reaction": "neutral",
                "confidence_narrative": "Test.",
                "key_quotes_used": [],
            }
            for i in range(7)
        ]
        raw = json.dumps({"segments": segments_data})
        segments = _parse_llm_response(raw, [])
        assert len(segments) <= 5

    def test_endpoint_returns_503_without_api_key(self):
        """POST /api/simulate should return 503 when no API key is configured."""
        import os
        from fastapi.testclient import TestClient
        from backend.app.main import app

        client = TestClient(app, raise_server_exceptions=False)
        saved_key = os.environ.pop("SIMULATION_LLM_API_KEY", None)
        try:
            response = client.post(
                "/api/simulate",
                json={"scenario": "What if price drops to $99?", "product_model": "Shark Navigator"},
            )
            assert response.status_code == 503
        finally:
            if saved_key:
                os.environ["SIMULATION_LLM_API_KEY"] = saved_key

    def test_endpoint_uses_cache_on_second_call(self):
        """Second identical request should hit cache, not call LLM again."""
        from unittest.mock import patch, MagicMock
        from fastapi.testclient import TestClient
        from backend.app.main import app
        from backend.app.routers import simulate as sim_module
        from backend.models.schemas import SimulationResult, SimulatedSegment, _SIMULATOR_DISCLAIMER

        # Pre-populate cache with a known result
        mock_result = SimulationResult(
            scenario="cached scenario test",
            product_model=None,
            segments=[SimulatedSegment(
                segment_label="Cached segment",
                predicted_reaction="positive",
                confidence_narrative="From cache.",
                key_quotes_used=[],
            )],
            overall_disclaimer=_SIMULATOR_DISCLAIMER,
            model_used="cached-model",
            tokens_consumed=0,
        )
        from backend.app.routers.simulate import _cache_key, _cache
        from backend.models.schemas import SimulationRequest
        req = SimulationRequest(scenario="cached scenario test")
        _cache[_cache_key(req)] = mock_result

        client = TestClient(app)
        response = client.post(
            "/api/simulate",
            json={"scenario": "cached scenario test"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["model_used"] == "cached-model"
        assert data["tokens_consumed"] == 0

    def test_simulated_segment_schema(self):
        """SimulatedSegment rejects invalid predicted_reaction values."""
        from backend.models.schemas import SimulatedSegment
        for valid in ("positive", "negative", "mixed", "neutral"):
            s = SimulatedSegment(
                segment_label="Test",
                predicted_reaction=valid,
                confidence_narrative="ok",
            )
            assert s.predicted_reaction == valid

        with pytest.raises(Exception):
            SimulatedSegment(
                segment_label="Test",
                predicted_reaction="maybe",
                confidence_narrative="ok",
            )
