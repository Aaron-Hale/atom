# Quickstart: ATOM Evidence Retrieval Baselines

## 1. Create Environment

```bash
cd /Users/aaronhale/projects/atom
python3.11 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install fastapi sentence-transformers transformers peft faiss-cpu pytest uvicorn
```

## 2. Prepare Local Data and Artifacts

```bash
mkdir -p data/cuad artifacts/index artifacts/models docs
# Place canonical CUAD contract text files under data/cuad/
```

## 3. Build Deterministic Index

```bash
PYTHONHASHSEED=0 \
python -m atom.cli.index \
  --cuad-dir data/cuad \
  --output-index artifacts/index/cuad.faiss \
  --output-manifest artifacts/index/manifest.json \
  --seed 42
```

## 4. Run Retrieval (Strict Evidence Spans)

```bash
python -m atom.cli.retrieve \
  --query "change of control clause" \
  --mode vector_only \
  --top-k 100 \
  --top-n 10
```

Expected output fields per result: `doc_id`, `chunk_id`, `start`, `end`, `quote`, `score`.

## 5. Train LoRA Reranker Only

```bash
python -m atom.cli.train_reranker_lora \
  --train-split data/splits/train.jsonl \
  --base-reranker-model cross-encoder/ms-marco-MiniLM-L-6-v2 \
  --output-adapter-dir artifacts/models/reranker-lora \
  --seed 42
```

Constraint: embedding model parameters remain frozen; only reranker LoRA adapters are trainable.

## 6. Run Full Comparison Evaluation

```bash
python -m atom.cli.evaluate \
  --splits held_out,hard \
  --modes vector_only,base_reranker,lora_reranker \
  --seed 42 \
  --config-id atom-baseline-v1 \
  --report-path docs/report_2026-03-07.md
```

## 7. Execute Tests

```bash
pytest tests/unit tests/integration tests/regression -q
```

Required checks:
- Offset fidelity (`quote == source_text[start:end]`)
- Schema completeness for required evidence fields
- Mode comparison completeness across three modes and two splits
- Reproducibility tolerance checks for repeated runs
