# AGENTS.md

## Project goal
Build ATOM as a local-first, evidence-grounded contract clause retrieval and reranking
system over CUAD, with reproducible evaluation and regression discipline.

## Non-goals
- not a general legal copilot
- not legal advice
- not feature work without measurable retrieval/reranking value
- not product-polish work that bypasses evaluation discipline

## Core rules
- Evidence fidelity is non-negotiable: never drop, alter, or misalign source IDs, spans,
  offsets, or provenance.
- Any change touching retrieval, reranking, outputs, or schemas MUST include updated tests;
  no merge with failing tests.
- Keep diffs minimal and reviewable; avoid broad refactors unless required for correctness.
- Every improvement claim MUST show explicit baseline-vs-improved metrics on the same eval
  protocol and data split.
- Never claim success without measured results; "looks better" is not acceptable evidence.
- Record evaluations in `docs/report_*.md` with config, dataset/split, and key metrics.
- Keep scripts deterministic where practical (seed, pinned inputs, stable configs).
- Prefer local-first and simplest viable architecture before adding infrastructure.
