"""
What-If Simulator endpoint — POST /api/simulate

Aaru-style: grounds LLM reasoning in real consumer mention data.
LLM calls ARE allowed in this path (contrast: forecast.py has a hard no-LLM fence).

Honesty label: overall_disclaimer MUST contain the literal string:
  "Simulated reaction based on LLM heuristic, not empirical behavior modeling."
Charter §6.2 greps for this string — missing = automatic FAIL.

Configuration:
  SIMULATION_LLM_API_KEY   — Anthropic or OpenAI API key (see .env.example)
  SIMULATION_LLM_PROVIDER  — "anthropic" (default) or "openai"
  SIMULATION_LLM_MODEL     — override model ID (optional, defaults below)
"""
import hashlib
import json
import os
import random
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple

from fastapi import APIRouter, Depends, HTTPException

from backend.app.scrapers.base import BaseScraper
from backend.app.scrapers import get_scraper
from backend.models.schemas import (
    MentionFilter,
    SimulatedSegment,
    SimulationRequest,
    SimulationResult,
    _SIMULATOR_DISCLAIMER,
)

router = APIRouter(prefix="/api/simulate", tags=["simulator"])

# ─────────────────────────────────────────────────────────────────────────────
# Simple in-process cache: (scenario_hash) → SimulationResult
# Prevents LLM cost blowup on repeated demo runs.
# ─────────────────────────────────────────────────────────────────────────────
_cache: Dict[str, SimulationResult] = {}

GROUNDING_MENTION_COUNT = 8   # how many real mentions to pass to the LLM
SIMULATION_TIMEOUT_SECS = 30
DEFAULT_ANTHROPIC_MODEL = "claude-haiku-4-5-20251001"   # fast + cheap for demo
DEFAULT_OPENAI_MODEL = "gpt-4o-mini"

# ─────────────────────────────────────────────────────────────────────────────
# Cache key
# ─────────────────────────────────────────────────────────────────────────────

def _cache_key(request: SimulationRequest) -> str:
    payload = {
        "scenario": request.scenario.strip().lower(),
        "product_model": (request.product_model or "").strip().lower(),
        "filter_context": request.filter_context.model_dump() if request.filter_context else None,
    }
    return hashlib.md5(json.dumps(payload, sort_keys=True, default=str).encode()).hexdigest()


# ─────────────────────────────────────────────────────────────────────────────
# LLM client helpers
# ─────────────────────────────────────────────────────────────────────────────

def _get_provider() -> str:
    return os.environ.get("SIMULATION_LLM_PROVIDER", "anthropic").lower().strip()


def _get_api_key() -> str:
    key = os.environ.get("SIMULATION_LLM_API_KEY", "")
    if not key:
        raise EnvironmentError(
            "SIMULATION_LLM_API_KEY is not set. "
            "Add it to your .env file — see backend/.env.example."
        )
    return key


def _call_anthropic(
    system_prompt: str,
    user_prompt: str,
    model: Optional[str] = None,
) -> Tuple[str, str, int]:
    """
    Call Anthropic Claude. Returns (response_text, model_id, tokens_consumed).
    Raises TimeoutError on timeout, RuntimeError on API error.
    """
    try:
        import anthropic
    except ImportError as e:
        raise ImportError(
            "anthropic package is required. Install with: pip install anthropic"
        ) from e

    api_key = _get_api_key()
    model_id = model or os.environ.get("SIMULATION_LLM_MODEL", DEFAULT_ANTHROPIC_MODEL)
    client = anthropic.Anthropic(api_key=api_key, timeout=SIMULATION_TIMEOUT_SECS)

    message = client.messages.create(
        model=model_id,
        max_tokens=1024,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )
    text = message.content[0].text if message.content else ""
    tokens = (message.usage.input_tokens or 0) + (message.usage.output_tokens or 0)
    return text, model_id, tokens


def _call_openai(
    system_prompt: str,
    user_prompt: str,
    model: Optional[str] = None,
) -> Tuple[str, str, int]:
    """
    Call OpenAI. Returns (response_text, model_id, tokens_consumed).
    """
    try:
        import openai
    except ImportError as e:
        raise ImportError(
            "openai package is required. Install with: pip install openai"
        ) from e

    api_key = _get_api_key()
    model_id = model or os.environ.get("SIMULATION_LLM_MODEL", DEFAULT_OPENAI_MODEL)
    client = openai.OpenAI(api_key=api_key, timeout=SIMULATION_TIMEOUT_SECS)

    response = client.chat.completions.create(
        model=model_id,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=1024,
    )
    text = response.choices[0].message.content or ""
    tokens = response.usage.total_tokens if response.usage else 0
    return text, model_id, tokens


def _call_llm(system_prompt: str, user_prompt: str) -> Tuple[str, str, int]:
    """Dispatch to configured LLM provider."""
    provider = _get_provider()
    if provider == "openai":
        return _call_openai(system_prompt, user_prompt)
    return _call_anthropic(system_prompt, user_prompt)


# ─────────────────────────────────────────────────────────────────────────────
# Prompt construction
# ─────────────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """\
You are a consumer insights analyst specializing in home appliances and consumer electronics. \
Your task is to simulate how different consumer segments would react to a hypothetical product \
or marketing scenario, grounded in real consumer review data provided to you.

You must:
1. Identify 3-5 distinct consumer segments relevant to this product and scenario
2. Predict each segment's reaction (positive/negative/mixed/neutral)
3. Ground each prediction in the actual review quotes provided — cite which quotes informed each segment
4. Write 2-3 sentences of plain-English narrative for each segment
5. Be honest about uncertainty — this is a simulation, not a measurement

Output your response as valid JSON matching this exact structure:
{
  "segments": [
    {
      "segment_label": "string — 3-7 word consumer segment description",
      "predicted_reaction": "positive" | "negative" | "mixed" | "neutral",
      "confidence_narrative": "string — 2-3 sentences explaining the predicted reaction",
      "key_quotes_used": ["quote1", "quote2"]
    }
  ]
}

Do not add any text outside the JSON object. Do not add markdown fences."""


def _build_user_prompt(
    scenario: str,
    product_model: Optional[str],
    grounding_mentions: list,
) -> str:
    product_context = f"Product: {product_model}\n" if product_model else ""
    mentions_text = "\n\n".join(
        f"[Review {i+1}]: {m.text[:300]}" for i, m in enumerate(grounding_mentions)
    )
    return (
        f"{product_context}"
        f"Scenario: {scenario}\n\n"
        f"--- Real consumer reviews for grounding ({len(grounding_mentions)} mentions) ---\n\n"
        f"{mentions_text}\n\n"
        f"---\n\n"
        f"Based on these real reviews, simulate how different consumer segments would react "
        f"to the scenario described above. Return JSON only."
    )


# ─────────────────────────────────────────────────────────────────────────────
# LLM response parser
# ─────────────────────────────────────────────────────────────────────────────

def _parse_llm_response(
    raw: str,
    grounding_mentions: list,
) -> List[SimulatedSegment]:
    """
    Parse JSON from LLM response into SimulatedSegment list.
    Falls back to a structured error segment on parse failure.
    """
    try:
        # Strip any accidental markdown fences
        text = raw.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])

        data = json.loads(text)
        segments_raw = data.get("segments") or []
        segments = []
        for s in segments_raw[:5]:  # cap at 5 per charter
            reaction = s.get("predicted_reaction", "neutral")
            if reaction not in ("positive", "negative", "mixed", "neutral"):
                reaction = "neutral"
            segments.append(SimulatedSegment(
                segment_label=str(s.get("segment_label", "Unknown segment")),
                predicted_reaction=reaction,
                confidence_narrative=str(s.get("confidence_narrative", "")),
                key_quotes_used=[str(q) for q in (s.get("key_quotes_used") or [])[:5]],
            ))
        if segments:
            return segments
    except (json.JSONDecodeError, KeyError, TypeError):
        pass

    # Fallback: return a single "parse error" segment
    return [SimulatedSegment(
        segment_label="Parse error — raw response attached",
        predicted_reaction="neutral",
        confidence_narrative=(
            "The LLM returned a response that could not be parsed as structured JSON. "
            "Raw response has been attached for inspection."
        ),
        key_quotes_used=[raw[:500]],
    )]


# ─────────────────────────────────────────────────────────────────────────────
# Grounding mention selection
# ─────────────────────────────────────────────────────────────────────────────

def _select_grounding_mentions(
    scraper: BaseScraper,
    product_model: Optional[str],
    filter_context: Optional[MentionFilter],
    count: int = GROUNDING_MENTION_COUNT,
) -> list:
    """
    Select N real mentions to ground the simulation.
    Prefers mentions matching product_model; falls back to all mentions.
    Selects a spread across positive/negative to give the LLM balanced context.
    """
    all_mentions = scraper.fetch(limit=10000, offset=0)

    # Apply product filter
    if product_model:
        candidates = [
            m for m in all_mentions
            if m.product_model and product_model.lower() in m.product_model.lower()
            and getattr(m, "record_type", "review") == "review"
        ]
    else:
        candidates = [
            m for m in all_mentions
            if getattr(m, "record_type", "review") == "review"
        ]

    # Apply filter_context brand/category if provided
    if filter_context:
        if filter_context.brand:
            candidates = [m for m in candidates if m.brand == filter_context.brand]
        if filter_context.category:
            candidates = [m for m in candidates if m.category == filter_context.category]

    if not candidates:
        candidates = [m for m in all_mentions if getattr(m, "record_type", "review") == "review"]

    if not candidates:
        return []

    # Sort by absolute sentiment to get a mix of strong positive + strong negative
    sorted_candidates = sorted(candidates, key=lambda m: abs(m.derived.compound_score), reverse=True)

    # Take top-scoring, then interleave pos/neg for balance
    top = sorted_candidates[:min(50, len(sorted_candidates))]
    positives = [m for m in top if m.derived.compound_score >= 0.05]
    negatives = [m for m in top if m.derived.compound_score <= -0.05]

    selected = []
    half = count // 2
    selected.extend(positives[:half])
    selected.extend(negatives[:half])

    # Fill remaining slots from leftovers if needed
    if len(selected) < count:
        remaining = [m for m in top if m not in selected]
        selected.extend(remaining[:count - len(selected)])

    random.shuffle(selected)
    return selected[:count]


# ─────────────────────────────────────────────────────────────────────────────
# Endpoint
# ─────────────────────────────────────────────────────────────────────────────

@router.post("", response_model=SimulationResult)
def run_simulation(
    request: SimulationRequest,
    scraper: BaseScraper = Depends(get_scraper),
) -> SimulationResult:
    """
    Simulate consumer segment reactions to a hypothetical scenario.

    Grounds the LLM in real mention data — passes 5-10 actual consumer reviews
    as context so the LLM reasons over observed consumer text, not product names alone.

    Caches by (scenario, product_model, filter_context_hash) to prevent cost blowup.
    Times out at 30 seconds with a structured error response.

    NOTE: This is a simulation, not a measurement. The overall_disclaimer field
    makes this explicit per charter §6.2 anti-theater requirements.
    """
    # Check cache first
    key = _cache_key(request)
    if key in _cache:
        return _cache[key]

    # Select grounding mentions
    grounding_mentions = _select_grounding_mentions(
        scraper, request.product_model, request.filter_context
    )

    # Build prompts
    user_prompt = _build_user_prompt(
        request.scenario,
        request.product_model,
        grounding_mentions,
    )

    # Call LLM with timeout handling
    try:
        raw_response, model_id, tokens = _call_llm(SYSTEM_PROMPT, user_prompt)
    except EnvironmentError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except ImportError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        err_str = str(e).lower()
        if "timeout" in err_str or "timed out" in err_str or "time" in err_str:
            raise HTTPException(
                status_code=504,
                detail=(
                    "Simulation timed out after 30 seconds. "
                    "Try a more specific scenario or a smaller product filter."
                ),
            )
        raise HTTPException(status_code=502, detail=f"LLM error: {str(e)}")

    # Parse response
    segments = _parse_llm_response(raw_response, grounding_mentions)

    result = SimulationResult(
        scenario=request.scenario,
        product_model=request.product_model,
        segments=segments,
        overall_disclaimer=_SIMULATOR_DISCLAIMER,
        model_used=model_id,
        tokens_consumed=tokens,
    )

    # Cache and return
    _cache[key] = result
    return result
