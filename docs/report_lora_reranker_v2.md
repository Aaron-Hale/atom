# LoRA v2 Reranker Evaluation Report

## Experiment
- Date (UTC): 2026-03-08
- Eval set: `eval/evalset_v1.jsonl` (1903 items)
- Index: `data/faiss.index`
- Metadata: `data/chunk_metadata.jsonl`
- Candidate depth: `rerank-candidates=50`
- Query mode: `clause_only`
- Score blending: `vector_weight=0.25`
- Boilerplate controls: `penalty=0.35`, filter enabled, `max_start=1800`
- Methods compared: vector-only vs tuned base vs LoRA v2

## Eval command
```bash
PYTHONPATH=. .venv/bin/python eval/run_retrieval_eval.py \
  --evalset eval/evalset_v1.jsonl \
  --index data/faiss.index \
  --metadata data/chunk_metadata.jsonl \
  --reranker lora \
  --reranker-model cross-encoder/ms-marco-MiniLM-L6-v2 \
  --lora-adapter models/reranker_lora_v2 \
  --rerank-candidates 50 \
  --top-k 3 10 \
  --coverage-k 20 50 100 \
  --reranker-query-mode clause_only \
  --reranker-vector-weight 0.25 \
  --reranker-boilerplate-penalty 0.35 \
  --reranker-filter-boilerplate \
  --reranker-boilerplate-max-start 1800 \
  --report /tmp/report_lora_reranker_v2_eval.md
```

## Overall results

| Method | Hit@3 | Recall@3 | Hit@10 | Recall@10 |
| --- | ---: | ---: | ---: | ---: |
| Vector-only | 0.1125 | 0.0831 | 0.2060 | 0.1606 |
| Tuned base reranker | 0.1329 | 0.1058 | 0.2291 | 0.1833 |
| LoRA v2 reranker | 0.1109 | 0.0813 | 0.2212 | 0.1714 |

## Deltas vs vector-only
- Tuned base: `+0.0205` Hit@3, `+0.0231` Hit@10
- LoRA v2: `-0.0016` Hit@3, `+0.0152` Hit@10

## Deltas vs tuned base
- LoRA v2: `-0.0220` Hit@3, `-0.0079` Hit@10
- LoRA v2: `-0.0245` Recall@3, `-0.0119` Recall@10

## Conclusion
- LoRA v2 **does not beat** the tuned base reranker on the held-out eval at `rerank-candidates=50`.
- Tuned base remains the best-performing reranker configuration in this comparison.
- LoRA v2 still improves over vector-only at @10, but regresses at @3 and underperforms tuned base overall.

## Notes
- Comparison is on the same eval split/protocol and same tuned retrieval/rerank controls.
- Adapter used: `models/reranker_lora_v2/`.
