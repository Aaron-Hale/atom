#!/usr/bin/env python3
"""Deterministic CUAD export into canonical contract and label JSONL stores."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

# Day 4 canonical clause taxonomy.
CLAUSE_TYPES_V1 = [
    "assignment",
    "change_of_control",
    "confidentiality",
    "exclusivity",
    "governing_law",
    "limitation_of_liability",
    "most_favored_nation",
    "non_compete",
    "termination",
    "warranty",
]

_CLAUSE_ALIASES = {
    "anti_assignment": "assignment",
    "assignment_and_delegation": "assignment",
    "change_in_control": "change_of_control",
    "change_of_control": "change_of_control",
    "confidentiality": "confidentiality",
    "non_disclosure": "confidentiality",
    "exclusive_rights": "exclusivity",
    "exclusivity": "exclusivity",
    "governing_law": "governing_law",
    "choice_of_law": "governing_law",
    "limitation_of_liability": "limitation_of_liability",
    "liability_cap": "limitation_of_liability",
    "cap_on_liability": "limitation_of_liability",
    "uncapped_liability": "limitation_of_liability",
    "most_favored_nation": "most_favored_nation",
    "most_favoured_nation": "most_favored_nation",
    "mfn": "most_favored_nation",
    "non_compete": "non_compete",
    "non_competition": "non_compete",
    "termination": "termination",
    "term_and_termination": "termination",
    "termination_for_convenience": "termination",
    "warranties": "warranty",
    "warranty": "warranty",
}

HF_CUAD_JSON = "hf://datasets/kenlevine/CUAD/CUAD_v1.json"


@dataclass(frozen=True)
class ContractRecord:
    doc_id: str
    text: str


@dataclass(frozen=True)
class RawLabel:
    doc_id: str
    clause_type: str
    start: int
    end: int


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--cuad-path",
        type=Path,
        default=None,
        help="Optional local CUAD JSON override (SQuAD-style). Defaults to Hugging Face CUAD.",
    )
    parser.add_argument("--contracts-out", type=Path, default=Path("data/contracts.jsonl"))
    parser.add_argument("--labels-out", type=Path, default=Path("data/labels.jsonl"))
    return parser.parse_args()


def slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value or "document"


def stable_doc_id(source_id: str, text: str) -> str:
    basis = source_id if source_id else text
    digest = hashlib.sha1(basis.encode("utf-8")).hexdigest()[:12]
    return f"cuad_{slugify(source_id)[:40]}_{digest}"


def normalize_clause_type(raw_value: str) -> str | None:
    raw = raw_value or ""
    candidates = [raw]

    # CUAD question strings can contain the clause taxonomy in quoted text.
    quoted = re.findall(r'"([^"]+)"|\'([^\']+)\'', raw)
    for q1, q2 in quoted:
        candidates.append(q1 or q2)

    match = re.search(r'related to\s+"([^"]+)"', raw, flags=re.IGNORECASE)
    if match:
        candidates.append(match.group(1))

    for candidate_raw in candidates:
        candidate_clean = candidate_raw.split("Details:")[0].strip()
        normalized = slugify(candidate_clean)
        if not normalized:
            continue

        if normalized in _CLAUSE_ALIASES:
            clause = _CLAUSE_ALIASES[normalized]
            return clause if clause in CLAUSE_TYPES_V1 else None

        if "confidential" in normalized:
            return "confidentiality"
        if "indemn" in normalized and "indemnification" in CLAUSE_TYPES_V1:
            return "indemnification"

        for candidate in CLAUSE_TYPES_V1:
            if candidate in normalized:
                return candidate
    return None


def resolve_clause_type(qa: dict[str, Any]) -> str | None:
    qa_id = str(qa.get("id", ""))
    question = str(qa.get("question", ""))
    return normalize_clause_type(qa_id) or normalize_clause_type(question)


def _payload_from_dataset_row(row: dict[str, Any]) -> dict[str, Any]:
    if isinstance(row.get("data"), list):
        return {"data": row["data"]}
    raise ValueError("Expected CUAD row with top-level 'data' list.")


def load_cuad_payload(cuad_path: Path | None) -> tuple[dict[str, Any], str]:
    try:
        from datasets import load_dataset
    except ImportError as exc:
        raise RuntimeError(
            "Missing dependency 'datasets'. Install it (for example: pip install datasets) "
            "or run this script in the project virtual environment."
        ) from exc

    try:
        if cuad_path is not None:
            if not cuad_path.exists():
                raise FileNotFoundError(f"Local CUAD file not found: {cuad_path}")
            dataset = load_dataset("json", data_files={"train": str(cuad_path)})
            source = str(cuad_path)
        else:
            dataset = load_dataset("json", data_files={"train": HF_CUAD_JSON})
            source = HF_CUAD_JSON
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(
            "Failed to load CUAD. Use network access for Hugging Face default or pass "
            "--cuad-path /path/to/CUAD_v1.json for a local override."
        ) from exc

    if "train" not in dataset or len(dataset["train"]) == 0:
        raise RuntimeError("Loaded CUAD dataset has no rows.")
    payload = _payload_from_dataset_row(dataset["train"][0])
    return payload, source


def iter_cuad_documents(payload: dict[str, Any]) -> Iterable[tuple[str, str, list[dict[str, Any]]]]:
    """Yield (source_id, context_text, qas) from SQuAD-style CUAD payload."""
    for article in payload.get("data", []):
        title = str(article.get("title", "")).strip() or "untitled"
        for p_idx, paragraph in enumerate(article.get("paragraphs", [])):
            context = paragraph.get("context", "")
            if not isinstance(context, str):
                continue
            source_id = f"{title}#{p_idx}"
            qas = paragraph.get("qas", [])
            if not isinstance(qas, list):
                qas = []
            yield source_id, context, qas


def extract_labels(doc_id: str, text: str, qas: list[dict[str, Any]]) -> list[RawLabel]:
    out: list[RawLabel] = []
    for qa in qas:
        clause_type = resolve_clause_type(qa)
        if clause_type is None:
            continue

        answers = qa.get("answers", [])
        if not isinstance(answers, list):
            continue

        for answer in answers:
            start = answer.get("answer_start")
            answer_text = answer.get("text", "")
            if not isinstance(start, int) or not isinstance(answer_text, str):
                continue
            end = start + len(answer_text)
            if start < 0 or end > len(text) or start >= end:
                continue
            out.append(RawLabel(doc_id=doc_id, clause_type=clause_type, start=start, end=end))
    return out


def build_exports(
    payload: dict[str, Any]
) -> tuple[list[ContractRecord], list[dict[str, Any]], dict[str, int], dict[str, int], dict[str, int]]:
    contracts: list[ContractRecord] = []
    raw_labels: list[RawLabel] = []
    clause_qa_counts: dict[str, int] = {clause: 0 for clause in CLAUSE_TYPES_V1}
    clause_span_counts: dict[str, int] = {clause: 0 for clause in CLAUSE_TYPES_V1}

    for source_id, text, qas in iter_cuad_documents(payload):
        doc_id = stable_doc_id(source_id=source_id, text=text)
        contracts.append(ContractRecord(doc_id=doc_id, text=text))

        for qa in qas:
            clause_type = resolve_clause_type(qa)
            if clause_type is not None:
                clause_qa_counts[clause_type] += 1

        labels = extract_labels(doc_id=doc_id, text=text, qas=qas)
        raw_labels.extend(labels)
        for label in labels:
            clause_span_counts[label.clause_type] += 1

    # Deterministic ordering.
    contracts.sort(key=lambda c: c.doc_id)

    grouped: dict[tuple[str, str], set[tuple[int, int]]] = defaultdict(set)
    for label in raw_labels:
        grouped[(label.doc_id, label.clause_type)].add((label.start, label.end))

    labels_out: list[dict[str, Any]] = []
    clause_label_row_counts: dict[str, int] = {clause: 0 for clause in CLAUSE_TYPES_V1}
    for (doc_id, clause_type), spans in sorted(grouped.items(), key=lambda kv: (kv[0][0], kv[0][1])):
        clause_label_row_counts[clause_type] += 1
        labels_out.append(
            {
                "doc_id": doc_id,
                "clause_type": clause_type,
                "spans": [{"start": start, "end": end} for start, end in sorted(spans)],
            }
        )

    return contracts, labels_out, clause_qa_counts, clause_label_row_counts, clause_span_counts


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True, sort_keys=True) + "\n")


def main() -> None:
    args = parse_args()
    payload, source = load_cuad_payload(args.cuad_path)

    contracts, labels, clause_qa_counts, clause_label_row_counts, clause_span_counts = build_exports(payload)
    if not contracts or not labels:
        raise RuntimeError(
            "Export would be empty; aborting. Verify CUAD input and clause mapping. "
            "Expected non-zero contracts and labels."
        )
    missing_clause_types = [clause for clause in CLAUSE_TYPES_V1 if clause_qa_counts[clause] == 0]
    if missing_clause_types:
        raise RuntimeError(
            "Selected clause types are unavailable in CUAD question/id fields: "
            f"{', '.join(missing_clause_types)}. "
            "Update normalization/parsing or explicitly remove unavailable types from CLAUSE_TYPES_V1."
        )

    write_jsonl(args.contracts_out, ({"doc_id": c.doc_id, "text": c.text} for c in contracts))
    write_jsonl(args.labels_out, labels)

    print(f"source: {source}")
    print(f"contracts: {len(contracts)}")
    print(f"label rows (doc_id+clause_type): {len(labels)}")
    print("per-clause mapped qa entries:")
    for clause in CLAUSE_TYPES_V1:
        print(f"{clause}: {clause_qa_counts[clause]}")
    print("per-clause label rows (doc_id+clause_type):")
    for clause in CLAUSE_TYPES_V1:
        print(f"{clause}: {clause_label_row_counts[clause]}")
    print("per-clause span counts (individual answer spans):")
    for clause in CLAUSE_TYPES_V1:
        print(f"{clause}: {clause_span_counts[clause]}")


if __name__ == "__main__":
    main()
