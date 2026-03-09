# ATOM: Agentic Tuning, Optimization, and MLOps

ATOM is a portfolio project for legal contract understanding built on CUAD-derived contract data. The repository focuses on reproducible retrieval, reranking, and domain-adapted LoRA fine-tuning for clause evidence detection.

**Naming note:** “Agentic” in ATOM reflects the development workflow and project direction. This repository was built in an agent-assisted workflow (including Spec Kit and Codex), while the current implemented artifacts focus on legal retrieval, reranking, and LoRA fine-tuning rather than a deployed agent runtime.

The project contains two primary tracks:

1. **Retrieval and reranking over contract chunks**
2. **Clause-conditioned LoRA fine-tuning for legal evidence detection**

The implementation emphasizes deterministic data construction, document-level split control, held-out evaluation, and comparison against strong baselines.

---

## Overview

Legal contract understanding often combines multiple stages:

- document preprocessing and chunking
- semantic retrieval over chunked text
- reranking of retrieved candidates
- task-specific classification or scoring

ATOM implements these stages locally using CUAD-derived data and evaluates them with reproducible artifacts and reports.

---

## Repository Highlights

### Retrieval and reranking

This track includes:

- deterministic export of contract text and labels
- offset-preserving chunking with stable chunk IDs
- local embedding and FAISS indexing
- held-out retrieval evaluation
- off-the-shelf reranker baselines
- LoRA reranker experiments
- candidate coverage diagnostics and ablation reports

### LoRA fine-tuning

This repository also includes a clause-conditioned binary detector trained with LoRA.

Task definition:

> Given a clause type and a chunk of contract text, predict whether the chunk contains evidence for that clause.

This formulation produced the strongest fine-tuning result in the repository and serves as the main LoRA artifact.

---

## Final LoRA Artifact: Clause-Conditioned Binary Detector

### Task

Input:
- clause type prompt
- chunk text

Output:
- binary prediction indicating whether the chunk contains evidence for the specified clause type

### Input format

- `text_a`: `Clause type: <clause_type>. Does this chunk contain evidence for this clause?`
- `text_b`: chunk text

### Labeling policy

- label `1` if a chunk overlaps any annotated span for the target clause type in the same document
- label `0` otherwise

### Split policy

- deterministic document-level split using a SHA1 bucket over `doc_id`
- no document leakage across train and validation

### Negative construction

Training negatives are generated deterministically from a mix of:

- nearby same-document non-overlap negatives
- same-document non-overlap negatives
- cross-document hard negatives
- clause-absent document negatives

---

## Results

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

The clause-conditioned binary detector is the strongest fine-tuning result in the repository. On the held-out validation split, the LoRA model improves over both:

- a lexical baseline
- a non-fine-tuned pretrained baseline

This provides a clear example of domain-adapted LoRA fine-tuning on legal contract data.

---

## Reranker Track Summary

The reranker work remains an important part of the repository.

Key outcomes include:

- improved retrieval quality from chunking and indexing changes
- a tuned off-the-shelf reranker that outperformed vector-only retrieval
- LoRA reranker experiments that improved over vector-only retrieval and approached the tuned base reranker, but did not consistently exceed it overall

This track is included as a retrieval and ranking artifact rather than the primary fine-tuning artifact.

---

## Demo / Inference

A local demo script is included for the clause-conditioned binary detector.

### Direct text mode

```bash
.venv/bin/python scripts/run_clause_binary_demo.py \
  --clause-type assignment \
  --text "Neither party may assign this Agreement without prior written consent..."
```

### File mode

```bash
.venv/bin/python scripts/run_clause_binary_demo.py \
  --clause-type termination \
  --text-file path/to/example.txt
```

### Output

The demo prints:

- `predicted_probability`
- `predicted_label`
- `model_path`
- `clause_type`

Additional usage details are documented in:

- `docs/clause_binary_demo.md`

---

## Key Artifacts

### Retrieval / reranking

- `data/faiss.index`
- `data/chunk_metadata.jsonl`
- `eval/run_retrieval_eval.py`
- `docs/report_retrieval_baseline.md`
- `docs/report_rerank_baseline_v2_20.md`
- `docs/report_rerank_baseline_v2_50.md`
- `docs/report_lora_reranker_v3.md`

### Clause-conditioned binary LoRA detector

- `scripts/build_clause_binary_dataset.py`
- `train/train_clause_binary_lora.py`
- `eval/eval_clause_binary_lora.py`
- `scripts/run_clause_binary_demo.py`
- `data/clause_binary_train.jsonl`
- `data/clause_binary_val.jsonl`
- `models/clause_binary_lora/`
- `docs/train_log_clause_binary_lora.md`
- `docs/report_clause_binary_lora.md`
- `docs/clause_binary_demo.md`

---

## Repository Structure

```text
app/
  services/
    rerank.py
    retrieve.py

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
  clause_binary_demo.md
  progress_log.md
  rerank_dataset.md
  report_clause_binary_lora.md
  report_lora_reranker_v1.md
  report_lora_reranker_v2.md
  report_lora_reranker_v3.md
  report_rerank_baseline.md
  report_rerank_baseline_v2_20.md
  report_rerank_baseline_v2_50.md
  report_retrieval_baseline.md
  train_log_clause_binary_lora.md
  train_log_lora_v1.md
  train_log_lora_v2.md

eval/
  eval_clause_binary_lora.py
  evalset_v1.jsonl
  run_retrieval_eval.py

models/
  clause_binary_lora/
  reranker_lora/
  reranker_lora_v2/
  reranker_lora_v3/

scripts/
  build_clause_binary_dataset.py
  build_evalset.py
  build_index.py
  build_rerank_dataset.py
  chunk_contracts.py
  export_cuad.py
  run_clause_binary_demo.py

train/
  train_clause_binary_lora.py
  train_reranker_lora.py

tests/
  test_chunking.py
```

---

## Reproducibility Notes

The repository is designed to be reproducible where practical:

- deterministic chunk construction
- deterministic dataset generation
- document-level train/validation split control
- explicit reports for major experiments
- saved LoRA adapters and training logs

Some generated artifacts in `data/` and `models/` are committed for inspection and reproducibility.

---

## Recommended Entry Points

For a quick review, start with:

1. `docs/report_clause_binary_lora.md`
2. `docs/train_log_clause_binary_lora.md`
3. `docs/clause_binary_demo.md`
4. `docs/report_rerank_baseline_v2_50.md`
5. `docs/report_lora_reranker_v3.md`
6. `docs/progress_log.md`

---

## Current Status

The repository currently contains:

- a complete retrieval and reranking pipeline over contract chunks
- multiple reranker baselines and LoRA reranker experiments
- a clause-conditioned binary LoRA detector with a clear held-out improvement over baseline systems
- a local demo script for direct inference

The most natural next step is lightweight productization, such as:

- integrating retrieval and clause evidence scoring
- expanding example-driven demos
- adding a small service layer around the detector
