# LoRA Reranker Training Log (v1)

- Date (UTC): 2026-03-08
- Script: `train/train_reranker_lora.py`
- Base backbone: `cross-encoder/ms-marco-MiniLM-L6-v2`
- Train split: `data/rerank_train.jsonl`
- Validation split: `data/rerank_val.jsonl`
- Output dir: `models/reranker_lora/`

## Command

```bash
.venv/bin/python train/train_reranker_lora.py --num-train-epochs 1 --allow-remote-download
```

## Dataset Sizes

- Train samples: `12502`
- Validation samples: `3719`

## Hyperparameters

- Seed: `42`
- Epochs: `1.0`
- Max length: `512`
- Learning rate: `2e-4`
- Weight decay: `0.01`
- Warmup ratio: `0.05`
- Train batch size (device): `16`
- Eval batch size (device): `32`
- Gradient accumulation: `1`
- Metric threshold: `0.5`
- LoRA task type: `SEQ_CLS`
- LoRA rank (`r`): `16`
- LoRA alpha: `32`
- LoRA dropout: `0.1`
- LoRA target modules: `query,value`
- LoRA modules to save: `classifier` (classifier head preserved)

## Validation Metrics

- `eval_loss`: `0.3844`
- `eval_accuracy`: `0.8365`
- `eval_precision`: `0.8672`
- `eval_recall`: `0.5443`
- `eval_f1`: `0.6688`

## Train Runtime

- `train_runtime`: `981.921s`
- `train_samples_per_second`: `12.732`
- `train_steps_per_second`: `0.796`
- `train_loss`: `0.5207`

## Saved Artifacts

- Adapter weights/config: `models/reranker_lora/adapter_model.safetensors`, `models/reranker_lora/adapter_config.json`
- Tokenizer artifacts: `models/reranker_lora/tokenizer.json`, `models/reranker_lora/tokenizer_config.json`
- Training state for reproducibility: `models/reranker_lora/training_args.bin`, `models/reranker_lora/trainer_state.json`, `models/reranker_lora/run_summary.json`
- Checkpoints: `models/reranker_lora/checkpoint-32/`, `models/reranker_lora/checkpoint-782/`

## Inference Load Check

Adapter load sanity check passed with:

- Base model: `cross-encoder/ms-marco-MiniLM-L6-v2`
- Adapter path: `models/reranker_lora/`
- Output logits shape: `(1, 1)`
