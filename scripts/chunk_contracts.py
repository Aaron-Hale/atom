#!/usr/bin/env python3
"""Deterministic fixed-size chunking with exact character offsets."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class ChunkRecord:
    chunk_id: str
    doc_id: str
    start: int
    end: int
    text: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("data/contracts.jsonl"))
    parser.add_argument("--output", type=Path, default=Path("data/chunks.jsonl"))
    parser.add_argument("--chunk-size", type=int, default=1200)
    parser.add_argument("--chunk-overlap", type=int, default=200)
    return parser.parse_args()


def iter_contracts(path: Path) -> Iterable[dict[str, str]]:
    with path.open("r", encoding="utf-8") as infile:
        for line in infile:
            if not line.strip():
                continue
            record = json.loads(line)
            yield {"doc_id": record["doc_id"], "text": record["text"]}


def chunk_document(doc_id: str, text: str, chunk_size: int, chunk_overlap: int) -> list[ChunkRecord]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be > 0")
    if chunk_overlap < 0:
        raise ValueError("chunk_overlap must be >= 0")
    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be < chunk_size")
    if not text:
        return []

    step = chunk_size - chunk_overlap
    chunks: list[ChunkRecord] = []

    for index, start in enumerate(range(0, len(text), step)):
        end = min(start + chunk_size, len(text))
        chunk_text = text[start:end]
        chunk_id = f"{doc_id}::chunk_{index:05d}"
        chunks.append(
            ChunkRecord(chunk_id=chunk_id, doc_id=doc_id, start=start, end=end, text=chunk_text)
        )
        if end == len(text):
            break

    return chunks


def chunk_contracts(
    input_path: Path, output_path: Path, chunk_size: int = 1200, chunk_overlap: int = 200
) -> int:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    written = 0

    with output_path.open("w", encoding="utf-8") as outfile:
        for contract in iter_contracts(input_path):
            doc_id = contract["doc_id"]
            text = contract["text"]
            for chunk in chunk_document(
                doc_id=doc_id, text=text, chunk_size=chunk_size, chunk_overlap=chunk_overlap
            ):
                outfile.write(
                    json.dumps(
                        {
                            "chunk_id": chunk.chunk_id,
                            "doc_id": chunk.doc_id,
                            "start": chunk.start,
                            "end": chunk.end,
                            "text": chunk.text,
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                )
                written += 1

    return written


def main() -> None:
    args = parse_args()
    written = chunk_contracts(
        input_path=args.input,
        output_path=args.output,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
    )
    print(f"Wrote {written} chunks to {args.output}")


if __name__ == "__main__":
    main()
