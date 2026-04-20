---
id: 01_repo_deepread
title: autoresearch Deep Read Notes
tags: [ai-tech, knowledge, karpathy, autoresearch, agent-ml]
status: confirmed
last_modified: 2026-04-15
source: https://github.com/karpathy/autoresearch
summary: Karpathy autoresearch repo 深度解读，AI-agent-driven ML research 最小脚手架
---
# autoresearch — Deep Read Notes
**Source:** https://github.com/karpathy/autoresearch
**Fetch date:** 2026-04-11
**Branch confirmed:** `master` (not `main`)
**Repo stats:** 70.5k stars, 10.3k forks, 9 contributors, 36 commits, MIT license
**Languages:** Python 83.4%, Jupyter Notebook 16.6%
**Active period:** First commits ~early March 2026; latest commit Mar 26 2026 (very fresh)

---

## What This Actually Is

autoresearch is a minimal scaffold for **AI-agent-driven ML research**. The idea: give an LLM agent (Claude, Codex, etc.) a real but small GPT training setup, let it run experiments autonomously overnight, and wake up to a log of kept/discarded experiments and a (hopefully) improved model. Karpathy's framing from the README intro is worth quoting in full:

> "One day, frontier AI research used to be done by meat computers in between eating, sleeping, having other fun, and synchronizing once in a while using sound wave interconnect in the ritual of 'group meeting'. That era is long gone. Research is now entirely the domain of autonomous swarms of AI agents running across compute cluster megastructures in the skies. The agents claim that we are now in the 10,205th generation of the code base, in any case no one could tell if that's right or wrong as the 'code' is now a self-modifying binary that has grown beyond human comprehension. This repo is the story of how it all began. -@karpathy, March 2026"

The core loop in plain terms: **modify train.py → git commit → run for 5 min → check val_bpb → keep or git reset → repeat indefinitely**.

---

## Raw README: Core Passages (verbatim)

### The Idea

> "The idea: give an AI agent a small but real LLM training setup and let it experiment autonomously overnight. It modifies the code, trains for 5 minutes, checks if the result improved, keeps or discards, and repeats. You wake up in the morning to a log of experiments and (hopefully) a better model."

> "The core idea is that you're not touching any of the Python files like you normally would as a researcher. Instead, you are programming the `program.md` Markdown files that provide context to the AI agents and set up your autonomous research org."

### Design Choices (verbatim from README)

> "**Single file to modify.** The agent only touches `train.py`. This keeps the scope manageable and diffs reviewable."

> "**Fixed time budget.** Training always runs for exactly 5 minutes, regardless of your specific platform. This means you can expect approx 12 experiments/hour and approx 100 experiments while you sleep. There are two upsides of this design decision. First, this makes experiments directly comparable regardless of what the agent changes (model size, batch size, architecture, etc). Second, this means that autoresearch will find the most optimal model for your platform in that time budget."

> "**Self-contained.** No external dependencies beyond PyTorch and a few small packages. No distributed training, no complex configs. One GPU, one file, one metric."

---

## File Architecture

```
prepare.py      — constants, data prep + runtime utilities (human sets up once, agent never touches)
train.py        — model, optimizer, training loop (the ONLY file the agent edits)
program.md      — agent instructions (the ONLY file the human iterates on)
pyproject.toml  — dependencies (torch 2.9.1, numpy, pandas, matplotlib, tiktoken; CUDA 12.8)
analysis.ipynb  — post-hoc visualization of results.tsv (run by human after sessions)
results.tsv     — experiment log (created per run, untracked by git, 5 cols: commit/val_bpb/memory_gb/status/description)
progress.png    — visual demo in README
```

**Key design separation:** `prepare.py` is the "constitution" — fixed evaluation, data loading, tokenizer, time budget constant. `train.py` is "the law" — anything in there is fair game for the agent. `program.md` is "the executive order" — what the human tells the agent to optimize for and how to behave.

---

## train.py: Architecture and Code Structure

### GPTConfig dataclass (the model spec)

```python
@dataclass
class GPTConfig:
    sequence_len: int = 2048
    vocab_size: int = 32768
    n_layer: int = 12
    n_head: int = 6
    n_kv_head: int = 6
    n_embd: int = 768
    window_pattern: str = "SSSL"
```

The `SSSL` window pattern is significant: it's alternating banded (Sliding window) vs full (L = full attention) layers. This is a design choice the agent can change.

### Top-level hyperparameter constants (agent's main playground)

```python
ASPECT_RATIO = 64
HEAD_DIM = 128
WINDOW_PATTERN = "SSSL"
TOTAL_BATCH_SIZE = 2**19
EMBEDDING_LR = 0.6
UNEMBEDDING_LR = 0.004
MATRIX_LR = 0.04
SCALAR_LR = 0.5
WEIGHT_DECAY = 0.2
ADAM_BETAS = (0.8, 0.95)
WARMUP_RATIO = 0.0
WARMDOWN_RATIO = 0.5
FINAL_LR_FRAC = 0.0
DEPTH = 8
DEVICE_BATCH_SIZE = 128
```

Note: **no argparse, no config file**. All hyperparameters are module-level constants in train.py, which is why the agent edits the source directly. This is an intentional constraint — simple, reviewable diffs.

### Key model components

- `CausalSelfAttention` — supports both sliding-window (banded) and full attention, controlled by `WINDOW_PATTERN`
- `MLP` — standard feed-forward
- `Block` — attention + MLP with residual
- `GPT` — full transformer stack
- `MuonAdamW` — **custom hybrid optimizer**: Muon updates for 2D weight matrices, AdamW for scalars/embeddings. This is Karpathy bringing in the Muon optimizer from his nanochat work.

Key utility functions:
- `norm(x)` — likely RMSNorm
- `has_ve(layer_idx, n_layer)` — value-embedding variant selector
- `apply_rotary_emb(x, cos, sin)` — RoPE
- `adamw_step_fused` / `muon_step_fused` — fused CUDA kernel optimizer steps
- `build_model_config(depth)` — constructs GPTConfig from DEPTH constant
- `get_lr_multiplier(progress)`, `get_muon_momentum(step)`, `get_weight_decay(progress)` — schedule functions

### Training loop structure

```python
while True:
    # forward + accumulate gradients
    for micro_step in range(grad_accum_steps):
        with autocast_ctx:
            loss = model(x, y)
        loss.backward()
        x, y, epoch = next(train_loader)
    
    # schedule update
    progress = min(total_training_time / TIME_BUDGET, 1.0)
    lrm = get_lr_multiplier(progress)
    # ... update optimizer param groups ...
    optimizer.step()
    
    # termination
    if step > 10 and total_training_time >= TIME_BUDGET:
        break
```

Uses: Flash Attention 3, bfloat16 precision, torch.compile. TIME_BUDGET comes from prepare.py (fixed at 300 seconds).

### End-of-run output (what the agent reads)

```
---
val_bpb:          0.997900
training_seconds: 300.1
total_seconds:    325.9
peak_vram_mb:     45060.2
mfu_percent:      39.80
total_tokens_M:   499.6
num_steps:        953
num_params_M:     50.3
depth:            8
```

---

## prepare.py: The Fixed Foundation

**Constants:**
- `MAX_SEQ_LEN = 2048`
- `TIME_BUDGET = 300` (seconds — this is the wall-clock budget imported by train.py)
- `VOCAB_SIZE = 8192`
- `MAX_SHARD = 6542`
- Cache location: `~/.cache/autoresearch/`

**Key functions:**
- `download_single_shard(index)` / `download_data()` — downloads training data as parquet shards with retry logic
- `train_tokenizer()` — trains BPE tokenizer using rustbpe, wraps as tiktoken encoding
- `make_dataloader()` — BOS-aligned dataloader with best-fit packing for 100% utilization
- `evaluate_bpb()` — the sacred evaluation function; computes cross-entropy bits-per-byte excluding special tokens. **Agent cannot touch this.**
- `class Tokenizer` — wrapper with encode/decode/vocab_size/BOS token

**Important**: `prepare.py` is also the source of `TIME_BUDGET`. The agent cannot change how long training runs — only what happens during those 300 seconds.

---

## program.md: The Agent Operating System (verbatim, key excerpts)

This file is the most intellectually interesting part of the system. It's literally a "skill file" for the agent.

### Setup protocol (verbatim)

> "1. **Agree on a run tag**: propose a tag based on today's date (e.g. `mar5`). The branch `autoresearch/<tag>` must not already exist — this is a fresh run.
> 2. **Create the branch**: `git checkout -b autoresearch/<tag>` from current master.
> 3. **Read the in-scope files**: The repo is small. Read these files for full context..."
> 4. **Verify data exists**... 5. **Initialize results.tsv**..."

### What the agent can/cannot do (verbatim)

> "**What you CAN do:** Modify `train.py` — this is the only file you edit. Everything is fair game: model architecture, optimizer, hyperparameters, training loop, batch size, model size, etc."

> "**What you CANNOT do:** Modify `prepare.py`... Install new packages... Modify the evaluation harness."

### Simplicity criterion (verbatim — one of the most interesting design decisions)

> "All else being equal, simpler is better. A small improvement that adds ugly complexity is not worth it. Conversely, removing something and getting equal or better results is a great outcome — that's a simplification win. When evaluating whether to keep a change, weigh the complexity cost against the improvement magnitude. A 0.001 val_bpb improvement that adds 20 lines of hacky code? Probably not worth it. A 0.001 val_bpb improvement from deleting code? Definitely keep. An improvement of ~0 but much simpler code? Keep."

### The NEVER STOP instruction (verbatim — this is the key autonomous-operation mechanism)

> "**NEVER STOP**: Once the experiment loop has begun (after the initial setup), do NOT pause to ask the human if you should continue. Do NOT ask 'should I keep going?' or 'is this a good stopping point?'. The human might be asleep, or gone from a computer and expects you to continue working *indefinitely* until you are manually stopped. You are autonomous. If you run out of ideas, think harder — read papers referenced in the code, re-read the in-scope files for new angles, try combining previous near-misses, try more radical architectural changes. The loop runs until the human interrupts you, period."

### The experiment loop (verbatim)

> "LOOP FOREVER:
> 1. Look at the git state: the current branch/commit we're on
> 2. Tune `train.py` with an experimental idea by directly hacking the code.
> 3. git commit
> 4. Run the experiment: `uv run train.py > run.log 2>&1` (redirect everything — do NOT use tee or let output flood your context)
> 5. Read out the results: `grep "^val_bpb:\|^peak_vram_mb:" run.log`
> 6. If the grep output is empty, the run crashed. Run `tail -n 50 run.log`...
> 7. Record the results in the tsv...
> 8. If val_bpb improved (lower), you 'advance' the branch, keeping the git commit
> 9. If val_bpb is equal or worse, you git reset back to where you started"

### Crash handling (verbatim)

> "If a run crashes (OOM, or a bug, or etc.), use your judgment: If it's something dumb and easy to fix (e.g. a typo, a missing import), fix it and re-run. If the idea itself is fundamentally broken, just skip it, log 'crash' as the status in the tsv, and move on."

---

## results.tsv: The Experiment Log Schema

Tab-separated (deliberately NOT comma-separated because commas appear in descriptions). 5 columns:

```
commit    val_bpb    memory_gb    status    description
```

Example from program.md:
```
a1b2c3d	0.997900	44.0	keep	baseline
b2c3d4e	0.993200	44.2	keep	increase LR to 0.04
c3d4e5f	1.005000	44.0	discard	switch to GeLU activation
d4e5f6g	0.000000	0.0	crash	double model width (OOM)
```

Importantly: `results.tsv` is **untracked by git** (not committed). The git history itself IS the experiment log for code; results.tsv is the performance log. The agent maintains both separately.

---

## analysis.ipynb: Post-Session Analysis Tool

Six cells:
1. Load results.tsv (pandas, 5 cols)
2. Status distribution: KEEP / DISCARD / CRASH counts + keep rate
3. Print all KEEP experiments with their val_bpb
4. Scatter plot: val_bpb over experiment sequence; discards=faint dots, keeps=green points, running-best=step line, labels=descriptions
5. Summary stats: baseline vs best, percentage improvement
6. Top hits ranked by delta (improvement vs prior state)

This is a human-facing tool, run after the agent session. The agent itself never touches this.

---

## Commit History (recent, from master branch)

| Date | Commit message |
|------|---------------|
| Mar 26 | Merge pull request #342 from kaizen-38/feat/bug-fix |
| Mar 21 | Enhance README with more project context and links |
| Mar 19 | fix(analysis): define best_bpb before y-axis scaling |
| Mar 16 | add AMD ROCm fork to notable forks section |
| Mar 11 | Guard against infinite loop when no training shards exist |
| Mar 11 | fix NaN loss not caught by fast-fail check |
| Mar 9 | Include beginner's guide to neural networks |
| Mar 8 | reshuffle readme a bit and link to tiny stories |
| Mar 7 | Honor --download-workers instead of hardcoding 8 |
| Mar 7 | Fix agent crash blindspot by forcing it to read traceback |
| Mar 6 | add analysis notebook for convenience |

Key signal from commit history: the project is ~5 weeks old (first commits early March 2026). Active bug-fixing phase. "Fix agent crash blindspot by forcing it to read traceback" is interesting — Karpathy had to patch program.md or the code to make the agent reliably read failure output rather than ignoring it.

---

## Dependencies (pyproject.toml)

- torch 2.9.1 (CUDA 12.8 wheels from download.pytorch.org/whl/cu128)
- numpy, pandas, matplotlib, tiktoken
- Python >= 3.10
- Package manager: `uv` (Astral's fast Python package manager)

Very lean stack. No Hugging Face, no complex framework dependencies.

---

## What a First-Time User Would Run

```bash
# 1. Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Clone and install deps
git clone https://github.com/karpathy/autoresearch
cd autoresearch
uv sync

# 3. One-time data prep (~2 min)
uv run prepare.py

# 4. Test that training works manually
uv run train.py
# wait 5 minutes, check terminal output for val_bpb

# 5. Launch agent in autonomous mode
# Open Claude/Codex in this directory, grant code execution permissions, then prompt:
# "Have a look at program.md and let's kick off a new experiment! Let's do the setup first."
# The agent will propose a branch name, read the files, initialize results.tsv, and begin the loop.
```

The agent then runs indefinitely. Kill it manually when done. Run `jupyter notebook analysis.ipynb` to review results.

---

## Reading Notes & A-Ha Moments

### 1. program.md IS the research methodology
The most original insight in this repo is that **the human's job is to write the agent's operating procedure, not to run the experiments**. `program.md` is a protocol document that Karpathy explicitly calls a "super lightweight skill." The human iterates on `program.md` the same way they'd iterate on a research team's standard operating procedures. This is a genuinely new model of how humans direct AI research labor.

### 2. Git as the agent's undo/redo memory
The agent uses `git reset` to "discard" failed experiments and advances the branch commit-by-commit when experiments succeed. This is elegant: git history becomes a permanent record of which architectural decisions actually worked. The results.tsv gives you the metrics; the diff between consecutive kept commits gives you the exact code change that produced each improvement.

### 3. Context hygiene: redirecting output to run.log
The instruction `uv run train.py > run.log 2>&1` and then `grep "^val_bpb:\|^peak_vram_mb:" run.log` to extract results is explicitly to "not let output flood your context." This is Karpathy solving the same problem Vincent's system solves — keeping the agent's working memory clean. The agent needs to survive 100 experiments in a single session; if it read full training logs each time it'd exhaust context in 10 runs.

### 4. Simplicity criterion as anti-overfitting
The "simpler is better, all else being equal" instruction is functionally Occam's Razor applied to code complexity. Without it, an AI agent would naturally accumulate hacks (much like human researchers do under publish-or-perish pressure). Karpathy is encoding "don't overfit the experimental setup" directly into the agent's value function.

### 5. Fixed time budget solves comparability AND platform-specificity simultaneously
Because TIME_BUDGET=300 is fixed and comes from prepare.py (agent cannot change it), all experiments are directly comparable regardless of model size or architecture changes. A bigger model with the same val_bpb doesn't "win" — it just uses more memory for the same result. This is clever metric design.

### 6. The "NEVER STOP" instruction is load-bearing
Without explicit instruction to never pause, LLM agents naturally insert confirmation checkpoints. Karpathy explicitly anticipates this ("the human might be asleep") and removes the agent's permission to pause. This transforms the agent from an interactive assistant into an autonomous worker. It's a behavioral constraint baked into the protocol, not the code.

### 7. The data is a pre-trained web corpus, not a toy dataset
`MAX_SHARD = 6542` shards of parquet data, custom BPE tokenizer trained on the data. This is real-scale NLP training data, just with a small model (DEPTH=8, ~50M params). The task is genuinely meaningful: compress natural language as efficiently as possible in 5 minutes.

### 8. MuonAdamW optimizer — cutting-edge
The custom `MuonAdamW` combining Muon (orthogonal gradient updates for weight matrices) with AdamW (for scalars/embeddings) is state-of-the-art optimizer research. The agent can change optimizer configuration, which means it could theoretically rediscover aspects of good optimizer design experimentally.

---

## What the "Research Loop" Actually Looks Like in Code

1. Agent reads `program.md` → understands the protocol
2. Agent creates a git branch `autoresearch/<date>`
3. Agent reads `prepare.py`, `train.py`, `README.md` for full context
4. Agent writes `results.tsv` header
5. **Loop begins:**
   - Agent edits train.py (e.g., changes `DEPTH = 8` to `DEPTH = 10`, or modifies the attention pattern, or tweaks learning rates)
   - `git commit -m "increase depth to 10"`
   - `uv run train.py > run.log 2>&1` (blocks for ~5min 20sec)
   - `grep "^val_bpb:\|^peak_vram_mb:" run.log` → get metric
   - If improved: write `a1b2c3d   0.9912   44.1   keep   increase depth to 10` to results.tsv
   - If worse: `git reset --hard HEAD~1`, write `a1b2c3d   0.9980   44.1   discard   increase depth to 10`
   - Repeat

The branch walks forward through successful experiments only. Failed experiments leave no trace in git (only in results.tsv). Human interrupts the loop manually.

---

## Open Questions / Unresolved

1. **What dataset is actually used?** The parquet shards are downloaded but the source URL isn't visible from the README or prepare.py summary. Likely a Common Crawl or FineWeb derivative given the entropy comment ("a lot less entropy" for TinyStories vs default).

2. **What does the default baseline val_bpb actually look like?** The example shows `0.997900` but that's the program.md example, not a real run. No actual results.tsv is committed to the repo.

3. **Flash Attention 3 kernel fallback:** The README mentions the parent nanochat repo has a Flash Attention 3 fallback. Is there one here? Unclear. Might mean the code simply crashes on non-H100 hardware without modification.

4. **How does the agent handle the ~25 second startup/compilation time?** `total_seconds: 325.9` vs `training_seconds: 300.1` suggests ~25 sec overhead per run. Over 100 runs that's ~40 minutes of overhead. Not a problem but worth knowing.

5. **Multi-agent extension:** Karpathy mentions "how you'd add more agents to the mix" as obvious future work. No code for this exists yet. Each agent would need its own branch. Coordination mechanism undefined.

6. **Agent permission scope:** README says "disable all permissions" when spinning up the agent. What this means exactly depends on the Claude/Codex UI. For Claude Code specifically, this would mean no web search, presumably.

7. **Does the agent actually use paper citations?** The NEVER STOP instruction says "read papers referenced in the code" when stuck. Are there paper references in train.py? Not visible from the summary — possibly in comments.

---

## Relevance to Vincent's Projects

**For MeowOS / BaseOS architecture thinking:**
- The `program.md as skill file` pattern is directly applicable. Vincent's system already uses CLAUDE.md + agent prompts; autoresearch shows a more minimal version of the same idea where the protocol IS the product.
- The context hygiene approach (redirect to log, grep only key metrics) is a pattern worth importing for any agent loop that might run many iterations.
- The `results.tsv + git history = dual experiment log` pattern is elegant for tracking iterative AI work.

**For understanding AI knowledge structures (Vincent's stated interest):**
- autoresearch is a concrete example of how an AI agent accumulates "knowledge" through iteration: the git branch IS the accumulated knowledge. No explicit KB; the code diff IS the knowledge representation.
- The simplicity criterion is a form of knowledge compression — the agent is instructed to prefer lower-complexity representations of the same performance.
- This is worth comparing to Vincent's own KB-first approach in MeowOS: autoresearch uses no explicit knowledge base at all; the artifact (train.py) IS the knowledge store.

**Limitations for Vincent's use case:**
- Requires NVIDIA GPU (H100 tested). Not directly runnable without the hardware.
- The domain is pure ML training optimization — the loop doesn't generalize to other research domains out of the box. program.md would need substantial rewriting to adapt to, e.g., business strategy or historical research.
- The 5-minute time budget is specifically calibrated to LLM training. Different domains need different feedback cycle designs.

---

## KB file path
`D:\Ai_Project\MeowOS\80_Knowledge\84_AI_Tech\autoresearch_2026-04-11\01_repo_deepread.md`
