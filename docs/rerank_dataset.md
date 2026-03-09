# Reranker Dataset Construction (v2)

## Scope
Dataset v2 was rebuilt from the improved retrieval-stage artifacts (`data/faiss.index` + `data/chunk_metadata.jsonl`) with deterministic query/candidate policies aligned to the tuned reranker setup.

## Inputs
- Eval set: `eval/evalset_v1.jsonl`
- Metadata: `data/chunk_metadata.jsonl`
- FAISS index: `data/faiss.index`
- Encoder: `sentence-transformers/all-MiniLM-L6-v2`

## v2 generation command
```bash
PYTHONPATH=. .venv/bin/python scripts/build_rerank_dataset.py \
  --evalset eval/evalset_v1.jsonl \
  --metadata data/chunk_metadata.jsonl \
  --index data/faiss.index \
  --train-out data/rerank_train_v2.jsonl \
  --val-out data/rerank_val_v2.jsonl \
  --query-mode clause_only \
  --vector-top-k 50 \
  --hard-negatives-per-query 4 \
  --same-doc-negatives-per-query 2 \
  --val-ratio 0.2
```

## Deterministic policies
- Eval rows sorted by `id`.
- Split by `sha1(doc_id)` bucket (`val_ratio=0.2`) to avoid doc leakage.
- Query mode for training rows: `clause_only` (`"<clause_type> clause"`).
- Positives: same-document chunk overlaps expected span.
- Hard negatives: top-50 vector-retrieved cross-doc non-overlap chunks, with front-matter/boilerplate skip near document start (`boilerplate_max_start=1800`).
- Same-doc negatives: non-overlap chunks in deterministic offset order.
- Final rows sorted by `(query_id, label, chunk_id)`.

## v2 outputs
- `data/rerank_train_v2.jsonl` (13,554 rows)
- `data/rerank_val_v2.jsonl` (4,053 rows)

## v2 class balance
- Train: positives `4,753`, negatives `8,801`, positive rate `0.350671`
- Val: positives `1,438`, negatives `2,615`, positive rate `0.354799`

## Compatibility note
- v1 files are not overwritten: `data/rerank_train.jsonl` and `data/rerank_val.jsonl` remain untouched.
