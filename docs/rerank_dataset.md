# Reranker Dataset Construction (Day 9)

This document describes how `scripts/build_rerank_dataset.py` constructs deterministic pointwise reranker training data for ATOM.

## Inputs

- Eval set: `eval/evalset_v1.jsonl`
- Chunk store metadata: `data/chunk_metadata.jsonl`
- Vector retriever index: `data/faiss.index`
- Vector encoder: `sentence-transformers/all-MiniLM-L6-v2`

## Output format

Each JSONL row uses pointwise format:

```json
{"query": "...", "text": "...", "label": 0|1, "meta": {...}}
```

`meta` preserves provenance and offsets (`query_id`, `query_doc_id`, `clause_type`, `chunk_id`, `chunk_doc_id`, `chunk_start`, `chunk_end`, `expected_spans`) and includes `negative_type` for negatives.

## Labeling rules

For each eval query:

1. Positives (`label=1`):
- Candidate chunks are from the same `doc_id` as the query.
- A chunk is positive if its `[start, end)` overlaps any expected span in `expected_spans`.

2. Hard negatives (`label=0`, `negative_type="hard"`):
- Run vector retrieval over the full index (top `--vector-top-k`, default `20`).
- Keep top retrieved chunks that do **not** overlap expected spans and come from a different `doc_id`.
- Skip obviously filing/header boilerplate chunks (e.g., SEC confidentiality/table-of-contents boilerplate) using deterministic marker checks.
- Keep up to `--hard-negatives-per-query` (default `4`), preserving retrieval rank order.

3. Same-document negatives (`label=0`, `negative_type="same_doc"`):
- From the query’s own `doc_id`, select chunks that do not overlap expected spans.
- Keep up to `--same-doc-negatives-per-query` (default `2`) in deterministic chunk order `(start, end, chunk_id)`.

Queries with zero positive chunks are skipped.

## Split policy (deterministic)

Train/validation split is by `doc_id` only.

- Compute `sha1(doc_id)`.
- Convert first 8 hex chars to a bucket in `[0,1)`.
- Put the entire `doc_id` into validation if bucket `< --val-ratio` (default `0.2`), else train.

This prevents document leakage across splits and is stable across runs.

## Reproducibility

Determinism comes from:

- Sorted eval query order by `id`
- Deterministic same-doc chunk ordering
- Fixed retrieval `top_k` and fixed per-query negative caps
- Deterministic boilerplate marker filtering for hard negatives
- Hash-based `doc_id` split
- Sorted final output rows by `(query_id, label, chunk_id)`

## Run command

```bash
.venv/bin/python scripts/build_rerank_dataset.py
```

## Current dataset stats

Generated files:

- `data/rerank_train.jsonl`
- `data/rerank_val.jsonl`

Counts from the latest run:

- Train: total `12502`, positives `3735`, negatives `8767`, positive rate `0.298752`, hard negatives `5834`, same-doc negatives `2933`
- Val: total `3719`, positives `1128`, negatives `2591`, positive rate `0.303307`, hard negatives `1721`, same-doc negatives `870`
