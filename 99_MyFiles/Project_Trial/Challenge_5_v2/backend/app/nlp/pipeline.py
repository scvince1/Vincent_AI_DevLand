"""
NLP Pipeline orchestrator.

Processing order:
  1. Pre-process: merge multi-word domain terms into single tokens
  2. LAYER 1: VADER baseline
  3. Load spaCy doc (one parse, shared across LAYER 2 modules)
  4. LAYER 2a: sarcasm detection
  5. LAYER 2b: comparative pairs extraction
  6. LAYER 2c: ABSA
  7. Compute final compound_score:
       - If aspects found: weighted average of aspect scores
       - Else: VADER compound
       - If sarcasm_flag: multiply by -1 (and cap at -0.3 minimum)
  8. Derive overall_sentiment label from final compound_score
  9. Compute confidence

LAYER 2 overrides LAYER 1 in this priority:
  - sarcasm_flag=True  → invert compound, set label to "negative"
  - aspects non-empty  → use aspect-weighted compound + distribution label
  - comparative_pairs  → added to output, does NOT override overall
  - fallback           → VADER compound + label
"""
from __future__ import annotations

import re
from typing import List, Optional

from backend.app.nlp.absa import extract_aspects
from backend.app.nlp.comparative import extract_comparative_pairs
from backend.app.nlp.domain_lexicon import DOMAIN_TERMS, MULTIWORD_TERMS
from backend.app.nlp.sarcasm import detect_sarcasm
from backend.app.nlp.vader import get_vader_scores, vader_label
from backend.models.schemas import (
    AspectSentiment,
    ComparativePair,
    DerivedSentiment,
    Polarity,
    SentimentLabel,
    Brand,
)

# Lazy-load spaCy to avoid startup cost when not needed
_nlp = None


def _get_nlp():
    global _nlp
    if _nlp is None:
        try:
            import spacy
            _nlp = spacy.load("en_core_web_sm")
        except Exception:
            _nlp = False  # flag: unavailable
    return _nlp if _nlp is not False else None


def preprocess_domain_terms(text: str) -> str:
    """
    Merge multi-word domain terms into underscore-joined tokens so spaCy
    treats them as a single unit.

    Example: "self-empty base" → "self_empty_base"
             "HEPA filter" → "hepa_filter"
    """
    result = text
    for surface, canonical in MULTIWORD_TERMS:
        pattern = re.compile(r"\b" + re.escape(surface) + r"\b", re.IGNORECASE)
        result = pattern.sub(canonical, result)
    return result


def _compute_aspect_compound(aspects: List[dict]) -> float:
    """Weighted average of aspect scores."""
    if not aspects:
        return 0.0
    # Weight: more confident aspects contribute more
    total_weight = sum(a.get("confidence", 0.5) for a in aspects)
    if total_weight == 0:
        return 0.0
    weighted_sum = sum(a.get("score", 0.0) * a.get("confidence", 0.5) for a in aspects)
    return weighted_sum / total_weight


def _derive_label(compound: float, aspects: List[dict]) -> str:
    """
    Derive overall sentiment label.
    If aspects present, use distribution (majority polarity).
    Otherwise use compound threshold.
    """
    if aspects:
        pos = sum(1 for a in aspects if a.get("polarity") == "positive")
        neg = sum(1 for a in aspects if a.get("polarity") == "negative")
        mixed = sum(1 for a in aspects if a.get("polarity") == "mixed")
        total = len(aspects)
        if neg > 0 and pos > 0:
            return "mixed"
        if neg / total >= 0.6:
            return "negative"
        if pos / total >= 0.6:
            return "positive"
        if mixed > 0:
            return "mixed"
        # Fall through to compound-based
    return vader_label(compound)


def _compute_confidence(
    vader_scores: dict,
    aspects: List[dict],
    sarcasm_flag: bool,
    comparative_pairs: List[dict],
) -> float:
    """Heuristic confidence score."""
    base = min(0.5 + abs(vader_scores.get("compound", 0)) * 0.4, 0.85)
    if aspects:
        aspect_confidence = sum(a.get("confidence", 0.5) for a in aspects) / len(aspects)
        base = (base + aspect_confidence) / 2
    if sarcasm_flag:
        base = max(base, 0.72)  # sarcasm detection already has high confidence
    if comparative_pairs:
        base = max(base, 0.65)
    return round(min(base, 1.0), 3)


class SentimentResult:
    """Internal result object — converted to Pydantic DerivedSentiment via to_derived_sentiment()."""

    def __init__(
        self,
        compound_score: float,
        overall_sentiment: str,
        confidence: float,
        sarcasm_flag: bool,
        aspects: List[dict],
        comparative_pairs: List[dict],
    ):
        self.compound_score = round(max(-1.0, min(1.0, compound_score)), 4)
        self.overall_sentiment = overall_sentiment
        self.confidence = confidence
        self.sarcasm_flag = sarcasm_flag
        self.aspects = aspects
        self.comparative_pairs = comparative_pairs

    def to_derived_sentiment(self) -> DerivedSentiment:
        """Convert to Pydantic DerivedSentiment for use in routers/scrapers."""
        aspect_objs = []
        for a in self.aspects:
            aspect_objs.append(
                AspectSentiment(
                    name=a.get("name", ""),
                    polarity=Polarity(a.get("polarity", "neutral")),
                    score=float(a.get("score", 0.0)),
                    confidence=float(a.get("confidence", 0.5)),
                    snippet=a.get("snippet", ""),
                )
            )

        pair_objs: Optional[List[ComparativePair]] = None
        if self.comparative_pairs:
            pair_objs = []
            for p in self.comparative_pairs:
                try:
                    brand_val = Brand(p.get("brand", "other"))
                except ValueError:
                    brand_val = Brand.other
                pair_objs.append(
                    ComparativePair(
                        brand=brand_val,
                        aspect=p.get("aspect", "general"),
                        polarity=Polarity(p.get("polarity", "neutral")),
                        score=float(p.get("score", 0.0)),
                    )
                )

        return DerivedSentiment(
            overall_sentiment=SentimentLabel(self.overall_sentiment),
            compound_score=self.compound_score,
            confidence=self.confidence,
            sarcasm_flag=self.sarcasm_flag,
            aspects=aspect_objs,
            comparative_pairs=pair_objs,
        )


def analyze(text: str) -> SentimentResult:
    """
    Full NLP pipeline. Returns SentimentResult.

    This is the real pipeline — no mocks. Edge-case tests run against this.
    """
    # 1. Pre-process multi-word domain terms
    processed_text = preprocess_domain_terms(text)

    # 2. LAYER 1 — VADER baseline
    vader_scores = get_vader_scores(processed_text)

    # 3. spaCy parse (shared across layer 2 modules)
    nlp = _get_nlp()
    doc = nlp(processed_text) if nlp is not None else None

    # 4. LAYER 2a — sarcasm
    sarcasm_flag, sarcasm_confidence = detect_sarcasm(text, vader_scores)

    # 5. LAYER 2b — comparative pairs
    comparative_pairs = extract_comparative_pairs(text, doc)

    # 6. LAYER 2c — ABSA
    aspects = extract_aspects(processed_text, doc)

    # 7. Compute final compound score
    if aspects:
        compound = _compute_aspect_compound(aspects)
    else:
        compound = vader_scores.get("compound", 0.0)

    # Sarcasm overrides: invert if sarcasm detected
    if sarcasm_flag:
        if compound > 0:
            compound = -compound
        elif compound > -0.3:
            compound = -0.35  # ensure it's clearly negative

    # 8. Derive label
    if sarcasm_flag:
        label = "negative"
    else:
        label = _derive_label(compound, aspects)

    # 9. Confidence
    confidence = _compute_confidence(vader_scores, aspects, sarcasm_flag, comparative_pairs)

    return SentimentResult(
        compound_score=compound,
        overall_sentiment=label,
        confidence=confidence,
        sarcasm_flag=sarcasm_flag,
        aspects=aspects,
        comparative_pairs=comparative_pairs,
    )
