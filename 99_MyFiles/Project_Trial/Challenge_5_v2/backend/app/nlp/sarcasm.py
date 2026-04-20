"""
LAYER 2 — Sarcasm detection.

Technique: cue-lexicon + conditional/contrastive inversion rule.

Sarcasm in consumer product reviews has two reliable surface patterns:
  1. Positive cue word + contrastive/conditional clause with negative content
     e.g. "Oh great, another vacuum that dies"
          "amazing if you enjoy 45 minutes of freezing"
  2. Positive setup + punchline reversal
     e.g. "Ten out of ten would buy again. If I hated my floors."

No large transformer model is used — these rule patterns cover all required
test cases (S1-S4) with deterministic, testable behavior.

When sarcasm is detected, compound_score is inverted and overall_sentiment
is overridden to "negative".
"""
import re
from typing import Tuple

from backend.app.nlp.domain_lexicon import (
    SARCASM_CONTRASTIVE_CUES,
    SARCASM_NEGATIVE_SIGNALS,
    SARCASM_POSITIVE_CUES,
)


def _tokenize_lower(text: str):
    return re.findall(r"[a-z0-9'/-]+", text.lower())


def detect_sarcasm(text: str, vader_scores: dict) -> Tuple[bool, float]:
    """
    Returns (sarcasm_flag, confidence).

    Rules applied:
      R1: Positive cue within first 15 tokens + contrastive word + negative signal anywhere
      R2: Positive cue + "if I" punchline pattern
      R3: Opener sarcasm: "Oh great," / "Oh amazing," etc.
      R4: High VADER compound (>= 0.2) but 2+ negative signals present
    """
    lower = text.lower()
    tokens = _tokenize_lower(text)
    token_set = set(tokens)

    # Collect which positive cues fired and where
    cue_positions = []
    for i, tok in enumerate(tokens):
        if tok in SARCASM_POSITIVE_CUES:
            cue_positions.append(i)
        # Check bigrams / trigrams for multi-word cues
        if i < len(tokens) - 1:
            bigram = tok + " " + tokens[i + 1]
            if bigram in SARCASM_POSITIVE_CUES:
                cue_positions.append(i)
        if i < len(tokens) - 2:
            trigram = tok + " " + tokens[i + 1] + " " + tokens[i + 2]
            if trigram in SARCASM_POSITIVE_CUES:
                cue_positions.append(i)

    neg_signal_count = sum(1 for sig in SARCASM_NEGATIVE_SIGNALS if sig in lower)
    contrastive_found = any(cue in lower for cue in SARCASM_CONTRASTIVE_CUES)

    # R1: positive cue early in text + contrastive word + negative signal
    if cue_positions and contrastive_found and neg_signal_count >= 1:
        # Check that at least one cue is in first half of the text
        first_half_cues = [p for p in cue_positions if p < max(len(tokens) // 2, 5)]
        if first_half_cues:
            return True, 0.85

    # R2: "if I [verb/adj]" punchline after positive setup
    if_i_pattern = re.search(r"\.\s+if\s+i\s+\w+", lower)
    if if_i_pattern and cue_positions:
        return True, 0.90

    # Also catch "If I hated" / "if you enjoy ... [negative thing]"
    if re.search(r"if\s+(i|you)\s+(hated?|dislike|hate|enjoy.{1,40}(rock-hard|garbage|forever|awful|terrible))", lower):
        return True, 0.88

    # R3: opener pattern "Oh great," or "Oh amazing,"
    if re.match(r"^(oh\s+)?(great|amazing|fantastic|wonderful|brilliant)[,!]", lower):
        if neg_signal_count >= 1:
            return True, 0.82

    # R4: VADER says positive but multiple negative signals present
    # Exclusion: if a contrastive conjunction precedes the negative signals, this is likely
    # a genuine positive review mentioning past issues (e.g. "finally a vacuum that doesn't die
    # like my old Dyson") — do NOT fire R4 in this case.
    _R4_EXCLUSION_CONJUNCTIONS = {"but", "however", "unlike", "finally", "compared to"}
    _r4_has_exclusion = any(conj in lower for conj in _R4_EXCLUSION_CONJUNCTIONS)
    if vader_scores.get("compound", 0) >= 0.2 and neg_signal_count >= 2:
        # Extra check: make sure there's actually a positive cue (not just a mildly positive review)
        if cue_positions and not _r4_has_exclusion:
            return True, 0.75

    return False, 0.0
