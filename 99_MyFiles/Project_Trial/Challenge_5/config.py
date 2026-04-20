"""
Global configuration for SharkNinja Consumer Sentiment Dashboard.
"""

import os

# ---------------------------------------------------------------------------
# Product taxonomy
# ---------------------------------------------------------------------------

PRODUCT_CATEGORIES = {
    "robot_vacuum": "Robot Vacuum",
    "stick_vacuum": "Stick Vacuum",
    "hair_dryer": "Hair Dryer",
    "air_fryer": "Air Fryer",
    "blender": "Blender",
    "coffee_maker": "Coffee Maker",
}

BRANDS = {
    "shark": "Shark",
    "ninja": "Ninja",
}

# Maps each brand to the categories it owns
BRAND_CATEGORY_MAP = {
    "shark": ["robot_vacuum", "stick_vacuum", "hair_dryer"],
    "ninja": ["air_fryer", "blender", "coffee_maker"],
}

PLATFORMS = {
    "reddit": "Reddit",
    "amazon": "Amazon",
    "tiktok": "TikTok",
}

# ---------------------------------------------------------------------------
# Specific product model names (realistic SharkNinja naming conventions)
# ---------------------------------------------------------------------------

PRODUCT_NAMES = {
    "robot_vacuum": [
        "Shark AI Ultra Robot Vacuum RV2502WD",
        "Shark IQ Robot Self-Empty XL RV1001AE",
        "Shark Matrix Robot Vacuum RV2310WD",
        "Shark AI VACMOP Pro Robotic AV2001WD",
    ],
    "stick_vacuum": [
        "Shark Stratos Cordless IX141",
        "Shark Vertex DuoClean PowerFins IZ462H",
        "Shark Rocket Ultra-Light HV302",
        "Shark Anti Hair Wrap IZ320UKT",
    ],
    "hair_dryer": [
        "Shark HyperAIR Blow Dryer HD430",
        "Shark FlexStyle Air Styling & Drying System HD435",
        "Shark SmoothStyle Heated Comb & Straightener HT202",
        "Shark HyperAIR Speed Dryer HD110",
    ],
    "air_fryer": [
        "Ninja Foodi 6-in-1 DualZone Air Fryer DZ201",
        "Ninja Air Fryer Max XL AF161",
        "Ninja Foodi Smart XL 6-in-1 Indoor Grill AG651",
        "Ninja Speedi 10-in-1 Rapid Cooker SF301",
    ],
    "blender": [
        "Ninja Professional Plus Blender BN701",
        "Ninja Foodi Power Nutri Duo SS201",
        "Ninja Detect Kitchen System Power Blender TB401",
        "Ninja Blast Portable Blender BC151",
    ],
    "coffee_maker": [
        "Ninja DualBrew Pro CFP301",
        "Ninja Specialty Coffee Maker CM401",
        "Ninja Hot & Iced XL Coffee Maker CP307",
        "Ninja Luxe Cafe Premier System CFN701",
    ],
}

# ---------------------------------------------------------------------------
# Dashboard visual identity
# ---------------------------------------------------------------------------

COLOR_SCHEME = {
    "primary": "#00B4D8",
    "secondary": "#0077B6",
    "positive": "#2EC4B6",
    "negative": "#E63946",
    "neutral": "#8D99AE",
    "shark": "#0096C7",
    "ninja": "#F4A261",
    "background": "#0E1117",
    "surface": "#1A1F2E",
    "text": "#FAFAFA",
    "text_muted": "#8D99AE",
    "grid": "#2A2F3E",
    "reddit": "#FF4500",
    "amazon": "#FF9900",
    "tiktok": "#69C9D0",
}

# ---------------------------------------------------------------------------
# Sentiment classification thresholds (VADER compound score)
# ---------------------------------------------------------------------------

SENTIMENT_THRESHOLDS = {
    "positive": 0.2,
    "negative": -0.2,
}

# ---------------------------------------------------------------------------
# File system
# ---------------------------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data", "sample")
