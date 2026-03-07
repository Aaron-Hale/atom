from __future__ import annotations

import json
from pathlib import Path

from scripts.chunk_contracts import chunk_contracts, chunk_document


def test_chunk_text_matches_source_slice() -> None:
    text = "0123456789" * 400
    doc_id = "doc_a"
    chunks = chunk_document(doc_id=doc_id, text=text, chunk_size=1200, chunk_overlap=200)

    assert chunks
    for chunk in chunks:
        assert chunk.text == text[chunk.start : chunk.end]


def test_chunk_bounds_and_overlap_consistency() -> None:
    text = "abcdefg" * 500
    chunks = chunk_document(doc_id="doc_b", text=text, chunk_size=1200, chunk_overlap=200)
    step = 1200 - 200

    assert chunks[0].start == 0
    assert chunks[-1].end == len(text)

    for chunk in chunks:
        assert 0 <= chunk.start < chunk.end <= len(text)
        assert chunk.end - chunk.start <= 1200

    for previous, current in zip(chunks, chunks[1:]):
        assert current.start - previous.start == step
        overlap = previous.end - current.start
        expected_overlap = min(200, previous.end - previous.start)
        assert overlap == expected_overlap


def test_chunk_contracts_jsonl_round_trip(tmp_path: Path) -> None:
    contracts_path = tmp_path / "contracts.jsonl"
    output_a = tmp_path / "chunks_a.jsonl"
    output_b = tmp_path / "chunks_b.jsonl"

    records = [
        {"doc_id": "doc_1", "text": "A" * 1700},
        {"doc_id": "doc_2", "text": "B" * 900},
    ]
    with contracts_path.open("w", encoding="utf-8") as outfile:
        for record in records:
            outfile.write(json.dumps(record) + "\n")

    written_a = chunk_contracts(contracts_path, output_a, chunk_size=1200, chunk_overlap=200)
    written_b = chunk_contracts(contracts_path, output_b, chunk_size=1200, chunk_overlap=200)

    assert written_a == written_b
    assert output_a.read_text(encoding="utf-8") == output_b.read_text(encoding="utf-8")

    by_doc = {record["doc_id"]: record["text"] for record in records}
    with output_a.open("r", encoding="utf-8") as infile:
        parsed = [json.loads(line) for line in infile if line.strip()]

    assert parsed
    for chunk in parsed:
        assert set(chunk.keys()) == {"chunk_id", "doc_id", "start", "end", "text"}
        source_text = by_doc[chunk["doc_id"]]
        assert chunk["text"] == source_text[chunk["start"] : chunk["end"]]
