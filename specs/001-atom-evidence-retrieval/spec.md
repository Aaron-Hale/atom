# Feature Specification: ATOM Evidence Retrieval Baselines

**Feature Branch**: `001-atom-evidence-retrieval`  
**Created**: 2026-03-07  
**Status**: Draft  
**Input**: User description: "Build ATOM as a local-first contract clause finder over CUAD that returns strict evidence spans for clause queries. The system MUST support: (1) vector retrieval baseline, (2) off-the-shelf reranker baseline, and (3) LoRA fine-tuned reranker. The primary output is evidence spans, not prose answers. Required output fields: doc_id, chunk_id, start, end, quote, score. The system MUST preserve exact evidence offsets into source contract text. Success is measured by reproducible evaluation reports comparing vector-only vs base reranker vs LoRA reranker on held-out and hard eval sets. Non-goals: legal advice, broad frontend, cloud deployment, polished product UI. The project MUST also preserve visible spec-kit artifacts and visible Codex/agent workflow artifacts in the repo."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Retrieve Strict Evidence Spans (Priority: P1)

A researcher submits a clause query and receives ranked evidence spans from CUAD contracts, with each result tied to exact source offsets and identifiers.

**Why this priority**: Returning precise, auditable evidence spans is the core value of ATOM.

**Independent Test**: Can be fully tested by issuing clause queries and verifying returned results include required fields and exact offset-aligned quotes.

**Acceptance Scenarios**:

1. **Given** indexed CUAD contracts and a clause query, **When** the user runs retrieval, **Then** the system returns ranked evidence results containing `doc_id`, `chunk_id`, `start`, `end`, `quote`, and `score`.
2. **Given** a returned result with `start` and `end`, **When** the corresponding substring is read from the source contract, **Then** it exactly matches the returned `quote`.
3. **Given** no matching evidence for a query, **When** retrieval completes, **Then** the system returns an empty result set without generating prose answers.

---

### User Story 2 - Compare Baseline and Improved Ranking Modes (Priority: P2)

An evaluator runs the same query/evaluation protocol across vector retrieval only, vector plus base reranker, and vector plus LoRA reranker to compare evidence retrieval quality.

**Why this priority**: Improvement claims must be measurable and attributable to ranking mode changes.

**Independent Test**: Can be tested by running all three modes on the same held-out and hard sets and confirming side-by-side metrics are produced.

**Acceptance Scenarios**:

1. **Given** fixed evaluation datasets and protocol, **When** evaluation is run for all three modes, **Then** outputs include directly comparable metrics for each mode.
2. **Given** shared query sets, **When** the evaluator compares runs, **Then** differences are attributable to ranking mode rather than split/protocol drift.
3. **Given** a LoRA-reranker evaluation run, **When** the evaluator inspects report provenance, **Then** the report includes base reranker ID, LoRA adapter artifact path/checksum, training split ID, and seed from the run that produced that adapter.

---

### User Story 3 - Preserve Visible Process and Artifacts (Priority: P3)

A project maintainer can inspect repository artifacts to understand what was specified, run, and measured for each retrieval/reranking iteration.

**Why this priority**: Visibility and reproducibility are required governance constraints for this project.

**Independent Test**: Can be tested by checking that spec-kit artifacts and Codex/agent workflow artifacts are present and evaluation reports are committed in the expected paths.

**Acceptance Scenarios**:

1. **Given** a completed iteration, **When** a maintainer reviews the repository, **Then** spec-kit artifacts for the feature remain visible under `specs/`.
2. **Given** completed evaluations, **When** a maintainer reviews documentation, **Then** reports exist under `docs/report_*.md` with configuration, split, and key metrics.
3. **Given** a completed evaluation report, **When** a maintainer traces its origin, **Then** the report links to specific spec-kit artifacts and a committed Codex/agent workflow log for that same iteration.

### Edge Cases

- Query text is empty, whitespace-only, or exceeds configured query length limits.
- A returned chunk contains repeated text where incorrect offsets could point to the wrong occurrence.
- Source documents contain unusual punctuation or encoding that can cause character-offset drift.
- A clause query has relevant evidence spanning chunk boundaries.
- Two ranking modes produce tied scores for multiple results.
- A required output field is missing or null in one result row.
- Held-out and hard evaluation sets have different label densities, risking misleading aggregate comparisons.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST support clause-query evidence retrieval over the CUAD corpus in a local-first workflow.
- **FR-002**: System MUST support a vector-retrieval-only baseline mode.
- **FR-003**: System MUST support an off-the-shelf reranker mode layered on the same retrieval candidate set.
- **FR-004**: System MUST support a LoRA fine-tuned reranker mode layered on the same retrieval candidate set.
- **FR-005**: System MUST return evidence results as structured records and MUST NOT return prose answers as the primary output.
- **FR-006**: Every returned evidence record MUST include `doc_id`, `chunk_id`, `start`, `end`, `quote`, and `score`.
- **FR-007**: `start` and `end` MUST map to exact character offsets in the source contract text for the returned `doc_id`.
- **FR-008**: Returned `quote` MUST exactly match the substring defined by `[start, end)` in the source contract text.
- **FR-009**: System MUST preserve `doc_id`, `chunk_id`, offsets, and provenance consistently through retrieval, reranking, and output generation.
- **FR-010**: System MUST provide deterministic evaluation execution controls so repeated runs with the same inputs can be reproduced.
- **FR-011**: System MUST evaluate vector-only, base-reranker, and LoRA-reranker modes on both held-out and hard evaluation sets using the same protocol per comparison.
- **FR-012**: System MUST produce evaluation reports that explicitly compare the three modes and record dataset/split identifiers, configuration identifiers, and key metrics.
- **FR-013**: System MUST store evaluation reports in `docs/report_*.md` and keep spec-kit feature artifacts visible in the repository.
- **FR-014**: System MUST preserve visible Codex/agent workflow artifacts in the repository for traceability.
- **FR-015**: LoRA fine-tuning for this feature MUST be applied to the reranker only and MUST NOT shift scope to fine-tuning the embedding model.
- **FR-016**: LoRA-reranker mode MUST be backed by a locally produced adapter artifact from this repository workflow; the artifact path/checksum, base reranker identifier, training split identifier, and seed MUST be recorded in the evaluation report.
- **FR-017**: LoRA training MUST emit machine-readable evidence that embedding-model parameters remained frozen (zero embedding parameters updated).
- **FR-018**: Retrieval API/CLI outputs MUST NOT include `answer`, `summary`, or any other generative prose field; outputs are limited to evidence records and traceability metadata.
- **FR-019**: Each evaluation report MUST include absolute per-mode metrics and explicit delta columns versus both vector-only and base-reranker baselines on the same split/protocol.
- **FR-020**: Each committed evaluation report MUST include links to the exact spec-kit feature artifacts and Codex/agent workflow artifact(s) used for that run.

### Evidence & Traceability Requirements *(mandatory when retrieval/evidence is involved)*

- **EV-001**: System MUST preserve source identifiers and exact evidence spans/offsets through retrieval, reranking, and output formatting.
- **EV-002**: System MUST emit provenance fields that allow each result to be traced back to original source text without ambiguity.
- **EV-003**: Any schema change affecting evidence/provenance MUST define migration and regression validation requirements.

### Key Entities *(include if feature involves data)*

- **Contract Document**: A CUAD source contract identified by `doc_id`, containing canonical full text used for offset validation.
- **Evidence Chunk**: A retrievable text segment identified by `chunk_id` and linked to one contract document.
- **Evidence Result**: A ranked output record with required fields (`doc_id`, `chunk_id`, `start`, `end`, `quote`, `score`) and provenance needed for auditing.
- **Evaluation Split**: A named query/evidence dataset partition (held-out or hard) used for comparable benchmarking.
- **Evaluation Report**: A versioned summary of configuration, split, metrics, and baseline-vs-improved comparisons stored in `docs/report_*.md`.

## Assumptions

- Clause queries are executed by internal evaluators/researchers, not end consumers.
- Offsets are interpreted as character offsets into canonical contract text.
- Held-out and hard evaluation sets are predefined and stable during each comparison cycle.
- Reproducibility is assessed by rerunning identical inputs and verifying materially equivalent metrics.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of returned evidence results include all required fields: `doc_id`, `chunk_id`, `start`, `end`, `quote`, `score`.
- **SC-002**: In automated offset-audit checks, 100% of evaluated results have `quote` exactly matching the source substring defined by `[start, end)`.
- **SC-003**: For each release candidate, all three modes (vector-only, base reranker, LoRA reranker) are evaluated on both held-out and hard sets under one shared protocol, with no missing comparison cells.
- **SC-004**: Re-running the same evaluation configuration and split twice yields metric variance within a pre-declared tolerance band in the report.
- **SC-005**: Every improvement claim is backed by a committed report in `docs/report_*.md` that includes baseline-vs-improved metrics, split identifiers, and reproducibility controls.
- **SC-006**: 100% of LoRA-mode report entries include adapter provenance (`base_model_id`, `adapter_path`, `adapter_checksum`, `train_split_id`, `seed`) and an embedding-freeze assertion.
- **SC-007**: 100% of committed reports link to both (a) spec-kit artifacts under `specs/001-atom-evidence-retrieval/` and (b) a Codex/agent workflow artifact path for the same run.

### Baseline vs Improved Evaluation *(mandatory for improvement claims)*

- Baseline and improved comparisons MUST cover: vector-only baseline, off-the-shelf reranker baseline, and LoRA fine-tuned reranker.
- Comparisons MUST use the same dataset partition, metric definitions, and evaluation protocol for all three modes within a report.
- Reports MUST document reproducibility controls including seed policy, split version identifiers, and model/config identifiers.
- Reports MUST include per-split delta tables (LoRA vs vector-only, LoRA vs base reranker) in addition to absolute metrics.
- Reports MUST include LoRA training provenance and embedding-freeze evidence for any LoRA-mode result.
- Improvement claims are valid only when captured in `docs/report_*.md` with explicit baseline-vs-improved metric tables.

## Out of Scope & Safety Boundaries *(mandatory)*

- This feature MUST NOT present outputs as legal advice.
- This feature MUST NOT broaden scope into a general legal copilot.
- This feature MUST NOT include broad frontend product development.
- This feature MUST NOT include cloud deployment work.
- This feature MUST NOT prioritize polished product UI over retrieval/reranking evaluation discipline.
- This feature MUST NOT expand into embedding-model fine-tuning.
- This feature MUST NOT require a prose-answer endpoint or chat-style legal assistant behavior.
