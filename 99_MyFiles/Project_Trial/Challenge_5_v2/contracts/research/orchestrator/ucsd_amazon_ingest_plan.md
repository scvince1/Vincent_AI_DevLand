# UCSD Amazon Reviews '23 — Ingest Plan for Round 4

**Author:** backend-engineer-v3 (research window, 2026-04-11)
**Purpose:** R4 backend-engineer-v4 reference — how to ingest the UCSD Amazon Reviews 2023 dataset as the historical Amazon coverage source in place of live scraping.
**Feeds:** `contracts/real_api_integration_proposal.md` (Offline Corpora section)

---

## 1. Download Mechanism

**Recommended: Direct JSONL.gz download from UCSD datarepo** (Method B below). Faster for targeted category subsets than the HuggingFace datasets library, which streams the full dataset by default.

### Method A — HuggingFace datasets library (streaming-friendly, higher overhead)

```python
from datasets import load_dataset

# Reviews for a specific category
dataset = load_dataset(
    "McAuley-Lab/Amazon-Reviews-2023",
    "raw_review_Home_and_Kitchen",
    trust_remote_code=True,
    streaming=True,  # use streaming=True to avoid loading 67M rows into RAM
)

# Item metadata (for ASIN lookup / product name mapping)
meta = load_dataset(
    "McAuley-Lab/Amazon-Reviews-2023",
    "raw_meta_Appliances",
    split="full",
    trust_remote_code=True,
)
```

**Drawback:** `trust_remote_code=True` executes the dataset's loader script — supply chain risk for production use. Acceptable for internal R4 demo ingest.

### Method B — Direct JSONL.gz download (recommended for targeted ingest)

Base URL pattern:
```
Reviews: https://datarepo.eng.ucsd.edu/mcauley_group/data/amazon_2023/raw/review_categories/{CATEGORY}.jsonl.gz
Metadata: https://datarepo.eng.ucsd.edu/mcauley_group/data/amazon_2023/raw/meta_categories/meta_{CATEGORY}.jsonl.gz
```

Download and stream without full decompress:
```python
import gzip, json, urllib.request

url = "https://datarepo.eng.ucsd.edu/mcauley_group/data/amazon_2023/raw/review_categories/Appliances.jsonl.gz"
with urllib.request.urlopen(url) as response:
    with gzip.GzipFile(fileobj=response) as f:
        for line in f:
            review = json.loads(line)
            # filter by parent_asin here before accumulating
```

**Advantage:** No HuggingFace auth, no loader script trust, can filter by ASIN on-the-fly without storing the full file.

---

## 2. Relevant Categories for SharkNinja Coverage

Two primary categories cover the target SKUs:

| Category identifier | HF config name | Reviews | Items | Notes |
|---|---|---|---|---|
| `Appliances` | `raw_review_Appliances` | 2.1M | 94.3K | Robot vacuums, cordless sticks, air fryers, coffee makers — primary target |
| `Home_and_Kitchen` | `raw_review_Home_and_Kitchen` | 67.4M | 3.7M | Broader coverage including KitchenAid, blenders — secondary target |

**Priority order for R4:** Download `Appliances` first (smaller, more targeted). Add `Home_and_Kitchen` only if Appliances ASIN coverage is insufficient for Ninja kitchen SKUs.

### ASIN filtering strategy

The dataset has no "brand" field on reviews — filter by `parent_asin` against a pre-built ASIN list. Build the ASIN list by:
1. Download `meta_Appliances.jsonl.gz` (metadata file)
2. Filter metadata rows where `brand` field contains "Shark", "Ninja", "Dyson", "iRobot", "Roborock", "KitchenAid"
3. Collect matching `parent_asin` values into a set
4. Filter the reviews file keeping only rows where `parent_asin` is in that set

Known ASIN prefixes for reference (verify against metadata):
- Shark/Ninja products sold under parent company SharkNinja: brand field = "Shark" or "Ninja" or "SharkNinja"
- Dyson: brand = "Dyson"
- iRobot: brand = "iRobot"
- Roborock: brand = "roborock" (lowercase in some entries)

---

## 3. Field Mapping to `Mention` Pydantic Schema

UCSD review schema fields vs. our `Mention` model:

| UCSD field | Type | Maps to `Mention` field | Notes |
|---|---|---|---|
| `rating` | float (1.0-5.0) | `rating` | Direct map |
| `text` | str | `text` | Direct map — run through NLP pipeline |
| `title` | str | prepend to `text` | Concatenate `title + ". " + text` for richer NLP input |
| `parent_asin` | str | `product_model` | Resolve to human SKU name via metadata lookup |
| `user_id` | str | `author_handle` | Hash/anonymize before storing |
| `timestamp` | int (Unix ms) | `posted_at` | Convert: `datetime.fromtimestamp(ts/1000, tz=timezone.utc)` |
| `helpful_vote` | int | not mapped | No field in Mention schema — discard or add optional field |
| `verified_purchase` | bool | not mapped | Could add `Optional[bool]` to Mention in R4 if useful |
| `asin` | str | secondary lookup | Use to cross-ref metadata for product_model name resolution |
| `images` | list | not mapped | Discard |

**Source platform:** hardcode `source_platform = SourcePlatform.amazon` for all UCSD-ingested rows.

**ingested_at:** set to `datetime.now(timezone.utc)` at ingest time.

**mention_id:** generate UUID4 at ingest time — do not use UCSD's user_id or asin as the id.

**brand / category:** resolve from metadata `brand` field → map to our `Brand` enum. `category` requires a manual mapping table (e.g. "Vacuums" → `Category.robot_vacuum` or `Category.cordless_stick` depending on product title keywords).

### Field mapping gaps / conflicts

| Gap | Severity | Resolution |
|---|---|---|
| No `source_url` in UCSD data | Minor | Set `source_url = None` (field is Optional) |
| `product_model` is ASIN, not human name | Medium | Requires metadata join on `parent_asin` to get `title` field |
| `brand` enum mismatch (UCSD uses free-text) | Medium | Write normalization function: `"Shark" → Brand.shark`, `"SharkNinja" → Brand.shark` etc. |
| `category` not directly available | Medium | Infer from product title keywords or metadata `categories` list |
| No `language` field | Minor | Default `language = "en"` (dataset is English-only) |
| `timestamp` is Unix milliseconds | Minor | Divide by 1000 before `datetime.fromtimestamp()` |

---

## 4. Estimated Download Size (Relevant Subsets Only)

Exact compressed file sizes are not published on the dataset page. Estimates based on review counts and token counts:

| Category | Reviews | Approx tokens | Estimated compressed size |
|---|---|---|---|
| `Appliances` | 2.1M | 92.8M | ~0.5-1 GB compressed |
| `Home_and_Kitchen` | 67.4M | 3.1B | ~15-20 GB compressed |
| Metadata `Appliances` | — | 95.3M | ~0.5-1 GB compressed |
| Metadata `Home_and_Kitchen` | — | 3.8B | ~18-25 GB compressed |

**R4 recommended download:** `Appliances` reviews + `Appliances` metadata only = ~1-2 GB total. This covers robot vacuums, cordless sticks, air fryers, coffee makers. Avoid `Home_and_Kitchen` unless ASIN coverage proves insufficient — it is 15-20x larger for limited marginal gain.

---

## 5. Data Recency

- **Hard cap: September 2023.** The dataset covers May 1996 to September 2023. No live updates.
- Last repository update: April 7, 2024 (added index files, not new reviews).
- **Implication for R4:** UCSD data is historical baseline only. For post-Sep-2023 Amazon coverage, no clean legal path exists (see `real_api_integration_proposal.md`). The dashboard should label UCSD-sourced data with a "Historical (pre-Oct 2023)" tag or equivalent to set user expectations.

---

## 6. Licensing Conclusion

**YELLOW LIGHT for R4 commercial demo use.**

**Finding:** The HuggingFace dataset page (`McAuley-Lab/Amazon-Reviews-2023`) shows **no license field** — the license is listed as "Unknown" or absent. The official project site (`amazon-reviews-2023.github.io`) also contains no license statement. The McAuley lab's older 2018 dataset page at `jmcauley.ucsd.edu/data/amazon/` historically stated data was available "for research purposes" — but this language does not appear on the 2023 dataset page.

**Risk assessment:**

| Use case | Risk level | Reasoning |
|---|---|---|
| Internal R&D, academic research, non-public demo | Low | Consistent with the academic release intent; no license = permissive for research by convention |
| Internal demo to SharkNinja team / investors (non-public) | Low-Medium | Not clearly prohibited, but no explicit commercial permission granted |
| Public-facing production dashboard serving paying customers | Medium-High | No license grant for commercial use; underlying reviews are Amazon user content which Amazon's ToS restricts commercial exploitation of |
| SharkNinja client deliverable (billable work product) | Medium-High | Same as above; recommend legal review before this use case |

**Recommended action for R4:** Use UCSD data for demo and prototyping. Before any client-deliverable or production deployment, obtain written clarification from McAuley Lab (contact: yphou@ucsd.edu) on whether commercial demo use is permitted. Do not treat "no license stated" as "commercial use permitted."

---

## 7. R4 Implementation Checklist (for backend-engineer-v4)

- [ ] Download `Appliances.jsonl.gz` and `meta_Appliances.jsonl.gz` from UCSD datarepo
- [ ] Build ASIN set: filter metadata by brand names (Shark, Ninja, SharkNinja, Dyson, iRobot, roborock, KitchenAid)
- [ ] Write `UCSDAdapter(BaseScraper)` in `backend/app/scrapers/ucsd_adapter.py`
  - Stream-reads the JSONL.gz, filters by ASIN set
  - Applies field mapping table from §3 above
  - Resolves `product_model` from metadata title
  - Normalizes `brand` free-text to `Brand` enum
  - Infers `category` from product title keywords
  - Passes `text` through existing NLP pipeline (`analyze()`)
- [ ] Register adapter in `backend/app/scrapers/__init__.py` factory
- [ ] No router changes needed (BaseScraper ABC compliance)
- [ ] Add `Optional[bool] verified_purchase` to `Mention` if deemed useful — requires schema change + contract regen + frontend notification
- [ ] Label ingested rows with a metadata tag indicating UCSD source and pre-Oct-2023 recency

---

*Research conducted 2026-04-11. Dataset hosted at: https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023 and https://datarepo.eng.ucsd.edu/mcauley_group/data/amazon_2023/*
