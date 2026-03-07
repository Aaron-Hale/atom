# Data Model: ATOM Evidence Retrieval Baselines

## Entity: ContractDocument

- Description: Canonical CUAD contract text source used for retrieval and offset validation.
- Fields:
  - `doc_id` (string, required, unique): stable contract identifier.
  - `source_path` (string, required): local file path to canonical text.
  - `text` (string, required): normalized canonical document text.
  - `text_checksum` (string, required): checksum for reproducibility and drift detection.
- Validation Rules:
  - `doc_id` must be non-empty and globally unique.
  - `text` length must be > 0.
- Relationships:
  - One `ContractDocument` has many `EvidenceChunk`.

## Entity: EvidenceChunk

- Description: Retrieval unit derived from one contract document.
- Fields:
  - `chunk_id` (string, required): unique chunk identifier scoped to `doc_id`.
  - `doc_id` (string, required): foreign key to `ContractDocument.doc_id`.
  - `chunk_text` (string, required): text content indexed in FAISS.
  - `chunk_start` (integer, required): character start offset in canonical document.
  - `chunk_end` (integer, required): character end offset in canonical document (exclusive).
- Validation Rules:
  - Composite uniqueness: (`doc_id`, `chunk_id`).
  - `0 <= chunk_start < chunk_end <= len(document.text)`.
  - `chunk_text == document.text[chunk_start:chunk_end]`.
- Relationships:
  - Many `EvidenceChunk` belong to one `ContractDocument`.
  - One `EvidenceChunk` can map to many `EvidenceResult` across queries/modes.

## Entity: ClauseQuery

- Description: User-supplied clause search input for retrieval/evaluation.
- Fields:
  - `query_id` (string, required for eval; optional ad-hoc): stable identifier in eval runs.
  - `query_text` (string, required): clause query text.
  - `split` (enum: `held_out`, `hard`, optional): evaluation split membership.
- Validation Rules:
  - `query_text` must be non-empty after trim.
  - Query length must satisfy configured max character threshold.

## Entity: EvidenceResult

- Description: Ranked evidence-span output record returned by API/CLI.
- Fields:
  - `doc_id` (string, required)
  - `chunk_id` (string, required)
  - `start` (integer, required): char start offset in canonical document.
  - `end` (integer, required): char end offset in canonical document (exclusive).
  - `quote` (string, required): exact substring at `[start, end)`.
  - `score` (float, required): ranking score for selected mode.
  - `mode` (enum, required): `vector_only`, `base_reranker`, `lora_reranker`.
  - `provenance` (object, required): includes retrieval model ID, reranker model ID (if any), index version, run ID.
- Validation Rules:
  - Required schema fields from FR-006 must always be present and non-null.
  - `0 <= start < end <= len(document.text)`.
  - `quote == document.text[start:end]`.
  - `doc_id` and `chunk_id` must resolve to existing source entities.

## Entity: EvaluationRun

- Description: Deterministic execution record for one mode on one split.
- Fields:
  - `run_id` (string, required, unique)
  - `mode` (enum, required): `vector_only`, `base_reranker`, `lora_reranker`
  - `split` (enum, required): `held_out`, `hard`
  - `seed` (integer, required)
  - `dataset_version` (string, required)
  - `config_id` (string, required)
  - `metrics` (object, required): includes `ndcg@10`, `mrr@10`, `recall@50`.
  - `timestamp_utc` (string, required)
- Validation Rules:
  - Exactly one run per (`mode`, `split`, `config_id`, `seed`) per execution pass.
  - Metrics must be numeric and finite.

## Entity: EvaluationReport

- Description: Markdown report artifact for baseline-vs-improved comparisons.
- Fields:
  - `report_path` (string, required): `docs/report_*.md`.
  - `compared_runs` (list[run_id], required): covers all 3 modes x 2 splits.
  - `protocol_summary` (string, required)
  - `variance_check` (object, required): repeated-run deltas + threshold.
- Validation Rules:
  - Must include all comparison cells before claim is considered valid.
  - Must include seed/split/config/model identifiers.

## State Transitions

- `ContractDocument`: `ingested -> indexed -> validated`.
- `EvidenceChunk`: `generated -> indexed -> retrievable`.
- `EvaluationRun`: `planned -> running -> completed -> reported` (or `failed`).
- `EvaluationReport`: `drafted -> reviewed -> committed`.
