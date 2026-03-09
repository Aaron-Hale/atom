#!/usr/bin/env python3
"""Evaluate clause-conditioned binary detector: lexical vs pretrained vs LoRA."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np
import torch
from peft import PeftModel
from sklearn.metrics import (
    average_precision_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from transformers import AutoModelForSequenceClassification, AutoTokenizer


CLAUSE_KEYWORDS: dict[str, list[str]] = {
    "assignment": ["assign", "assignment", "transfer", "delegate"],
    "change_of_control": ["change of control", "acquisition", "merger", "control"],
    "confidentiality": ["confidential", "non-disclosure", "disclose", "privacy"],
    "exclusivity": ["exclusive", "exclusivity", "sole", "only"],
    "governing_law": ["governing law", "laws of", "jurisdiction", "venue"],
    "limitation_of_liability": ["limitation of liability", "liable", "damages", "liability cap"],
    "most_favored_nation": ["most favored nation", "mfn", "most-favored"],
    "non_compete": ["non-compete", "non compete", "compete", "competitive"],
    "termination": ["terminate", "termination", "expire", "end of term"],
    "warranty": ["warrant", "warranty", "as is", "merchantability"],
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train-file", type=Path, default=Path("data/clause_binary_train.jsonl"))
    parser.add_argument("--val-file", type=Path, default=Path("data/clause_binary_val.jsonl"))
    parser.add_argument("--base-model", default="cross-encoder/ms-marco-MiniLM-L6-v2")
    parser.add_argument("--adapter", type=Path, default=Path("models/clause_binary_lora"))
    parser.add_argument("--report", type=Path, default=Path("docs/report_clause_binary_lora.md"))
    parser.add_argument("--max-length", type=int, default=256)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--threshold-train-max", type=int, default=20000)
    parser.add_argument("--error-examples", type=int, default=12)
    return parser.parse_args()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as infile:
        for line in infile:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def lexical_score(rows: list[dict[str, Any]]) -> np.ndarray:
    scores: list[float] = []
    for row in rows:
        clause = str(row["clause_type"])
        text = str(row["text_b"]).lower()
        kws = CLAUSE_KEYWORDS.get(clause, [clause.replace("_", " ")])
        hits = sum(1 for kw in kws if kw.lower() in text)
        score = hits / max(1, len(kws))
        scores.append(float(score))
    return np.asarray(scores, dtype=np.float32)


def predict_scores(model: Any, tokenizer: Any, rows: list[dict[str, Any]], max_length: int, batch_size: int) -> np.ndarray:
    model.eval()
    model = model.to("cpu")
    scores: list[np.ndarray] = []
    with torch.no_grad():
        for i in range(0, len(rows), batch_size):
            batch = rows[i : i + batch_size]
            a = [str(r["text_a"]) for r in batch]
            b = [str(r["text_b"]) for r in batch]
            encoded = tokenizer(a, b, truncation=True, max_length=max_length, padding=True, return_tensors="pt")
            logits = model(**encoded).logits
            if logits.shape[-1] == 1:
                out = torch.sigmoid(logits.squeeze(-1)).cpu().numpy()
            else:
                out = torch.softmax(logits, dim=-1)[:, 1].cpu().numpy()
            scores.append(out)
    return np.concatenate(scores) if scores else np.asarray([], dtype=np.float32)


def best_threshold(y_true: np.ndarray, scores: np.ndarray) -> tuple[float, float]:
    unique = np.unique(scores)
    if unique.size > 200:
        candidates = np.unique(np.quantile(scores, np.linspace(0.01, 0.99, 200)))
    else:
        candidates = unique
    best_t = 0.5
    best_f1 = -1.0
    for t in candidates:
        pred = (scores >= float(t)).astype(np.int64)
        f1 = f1_score(y_true, pred, zero_division=0)
        if f1 > best_f1:
            best_f1 = float(f1)
            best_t = float(t)
    return best_t, best_f1


def metrics_at_threshold(y_true: np.ndarray, scores: np.ndarray, threshold: float) -> dict[str, float]:
    pred = (scores >= threshold).astype(np.int64)
    pr_auc = float(average_precision_score(y_true, scores)) if len(np.unique(y_true)) > 1 else 0.0
    roc_auc = float(roc_auc_score(y_true, scores)) if len(np.unique(y_true)) > 1 else 0.0
    return {
        "threshold": float(threshold),
        "pr_auc": pr_auc,
        "roc_auc": roc_auc,
        "f1": float(f1_score(y_true, pred, zero_division=0)),
        "precision": float(precision_score(y_true, pred, zero_division=0)),
        "recall": float(recall_score(y_true, pred, zero_division=0)),
    }


def per_clause_metrics(rows: list[dict[str, Any]], scores: np.ndarray, threshold: float) -> dict[str, dict[str, float]]:
    by_clause: dict[str, list[int]] = defaultdict(list)
    for i, row in enumerate(rows):
        by_clause[str(row["clause_type"])].append(i)

    out: dict[str, dict[str, float]] = {}
    for clause in sorted(by_clause):
        idx = by_clause[clause]
        y = np.asarray([int(rows[i]["label"]) for i in idx], dtype=np.int64)
        s = scores[idx]
        p = (s >= threshold).astype(np.int64)
        pr_auc = float(average_precision_score(y, s)) if len(np.unique(y)) > 1 else 0.0
        roc_auc = float(roc_auc_score(y, s)) if len(np.unique(y)) > 1 else 0.0
        out[clause] = {
            "support": int(y.size),
            "positives": int(y.sum()),
            "precision": float(precision_score(y, p, zero_division=0)),
            "recall": float(recall_score(y, p, zero_division=0)),
            "f1": float(f1_score(y, p, zero_division=0)),
            "pr_auc": pr_auc,
            "roc_auc": roc_auc,
        }
    return out


def macro_from_per_clause(per_clause: dict[str, dict[str, float]]) -> dict[str, float]:
    keys = ["precision", "recall", "f1", "pr_auc", "roc_auc"]
    out: dict[str, float] = {}
    for k in keys:
        vals = [v[k] for v in per_clause.values()]
        out[f"macro_{k}"] = float(np.mean(vals)) if vals else 0.0
    return out


def main() -> None:
    args = parse_args()

    train_rows = load_jsonl(args.train_file)
    val_rows = load_jsonl(args.val_file)
    if not train_rows or not val_rows:
        raise ValueError("Train/val files must be non-empty")

    y_train = np.asarray([int(r["label"]) for r in train_rows], dtype=np.int64)
    y_val = np.asarray([int(r["label"]) for r in val_rows], dtype=np.int64)

    train_subset = train_rows[: min(len(train_rows), args.threshold_train_max)]
    y_train_subset = y_train[: len(train_subset)]

    tokenizer = AutoTokenizer.from_pretrained(args.base_model, local_files_only=True)

    base_model = AutoModelForSequenceClassification.from_pretrained(args.base_model, local_files_only=True)

    lora_base = AutoModelForSequenceClassification.from_pretrained(
        args.base_model,
        num_labels=2,
        ignore_mismatched_sizes=True,
        local_files_only=True,
    )
    lora_model = PeftModel.from_pretrained(lora_base, str(args.adapter), local_files_only=True)

    train_scores_lex = lexical_score(train_subset)
    val_scores_lex = lexical_score(val_rows)

    train_scores_base = predict_scores(base_model, tokenizer, train_subset, args.max_length, args.batch_size)
    val_scores_base = predict_scores(base_model, tokenizer, val_rows, args.max_length, args.batch_size)

    train_scores_lora = predict_scores(lora_model, tokenizer, train_subset, args.max_length, args.batch_size)
    val_scores_lora = predict_scores(lora_model, tokenizer, val_rows, args.max_length, args.batch_size)

    t_lex, _ = best_threshold(y_train_subset, train_scores_lex)
    t_base, _ = best_threshold(y_train_subset, train_scores_base)
    t_lora, _ = best_threshold(y_train_subset, train_scores_lora)

    overall = {
        "lexical": metrics_at_threshold(y_val, val_scores_lex, t_lex),
        "pretrained": metrics_at_threshold(y_val, val_scores_base, t_base),
        "lora": metrics_at_threshold(y_val, val_scores_lora, t_lora),
    }

    per_clause = {
        "lexical": per_clause_metrics(val_rows, val_scores_lex, t_lex),
        "pretrained": per_clause_metrics(val_rows, val_scores_base, t_base),
        "lora": per_clause_metrics(val_rows, val_scores_lora, t_lora),
    }

    macro = {
        "lexical": macro_from_per_clause(per_clause["lexical"]),
        "pretrained": macro_from_per_clause(per_clause["pretrained"]),
        "lora": macro_from_per_clause(per_clause["lora"]),
    }

    # Representative LoRA errors
    pred_lora = (val_scores_lora >= t_lora).astype(np.int64)
    errors: list[dict[str, Any]] = []
    for i, row in enumerate(val_rows):
        true_y = int(row["label"])
        pred_y = int(pred_lora[i])
        if true_y == pred_y:
            continue
        errors.append(
            {
                "example_id": str(row["example_id"]),
                "doc_id": str(row["doc_id"]),
                "chunk_id": str(row["chunk_id"]),
                "clause_type": str(row["clause_type"]),
                "true": true_y,
                "pred": pred_y,
                "score": float(val_scores_lora[i]),
                "text_preview": str(row["text_b"])[:180].replace("\n", " "),
            }
        )
        if len(errors) >= args.error_examples:
            break

    lines: list[str] = []
    lines.append("# Clause-Conditioned Binary LoRA Report")
    lines.append("")
    lines.append("## Setup")
    lines.append(f"- Train file: `{args.train_file}`")
    lines.append(f"- Val file: `{args.val_file}`")
    lines.append(f"- Base model: `{args.base_model}`")
    lines.append(f"- LoRA adapter: `{args.adapter}`")
    lines.append(f"- Threshold tuning rows (train): {len(train_subset)}")
    lines.append("")
    lines.append("## Overall Metrics (val)")
    lines.append("")
    lines.append("| Method | PR-AUC | ROC-AUC | F1 | Precision | Recall | Threshold |")
    lines.append("| --- | ---: | ---: | ---: | ---: | ---: | ---: |")
    for method in ["lexical", "pretrained", "lora"]:
        m = overall[method]
        lines.append(
            f"| {method} | {m['pr_auc']:.4f} | {m['roc_auc']:.4f} | {m['f1']:.4f} | {m['precision']:.4f} | {m['recall']:.4f} | {m['threshold']:.4f} |"
        )

    lines.append("")
    lines.append("## Macro Averages Over Clause Types (positive class)")
    lines.append("")
    lines.append("| Method | Macro PR-AUC | Macro ROC-AUC | Macro F1 | Macro Precision | Macro Recall |")
    lines.append("| --- | ---: | ---: | ---: | ---: | ---: |")
    for method in ["lexical", "pretrained", "lora"]:
        m = macro[method]
        lines.append(
            f"| {method} | {m['macro_pr_auc']:.4f} | {m['macro_roc_auc']:.4f} | {m['macro_f1']:.4f} | {m['macro_precision']:.4f} | {m['macro_recall']:.4f} |"
        )

    lines.append("")
    lines.append("## Per-Clause Positive-Class Metrics (LoRA)")
    lines.append("")
    lines.append("| Clause | Positives | Precision | Recall | F1 | PR-AUC | ROC-AUC |")
    lines.append("| --- | ---: | ---: | ---: | ---: | ---: | ---: |")
    for clause in sorted(per_clause["lora"]):
        c = per_clause["lora"][clause]
        lines.append(
            f"| {clause} | {c['positives']} | {c['precision']:.4f} | {c['recall']:.4f} | {c['f1']:.4f} | {c['pr_auc']:.4f} | {c['roc_auc']:.4f} |"
        )

    lines.append("")
    lines.append("## Representative LoRA Errors")
    lines.append("")
    if not errors:
        lines.append("No errors found.")
    else:
        for i, err in enumerate(errors, start=1):
            lines.append(f"### Error {i}: `{err['example_id']}`")
            lines.append(f"- Clause: `{err['clause_type']}`")
            lines.append(f"- True: `{err['true']}` Pred: `{err['pred']}` Score: {err['score']:.4f}")
            lines.append(f"- Doc: `{err['doc_id']}` Chunk: `{err['chunk_id']}`")
            lines.append(f"- Preview: \"{err['text_preview']}\"")
            lines.append("")

    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    summary = {
        "overall": overall,
        "macro": macro,
        "report": str(args.report),
    }
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
