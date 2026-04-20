"""
Consumer-electronics domain lexicon.

DOMAIN_TERMS maps surface forms (lowercased) to canonical aspect names.
The canonical names are used throughout the NLP pipeline and in API responses.
Terms listed here are protected from being treated as stopwords or unknown
tokens during tokenization and POS tagging.

Multi-word terms (e.g. "self-empty base") must be handled by the pipeline's
preprocessor before spaCy tokenization.
"""
from typing import Dict, List, Set

# ---------------------------------------------------------------------------
# Primary mapping: surface form -> canonical aspect name
# ---------------------------------------------------------------------------
DOMAIN_TERMS: Dict[str, str] = {
    # --- Vacuums ---
    "suction": "suction",
    "brushroll": "brushroll",
    "brush roll": "brushroll",
    "dustbin": "dustbin",
    "dust bin": "dustbin",
    "dustcup": "dustbin",
    "dust cup": "dustbin",
    "hepa": "hepa_filter",
    "hepa filter": "hepa_filter",
    "cyclonic": "cyclonic_suction",
    "cyclone": "cyclonic_suction",
    "agitator": "agitator",
    "agitator bar": "agitator",
    "roller": "roller",
    "canister": "canister",
    "self-empty": "self_empty_base",
    "self empty": "self_empty_base",
    "self-emptying": "self_empty_base",
    "self emptying": "self_empty_base",
    "self-empty base": "self_empty_base",
    "auto-empty": "self_empty_base",
    "mop pad": "mop_pad",
    "mopping pad": "mop_pad",
    "edge cleaning": "edge_cleaning",
    "tangle": "tangle",
    "tangling": "tangle",
    "navigation": "navigation",
    "lidar": "lidar",
    "mapping": "mapping",
    "obstacle avoidance": "navigation",
    "docking": "charging_dock",
    # --- Kitchen / Air Fryer ---
    "basket": "basket",
    "basket coating": "basket_coating",
    "nonstick": "nonstick_coating",
    "non-stick": "nonstick_coating",
    "crisper plate": "crisper_plate",
    "crisping plate": "crisper_plate",
    "dual zone": "dual_zone",
    "dualzone": "dual_zone",
    "preset": "preset",
    "heating element": "heating_element",
    "blade assembly": "blade_assembly",
    "pitcher": "pitcher",
    "tamper": "tamper",
    "cooking performance": "cooking_performance",
    # --- Coffee ---
    "carafe": "carafe",
    "descale": "descaling",
    "descaling": "descaling",
    "descaler": "descaling",
    "pod": "pod_compartment",
    "pod compartment": "pod_compartment",
    "steam wand": "steam_wand",
    "portafilter": "portafilter",
    "bean hopper": "bean_hopper",
    "grinder": "grinder",
    "burr grinder": "grinder",
    "crema": "crema",
    "brew": "brew_speed",
    "brew speed": "brew_speed",
    "brewing": "brew_speed",
    "shot quality": "shot_quality",
    "coffee quality": "coffee_quality",
    "coffee": "coffee_quality",
    "espresso": "shot_quality",
    "cooks": "cooking_performance",
    "cooking": "cooking_performance",
    # --- Air Care ---
    "prefilter": "prefilter",
    "pre-filter": "prefilter",
    "cadr": "cadr",
    "ionizer": "ionizer",
    "activated carbon": "activated_carbon",
    # --- Hair Tools ---
    "barrel": "barrel",
    "plate": "plate",
    "heat setting": "heat_setting",
    "ionic": "ionic",
    # --- General / Universal ---
    "warranty": "warranty",
    "app": "app",
    "firmware": "firmware",
    "battery": "battery",
    "runtime": "battery",
    "battery life": "battery",
    "run time": "battery",
    "charging dock": "charging_dock",
    "charging base": "charging_dock",
    "replacement part": "replacement_part",
    "noise": "noise",
    "loud": "noise",
    "loudness": "noise",
    "price": "price",
    "cost": "price",
    "maintenance": "maintenance",
    "durability": "durability",
    "build quality": "durability",
}

# ---------------------------------------------------------------------------
# Multi-word terms (those containing a space or hyphen) — ordered longest first
# so the preprocessor replaces the most specific match first.
# ---------------------------------------------------------------------------
MULTIWORD_TERMS: List[tuple] = sorted(
    [(surface, canonical) for surface, canonical in DOMAIN_TERMS.items() if " " in surface or "-" in surface],
    key=lambda x: -len(x[0]),
)

# ---------------------------------------------------------------------------
# All canonical aspect names — used for normalization validation
# ---------------------------------------------------------------------------
CANONICAL_ASPECTS: Set[str] = set(DOMAIN_TERMS.values())

# ---------------------------------------------------------------------------
# Brand surface-form aliases -> canonical brand string
# Used by comparative.py to detect brand mentions in text
# ---------------------------------------------------------------------------
BRAND_ALIASES: Dict[str, str] = {
    # Shark
    "shark": "shark",
    "shark matrix": "shark",
    "shark iq": "shark",
    "powerdetect": "shark",
    "shark powerdetect": "shark",
    "sharkninja": "shark",
    # Ninja
    "ninja": "ninja",
    "ninja foodi": "ninja",
    "foodi": "ninja",
    "ninja creami": "ninja",
    "creami": "ninja",
    "ninja coffee bar": "ninja",
    "ninja espresso": "ninja",
    "ninja coffee": "ninja",
    # Dyson
    "dyson": "dyson",
    "dyson v": "dyson",
    # iRobot
    "irobot": "irobot",
    "roomba": "irobot",
    "i-robot": "irobot",
    # Roborock
    "roborock": "roborock",
    # KitchenAid
    "kitchenaid": "kitchenaid",
    "kitchen aid": "kitchenaid",
    # Breville
    "breville": "breville",
    # Cuisinart
    "cuisinart": "cuisinart",
    # Keurig
    "keurig": "keurig",
    # De'Longhi
    "delonghi": "delonghi",
    "de'longhi": "delonghi",
    "de longhi": "delonghi",
}

# ---------------------------------------------------------------------------
# Sarcasm detection lexicons
# ---------------------------------------------------------------------------
SARCASM_POSITIVE_CUES: Set[str] = {
    "great", "amazing", "fantastic", "love", "loving", "revolutionary",
    "incredible", "perfect", "ten out of ten", "10/10", "wow", "wonderful",
    "brilliant", "excellent", "superb", "outstanding", "best",
    "so good", "so great", "really great", "just great",
}

SARCASM_NEGATIVE_SIGNALS: Set[str] = {
    "dies", "dead", "jammed", "jam", "hated", "hate", "flaking", "garbage",
    "broke", "broken", "worst", "terrible", "awful", "useless", "horrible",
    "disgusting", "pathetic", "disaster", "nightmare", "ridiculous",
    "waste", "regret", "disappointed", "disappointing", "frustrating",
    "can't", "cant", "cannot", "doesn't", "doesnt", "doesn't work", "stopped working",
    "rock-hard", "impossible", "forever", "crush",
}

# Conditional/contrastive words that introduce the punchline in sarcasm
SARCASM_CONTRASTIVE_CUES: Set[str] = {
    "if", "but", "except", "unless", "however", "although", "though",
    "after", "once you", "as long as", "provided",
}
