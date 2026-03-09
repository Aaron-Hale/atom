#!/usr/bin/env python3
"""Run retrieval eval with vector-only, base reranker, and LoRA reranker modes."""

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

from app.services.rerank import BaseReranker, LoraReranker


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


@dataclass(frozen=True)
class CoverageResult:
    overall: dict[int, dict[str, float]]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evalset", type=Path, default=Path("eval/evalset_v1.jsonl"))
    parser.add_argument("--index", type=Path, default=Path("data/faiss.index"))
    parser.add_argument("--metadata", type=Path, default=Path("data/chunk_metadata.jsonl"))
    parser.add_argument("--report", type=Path, default=Path("docs/report_rerank_baseline.md"))
    parser.add_argument("--model", default="sentence-transformers/all-MiniLM-L6-v2")
    parser.add_argument("--reranker", choices=["none", "base", "lora"], default="none")
    parser.add_argument("--reranker-model", default="cross-encoder/ms-marco-MiniLM-L6-v2")
    parser.add_argument("--lora-adapter", type=Path, default=Path("models/reranker_lora"))
    parser.add_argument("--rerank-candidates", type=int, default=20)
    parser.add_argument(
        "--reranker-query-mode",
        choices=["natural", "clause_only", "structured_clause"],
        default="natural",
    )
    parser.add_argument("--reranker-vector-weight", type=float, default=0.0)
    parser.add_argument("--reranker-boilerplate-penalty", type=float, default=0.0)
    parser.add_argument("--reranker-filter-boilerplate", action="store_true")
    parser.add_argument("--reranker-boilerplate-max-start", type=int, default=1800)
    parser.add_argument("--reranker-min-candidates-after-filter", type=int, default=5)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--top-k", type=int, nargs="+", default=[1, 3, 5, 10])
    parser.add_argument("--coverage-k", type=int, nargs="+", default=[20, 50, 100])
    parser.add_argument("--failure-examples", type=int, default=5)
    parser.add_argument("--comparison-examples", type=int, default=3)
    return parser.parse_args()


def normalize_clause_type(clause_type: str) -> str:
    return clause_type.replace("_", " ").strip()


def build_reranker_query(item: dict[str, object], query_mode: str) -> str:
    if query_mode == "natural":
        return str(item["question"])

    clause_label = normalize_clause_type(str(item["clause_type"]))
    if query_mode == "clause_only":
        return f"{clause_label} clause"

    return f"Find the clause in this contract. Clause type: {clause_label}."


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


def apply_reranker(
    eval_items: list[dict[str, object]],
    vector_rankings: list[list[dict[str, object]]],
    reranker: Any,
    top_k: int,
    batch_size: int,
    query_mode: str,
    vector_weight: float,
    boilerplate_penalty: float,
    boilerplate_filter: bool,
    boilerplate_max_start: int,
    min_candidates_after_filter: int,
) -> list[list[dict[str, object]]]:
    queries = [build_reranker_query(item=item, query_mode=query_mode) for item in eval_items]
    return reranker.rerank_batch(
        queries=queries,
        candidate_lists=vector_rankings,
        top_k=top_k,
        batch_size=batch_size,
        vector_weight=vector_weight,
        boilerplate_penalty=boilerplate_penalty,
        boilerplate_filter=boilerplate_filter,
        boilerplate_max_start=boilerplate_max_start,
        min_candidates_after_filter=min_candidates_after_filter,
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


def evaluate_candidate_coverage(
    eval_items: list[dict[str, object]],
    ranked_candidates: list[list[dict[str, object]]],
    top_k_values: list[int],
) -> CoverageResult:
    totals_by_k = {k: {"hits": 0, "recall_sum": 0.0} for k in top_k_values}

    for item, retrieved in zip(eval_items, ranked_candidates):
        expected_spans = [
            {"start": int(span["start"]), "end": int(span["end"])}
            for span in item["expected_spans"]  # type: ignore[index]
        ]
        num_expected = len(expected_spans)
        doc_id = str(item["doc_id"])

        for k in top_k_values:
            covered = set()
            for chunk in retrieved[:k]:
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

            totals_by_k[k]["hits"] += 1 if covered else 0
            totals_by_k[k]["recall_sum"] += (len(covered) / num_expected) if num_expected else 0.0

    total_items = len(eval_items)
    return CoverageResult(
        overall={
            k: {
                "candidate_hit_at_k": totals_by_k[k]["hits"] / total_items,
                "oracle_recall_at_k": totals_by_k[k]["recall_sum"] / total_items,
            }
            for k in top_k_values
        }
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
    coverage_result: CoverageResult,
    coverage_k_values: list[int],
    base_result: EvalResult | None,
    lora_result: EvalResult | None,
    base_helped_examples: list[dict[str, object]],
    base_regressed_examples: list[dict[str, object]],
    lora_helped_examples: list[dict[str, object]],
    lora_regressed_examples: list[dict[str, object]],
) -> None:
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    top_k_values = sorted(args.top_k)

    lines: list[str] = []
    lines.append("# Reranker Evaluation Report")
    lines.append("")
    lines.append("## Experiment")
    lines.append(f"- Generated: {generated}")
    lines.append("- Purpose: compare vector-only retrieval against base and LoRA reranker modes")
    lines.append(f"- Eval set: `{args.evalset}`")
    lines.append(f"- Eval items: {eval_size}")
    lines.append(f"- Index: `{args.index}`")
    lines.append(f"- Metadata: `{args.metadata}`")
    lines.append(f"- Vector encoder: `{args.model}`")
    lines.append(f"- Reranker mode: `{args.reranker}`")
    if args.reranker != "none":
        lines.append(f"- Reranker backbone: `{args.reranker_model}`")
        lines.append(f"- LoRA adapter path: `{args.lora_adapter}`")
        lines.append(f"- Rerank candidate pool: top {args.rerank_candidates} vector candidates")
        lines.append(f"- Reranker query mode: `{args.reranker_query_mode}`")
        lines.append(f"- Score blend vector weight: {args.reranker_vector_weight:.2f}")
        lines.append(f"- Boilerplate penalty: {args.reranker_boilerplate_penalty:.2f}")
        lines.append(f"- Boilerplate filter enabled: `{args.reranker_filter_boilerplate}`")
        lines.append(f"- Boilerplate max-start: {args.reranker_boilerplate_max_start}")
        lines.append(
            f"- Min candidates after filter fallback: {args.reranker_min_candidates_after_filter}"
        )
    lines.append(f"- Top-K: {top_k_values}")
    if args.reranker_query_mode == "natural":
        lines.append(
            '- Reranker query policy: deterministic contract-specific question format `In the agreement "<title cue>", '
            'find the <clause_type> clause.`'
        )
        lines.append(
            "- Title cue policy: first meaningful contract header/title line from source text after skipping filing boilerplate lines"
        )
    elif args.reranker_query_mode == "clause_only":
        lines.append("- Reranker query policy: deterministic clause label only (`<clause_type> clause`)")
    else:
        lines.append(
            "- Reranker query policy: deterministic structured clause prompt (`Find the clause in this contract. Clause type: <clause_type>.`)"
        )
    lines.append(f"- Example reranker query: {sample_question}")
    lines.append("")
    lines.append("## Vector Candidate Coverage (Oracle Overlap)")
    lines.append("")
    lines.append("| K | Candidate Hit@K | Oracle Recall@K |")
    lines.append("| --- | --- | --- |")
    for k in coverage_k_values:
        lines.append(
            f"| {k} | {coverage_result.overall[k]['candidate_hit_at_k']:.4f} | {coverage_result.overall[k]['oracle_recall_at_k']:.4f} |"
        )
    lines.append("")

    lines.append("## Overall Metrics")
    lines.append("")
    if base_result is None and lora_result is None:
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
        if base_result is not None and lora_result is not None:
            lines.append(
                "| K | Vec Hit@K | Base Hit@K | LoRA Hit@K | dBase | dLoRA | Vec Rec@K | Base Rec@K | LoRA Rec@K | dBase | dLoRA |"
            )
            lines.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
        elif base_result is not None:
            lines.append(
                "| K | Vector Hit@K | Base Hit@K | Delta | Vector Recall@K | Base Recall@K | Delta |"
            )
            lines.append("| --- | --- | --- | --- | --- | --- | --- |")
        else:
            lines.append(
                "| K | Vector Hit@K | LoRA Hit@K | Delta | Vector Recall@K | LoRA Recall@K | Delta |"
            )
            lines.append("| --- | --- | --- | --- | --- | --- | --- |")
        for k in top_k_values:
            v_hit = vector_result.overall[k]["hit_at_k"]
            v_rec = vector_result.overall[k]["recall_at_k"]
            if base_result is not None and lora_result is not None:
                b_hit = base_result.overall[k]["hit_at_k"]
                l_hit = lora_result.overall[k]["hit_at_k"]
                b_rec = base_result.overall[k]["recall_at_k"]
                l_rec = lora_result.overall[k]["recall_at_k"]
                lines.append(
                    f"| {k} | {v_hit:.4f} | {b_hit:.4f} | {l_hit:.4f} | {b_hit - v_hit:+.4f} | {l_hit - v_hit:+.4f} | {v_rec:.4f} | {b_rec:.4f} | {l_rec:.4f} | {b_rec - v_rec:+.4f} | {l_rec - v_rec:+.4f} |"
                )
            elif base_result is not None:
                b_hit = base_result.overall[k]["hit_at_k"]
                b_rec = base_result.overall[k]["recall_at_k"]
                lines.append(
                    f"| {k} | {v_hit:.4f} | {b_hit:.4f} | {b_hit - v_hit:+.4f} | {v_rec:.4f} | {b_rec:.4f} | {b_rec - v_rec:+.4f} |"
                )
            else:
                l_hit = lora_result.overall[k]["hit_at_k"]  # type: ignore[index]
                l_rec = lora_result.overall[k]["recall_at_k"]  # type: ignore[index]
                lines.append(
                    f"| {k} | {v_hit:.4f} | {l_hit:.4f} | {l_hit - v_hit:+.4f} | {v_rec:.4f} | {l_rec:.4f} | {l_rec - v_rec:+.4f} |"
                )

    lines.append("")
    lines.append("## Per-Clause Metrics")
    lines.append("")
    if base_result is None and lora_result is None:
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
        if base_result is not None and lora_result is not None:
            lines.append(
                "| Clause | N | "
                + " | ".join(
                    [
                        f"Hit@{k} Vec | Hit@{k} Base | Hit@{k} LoRA | dBase | dLoRA | Rec@{k} Vec | Rec@{k} Base | Rec@{k} LoRA | dBase | dLoRA"
                        for k in top_k_values
                    ]
                )
                + " |"
            )
            lines.append(
                "| --- | --- | "
                + " | ".join(
                    ["--- | --- | --- | --- | --- | --- | --- | --- | --- | ---"] * len(top_k_values)
                )
                + " |"
            )
        elif base_result is not None:
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
        else:
            lines.append(
                "| Clause | N | "
                + " | ".join(
                    [
                        f"Hit@{k} Vec | Hit@{k} LoRA | dHit@{k} | Rec@{k} Vec | Rec@{k} LoRA | dRec@{k}"
                        for k in top_k_values
                    ]
                )
                + " |"
            )
            lines.append("| --- | --- | " + " | ".join(["--- | --- | --- | --- | --- | ---"] * len(top_k_values)) + " |")
        for clause_type in sorted(vector_result.by_clause):
            vec_clause = vector_result.by_clause[clause_type]
            n = int(vec_clause[top_k_values[0]]["count"])
            row = [clause_type, str(n)]
            for k in top_k_values:
                vec_hit = vec_clause[k]["hit_at_k"]
                vec_rec = vec_clause[k]["recall_at_k"]
                if base_result is not None and lora_result is not None:
                    b_clause = base_result.by_clause[clause_type]
                    l_clause = lora_result.by_clause[clause_type]
                    b_hit = b_clause[k]["hit_at_k"]
                    l_hit = l_clause[k]["hit_at_k"]
                    b_rec = b_clause[k]["recall_at_k"]
                    l_rec = l_clause[k]["recall_at_k"]
                    row.append(f"{vec_hit:.4f}")
                    row.append(f"{b_hit:.4f}")
                    row.append(f"{l_hit:.4f}")
                    row.append(f"{b_hit - vec_hit:+.4f}")
                    row.append(f"{l_hit - vec_hit:+.4f}")
                    row.append(f"{vec_rec:.4f}")
                    row.append(f"{b_rec:.4f}")
                    row.append(f"{l_rec:.4f}")
                    row.append(f"{b_rec - vec_rec:+.4f}")
                    row.append(f"{l_rec - vec_rec:+.4f}")
                elif base_result is not None:
                    b_clause = base_result.by_clause[clause_type]
                    b_hit = b_clause[k]["hit_at_k"]
                    b_rec = b_clause[k]["recall_at_k"]
                    row.append(f"{vec_hit:.4f}")
                    row.append(f"{b_hit:.4f}")
                    row.append(f"{b_hit - vec_hit:+.4f}")
                    row.append(f"{vec_rec:.4f}")
                    row.append(f"{b_rec:.4f}")
                    row.append(f"{b_rec - vec_rec:+.4f}")
                else:
                    l_clause = lora_result.by_clause[clause_type]  # type: ignore[index]
                    l_hit = l_clause[k]["hit_at_k"]
                    l_rec = l_clause[k]["recall_at_k"]
                    row.append(f"{vec_hit:.4f}")
                    row.append(f"{l_hit:.4f}")
                    row.append(f"{l_hit - vec_hit:+.4f}")
                    row.append(f"{vec_rec:.4f}")
                    row.append(f"{l_rec:.4f}")
                    row.append(f"{l_rec - vec_rec:+.4f}")
            lines.append("| " + " | ".join(row) + " |")

    lines.append("")
    lines.append("## Comparison Examples")
    lines.append("")
    if base_result is None and lora_result is None:
        lines.append("Reranker disabled; no vector-vs-reranker comparison examples.")
    else:
        if base_result is not None:
            lines.append("### Base: Cases Where Reranking Helped")
            if not base_helped_examples:
                lines.append("No base helped examples found in this run.")
            else:
                for idx, example in enumerate(base_helped_examples, start=1):
                    lines.append(f"#### Base Helped {idx}: `{example['id']}`")
                    lines.append(f"- Clause: `{example['clause_type']}`")
                    lines.append(f"- Doc: `{example['doc_id']}`")
                    lines.append(f"- Question: {example['question']}")
                    lines.append(f"- Expected spans: {example['expected_spans']}")
                    lines.append("- Vector top chunks:")
                    write_top_chunks(lines, example["vector_top"])
                    lines.append("- Base-reranked top chunks:")
                    write_top_chunks(lines, example["rerank_top"])
                    lines.append("")

            lines.append("### Base: Cases Where Reranking Failed")
            if not base_regressed_examples:
                lines.append("No base regressed examples found in this run.")
            else:
                for idx, example in enumerate(base_regressed_examples, start=1):
                    lines.append(f"#### Base Regressed {idx}: `{example['id']}`")
                    lines.append(f"- Clause: `{example['clause_type']}`")
                    lines.append(f"- Doc: `{example['doc_id']}`")
                    lines.append(f"- Question: {example['question']}")
                    lines.append(f"- Expected spans: {example['expected_spans']}")
                    lines.append("- Vector top chunks:")
                    write_top_chunks(lines, example["vector_top"])
                    lines.append("- Base-reranked top chunks:")
                    write_top_chunks(lines, example["rerank_top"])
                    lines.append("")

        if lora_result is not None:
            lines.append("### LoRA: Cases Where Reranking Helped")
            if not lora_helped_examples:
                lines.append("No LoRA helped examples found in this run.")
            else:
                for idx, example in enumerate(lora_helped_examples, start=1):
                    lines.append(f"#### LoRA Helped {idx}: `{example['id']}`")
                    lines.append(f"- Clause: `{example['clause_type']}`")
                    lines.append(f"- Doc: `{example['doc_id']}`")
                    lines.append(f"- Question: {example['question']}")
                    lines.append(f"- Expected spans: {example['expected_spans']}")
                    lines.append("- Vector top chunks:")
                    write_top_chunks(lines, example["vector_top"])
                    lines.append("- LoRA-reranked top chunks:")
                    write_top_chunks(lines, example["rerank_top"])
                    lines.append("")

            lines.append("### LoRA: Cases Where Reranking Failed")
            if not lora_regressed_examples:
                lines.append("No LoRA regressed examples found in this run.")
            else:
                for idx, example in enumerate(lora_regressed_examples, start=1):
                    lines.append(f"#### LoRA Regressed {idx}: `{example['id']}`")
                    lines.append(f"- Clause: `{example['clause_type']}`")
                    lines.append(f"- Doc: `{example['doc_id']}`")
                    lines.append(f"- Question: {example['question']}")
                    lines.append(f"- Expected spans: {example['expected_spans']}")
                    lines.append("- Vector top chunks:")
                    write_top_chunks(lines, example["vector_top"])
                    lines.append("- LoRA-reranked top chunks:")
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

    if base_result is not None:
        lines.append("### Base-Reranker Failures")
        base_failures = base_result.failures[: args.failure_examples]
        if not base_failures:
            lines.append("No base-reranker failures at max K in this run.")
        else:
            for idx, fail in enumerate(base_failures, start=1):
                lines.append(f"#### Base Failure {idx}: `{fail['id']}`")
                lines.append(f"- Clause: `{fail['clause_type']}`")
                lines.append(f"- Doc: `{fail['doc_id']}`")
                lines.append(f"- Question: {fail['question']}")
                lines.append(f"- Expected spans: {fail['expected_spans']}")
                lines.append("- Top retrieved chunks:")
                write_top_chunks(lines, fail["top_chunks"])
                lines.append("")
    if lora_result is not None:
        lines.append("### LoRA-Reranker Failures")
        lora_failures = lora_result.failures[: args.failure_examples]
        if not lora_failures:
            lines.append("No LoRA-reranker failures at max K in this run.")
        else:
            for idx, fail in enumerate(lora_failures, start=1):
                lines.append(f"#### LoRA Failure {idx}: `{fail['id']}`")
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
    coverage_k_values = sorted(set(int(k) for k in args.coverage_k))
    if not (0.0 <= args.reranker_vector_weight <= 1.0):
        raise ValueError("--reranker-vector-weight must be in [0.0, 1.0]")
    if args.reranker_boilerplate_penalty < 0.0:
        raise ValueError("--reranker-boilerplate-penalty must be >= 0.0")
    if args.reranker_boilerplate_max_start < 0:
        raise ValueError("--reranker-boilerplate-max-start must be >= 0")
    if args.reranker_min_candidates_after_filter < 1:
        raise ValueError("--reranker-min-candidates-after-filter must be >= 1")

    if args.reranker != "none" and max(top_k_values) > args.rerank_candidates:
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

    candidate_k = max(
        max(top_k_values),
        max(coverage_k_values),
        args.rerank_candidates if args.reranker != "none" else 0,
    )
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
    coverage_result = evaluate_candidate_coverage(
        eval_items=eval_items,
        ranked_candidates=vector_rankings,
        top_k_values=coverage_k_values,
    )

    base_result: EvalResult | None = None
    lora_result: EvalResult | None = None
    base_helped_examples: list[dict[str, object]] = []
    base_regressed_examples: list[dict[str, object]] = []
    lora_helped_examples: list[dict[str, object]] = []
    lora_regressed_examples: list[dict[str, object]] = []

    rerank_inputs = [candidates[: args.rerank_candidates] for candidates in vector_rankings]
    if args.reranker in {"base", "lora"}:
        base_reranker = BaseReranker(model_name=args.reranker_model)
        base_rankings = apply_reranker(
            eval_items=eval_items,
            vector_rankings=rerank_inputs,
            reranker=base_reranker,
            top_k=args.rerank_candidates,
            batch_size=args.batch_size,
            query_mode=args.reranker_query_mode,
            vector_weight=args.reranker_vector_weight,
            boilerplate_penalty=args.reranker_boilerplate_penalty,
            boilerplate_filter=args.reranker_filter_boilerplate,
            boilerplate_max_start=args.reranker_boilerplate_max_start,
            min_candidates_after_filter=args.reranker_min_candidates_after_filter,
        )

        base_result = evaluate_rankings(
            eval_items=eval_items,
            ranked_candidates=base_rankings,
            top_k_values=top_k_values,
        )
        base_helped_examples, base_regressed_examples = collect_comparison_examples(
            eval_items=eval_items,
            vector_hits=vector_result.hits_at_max_k,
            rerank_hits=base_result.hits_at_max_k,
            vector_rankings=vector_rankings,
            rerank_rankings=base_rankings,
            limit=args.comparison_examples,
        )
    if args.reranker == "lora":
        lora_reranker = LoraReranker(
            model_name=args.reranker_model,
            adapter_path=str(args.lora_adapter),
        )
        lora_rankings = apply_reranker(
            eval_items=eval_items,
            vector_rankings=rerank_inputs,
            reranker=lora_reranker,
            top_k=args.rerank_candidates,
            batch_size=args.batch_size,
            query_mode=args.reranker_query_mode,
            vector_weight=args.reranker_vector_weight,
            boilerplate_penalty=args.reranker_boilerplate_penalty,
            boilerplate_filter=args.reranker_filter_boilerplate,
            boilerplate_max_start=args.reranker_boilerplate_max_start,
            min_candidates_after_filter=args.reranker_min_candidates_after_filter,
        )
        lora_result = evaluate_rankings(
            eval_items=eval_items,
            ranked_candidates=lora_rankings,
            top_k_values=top_k_values,
        )
        lora_helped_examples, lora_regressed_examples = collect_comparison_examples(
            eval_items=eval_items,
            vector_hits=vector_result.hits_at_max_k,
            rerank_hits=lora_result.hits_at_max_k,
            vector_rankings=vector_rankings,
            rerank_rankings=lora_rankings,
            limit=args.comparison_examples,
        )

    write_report(
        report_path=args.report,
        args=args,
        eval_size=len(eval_items),
        sample_question=(
            build_reranker_query(
                item=eval_items[0],
                query_mode=args.reranker_query_mode,
            )
            if eval_items
            else ""
        ),
        vector_result=vector_result,
        coverage_result=coverage_result,
        coverage_k_values=coverage_k_values,
        base_result=base_result,
        lora_result=lora_result,
        base_helped_examples=base_helped_examples,
        base_regressed_examples=base_regressed_examples,
        lora_helped_examples=lora_helped_examples,
        lora_regressed_examples=lora_regressed_examples,
    )

    print(f"Evaluated {len(eval_items)} items")
    print("Vector-only metrics:")
    for k in top_k_values:
        print(
            f"  Hit@{k}: {vector_result.overall[k]['hit_at_k']:.4f} | "
            + f"Recall@{k}: {vector_result.overall[k]['recall_at_k']:.4f}"
        )
    print("Vector candidate coverage/oracle overlap:")
    for k in coverage_k_values:
        print(
            f"  Top-{k}: Candidate Hit={coverage_result.overall[k]['candidate_hit_at_k']:.4f} | "
            + f"Oracle Recall={coverage_result.overall[k]['oracle_recall_at_k']:.4f}"
        )

    if base_result is not None:
        print("Base-reranker metrics:")
        for k in top_k_values:
            print(
                f"  Hit@{k}: {base_result.overall[k]['hit_at_k']:.4f} | "
                + f"Recall@{k}: {base_result.overall[k]['recall_at_k']:.4f}"
            )
    if lora_result is not None:
        print("LoRA-reranker metrics:")
        for k in top_k_values:
            print(
                f"  Hit@{k}: {lora_result.overall[k]['hit_at_k']:.4f} | "
                + f"Recall@{k}: {lora_result.overall[k]['recall_at_k']:.4f}"
            )

    print(f"Wrote report to {args.report}")


if __name__ == "__main__":
    main()
