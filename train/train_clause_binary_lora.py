#!/usr/bin/env python3
"""Train clause-conditioned binary chunk detector with LoRA."""

from __future__ import annotations

import argparse
import json
import random
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
import torch
from datasets import Dataset
from peft import LoraConfig, TaskType, get_peft_model
from sklearn.metrics import average_precision_score, f1_score, precision_score, recall_score, roc_auc_score
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    DataCollatorWithPadding,
    Trainer,
    TrainingArguments,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train-file", type=Path, default=Path("data/clause_binary_train.jsonl"))
    parser.add_argument("--val-file", type=Path, default=Path("data/clause_binary_val.jsonl"))
    parser.add_argument("--base-model", default="cross-encoder/ms-marco-MiniLM-L6-v2")
    parser.add_argument("--output-dir", type=Path, default=Path("models/clause_binary_lora"))
    parser.add_argument("--max-length", type=int, default=256)
    parser.add_argument("--learning-rate", type=float, default=2e-4)
    parser.add_argument("--weight-decay", type=float, default=0.01)
    parser.add_argument("--num-train-epochs", type=float, default=1.0)
    parser.add_argument("--per-device-train-batch-size", type=int, default=32)
    parser.add_argument("--per-device-eval-batch-size", type=int, default=64)
    parser.add_argument("--gradient-accumulation-steps", type=int, default=1)
    parser.add_argument("--warmup-ratio", type=float, default=0.05)
    parser.add_argument("--logging-steps", type=int, default=25)
    parser.add_argument("--save-total-limit", type=int, default=2)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--lora-r", type=int, default=16)
    parser.add_argument("--lora-alpha", type=int, default=32)
    parser.add_argument("--lora-dropout", type=float, default=0.1)
    parser.add_argument("--lora-target-modules", default="query,value")
    parser.add_argument("--lora-modules-to-save", default="classifier")
    parser.add_argument("--allow-remote-download", action="store_true")
    return parser.parse_args()


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as infile:
        for line in infile:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def as_dataset(rows: list[dict[str, Any]]) -> Dataset:
    return Dataset.from_list(
        [
            {
                "text_a": str(r["text_a"]),
                "text_b": str(r["text_b"]),
                "labels": int(r["label"]),
            }
            for r in rows
        ]
    )


def load_tokenizer(model_name: str, allow_remote_download: bool):
    try:
        return AutoTokenizer.from_pretrained(model_name, local_files_only=True)
    except OSError:
        if not allow_remote_download:
            raise
        return AutoTokenizer.from_pretrained(model_name, local_files_only=False)


def load_model(model_name: str, allow_remote_download: bool):
    kwargs = {"num_labels": 2, "ignore_mismatched_sizes": True}
    try:
        return AutoModelForSequenceClassification.from_pretrained(model_name, local_files_only=True, **kwargs)
    except OSError:
        if not allow_remote_download:
            raise
        return AutoModelForSequenceClassification.from_pretrained(model_name, local_files_only=False, **kwargs)


def best_f1_threshold(y_true: np.ndarray, scores: np.ndarray) -> tuple[float, float]:
    unique = np.unique(scores)
    if unique.size > 200:
        qs = np.linspace(0.01, 0.99, 200)
        candidates = np.unique(np.quantile(scores, qs))
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


def compute_metrics(eval_pred):
    logits, labels = eval_pred
    labels = np.asarray(labels).reshape(-1)
    logits = np.asarray(logits)
    probs = torch.softmax(torch.tensor(logits), dim=-1).numpy()[:, 1]

    pr_auc = float(average_precision_score(labels, probs)) if len(np.unique(labels)) > 1 else 0.0
    roc_auc = float(roc_auc_score(labels, probs)) if len(np.unique(labels)) > 1 else 0.0
    t, _ = best_f1_threshold(labels, probs)
    pred = (probs >= t).astype(np.int64)

    return {
        "threshold": float(t),
        "pr_auc": pr_auc,
        "roc_auc": roc_auc,
        "f1": float(f1_score(labels, pred, zero_division=0)),
        "precision": float(precision_score(labels, pred, zero_division=0)),
        "recall": float(recall_score(labels, pred, zero_division=0)),
    }


def main() -> None:
    args = parse_args()
    set_seed(args.seed)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    train_rows = load_jsonl(args.train_file)
    val_rows = load_jsonl(args.val_file)
    if not train_rows or not val_rows:
        raise ValueError("Train/val datasets must be non-empty")

    tokenizer = load_tokenizer(args.base_model, args.allow_remote_download)
    model = load_model(args.base_model, args.allow_remote_download)

    target_modules = [m.strip() for m in args.lora_target_modules.split(",") if m.strip()]
    modules_to_save = [m.strip() for m in args.lora_modules_to_save.split(",") if m.strip()]

    lora_config = LoraConfig(
        task_type=TaskType.SEQ_CLS,
        r=args.lora_r,
        lora_alpha=args.lora_alpha,
        lora_dropout=args.lora_dropout,
        target_modules=target_modules,
        modules_to_save=modules_to_save or None,
        bias="none",
    )
    model = get_peft_model(model, lora_config)

    train_dataset = as_dataset(train_rows)
    val_dataset = as_dataset(val_rows)

    def preprocess(examples: dict[str, list[str]]) -> dict[str, Any]:
        return tokenizer(examples["text_a"], examples["text_b"], truncation=True, max_length=args.max_length)

    train_dataset = train_dataset.map(preprocess, batched=True, desc="Tokenizing train")
    val_dataset = val_dataset.map(preprocess, batched=True, desc="Tokenizing val")

    train_counts = Counter(int(r["label"]) for r in train_rows)
    val_counts = Counter(int(r["label"]) for r in val_rows)

    training_args = TrainingArguments(
        output_dir=str(args.output_dir),
        learning_rate=args.learning_rate,
        weight_decay=args.weight_decay,
        num_train_epochs=args.num_train_epochs,
        per_device_train_batch_size=args.per_device_train_batch_size,
        per_device_eval_batch_size=args.per_device_eval_batch_size,
        gradient_accumulation_steps=args.gradient_accumulation_steps,
        warmup_ratio=args.warmup_ratio,
        logging_steps=args.logging_steps,
        eval_strategy="epoch",
        save_strategy="epoch",
        save_total_limit=args.save_total_limit,
        load_best_model_at_end=True,
        metric_for_best_model="pr_auc",
        greater_is_better=True,
        seed=args.seed,
        report_to="none",
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        processing_class=tokenizer,
        data_collator=DataCollatorWithPadding(tokenizer=tokenizer),
        compute_metrics=compute_metrics,
    )

    train_result = trainer.train()
    eval_metrics = trainer.evaluate()

    trainer.save_model(str(args.output_dir))
    tokenizer.save_pretrained(str(args.output_dir))
    trainer.save_state()

    summary = {
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "base_model": args.base_model,
        "train_file": str(args.train_file),
        "val_file": str(args.val_file),
        "seed": args.seed,
        "train_samples": len(train_rows),
        "val_samples": len(val_rows),
        "train_label_counts": dict(sorted(train_counts.items())),
        "val_label_counts": dict(sorted(val_counts.items())),
        "lora": {
            "r": args.lora_r,
            "alpha": args.lora_alpha,
            "dropout": args.lora_dropout,
            "target_modules": target_modules,
            "modules_to_save": modules_to_save,
        },
        "training": {
            "max_length": args.max_length,
            "learning_rate": args.learning_rate,
            "weight_decay": args.weight_decay,
            "num_train_epochs": args.num_train_epochs,
            "per_device_train_batch_size": args.per_device_train_batch_size,
            "per_device_eval_batch_size": args.per_device_eval_batch_size,
            "gradient_accumulation_steps": args.gradient_accumulation_steps,
            "warmup_ratio": args.warmup_ratio,
        },
        "train_metrics": train_result.metrics,
        "eval_metrics": eval_metrics,
    }

    with (args.output_dir / "run_summary.json").open("w", encoding="utf-8") as out:
        json.dump(summary, out, indent=2, sort_keys=True)
        out.write("\n")

    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
