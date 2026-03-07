# Implementation Plan: ATOM Evidence Retrieval Baselines

**Branch**: `001-atom-evidence-retrieval` | **Date**: 2026-03-07 | **Spec**: [/Users/aaronhale/projects/atom/specs/001-atom-evidence-retrieval/spec.md](/Users/aaronhale/projects/atom/specs/001-atom-evidence-retrieval/spec.md)
**Input**: Feature specification from `/specs/001-atom-evidence-retrieval/spec.md`

## Summary

Build a local-first Python service and CLI that retrieves CUAD evidence spans and compares three ranking modes (vector-only, base reranker, LoRA reranker-only fine-tune) with strict offset fidelity. The implementation uses FAISS for candidate retrieval, sentence-transformers embeddings, transformers+peft reranking, FastAPI/JSON contracts for evidence outputs, pytest for regression discipline, and markdown reports in `docs/report_*.md` for measurable baseline-vs-improved comparisons.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: FastAPI, sentence-transformers, transformers, peft, faiss-cpu, pytest  
**Storage**: Local filesystem artifacts (CUAD source text, FAISS index, model checkpoints, report markdown)  
**Testing**: pytest (unit + integration + regression)  
**Target Platform**: Local macOS/Linux development workstation (CPU-first; optional local GPU for LoRA)  
**Project Type**: local-first backend service + CLI evaluation pipeline  
**Performance Goals**: p95 retrieval+rereank latency <= 1.5s/query on held-out benchmark slice; full evaluation run (all 3 modes x 2 splits) <= 45 min on reference workstation  
**Constraints**: strict evidence output schema (`doc_id`, `chunk_id`, `start`, `end`, `quote`, `score`), exact `[start, end)` quote matching, deterministic seeds/configs, no mandatory cloud dependency  
**Scale/Scope**: CUAD corpus indexing with up to ~1M chunks in FAISS; top-k retrieval (k<=200) and top-n outputs (n<=20) per query for evaluator workflows

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Pre-Design Gate Review

- [x] Evidence fidelity preserved: data model and outputs retain document IDs, span offsets, and provenance fields with no lossy transforms.
- [x] Local-first execution: core retrieval, reranking, and evaluation can run locally without mandatory remote services.
- [x] Deterministic protocol defined: seeds, dataset versions/splits, configs, and artifact versions are specified for reproducibility.
- [x] Baseline and improved comparison plan: same evaluation protocol, metrics, and reporting format defined before implementation.
- [x] LoRA proof plan defined: reports require adapter provenance plus embedding-freeze evidence for LoRA-mode claims.
- [x] Test strategy includes unit + integration/regression coverage for changed retrieval, reranking, schema, or evidence-handling behavior.
- [x] Scope boundaries confirmed: work is not legal advice and not a general legal copilot.
- [x] Report output path defined for measurable outcomes (`docs/report_*.md`).
- [x] Traceability visibility defined: each report links to spec-kit artifacts and Codex/agent workflow artifacts for the same run.

### Post-Design Gate Review

- [x] Evidence fidelity controls defined in `data-model.md` and `contracts/evidence-api.yaml` (span schema + quote offset validation).
- [x] Local-first architecture and quickstart rely only on local files/models (`quickstart.md`).
- [x] Determinism controls captured in `research.md` and quickstart run commands (seeded configs + split IDs).
- [x] Baseline/improved comparison protocol fixed across three modes and two splits in contracts + quickstart.
- [x] Planned tests include schema, offset, ranking-mode parity, and evaluation regression checks.
- [x] LoRA design includes adapter provenance fields and embedding-freeze assertions in report outputs.
- [x] Out-of-scope boundaries preserved (no legal advice, no cloud requirement, no embedding-model fine-tuning).
- [x] Report destination and measurable before/after outputs explicitly documented.
- [x] Artifact-visibility design includes linked spec-kit and Codex/agent workflow evidence per report.

## Project Structure

### Documentation (this feature)

```text
specs/001-atom-evidence-retrieval/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── evidence-api.yaml
│   └── evaluation-cli.md
└── tasks.md
```

### Source Code (repository root)

```text
src/
└── atom/
    ├── api/
    │   └── app.py
    ├── cli/
    │   ├── retrieve.py
    │   ├── evaluate.py
    │   └── train_reranker_lora.py
    ├── data/
    │   ├── loaders.py
    │   └── chunking.py
    ├── retrieval/
    │   ├── embeddings.py
    │   └── faiss_index.py
    ├── reranking/
    │   ├── base_reranker.py
    │   ├── lora_reranker.py
    │   └── scoring.py
    ├── evaluation/
    │   ├── metrics.py
    │   ├── protocol.py
    │   └── report_writer.py
    └── schemas/
        └── evidence.py

tests/
├── unit/
│   ├── test_offsets.py
│   ├── test_schema.py
│   └── test_metrics.py
├── integration/
│   ├── test_retrieve_api.py
│   ├── test_mode_comparison.py
│   └── test_lora_reranker_only.py
└── regression/
    ├── test_eval_reproducibility.py
    └── test_report_contract.py

docs/
└── report_*.md
```

**Structure Decision**: Use a single Python project with service + CLI modules so retrieval, reranking, and evaluation share one evidence schema and deterministic config path while keeping local-first operation simple.

## Phase 0: Research Plan

1. Finalize evidence schema contract and offset invariants for strict span-grounded outputs.
2. Define FAISS retrieval configuration and embedding model usage best practices for local-first reproducibility.
3. Define reranker architecture split between base transformer inference and PEFT LoRA fine-tuning limited to reranker weights.
4. Define evaluation protocol (held-out + hard splits, fixed metrics, seeded runs, reproducibility tolerance, explicit delta tables).
5. Define markdown report template requirements for recruiter-readable before/after comparisons.

## Phase 1: Design Plan

1. Convert spec entities to concrete data model with validation rules and provenance links.
2. Define FastAPI retrieval endpoint contract returning strict evidence results only.
3. Define CLI contract for indexing, retrieval, evaluation, and LoRA training workflows.
4. Draft quickstart for local environment setup, deterministic runs, and report generation.
5. Update agent context for Codex with selected stack and project shape.

## Phase 2: Implementation Planning Approach

1. Build deterministic ingestion/indexing pipeline first; block on offset fidelity tests.
2. Implement vector baseline retrieval path and API/CLI outputs.
3. Integrate base reranker mode without changing candidate set provenance.
4. Add LoRA reranker fine-tune/inference path with explicit guardrails preventing embedding-model training.
5. Implement evaluation harness + markdown reporting and regression suite for baseline-vs-improved comparison discipline, including LoRA provenance proofs and linked workflow/spec artifacts.

## Complexity Tracking

No constitution violations identified; no justified exceptions required.
