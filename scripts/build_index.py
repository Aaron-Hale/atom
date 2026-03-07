#!/usr/bin/env python3
"""Build a local FAISS index from chunked contract text."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chunks", type=Path, default=Path("data/chunks.jsonl"))
    parser.add_argument("--index-out", type=Path, default=Path("data/faiss.index"))
    parser.add_argument("--metadata-out", type=Path, default=Path("data/chunk_metadata.jsonl"))
    parser.add_argument("--model", default="sentence-transformers/all-MiniLM-L6-v2")
    parser.add_argument("--batch-size", type=int, default=128)
    return parser.parse_args()


def load_chunks(chunks_path: Path) -> tuple[list[str], list[dict[str, object]]]:
    texts: list[str] = []
    metadata: list[dict[str, object]] = []

    with chunks_path.open("r", encoding="utf-8") as infile:
        for line in infile:
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            metadata.append(
                {
                    "doc_id": record["doc_id"],
                    "chunk_id": record["chunk_id"],
                    "start": record["start"],
                    "end": record["end"],
                    "text": record["text"],
                }
            )
            texts.append(record["text"])

    return texts, metadata


def save_metadata(metadata: list[dict[str, object]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as outfile:
        for row in metadata:
            outfile.write(json.dumps(row, ensure_ascii=False) + "\n")


def build_index(
    chunks_path: Path,
    index_out: Path,
    metadata_out: Path,
    model_name: str,
    batch_size: int,
) -> int:
    texts, metadata = load_chunks(chunks_path)
    if not texts:
        raise ValueError(f"No chunks found in {chunks_path}")

    model = SentenceTransformer(model_name, local_files_only=True)
    embeddings = model.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )
    embeddings = np.asarray(embeddings, dtype=np.float32)

    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)

    index_out.parent.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(index_out))
    save_metadata(metadata, metadata_out)

    return index.ntotal


def main() -> None:
    args = parse_args()
    total = build_index(
        chunks_path=args.chunks,
        index_out=args.index_out,
        metadata_out=args.metadata_out,
        model_name=args.model,
        batch_size=args.batch_size,
    )
    print(f"Indexed {total} chunks")
    print(f"Wrote FAISS index to {args.index_out}")
    print(f"Wrote metadata to {args.metadata_out}")


if __name__ == "__main__":
    main()
