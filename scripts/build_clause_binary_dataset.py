#!/usr/bin/env python3
"""Build deterministic clause-conditioned binary chunk datasets."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


CLAUSE_KEYWORDS: dict[str, list[str]] = {
    "assignment": ["assign", "assignment", "transfer", "delegate"],
    "change_of_control": ["change of control", "acquisition", "merger", "control"],
    "confidentiality": ["confidential", "non-disclosure", "disclose", "privacy"],
    "exclusivity": ["exclusive", "exclusivity", "sole", "only"],
    "governing_law": ["governing law", "laws of", "jurisdiction", "venue"],
    "limitation_of_liability": ["limitation of liability", "liable", "damages", "liability cap"],
    "most_favored_nation": ["most favored nation", "mfN", "most-favored"],
    "non_compete": ["non-compete", "non compete", "compete", "competitive"],
    "termination": ["terminate", "termination", "expire", "end of term"],
    "warranty": ["warrant", "warranty", "as is", "merchantability"],
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chunks", type=Path, default=Path("data/chunks.jsonl"))
    parser.add_argument("--labels", type=Path, default=Path("data/labels.jsonl"))
    parser.add_argument("--train-out", type=Path, default=Path("data/clause_binary_train.jsonl"))
    parser.add_argument("--val-out", type=Path, default=Path("data/clause_binary_val.jsonl"))
    parser.add_argument("--val-ratio", type=float, default=0.2)
    parser.add_argument("--max-nearby-neg", type=int, default=2)
    parser.add_argument("--max-same-doc-neg", type=int, default=1)
    parser.add_argument("--max-cross-doc-neg", type=int, default=1)
    parser.add_argument("--max-absent-neg", type=int, default=1)
    return parser.parse_args()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as infile:
        for line in infile:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as out:
        for row in rows:
            out.write(json.dumps(row, ensure_ascii=False) + "\n")


def stable_hash(text: str) -> int:
    return int(hashlib.sha1(text.encode("utf-8")).hexdigest()[:16], 16)


def in_validation(doc_id: str, val_ratio: float) -> bool:
    bucket = int(hashlib.sha1(doc_id.encode("utf-8")).hexdigest()[:8], 16) / 0xFFFFFFFF
    return bucket < val_ratio


def overlap_len(a_start: int, a_end: int, b_start: int, b_end: int) -> int:
    return max(0, min(a_end, b_end) - max(a_start, b_start))


def keyword_hits(clause_type: str, text: str) -> int:
    lowered = text.lower()
    return sum(1 for kw in CLAUSE_KEYWORDS.get(clause_type, []) if kw.lower() in lowered)


def main() -> None:
    args = parse_args()
    if not (0.0 < args.val_ratio < 1.0):
        raise ValueError("--val-ratio must be in (0, 1)")

    chunk_rows = load_jsonl(args.chunks)
    label_rows = load_jsonl(args.labels)
    if not chunk_rows or not label_rows:
        raise ValueError("Input files must be non-empty")

    clause_types = sorted({str(row["clause_type"]) for row in label_rows})
    spans_by_doc_clause: dict[str, dict[str, list[tuple[int, int]]]] = defaultdict(lambda: defaultdict(list))
    for row in label_rows:
        doc_id = str(row["doc_id"])
        clause_type = str(row["clause_type"])
        for span in row["spans"]:
            spans_by_doc_clause[doc_id][clause_type].append((int(span["start"]), int(span["end"])))

    chunks_by_doc: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in chunk_rows:
        chunks_by_doc[str(row["doc_id"])].append(row)
    for doc_id in chunks_by_doc:
        chunks_by_doc[doc_id].sort(key=lambda r: (int(r["start"]), int(r["end"]), str(r["chunk_id"])))

    positive_idx_by_doc_clause: dict[str, dict[str, set[int]]] = defaultdict(lambda: defaultdict(set))
    all_neg_by_clause: dict[str, list[tuple[str, int, int]]] = defaultdict(list)

    for doc_id, doc_chunks in chunks_by_doc.items():
        spans_for_doc = spans_by_doc_clause.get(doc_id, {})
        for clause_type in clause_types:
            spans = spans_for_doc.get(clause_type, [])
            for i, chunk in enumerate(doc_chunks):
                c_start = int(chunk["start"])
                c_end = int(chunk["end"])
                is_positive = any(overlap_len(c_start, c_end, s, e) > 0 for s, e in spans)
                if is_positive:
                    positive_idx_by_doc_clause[doc_id][clause_type].add(i)

    for doc_id, doc_chunks in chunks_by_doc.items():
        for clause_type in clause_types:
            pos_idx = positive_idx_by_doc_clause[doc_id].get(clause_type, set())
            for i, chunk in enumerate(doc_chunks):
                if i in pos_idx:
                    continue
                hits = keyword_hits(clause_type, str(chunk["text"]))
                all_neg_by_clause[clause_type].append((doc_id, i, hits))

    for clause_type in clause_types:
        all_neg_by_clause[clause_type].sort(
            key=lambda t: (-t[2], stable_hash(f"{clause_type}|{t[0]}|{t[1]}"))
        )

    examples: list[dict[str, Any]] = []

    def add_example(doc_id: str, chunk: dict[str, Any], clause_type: str, label: int, source: str) -> None:
        text_a = f"Clause type: {clause_type}. Does this chunk contain evidence for this clause?"
        examples.append(
            {
                "example_id": f"{chunk['chunk_id']}|{clause_type}|{label}|{source}",
                "doc_id": doc_id,
                "chunk_id": str(chunk["chunk_id"]),
                "clause_type": clause_type,
                "text_a": text_a,
                "text_b": str(chunk["text"]),
                "label": int(label),
                "source": source,
                "start": int(chunk["start"]),
                "end": int(chunk["end"]),
            }
        )

    for doc_id in sorted(chunks_by_doc):
        doc_chunks = chunks_by_doc[doc_id]
        for clause_type in clause_types:
            pos_idx = sorted(positive_idx_by_doc_clause[doc_id].get(clause_type, set()))
            neg_idx = [i for i in range(len(doc_chunks)) if i not in set(pos_idx)]

            for p in pos_idx:
                pos_chunk = doc_chunks[p]
                add_example(doc_id, pos_chunk, clause_type, 1, "positive_overlap")

                selected: set[int] = set()

                nearby = sorted(neg_idx, key=lambda i: (abs(i - p), i))[: args.max_nearby_neg]
                for n in nearby:
                    add_example(doc_id, doc_chunks[n], clause_type, 0, "nearby_same_doc")
                    selected.add(n)

                remaining_same_doc = [i for i in neg_idx if i not in selected]
                remaining_same_doc.sort(key=lambda i: stable_hash(f"same|{doc_id}|{clause_type}|{p}|{i}"))
                for n in remaining_same_doc[: args.max_same_doc_neg]:
                    add_example(doc_id, doc_chunks[n], clause_type, 0, "same_doc_non_overlap")
                    selected.add(n)

                if args.max_cross_doc_neg > 0 and all_neg_by_clause[clause_type]:
                    start_idx = stable_hash(f"cross|{doc_id}|{clause_type}|{p}") % len(all_neg_by_clause[clause_type])
                    picked = 0
                    for offset in range(len(all_neg_by_clause[clause_type])):
                        cand_doc, cand_i, _ = all_neg_by_clause[clause_type][(start_idx + offset) % len(all_neg_by_clause[clause_type])]
                        if cand_doc == doc_id:
                            continue
                        add_example(cand_doc, chunks_by_doc[cand_doc][cand_i], clause_type, 0, "cross_doc_hard")
                        picked += 1
                        if picked >= args.max_cross_doc_neg:
                            break

            if not pos_idx and args.max_absent_neg > 0 and neg_idx:
                scored = []
                for i in neg_idx:
                    chunk = doc_chunks[i]
                    hits = keyword_hits(clause_type, str(chunk["text"]))
                    scored.append((i, hits))
                scored.sort(key=lambda t: (-t[1], stable_hash(f"absent|{doc_id}|{clause_type}|{t[0]}")))
                for i, _ in scored[: args.max_absent_neg]:
                    add_example(doc_id, doc_chunks[i], clause_type, 0, "clause_absent_doc")

    deduped: dict[str, dict[str, Any]] = {}
    for row in examples:
        deduped[row["example_id"]] = row
    all_rows = sorted(
        deduped.values(),
        key=lambda r: (r["doc_id"], r["clause_type"], r["chunk_id"], r["label"], r["source"]),
    )

    train_rows: list[dict[str, Any]] = []
    val_rows: list[dict[str, Any]] = []
    for row in all_rows:
        if in_validation(str(row["doc_id"]), args.val_ratio):
            val_rows.append(row)
        else:
            train_rows.append(row)

    write_jsonl(args.train_out, train_rows)
    write_jsonl(args.val_out, val_rows)

    train_y = Counter(int(r["label"]) for r in train_rows)
    val_y = Counter(int(r["label"]) for r in val_rows)
    train_source = Counter(str(r["source"]) for r in train_rows)
    val_source = Counter(str(r["source"]) for r in val_rows)

    print(f"Wrote {len(train_rows)} rows to {args.train_out}")
    print(f"Wrote {len(val_rows)} rows to {args.val_out}")
    print("Clause types:", clause_types)
    print("Train label counts:", json.dumps(dict(sorted(train_y.items())), sort_keys=True))
    print("Val label counts:", json.dumps(dict(sorted(val_y.items())), sort_keys=True))
    print("Train source counts:", json.dumps(dict(sorted(train_source.items())), sort_keys=True))
    print("Val source counts:", json.dumps(dict(sorted(val_source.items())), sort_keys=True))


if __name__ == "__main__":
    main()
