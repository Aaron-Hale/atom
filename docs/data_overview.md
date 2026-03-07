# Data Overview

`python scripts/export_cuad.py` exports a deterministic canonical local data store from CUAD into:

- `data/contracts.jsonl`: one row per contract with `{doc_id, text}`.
- `data/labels.jsonl`: one row per `(doc_id, clause_type)` with `{doc_id, clause_type, spans:[{start,end}]}`.

Data source behavior:

- Default: loads CUAD JSON from Hugging Face via `datasets` (`hf://datasets/kenlevine/CUAD/CUAD_v1.json`).
- Optional override: `--cuad-path /path/to/CUAD_v1.json`.
- The script fails with a clear actionable error if CUAD cannot be loaded.
- The script also fails if export would be empty (non-zero contracts and labels are required).

The exporter uses a fixed clause taxonomy `CLAUSE_TYPES_V1`:

- `assignment`
- `change_of_control`
- `confidentiality`
- `exclusivity`
- `governing_law`
- `limitation_of_liability`
- `most_favored_nation`
- `non_compete`
- `termination`
- `warranty`

Determinism and fidelity notes:

- `doc_id` is stable from CUAD source identifiers (hash-backed).
- Span offsets are preserved from CUAD `answer_start` and answer text length.
- Output rows are sorted deterministically before writing.
- Clause mapping resolves from both `qa.id` and `qa.question`, with normalization and aliases.
- The script fails clearly if any selected `CLAUSE_TYPES_V1` member is unavailable in CUAD
  question/id fields, rather than silently exporting it as zero.
- Script prints source and exported contract count, then explicitly separates:
  - label rows (`doc_id+clause_type` rows in `labels.jsonl`)
  - per-clause mapped QA entry counts
  - per-clause label row counts
  - per-clause span counts (individual answer spans)
