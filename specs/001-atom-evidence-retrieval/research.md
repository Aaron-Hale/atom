# Research: ATOM Evidence Retrieval Baselines

## Decision 1: Core Runtime Stack

- Decision: Use Python 3.11 with FastAPI, sentence-transformers, transformers, peft, faiss-cpu, pytest.
- Rationale: Matches requested stack, has mature local tooling for retrieval/reranking pipelines, and supports deterministic evaluation scripts plus contract tests.
- Alternatives considered: Python 3.12 (newer but more package compatibility risk), Flask + custom validation (less explicit API contracts), PyTorch-only custom embedding stack (more maintenance burden).

## Decision 2: Local-First Retrieval Architecture

- Decision: Keep all indexing, retrieval, reranking, and evaluation artifacts on local filesystem (`data/`, `artifacts/`, `docs/`).
- Rationale: Satisfies constitution local-first principle and reduces operational complexity while enabling reproducible local reruns.
- Alternatives considered: Managed vector DB (adds infra and non-local dependency), hybrid cloud evaluation (violates local-first default).

## Decision 3: Evidence Span Fidelity Contract

- Decision: Canonical evidence record schema is exactly `doc_id`, `chunk_id`, `start`, `end`, `quote`, `score` with optional provenance metadata; enforce `[start, end)` exact quote match.
- Rationale: Directly implements FR-006 through FR-009 and EV-001/EV-002, allowing auditable source-grounded outputs.
- Alternatives considered: Token-offset schema (harder to align with char offsets required by spec), answer-style outputs (out-of-scope).

## Decision 4: Retrieval and Reranking Pipeline

- Decision: Use sentence-transformers embeddings + FAISS for candidate generation, then rerank the same candidate set in two modes: base transformer reranker and LoRA-adapted reranker.
- Rationale: Preserves comparable protocol across modes and isolates ranking changes for measurable before/after claims.
- Alternatives considered: End-to-end cross-encoder only (too slow for baseline candidate generation), BM25 baseline only (does not meet requested vector baseline scope).

## Decision 5: LoRA Scope Control

- Decision: Apply PEFT LoRA fine-tuning only to reranker model modules; enforce configuration check that embedding model parameters remain frozen and untouched.
- Rationale: Meets FR-015 and prevents scope drift into embedding-model fine-tuning.
- Alternatives considered: Joint embedding+rereanker adaptation (violates explicit scope boundary), full reranker finetune without LoRA (higher resource cost, less local-friendly).

## Decision 6: Evaluation Protocol and Metrics

- Decision: Run all three modes on held-out and hard splits under one shared protocol with fixed seeds, split IDs, model/config IDs; use primary `nDCG@10` with required secondary `MRR@10` and `Recall@50`.
- Rationale: Supports consistent baseline-vs-improved comparison and avoids single-metric blind spots.
- Alternatives considered: Recall-only reporting (insufficient top-rank quality signal), qualitative-only comparisons (not acceptable under constitution).

## Decision 7: Reproducibility and Variance Tolerance

- Decision: Log seed, dataset version, split checksum, model revision, and command invocation in every report; run each evaluation config twice and require metric delta within predeclared tolerance (<=0.005 absolute on primary metric).
- Rationale: Implements deterministic workflow obligations while acknowledging limited nondeterminism in ML inference/training.
- Alternatives considered: Single-run reporting (higher false-improvement risk), strict bitwise determinism requirement (often impractical across hardware).

## Decision 8: Report Format for Recruiter-Readable Reviews

- Decision: Standardize `docs/report_*.md` with concise sections: setup, protocol, metrics table (vector vs base reranker vs LoRA), variance check, and key takeaways with explicit caveats.
- Rationale: Keeps results readable for non-specialist reviewers while preserving evidence-grounded quantitative rigor.
- Alternatives considered: Notebook-only artifacts (harder to diff/review), JSON-only metrics (less reviewer-friendly).
