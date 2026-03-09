# Contract Chunking Policy (Day 12)

ATOM uses deterministic fixed-size character chunking over `data/contracts.jsonl`:

- Input: one JSON object per line with `doc_id` and `text`.
- Output: `data/chunks.jsonl` with fields:
  - `chunk_id`
  - `doc_id`
  - `start`
  - `end`
  - `text`

## Parameters

- `chunk_size = 900`
- `chunk_overlap = 250`
- `step = chunk_size - chunk_overlap = 650`

## Offset policy

- For each document, chunk starts are generated from `0` with fixed stride `step`.
- Each chunk uses:
  - `start = start_index`
  - `end = min(start + chunk_size, len(text))`
  - `text = text[start:end]`
- Chunking stops when a chunk reaches `end == len(text)`.
- Character offsets are exact; chunk text is always the original source slice.

## Embedding Representation

- Raw chunk data remains offset-preserving:
  - `text = text[start:end]` is unchanged and is retained in metadata for evidence.
- During index build, embedding input text is enriched deterministically as:
  - `Document Title: <title cue>`
  - `Section Heading: <heading>` (when a simple uppercase-like heading is found in-chunk)
  - `Chunk Text: <raw chunk text>`
- Title cue is extracted from each source contract deterministically using early header lines.
- Heading cue is extracted from early lines inside each chunk and used only for embeddings.
- Enriched text is used for vector encoding only; retrieval outputs still return raw chunk text and exact offsets.

## Deterministic IDs

- Chunk IDs are stable and deterministic:
  - `chunk_id = "{doc_id}::chunk_{index:05d}"`
- `index` is the 0-based chunk order within each `doc_id`.
