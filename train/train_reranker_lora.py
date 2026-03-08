#!/usr/bin/env python3
"""Train a LoRA adapter for the ATOM cross-encoder reranker."""

from __future__ import annotations

import argparse
import json
import random
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
import torch
from datasets import Dataset
from peft import LoraConfig, TaskType, get_peft_model
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    DataCollatorWithPadding,
    Trainer,
    TrainingArguments,
)


class BCETrainer(Trainer):
    """Trainer with BCE-with-logits loss for a single-logit reranker head."""

    def compute_loss(self, model, inputs, return_outputs=False, **kwargs):  # type: ignore[override]
        labels = inputs.pop("labels").float()
        outputs = model(**inputs)
        logits = outputs.logits.view(-1)
        loss = torch.nn.functional.binary_cross_entropy_with_logits(logits, labels)
        if return_outputs:
            return loss, outputs
        return loss


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train-file", type=Path, default=Path("data/rerank_train.jsonl"))
    parser.add_argument("--val-file", type=Path, default=Path("data/rerank_val.jsonl"))
    parser.add_argument("--base-model", default="cross-encoder/ms-marco-MiniLM-L6-v2")
    parser.add_argument("--output-dir", type=Path, default=Path("models/reranker_lora"))
    parser.add_argument("--max-length", type=int, default=512)
    parser.add_argument("--learning-rate", type=float, default=2e-4)
    parser.add_argument("--weight-decay", type=float, default=0.01)
    parser.add_argument("--num-train-epochs", type=float, default=1.0)
    parser.add_argument("--per-device-train-batch-size", type=int, default=16)
    parser.add_argument("--per-device-eval-batch-size", type=int, default=32)
    parser.add_argument("--gradient-accumulation-steps", type=int, default=1)
    parser.add_argument("--warmup-ratio", type=float, default=0.05)
    parser.add_argument("--logging-steps", type=int, default=25)
    parser.add_argument("--eval-strategy", choices=("epoch", "steps"), default="epoch")
    parser.add_argument("--eval-steps", type=int, default=100)
    parser.add_argument("--save-strategy", choices=("epoch", "steps"), default="epoch")
    parser.add_argument("--save-steps", type=int, default=100)
    parser.add_argument("--save-total-limit", type=int, default=2)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--lora-r", type=int, default=16)
    parser.add_argument("--lora-alpha", type=int, default=32)
    parser.add_argument("--lora-dropout", type=float, default=0.1)
    parser.add_argument("--lora-target-modules", default="query,value")
    parser.add_argument("--lora-modules-to-save", default="classifier")
    parser.add_argument("--metric-threshold", type=float, default=0.5)
    parser.add_argument("--max-train-samples", type=int, default=None)
    parser.add_argument("--max-val-samples", type=int, default=None)
    parser.add_argument("--smoke-run", action="store_true")
    parser.add_argument("--smoke-train-samples", type=int, default=256)
    parser.add_argument("--smoke-val-samples", type=int, default=128)
    parser.add_argument(
        "--allow-remote-download",
        action="store_true",
        help="If set, allow Hugging Face download when local cache misses.",
    )
    return parser.parse_args()


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as infile:
        for line in infile:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def as_dataset(rows: list[dict[str, Any]]) -> Dataset:
    normalized = [
        {
            "query": str(row["query"]),
            "text": str(row["text"]),
            "labels": float(row["label"]),
        }
        for row in rows
    ]
    return Dataset.from_list(normalized)


def load_tokenizer(model_name: str, allow_remote_download: bool):
    try:
        return AutoTokenizer.from_pretrained(model_name, local_files_only=True)
    except OSError:
        if not allow_remote_download:
            raise
        return AutoTokenizer.from_pretrained(model_name, local_files_only=False)


def load_model(model_name: str, allow_remote_download: bool):
    try:
        return AutoModelForSequenceClassification.from_pretrained(
            model_name,
            local_files_only=True,
        )
    except OSError:
        if not allow_remote_download:
            raise
        return AutoModelForSequenceClassification.from_pretrained(
            model_name,
            local_files_only=False,
        )


def compute_metrics_builder(threshold: float):
    def compute_metrics(eval_pred):
        logits, labels = eval_pred
        logits = np.asarray(logits).reshape(-1)
        labels = np.asarray(labels).reshape(-1)
        probs = 1.0 / (1.0 + np.exp(-logits))
        preds = (probs >= threshold).astype(np.int64)
        return {
            "accuracy": float(accuracy_score(labels, preds)),
            "precision": float(precision_score(labels, preds, zero_division=0)),
            "recall": float(recall_score(labels, preds, zero_division=0)),
            "f1": float(f1_score(labels, preds, zero_division=0)),
        }

    return compute_metrics


def main() -> None:
    args = parse_args()
    set_seed(args.seed)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    train_rows = load_jsonl(args.train_file)
    val_rows = load_jsonl(args.val_file)

    if args.smoke_run:
        train_rows = train_rows[: min(args.smoke_train_samples, len(train_rows))]
        val_rows = val_rows[: min(args.smoke_val_samples, len(val_rows))]
    else:
        if args.max_train_samples is not None:
            train_rows = train_rows[: min(args.max_train_samples, len(train_rows))]
        if args.max_val_samples is not None:
            val_rows = val_rows[: min(args.max_val_samples, len(val_rows))]

    tokenizer = load_tokenizer(args.base_model, args.allow_remote_download)
    model = load_model(args.base_model, args.allow_remote_download)

    target_modules = [item.strip() for item in args.lora_target_modules.split(",") if item.strip()]
    modules_to_save = [item.strip() for item in args.lora_modules_to_save.split(",") if item.strip()]

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
        return tokenizer(
            examples["query"],
            examples["text"],
            truncation=True,
            max_length=args.max_length,
        )

    train_dataset = train_dataset.map(preprocess, batched=True, desc="Tokenizing train")
    val_dataset = val_dataset.map(preprocess, batched=True, desc="Tokenizing val")

    data_collator = DataCollatorWithPadding(tokenizer=tokenizer)
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
        eval_strategy=args.eval_strategy,
        eval_steps=args.eval_steps if args.eval_strategy == "steps" else None,
        save_strategy=args.save_strategy,
        save_steps=args.save_steps if args.save_strategy == "steps" else None,
        save_total_limit=args.save_total_limit,
        load_best_model_at_end=True,
        metric_for_best_model="f1",
        greater_is_better=True,
        seed=args.seed,
        remove_unused_columns=True,
        report_to="none",
    )

    trainer = BCETrainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        processing_class=tokenizer,
        data_collator=data_collator,
        compute_metrics=compute_metrics_builder(args.metric_threshold),
    )

    train_result = trainer.train()
    eval_metrics = trainer.evaluate()

    trainer.save_model(str(args.output_dir))
    tokenizer.save_pretrained(str(args.output_dir))
    trainer.save_state()

    run_summary = {
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "base_model": args.base_model,
        "train_file": str(args.train_file),
        "val_file": str(args.val_file),
        "train_samples": len(train_rows),
        "val_samples": len(val_rows),
        "seed": args.seed,
        "smoke_run": bool(args.smoke_run),
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
            "metric_threshold": args.metric_threshold,
        },
        "train_metrics": train_result.metrics,
        "eval_metrics": eval_metrics,
    }
    with (args.output_dir / "run_summary.json").open("w", encoding="utf-8") as outfile:
        json.dump(run_summary, outfile, indent=2, sort_keys=True)
        outfile.write("\n")

    print(json.dumps(run_summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
