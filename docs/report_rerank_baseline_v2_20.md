# Reranker Evaluation Report (v2, rerank-candidates=20)

## Experiment
- Generated: 2026-03-08 UTC
- Eval set: `eval/evalset_v1.jsonl` (1903 items)
- Index: `data/faiss.index`
- Metadata: `data/chunk_metadata.jsonl`
- Vector encoder: `sentence-transformers/all-MiniLM-L6-v2`
- Reranker backbone: `cross-encoder/ms-marco-MiniLM-L6-v2`
- Rerank candidates: 20
- Top-K metrics: Hit@3 / Recall@3 and Hit@10 / Recall@10
- Determinism: same dataset/index/configs; no stochastic training in this eval path

## Commands

```bash
# Natural baseline (previous behavior)
PYTHONPATH=. .venv/bin/python eval/run_retrieval_eval.py \
  --evalset eval/evalset_v1.jsonl \
  --index data/faiss.index \
  --metadata data/chunk_metadata.jsonl \
  --reranker base \
  --rerank-candidates 20 \
  --top-k 3 10 \
  --coverage-k 20 50 100 \
  --reranker-query-mode natural \
  --reranker-vector-weight 0.00 \
  --reranker-boilerplate-penalty 0.00 \
  --report /tmp/report_rr20_natural_baseline.md

# Natural + controls
PYTHONPATH=. .venv/bin/python eval/run_retrieval_eval.py \
  --evalset eval/evalset_v1.jsonl \
  --index data/faiss.index \
  --metadata data/chunk_metadata.jsonl \
  --reranker base \
  --rerank-candidates 20 \
  --top-k 3 10 \
  --coverage-k 20 50 100 \
  --reranker-query-mode natural \
  --reranker-vector-weight 0.25 \
  --reranker-boilerplate-penalty 0.35 \
  --reranker-filter-boilerplate \
  --reranker-boilerplate-max-start 1800 \
  --report /tmp/report_rr20_natural_b025_p035_f1.md

# Structured clause + controls
PYTHONPATH=. .venv/bin/python eval/run_retrieval_eval.py \
  --evalset eval/evalset_v1.jsonl \
  --index data/faiss.index \
  --metadata data/chunk_metadata.jsonl \
  --reranker base \
  --rerank-candidates 20 \
  --top-k 3 10 \
  --coverage-k 20 50 100 \
  --reranker-query-mode structured_clause \
  --reranker-vector-weight 0.25 \
  --reranker-boilerplate-penalty 0.35 \
  --reranker-filter-boilerplate \
  --reranker-boilerplate-max-start 1800 \
  --report /tmp/report_rr20_structured_b025_p035_f1.md

# Clause-only + controls (best)
PYTHONPATH=. .venv/bin/python eval/run_retrieval_eval.py \
  --evalset eval/evalset_v1.jsonl \
  --index data/faiss.index \
  --metadata data/chunk_metadata.jsonl \
  --reranker base \
  --rerank-candidates 20 \
  --top-k 3 10 \
  --coverage-k 20 50 100 \
  --reranker-query-mode clause_only \
  --reranker-vector-weight 0.25 \
  --reranker-boilerplate-penalty 0.35 \
  --reranker-filter-boilerplate \
  --reranker-boilerplate-max-start 1800 \
  --report /tmp/report_rr20_clause_b025_p035_f1.md
```

## Variant Comparison (same split/protocol)

| Variant | Query mode | Vec weight | Boilerplate penalty | Filter | Hit@3 | Recall@3 | Hit@10 | Recall@10 |
| --- | --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| Vector-only | n/a | n/a | n/a | n/a | 0.1125 | 0.0831 | 0.2060 | 0.1606 |
| Base reranker baseline | natural | 0.00 | 0.00 | off | 0.1009 | 0.0755 | 0.2007 | 0.1558 |
| Base reranker tuned | natural | 0.25 | 0.35 | on | 0.1156 | 0.0858 | 0.2118 | 0.1659 |
| Base reranker tuned | structured_clause | 0.25 | 0.35 | on | 0.1203 | 0.0926 | 0.2160 | 0.1707 |
| **Base reranker tuned (best)** | **clause_only** | **0.25** | **0.35** | **on** | **0.1308** | **0.1025** | **0.2176** | **0.1731** |

## Outcome
- Baseline reranker (`natural`, no blend/penalty/filter) regresses vs vector-only.
- Adding query-mode control + blend + boilerplate control recovers and exceeds vector-only.
- Best overall at `rerank-candidates=20`: `clause_only` + vector weight `0.25` + penalty `0.35` + boilerplate filter on.

## Failure Pattern Check (boilerplate/front-matter)
- Baseline reranker failure examples still include rank-1 `chunk_00000` front-matter/title-page content (e.g., lines containing `EXHIBIT` and `Confidential Treatment Requested`).
- Tuned best variant failure examples no longer show those `chunk_00000` title-page/SEC boilerplate hits in the top-ranked failures sampled in the report.
