# Contract Chunking Policy (Day 5)

ATOM uses deterministic fixed-size character chunking over `data/contracts.jsonl`:

- Input: one JSON object per line with `doc_id` and `text`.
- Output: `data/chunks.jsonl` with fields:
  - `chunk_id`
  - `doc_id`
  - `start`
  - `end`
  - `text`

## Parameters

- `chunk_size = 1200`
- `chunk_overlap = 200`
- `step = chunk_size - chunk_overlap = 1000`

## Offset policy

- For each document, chunk starts are generated from `0` with fixed stride `step`.
- Each chunk uses:
  - `start = start_index`
  - `end = min(start + chunk_size, len(text))`
  - `text = text[start:end]`
- Chunking stops when a chunk reaches `end == len(text)`.
- Character offsets are exact; chunk text is always the original source slice.

## Deterministic IDs

- Chunk IDs are stable and deterministic:
  - `chunk_id = "{doc_id}::chunk_{index:05d}"`
- `index` is the 0-based chunk order within each `doc_id`.
