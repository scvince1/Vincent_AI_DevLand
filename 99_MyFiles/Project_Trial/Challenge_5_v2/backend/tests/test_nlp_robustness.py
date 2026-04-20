"""
NLP Robustness Test Suite — additive coverage beyond the 16 gating edge cases.

These tests probe the pipeline on inputs that are structurally distinct from the
requirements.md cases. Some are expected to pass today; others are marked xfail
to document known refinement opportunities for round 2.

All tests run against the REAL pipeline. Zero mocks.
Do NOT import fixtures from test_nlp_edge_cases.py — this file is self-contained.
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import pytest

from backend.app.nlp.pipeline import analyze


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _aspects(result) -> dict:
    return {a["name"]: a["polarity"] for a in result.aspects}


def _pairs_by_brand(result) -> dict:
    out = {}
    for p in result.comparative_pairs:
        brand = p["brand"]
        if brand not in out:
            out[brand] = []
        out[brand].append(p)
    return out


# ---------------------------------------------------------------------------
# R1 — Double negation
# ---------------------------------------------------------------------------

def test_double_negation_positive():
    """
    'Not bad at all' is a mildly positive construction.
    Pipeline should not score this as negative.
    """
    result = analyze("This Shark is not bad at all")
    assert result.overall_sentiment in ("positive", "neutral"), (
        f"'not bad at all' expected positive/neutral, got '{result.overall_sentiment}' "
        f"(compound={result.compound_score:.3f})"
    )
    assert result.compound_score > -0.1, (
        f"Compound too negative for 'not bad at all': {result.compound_score:.3f}"
    )


def test_double_negation_neutral():
    """
    'Not exactly terrible but not great either' — hedged, should be neutral or mildly negative,
    definitely not strongly positive.
    """
    result = analyze("The Ninja Creami is not exactly terrible but not great either")
    # Acceptable: neutral or negative. Not acceptable: strongly positive.
    assert result.compound_score < 0.5, (
        f"Hedged double-negative scored too positive: compound={result.compound_score:.3f}"
    )


# ---------------------------------------------------------------------------
# R2 — Three-brand comparative
# ---------------------------------------------------------------------------

@pytest.mark.xfail(
    reason="refinement round 2: three-brand comparative — iRobot pair not emitted; "
           "pipeline extracts shark/dyson but misses irobot in the 'than iRobot but' clause"
)
def test_three_brand_comparative_four_pairs():
    """
    'Shark Matrix has better navigation than iRobot but worse suction than Dyson.'
    Should yield at least 4 comparative pairs covering all three brands.
    """
    text = "The Shark Matrix has better navigation than iRobot but worse suction than Dyson."
    result = analyze(text)
    pairs_by_brand = _pairs_by_brand(result)

    assert "shark" in pairs_by_brand, "shark not in comparative pairs"
    assert "irobot" in pairs_by_brand, "irobot not in comparative pairs"
    assert "dyson" in pairs_by_brand, "dyson not in comparative pairs"
    assert len(result.comparative_pairs) >= 4, (
        f"Expected >= 4 pairs for three-brand comparison, got {len(result.comparative_pairs)}"
    )


def test_three_brand_at_least_two_pairs():
    """
    Relaxed version: even if all three brands aren't resolved, at least 2 pairs
    and at least 2 different brands must be present.
    """
    text = "The Shark Matrix has better navigation than iRobot but worse suction than Dyson."
    result = analyze(text)
    assert len(result.comparative_pairs) >= 2, (
        f"Expected >= 2 comparative pairs, got {len(result.comparative_pairs)}"
    )
    brands_seen = {p["brand"] for p in result.comparative_pairs}
    assert len(brands_seen) >= 2, (
        f"Expected >= 2 brands in pairs, got {brands_seen}"
    )


# ---------------------------------------------------------------------------
# R3 — Multi-aspect long review
# ---------------------------------------------------------------------------

def test_multi_aspect_count():
    """
    A review mentioning 4 domain terms must emit at least 4 aspect entries.
    """
    text = "Suction is fantastic, the navigation is precise, the app is buggy, and the battery drains too fast."
    result = analyze(text)
    assert len(result.aspects) >= 4, (
        f"Expected >= 4 aspects, got {len(result.aspects)}: {_aspects(result)}"
    )


@pytest.mark.xfail(
    reason="refinement round 2: multi-aspect polarity — 'buggy' and 'drains too fast' not "
           "in STRONG_NEGATIVES lexicon; app and battery currently score neutral/positive"
)
def test_multi_aspect_correct_polarities():
    """
    'app is buggy' → app: negative. 'battery drains too fast' → battery: negative.
    Currently fails because 'buggy' and 'drains' are not in STRONG_NEGATIVES.
    """
    text = "Suction is fantastic, the navigation is precise, the app is buggy, and the battery drains too fast."
    result = analyze(text)
    aspects = _aspects(result)
    assert aspects.get("app") in ("negative", "mixed"), (
        f"app expected negative, got '{aspects.get('app')}'"
    )
    assert aspects.get("battery") in ("negative", "mixed"), (
        f"battery expected negative, got '{aspects.get('battery')}'"
    )


# ---------------------------------------------------------------------------
# R4 — Sarcasm with alternative cue words
# ---------------------------------------------------------------------------

@pytest.mark.xfail(
    reason="refinement round 2: 'brilliant' sarcasm variant — pipeline R1/R3 patterns "
           "require contrastive cue or 'Oh brilliant,' opener; mid-sentence 'brilliant' + "
           "failure clause does not trigger current rules"
)
def test_sarcasm_brilliant_cue():
    """
    'Brilliant engineering — a robot vacuum that gets lost every single time.'
    'Brilliant' as sarcastic opener + failure clause should flag as sarcasm.
    """
    text = "Brilliant engineering — a robot vacuum that gets lost in my living room every single time."
    result = analyze(text)
    assert result.sarcasm_flag is True, (
        f"sarcasm_flag expected True for 'Brilliant engineering — [failure]', got False. "
        f"compound={result.compound_score:.3f}"
    )
    assert result.overall_sentiment == "negative", (
        f"overall_sentiment expected 'negative', got '{result.overall_sentiment}'"
    )


def test_sarcasm_gem_cue():
    """
    'What a gem — paid $500 and the brushroll jammed after two weeks.'
    'gem' is a positive cue, followed by a strong negative clause. Pipeline
    should catch the negative content even if sarcasm_flag does not fire
    (brushroll jammed is in STRONG_NEGATIVES).
    """
    text = "What a gem — paid $500 and the brushroll jammed after two weeks."
    result = analyze(text)
    # Primary assertion: result is not positive overall
    assert result.overall_sentiment != "positive", (
        f"Expected not positive for gem+jam review, got '{result.overall_sentiment}'"
    )
    # Secondary: brushroll aspect should be detected and negative
    aspects = _aspects(result)
    assert "brushroll" in aspects, f"brushroll not extracted. Got: {list(aspects.keys())}"
    assert aspects["brushroll"] in ("negative", "mixed"), (
        f"brushroll expected negative, got '{aspects['brushroll']}'"
    )


# ---------------------------------------------------------------------------
# R5 — Domain term without strong sentiment
# ---------------------------------------------------------------------------

def test_portafilter_domain_term_extracted():
    """
    'The portafilter warrants replacement every three months.'
    Domain term 'portafilter' must be extracted as an aspect even when the
    sentence has no strong sentiment word.
    """
    text = "The portafilter warrants replacement every three months."
    result = analyze(text)
    aspects = _aspects(result)
    assert "portafilter" in aspects, (
        f"'portafilter' not extracted as an aspect. Got: {list(aspects.keys())}"
    )
    # Polarity may be neutral or mildly negative — we don't mandate a specific label
    assert aspects["portafilter"] in ("neutral", "negative", "mixed"), (
        f"portafilter polarity unexpected: '{aspects['portafilter']}'"
    )


# ---------------------------------------------------------------------------
# R6 — Negated positive
# ---------------------------------------------------------------------------

def test_negated_positive_overall_negative():
    """
    'I do not love the new Shark IQ — the app is clunky.'
    Negation of a positive word + negative aspect. Overall should not be positive.
    """
    text = "I do not love the new Shark IQ — the app is clunky."
    result = analyze(text)
    assert result.overall_sentiment != "positive", (
        f"Negated positive expected not-positive, got '{result.overall_sentiment}' "
        f"(compound={result.compound_score:.3f})"
    )


def test_negated_positive_app_aspect_negative():
    """
    'app is clunky' — 'clunky' should drive app aspect to negative.
    """
    text = "I do not love the new Shark IQ — the app is clunky."
    result = analyze(text)
    aspects = _aspects(result)
    assert "app" in aspects, f"'app' not extracted. Got: {list(aspects.keys())}"
    assert aspects["app"] in ("negative", "mixed"), (
        f"app expected negative for 'app is clunky', got '{aspects['app']}'"
    )


# ---------------------------------------------------------------------------
# R7 — Neutral factual statement
# ---------------------------------------------------------------------------

def test_neutral_factual_low_compound():
    """
    'The Ninja Foodi Dual Zone has two baskets and 6 preset modes.'
    Pure specification, no opinion. Compound score should be near zero.
    """
    text = "The Ninja Foodi Dual Zone has two baskets and 6 preset modes."
    result = analyze(text)
    assert abs(result.compound_score) < 0.4, (
        f"Factual statement should have low absolute compound, got {result.compound_score:.3f}"
    )
    assert result.sarcasm_flag is False, "Factual statement must not trigger sarcasm"


# ---------------------------------------------------------------------------
# R8 — Mixed with contrastive (dustbin "a joke")
# ---------------------------------------------------------------------------

def test_mixed_contrastive_suction_positive():
    """
    'Suction is fantastic but the dustbin is a joke.'
    Suction aspect must be positive regardless of dustbin outcome.
    """
    text = "Suction is fantastic but the dustbin is a joke."
    result = analyze(text)
    aspects = _aspects(result)
    assert "suction" in aspects, f"suction not extracted. Got: {list(aspects.keys())}"
    assert aspects["suction"] == "positive", (
        f"suction expected positive, got '{aspects['suction']}'"
    )


@pytest.mark.xfail(
    reason="refinement round 2: 'a joke' not in STRONG_NEGATIVES lexicon; "
           "dustbin scores positive because 'fantastic' bleeds into the clause window"
)
def test_mixed_contrastive_dustbin_negative():
    """
    'dustbin is a joke' — dustbin aspect should be negative.
    Currently fails because 'joke' is not in the STRONG_NEGATIVES lexicon.
    """
    text = "Suction is fantastic but the dustbin is a joke."
    result = analyze(text)
    aspects = _aspects(result)
    assert "dustbin" in aspects, f"dustbin not extracted. Got: {list(aspects.keys())}"
    assert aspects["dustbin"] in ("negative", "mixed"), (
        f"dustbin expected negative for 'is a joke', got '{aspects['dustbin']}'"
    )


# ---------------------------------------------------------------------------
# R9 — Brand alias (Roomba → irobot)
# ---------------------------------------------------------------------------

@pytest.mark.xfail(
    reason="refinement round 2: 'Roomba j7+' brand alias not producing comparative pairs; "
           "BRAND_ALIASES maps 'roomba' → irobot but the comparative extractor "
           "does not detect a comparison structure in this sentence"
)
def test_roomba_brand_alias_comparative():
    """
    'The Roomba j7+ beats the Shark IQ on obstacle avoidance.'
    'Roomba' → irobot via BRAND_ALIASES. irobot should be positive on obstacle_avoidance,
    shark negative on same aspect.
    """
    text = "The Roomba j7+ beats the Shark IQ on obstacle avoidance."
    result = analyze(text)
    pairs_by_brand = _pairs_by_brand(result)
    assert "irobot" in pairs_by_brand, (
        f"irobot (via 'Roomba' alias) not found in comparative pairs. Got: {list(pairs_by_brand.keys())}"
    )
    assert "shark" in pairs_by_brand, (
        f"shark not found in comparative pairs. Got: {list(pairs_by_brand.keys())}"
    )
    irobot_polarities = [p["polarity"] for p in pairs_by_brand.get("irobot", [])]
    assert "positive" in irobot_polarities, (
        f"irobot expected positive polarity, got {irobot_polarities}"
    )


# ---------------------------------------------------------------------------
# R10 — Rhetorical question
# ---------------------------------------------------------------------------

@pytest.mark.xfail(
    reason="refinement round 2: rhetorical question form — 'How am I supposed to love' "
           "contains 'love' (positive cue) and 'cannot' (negation) but the overall VADER "
           "score is dominated by 'love' and the pipeline returns positive; "
           "interrogative form inversion not implemented"
)
def test_rhetorical_question_negative():
    """
    'How am I supposed to love a vacuum that cannot handle pet hair?'
    Rhetorical question with negation implies frustration/negativity.
    Pipeline currently scores positive due to 'love' dominating.
    """
    text = "How am I supposed to love a vacuum that cannot handle pet hair?"
    result = analyze(text)
    assert result.overall_sentiment == "negative", (
        f"Rhetorical negative question expected 'negative', got '{result.overall_sentiment}' "
        f"(compound={result.compound_score:.3f})"
    )
