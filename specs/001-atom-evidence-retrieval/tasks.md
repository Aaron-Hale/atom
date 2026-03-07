# Tasks: ATOM Evidence Retrieval Baselines

**Input**: Design documents from `/Users/aaronhale/projects/atom/specs/001-atom-evidence-retrieval/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Tests are REQUIRED for this feature because retrieval, reranking, evidence schema, and evaluation workflow behavior are in scope.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: User story label (`[US1]`, `[US2]`, `[US3]`) for story-phase tasks only
- Every task includes an explicit file path

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize Python project and deterministic local-first scaffolding.

- [ ] T001 Create package skeleton and module directories in `src/atom/__init__.py`
- [ ] T002 Initialize project dependencies and tool config in `pyproject.toml`
- [ ] T003 [P] Configure pytest defaults and markers in `pytest.ini`
- [ ] T004 [P] Create deterministic run configuration template in `config/eval/default.yaml`
- [ ] T005 [P] Create local artifact directory placeholders in `artifacts/.gitkeep`
- [ ] T006 [P] Add markdown report template for recruiter-readable outputs in `docs/report_template.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build core data, schema, retrieval, and determinism primitives required by all user stories.

**⚠️ CRITICAL**: Complete this phase before starting user stories.

- [ ] T007 Implement strict evidence result schema and validators in `src/atom/schemas/evidence.py`
- [ ] T008 [P] Implement runtime settings and seed management in `src/atom/config/settings.py`
- [ ] T009 [P] Implement CUAD document loader with checksum capture in `src/atom/data/loaders.py`
- [ ] T010 Implement deterministic chunking with character offsets in `src/atom/data/chunking.py`
- [ ] T011 [P] Implement sentence-transformers embedding wrapper in `src/atom/retrieval/embeddings.py`
- [ ] T012 Implement FAISS index build/load/search utilities in `src/atom/retrieval/faiss_index.py`
- [ ] T013 [P] Implement run-manifest logging for reproducibility metadata in `src/atom/evaluation/run_manifest.py`
- [ ] T014 Create shared pytest fixtures for documents, chunks, and queries in `tests/conftest.py`
- [ ] T015 [P] Add unit tests for evidence schema required/forbidden fields (`answer`/`summary` disallowed) and offset invariants in `tests/unit/test_schema.py`
- [ ] T016 [P] Add unit tests for deterministic chunking and seed behavior in `tests/unit/test_determinism.py`

**Checkpoint**: Foundational layer is complete; user stories can begin.

---

## Phase 3: User Story 1 - Retrieve Strict Evidence Spans (Priority: P1) 🎯 MVP

**Goal**: Return ranked evidence spans with exact source offsets and strict required output fields.

**Independent Test**: Submit a clause query and verify each result includes `doc_id`, `chunk_id`, `start`, `end`, `quote`, `score` and `quote == source_text[start:end]`; no-match queries return empty results only.

### Tests for User Story 1

- [ ] T017 [P] [US1] Add API contract test for `/v1/retrieve` strict schema (required fields present, generative prose fields absent) in `tests/contract/test_retrieve_contract.py`
- [ ] T018 [P] [US1] Add integration test for end-to-end retrieval query flow validating every returned row has exact `[start,end)` quote alignment in `tests/integration/test_retrieve_api.py`
- [ ] T019 [P] [US1] Add regression test for repeated-text offset disambiguation in `tests/regression/test_offset_regression.py`

### Implementation for User Story 1

- [ ] T020 [P] [US1] Implement retrieval pipeline orchestration (query -> candidates -> evidence records) in `src/atom/retrieval/pipeline.py`
- [ ] T021 [US1] Implement strict evidence result assembly and provenance propagation in `src/atom/retrieval/service.py`
- [ ] T022 [US1] Implement FastAPI retrieval endpoint behavior and request validation in `src/atom/api/app.py`
- [ ] T023 [US1] Implement retrieve CLI command contract in `src/atom/cli/retrieve.py`
- [ ] T024 [US1] Implement empty/whitespace/no-match handling without prose output in `src/atom/api/error_handlers.py`
- [ ] T025 [US1] Add quote-offset verification guardrail before response emission in `src/atom/retrieval/validators.py`
- [ ] T026 [US1] Wire API route module and schema binding for retrieval in `src/atom/api/routes/retrieve.py`

**Checkpoint**: User Story 1 is independently functional and testable.

---

## Phase 4: User Story 2 - Compare Baseline and Improved Ranking Modes (Priority: P2)

**Goal**: Run vector-only, base reranker, and LoRA reranker modes under one deterministic protocol and produce measurable comparisons.

**Independent Test**: Execute evaluation for all three modes across held-out and hard splits and verify complete comparison tables for `nDCG@10`, `MRR@10`, and `Recall@50` with reproducibility metadata.

### Tests for User Story 2

- [ ] T027 [P] [US2] Add contract test for `atom evaluate` output requiring absolute metrics plus delta columns (LoRA-vs-vector and LoRA-vs-base) in `tests/contract/test_evaluate_cli_contract.py`
- [ ] T028 [P] [US2] Add integration test for three-mode comparison on shared candidate sets in `tests/integration/test_mode_comparison.py`
- [ ] T029 [P] [US2] Add integration test enforcing LoRA reranker-only fine-tuning scope with zero embedding-parameter updates in `tests/integration/test_lora_reranker_only.py`
- [ ] T030 [P] [US2] Add regression test for repeated-run variance tolerance and stable LoRA provenance fields in `tests/regression/test_eval_reproducibility.py`

### Implementation for User Story 2

- [ ] T031 [P] [US2] Implement base reranker inference adapter in `src/atom/reranking/base_reranker.py`
- [ ] T032 [P] [US2] Implement PEFT LoRA reranker loader/inference adapter in `src/atom/reranking/lora_reranker.py`
- [ ] T033 [US2] Implement shared ranking score normalization and tie handling in `src/atom/reranking/scoring.py`
- [ ] T034 [US2] Implement evaluation protocol runner for splits/modes/config IDs in `src/atom/evaluation/protocol.py`
- [ ] T035 [P] [US2] Implement retrieval-quality metrics (`nDCG@10`, `MRR@10`, `Recall@50`) in `src/atom/evaluation/metrics.py`
- [ ] T036 [US2] Implement markdown report generation with absolute metrics, delta tables, and LoRA provenance block in `src/atom/evaluation/report_writer.py`
- [ ] T037 [US2] Implement evaluation CLI command and report emission in `src/atom/cli/evaluate.py`
- [ ] T038 [US2] Implement LoRA training CLI with embedding-freeze guardrails and adapter checksum/base-model/train-split logging in `src/atom/cli/train_reranker_lora.py`

**Checkpoint**: User Stories 1 and 2 are independently functional and produce measurable comparisons.

---

## Phase 5: User Story 3 - Preserve Visible Process and Artifacts (Priority: P3)

**Goal**: Keep spec-kit/Codex workflow artifacts and evaluation evidence visible and auditable in-repo.

**Independent Test**: Verify repository contains required spec artifacts and `docs/report_*.md` outputs with config, split, and key metrics.

### Tests for User Story 3

- [ ] T039 [P] [US3] Add integration test requiring each report to link spec-kit artifact paths and Codex/agent workflow artifact paths in `tests/integration/test_artifact_visibility.py`

### Implementation for User Story 3

- [ ] T040 [P] [US3] Implement artifact manifest generator enforcing per-run links between report, spec-kit files, and Codex/agent workflow logs in `src/atom/evaluation/artifact_manifest.py`
- [ ] T041 [US3] Implement artifact publication CLI command in `src/atom/cli/publish_artifacts.py`
- [ ] T042 [US3] Implement workflow trace writer linked to evaluation runs with stable run IDs and command metadata in `src/atom/evaluation/workflow_log.py`
- [ ] T043 [US3] Generate initial report index linking each report to required spec-kit and Codex/agent artifacts in `docs/report_index.md`

**Checkpoint**: All user stories are independently functional and traceability artifacts are visible.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final hardening, documentation, and release-readiness checks across stories.

- [ ] T044 [P] Update quickstart to match implemented commands and paths in `specs/001-atom-evidence-retrieval/quickstart.md`
- [ ] T045 [P] Add API/CLI usage examples aligned with contracts in `docs/usage.md`
- [ ] T046 Run full test suite and capture results summary in `docs/test-results.md`
- [ ] T047 Run baseline-vs-improved evaluation and commit report artifact with delta tables and LoRA proof block in `docs/report_2026-03-07_baseline-vs-improved.md`
- [ ] T048 Validate OpenAPI contract matches implementation responses and forbids prose answer fields in `specs/001-atom-evidence-retrieval/contracts/evidence-api.yaml`
- [ ] T049 Perform final quality pass on deterministic config and metadata logging in `config/eval/default.yaml`

---

## Dependencies & Execution Order

### Phase Dependencies

- Setup (Phase 1): No dependencies.
- Foundational (Phase 2): Depends on Setup; blocks all user stories.
- User Story Phases (Phase 3-5): Depend on Foundational completion.
- Polish (Phase 6): Depends on completed target user stories.

### User Story Dependencies

- US1 (P1): Starts after Foundational; no dependency on other stories.
- US2 (P2): Starts after Foundational; reuses US1 retrieval outputs but remains independently testable.
- US3 (P3): Starts after Foundational and can proceed in parallel with late US2 work once reports are emitted.

### Dependency Graph

- `US1 -> US2 -> US3` for full-value delivery order.
- `US1` alone is MVP scope.
- `US2` requires foundational retrieval/reporting primitives but not US3 completion.

### Within-Story Ordering Rules

- Write tests first and confirm failure.
- Implement models/schemas before services.
- Implement services before API/CLI interfaces.
- Complete story checkpoint before declaring story done.

---

## Parallel Execution Examples

### User Story 1

```bash
# Parallel test creation
T017, T018, T019

# Parallel implementation after tests exist
T020 and T025
```

### User Story 2

```bash
# Parallel test creation
T027, T028, T029, T030

# Parallel model/adaptor work
T031, T032, T035
```

### User Story 3

```bash
# Parallel artifact and test work
T039 and T040
```

---

## Implementation Strategy

### MVP First (US1)

1. Complete Phase 1 and Phase 2.
2. Deliver Phase 3 (US1) end-to-end.
3. Validate independent test criteria for strict evidence spans.

### Incremental Delivery

1. Add US2 to deliver measurable baseline-vs-improved evaluation.
2. Add US3 to deliver repository-visible process/report traceability.
3. Finish Phase 6 polish and final report publication.

### Parallel Team Strategy

1. Team aligns on Setup + Foundational.
2. After Foundational: one stream executes US1/US2 ranking work while another prepares US3 artifact visibility work.
3. Merge only with passing tests and committed measurable reports.
