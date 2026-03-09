# ATOM: Agentic Tuning, Optimization, and MLOps

ATOM is a portfolio project for legal contract understanding built on CUAD-derived data. The repo demonstrates two complementary tracks:

1. Retrieval / reranking system design
2. Domain-specific LoRA fine-tuning

The goal is not just to train models, but to build a reproducible pipeline with deterministic data construction, honest baselines, and clear evaluation.

---

## What this repo demonstrates

### 1) Retrieval / reranking track

This track shows end-to-end retrieval engineering over contract text:

- deterministic export from CUAD into canonical local artifacts
- deterministic chunking with stable chunk IDs and preserved offsets
- local embedding + FAISS indexing
- retrieval evaluation over a held-out clause-oriented eval set
- reranker ablations and tuning
- LoRA reranker experiments with honest comparison against strong baselines

This track proves systems thinking, evaluation rigor, and the judgment to distinguish between:
- improvements from retrieval/indexing changes
- improvements from reranking
- improvements from fine-tuning

### 2) LoRA fine-tuning track

This repo also includes a clause-conditioned binary legal chunk detector trained with LoRA.

This was added after observing that LoRA reranker experiments improved over vector-only retrieval but did not clearly beat a carefully tuned off-the-shelf reranker overall. Rather than forcing the wrong conclusion, the project pivoted to a cleaner supervised task that better demonstrates practical fine-tuning skill.

The final binary detector asks:

> Given a clause type and a chunk of contract text, does this chunk contain evidence for that clause?

This produced a clear and defensible LoRA win over both lexical and non-fine-tuned pretrained baselines.

---

## Final LoRA artifact: clause-conditioned binary detector

### Task

Input:
- clause type prompt
- chunk text

Output:
- binary label indicating whether the chunk contains evidence for that clause

### Input format

- `text_a`: `Clause type: <clause_type>. Does this chunk contain evidence for this clause?`
- `text_b`: chunk text

### Labeling policy

- `1` if a chunk overlaps any labeled span for that clause type in the same document
- `0` otherwise

### Split policy

- deterministic doc-level split using SHA1 bucket over `doc_id`
- no document leakage across train/validation

### Negative construction

Deterministic negatives include:
- nearby same-doc non-overlap negatives
- same-doc non-overlap negatives
- cross-doc hard negatives
- clause-absent document negatives

---

## Key results

### Clause-conditioned binary detector (validation)

| Model | PR-AUC | ROC-AUC | F1 |
|---|---:|---:|---:|
| Lexical baseline | 0.4702 | 0.7793 | 0.5804 |
| Pretrained baseline (non-fine-tuned) | 0.4791 | 0.7463 | 0.5212 |
| **LoRA** | **0.6956** | **0.8664** | **0.6346** |

### Macro positive-class metrics over clause types

| Model | Macro PR-AUC | Macro F1 |
|---|---:|---:|
| Lexical baseline | 0.3808 | 0.4440 |
| Pretrained baseline (non-fine-tuned) | 0.3882 | 0.3817 |
| **LoRA** | **0.5294** | **0.4794** |

### Interpretation

The LoRA binary detector is the strongest fine-tuning artifact in the repo because it clearly improves over:
- a lexical baseline
- a non-fine-tuned pretrained baseline

This supports a strong portfolio claim:

> Built a clause-conditioned legal chunk detector and fine-tuned a LoRA adapter that improved PR-AUC, ROC-AUC, and F1 over lexical and non-fine-tuned baselines on held-out contract data.

---

## Reranker track summary

The reranker work remains valuable and stays in the repo as a separate artifact.

Highlights:
- improved retrieval via chunking/indexing changes
- tuned off-the-shelf reranker became the strongest overall reranking baseline
- LoRA reranker v3 nearly matched the tuned base reranker and beat vector-only retrieval, but did not clearly beat the tuned base overall

That result is still useful because it demonstrates:
- proper baseline construction
- ablations
- candidate coverage analysis
- pairwise fine-tuning attempts
- honest evaluation rather than overstated claims

---

## Repository structure

    app/
      services/
        rerank.py

    data/
      contracts.jsonl
      labels.jsonl
      chunks.jsonl
      chunk_metadata.jsonl
      faiss.index
      rerank_*.jsonl
      clause_binary_train.jsonl
      clause_binary_val.jsonl

    docs/
      chunking.md
      rerank_dataset.md
      report_retrieval_baseline.md
      report_rerank_baseline*.md
      report_lora_reranker*.md
      report_clause_binary_lora.md
      train_log_lora_v2.md
      train_log_clause_binary_lora.md
      progress_log.md

    eval/
      run_retrieval_eval.py
      eval_clause_binary_lora.py

    models/
      reranker_lora_v2/
      reranker_lora_v3/
      clause_binary_lora/

    scripts/
      export_cuad.py
      chunk_contracts.py
      build_index.py
      build_evalset.py
      build_rerank_dataset.py
      build_clause_binary_dataset.py

    train/
      train_reranker_lora.py
      train_clause_binary_lora.py

---

## Main artifacts

### Retrieval / reranking artifacts

- `data/faiss.index`
- `data/chunk_metadata.jsonl`
- `eval/run_retrieval_eval.py`
- `docs/report_retrieval_baseline.md`
- `docs/report_rerank_baseline_v2_20.md`
- `docs/report_rerank_baseline_v2_50.md`
- `docs/report_lora_reranker_v3.md`

### LoRA binary detector artifacts

- `scripts/build_clause_binary_dataset.py`
- `train/train_clause_binary_lora.py`
- `eval/eval_clause_binary_lora.py`
- `data/clause_binary_train.jsonl`
- `data/clause_binary_val.jsonl`
- `models/clause_binary_lora/`
- `docs/train_log_clause_binary_lora.md`
- `docs/report_clause_binary_lora.md`

---

## Why this project is portfolio-worthy

This repo is not just "I trained a model."

It shows:
- deterministic dataset construction
- reproducible train/validation splits
- indexing and retrieval engineering
- hard-negative strategy
- honest baseline comparison
- LoRA fine-tuning on domain-specific legal data
- the ability to pivot when an experiment is technically interesting but not the strongest artifact

That combination is much more credible than a single cherry-picked training run.

---

## Recommended entry points

If you are reviewing this repo, start here:

1. `docs/report_clause_binary_lora.md`
2. `docs/train_log_clause_binary_lora.md`
3. `docs/report_rerank_baseline_v2_50.md`
4. `docs/report_lora_reranker_v3.md`
5. `docs/progress_log.md`

---

## Current status

The repo now contains:

- a strong retrieval / reranking artifact
- a successful clause-conditioned binary LoRA fine-tuning artifact
- clean commit history separating:
  - reranker improvements
  - final LoRA binary detector artifact

The next likely phase is lightweight productization:
- inference/demo layer for the binary detector
- integration of retrieval + clause evidence scoring
- cleaner user-facing examples
