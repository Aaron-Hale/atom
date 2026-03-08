#!/usr/bin/env python3
"""Build deterministic pointwise reranker datasets from eval and chunk metadata."""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
from sentence_transformers import SentenceTransformer

HARD_NEGATIVE_BOILERPLATE_MARKERS = (
    "confidential treatment requested",
    "securities and exchange commission",
    "filed with the commission",
    "pursuant to 17 c.f.r",
    "table of contents",
    "source:",
)


@dataclass(frozen=True)
class ChunkRow:
    doc_id: str
    chunk_id: str
    start: int
    end: int
    text: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evalset", type=Path, default=Path("eval/evalset_v1.jsonl"))
    parser.add_argument("--metadata", type=Path, default=Path("data/chunk_metadata.jsonl"))
    parser.add_argument("--index", type=Path, default=Path("data/faiss.index"))
    parser.add_argument("--train-out", type=Path, default=Path("data/rerank_train.jsonl"))
    parser.add_argument("--val-out", type=Path, default=Path("data/rerank_val.jsonl"))
    parser.add_argument("--model", default="sentence-transformers/all-MiniLM-L6-v2")
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--vector-top-k", type=int, default=20)
    parser.add_argument("--hard-negatives-per-query", type=int, default=4)
    parser.add_argument("--same-doc-negatives-per-query", type=int, default=2)
    parser.add_argument("--val-ratio", type=float, default=0.2)
    return parser.parse_args()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as infile:
        for line in infile:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def load_chunks(path: Path) -> list[ChunkRow]:
    rows = load_jsonl(path)
    return [
        ChunkRow(
            doc_id=str(row["doc_id"]),
            chunk_id=str(row["chunk_id"]),
            start=int(row["start"]),
            end=int(row["end"]),
            text=str(row["text"]),
        )
        for row in rows
    ]


def spans_overlap(start_a: int, end_a: int, start_b: int, end_b: int) -> bool:
    return max(start_a, start_b) < min(end_a, end_b)


def overlaps_expected(chunk: ChunkRow, expected_spans: list[dict[str, int]]) -> bool:
    return any(
        spans_overlap(chunk.start, chunk.end, int(span["start"]), int(span["end"]))
        for span in expected_spans
    )


def in_validation(doc_id: str, val_ratio: float) -> bool:
    digest = hashlib.sha1(doc_id.encode("utf-8")).hexdigest()
    bucket = int(digest[:8], 16) / 0xFFFFFFFF
    return bucket < val_ratio


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as outfile:
        for row in rows:
            outfile.write(json.dumps(row, ensure_ascii=False) + "\n")


def build_stats(rows: list[dict[str, Any]]) -> dict[str, float | int]:
    total = len(rows)
    positives = sum(1 for row in rows if int(row["label"]) == 1)
    negatives = total - positives
    hard_negs = sum(1 for row in rows if row["meta"].get("negative_type") == "hard")
    same_doc_negs = sum(
        1 for row in rows if row["meta"].get("negative_type") == "same_doc"
    )
    pos_rate = (positives / total) if total else 0.0
    return {
        "total": total,
        "positives": positives,
        "negatives": negatives,
        "positive_rate": round(pos_rate, 6),
        "hard_negatives": hard_negs,
        "same_doc_negatives": same_doc_negs,
    }


def is_boilerplate_heavy_chunk(text: str) -> bool:
    probe = " ".join(str(text).lower().split())
    if not probe:
        return False
    marker_hits = sum(1 for marker in HARD_NEGATIVE_BOILERPLATE_MARKERS if marker in probe)
    if marker_hits >= 2:
        return True
    return marker_hits >= 1 and probe.startswith("exhibit")


def main() -> None:
    args = parse_args()

    eval_rows = load_jsonl(args.evalset)
    eval_rows.sort(key=lambda row: str(row["id"]))

    chunks = load_chunks(args.metadata)
    if not chunks:
        raise ValueError(f"No chunk metadata rows found in {args.metadata}")

    chunks_by_doc: dict[str, list[ChunkRow]] = {}
    chunk_by_id: dict[str, ChunkRow] = {}
    for chunk in chunks:
        chunks_by_doc.setdefault(chunk.doc_id, []).append(chunk)
        chunk_by_id[chunk.chunk_id] = chunk

    for doc_id in chunks_by_doc:
        chunks_by_doc[doc_id].sort(key=lambda row: (row.start, row.end, row.chunk_id))

    model = SentenceTransformer(args.model, local_files_only=True)
    query_texts = [str(row["question"]) for row in eval_rows]
    query_vectors = model.encode(
        query_texts,
        batch_size=args.batch_size,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )
    query_vectors = np.asarray(query_vectors, dtype=np.float32)
    del model

    import faiss

    index = faiss.read_index(str(args.index))
    if index.ntotal != len(chunks):
        raise ValueError(
            f"Index vectors ({index.ntotal}) != metadata rows ({len(chunks)}): {args.index} vs {args.metadata}"
        )

    train_rows: list[dict[str, Any]] = []
    val_rows: list[dict[str, Any]] = []

    for i, item in enumerate(eval_rows, start=1):
        query_id = str(item["id"])
        doc_id = str(item["doc_id"])
        question = str(item["question"])
        clause_type = str(item["clause_type"])
        expected_spans = [
            {"start": int(span["start"]), "end": int(span["end"])}
            for span in item["expected_spans"]
        ]

        doc_chunks = chunks_by_doc.get(doc_id, [])
        positive_chunks = [chunk for chunk in doc_chunks if overlaps_expected(chunk, expected_spans)]
        positive_ids = {chunk.chunk_id for chunk in positive_chunks}

        same_doc_negatives = [chunk for chunk in doc_chunks if chunk.chunk_id not in positive_ids]
        same_doc_negatives = same_doc_negatives[: args.same_doc_negatives_per_query]

        query_vec = query_vectors[i - 1].reshape(1, -1)
        scores, hit_indices = index.search(query_vec, args.vector_top_k)

        hard_negatives: list[tuple[ChunkRow, float]] = []
        for idx, score in zip(hit_indices[0], scores[0]):
            if idx < 0:
                continue
            chunk = chunks[int(idx)]
            if chunk.doc_id == doc_id:
                continue
            if overlaps_expected(chunk, expected_spans):
                continue
            if is_boilerplate_heavy_chunk(chunk.text):
                continue
            hard_negatives.append((chunk, float(score)))
            if len(hard_negatives) >= args.hard_negatives_per_query:
                break

        if not positive_chunks:
            continue

        target_rows = val_rows if in_validation(doc_id, args.val_ratio) else train_rows

        for chunk in positive_chunks:
            target_rows.append(
                {
                    "query": question,
                    "text": chunk.text,
                    "label": 1,
                    "meta": {
                        "query_id": query_id,
                        "query_doc_id": doc_id,
                        "clause_type": clause_type,
                        "chunk_id": chunk.chunk_id,
                        "chunk_doc_id": chunk.doc_id,
                        "chunk_start": chunk.start,
                        "chunk_end": chunk.end,
                        "expected_spans": expected_spans,
                        "source": "positive_overlap_same_doc",
                    },
                }
            )

        for chunk, score in hard_negatives:
            target_rows.append(
                {
                    "query": question,
                    "text": chunk.text,
                    "label": 0,
                    "meta": {
                        "query_id": query_id,
                        "query_doc_id": doc_id,
                        "clause_type": clause_type,
                        "chunk_id": chunk.chunk_id,
                        "chunk_doc_id": chunk.doc_id,
                        "chunk_start": chunk.start,
                        "chunk_end": chunk.end,
                        "expected_spans": expected_spans,
                        "negative_type": "hard",
                        "vector_score": score,
                        "source": "vector_topk_non_overlap",
                    },
                }
            )

        for chunk in same_doc_negatives:
            target_rows.append(
                {
                    "query": question,
                    "text": chunk.text,
                    "label": 0,
                    "meta": {
                        "query_id": query_id,
                        "query_doc_id": doc_id,
                        "clause_type": clause_type,
                        "chunk_id": chunk.chunk_id,
                        "chunk_doc_id": chunk.doc_id,
                        "chunk_start": chunk.start,
                        "chunk_end": chunk.end,
                        "expected_spans": expected_spans,
                        "negative_type": "same_doc",
                        "source": "same_doc_non_overlap",
                    },
                }
            )

        if i % 200 == 0 or i == len(eval_rows):
            print(f"Processed {i}/{len(eval_rows)} eval queries")

    train_rows.sort(
        key=lambda row: (
            str(row["meta"]["query_id"]),
            int(row["label"]),
            str(row["meta"]["chunk_id"]),
        )
    )
    val_rows.sort(
        key=lambda row: (
            str(row["meta"]["query_id"]),
            int(row["label"]),
            str(row["meta"]["chunk_id"]),
        )
    )

    write_jsonl(args.train_out, train_rows)
    write_jsonl(args.val_out, val_rows)

    train_stats = build_stats(train_rows)
    val_stats = build_stats(val_rows)

    print(f"Wrote {len(train_rows)} rows to {args.train_out}")
    print(f"Wrote {len(val_rows)} rows to {args.val_out}")
    print("Train stats:", json.dumps(train_stats, sort_keys=True))
    print("Val stats:", json.dumps(val_stats, sort_keys=True))


if __name__ == "__main__":
    main()
