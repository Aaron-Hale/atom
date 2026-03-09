# LoRA v2 Training Log

## Run
- Date (UTC): 2026-03-08
- Script: `train/train_reranker_lora.py`
- Base model: `cross-encoder/ms-marco-MiniLM-L6-v2`
- Train file: `data/rerank_train_v2.jsonl`
- Val file: `data/rerank_val_v2.jsonl`
- Output dir: `models/reranker_lora_v2`
- Seed: `42`

## Command
```bash
PYTHONPATH=. .venv/bin/python train/train_reranker_lora.py \
  --train-file data/rerank_train_v2.jsonl \
  --val-file data/rerank_val_v2.jsonl \
  --output-dir models/reranker_lora_v2 \
  --base-model cross-encoder/ms-marco-MiniLM-L6-v2 \
  --num-train-epochs 1.0 \
  --per-device-train-batch-size 16 \
  --per-device-eval-batch-size 32 \
  --learning-rate 2e-4 \
  --weight-decay 0.01 \
  --seed 42 \
  --save-load-parity-check \
  --parity-slice-size 128 \
  --parity-batch-size 32
```

## Dataset size
- Train samples: `13,554`
- Val samples: `4,053`

## Hyperparameters
- LoRA: `r=16`, `alpha=32`, `dropout=0.1`, target modules `query,value`
- Max length: `512`
- LR: `2e-4`
- Weight decay: `0.01`
- Epochs: `1.0`

## Training result
- Train loss: `0.4429`
- Train runtime: `797.488s`
- Train steps/sec: `1.063`

## Validation result
- Eval loss: `0.1508`
- Accuracy: `0.9585`
- Precision: `0.9441`
- Recall: `0.9388`
- F1: `0.9414`

## Save/load parity check
- Enabled: yes
- Slice size: `128`
- Max abs diff: `0.0`
- Mean abs diff: `0.0`
- P95 abs diff: `0.0`
- `allclose`: `true`

## Artifacts written
- `models/reranker_lora_v2/adapter_config.json`
- `models/reranker_lora_v2/adapter_model.safetensors`
- `models/reranker_lora_v2/run_summary.json`
- tokenizer and trainer state files under `models/reranker_lora_v2/`
