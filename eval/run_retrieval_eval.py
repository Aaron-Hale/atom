#!/usr/bin/env python3
"""Run Day 8 retrieval eval with vector-only vs base-reranker comparison."""

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

from app.services.rerank import BaseReranker


@dataclass(frozen=True)
class ChunkMeta:
    doc_id: str
    chunk_id: str
    start: int
    end: int
    text: str


@dataclass
class EvalResult:
    overall: dict[int, dict[str, float]]
    by_clause: dict[str, dict[int, dict[str, float]]]
    failures: list[dict[str, object]]
    hits_at_max_k: list[bool]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evalset", type=Path, default=Path("eval/evalset_v1.jsonl"))
    parser.add_argument("--index", type=Path, default=Path("data/faiss.index"))
    parser.add_argument("--metadata", type=Path, default=Path("data/chunk_metadata.jsonl"))
    parser.add_argument("--report", type=Path, default=Path("docs/report_rerank_baseline.md"))
    parser.add_argument("--model", default="sentence-transformers/all-MiniLM-L6-v2")
    parser.add_argument("--reranker", choices=["none", "base"], default="none")
    parser.add_argument("--reranker-model", default="cross-encoder/ms-marco-MiniLM-L6-v2")
    parser.add_argument("--rerank-candidates", type=int, default=20)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--top-k", type=int, nargs="+", default=[1, 3, 5, 10])
    parser.add_argument("--failure-examples", type=int, default=5)
    parser.add_argument("--comparison-examples", type=int, default=3)
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


def encode_questions(
    questions: list[str],
    model: SentenceTransformer,
) -> list[np.ndarray]:
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
    return vectors


def retrieve_vector_candidates(
    query_vectors: list[np.ndarray],
    metadata: list[ChunkMeta],
    index: Any,
    candidate_k: int,
) -> list[list[dict[str, object]]]:
    all_ranked: list[list[dict[str, object]]] = []
    total = len(query_vectors)

    for idx, vector in enumerate(query_vectors, start=1):
        query = vector.reshape(1, -1)
        score_row, index_row = index.search(query, candidate_k)

        ranked: list[dict[str, object]] = []
        for hit_idx, score in zip(index_row[0], score_row[0]):
            if hit_idx < 0:
                continue
            chunk = metadata[int(hit_idx)]
            ranked.append(
                {
                    "doc_id": chunk.doc_id,
                    "chunk_id": chunk.chunk_id,
                    "score": float(score),
                    "start": chunk.start,
                    "end": chunk.end,
                    "text": chunk.text,
                }
            )
        all_ranked.append(ranked)

        if idx % 200 == 0 or idx == total:
            print(f"Retrieved {idx}/{total} candidate sets")

    return all_ranked


def apply_base_reranker(
    eval_items: list[dict[str, object]],
    vector_rankings: list[list[dict[str, object]]],
    reranker: BaseReranker,
    top_k: int,
    batch_size: int,
) -> list[list[dict[str, object]]]:
    queries = [str(item["question"]) for item in eval_items]
    return reranker.rerank_batch(
        queries=queries,
        candidate_lists=vector_rankings,
        top_k=top_k,
        batch_size=batch_size,
    )


def evaluate_rankings(
    eval_items: list[dict[str, object]],
    ranked_candidates: list[list[dict[str, object]]],
    top_k_values: list[int],
) -> EvalResult:
    max_k = max(top_k_values)

    totals_by_k = {k: {"hits": 0, "recall_sum": 0.0} for k in top_k_values}
    clause_totals: dict[str, dict[int, dict[str, float]]] = defaultdict(
        lambda: {k: {"hits": 0, "recall_sum": 0.0, "count": 0} for k in top_k_values}
    )

    failures: list[dict[str, object]] = []
    hits_at_max_k: list[bool] = []

    for item, retrieved in zip(eval_items, ranked_candidates):
        expected_spans = [
            {"start": int(span["start"]), "end": int(span["end"])}
            for span in item["expected_spans"]  # type: ignore[index]
        ]
        num_expected = len(expected_spans)
        doc_id = str(item["doc_id"])
        clause_type = str(item["clause_type"])

        for k in top_k_values:
            top_chunks = retrieved[:k]

            covered = set()
            for chunk in top_chunks:
                if str(chunk["doc_id"]) != doc_id:
                    continue
                for span_idx, span in enumerate(expected_spans):
                    if spans_overlap(
                        int(chunk["start"]),
                        int(chunk["end"]),
                        span["start"],
                        span["end"],
                    ):
                        covered.add(span_idx)

            hit = 1 if covered else 0
            recall = (len(covered) / num_expected) if num_expected else 0.0

            totals_by_k[k]["hits"] += hit
            totals_by_k[k]["recall_sum"] += recall

            clause_totals[clause_type][k]["hits"] += hit
            clause_totals[clause_type][k]["recall_sum"] += recall
            clause_totals[clause_type][k]["count"] += 1

        max_k_hit = any(
            str(chunk["doc_id"]) == doc_id
            and any(
                spans_overlap(
                    int(chunk["start"]),
                    int(chunk["end"]),
                    span["start"],
                    span["end"],
                )
                for span in expected_spans
            )
            for chunk in retrieved[:max_k]
        )
        hits_at_max_k.append(max_k_hit)

        if not max_k_hit:
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
                            "score": round(float(chunk["score"]), 4),
                            "doc_id": chunk["doc_id"],
                            "chunk_id": chunk["chunk_id"],
                            "start": chunk["start"],
                            "end": chunk["end"],
                            "text_preview": str(chunk["text"])[:160].replace("\n", " "),
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

    return EvalResult(
        overall=overall,
        by_clause=by_clause,
        failures=failures,
        hits_at_max_k=hits_at_max_k,
    )


def collect_comparison_examples(
    eval_items: list[dict[str, object]],
    vector_hits: list[bool],
    rerank_hits: list[bool],
    vector_rankings: list[list[dict[str, object]]],
    rerank_rankings: list[list[dict[str, object]]],
    limit: int,
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    helped: list[dict[str, object]] = []
    regressed: list[dict[str, object]] = []

    for item, vec_hit, rr_hit, vec_chunks, rr_chunks in zip(
        eval_items,
        vector_hits,
        rerank_hits,
        vector_rankings,
        rerank_rankings,
    ):
        example = {
            "id": item["id"],
            "doc_id": item["doc_id"],
            "clause_type": item["clause_type"],
            "question": item["question"],
            "expected_spans": item["expected_spans"],
            "vector_top": [
                {
                    "rank": rank + 1,
                    "score": round(float(chunk["score"]), 4),
                    "doc_id": chunk["doc_id"],
                    "chunk_id": chunk["chunk_id"],
                    "start": chunk["start"],
                    "end": chunk["end"],
                    "text_preview": str(chunk["text"])[:120].replace("\n", " "),
                }
                for rank, chunk in enumerate(vec_chunks[:3])
            ],
            "rerank_top": [
                {
                    "rank": rank + 1,
                    "score": round(float(chunk["score"]), 4),
                    "doc_id": chunk["doc_id"],
                    "chunk_id": chunk["chunk_id"],
                    "start": chunk["start"],
                    "end": chunk["end"],
                    "text_preview": str(chunk["text"])[:120].replace("\n", " "),
                }
                for rank, chunk in enumerate(rr_chunks[:3])
            ],
        }

        if (not vec_hit) and rr_hit and len(helped) < limit:
            helped.append(example)
        if vec_hit and (not rr_hit) and len(regressed) < limit:
            regressed.append(example)

        if len(helped) >= limit and len(regressed) >= limit:
            break

    return helped, regressed


def write_top_chunks(lines: list[str], chunks: list[dict[str, object]]) -> None:
    for chunk in chunks:
        lines.append(
            "  - "
            + f"rank {chunk['rank']}, score {chunk['score']}, doc `{chunk['doc_id']}`, "
            + f"chunk `{chunk['chunk_id']}`, offsets [{chunk['start']}, {chunk['end']}], "
            + f"preview: \"{chunk['text_preview']}\""
        )


def write_report(
    report_path: Path,
    args: argparse.Namespace,
    eval_size: int,
    sample_question: str,
    vector_result: EvalResult,
    rerank_result: EvalResult | None,
    helped_examples: list[dict[str, object]],
    regressed_examples: list[dict[str, object]],
) -> None:
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    top_k_values = sorted(args.top_k)

    lines: list[str] = []
    lines.append("# Rerank Baseline Report (Day 8)")
    lines.append("")
    lines.append("## Experiment")
    lines.append(f"- Generated: {generated}")
    lines.append("- Purpose: compare vector-only retrieval vs vector + base cross-encoder reranking")
    lines.append(f"- Eval set: `{args.evalset}`")
    lines.append(f"- Eval items: {eval_size}")
    lines.append(f"- Index: `{args.index}`")
    lines.append(f"- Metadata: `{args.metadata}`")
    lines.append(f"- Vector encoder: `{args.model}`")
    lines.append(f"- Reranker mode: `{args.reranker}`")
    if rerank_result is not None:
        lines.append(f"- Base reranker: `{args.reranker_model}`")
        lines.append(f"- Rerank candidate pool: top {args.rerank_candidates} vector candidates")
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
    if rerank_result is None:
        lines.append("| Metric | " + " | ".join([f"@{k}" for k in top_k_values]) + " |")
        lines.append("| --- | " + " | ".join(["---"] * len(top_k_values)) + " |")
        lines.append(
            "| Hit@K | "
            + " | ".join(f"{vector_result.overall[k]['hit_at_k']:.4f}" for k in top_k_values)
            + " |"
        )
        lines.append(
            "| Recall@K | "
            + " | ".join(f"{vector_result.overall[k]['recall_at_k']:.4f}" for k in top_k_values)
            + " |"
        )
    else:
        lines.append(
            "| K | Vector Hit@K | Base Hit@K | Delta | Vector Recall@K | Base Recall@K | Delta |"
        )
        lines.append("| --- | --- | --- | --- | --- | --- | --- |")
        for k in top_k_values:
            v_hit = vector_result.overall[k]["hit_at_k"]
            r_hit = rerank_result.overall[k]["hit_at_k"]
            v_rec = vector_result.overall[k]["recall_at_k"]
            r_rec = rerank_result.overall[k]["recall_at_k"]
            lines.append(
                f"| {k} | {v_hit:.4f} | {r_hit:.4f} | {r_hit - v_hit:+.4f} | {v_rec:.4f} | {r_rec:.4f} | {r_rec - v_rec:+.4f} |"
            )

    lines.append("")
    lines.append("## Per-Clause Metrics")
    lines.append("")
    if rerank_result is None:
        lines.append("| Clause | N | " + " | ".join([f"Hit@{k} | Recall@{k}" for k in top_k_values]) + " |")
        lines.append("| --- | --- | " + " | ".join(["--- | ---"] * len(top_k_values)) + " |")
        for clause_type, clause_metrics in vector_result.by_clause.items():
            n = int(clause_metrics[top_k_values[0]]["count"])
            row = [clause_type, str(n)]
            for k in top_k_values:
                row.append(f"{clause_metrics[k]['hit_at_k']:.4f}")
                row.append(f"{clause_metrics[k]['recall_at_k']:.4f}")
            lines.append("| " + " | ".join(row) + " |")
    else:
        lines.append(
            "| Clause | N | "
            + " | ".join(
                [
                    f"Hit@{k} Vec | Hit@{k} Base | dHit@{k} | Rec@{k} Vec | Rec@{k} Base | dRec@{k}"
                    for k in top_k_values
                ]
            )
            + " |"
        )
        lines.append("| --- | --- | " + " | ".join(["--- | --- | --- | --- | --- | ---"] * len(top_k_values)) + " |")
        for clause_type in sorted(vector_result.by_clause):
            vec_clause = vector_result.by_clause[clause_type]
            rr_clause = rerank_result.by_clause[clause_type]
            n = int(vec_clause[top_k_values[0]]["count"])
            row = [clause_type, str(n)]
            for k in top_k_values:
                vec_hit = vec_clause[k]["hit_at_k"]
                rr_hit = rr_clause[k]["hit_at_k"]
                vec_rec = vec_clause[k]["recall_at_k"]
                rr_rec = rr_clause[k]["recall_at_k"]
                row.append(f"{vec_hit:.4f}")
                row.append(f"{rr_hit:.4f}")
                row.append(f"{rr_hit - vec_hit:+.4f}")
                row.append(f"{vec_rec:.4f}")
                row.append(f"{rr_rec:.4f}")
                row.append(f"{rr_rec - vec_rec:+.4f}")
            lines.append("| " + " | ".join(row) + " |")

    lines.append("")
    lines.append("## Comparison Examples")
    lines.append("")
    if rerank_result is None:
        lines.append("Reranker disabled; no vector-vs-reranker comparison examples.")
    else:
        lines.append("### Cases Where Reranking Helped")
        if not helped_examples:
            lines.append("No helped examples found in this run.")
        else:
            for idx, example in enumerate(helped_examples, start=1):
                lines.append(f"#### Helped {idx}: `{example['id']}`")
                lines.append(f"- Clause: `{example['clause_type']}`")
                lines.append(f"- Doc: `{example['doc_id']}`")
                lines.append(f"- Question: {example['question']}")
                lines.append(f"- Expected spans: {example['expected_spans']}")
                lines.append("- Vector top chunks:")
                write_top_chunks(lines, example["vector_top"])
                lines.append("- Base-reranked top chunks:")
                write_top_chunks(lines, example["rerank_top"])
                lines.append("")

        lines.append("### Cases Where Reranking Failed")
        if not regressed_examples:
            lines.append("No regressed examples found in this run.")
        else:
            for idx, example in enumerate(regressed_examples, start=1):
                lines.append(f"#### Regressed {idx}: `{example['id']}`")
                lines.append(f"- Clause: `{example['clause_type']}`")
                lines.append(f"- Doc: `{example['doc_id']}`")
                lines.append(f"- Question: {example['question']}")
                lines.append(f"- Expected spans: {example['expected_spans']}")
                lines.append("- Vector top chunks:")
                write_top_chunks(lines, example["vector_top"])
                lines.append("- Base-reranked top chunks:")
                write_top_chunks(lines, example["rerank_top"])
                lines.append("")

    lines.append("## Failure Examples (By Method)")
    lines.append("")
    lines.append("### Vector-Only Failures")
    vector_failures = vector_result.failures[: args.failure_examples]
    if not vector_failures:
        lines.append("No vector-only failures at max K in this run.")
    else:
        for idx, fail in enumerate(vector_failures, start=1):
            lines.append(f"#### Vector Failure {idx}: `{fail['id']}`")
            lines.append(f"- Clause: `{fail['clause_type']}`")
            lines.append(f"- Doc: `{fail['doc_id']}`")
            lines.append(f"- Question: {fail['question']}")
            lines.append(f"- Expected spans: {fail['expected_spans']}")
            lines.append("- Top retrieved chunks:")
            write_top_chunks(lines, fail["top_chunks"])
            lines.append("")

    if rerank_result is not None:
        lines.append("### Base-Reranker Failures")
        rerank_failures = rerank_result.failures[: args.failure_examples]
        if not rerank_failures:
            lines.append("No base-reranker failures at max K in this run.")
        else:
            for idx, fail in enumerate(rerank_failures, start=1):
                lines.append(f"#### Reranker Failure {idx}: `{fail['id']}`")
                lines.append(f"- Clause: `{fail['clause_type']}`")
                lines.append(f"- Doc: `{fail['doc_id']}`")
                lines.append(f"- Question: {fail['question']}")
                lines.append(f"- Expected spans: {fail['expected_spans']}")
                lines.append("- Top retrieved chunks:")
                write_top_chunks(lines, fail["top_chunks"])
                lines.append("")

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    top_k_values = sorted(set(int(k) for k in args.top_k))

    if args.reranker == "base" and max(top_k_values) > args.rerank_candidates:
        raise ValueError(
            f"max(top_k)={max(top_k_values)} exceeds rerank candidate pool {args.rerank_candidates}"
        )

    eval_items = load_jsonl(args.evalset)
    metadata = load_metadata(args.metadata)

    model = SentenceTransformer(args.model, local_files_only=True)
    import faiss

    index = faiss.read_index(str(args.index))

    questions = [str(item["question"]) for item in eval_items]
    query_vectors = encode_questions(questions=questions, model=model)

    candidate_k = max(max(top_k_values), args.rerank_candidates if args.reranker == "base" else 0)
    vector_rankings = retrieve_vector_candidates(
        query_vectors=query_vectors,
        metadata=metadata,
        index=index,
        candidate_k=candidate_k,
    )

    vector_result = evaluate_rankings(
        eval_items=eval_items,
        ranked_candidates=vector_rankings,
        top_k_values=top_k_values,
    )

    rerank_result: EvalResult | None = None
    helped_examples: list[dict[str, object]] = []
    regressed_examples: list[dict[str, object]] = []

    if args.reranker == "base":
        reranker = BaseReranker(model_name=args.reranker_model)
        rerank_rankings = apply_base_reranker(
            eval_items=eval_items,
            vector_rankings=[candidates[: args.rerank_candidates] for candidates in vector_rankings],
            reranker=reranker,
            top_k=args.rerank_candidates,
            batch_size=args.batch_size,
        )

        rerank_result = evaluate_rankings(
            eval_items=eval_items,
            ranked_candidates=rerank_rankings,
            top_k_values=top_k_values,
        )
        helped_examples, regressed_examples = collect_comparison_examples(
            eval_items=eval_items,
            vector_hits=vector_result.hits_at_max_k,
            rerank_hits=rerank_result.hits_at_max_k,
            vector_rankings=vector_rankings,
            rerank_rankings=rerank_rankings,
            limit=args.comparison_examples,
        )

    write_report(
        report_path=args.report,
        args=args,
        eval_size=len(eval_items),
        sample_question=str(eval_items[0]["question"]) if eval_items else "",
        vector_result=vector_result,
        rerank_result=rerank_result,
        helped_examples=helped_examples,
        regressed_examples=regressed_examples,
    )

    print(f"Evaluated {len(eval_items)} items")
    print("Vector-only metrics:")
    for k in top_k_values:
        print(
            f"  Hit@{k}: {vector_result.overall[k]['hit_at_k']:.4f} | "
            + f"Recall@{k}: {vector_result.overall[k]['recall_at_k']:.4f}"
        )

    if rerank_result is not None:
        print("Base-reranker metrics:")
        for k in top_k_values:
            print(
                f"  Hit@{k}: {rerank_result.overall[k]['hit_at_k']:.4f} | "
                + f"Recall@{k}: {rerank_result.overall[k]['recall_at_k']:.4f}"
            )

    print(f"Wrote report to {args.report}")


if __name__ == "__main__":
    main()
