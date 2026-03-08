#!/usr/bin/env python3
"""Build a deterministic retrieval eval set from exported CUAD labels."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

NOISE_PREFIXES = ("REDACTED", "CONFIDENTIAL", "SOURCE:")
TITLE_HINTS = ("agreement", "contract", "amendment", "license", "lease", "policy", "plan")
TITLE_BOILERPLATE_MARKERS = (
    "confidential treatment requested",
    "confidential treatment has been requested",
    "confidential portions of this",
    "redacted provisions",
    "confidential portion has been filed",
    "filed with the commission",
    "securities and exchange commission",
    "pursuant to 17 c.f.r",
    "has been omitted",
    "has been redacted",
    "table of contents",
)
NON_TITLE_SECTION_MARKERS = (
    "term of contract",
    "witnesseth",
    "recitals",
    "table of contents",
    "miscellaneous provisions",
    "consultant's obligations",
    "adams golf's obligations",
    "termination",
    "definitions",
)
NON_TITLE_PHRASES = (
    "entered into",
    "during the term",
    "whereas",
    "now therefore",
    "the parties agree",
    "shall be",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--labels", type=Path, default=Path("data/labels.jsonl"))
    parser.add_argument("--contracts", type=Path, default=Path("data/contracts.jsonl"))
    parser.add_argument("--out", type=Path, default=Path("eval/evalset_v1.jsonl"))
    return parser.parse_args()


def _sorted_spans(spans: list[dict[str, int]]) -> list[dict[str, int]]:
    return sorted(
        ({"start": int(span["start"]), "end": int(span["end"])} for span in spans),
        key=lambda span: (span["start"], span["end"]),
    )


def load_contract_texts(path: Path) -> dict[str, str]:
    texts: dict[str, str] = {}
    with path.open("r", encoding="utf-8") as infile:
        for line in infile:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            texts[str(row["doc_id"])] = str(row.get("text", ""))
    return texts


def extract_title_cue(contract_text: str, doc_id: str) -> str:
    def normalize_title_candidate(value: str) -> str:
        cue = re.sub(r"\s+", " ", value).strip()
        cue = re.sub(
            r"^.*?(?:filed with the commission|securities and exchange commission)\s+",
            "",
            cue,
            flags=re.IGNORECASE,
        )
        cue = re.sub(
            r"^.*?(?:confidential treatment requested|confidential portions of this)\s+",
            "",
            cue,
            flags=re.IGNORECASE,
        )
        cue = re.sub(
            r"^(?:Execution Version|EXHIBIT\s+[A-Za-z0-9.\-]+(?:[:\-\s]+|$))+",
            "",
            cue,
            flags=re.IGNORECASE,
        )
        cue = re.sub(r"^This\s+", "", cue, flags=re.IGNORECASE)
        return cue.strip()

    def is_title_boilerplate(value: str) -> bool:
        lowered = value.lower()
        return any(marker in lowered for marker in TITLE_BOILERPLATE_MARKERS)

    def is_plausible_title(value: str) -> bool:
        lowered = value.lower()
        if any(marker in lowered for marker in NON_TITLE_SECTION_MARKERS):
            return False
        if any(phrase in lowered for phrase in NON_TITLE_PHRASES):
            return False
        if " this agreement" in lowered:
            return False
        if any(ch in value for ch in ",;:"):
            return False
        if not any(hint in lowered for hint in TITLE_HINTS):
            return False
        tail = lowered.rstrip(" .-)'\"")
        if not (
            tail.endswith(TITLE_HINTS)
            or "agreement and plan" in lowered
        ):
            return False
        if len(value) > 120:
            return False
        word_count = len(value.split())
        if word_count < 2 or word_count > 14:
            return False
        alpha_chars = [ch for ch in value if ch.isalpha()]
        if not alpha_chars:
            return False
        upper_ratio = sum(1 for ch in alpha_chars if ch.isupper()) / len(alpha_chars)
        titlecase_words = [
            token for token in re.findall(r"[A-Za-z][A-Za-z0-9'/-]*", value) if token[0].isupper()
        ]
        titlecase_ratio = len(titlecase_words) / max(len(value.split()), 1)
        if upper_ratio < 0.45 and titlecase_ratio < 0.65:
            return False
        return True

    fallback = doc_id.replace("cuad_", "").replace("_", " ")[:80].strip() or doc_id
    for raw_line in contract_text.splitlines()[:160]:
        line_text = re.sub(r"\s+", " ", raw_line).strip()
        if not line_text:
            continue
        if line_text.upper().startswith(NOISE_PREFIXES):
            continue
        for pattern in (
            r"([A-Z][A-Z0-9,&/\-\(\)\' ]{4,140}?(?:AGREEMENT|CONTRACT|AMENDMENT|LICENSE|LEASE|PLAN))",
            r"([A-Z][A-Za-z0-9,&/\-\(\)\' ]{4,140}?(?:Agreement|Contract|Amendment|License|Lease|Plan))",
        ):
            for match in re.finditer(pattern, line_text):
                cue = normalize_title_candidate(match.group(1))
                if len(cue) >= 6 and not is_title_boilerplate(cue) and is_plausible_title(cue):
                    return cue[:120]

    lines = contract_text.splitlines()
    cleaned_lines: list[str] = []
    for line in lines[:200]:
        text = re.sub(r"\s+", " ", line).strip()
        if not text:
            continue
        if text.upper().startswith(NOISE_PREFIXES):
            continue
        if is_title_boilerplate(text):
            continue
        if len(text) < 5:
            continue
        if sum(ch.isalpha() for ch in text) < 4:
            continue
        cleaned_lines.append(text)

    if not cleaned_lines:
        return fallback

    def is_section_line(value: str) -> bool:
        return bool(re.match(r"^(\(?\d+[\.\)]|[A-Za-z]\)|[ivxlcdmIVXLCDM]+\.)\s", value))

    def looks_like_header(value: str) -> bool:
        if is_section_line(value):
            return False
        if len(value) > 110:
            return False
        words = value.split()
        if len(words) > 16:
            return False
        alpha_chars = [ch for ch in value if ch.isalpha()]
        if not alpha_chars:
            return False
        upper_ratio = sum(1 for ch in alpha_chars if ch.isupper()) / len(alpha_chars)
        return upper_ratio >= 0.45

    for line in cleaned_lines:
        lower = line.lower()
        if (
            looks_like_header(line)
            and any(hint in lower for hint in TITLE_HINTS)
            and not is_title_boilerplate(line)
            and is_plausible_title(line)
        ):
            return normalize_title_candidate(line)[:120]

    for line in cleaned_lines:
        if (
            looks_like_header(line)
            and not is_title_boilerplate(line)
            and is_plausible_title(line)
        ):
            return normalize_title_candidate(line)[:120]

    for line in cleaned_lines:
        lower = line.lower()
        if (
            any(hint in lower for hint in TITLE_HINTS)
            and not is_section_line(line)
            and not is_title_boilerplate(line)
            and is_plausible_title(line)
        ):
            return normalize_title_candidate(line)[:120]

    return normalize_title_candidate(cleaned_lines[0])[:120]


def build_evalset(labels_path: Path, contracts_path: Path) -> list[dict[str, object]]:
    contract_texts = load_contract_texts(contracts_path)
    rows: list[dict[str, object]] = []

    with labels_path.open("r", encoding="utf-8") as infile:
        for line in infile:
            line = line.strip()
            if not line:
                continue

            record = json.loads(line)
            clause_type = str(record["clause_type"])
            clause_name = clause_type.replace("_", " ")
            title_cue = extract_title_cue(
                contract_texts.get(str(record["doc_id"]), ""),
                str(record["doc_id"]),
            )
            question = f'In the agreement "{title_cue}", find the {clause_name} clause.'

            rows.append(
                {
                    "id": f"{record['doc_id']}::{clause_type}",
                    "doc_id": record["doc_id"],
                    "clause_type": clause_type,
                    "question": question,
                    "expected_spans": _sorted_spans(record["spans"]),
                }
            )

    rows.sort(key=lambda row: (str(row["doc_id"]), str(row["clause_type"]), str(row["id"])))
    return rows


def write_jsonl(rows: list[dict[str, object]], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as outfile:
        for row in rows:
            outfile.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> None:
    args = parse_args()
    rows = build_evalset(args.labels, args.contracts)
    write_jsonl(rows, args.out)
    print(f"Wrote {len(rows)} eval rows to {args.out}")


if __name__ == "__main__":
    main()
