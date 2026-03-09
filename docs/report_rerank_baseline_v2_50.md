# Reranker Evaluation Report (v2, rerank-candidates=50)

## Experiment
- Generated: 2026-03-08 UTC
- Eval set: `eval/evalset_v1.jsonl` (1903 items)
- Index: `data/faiss.index`
- Metadata: `data/chunk_metadata.jsonl`
- Vector encoder: `sentence-transformers/all-MiniLM-L6-v2`
- Reranker backbone: `cross-encoder/ms-marco-MiniLM-L6-v2`
- Rerank candidates: 50
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
  --rerank-candidates 50 \
  --top-k 3 10 \
  --coverage-k 20 50 100 \
  --reranker-query-mode natural \
  --reranker-vector-weight 0.00 \
  --reranker-boilerplate-penalty 0.00 \
  --report /tmp/report_rr50_natural_baseline.md

# Structured clause + controls
PYTHONPATH=. .venv/bin/python eval/run_retrieval_eval.py \
  --evalset eval/evalset_v1.jsonl \
  --index data/faiss.index \
  --metadata data/chunk_metadata.jsonl \
  --reranker base \
  --rerank-candidates 50 \
  --top-k 3 10 \
  --coverage-k 20 50 100 \
  --reranker-query-mode structured_clause \
  --reranker-vector-weight 0.25 \
  --reranker-boilerplate-penalty 0.35 \
  --reranker-filter-boilerplate \
  --reranker-boilerplate-max-start 1800 \
  --report /tmp/report_rr50_structured_b025_p035_f1.md

# Clause-only + controls (best)
PYTHONPATH=. .venv/bin/python eval/run_retrieval_eval.py \
  --evalset eval/evalset_v1.jsonl \
  --index data/faiss.index \
  --metadata data/chunk_metadata.jsonl \
  --reranker base \
  --rerank-candidates 50 \
  --top-k 3 10 \
  --coverage-k 20 50 100 \
  --reranker-query-mode clause_only \
  --reranker-vector-weight 0.25 \
  --reranker-boilerplate-penalty 0.35 \
  --reranker-filter-boilerplate \
  --reranker-boilerplate-max-start 1800 \
  --report /tmp/report_rr50_clause_b025_p035_f1.md
```

## Variant Comparison (same split/protocol)

| Variant | Query mode | Vec weight | Boilerplate penalty | Filter | Hit@3 | Recall@3 | Hit@10 | Recall@10 |
| --- | --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| Vector-only | n/a | n/a | n/a | n/a | 0.1125 | 0.0831 | 0.2060 | 0.1606 |
| Base reranker baseline | natural | 0.00 | 0.00 | off | 0.0956 | 0.0733 | 0.1950 | 0.1500 |
| Base reranker tuned | structured_clause | 0.25 | 0.35 | on | 0.1240 | 0.0976 | 0.2233 | 0.1774 |
| **Base reranker tuned (best)** | **clause_only** | **0.25** | **0.35** | **on** | **0.1329** | **0.1058** | **0.2291** | **0.1833** |

## Outcome
- Baseline reranker (`natural`, no blend/penalty/filter) regresses vs vector-only.
- With query-mode control + blend + boilerplate control, reranker clearly beats vector-only overall.
- Best overall at `rerank-candidates=50`: `clause_only` + vector weight `0.25` + penalty `0.35` + boilerplate filter on.

## Failure Pattern Check (boilerplate/front-matter)
- Baseline reranker failure examples include rank-1 title-page boilerplate (`chunk_00000`) with SEC/front-matter text.
- Tuned best variant sampled failures no longer show those front-matter `chunk_00000` entries dominating the top rank.
