<!--
Sync Impact Report
- Version change: template (unversioned) -> 1.0.0
- Modified principles:
  - Template Principle 1 -> I. Evidence Fidelity First
  - Template Principle 2 -> II. Local-First, Minimal Complexity
  - Template Principle 3 -> III. Reproducible and Deterministic Workflows
  - Template Principle 4 -> IV. Testable Retrieval and Reranking
  - Template Principle 5 -> V. Metrics Before Claims
- Added sections:
  - Scope Boundaries
  - Delivery Workflow and Reporting
- Removed sections:
  - None
- Templates requiring updates:
  - ✅ updated: .specify/templates/plan-template.md
  - ✅ updated: .specify/templates/spec-template.md
  - ✅ updated: .specify/templates/tasks-template.md
  - ⚠ pending: .specify/templates/commands/*.md (directory not present in repository)
  - ✅ reviewed, no change required: AGENTS.md
- Follow-up TODOs:
  - None
-->
# ATOM Constitution

## Core Principles

### I. Evidence Fidelity First
The system MUST preserve evidence traceability end to end. Source document identifiers,
character offsets, spans, and retrieval provenance MUST not be dropped, altered, or
reinterpreted without an explicit, tested mapping. Any schema change that touches evidence
fields MUST include migration coverage and regression tests for span accuracy.
Rationale: trust in clause retrieval and reranking depends on exact source-grounded evidence.

### II. Local-First, Minimal Complexity
Core retrieval, reranking, and evaluation workflows MUST run locally without mandatory
network services. Teams MUST choose the simplest architecture that satisfies current
requirements and MUST justify any added infrastructure with measured bottlenecks or clear
operational need. Broad refactors are disallowed unless required for correctness or
measurable maintainability gains.
Rationale: local-first operation reduces fragility and complexity, and keeps iteration fast.

### III. Reproducible and Deterministic Workflows
Evaluation and data-processing scripts MUST be reproducible. Scripts MUST pin or log random
seeds, input datasets, split definitions, config versions, and model artifacts. Where full
determinism is not technically possible, the source of nondeterminism MUST be documented and
bounded with repeated-run variance reporting.
Rationale: reproducibility is required for credible baseline-to-improved comparisons.

### IV. Testable Retrieval and Reranking
All behavior changes MUST include relevant automated tests. At minimum, changes to retrieval,
reranking, scoring, schemas, or evidence handling MUST include targeted unit tests and
integration or regression tests that validate end-to-end behavior on representative CUAD
slices. Merges are blocked if required tests fail.
Rationale: testability is the control mechanism that prevents silent quality regressions.

### V. Metrics Before Claims
No change may be called an improvement without metrics. Every experiment, report, or merge
request claiming quality gains MUST present explicit baseline-vs-improved results produced on
the same evaluation protocol and dataset partition. Reports MUST be written to `docs/report_*.md`
and include metric definitions, confidence notes, and known limitations.
Rationale: measurable evidence is the only acceptable basis for success claims.

## Scope Boundaries

ATOM is a local-first retrieval and reranking system for contracts, not a general legal
copilot. Outputs MUST not be presented as legal advice. Feature scope MUST prioritize
evaluation value over product polish and MUST reject speculative additions that lack a clear,
measurable retrieval or reranking objective.

## Delivery Workflow and Reporting

Work MUST be delivered as minimal, reviewable diffs with explicit baseline impact. Pull
requests MUST include: purpose, changed components, test evidence, and metric deltas when
behavior changes are introduced. Evaluation artifacts, including command invocations and
output locations, MUST be documented so another contributor can reproduce results locally.

## Governance

This constitution overrides conflicting team conventions for this repository.
Amendments require a documented proposal, rationale, impacted templates, and migration notes
for in-flight work. Governance versioning follows semantic rules:
- MAJOR for principle removals or incompatible governance changes.
- MINOR for new principles or materially expanded mandatory guidance.
- PATCH for clarifications that do not change obligations.
Compliance review is required at plan approval and pull request review. Reviewers MUST verify:
evidence fidelity protections, deterministic or documented evaluation setup, adequate tests,
and explicit baseline-vs-improved metrics for any claimed improvement.

**Version**: 1.0.0 | **Ratified**: 2026-03-07 | **Last Amended**: 2026-03-07
