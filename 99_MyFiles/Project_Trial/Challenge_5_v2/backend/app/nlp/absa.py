"""
LAYER 2 — Aspect-Based Sentiment Analysis (ABSA).

Technique: clause-aware window scoring + domain lexicon, with spaCy
dependency subtree parsing for better accuracy.

The key insight: a wide window (±50 chars) picks up opinion words from
ADJACENT aspects and averages out. We instead:
  1. Split the text into clauses at comma / "but" / "and" boundaries
  2. For each clause, find domain terms (aspects)
  3. Score each clause independently using VADER + strong opinion override
  4. Associate the aspect name with its clause's score

This ensures "Suction is incredible but the dustbin is tiny and the battery
is garbage" produces three distinct aspect scores rather than one average.
"""
import re
from typing import List, Dict, Tuple, Optional

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from backend.app.nlp.domain_lexicon import DOMAIN_TERMS

_analyzer = SentimentIntensityAnalyzer()

# Strong positive opinion words — override VADER when present
STRONG_POSITIVES: Dict[str, float] = {
    "great": 0.55,
    "incredible": 0.75,
    "excellent": 0.70,
    "amazing": 0.70,
    "perfect": 0.65,
    "fantastic": 0.70,
    "wonderful": 0.60,
    "outstanding": 0.70,
    "brilliant": 0.65,
    "superb": 0.70,
    "works": 0.30,
    "picks up": 0.40,
    "love": 0.60,
    "good": 0.40,
    "nice": 0.40,
    "better": 0.40,
    "fast": 0.30,
    "quick": 0.30,
    "clean": 0.30,
}

# Strong negative opinion words
STRONG_NEGATIVES: Dict[str, float] = {
    "garbage": -0.75,
    "terrible": -0.70,
    "awful": -0.70,
    "horrible": -0.70,
    "useless": -0.65,
    "broken": -0.65,
    "dead": -0.60,
    "jammed": -0.60,
    "jam": -0.50,
    "jams": -0.55,
    "tangle": -0.50,
    "tangles": -0.55,
    "tiny": -0.40,
    "small": -0.30,
    "mess": -0.60,
    "flaking": -0.65,
    "flakes": -0.60,
    "impossible": -0.65,
    "frustrating": -0.60,
    "disappointing": -0.55,
    "loud": -0.45,
    "noisy": -0.45,
    "bad": -0.55,
    "poor": -0.50,
    "slow": -0.40,
    "hard": -0.30,
    "stops": -0.40,
    "stop": -0.35,
    "forever": -0.40,
    "gets old": -0.45,
    "old fast": -0.45,
    "replacing": -0.30,
    "needs replacing": -0.50,
    "can't": -0.55,
    "cannot": -0.55,
    "takes forever": -0.60,
}

# Sentiment modifiers
NEGATION_WORDS = {"not", "no", "never", "don't", "doesn't", "didn't", "won't",
                  "can't", "cannot", "isn't", "aren't", "wasn't", "weren't"}


def _split_into_clauses(text: str) -> List[str]:
    """
    Split text into clauses at comma, 'but', 'and', semicolons.
    Returns non-empty clauses.
    """
    # Split on common clause separators
    clauses = re.split(r",\s*|;\s*|\s+but\s+|\s+and\s+|\s+which\s+|\s+however\s+", text, flags=re.IGNORECASE)
    return [c.strip() for c in clauses if c.strip() and len(c.strip()) > 3]


def _score_clause(clause: str) -> Tuple[float, str, float]:
    """
    Score a single clause. Returns (compound, label, confidence).
    Uses VADER base + strong opinion word overrides.
    """
    lower = clause.lower()
    tokens = re.findall(r"\b[a-z']+\b", lower)
    token_set = set(tokens)

    # Check for negation in this clause
    has_negation = bool(token_set & NEGATION_WORDS)

    # Find strongest positive and negative signals
    max_pos = 0.0
    max_neg = 0.0
    pos_word = None
    neg_word = None

    # Check multi-word negatives first
    for phrase, score in STRONG_NEGATIVES.items():
        if phrase in lower:
            if abs(score) > abs(max_neg):
                max_neg = score
                neg_word = phrase

    # Check multi-word positives
    for phrase, score in STRONG_POSITIVES.items():
        if phrase in lower:
            if score > max_pos:
                max_pos = score
                pos_word = phrase

    # Check single-word tokens
    for tok in tokens:
        if tok in STRONG_NEGATIVES and abs(STRONG_NEGATIVES[tok]) > abs(max_neg):
            max_neg = STRONG_NEGATIVES[tok]
            neg_word = tok
        if tok in STRONG_POSITIVES and STRONG_POSITIVES[tok] > max_pos:
            max_pos = STRONG_POSITIVES[tok]
            pos_word = tok

    # Get VADER baseline
    vader = _analyzer.polarity_scores(clause)
    vader_compound = vader["compound"]

    # Determine final score
    if max_neg != 0.0 and max_pos != 0.0:
        # Both signals: if negation present, flip; otherwise it's mixed
        if has_negation:
            # e.g. "can't clean" — negation + positive word = negative
            compound = max_neg if max_neg != 0.0 else -max_pos
        else:
            # True mixed: "loud as hell but works"
            compound = 0.0
            label = "mixed"
            return compound, label, 0.6
    elif max_neg != 0.0:
        compound = max_neg
    elif max_pos != 0.0:
        if has_negation:
            compound = -max_pos
        else:
            compound = max_pos
    else:
        # Fall back to VADER
        compound = vader_compound

    # Derive label
    if compound >= 0.05:
        label = "positive"
    elif compound <= -0.05:
        label = "negative"
    else:
        label = "neutral"

    confidence = min(0.5 + abs(compound) * 0.5, 1.0)
    return compound, label, confidence


def _find_domain_terms_in_clause(clause: str) -> List[Tuple[str, str]]:
    """
    Find all domain terms in a clause. Returns list of (surface_form, canonical_name).
    Sorted longest match first to avoid partial matches.

    Also checks for underscore-joined canonical names (produced by the preprocessor
    when multi-word terms are merged, e.g. "basket_coating").
    """
    clause_lower = clause.lower()
    found = []
    seen_positions = set()

    # Build extended search list: original surface forms + underscore-joined canonicals
    search_terms = list(DOMAIN_TERMS.items())
    # Add underscore-joined forms (from preprocessor output)
    canonical_to_canonical = {v: v for v in DOMAIN_TERMS.values()}
    for canonical in canonical_to_canonical:
        if canonical not in DOMAIN_TERMS:  # avoid duplicates
            search_terms.append((canonical, canonical))

    sorted_terms = sorted(search_terms, key=lambda x: -len(x[0]))
    for surface, canonical in sorted_terms:
        for m in re.finditer(r"\b" + re.escape(surface) + r"\b", clause_lower):
            # Check for overlap with already-found terms
            pos = m.start()
            if not any(abs(pos - p) < len(surface) for p in seen_positions):
                found.append((surface, canonical))
                seen_positions.add(pos)
                break  # one hit per term per clause

    return found


def _apply_maintenance_context(text: str, results: Dict[str, dict]) -> Dict[str, dict]:
    """
    Apply semantic overrides for maintenance-related aspects.

    Patterns like "once you descale it weekly" / "needs replacing often" imply
    maintenance burden → negative, even if the surrounding clause is otherwise positive.
    """
    lower = text.lower()

    # Maintenance burden patterns: [action] + frequency/obligation context
    MAINTENANCE_ASPECTS = {"descaling", "hepa_filter", "prefilter", "replacement_part", "maintenance"}
    BURDEN_PATTERNS = [
        r"once you\s+\w+\s+it\s+(weekly|daily|monthly|often|regularly|every\s+\w+)",
        r"needs?\s+(replacing|cleaning|descaling|maintenance)\s+(way\s+too|too|very)",
        r"(descal|replac|clean)\w+\s+(takes?\s+forever|is\s+a\s+pain|gets?\s+old)",
        r"which\s+gets?\s+old\s+fast",
        r"replacement.{1,20}(too\s+often|frequent|expensive)",
    ]

    has_maintenance_burden = any(re.search(p, lower) for p in BURDEN_PATTERNS)

    if has_maintenance_burden:
        for aspect in MAINTENANCE_ASPECTS:
            if aspect in results and results[aspect]["polarity"] in ("positive", "neutral"):
                results[aspect] = {
                    **results[aspect],
                    "polarity": "negative",
                    "score": -0.4,
                    "confidence": 0.7,
                }

    # "needs replacing way too often" → negative for any aspect mentioned
    replacing_match = re.search(r"needs?\s+replacing\s+(way\s+too|too)\s+often", lower)
    if replacing_match:
        # Find what needs replacing — it's the subject before "needs"
        before = lower[:replacing_match.start()]
        for aspect in list(results.keys()):
            if aspect in before:
                results[aspect] = {**results[aspect], "polarity": "negative", "score": -0.5, "confidence": 0.75}

    return results


def extract_aspects(text: str, doc=None) -> List[dict]:
    """
    Main entry point. Clause-aware ABSA.
    Returns list of aspect dicts with keys: name, polarity, score, confidence, snippet.
    """
    results: Dict[str, dict] = {}

    # 1. Split into clauses and process each independently
    clauses = _split_into_clauses(text)

    for clause in clauses:
        terms = _find_domain_terms_in_clause(clause)
        if not terms:
            continue

        compound, label, confidence = _score_clause(clause)

        for surface, canonical in terms:
            # Use the highest-confidence result if aspect appears in multiple clauses
            if canonical not in results or confidence > results[canonical]["confidence"]:
                results[canonical] = {
                    "name": canonical,
                    "polarity": label,
                    "score": round(compound, 4),
                    "confidence": round(confidence, 3),
                    "snippet": clause.strip(),
                }

    # 2. Post-process: maintenance-type aspects that appear after "once you" / "if you" etc.
    #    are inherently negative (burden of maintenance)
    results = _apply_maintenance_context(text, results)

    # 3. If spaCy doc is available, try to improve scoring via dep-parse subtree
    if doc is not None and results:
        results = _refine_with_spacy(text, doc, results)

    # 4. Also scan full text for domain terms not found in clause split
    # (catches terms that appear in non-standard clause structures)
    text_lower = text.lower()
    sorted_terms = sorted(DOMAIN_TERMS.items(), key=lambda x: -len(x[0]))
    for surface, canonical in sorted_terms:
        if canonical in results:
            continue
        m = re.search(r"\b" + re.escape(surface) + r"\b", text_lower)
        if m:
            # Score a tight window around this term
            start = max(0, m.start() - 40)
            end = min(len(text), m.end() + 40)
            window = text[start:end]
            compound, label, confidence = _score_clause(window)
            results[canonical] = {
                "name": canonical,
                "polarity": label,
                "score": round(compound, 4),
                "confidence": round(confidence * 0.8, 3),  # lower conf for window
                "snippet": window.strip(),
            }

    return list(results.values())


_COPULAR_VERBS = {"be", "seem", "feel", "look", "sound", "remain", "become"}


def _refine_with_spacy(text: str, doc, results: Dict[str, dict]) -> Dict[str, dict]:
    """
    Use spaCy dep-parse to refine aspect scores where possible.
    Only updates results when spaCy subtree gives a clearer signal.

    Includes explicit copular construction handling: if an aspect token is
    the nsubj of a copular verb (be, seem, feel, etc.), collect the verb's
    acomp/attr/xcomp children as candidate opinion tokens for that aspect.
    """
    for token in doc:
        token_lower = token.text.lower()
        lemma_lower = token.lemma_.lower()
        canonical = DOMAIN_TERMS.get(token_lower) or DOMAIN_TERMS.get(lemma_lower)
        if not canonical:
            continue

        # Check for copular construction: aspect is nsubj of a copular verb
        # e.g. "The portafilter is solid" → portafilter -nsubj→ is -acomp→ solid
        opinion_tokens_from_copula = []
        if token.dep_ == "nsubj" and token.head.lemma_.lower() in _COPULAR_VERBS:
            copula_head = token.head
            for child in copula_head.children:
                if child.dep_ in ("acomp", "attr", "xcomp"):
                    opinion_tokens_from_copula.extend(list(child.subtree))

        if canonical not in results and not opinion_tokens_from_copula:
            continue

        if opinion_tokens_from_copula:
            copula_text = " ".join(t.text for t in opinion_tokens_from_copula)
            compound, label, confidence = _score_clause(copula_text)
            if canonical not in results:
                # New aspect discovered via copular walk
                results[canonical] = {
                    "name": canonical,
                    "polarity": label,
                    "score": round(compound, 4),
                    "confidence": round(confidence, 3),
                    "snippet": copula_text[:100],
                }
            else:
                current = results[canonical]
                if label != "neutral" and confidence > current["confidence"]:
                    results[canonical] = {
                        "name": canonical,
                        "polarity": label,
                        "score": round(compound, 4),
                        "confidence": round(confidence, 3),
                        "snippet": copula_text[:100],
                    }
            continue

        # Standard subtree walk
        subtree_tokens = list(token.subtree)
        subtree_text = " ".join(t.text for t in subtree_tokens)

        compound, label, confidence = _score_clause(subtree_text)

        # Only update if spaCy gives a more confident non-neutral result
        current = results[canonical]
        if (label != "neutral" and confidence > current["confidence"]
                and abs(compound) > abs(current["score"])):
            results[canonical] = {
                "name": canonical,
                "polarity": label,
                "score": round(compound, 4),
                "confidence": round(confidence, 3),
                "snippet": subtree_text[:100],
            }

    return results
