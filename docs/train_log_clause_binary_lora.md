# Clause-Conditioned Binary LoRA Train Log

## Scope
- New in-repo artifact for clause-conditioned binary evidence detection.
- Existing reranker and multiclass clause-classifier artifacts were left untouched.

## Dataset construction
Inputs:
- `data/chunks.jsonl`
- `data/labels.jsonl`

Builder command:
```bash
PYTHONPATH=. .venv/bin/python scripts/build_clause_binary_dataset.py \
  --chunks data/chunks.jsonl \
  --labels data/labels.jsonl \
  --train-out data/clause_binary_train.jsonl \
  --val-out data/clause_binary_val.jsonl \
  --val-ratio 0.2
```

Label policy:
- Input pair format:
  - `text_a`: `Clause type: <clause_type>. Does this chunk contain evidence for this clause?`
  - `text_b`: chunk text
- Label `1`: chunk overlaps any span for that `clause_type` in the same `doc_id`.
- Label `0`: no overlap for that `clause_type`.

Negative policy (deterministic):
- `nearby_same_doc`: nearest same-doc non-overlap chunks around each positive.
- `same_doc_non_overlap`: additional same-doc non-overlap negatives with stable hash ordering.
- `cross_doc_hard`: cross-doc negatives ranked by clause keyword hits.
- `clause_absent_doc`: small quota from (doc, clause) pairs with no positives.

Split policy:
- Deterministic doc-level split from SHA1 bucket on `doc_id`.

Observed dataset summary:
- Train rows: `22813` (pos `4753`, neg `18060`)
- Val rows: `6778` (pos `1438`, neg `5340`)
- Clause types: assignment, change_of_control, confidentiality, exclusivity, governing_law, limitation_of_liability, most_favored_nation, non_compete, termination, warranty

## LoRA training
Train command:
```bash
PYTHONPATH=. .venv/bin/python train/train_clause_binary_lora.py \
  --train-file data/clause_binary_train.jsonl \
  --val-file data/clause_binary_val.jsonl \
  --output-dir models/clause_binary_lora \
  --base-model cross-encoder/ms-marco-MiniLM-L6-v2 \
  --num-train-epochs 1.0 \
  --per-device-train-batch-size 32 \
  --per-device-eval-batch-size 64 \
  --max-length 256 \
  --learning-rate 2e-4 \
  --weight-decay 0.01 \
  --seed 42
```

From `models/clause_binary_lora/run_summary.json`:
- Train runtime: `1099.68s`
- Train loss: `0.4051`
- Eval PR-AUC: `0.6956`
- Eval ROC-AUC: `0.8664`
- Eval F1: `0.6416`
- Eval precision: `0.5970`
- Eval recall: `0.6933`

Saved artifact:
- `models/clause_binary_lora/adapter_model.safetensors`
- `models/clause_binary_lora/adapter_config.json`
- `models/clause_binary_lora/run_summary.json`

## 3-way evaluation command
```bash
PYTHONPATH=. .venv/bin/python eval/eval_clause_binary_lora.py \
  --train-file data/clause_binary_train.jsonl \
  --val-file data/clause_binary_val.jsonl \
  --base-model cross-encoder/ms-marco-MiniLM-L6-v2 \
  --adapter models/clause_binary_lora \
  --report docs/report_clause_binary_lora.md \
  --max-length 256 \
  --batch-size 64 \
  --threshold-train-max 20000 \
  --error-examples 12
```
