#!/usr/bin/env python3
"""Run Day 7 vector-only retrieval eval with overlap metrics and markdown reporting."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
from sentence_transformers import SentenceTransformer


@dataclass(frozen=True)
class ChunkMeta:
    doc_id: str
    chunk_id: str
    start: int
    end: int
    text: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evalset", type=Path, default=Path("eval/evalset_v1.jsonl"))
    parser.add_argument("--index", type=Path, default=Path("data/faiss.index"))
    parser.add_argument("--metadata", type=Path, default=Path("data/chunk_metadata.jsonl"))
    parser.add_argument("--report", type=Path, default=Path("docs/report_retrieval_baseline.md"))
    parser.add_argument("--model", default="sentence-transformers/all-MiniLM-L6-v2")
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--top-k", type=int, nargs="+", default=[1, 3, 5, 10])
    parser.add_argument("--failure-examples", type=int, default=5)
    return parser.parse_args()


def load_jsonl(path: Path) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    with path.open("r", encoding="utf-8") as infile:
        for line in infile:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def load_metadata(path: Path) -> list[ChunkMeta]:
    rows = load_jsonl(path)
    return [
        ChunkMeta(
            doc_id=str(row["doc_id"]),
            chunk_id=str(row["chunk_id"]),
            start=int(row["start"]),
            end=int(row["end"]),
            text=str(row.get("text", "")),
        )
        for row in rows
    ]


def spans_overlap(start_a: int, end_a: int, start_b: int, end_b: int) -> bool:
    return max(start_a, start_b) < min(end_a, end_b)


def evaluate(
    eval_items: list[dict[str, object]],
    metadata: list[ChunkMeta],
    index: Any,
    model: SentenceTransformer,
    top_k_values: list[int],
    batch_size: int,
) -> tuple[dict[int, dict[str, float]], dict[str, dict[int, dict[str, float]]], list[dict[str, object]]]:
    max_k = max(top_k_values)
    questions = [str(item["question"]) for item in eval_items]

    # Encode one question at a time for runtime stability with the local env.
    vectors: list[np.ndarray] = []
    total = len(questions)
    for idx, question in enumerate(questions, start=1):
        vector = model.encode(
            [question],
            batch_size=1,
            show_progress_bar=False,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )
        vectors.append(np.asarray(vector[0], dtype=np.float32))
        if idx % 200 == 0 or idx == total:
            print(f"Encoded {idx}/{total} questions")

    totals_by_k = {k: {"hits": 0, "recall_sum": 0.0} for k in top_k_values}
    clause_totals: dict[str, dict[int, dict[str, float]]] = defaultdict(
        lambda: {k: {"hits": 0, "recall_sum": 0.0, "count": 0} for k in top_k_values}
    )

    failures: list[dict[str, object]] = []

    for row_idx, item in enumerate(eval_items):
        expected_spans = [
            {"start": int(span["start"]), "end": int(span["end"])}
            for span in item["expected_spans"]  # type: ignore[index]
        ]
        num_expected = len(expected_spans)
        doc_id = str(item["doc_id"])
        clause_type = str(item["clause_type"])

        query = vectors[row_idx].reshape(1, -1)
        score_row, index_row = index.search(query, max_k)
        retrieved = [metadata[i] for i in index_row[0] if i >= 0]
        retrieved_scores = [float(s) for s in score_row[0][: len(retrieved)]]

        for k in top_k_values:
            top_chunks = retrieved[:k]

            covered = set()
            for chunk in top_chunks:
                if chunk.doc_id != doc_id:
                    continue
                for span_idx, span in enumerate(expected_spans):
                    if spans_overlap(chunk.start, chunk.end, span["start"], span["end"]):
                        covered.add(span_idx)

            hit = 1 if covered else 0
            recall = (len(covered) / num_expected) if num_expected else 0.0

            totals_by_k[k]["hits"] += hit
            totals_by_k[k]["recall_sum"] += recall

            clause_totals[clause_type][k]["hits"] += hit
            clause_totals[clause_type][k]["recall_sum"] += recall
            clause_totals[clause_type][k]["count"] += 1

        if not any(
            chunk.doc_id == doc_id
            and any(
                spans_overlap(chunk.start, chunk.end, span["start"], span["end"])
                for span in expected_spans
            )
            for chunk in retrieved[:max_k]
        ):
            failures.append(
                {
                    "id": item["id"],
                    "doc_id": doc_id,
                    "clause_type": clause_type,
                    "question": item["question"],
                    "expected_spans": expected_spans,
                    "top_chunks": [
                        {
                            "rank": rank + 1,
                            "score": round(retrieved_scores[rank], 4),
                            "doc_id": chunk.doc_id,
                            "chunk_id": chunk.chunk_id,
                            "start": chunk.start,
                            "end": chunk.end,
                            "text_preview": chunk.text[:160].replace("\n", " "),
                        }
                        for rank, chunk in enumerate(retrieved[:3])
                    ],
                }
            )

    total_items = len(eval_items)
    overall = {
        k: {
            "hit_at_k": totals_by_k[k]["hits"] / total_items,
            "recall_at_k": totals_by_k[k]["recall_sum"] / total_items,
        }
        for k in top_k_values
    }

    by_clause: dict[str, dict[int, dict[str, float]]] = {}
    for clause_type in sorted(clause_totals):
        by_clause[clause_type] = {}
        for k in top_k_values:
            count = clause_totals[clause_type][k]["count"]
            by_clause[clause_type][k] = {
                "hit_at_k": clause_totals[clause_type][k]["hits"] / count if count else 0.0,
                "recall_at_k": clause_totals[clause_type][k]["recall_sum"] / count if count else 0.0,
                "count": float(count),
            }

    return overall, by_clause, failures


def format_table_header(top_k_values: list[int]) -> str:
    headers = ["Clause", "N"]
    for k in top_k_values:
        headers.append(f"Hit@{k}")
        headers.append(f"Recall@{k}")
    return "| " + " | ".join(headers) + " |"


def format_table_separator(top_k_values: list[int]) -> str:
    cols = ["---", "---"] + ["---"] * (2 * len(top_k_values))
    return "| " + " | ".join(cols) + " |"


def write_report(
    report_path: Path,
    args: argparse.Namespace,
    eval_size: int,
    sample_question: str,
    overall: dict[int, dict[str, float]],
    by_clause: dict[str, dict[int, dict[str, float]]],
    failures: list[dict[str, object]],
) -> None:
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    top_k_values = sorted(args.top_k)
    failure_examples = failures[: args.failure_examples]

    lines: list[str] = []
    lines.append("# Retrieval Baseline Report (Day 7, Vector-Only)")
    lines.append("")
    lines.append("## Experiment")
    lines.append(f"- Generated: {generated}")
    lines.append("- Purpose: baseline vector retrieval quality on deterministic eval set")
    lines.append(f"- Eval set: `{args.evalset}`")
    lines.append(f"- Eval items: {eval_size}")
    lines.append(f"- Index: `{args.index}`")
    lines.append(f"- Metadata: `{args.metadata}`")
    lines.append(f"- Encoder: `{args.model}`")
    lines.append(f"- Top-K: {top_k_values}")
    lines.append(
        '- Query policy: deterministic contract-specific question format `In the agreement "<title cue>", '
        'find the <clause_type> clause.`'
    )
    lines.append("- Title cue policy: first meaningful contract header/title line from source text after skipping filing boilerplate lines")
    lines.append(f"- Example question: {sample_question}")
    lines.append("")
    lines.append("## Overall Metrics")
    lines.append("")
    lines.append("| Metric | " + " | ".join([f"@{k}" for k in top_k_values]) + " |")
    lines.append("| --- | " + " | ".join(["---"] * len(top_k_values)) + " |")
    lines.append(
        "| Hit@K | " + " | ".join(f"{overall[k]['hit_at_k']:.4f}" for k in top_k_values) + " |"
    )
    lines.append(
        "| Recall@K | "
        + " | ".join(f"{overall[k]['recall_at_k']:.4f}" for k in top_k_values)
        + " |"
    )
    lines.append("")
    lines.append("## Per-Clause Metrics")
    lines.append("")
    lines.append(format_table_header(top_k_values))
    lines.append(format_table_separator(top_k_values))
    for clause_type, clause_metrics in by_clause.items():
        n = int(clause_metrics[top_k_values[0]]["count"])
        row = [clause_type, str(n)]
        for k in top_k_values:
            row.append(f"{clause_metrics[k]['hit_at_k']:.4f}")
            row.append(f"{clause_metrics[k]['recall_at_k']:.4f}")
        lines.append("| " + " | ".join(row) + " |")

    lines.append("")
    lines.append("## Failure Examples")
    lines.append("")
    if not failure_examples:
        lines.append("No failures at max K in this run.")
    else:
        for idx, fail in enumerate(failure_examples, start=1):
            lines.append(f"### Example {idx}: `{fail['id']}`")
            lines.append(f"- Clause: `{fail['clause_type']}`")
            lines.append(f"- Doc: `{fail['doc_id']}`")
            lines.append(f"- Question: {fail['question']}")
            lines.append(f"- Expected spans: {fail['expected_spans']}")
            lines.append("- Top retrieved chunks:")
            for chunk in fail["top_chunks"]:
                lines.append(
                    "  - "
                    + f"rank {chunk['rank']}, score {chunk['score']}, doc `{chunk['doc_id']}`, "
                    + f"chunk `{chunk['chunk_id']}`, offsets [{chunk['start']}, {chunk['end']}], "
                    + f"preview: \"{chunk['text_preview']}\""
                )
            lines.append("")

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    top_k_values = sorted(set(int(k) for k in args.top_k))

    eval_items = load_jsonl(args.evalset)
    metadata = load_metadata(args.metadata)
    model = SentenceTransformer(args.model, local_files_only=True)
    import faiss

    index = faiss.read_index(str(args.index))

    overall, by_clause, failures = evaluate(
        eval_items=eval_items,
        metadata=metadata,
        index=index,
        model=model,
        top_k_values=top_k_values,
        batch_size=args.batch_size,
    )

    write_report(
        report_path=args.report,
        args=args,
        eval_size=len(eval_items),
        sample_question=str(eval_items[0]["question"]) if eval_items else "",
        overall=overall,
        by_clause=by_clause,
        failures=failures,
    )

    print(f"Evaluated {len(eval_items)} items")
    for k in top_k_values:
        print(f"Hit@{k}: {overall[k]['hit_at_k']:.4f} | Recall@{k}: {overall[k]['recall_at_k']:.4f}")
    print(f"Wrote report to {args.report}")


if __name__ == "__main__":
    main()
