"""
generate_fixtures.py — Expanded CSV fixture generator for the SharkNinja sentiment dashboard.

Produces:
  backend/data/reviews_shark.csv         (Shark SKUs: Matrix, IQ, PowerDetect UV Reveal, Navigator)
  backend/data/reviews_ninja.csv         (Ninja SKUs: Foodi DualZone, Creami, Espresso Bar, Coffee Bar)
  backend/data/reviews_competitors.csv   (Competitors: Dyson V15, iRobot Roomba j7+, Roborock S8, KitchenAid Pro)

Total: ≥300 rows across ≥12 SKUs, all 5 platforms, 60-day timestamp spread.

Special requirements:
  - Preserves the original 16 edge-case rows verbatim (rows 1-25 of shark CSV, etc.)
  - Includes ~5 novelty-seed rows: "charging dock LED flickering" cluster with first_seen_at within last 14 days
  - Each SKU has ≥5 aspect mentions
  - PowerDetect UV Reveal has ≥6 aspects with double-digit mention counts

Run:
  python backend/scripts/generate_fixtures.py

from the project root directory.
"""

import csv
import os
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Date helpers
# ---------------------------------------------------------------------------

NOW = datetime(2026, 4, 11, 12, 0, 0, tzinfo=timezone.utc)
BASE = NOW - timedelta(days=60)


def dt(days_ago: float, hour: int = 12, minute: int = 0) -> str:
    """Return ISO timestamp string for NOW - days_ago."""
    ts = NOW - timedelta(days=days_ago, hours=-(hour - 12))
    ts = ts.replace(minute=minute, second=0, microsecond=0)
    return ts.strftime("%Y-%m-%dT%H:%M:%SZ")


def uid(prefix: str) -> str:
    return f"{prefix}-{str(uuid.uuid4())[:8]}"


# ---------------------------------------------------------------------------
# Column headers (matches existing CSVs)
# ---------------------------------------------------------------------------

HEADERS = [
    "mention_id", "source_platform", "source_url", "author_handle",
    "posted_at", "ingested_at", "brand", "category", "product_model",
    "text", "rating", "language", "topic_id",
]

PLATFORMS = ["reddit", "amazon", "youtube", "trustpilot", "twitter"]


# ---------------------------------------------------------------------------
# Edge-case rows preserved verbatim from original CSVs (all 16 must remain)
# These match requirements.md §3 exactly.
# ---------------------------------------------------------------------------

SHARK_EDGE_CASES = [
    # Row 1: sarcasm S1
    ["a1b2c3d4-0001-4000-8000-000000000001", "reddit", "https://reddit.com/r/VacuumCleaners/comments/abc1",
     "u/VacuumFanatic", "2026-03-15T14:23:00Z", "2026-03-15T15:00:00Z",
     "shark", "robot_vacuum", "PowerDetect UV Reveal",
     "Oh great, another vacuum that dies after 3 months. Loving the warranty process.",
     "1", "en", "sarcasm_negative"],
    # Row 2: ABSA A1
    ["a1b2c3d4-0002-4000-8000-000000000002", "amazon", "https://amazon.com/review/R001",
     "AmazonReviewer1", "2026-03-18T09:45:00Z", "2026-03-18T10:00:00Z",
     "shark", "robot_vacuum", "PowerDetect UV Reveal",
     "Suction is incredible but the dustbin is tiny and the battery is garbage.",
     "2", "en", "absa_mixed"],
    # Row 3: comparative C1
    ["a1b2c3d4-0003-4000-8000-000000000003", "reddit", "https://reddit.com/r/SharkVacuums/comments/abc3",
     "u/CleanFreak", "2026-03-20T16:30:00Z", "2026-03-20T17:00:00Z",
     "shark", "robot_vacuum", "Shark Matrix",
     "Switched from iRobot to Shark Matrix and honestly I regret it. The iRobot was smarter at mapping.",
     "2", "en", "comparative"],
    # Row 4: domain D1
    ["a1b2c3d4-0004-4000-8000-000000000004", "trustpilot", "https://trustpilot.com/review/shark/001",
     "TPReviewer1", "2026-03-22T11:00:00Z", "2026-03-22T11:30:00Z",
     "shark", "robot_vacuum", "PowerDetect UV Reveal",
     "The HEPA filter needs replacing way too often and the brushroll tangles on long hair.",
     "2", "en", "domain_terms"],
    # Row 5: comparative C2
    ["a1b2c3d4-0005-4000-8000-000000000005", "amazon", "https://amazon.com/review/R005",
     "AmazonReviewer5", "2026-03-25T13:20:00Z", "2026-03-25T14:00:00Z",
     "shark", "cordless_stick", "PowerDetect",
     "Shark is way better than Dyson at edge cleaning.",
     "5", "en", "comparative"],
    # Row 6: ABSA A2
    ["a1b2c3d4-0006-4000-8000-000000000006", "youtube", "https://youtube.com/watch?v=abc006&lc=001",
     "YTCommenter1", "2026-03-28T18:45:00Z", "2026-03-28T19:00:00Z",
     "shark", "robot_vacuum", "Shark Matrix",
     "App is a mess, navigation is incredible, and the self-empty base is loud as hell but works.",
     "3", "en", "absa_mixed"],
    # Row 7: genuine positive
    ["a1b2c3d4-0007-4000-8000-000000000007", "reddit", "https://reddit.com/r/VacuumCleaners/comments/abc7",
     "u/HomeCleaner99", "2026-04-01T10:15:00Z", "2026-04-01T10:30:00Z",
     "shark", "robot_vacuum", "PowerDetect UV Reveal",
     "Finally a vacuum that doesn't die or jam like my old Dyson — the suction is great and the brushroll doesn't tangle",
     "5", "en", "genuine_positive"],
    # Row 8: product feature positive
    ["a1b2c3d4-0008-4000-8000-000000000008", "amazon", "https://amazon.com/review/R008",
     "AmazonReviewer8", "2026-04-02T08:30:00Z", "2026-04-02T09:00:00Z",
     "shark", "robot_vacuum", "PowerDetect UV Reveal",
     "The UV reveal feature is genuinely useful — can finally see where the dust actually is. Suction power is impressive.",
     "5", "en", "product_feature"],
    # Row 9: navigation issue
    ["a1b2c3d4-0009-4000-8000-000000000009", "trustpilot", "https://trustpilot.com/review/shark/009",
     "TPReviewer9", "2026-04-03T14:00:00Z", "2026-04-03T14:30:00Z",
     "shark", "robot_vacuum", "Shark Matrix",
     "Navigation keeps getting stuck in corners and the mapping resets every few days. Really frustrating.",
     "2", "en", "navigation_issue"],
    # Row 10: domain D2
    ["a1b2c3d4-0010-4000-8000-000000000010", "reddit", "https://reddit.com/r/SharkVacuums/comments/abc10",
     "u/PetHairProblems", "2026-04-04T19:45:00Z", "2026-04-04T20:00:00Z",
     "shark", "robot_vacuum", "PowerDetect UV Reveal",
     "The agitator bar picks up pet hair but the roller stops spinning when you hit a rug edge.",
     "3", "en", "domain_terms"],
    # Row 11: battery positive
    ["a1b2c3d4-0011-4000-8000-000000000011", "amazon", "https://amazon.com/review/R011",
     "AmazonReviewer11", "2026-04-05T11:20:00Z", "2026-04-05T12:00:00Z",
     "shark", "cordless_stick", "PowerDetect",
     "Battery life has really improved from the previous model. Gets about 40 minutes on standard mode.",
     "4", "en", "battery_positive"],
    # Row 12: Navigator feedback
    ["a1b2c3d4-0012-4000-8000-000000000012", "reddit", "https://reddit.com/r/HomeImprovement/comments/abc12",
     "u/DIYDave", "2026-04-05T21:30:00Z", "2026-04-05T22:00:00Z",
     "shark", "upright", "Shark Navigator",
     "The Shark Navigator is solid for hardwood floors but struggles with thick carpets.",
     "3", "en", "product_feedback"],
    # Row 13: ABSA A3
    ["a1b2c3d4-0013-4000-8000-000000000013", "youtube", "https://youtube.com/watch?v=abc013&lc=002",
     "YTCommenter2", "2026-04-06T10:00:00Z", "2026-04-06T10:30:00Z",
     "shark", "robot_vacuum", "Shark Matrix",
     "Self-empty base works great and the HEPA filtration is excellent. Only complaint is the app is buggy.",
     "4", "en", "absa_positive"],
    # Row 14: mop issue
    ["a1b2c3d4-0014-4000-8000-000000000014", "amazon", "https://amazon.com/review/R014",
     "AmazonReviewer14", "2026-04-07T15:45:00Z", "2026-04-07T16:00:00Z",
     "shark", "robot_vacuum", "PowerDetect UV Reveal",
     "Mopping pad leaves streaks on hardwood. The vacuum function is excellent but the mop is disappointing.",
     "2", "en", "mop_issue"],
    # Row 15: sarcasm S2
    ["a1b2c3d4-0015-4000-8000-000000000015", "trustpilot", "https://trustpilot.com/review/shark/015",
     "TPReviewer15", "2026-04-07T17:00:00Z", "2026-04-07T17:30:00Z",
     "shark", "cordless_stick", "PowerDetect",
     "Ten out of ten would buy again. If I hated my floors.",
     "1", "en", "sarcasm_negative"],
    # Row 16: Lidar positive
    ["a1b2c3d4-0016-4000-8000-000000000016", "reddit", "https://reddit.com/r/VacuumCleaners/comments/abc16",
     "u/TechReviewer", "2026-04-08T09:30:00Z", "2026-04-08T10:00:00Z",
     "shark", "robot_vacuum", "Shark IQ",
     "Lidar navigation is precise and obstacle avoidance works well. The dustbin could be larger though.",
     "4", "en", "navigation_positive"],
    # Rows 17-25: additional originals kept verbatim
    ["a1b2c3d4-0017-4000-8000-000000000017", "amazon", "https://amazon.com/review/R017",
     "AmazonReviewer17", "2026-04-08T13:00:00Z", "2026-04-08T13:30:00Z",
     "shark", "robot_vacuum", "PowerDetect UV Reveal",
     "Charging dock fits perfectly in the corner and the robot returns reliably. Very happy with this purchase.",
     "5", "en", "general_positive"],
    ["a1b2c3d4-0018-4000-8000-000000000018", "reddit", "https://reddit.com/r/SharkVacuums/comments/abc18",
     "u/FrustratatedUser", "2026-04-08T20:15:00Z", "2026-04-08T20:30:00Z",
     "shark", "robot_vacuum", "Shark Matrix",
     "Firmware update broke the scheduling feature. Had to factory reset twice. Terrible software quality.",
     "1", "en", "firmware_issue"],
    ["a1b2c3d4-0019-4000-8000-000000000019", "youtube", "https://youtube.com/watch?v=abc019&lc=003",
     "YTCommenter3", "2026-04-09T11:30:00Z", "2026-04-09T12:00:00Z",
     "shark", "robot_vacuum", "PowerDetect UV Reveal",
     "The cyclonic suction on this model is impressive. Pet hair, debris, even cereal — it handles everything.",
     "5", "en", "suction_positive"],
    ["a1b2c3d4-0020-4000-8000-000000000020", "amazon", "https://amazon.com/review/R020",
     "AmazonReviewer20", "2026-04-09T16:45:00Z", "2026-04-09T17:00:00Z",
     "shark", "robot_vacuum", "Shark Matrix",
     "Warranty claim process took 6 weeks. Customer service was unresponsive. The vacuum itself is fine but the support is awful.",
     "2", "en", "warranty_issue"],
    ["a1b2c3d4-0021-4000-8000-000000000021", "trustpilot", "https://trustpilot.com/review/shark/021",
     "TPReviewer21", "2026-04-10T10:00:00Z", "2026-04-10T10:30:00Z",
     "shark", "cordless_stick", "PowerDetect",
     "Brushroll is easy to clean and replacement parts are affordable. Great value for money.",
     "4", "en", "maintenance_positive"],
    ["a1b2c3d4-0022-4000-8000-000000000022", "reddit", "https://reddit.com/r/HomeImprovement/comments/abc22",
     "u/CleanHomeDaily", "2026-04-10T14:30:00Z", "2026-04-10T15:00:00Z",
     "shark", "robot_vacuum", "PowerDetect UV Reveal",
     "After 6 months of daily use the suction is still as strong as day one. Build quality is excellent.",
     "5", "en", "durability_positive"],
    ["a1b2c3d4-0023-4000-8000-000000000023", "amazon", "https://amazon.com/review/R023",
     "AmazonReviewer23", "2026-04-10T17:00:00Z", "2026-04-10T17:30:00Z",
     "shark", "robot_vacuum", "Shark Matrix",
     "The app crashes constantly on Android. Navigation is good but I can't set schedules reliably.",
     "2", "en", "app_issue"],
    ["a1b2c3d4-0024-4000-8000-000000000024", "youtube", "https://youtube.com/watch?v=abc024&lc=004",
     "YTCommenter4", "2026-04-11T09:00:00Z", "2026-04-11T09:30:00Z",
     "shark", "robot_vacuum", "PowerDetect UV Reveal",
     "Price is high but the performance justifies it. Best robot vacuum I've owned in 10 years.",
     "5", "en", "price_value"],
    ["a1b2c3d4-0025-4000-8000-000000000025", "reddit", "https://reddit.com/r/VacuumCleaners/comments/abc25",
     "u/BudgetShopper", "2026-04-11T12:00:00Z", "2026-04-11T12:30:00Z",
     "shark", "robot_vacuum", "Shark IQ",
     "For the price it's decent but don't expect PowerDetect-level performance. Navigation is basic.",
     "3", "en", "price_comparison"],
]


# ---------------------------------------------------------------------------
# Synthetic expanded rows
# ---------------------------------------------------------------------------

def make_row(platform, brand, category, sku, text, rating, topic, days_ago, idx, hour=12):
    mid = f"gen-{brand[:3]}-{idx:04d}-{str(uuid.uuid4())[:8]}"
    posted = dt(days_ago, hour)
    ingested = dt(days_ago - 0.1, hour + 1)
    url_map = {
        "reddit": f"https://reddit.com/r/sharkninja/comments/gen{idx}",
        "amazon": f"https://amazon.com/review/GEN{idx:04d}",
        "youtube": f"https://youtube.com/watch?v=gen{idx:04d}&lc=001",
        "trustpilot": f"https://trustpilot.com/review/{brand}/gen{idx}",
        "twitter": f"https://twitter.com/user/status/gen{idx}",
    }
    handle_map = {
        "reddit": f"u/GenUser{idx}",
        "amazon": f"AmazonGenReviewer{idx}",
        "youtube": f"YTGenCommenter{idx}",
        "trustpilot": f"TPGenReviewer{idx}",
        "twitter": f"@GenTweetUser{idx}",
    }
    return [
        mid, platform, url_map[platform], handle_map[platform],
        posted, ingested,
        brand, category, sku,
        text, str(rating), "en", topic,
    ]


# ---------------------------------------------------------------------------
# Shark expanded rows
# ---------------------------------------------------------------------------

SHARK_EXPANDED = []
idx = 100

# PowerDetect UV Reveal — needs ≥6 aspects with double-digit counts
# Aspects: suction, battery, navigation, app, noise, durability, mop, brushroll, filter, dock
powerdetect_texts = [
    # suction (15+ mentions)
    ("Suction power on the PowerDetect is absolutely insane — picked up a whole pile of debris in one pass.", 5, "suction", "reddit", "robot_vacuum"),
    ("I'm shocked by the suction strength. Cleared my shaggy rug with zero effort.", 5, "suction", "amazon", "robot_vacuum"),
    ("Suction never drops even on thick carpet. Miles ahead of my old Roomba.", 5, "suction", "trustpilot", "robot_vacuum"),
    ("The suction on this thing is no joke. Best I've tested in this price range.", 5, "suction", "youtube", "robot_vacuum"),
    ("Noticed suction is weaker after 3 months. Might be filter clog but still concerning.", 3, "suction", "reddit", "robot_vacuum"),
    ("Suction is powerful but loud — sounds like a jet engine on max mode.", 4, "suction", "amazon", "robot_vacuum"),
    ("Insane suction on hardwood. Not as impressive on carpet but still good.", 4, "suction", "twitter", "robot_vacuum"),
    ("Suction lost power after dustbin got full. Learned to empty it more often.", 3, "suction", "reddit", "robot_vacuum"),
    ("Best suction I've seen on a robot vacuum under $500. Genuinely impressed.", 5, "suction", "youtube", "robot_vacuum"),
    ("Suction worked perfectly on pet hair. Golden retriever owner approved.", 5, "suction", "trustpilot", "robot_vacuum"),
    ("The suction is strong but the filter needs cleaning weekly to maintain it.", 3, "suction", "amazon", "robot_vacuum"),
    ("PowerDetect suction is noticeably better than the standard Shark Matrix.", 5, "suction", "reddit", "robot_vacuum"),
    ("Suction on high mode is incredible. Normal mode is sufficient for daily cleaning.", 5, "suction", "trustpilot", "robot_vacuum"),
    ("Suction keeps the house genuinely clean without me having to touch a mop.", 5, "suction", "youtube", "robot_vacuum"),
    ("Lost suction after 2 months. Warranty process was a nightmare. Not impressed.", 2, "suction", "amazon", "robot_vacuum"),

    # battery (12+ mentions)
    ("Battery lasts a full 90 minutes on standard mode. Covers my entire house.", 5, "battery", "reddit", "robot_vacuum"),
    ("Battery dies after 45 minutes on max suction. Fine for daily runs, not deep cleans.", 3, "battery", "amazon", "robot_vacuum"),
    ("Charging time is only 3 hours which is way better than competing models.", 4, "battery", "trustpilot", "robot_vacuum"),
    ("Battery health dropped visibly after 6 months of daily use.", 2, "battery", "reddit", "robot_vacuum"),
    ("Battery lasts longer than advertised in my testing. Impressed.", 5, "battery", "youtube", "robot_vacuum"),
    ("Battery indicator in app is accurate and gives good advance warning.", 4, "battery", "amazon", "robot_vacuum"),
    ("Battery drains faster when mopping simultaneously. Expected but worth noting.", 3, "battery", "twitter", "robot_vacuum"),
    ("Battery capacity is the weak link on an otherwise excellent machine.", 3, "battery", "trustpilot", "robot_vacuum"),
    ("Love the auto-recharge and resume feature. Battery management is smart.", 5, "battery", "reddit", "robot_vacuum"),
    ("Battery lasts long enough to clean my 2000sqft house in one go.", 5, "battery", "amazon", "robot_vacuum"),
    ("After 1 year the battery holds maybe 60% of original charge. Expected degradation.", 3, "battery", "youtube", "robot_vacuum"),
    ("Battery replacement is expensive. Wish Shark sold them at a more reasonable price.", 2, "battery", "trustpilot", "robot_vacuum"),

    # navigation (12+ mentions)
    ("Navigation maps the house incredibly fast on first run. Lidar is impressive.", 5, "navigation", "reddit", "robot_vacuum"),
    ("Navigation gets confused near glass doors. Workaround is to put a virtual wall.", 3, "navigation", "amazon", "robot_vacuum"),
    ("Obstacle avoidance saved my charging cables more than once. Very precise.", 5, "navigation", "trustpilot", "robot_vacuum"),
    ("Mapping restarted after firmware update. Very frustrating to re-train.", 2, "navigation", "reddit", "robot_vacuum"),
    ("Navigation around furniture is smooth and intelligent. Rarely gets stuck.", 5, "navigation", "youtube", "robot_vacuum"),
    ("No issues with stair avoidance even when I removed the sensors temporarily.", 5, "navigation", "amazon", "robot_vacuum"),
    ("Multi-floor mapping works but switching between floors is cumbersome in the app.", 3, "navigation", "twitter", "robot_vacuum"),
    ("Navigation is methodical and covers every corner unlike older random-path models.", 5, "navigation", "reddit", "robot_vacuum"),
    ("Gets stuck under my low-clearance couch despite the height specs saying it fits.", 2, "navigation", "trustpilot", "robot_vacuum"),
    ("Returns to dock 100% of the time even in a dark room. Impressive.", 5, "navigation", "youtube", "robot_vacuum"),
    ("Navigation accuracy improved noticeably after the 3.2 firmware update.", 4, "navigation", "amazon", "robot_vacuum"),
    ("Navigation is slower in rooms with lots of furniture but never fails to complete.", 4, "navigation", "reddit", "robot_vacuum"),

    # app (12+ mentions)
    ("The app is polished and easy to use. Scheduling works perfectly.", 5, "app", "reddit", "robot_vacuum"),
    ("App crashed twice during setup. Reinstalling fixed it but left a bad first impression.", 2, "app", "amazon", "robot_vacuum"),
    ("Alexa integration through the app works flawlessly. 'Alexa, start cleaning'.", 5, "app", "trustpilot", "robot_vacuum"),
    ("App UI is clean but the room naming feature is buried in menus.", 3, "app", "youtube", "robot_vacuum"),
    ("App doesn't support Android 14 properly. Buttons are cut off on my Pixel 8.", 2, "app", "reddit", "robot_vacuum"),
    ("Love the real-time map view in the app. Can watch the robot's progress live.", 5, "app", "twitter", "robot_vacuum"),
    ("App notifications are overzealous. Every cleaning sends 5 push alerts.", 2, "app", "amazon", "robot_vacuum"),
    ("The weekly schedule feature in the app finally convinced me to stay consistent.", 5, "app", "trustpilot", "robot_vacuum"),
    ("App is basic but functional. Does everything you need without bloat.", 4, "app", "youtube", "robot_vacuum"),
    ("Wish the app had a 'do not enter' zone feature for cat litter areas.", 3, "app", "reddit", "robot_vacuum"),
    ("App update removed the manual control joystick. Huge downgrade.", 2, "app", "amazon", "robot_vacuum"),
    ("App connects in under 5 seconds on WiFi. No Bluetooth pairing hassle.", 5, "app", "trustpilot", "robot_vacuum"),

    # noise (11+ mentions)
    ("Louder than expected on full power but runs late night on quiet mode fine.", 3, "noise", "reddit", "robot_vacuum"),
    ("Quiet mode is genuinely quiet. Can run it during a Zoom call without issues.", 5, "noise", "amazon", "robot_vacuum"),
    ("The self-empty dock is very loud. Woke up my baby twice already.", 2, "noise", "trustpilot", "robot_vacuum"),
    ("Noise level is acceptable on standard mode. Max mode is loud but you'd expect that.", 3, "noise", "youtube", "robot_vacuum"),
    ("Quietest robot vacuum I've owned. Neighbors haven't complained once.", 5, "noise", "reddit", "robot_vacuum"),
    ("Dock emptying sound is jarring but brief. I just set it to empty at 2pm when I'm out.", 4, "noise", "amazon", "robot_vacuum"),
    ("Quieter than my Dyson cordless. Kids don't even wake up when it runs at 8am.", 5, "noise", "twitter", "robot_vacuum"),
    ("Mopping mode is nearly silent. Vacuuming is louder but not unreasonable.", 4, "noise", "reddit", "robot_vacuum"),
    ("The high-pitched motor whine is annoying. Low mode is fine but high is unpleasant.", 2, "noise", "trustpilot", "robot_vacuum"),
    ("Noise level drops significantly on carpet vs hardwood. Smart adaptation.", 4, "noise", "youtube", "robot_vacuum"),
    ("Runs at 65dB measured. Acceptable for a robot vacuum in its class.", 4, "noise", "amazon", "robot_vacuum"),

    # durability (11+ mentions)
    ("6 months in and no signs of wear. Build quality is clearly better than last year's model.", 5, "durability", "reddit", "robot_vacuum"),
    ("Bumper cracked after minor collision with furniture leg. Disappointing build quality.", 2, "durability", "amazon", "robot_vacuum"),
    ("Body feels solid and premium. Nothing rattles or creaks after daily use.", 5, "durability", "trustpilot", "robot_vacuum"),
    ("Had a Shark 3 years ago that lasted a decade. Hoping this one does the same.", 5, "durability", "youtube", "robot_vacuum"),
    ("Wheel axle started grinding after 4 months. Called support and they sent a replacement unit.", 3, "durability", "reddit", "robot_vacuum"),
    ("Brushroll housing cracked during cleaning. Edge case but shouldn't happen.", 2, "durability", "amazon", "robot_vacuum"),
    ("Very solid build. Fell off a low step and kept working perfectly.", 5, "durability", "trustpilot", "robot_vacuum"),
    ("Motors are still running strong after 400+ cleaning sessions. Impressive longevity.", 5, "durability", "twitter", "robot_vacuum"),
    ("Lid hinge feels cheap but the main body is very solid.", 4, "durability", "reddit", "robot_vacuum"),
    ("Sensors still accurate after 18 months of heavy use. No calibration needed.", 5, "durability", "youtube", "robot_vacuum"),
    ("Replacement parts are available but pricey. Hope they stay available long-term.", 3, "durability", "amazon", "robot_vacuum"),
]

for text, rating, topic, plat, cat in powerdetect_texts:
    days = 60 - (idx % 60)
    SHARK_EXPANDED.append(make_row(plat, "shark", cat, "PowerDetect UV Reveal", text, rating, topic, days, idx, hour=(idx % 12) + 8))
    idx += 1

# Shark Matrix additional rows
shark_matrix_texts = [
    ("Matrix handles multi-room navigation without getting confused. Smart mapping.", 5, "navigation", "reddit", "robot_vacuum"),
    ("Matrix app scheduling finally works after the latest update. Was broken for weeks.", 3, "app", "amazon", "robot_vacuum"),
    ("Matrix suction is strong on hardwood but average on carpet.", 4, "suction", "trustpilot", "robot_vacuum"),
    ("Matrix noise on max is loud. Use quiet mode at night.", 3, "noise", "youtube", "robot_vacuum"),
    ("Matrix battery is underwhelming at 60 minutes on standard. Smaller house only.", 3, "battery", "reddit", "robot_vacuum"),
    ("Matrix build quality is good except the dustbin latch feels fragile.", 4, "durability", "amazon", "robot_vacuum"),
    ("Matrix app crashed on iOS 18. Support suggested reinstalling — not ideal.", 2, "app", "trustpilot", "robot_vacuum"),
    ("Matrix obstacle detection saved my power cable multiple times. Smart sensors.", 5, "navigation", "twitter", "robot_vacuum"),
    ("Matrix filter needs cleaning every week with a dog. Expected but plan for it.", 3, "filter", "reddit", "robot_vacuum"),
    ("Matrix firmware update pushed at 2am and disrupted my scheduled cleaning. Annoying.", 2, "app", "amazon", "robot_vacuum"),
    ("Matrix is my second Shark robot — upgrade from the original IQ model. Big improvement.", 5, "suction", "youtube", "robot_vacuum"),
    ("Matrix self-empty dock is worth the price premium. Never having to empty manually.", 5, "dock", "trustpilot", "robot_vacuum"),
]

for text, rating, topic, plat, cat in shark_matrix_texts:
    days = 60 - (idx % 58)
    SHARK_EXPANDED.append(make_row(plat, "shark", cat, "Shark Matrix", text, rating, topic, days, idx, hour=(idx % 12) + 8))
    idx += 1

# Shark IQ additional rows
shark_iq_texts = [
    ("IQ robot vacuum is solid entry-level option. Suction is good, navigation basic.", 4, "suction", "reddit", "robot_vacuum"),
    ("IQ battery life is excellent for the price tier. Full house on one charge.", 4, "battery", "amazon", "robot_vacuum"),
    ("IQ navigation is row-by-row style, not room-aware. Fine for simple layouts.", 3, "navigation", "trustpilot", "robot_vacuum"),
    ("IQ app is simple and reliable. Less features than Matrix but never crashes.", 5, "app", "youtube", "robot_vacuum"),
    ("IQ is noticeably quieter than my old upright. Night mode is near silent.", 5, "noise", "reddit", "robot_vacuum"),
    ("IQ dustbin is on the small side but empties easily.", 3, "dustbin", "amazon", "robot_vacuum"),
    ("IQ brushroll jammed twice in 3 months. Cleaned it and it recovered fine.", 3, "brushroll", "trustpilot", "robot_vacuum"),
    ("IQ is perfect for a one-bedroom apartment. Don't over-spec for small spaces.", 5, "navigation", "twitter", "robot_vacuum"),
    ("IQ dock connection is finicky. Sometimes robot misses the dock on return.", 3, "dock", "reddit", "robot_vacuum"),
    ("IQ value for money is unmatched at this price point. Shark's budget winner.", 5, "suction", "youtube", "robot_vacuum"),
]

for text, rating, topic, plat, cat in shark_iq_texts:
    days = 60 - (idx % 55)
    SHARK_EXPANDED.append(make_row(plat, "shark", cat, "Shark IQ", text, rating, topic, days, idx, hour=(idx % 12) + 8))
    idx += 1

# Shark Navigator additional rows
shark_nav_texts = [
    ("Navigator is a workhorse upright. Heavy but powerful for deep carpet cleaning.", 5, "suction", "reddit", "upright"),
    ("Navigator dustbin is huge and bagless. Easy to empty and rarely needs replacement parts.", 5, "dustbin", "amazon", "upright"),
    ("Navigator is loud on high power but delivers results. Worth the noise.", 4, "noise", "trustpilot", "upright"),
    ("Navigator anti-allergen HEPA filter is what sold me. Air quality improved noticeably.", 5, "filter", "youtube", "upright"),
    ("Navigator heavy and cumbersome to carry upstairs. Great for single-floor use.", 3, "durability", "reddit", "upright"),
    ("Navigator brushroll replacement is easy and affordable. 2 years in, still going.", 5, "brushroll", "amazon", "upright"),
    ("Navigator suction on carpet rivals professional cleaning equipment.", 5, "suction", "trustpilot", "upright"),
    ("Navigator hose attachment is well-designed. Great for stairs and upholstery.", 5, "brushroll", "twitter", "upright"),
    ("Navigator cord length is just 25ft. Not enough for larger rooms.", 3, "durability", "reddit", "upright"),
    ("Navigator value is undeniable. $200 corded upright that outperforms $400 cordless.", 5, "suction", "youtube", "upright"),
]

for text, rating, topic, plat, cat in shark_nav_texts:
    days = 60 - (idx % 50)
    SHARK_EXPANDED.append(make_row(plat, "shark", cat, "Shark Navigator", text, rating, topic, days, idx, hour=(idx % 12) + 8))
    idx += 1

# Novelty seed rows: "charging dock LED flickering" — new emerging issue on PowerDetect UV Reveal
# first_seen_at within last 14 days (days_ago <= 14)
NOVELTY_ROWS = [
    make_row("reddit", "shark", "robot_vacuum", "PowerDetect UV Reveal",
             "Anyone else notice the charging dock LED keeps flickering when the robot returns? Started happening 3 days ago after update.",
             2, "dock_led_flickering", 8, idx + 0, hour=10),
    make_row("amazon", "shark", "robot_vacuum", "PowerDetect UV Reveal",
             "Charging dock LED flickering constantly since last firmware push. Robot still charges but it's unsettling.",
             2, "dock_led_flickering", 10, idx + 1, hour=14),
    make_row("trustpilot", "shark", "robot_vacuum", "PowerDetect UV Reveal",
             "The dock LED flickers orange instead of solid white when charging. Customer service said they're looking into it.",
             2, "dock_led_flickering", 12, idx + 2, hour=11),
    make_row("youtube", "shark", "robot_vacuum", "PowerDetect UV Reveal",
             "Got the same dock LED flickering issue others are reporting. Makes me worry about charging stability.",
             2, "dock_led_flickering", 7, idx + 3, hour=16),
    make_row("twitter", "shark", "robot_vacuum", "PowerDetect UV Reveal",
             "My PowerDetect dock LED started flickering 5 days ago — seeing multiple reports on Reddit. Shark please address this!",
             2, "dock_led_flickering", 5, idx + 4, hour=9),
]
idx += 5


# ---------------------------------------------------------------------------
# Ninja expanded rows
# ---------------------------------------------------------------------------

NINJA_ROWS = []
ninja_idx = 200

ninja_texts = [
    # Foodi DualZone
    ("Foodi DualZone runs two zones at different temperatures simultaneously. Game changer for meal prep.", 5, "cooking_zones", "reddit", "air_fryer", "Ninja Foodi DualZone"),
    ("DualZone sync finish feature is brilliant. Both baskets done at exactly the same time.", 5, "cooking_zones", "amazon", "air_fryer", "Ninja Foodi DualZone"),
    ("DualZone capacity is perfect for a family of 4. Never need the oven anymore.", 5, "capacity", "trustpilot", "air_fryer", "Ninja Foodi DualZone"),
    ("DualZone takes up a lot of counter space. Measure your counter before buying.", 3, "size", "youtube", "air_fryer", "Ninja Foodi DualZone"),
    ("DualZone fan is loud on full blast but quieter than expected for the power.", 3, "noise", "reddit", "air_fryer", "Ninja Foodi DualZone"),
    ("DualZone baskets are dishwasher safe. Cleanup is the easiest part of this appliance.", 5, "cleaning", "amazon", "air_fryer", "Ninja Foodi DualZone"),
    ("DualZone temperature accuracy is excellent. Meats come out perfectly every time.", 5, "temperature", "trustpilot", "air_fryer", "Ninja Foodi DualZone"),
    ("DualZone preheat time is fast. Ready in 3 minutes versus 15 for a conventional oven.", 5, "preheat", "twitter", "air_fryer", "Ninja Foodi DualZone"),
    ("DualZone control panel is intuitive once you read the manual.", 4, "controls", "reddit", "air_fryer", "Ninja Foodi DualZone"),
    ("DualZone basket coating starting to peel after 6 months. Contact Ninja support now.", 2, "durability", "amazon", "air_fryer", "Ninja Foodi DualZone"),
    ("DualZone dehydrate function works great for jerky and herbs.", 5, "cooking_zones", "youtube", "air_fryer", "Ninja Foodi DualZone"),
    ("DualZone crisps frozen food like nothing else. Fries come out better than restaurant.", 5, "temperature", "trustpilot", "air_fryer", "Ninja Foodi DualZone"),

    # Ninja Creami
    ("Creami makes incredible ice cream from frozen bases. Texture is legitimately smooth.", 5, "texture", "reddit", "ice_cream_maker", "Ninja Creami"),
    ("Creami sorbet mode handles fruit bases beautifully. No ice chunks ever.", 5, "texture", "amazon", "ice_cream_maker", "Ninja Creami"),
    ("Creami motor is loud but the results are worth it. 2 minutes of noise for premium ice cream.", 4, "noise", "trustpilot", "ice_cream_maker", "Ninja Creami"),
    ("Creami pint container is small. Fine for 1-2 servings, not for parties.", 3, "capacity", "youtube", "ice_cream_maker", "Ninja Creami"),
    ("Creami light ice cream setting is perfect for protein ice cream recipes.", 5, "texture", "reddit", "ice_cream_maker", "Ninja Creami"),
    ("Creami motor burned out after 8 months. Replacement unit shipped quickly from Ninja.", 2, "durability", "amazon", "ice_cream_maker", "Ninja Creami"),
    ("Creami mix-in function works by re-spinning — genius design for add-ins.", 5, "texture", "twitter", "ice_cream_maker", "Ninja Creami"),
    ("Creami base needs 24 hours to freeze properly. Plan ahead or you'll be disappointed.", 3, "process", "trustpilot", "ice_cream_maker", "Ninja Creami"),
    ("Creami container is easy to clean. Dishwasher safe on top rack.", 5, "cleaning", "reddit", "ice_cream_maker", "Ninja Creami"),
    ("Creami is the only machine that gives me commercial-quality results at home.", 5, "texture", "youtube", "ice_cream_maker", "Ninja Creami"),
    ("Creami display scratches easily. Minor complaint for a great machine.", 3, "durability", "amazon", "ice_cream_maker", "Ninja Creami"),

    # Ninja Espresso Bar
    ("Espresso Bar extracts a genuinely good espresso shot. Crema is present and consistent.", 5, "espresso", "reddit", "coffee", "Ninja Espresso Bar"),
    ("Espresso Bar steam wand reaches temperature fast. Microfoam is excellent for latte art.", 5, "steam_wand", "amazon", "coffee", "Ninja Espresso Bar"),
    ("Espresso Bar grinder is built-in and quiet for a burr grinder.", 4, "grinder", "trustpilot", "coffee", "Ninja Espresso Bar"),
    ("Espresso Bar descaling mode is easy to run. Notification system tells you when it's due.", 5, "descale", "youtube", "coffee", "Ninja Espresso Bar"),
    ("Espresso Bar pod compatibility is limited. Only works with Nespresso Originalline.", 3, "pod", "reddit", "coffee", "Ninja Espresso Bar"),
    ("Espresso Bar water tank is generous. Fill once for a week of daily espressos.", 5, "capacity", "amazon", "coffee", "Ninja Espresso Bar"),
    ("Espresso Bar carafe mode brews 4 cups at once. Great for hosting.", 5, "carafe", "trustpilot", "coffee", "Ninja Espresso Bar"),
    ("Espresso Bar steam wand drips slightly after use. Minor annoyance.", 3, "steam_wand", "twitter", "coffee", "Ninja Espresso Bar"),
    ("Espresso Bar temperature setting lets me dial in extraction perfectly.", 5, "temperature", "reddit", "coffee", "Ninja Espresso Bar"),
    ("Espresso Bar dial controls feel premium. Much better than digital buttons.", 5, "controls", "youtube", "coffee", "Ninja Espresso Bar"),

    # Ninja Coffee Bar
    ("Coffee Bar brews a full carafe in 8 minutes. Speed is unmatched in its class.", 5, "brew_speed", "reddit", "coffee", "Ninja Coffee Bar"),
    ("Coffee Bar rich mode concentrate is perfect for iced coffee drinks.", 5, "temperature", "amazon", "coffee", "Ninja Coffee Bar"),
    ("Coffee Bar carafe keeps coffee hot for 4 hours. Better than my old machine.", 5, "carafe", "trustpilot", "coffee", "Ninja Coffee Bar"),
    ("Coffee Bar thermal carafe is the right choice. No burnt taste from hot plate.", 5, "temperature", "youtube", "coffee", "Ninja Coffee Bar"),
    ("Coffee Bar descale alert came on after 3 months. Easy process but unexpected frequency.", 3, "descale", "reddit", "coffee", "Ninja Coffee Bar"),
    ("Coffee Bar over-ice setting is incredible. Coffee chills perfectly without diluting.", 5, "temperature", "amazon", "coffee", "Ninja Coffee Bar"),
    ("Coffee Bar pod and grounds compatibility is the best feature. Ultimate flexibility.", 5, "pod", "twitter", "coffee", "Ninja Coffee Bar"),
    ("Coffee Bar warming plate cracked after 1 year. Replacement part available but frustrating.", 2, "durability", "trustpilot", "coffee", "Ninja Coffee Bar"),
    ("Coffee Bar frother makes decent foam. Not cafe quality but good enough for home.", 4, "steam_wand", "reddit", "coffee", "Ninja Coffee Bar"),
    ("Coffee Bar program settings are intuitive. Set it and forget it for morning routine.", 5, "controls", "youtube", "coffee", "Ninja Coffee Bar"),
]

for text, rating, topic, plat, cat, sku in ninja_texts:
    days = 60 - (ninja_idx % 59)
    NINJA_ROWS.append(make_row(plat, "ninja", cat, sku, text, rating, topic, days, ninja_idx, hour=(ninja_idx % 12) + 8))
    ninja_idx += 1

# ---------------------------------------------------------------------------
# Competitor expanded rows
# ---------------------------------------------------------------------------

COMPETITOR_ROWS = []
comp_idx = 300

competitor_texts = [
    # Dyson V15
    ("Dyson V15 laser dust detection is genuinely useful. Can see what you're cleaning.", 5, "suction", "reddit", "cordless_stick", "dyson", "Dyson V15"),
    ("Dyson V15 suction on full power is class-leading. Nothing on the market matches it.", 5, "suction", "amazon", "cordless_stick", "dyson", "Dyson V15"),
    ("Dyson V15 battery lasts 60 minutes on eco mode. Adequate for most homes.", 4, "battery", "trustpilot", "cordless_stick", "dyson", "Dyson V15"),
    ("Dyson V15 is very expensive but the engineering quality is obvious.", 4, "durability", "youtube", "cordless_stick", "dyson", "Dyson V15"),
    ("Dyson V15 attachment variety is unmatched. Has the right tool for every surface.", 5, "brushroll", "reddit", "cordless_stick", "dyson", "Dyson V15"),
    ("Dyson V15 charging dock is elegantly designed. Stores all attachments neatly.", 5, "dock", "amazon", "cordless_stick", "dyson", "Dyson V15"),
    ("Dyson V15 noise on max is really loud. Standard mode is more tolerable.", 3, "noise", "trustpilot", "cordless_stick", "dyson", "Dyson V15"),
    ("Dyson V15 app shows particle count in real time. Very satisfying to watch.", 5, "app", "twitter", "cordless_stick", "dyson", "Dyson V15"),
    ("Dyson V15 filter replacement costs $30 every 6 months. Factor this into total cost.", 3, "filter", "reddit", "cordless_stick", "dyson", "Dyson V15"),
    ("Dyson V15 at $800 is hard to justify. Shark PowerDetect is 40% cheaper with comparable results.", 3, "suction", "youtube", "cordless_stick", "dyson", "Dyson V15"),

    # iRobot Roomba j7+
    ("Roomba j7+ obstacle avoidance is the best in the industry. Never touched a cable.", 5, "navigation", "reddit", "robot_vacuum", "irobot", "iRobot Roomba j7+"),
    ("Roomba j7+ mapping accuracy is excellent. Room identification works perfectly.", 5, "navigation", "amazon", "robot_vacuum", "irobot", "iRobot Roomba j7+"),
    ("Roomba j7+ app is the most polished in the robot vacuum space.", 5, "app", "trustpilot", "robot_vacuum", "irobot", "iRobot Roomba j7+"),
    ("Roomba j7+ self-empty dock works silently. Big advantage over Shark's louder dock.", 5, "noise", "youtube", "robot_vacuum", "irobot", "iRobot Roomba j7+"),
    ("Roomba j7+ suction is weaker than Shark Matrix at the same price. Disappointing.", 3, "suction", "reddit", "robot_vacuum", "irobot", "iRobot Roomba j7+"),
    ("Roomba j7+ premium pricing is hard to justify given the suction difference vs Shark.", 3, "suction", "amazon", "robot_vacuum", "irobot", "iRobot Roomba j7+"),
    ("Roomba j7+ battery lasts 75 minutes. Better than most competitors.", 5, "battery", "trustpilot", "robot_vacuum", "irobot", "iRobot Roomba j7+"),
    ("Roomba j7+ firmware updates are more frequent and reliable than Shark's.", 5, "app", "twitter", "robot_vacuum", "irobot", "iRobot Roomba j7+"),
    ("Roomba j7+ brushroll is easier to clean than shark competitors. Simple design.", 5, "brushroll", "reddit", "robot_vacuum", "irobot", "iRobot Roomba j7+"),
    ("Roomba j7+ iRobot OS keeps getting better with each update. Good long-term value.", 5, "navigation", "youtube", "robot_vacuum", "irobot", "iRobot Roomba j7+"),

    # Roborock S8
    ("Roborock S8 mop and vacuum simultaneously feature is excellent. Saves time.", 5, "navigation", "reddit", "robot_vacuum", "roborock", "Roborock S8"),
    ("Roborock S8 sonic mopping is noticeably more effective than simple drag-mop designs.", 5, "navigation", "amazon", "robot_vacuum", "roborock", "Roborock S8"),
    ("Roborock S8 suction rivals much more expensive models.", 5, "suction", "trustpilot", "robot_vacuum", "roborock", "Roborock S8"),
    ("Roborock S8 app is the most feature-rich in the category. Maybe too many options.", 4, "app", "youtube", "robot_vacuum", "roborock", "Roborock S8"),
    ("Roborock S8 battery gives 180 minutes on standard. Outstanding range.", 5, "battery", "reddit", "robot_vacuum", "roborock", "Roborock S8"),
    ("Roborock S8 dock auto-refills the mop water. Completely hands-free mopping.", 5, "dock", "amazon", "robot_vacuum", "roborock", "Roborock S8"),
    ("Roborock S8 is noisy but cleans thoroughly. Trade-off I'm willing to make.", 4, "noise", "trustpilot", "robot_vacuum", "roborock", "Roborock S8"),
    ("Roborock S8 customer support is poor. Parts availability is also limited outside US.", 2, "durability", "twitter", "robot_vacuum", "roborock", "Roborock S8"),
    ("Roborock S8 obstacle detection occasionally fails on dark colored objects.", 3, "navigation", "reddit", "robot_vacuum", "roborock", "Roborock S8"),
    ("Roborock S8 price dropped by $100 in the last year. Now it's exceptional value.", 5, "suction", "youtube", "robot_vacuum", "roborock", "Roborock S8"),

    # KitchenAid Pro
    ("KitchenAid Pro motor is powerful enough for bread dough without straining.", 5, "motor", "reddit", "blender", "kitchenaid", "KitchenAid Pro"),
    ("KitchenAid Pro bowl capacity is 7qt. More than enough for double batches.", 5, "capacity", "amazon", "blender", "kitchenaid", "KitchenAid Pro"),
    ("KitchenAid Pro attachments are the real value proposition. Pasta, meat grinder, more.", 5, "attachments", "trustpilot", "blender", "kitchenaid", "KitchenAid Pro"),
    ("KitchenAid Pro is extremely heavy and takes up significant counter space.", 3, "size", "youtube", "blender", "kitchenaid", "KitchenAid Pro"),
    ("KitchenAid Pro noise on speed 10 is very loud. Expected for the power level.", 3, "noise", "reddit", "blender", "kitchenaid", "KitchenAid Pro"),
    ("KitchenAid Pro bowl lift mechanism is rock solid. Never wobbles during mixing.", 5, "durability", "amazon", "blender", "kitchenaid", "KitchenAid Pro"),
    ("KitchenAid Pro splash guard is essential but sold separately. Include it in the box.", 3, "attachments", "trustpilot", "blender", "kitchenaid", "KitchenAid Pro"),
    ("KitchenAid Pro 10 speeds are well calibrated. Each step makes a noticeable difference.", 5, "controls", "twitter", "blender", "kitchenaid", "KitchenAid Pro"),
    ("KitchenAid Pro whisk attachment makes the best meringue I've ever made.", 5, "attachments", "reddit", "blender", "kitchenaid", "KitchenAid Pro"),
    ("KitchenAid Pro price is high but will outlast cheaper alternatives by decades.", 5, "durability", "youtube", "blender", "kitchenaid", "KitchenAid Pro"),
]

for text, rating, topic, plat, cat, brand, sku in competitor_texts:
    days = 60 - (comp_idx % 58)
    COMPETITOR_ROWS.append(make_row(plat, brand, cat, sku, text, rating, topic, days, comp_idx, hour=(comp_idx % 12) + 8))
    comp_idx += 1

# ---------------------------------------------------------------------------
# Additional filler rows to reach ≥300 total
# Spread evenly across all SKUs and platforms
# ---------------------------------------------------------------------------

EXTRA_SHARK = []
extra_shark_idx = 500

extra_shark_data = [
    # PowerDetect UV Reveal extra
    ("PowerDetect UV Reveal handles pet hair like a champion. No tangles ever.", 5, "brushroll", "reddit", "robot_vacuum", "PowerDetect UV Reveal"),
    ("The UV light feature actually shows dust you didn't know was there. Eye-opening.", 5, "suction", "amazon", "robot_vacuum", "PowerDetect UV Reveal"),
    ("PowerDetect filter system is multi-stage and captures fine allergens well.", 5, "filter", "trustpilot", "robot_vacuum", "PowerDetect UV Reveal"),
    ("Scheduling in the app is reliable. Runs every morning at 9am without fail.", 5, "app", "youtube", "robot_vacuum", "PowerDetect UV Reveal"),
    ("Suction mode automatically adjusts on carpet vs hardwood. Clever design.", 5, "suction", "twitter", "robot_vacuum", "PowerDetect UV Reveal"),
    ("Battery returns to dock to charge mid-run and picks up where it left off.", 5, "battery", "reddit", "robot_vacuum", "PowerDetect UV Reveal"),
    ("Navigation handles open-plan layout perfectly. No missed zones.", 5, "navigation", "amazon", "robot_vacuum", "PowerDetect UV Reveal"),
    ("Noise is bearable on eco mode. Max mode is loud but I only use it weekly.", 4, "noise", "trustpilot", "robot_vacuum", "PowerDetect UV Reveal"),
    ("Durability after 9 months is excellent. No worn parts or degraded performance.", 5, "durability", "youtube", "robot_vacuum", "PowerDetect UV Reveal"),
    ("App onboarding experience is the best in class. Setup took under 10 minutes.", 5, "app", "reddit", "robot_vacuum", "PowerDetect UV Reveal"),
    # Shark Matrix extra
    ("Matrix dock emptying is automatic and the bag lasts 60 days. Genuinely hands-free.", 5, "dock", "amazon", "robot_vacuum", "Shark Matrix"),
    ("Matrix suction degrades slightly after 3 months. Filter cleaning helps a lot.", 3, "suction", "trustpilot", "robot_vacuum", "Shark Matrix"),
    ("Matrix navigation got confused once around a new piece of furniture. Remapped easily.", 4, "navigation", "youtube", "robot_vacuum", "Shark Matrix"),
    ("Matrix app widget on iPhone home screen is convenient. Nice UX touch.", 5, "app", "reddit", "robot_vacuum", "Shark Matrix"),
    ("Matrix battery life improved after a firmware update. Now lasts 75 minutes.", 4, "battery", "amazon", "robot_vacuum", "Shark Matrix"),
    # Shark IQ extra
    ("IQ robot has been running daily for 2 years with no hardware issues.", 5, "durability", "reddit", "robot_vacuum", "Shark IQ"),
    ("IQ navigation row-pattern means it's predictable. I know it won't miss a spot.", 4, "navigation", "amazon", "robot_vacuum", "Shark IQ"),
    ("IQ app is simple but that's a feature not a bug. No bloat.", 5, "app", "trustpilot", "robot_vacuum", "Shark IQ"),
    # Shark Navigator extra
    ("Navigator edge cleaning attachment is outstanding for baseboards.", 5, "brushroll", "reddit", "upright", "Shark Navigator"),
    ("Navigator HEPA filter removes dog dander effectively. Allergy sufferer approved.", 5, "filter", "amazon", "upright", "Shark Navigator"),
    ("Navigator cord winds up neatly and storage is compact for an upright.", 4, "durability", "trustpilot", "upright", "Shark Navigator"),
]

for text, rating, topic, plat, cat, sku in extra_shark_data:
    days = 60 - (extra_shark_idx % 57)
    EXTRA_SHARK.append(make_row(plat, "shark", cat, sku, text, rating, topic, days, extra_shark_idx, hour=(extra_shark_idx % 12) + 8))
    extra_shark_idx += 1

EXTRA_NINJA = []
extra_ninja_idx = 600

extra_ninja_data = [
    ("DualZone french fry results are restaurant quality every single time.", 5, "temperature", "reddit", "air_fryer", "ninja", "Ninja Foodi DualZone"),
    ("DualZone timer beep is satisfying. Clear audio cue when cooking completes.", 4, "controls", "amazon", "air_fryer", "ninja", "Ninja Foodi DualZone"),
    ("DualZone heat recovery between batches is fast. Efficient for batch cooking.", 5, "preheat", "trustpilot", "air_fryer", "ninja", "Ninja Foodi DualZone"),
    ("DualZone warranty support replaced my unit within 5 days of filing claim.", 5, "durability", "youtube", "air_fryer", "ninja", "Ninja Foodi DualZone"),
    ("DualZone saves me so much time versus the oven. Use it daily for dinner.", 5, "cooking_zones", "twitter", "air_fryer", "ninja", "Ninja Foodi DualZone"),
    ("Creami freezing requirement is the only inconvenience. Results justify the wait.", 4, "process", "reddit", "ice_cream_maker", "ninja", "Ninja Creami"),
    ("Creami protein ice cream mode is perfect for fitness-focused eating.", 5, "texture", "amazon", "ice_cream_maker", "ninja", "Ninja Creami"),
    ("Creami sorbet is smoother than anything I've made with traditional ice cream makers.", 5, "texture", "trustpilot", "ice_cream_maker", "ninja", "Ninja Creami"),
    ("Espresso Bar shot extraction time is adjustable. Advanced user feature I love.", 5, "espresso", "reddit", "coffee", "ninja", "Ninja Espresso Bar"),
    ("Espresso Bar milk frother makes excellent cappuccino foam.", 5, "steam_wand", "amazon", "coffee", "ninja", "Ninja Espresso Bar"),
    ("Coffee Bar scheduled brew function works flawlessly every morning.", 5, "brew_speed", "trustpilot", "coffee", "ninja", "Ninja Coffee Bar"),
    ("Coffee Bar over-ice brew is the best way to make cold brew at home.", 5, "temperature", "youtube", "coffee", "ninja", "Ninja Coffee Bar"),
    ("Coffee Bar specialty brew modes cover everything from espresso-style to tea.", 5, "controls", "twitter", "coffee", "ninja", "Ninja Coffee Bar"),
]

for text, rating, topic, plat, cat, brand, sku in extra_ninja_data:
    days = 60 - (extra_ninja_idx % 56)
    EXTRA_NINJA.append(make_row(plat, brand, cat, sku, text, rating, topic, days, extra_ninja_idx, hour=(extra_ninja_idx % 12) + 8))
    extra_ninja_idx += 1

EXTRA_COMP = []
extra_comp_idx = 700

extra_comp_data = [
    ("Dyson V15 cyclone technology is mature and consistently effective.", 5, "suction", "reddit", "cordless_stick", "dyson", "Dyson V15"),
    ("Dyson V15 HEPA filter captures 99.97% of particles. Best for allergy sufferers.", 5, "filter", "amazon", "cordless_stick", "dyson", "Dyson V15"),
    ("Dyson V15 screen showing particle count is gimmicky but customers love it.", 3, "app", "youtube", "cordless_stick", "dyson", "Dyson V15"),
    ("Roomba j7+ still the best at avoiding pet waste. The P.O.O.P. guarantee is real.", 5, "navigation", "reddit", "robot_vacuum", "irobot", "iRobot Roomba j7+"),
    ("Roomba j7+ zone cleaning via app is precise. Send it to just the kitchen easily.", 5, "app", "amazon", "robot_vacuum", "irobot", "iRobot Roomba j7+"),
    ("Roomba j7+ self-empty base is whisper quiet. Huge selling point vs Shark.", 5, "noise", "trustpilot", "robot_vacuum", "irobot", "iRobot Roomba j7+"),
    ("Roborock S8 auto-lift mop on carpet is smart. Never mops where it shouldn't.", 5, "navigation", "youtube", "robot_vacuum", "roborock", "Roborock S8"),
    ("Roborock S8 app map editor is the most detailed in the category.", 5, "app", "reddit", "robot_vacuum", "roborock", "Roborock S8"),
    ("Roborock S8 value at current price point is hard to beat vs Shark or iRobot.", 5, "suction", "amazon", "robot_vacuum", "roborock", "Roborock S8"),
    ("KitchenAid Pro flex edge beater reduces scraping. Saves so much time baking.", 5, "attachments", "trustpilot", "blender", "kitchenaid", "KitchenAid Pro"),
    ("KitchenAid Pro bowl capacity handles triple batches of cookie dough.", 5, "capacity", "reddit", "blender", "kitchenaid", "KitchenAid Pro"),
    ("KitchenAid Pro timer display is easy to read from across the kitchen.", 4, "controls", "amazon", "blender", "kitchenaid", "KitchenAid Pro"),
    ("KitchenAid Pro motor runs cool even on long mixing sessions. Well-engineered.", 5, "motor", "youtube", "blender", "kitchenaid", "KitchenAid Pro"),
]

for text, rating, topic, plat, cat, brand, sku in extra_comp_data:
    days = 60 - (extra_comp_idx % 55)
    EXTRA_COMP.append(make_row(plat, brand, cat, sku, text, rating, topic, days, extra_comp_idx, hour=(extra_comp_idx % 12) + 8))
    extra_comp_idx += 1

# ---------------------------------------------------------------------------
# Final top-up batch to guarantee ≥300 total
# ---------------------------------------------------------------------------

TOPUP_SHARK = []
topup_shark_idx = 800

topup_shark_data = [
    # PowerDetect UV Reveal top-up (more dock, filter, brushroll aspect mentions)
    ("Charging dock LED is a clear indicator of charging status. Simple and effective.", 5, "dock", "reddit", "robot_vacuum", "PowerDetect UV Reveal"),
    ("Filter indicator in the app tells me when to clean. Never guessing anymore.", 5, "filter", "amazon", "robot_vacuum", "PowerDetect UV Reveal"),
    ("Brushroll picks up fine debris like sand and flour easily. Impressive coverage.", 5, "brushroll", "trustpilot", "robot_vacuum", "PowerDetect UV Reveal"),
    ("App gives me a detailed map of cleaned area after each run. Very satisfying.", 5, "app", "youtube", "robot_vacuum", "PowerDetect UV Reveal"),
    ("Suction on hard floor is exceptional. Leaves the floor visibly cleaner.", 5, "suction", "twitter", "robot_vacuum", "PowerDetect UV Reveal"),
    ("Battery recharge is faster than advertised on the box. Nice surprise.", 4, "battery", "reddit", "robot_vacuum", "PowerDetect UV Reveal"),
    ("Navigation finally handles my dark hardwood floors without getting confused.", 4, "navigation", "amazon", "robot_vacuum", "PowerDetect UV Reveal"),
    ("Noise on auto-adjust mode is significantly less annoying than manual max.", 4, "noise", "trustpilot", "robot_vacuum", "PowerDetect UV Reveal"),
    ("Build quality is premium for the price bracket. Heavy and solid.", 5, "durability", "youtube", "robot_vacuum", "PowerDetect UV Reveal"),
    ("PowerDetect handles transitions between rugs and hardwood without hesitation.", 5, "navigation", "reddit", "robot_vacuum", "PowerDetect UV Reveal"),
    # Shark Matrix
    ("Matrix detects obstacles in realtime using vision AI. Rarely wrong.", 5, "navigation", "amazon", "robot_vacuum", "Shark Matrix"),
    ("Matrix quiet mode is acceptably quiet for an evening run.", 4, "noise", "trustpilot", "robot_vacuum", "Shark Matrix"),
    ("Matrix mopping pad attachment works okay but the UV Reveal version is better.", 3, "navigation", "reddit", "robot_vacuum", "Shark Matrix"),
    # Shark IQ
    ("IQ has been running twice a day for 6 months — no signs of wear.", 5, "durability", "youtube", "robot_vacuum", "Shark IQ"),
    ("IQ value vs the premium models is exceptional. 80% of the performance at 50% of the price.", 5, "suction", "amazon", "robot_vacuum", "Shark IQ"),
]

for text, rating, topic, plat, cat, sku in topup_shark_data:
    days = 60 - (topup_shark_idx % 52)
    TOPUP_SHARK.append(make_row(plat, "shark", cat, sku, text, rating, topic, days, topup_shark_idx, hour=(topup_shark_idx % 12) + 8))
    topup_shark_idx += 1

TOPUP_NINJA = []
topup_ninja_idx = 850

topup_ninja_data = [
    ("DualZone reheat mode is a killer feature for batch cooking and meal prep.", 5, "cooking_zones", "reddit", "air_fryer", "ninja", "Ninja Foodi DualZone"),
    ("DualZone handles steak perfectly with the right time and temp settings.", 5, "temperature", "amazon", "air_fryer", "ninja", "Ninja Foodi DualZone"),
    ("DualZone energy consumption is notably less than using the oven.", 5, "cooking_zones", "trustpilot", "air_fryer", "ninja", "Ninja Foodi DualZone"),
    ("Creami texture processing is consistent across all preset modes.", 5, "texture", "youtube", "ice_cream_maker", "ninja", "Ninja Creami"),
    ("Creami desserts come out lighter than traditional ice cream. Impressive tech.", 5, "texture", "reddit", "ice_cream_maker", "ninja", "Ninja Creami"),
    ("Espresso Bar espresso tastes comparable to professional cafe espresso.", 5, "espresso", "amazon", "coffee", "ninja", "Ninja Espresso Bar"),
    ("Coffee Bar coffee temperature is ideal. Not too hot, not too cold.", 5, "temperature", "trustpilot", "coffee", "ninja", "Ninja Coffee Bar"),
    ("Coffee Bar weekly clean reminder keeps the machine in top condition.", 5, "descale", "youtube", "coffee", "ninja", "Ninja Coffee Bar"),
]

for text, rating, topic, plat, cat, brand, sku in topup_ninja_data:
    days = 60 - (topup_ninja_idx % 51)
    TOPUP_NINJA.append(make_row(plat, brand, cat, sku, text, rating, topic, days, topup_ninja_idx, hour=(topup_ninja_idx % 12) + 8))
    topup_ninja_idx += 1

TOPUP_COMP = []
topup_comp_idx = 900

topup_comp_data = [
    ("Dyson V15 piezo sensor counting particles is genuinely useful feedback.", 5, "suction", "reddit", "cordless_stick", "dyson", "Dyson V15"),
    ("Dyson V15 hair screw tool is the best attachment for long hair users.", 5, "brushroll", "amazon", "cordless_stick", "dyson", "Dyson V15"),
    ("Dyson V15 LCD display showing suction mode is clear and helpful.", 5, "app", "trustpilot", "cordless_stick", "dyson", "Dyson V15"),
    ("Roomba j7+ avoids dark rugs correctly with the P.O.O.P. feature. Lifesaver.", 5, "navigation", "youtube", "robot_vacuum", "irobot", "iRobot Roomba j7+"),
    ("Roomba j7+ software updates add new features. Ecosystem gets better over time.", 5, "app", "reddit", "robot_vacuum", "irobot", "iRobot Roomba j7+"),
    ("Roborock S8 combined vacuum-mop in one pass saves 30 minutes weekly.", 5, "navigation", "amazon", "robot_vacuum", "roborock", "Roborock S8"),
    ("Roborock S8 dust collector capacity is larger than competitors at this price.", 5, "suction", "trustpilot", "robot_vacuum", "roborock", "Roborock S8"),
    ("KitchenAid Pro spiral dough hook kneads perfectly every time.", 5, "attachments", "youtube", "blender", "kitchenaid", "KitchenAid Pro"),
    ("KitchenAid Pro is the cornerstone of serious home baking. Worth every dollar.", 5, "durability", "reddit", "blender", "kitchenaid", "KitchenAid Pro"),
    ("KitchenAid Pro color selection is wide. Matches any kitchen aesthetic.", 4, "size", "amazon", "blender", "kitchenaid", "KitchenAid Pro"),
    ("KitchenAid Pro bowl scraper attachment is the most useful addition I've bought.", 5, "attachments", "trustpilot", "blender", "kitchenaid", "KitchenAid Pro"),
    ("KitchenAid Pro resale value is exceptional. Holds value for years.", 5, "durability", "youtube", "blender", "kitchenaid", "KitchenAid Pro"),
]

for text, rating, topic, plat, cat, brand, sku in topup_comp_data:
    days = 60 - (topup_comp_idx % 50)
    TOPUP_COMP.append(make_row(plat, brand, cat, sku, text, rating, topic, days, topup_comp_idx, hour=(topup_comp_idx % 12) + 8))
    topup_comp_idx += 1


# ---------------------------------------------------------------------------
# Write CSV files
# ---------------------------------------------------------------------------

def write_csv(path: str, header: list, rows: list) -> int:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(header)
        for row in rows:
            writer.writerow(row)
    return len(rows)


def main():
    base = Path(__file__).parent.parent / "data"
    base.mkdir(exist_ok=True)

    shark_rows = SHARK_EDGE_CASES + SHARK_EXPANDED + NOVELTY_ROWS + EXTRA_SHARK + TOPUP_SHARK
    ninja_rows = NINJA_ROWS + EXTRA_NINJA + TOPUP_NINJA
    competitor_rows = COMPETITOR_ROWS + EXTRA_COMP + TOPUP_COMP

    shark_path = str(base / "reviews_shark.csv")
    ninja_path = str(base / "reviews_ninja.csv")
    comp_path = str(base / "reviews_competitors.csv")

    n_shark = write_csv(shark_path, HEADERS, shark_rows)
    n_ninja = write_csv(ninja_path, HEADERS, ninja_rows)
    n_comp = write_csv(comp_path, HEADERS, competitor_rows)

    total = n_shark + n_ninja + n_comp
    print(f"Generated {total} rows total:")
    print(f"  {shark_path}: {n_shark} rows")
    print(f"  {ninja_path}: {n_ninja} rows")
    print(f"  {comp_path}: {n_comp} rows")

    # Verification checks
    print()
    print("Verification:")
    print(f"  Total >= 300: {'PASS' if total >= 300 else 'FAIL'} ({total})")
    print(f"  Novelty seed rows present: {'PASS' if len(NOVELTY_ROWS) >= 5 else 'FAIL'} ({len(NOVELTY_ROWS)} rows)")
    print(f"  Edge cases preserved: {'PASS' if len(SHARK_EDGE_CASES) >= 16 else 'FAIL'} ({len(SHARK_EDGE_CASES)} rows)")

    # Count SKUs
    all_rows = shark_rows + ninja_rows + competitor_rows
    skus = set(r[8] for r in all_rows if r[8])
    print(f"  Distinct SKUs >= 12: {'PASS' if len(skus) >= 12 else 'FAIL'} ({len(skus)}: {sorted(skus)})")

    # Count platforms
    platforms = set(r[1] for r in all_rows)
    print(f"  All 5 platforms present: {'PASS' if len(platforms) >= 5 else 'FAIL'} ({sorted(platforms)})")

    # Count PowerDetect aspects
    powerdetect_rows = [r for r in shark_rows if r[8] == "PowerDetect UV Reveal"]
    aspect_topics = {}
    for r in powerdetect_rows:
        topic = r[12]  # topic_id column
        aspect_topics[topic] = aspect_topics.get(topic, 0) + 1
    aspects_with_10plus = {k: v for k, v in aspect_topics.items() if v >= 10}
    print(f"  PowerDetect UV Reveal aspects with 10+ mentions: {'PASS' if len(aspects_with_10plus) >= 6 else 'FAIL'} ({len(aspects_with_10plus)})")
    for asp, cnt in sorted(aspects_with_10plus.items(), key=lambda x: -x[1]):
        print(f"    {asp}: {cnt}")


if __name__ == "__main__":
    main()
