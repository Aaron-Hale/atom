---
name: retrieval-eval
description: Standardize retrieval experiment execution, markdown reporting, and sanity checks for ATOM's clause retrieval pipeline over CUAD.
---

# retrieval-eval

## Purpose
This skill is for retrieval-quality changes in ATOM. It standardizes how to:
- run retrieval evaluations
- compare baseline vs changed behavior
- write reviewer-readable markdown reports
- reject unsupported claims of improvement

This skill is specific to this repo's evidence-grounded contract clause retrieval system. It is not a general benchmarking skill.

## Use this skill when
Use this skill when a change could affect retrieval quality or evidence fidelity, including:
- chunking policy changes
- retrieval/indexing changes
- embedding model changes
- reranking changes
- LoRA reranker training changes
- eval metric changes
- report generation changes
- candidate set or top-k behavior changes

## Do not use this skill when
Do not use this skill for:
- unrelated API wiring
- pure schema refactors
- README-only edits
- dependency/setup issues
- formatting-only changes
- code changes with no plausible effect on retrieval results

## Required outputs
When this skill is used, produce or update:
- a markdown report in `docs/report_*.md`
- explicit metric values, not impressions
- enough config detail to reproduce the run
- side-by-side comparison when comparing systems

Preferred report contents:
- experiment purpose
- dataset/evalset used
- model/index/reranker config
- chunking config if relevant
- overall metrics
- per-clause or per-slice breakdown when available
- 3-5 concrete examples or failure cases
- conclusion that matches the evidence

## Required metrics
Use the metrics supported by the repo at the time of the change. For retrieval changes, prefer:
- hit@K
- Recall@K
- span_overlap@K when available

Do not describe results as improved, better, complete, or done without metric evidence.

## Sanity checks before declaring success
Before declaring success, verify all of the following:
1. The relevant eval command actually ran.
2. The report file was created or updated in `docs/`.
3. The report includes numeric metrics.
4. Any claim of improvement is backed by side-by-side values.
5. Any regression or ambiguity is stated explicitly.
6. If evidence offsets or quote fidelity could be affected, relevant tests were run.
7. The conclusion does not overclaim beyond the reported results.

## Repo-specific rules
For this project:
- prioritize evidence fidelity over flashy presentation
- do not claim retrieval quality improved from anecdotal examples alone
- do not hide baseline numbers
- do not collapse vector-only, base reranker, and LoRA reranker into a vague summary
- preserve reviewer-readable markdown
- prefer minimal commands and minimal diffs
- write reports to `docs/report_*.md`

## Suggested workflow
1. Identify what changed and why it might affect retrieval quality.
2. Run the smallest relevant eval that can detect the effect.
3. Capture exact command and config details.
4. Write or update the report.
5. Compare against baseline if the change is meant to improve results.
6. State whether the change helped, hurt, or is inconclusive.

## Refusal conditions
Refuse to call a change successful if:
- no eval was run
- no metrics are shown
- no report was written
- the change could affect evidence fidelity and related checks were skipped
- the conclusion says improved but the report does not demonstrate it
