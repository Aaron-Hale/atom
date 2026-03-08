
## Day 3
- Added a project-local Codex skill for retrieval evaluation under `.codex/skills/retrieval-eval/`.
- Added a reusable markdown report template for ATOM retrieval experiments over CUAD.
- Established repo-specific rules that prevent declaring success without numeric metrics and written reports.
- Verified Codex can read and minimally refine the project-local skill and template.
- Fixed `.gitignore` so the project-local Codex skill is tracked in Git while keeping local environment artifacts ignored.
- Remaining blocker: eval scripts and reports do not exist yet, so the skill currently defines workflow and acceptance criteria.

## Day 4
- Implemented deterministic CUAD export into canonical contract and label stores.
- Loaded real CUAD data by default from Hugging Face, with optional local JSON override.
- Produced non-empty contracts.jsonl and labels.jsonl with stable doc IDs and preserved span offsets.
- Tightened clause normalization and updated the selected taxonomy to match clauses actually present in the source dataset.
- Remaining blocker: verify exported span quality manually before chunking on Day 5.

## Day 5
- Implemented deterministic offset-preserving chunking for exported CUAD contracts.
- Produced chunks.jsonl with exact start/end offsets and deterministic chunk IDs.
- Added tests proving chunk text exactly matches the original document slice and stays within bounds.
- Remaining blocker: need retrieval indexing on top of chunk metadata for Day 6.

## Day 6
- Built a local embedding + FAISS retrieval baseline over chunked CUAD contracts.
- Saved faiss.index and chunk metadata mapping for deterministic top-K retrieval.
- Implemented a retrieval service that returns scored chunk candidates with exact metadata.
- Remaining blocker: need a deterministic eval set and baseline retrieval report for Day 7.

## Day 7
- Built a deterministic baseline eval set from exported CUAD labels using contract-aware title cues.
- Implemented overlap-based vector retrieval evaluation using hit@K and Recall@K.
- Wrote a baseline retrieval report with overall metrics, per-clause breakdowns, and failure examples.
- Remaining blocker: need an off-the-shelf reranker baseline for Day 8.

## Day 8
- Added an off-the-shelf cross-encoder reranker on top of vector retrieval.
- Extended the eval runner to compare vector-only and vector+base-reranker performance.
- Wrote a reranker baseline report with overall metrics, per-clause breakdowns, and qualitative examples.
- Remaining blocker: need a reranker training dataset for LoRA fine-tuning on Day 9.

## Day 9
- Built deterministic pointwise reranker training and validation datasets from eval queries, chunk overlaps, and vector retrieval outputs.
- Included positives, hard negatives, and same-document negatives with metadata for debugging and analysis.
- Improved title-cue extraction to prefer real agreement titles over filing/redaction boilerplate.
- Added a light filter to avoid boilerplate-only hard negatives while preserving deterministic behavior.
- Remaining blocker: need LoRA reranker training and artifact save path for Day 10.

## Day 10
- Implemented LoRA fine-tuning for the reranker using the pointwise train/val dataset.
- Trained and saved reusable adapter artifacts under models/reranker_lora/.
- Logged the exact training command, dataset sizes, and validation metrics.
- Remaining blocker: need held-out comparison of vector vs base reranker vs LoRA reranker on Day 11.

## Day 11
- Loaded the saved LoRA adapter into the reranking path for held-out evaluation.
- Compared vector-only, base reranker, and LoRA reranker side-by-side on the baseline eval set.
- Found that the first-pass LoRA reranker underperformed the off-the-shelf base reranker on held-out retrieval metrics.
- Remaining blocker: improve training setup or data quality before claiming LoRA gains, then proceed to harder stress-test evaluation.
