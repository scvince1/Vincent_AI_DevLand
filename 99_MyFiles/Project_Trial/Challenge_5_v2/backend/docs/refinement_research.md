# NLP Refinement Research

**Purpose:** This document feeds round 2+ refinement decisions for the SharkNinja sentiment pipeline. It is NOT code changes — it is the research that informs what changes to make and in what order. Each section addresses one xfail in `backend/tests/test_nlp_robustness.py`. All recommendations are constrained to the project's no-transformer rule: spaCy `en_core_web_sm` + VADER + deterministic rule-based logic only.

---

## Topic 1 — Rhetorical Question Sentiment Inversion

### Problem restated
The pipeline scores "How am I supposed to love a vacuum that cannot handle pet hair?" as positive because `love` dominates the VADER signal. Rhetorical questions in product reviews are nearly always negative in intent, and the current rules have no interrogative-form awareness.

### State-of-art approaches
1. **Rhetorical structure theory (RST) + discourse trees** (arxiv 1704.05228): deep neural approach that labels clauses by rhetorical role; effective but requires transformer-level models — not compatible with our constraints.
2. **Computational detection of rhetorical figures** (arxiv 2406.16674): surveys rule-based cue patterns for lesser-known rhetorical devices including rhetorical questions; confirms that WH-word + negation cues can be assembled into rule sets without training data.
3. **Negation + WH-interrogative surface pattern**: the lightest-weight approach — detect sentence-final `?`, check for WH-opener (`how`, `why`, `who`, `what`, `when`, `where`) AND a negation signal in the same clause. This is purely syntactic and has no model dependency.

### Lightweight option compatible with our constraints
**Surface pattern rule**: if text ends with `?` AND starts with a WH-word AND contains a negation token (`not`, `cannot`, `can't`, `supposed to`, `never`, `why would`) — invert the compound score and override `overall_sentiment` to `negative`. Add this as Rule R5 in `sarcasm.py` (it is semantically a sarcasm/irony variant). No model needed; fully deterministic and testable.

### Implementation sketch
```python
WH_OPENERS = {"how", "why", "who", "what", "when", "where"}
RQ_NEGATION = {"not", "cannot", "can't", "supposed to", "never", "wouldn't", "why would"}

def _is_rhetorical_negative(text: str, lower: str) -> bool:
    if not lower.rstrip().endswith("?"):
        return False
    first_word = lower.split()[0] if lower.split() else ""
    if first_word not in WH_OPENERS:
        return False
    return any(neg in lower for neg in RQ_NEGATION)

# In detect_sarcasm(), add Rule R5:
if _is_rhetorical_negative(text, lower) and neg_signal_count >= 1:
    return True, 0.78
```

### References
- [Computational Approaches to Detection of Lesser-Known Rhetorical Figures (arxiv 2406.16674)](https://arxiv.org/html/2406.16674v1)
- [Sentiment Analysis based on Rhetorical Structure Theory (arxiv 1704.05228)](https://arxiv.org/abs/1704.05228)
- [IAE: Irony-based Adversarial Examples for Sentiment Analysis (arxiv 2411.07850)](https://arxiv.org/html/2411.07850v1)

---

## Topic 2 — Multi-Party Comparative Sentiment (3+ Brands)

### Problem restated
The current JJR-based extractor finds at most one `than`-clause per comparative adjective, so "Shark has better navigation than iRobot but worse suction than Dyson" only yields two pairs (shark/dyson on navigation) rather than four. The iRobot pair in the coordinated `but`-clause is missed.

### State-of-art approaches
1. **Jindal & Liu (AAAI 2006 / SIGIR 2006)**: foundational comparative sentence mining using class sequential rules + keyword strategy. Defines the tuple `(relation, features, entity_A, entity_B)` and explicitly handles coordination — "Canon's optics are better than Sony and Nikon" is parsed as one relation with two B-entities. Directly applicable as a rule extension.
2. **Ganapathibhotla & Liu (COLING 2008)**: extends the Jindal/Liu framework to opinion polarity per comparative pair — determines which entity benefits from each comparative. Available at [aclanthology.org/C08-1031.pdf](https://aclanthology.org/C08-1031.pdf).
3. **Graph-based multi-hop**: builds a directed graph of entity-aspect-polarity triples; overkill for our rule-based pipeline.

### Lightweight option compatible with our constraints
**Clause splitting + per-clause JJR extraction**: before running the comparative extractor, split on coordination conjunctions (`but`, `and`, `however`) using the existing `_split_into_clauses()` from `absa.py`. Run the JJR dep-walk independently on each clause. This is a 5-line change to `comparative.py`'s main loop and requires no new models.

### Implementation sketch
```python
# In extract_comparative_pairs(), before the existing spaCy walk:
from backend.app.nlp.absa import _split_into_clauses

all_pairs = []
for clause in _split_into_clauses(text):
    clause_doc = nlp(clause) if nlp else None
    all_pairs.extend(_extract_pairs_from_doc(clause_doc, clause))

# _extract_pairs_from_doc = current per-sentence JJR walk logic, extracted
# Dedup pairs by (brand, aspect) before returning
```

### References
- [Jindal & Liu — Mining Comparative Sentences and Relations (AAAI 2006)](https://www.cs.uic.edu/~liub/publications/aaai06-comp-relation.pdf)
- [Ganapathibhotla & Liu — Mining Opinions in Comparative Sentences (COLING 2008)](https://aclanthology.org/C08-1031.pdf)
- [Identifying Comparative Sentences in Text Documents (SIGIR 2006)](https://www.cs.uic.edu/~liub/publications/sigir06-comp.pdf)

---

## Topic 3 — Sarcasm Cue Lexicon Expansion

### Problem restated
The current `SARCASM_POSITIVE_CUES` set has ~20 entries covering common words like `great`, `amazing`, `wow`. Cue words like `brilliant`, `stellar`, `what a gem`, `flawless` are missing, causing the `sarcasm_brilliant_cue` xfail. The question is whether a principled, data-driven cue list exists in the literature.

### State-of-art approaches
1. **Riloff et al. EMNLP 2013** — "Sarcasm as Contrast between a Positive Sentiment and Negative Situation": bootstrapping algorithm that iteratively discovers positive sentiment verbs and negative situation phrases from labeled sarcastic tweets. The positive verb list (love, enjoy, adore, appreciate, cherish, relish, savor...) is directly applicable as a cue expansion. Paper and lists available at [cs.arizona.edu/~riloff](http://www2.cs.arizona.edu/~riloff/pdfs/official-emnlp13-sarcasm.pdf).
2. **Davidov, Tsur & Rappoport (CoNLL 2010)**: semi-supervised recognition on Amazon reviews and Twitter; extracted sarcasm patterns include: high-sentiment intensifier + failure-description template. Achieves 77% precision on Amazon reviews. Available at [semanticscholar.org](https://www.semanticscholar.org/paper/Semi-Supervised-Recognition-of-Sarcasm-in-Twitter-Davidov-Tsur/5c558dd46d9915c7335e045f9b4d1db0eb3bdfc9).
3. **Filatova (AAAI)**: sarcasm as sentiment flow shift — identifies inflection points where sentiment polarity reverses within a short span. Useful as a complement to cue-lexicon approach for catching cases without explicit positive openers.

### Lightweight option compatible with our constraints
**One-time cue list expansion** from Riloff's bootstrapped positive verb list + VADER's existing positive lexicon filtered to score >= 2.0. Add ~30 entries to `SARCASM_POSITIVE_CUES`: `brilliant`, `stellar`, `flawless`, `what a gem`, `absolutely perfect`, `love it`, `fantastic`, `genius`, `masterpiece`, `superb engineering`, `top notch`. No model required; test-driven addition of entries to the existing set in `domain_lexicon.py`.

### Implementation sketch
```python
# Additions to SARCASM_POSITIVE_CUES in domain_lexicon.py:
SARCASM_POSITIVE_CUES |= {
    "brilliant", "stellar", "flawless", "genius", "masterpiece",
    "what a gem", "absolutely perfect", "top notch", "superb engineering",
    "love it", "works perfectly", "best purchase", "best decision",
    # Riloff positive verb set (adapted for product context):
    "enjoy", "adore", "appreciate", "cherish", "relish",
}
# R3 opener pattern already catches "Oh brilliant," — just needs
# "brilliant" in SARCASM_POSITIVE_CUES to fire on mid-sentence use via R1/R4.
```

### References
- [Riloff et al. — Sarcasm as Contrast between Positive Sentiment and Negative Situation (EMNLP 2013)](http://www2.cs.arizona.edu/~riloff/pdfs/official-emnlp13-sarcasm.pdf)
- [Davidov, Tsur & Rappoport — Semi-Supervised Recognition of Sarcasm in Twitter and Amazon (CoNLL 2010)](https://www.semanticscholar.org/paper/Semi-Supervised-Recognition-of-Sarcasm-in-Twitter-Davidov-Tsur/5c558dd46d9915c7335e045f9b4d1db0eb3bdfc9)
- [Filatova — Sarcasm Detection Using Sentiment Flow Shifts (AAAI)](https://cdn.aaai.org/ocs/15480/15480-68660-1-PB.pdf)
- [Automatic Sarcasm Detection: A Survey (arxiv 1602.03426)](https://arxiv.org/pdf/1602.03426)

---

## Topic 4 — Idiomatic Negative Expressions in Product Reviews

### Problem restated
"The dustbin is a joke" scores positive because `joke` is not in `STRONG_NEGATIVES` and the copular dep-walk finds no negative opinion token. Common idioms (`a joke`, `a nightmare`, `a disaster`, `a mess`, `a lemon`) carry strong implicit negative sentiment but are invisible to lexicon-based scorers.

### State-of-art approaches
1. **SLIDE — Sentiment Lexicon of Common Idioms (LREC 2018, IBM Research)**: 5,000 frequently occurring English idioms with crowdsourced sentiment annotations (10 annotators per idiom). Over 40% are sentiment-bearing. Publicly available via IBM Developer Exchange. Directly downloadable and usable as a static lookup table. [aclanthology.org/L18-1379.pdf](https://aclanthology.org/L18-1379.pdf), [IBM Developer](https://developer.ibm.com/exchanges/data/all/sentiment-lexicon-of-idiomatic-expressions/).
2. **MWE polarity via linguistic features** (Cambridge NLE): uses Wiktionary + unigram sentiment + MWE internal structure features to determine polarity of verbal MWEs. More complex to operationalize but provides principled coverage.
3. **Curated idiom extension to STRONG_NEGATIVES**: the minimal approach — manually add ~60-80 product-review-relevant idiomatic forms directly to `STRONG_NEGATIVES` in `absa.py`, filtered from SLIDE's negative subset. One-time effort, zero model dependency, immediately testable.

### Lightweight option compatible with our constraints
**Static idiom sub-lexicon** added to `STRONG_NEGATIVES` in `absa.py`. Source: filter SLIDE's publicly available list for product-review-relevant negatives (a joke, a nightmare, a disaster, a mess, a waste of money, a lemon, a dud, a letdown, fell apart, stopped working, gave up, broke down). Score range: -0.55 to -0.75 depending on severity. ~60 entries covers the most common product-review idioms.

### Implementation sketch
```python
# Additions to STRONG_NEGATIVES in absa.py:
IDIOM_NEGATIVES: Dict[str, float] = {
    "a joke": -0.70,
    "a nightmare": -0.75,
    "a disaster": -0.75,
    "a mess": -0.65,
    "a waste of money": -0.80,
    "a lemon": -0.70,
    "a dud": -0.65,
    "a letdown": -0.60,
    "gave up": -0.55,
    "fell apart": -0.70,
    "stopped working": -0.65,
    "broke down": -0.65,
    "piece of junk": -0.80,
    "waste of time": -0.70,
}
STRONG_NEGATIVES.update(IDIOM_NEGATIVES)
# No other changes needed — existing multi-word phrase matching in _score_clause()
# already handles multi-word lookups via `if phrase in lower`.
```

### References
- [SLIDE — Sentiment Lexicon of Common Idioms (LREC 2018)](https://aclanthology.org/L18-1379.pdf)
- [IBM Developer Exchange — SLIDE download](https://developer.ibm.com/exchanges/data/all/sentiment-lexicon-of-idiomatic-expressions/)
- [Determining sentiment views of verbal MWEs (Cambridge NLE)](https://www.cambridge.org/core/journals/natural-language-engineering/article/determining-sentiment-views-of-verbal-multiword-expressions-using-linguistic-features/B992222E564C948CE90EA7238C0E9195)
- [Multiword Expressions: A Pain in the Neck for NLP](https://www.researchgate.net/publication/221628861_Multiword_Expressions_A_Pain_in_the_Neck_for_NLP)

---

## Topic 5 — NER-Aware Verb-Driven Comparative Structure Resolution

### Problem restated
"The Roomba j7+ beats the Shark IQ on obstacle avoidance" — `Roomba` is correctly aliased to `irobot` via `BRAND_ALIASES`, but the comparative extractor only walks JJR (comparative adjective) dependency arcs. `beats` is a verb (`VBZ`) with `nsubj=Roomba` and `dobj=Shark`, so the JJR walk never fires and no pairs are emitted.

### State-of-art approaches
1. **Jindal & Liu verb-based comparative patterns**: their keyword list explicitly includes comparative verbs (`beats`, `outperforms`, `surpasses`, `tops`, `crushes`, `exceeds`, `leads`, `dominates`). The subject of these verbs is entity A (winner), direct object is entity B (loser). Polarity: subject=positive, object=negative. Straightforward dep-parse extraction via spaCy `nsubj` + `dobj` on root verb.
2. **Phrase-level dependency parsing for opinion mining** (Zhao et al., EMNLP 2009, [aclanthology.org/D09-1159.pdf](https://aclanthology.org/D09-1159.pdf)): phrase-level dep-parse extracts (feature, opinion) pairs; can be adapted to extract (entity_A, entity_B, comparative_verb) triples.
3. **Entity-aware dep-parse pattern matching**: for each token with `pos_=VERB` and `lemma_` in a `COMPARATIVE_VERBS` set, walk `nsubj` child → resolve brand alias, walk `dobj` child → resolve brand alias. Assign positive polarity to nsubj-brand and negative to dobj-brand. Extend `comparative.py` with this as a parallel extraction path alongside the existing JJR walk.

### Lightweight option compatible with our constraints
**Verb-comparative extractor** added as a second pass in `extract_comparative_pairs()` in `comparative.py`. Define a `COMPARATIVE_VERBS` set of ~15 win-verbs (`beats`, `outperforms`, `surpasses`, `tops`, `crushes`, `exceeds`, `leads`, `dominates`, `outclasses`, `trounces`) and ~10 loss-verbs (`loses to`, `trails`, `lags behind`, `falls short of`). For win-verbs: nsubj=positive, dobj=negative. For loss-verbs: nsubj=negative, dobj=positive. Brand alias resolution via the existing `BRAND_ALIASES` dict.

### Implementation sketch
```python
COMPARATIVE_WIN_VERBS = {
    "beat", "outperform", "surpass", "top", "crush", "exceed",
    "lead", "dominate", "outclass", "trounce", "trump"
}
COMPARATIVE_LOSS_VERBS = {"trail", "lag", "lose"}

def _extract_verb_comparative_pairs(doc, text: str) -> List[dict]:
    pairs = []
    for token in doc:
        if token.lemma_.lower() not in COMPARATIVE_WIN_VERBS | COMPARATIVE_LOSS_VERBS:
            continue
        win = token.lemma_.lower() in COMPARATIVE_WIN_VERBS
        subj_brand = _find_brand_in_subtree(token, dep="nsubj")
        obj_brand = _find_brand_in_subtree(token, dep="dobj")
        aspect = _find_aspect_in_prep(token)  # walk "on X" prep phrase
        if subj_brand and obj_brand:
            pairs.append({"brand": subj_brand, "aspect": aspect,
                          "polarity": "positive" if win else "negative", "score": 0.6})
            pairs.append({"brand": obj_brand, "aspect": aspect,
                          "polarity": "negative" if win else "positive", "score": -0.6})
    return pairs
```

### References
- [Jindal & Liu — Mining Comparative Sentences and Relations (AAAI 2006)](https://www.cs.uic.edu/~liub/publications/aaai06-comp-relation.pdf)
- [Phrase Dependency Parsing for Opinion Mining (EMNLP 2009)](https://aclanthology.org/D09-1159.pdf)
- [Extracting Comparative Entities and Predicates from Texts (ACL 2011)](https://aclanthology.org/P11-1164.pdf)
- [spaCy Linguistic Features — Dependency Parsing](https://spacy.io/usage/linguistic-features)

---

## Prioritized Implementation Queue

Ranking by **effort vs xfail-coverage gain**. "Effort" = estimated lines of code + test additions. "Coverage gain" = number of xfails converted to passing + spillover benefit to edge cases not yet tested.

| Rank | Topic | Effort | xFails Fixed | Spillover Benefit | Verdict |
|------|-------|--------|--------------|-------------------|---------|
| 1 | **T4 — Idiom lexicon** (`STRONG_NEGATIVES` additions) | ~20 lines (no logic change, data only) | 1 direct (`dustbin is a joke`) | Fixes any review using "a nightmare", "a disaster", "a lemon", "piece of junk" — high frequency in real reviews | **Do first. Highest ROI.** |
| 2 | **T3 — Sarcasm cue expansion** (`SARCASM_POSITIVE_CUES` additions) | ~15 lines (data only) | 1 direct (`sarcasm_brilliant_cue`) | Broader sarcasm recall on any review using `brilliant`, `stellar`, `genius` as sarcastic opener | **Do second. Trivial effort, good judge story.** |
| 3 | **T1 — Rhetorical question Rule R5** (new rule in `sarcasm.py`) | ~15 lines (1 new function + 1 rule branch) | 1 direct (`rhetorical_question_negative`) | Handles "Why would anyone buy X?", "How is this acceptable?", "Who designed this?" — common reviewer patterns | **Do third. Small rule, deterministic, adds a new detectable phenomenon.** |
| 4 | **T5 — Verb-driven comparative extractor** (new pass in `comparative.py`) | ~40 lines (new function + COMPARATIVE_VERBS set) | 1 direct (`roomba_brand_alias_comparative`) | Resolves any "X beats/outperforms Y" pattern — directly serves the competitive intelligence use case (Priya P3 persona) | **Do fourth. Moderate effort, high demo value for the competitive analysis page.** |
| 5 | **T2 — Clause-split 3-brand comparative** (refactor `comparative.py` main loop) | ~30 lines (refactor + dedup logic) | 1 direct (`three_brand_four_pairs`) | Better multi-brand sentences, which are common in head-to-head review posts | **Do last. Depends on T5 being stable first; refactoring the main loop carries regression risk.** |

**Round 2 recommendation:** T4 + T3 together as one PR (pure data additions, zero logic risk). T1 as a second PR (one new rule). T5 + T2 as a third PR after T1 is stable. Total estimated effort across all 5: ~120 lines of code + ~10 new test assertions to convert xfails to passing.
