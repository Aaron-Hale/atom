# CLI Contract: Evaluation and Training

## Command: `atom index`

- Purpose: Build FAISS index from canonical CUAD documents and chunk mappings.
- Required args:
  - `--cuad-dir <path>`
  - `--output-index <path>`
  - `--output-manifest <path>`
  - `--seed <int>`
- Exit criteria:
  - Writes deterministic index + manifest with dataset checksum.

## Command: `atom retrieve`

- Purpose: Return strict evidence spans for one query.
- Required args:
  - `--query <text>`
  - `--mode vector_only|base_reranker|lora_reranker`
  - `--top-k <int>`
  - `--top-n <int>`
- Output contract:
  - JSON array/object where each record includes `doc_id`, `chunk_id`, `start`, `end`, `quote`, `score`.
  - No prose answer field allowed.

## Command: `atom evaluate`

- Purpose: Run baseline-vs-improved evaluation across all modes and splits.
- Required args:
  - `--splits held_out,hard`
  - `--modes vector_only,base_reranker,lora_reranker`
  - `--seed <int>`
  - `--config-id <id>`
  - `--report-path docs/report_<stamp>.md`
- Output contract:
  - Metrics table includes `nDCG@10`, `MRR@10`, `Recall@50` for each mode/split cell.
  - Includes reproducibility metadata: dataset version, split checksums, model IDs, seed.

## Command: `atom train-reranker-lora`

- Purpose: Fine-tune reranker with LoRA adapters only.
- Required args:
  - `--train-split <path>`
  - `--base-reranker-model <id/path>`
  - `--output-adapter-dir <path>`
  - `--seed <int>`
- Scope guardrails:
  - Must not update embedding model weights.
  - Must emit training config and adapter artifact IDs for report traceability.
