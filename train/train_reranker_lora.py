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
from peft import LoraConfig, PeftModel, TaskType, get_peft_model
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


class PairwiseTrainer(Trainer):
    """Trainer with margin ranking loss over (query, positive, negative) triplets."""

    def __init__(self, *args, pairwise_margin: float = 0.2, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.pairwise_margin = pairwise_margin

    def compute_loss(self, model, inputs, return_outputs=False, **kwargs):  # type: ignore[override]
        labels = inputs.pop("labels").float()
        pos_inputs = {
            "input_ids": inputs.pop("pos_input_ids"),
            "attention_mask": inputs.pop("pos_attention_mask"),
        }
        neg_inputs = {
            "input_ids": inputs.pop("neg_input_ids"),
            "attention_mask": inputs.pop("neg_attention_mask"),
        }
        pos_logits = model(**pos_inputs).logits.view(-1)
        neg_logits = model(**neg_inputs).logits.view(-1)
        loss = torch.nn.functional.margin_ranking_loss(
            pos_logits,
            neg_logits,
            labels,
            margin=self.pairwise_margin,
        )
        if return_outputs:
            return loss, {"logits": (pos_logits - neg_logits).unsqueeze(-1)}
        return loss


class PairwiseDataCollator:
    """Collate pairwise triplets into padded positive/negative model inputs."""

    def __init__(self, tokenizer: Any, max_length: int) -> None:
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __call__(self, features: list[dict[str, Any]]) -> dict[str, torch.Tensor]:
        queries = [str(feature["query"]) for feature in features]
        positives = [str(feature["pos_text"]) for feature in features]
        negatives = [str(feature["neg_text"]) for feature in features]
        labels = torch.ones(len(features), dtype=torch.float32)

        pos_encoded = self.tokenizer(
            queries,
            positives,
            truncation=True,
            max_length=self.max_length,
            padding=True,
            return_tensors="pt",
        )
        neg_encoded = self.tokenizer(
            queries,
            negatives,
            truncation=True,
            max_length=self.max_length,
            padding=True,
            return_tensors="pt",
        )

        return {
            "pos_input_ids": pos_encoded["input_ids"],
            "pos_attention_mask": pos_encoded["attention_mask"],
            "neg_input_ids": neg_encoded["input_ids"],
            "neg_attention_mask": neg_encoded["attention_mask"],
            "labels": labels,
        }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train-file", type=Path, default=Path("data/rerank_train_pairwise_v3.jsonl"))
    parser.add_argument("--val-file", type=Path, default=Path("data/rerank_val_pairwise_v3.jsonl"))
    parser.add_argument("--base-model", default="cross-encoder/ms-marco-MiniLM-L6-v2")
    parser.add_argument("--output-dir", type=Path, default=Path("models/reranker_lora_v3"))
    parser.add_argument("--train-objective", choices=("pointwise", "pairwise"), default="pairwise")
    parser.add_argument("--pairwise-margin", type=float, default=0.2)
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
    parser.add_argument("--save-load-parity-check", action="store_true")
    parser.add_argument("--parity-slice-size", type=int, default=64)
    parser.add_argument("--parity-batch-size", type=int, default=32)
    parser.add_argument("--parity-atol", type=float, default=1e-5)
    parser.add_argument("--parity-rtol", type=float, default=1e-4)
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
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False


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


def as_pairwise_dataset(rows: list[dict[str, Any]]) -> Dataset:
    normalized = [
        {
            "query": str(row["query"]),
            "pos_text": str(row["pos_text"]),
            "neg_text": str(row["neg_text"]),
            "labels": 1.0,
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


def compute_pairwise_metrics(eval_pred):
    logits, _labels = eval_pred
    diffs = np.asarray(logits).reshape(-1)
    return {
        "pairwise_accuracy": float(np.mean(diffs > 0.0)) if diffs.size else 0.0,
    }


def score_rows(
    model: torch.nn.Module,
    tokenizer: Any,
    rows: list[dict[str, Any]],
    max_length: int,
    batch_size: int,
) -> np.ndarray:
    if not rows:
        return np.asarray([], dtype=np.float32)

    model.eval()
    device = next(model.parameters()).device
    all_logits: list[np.ndarray] = []

    with torch.no_grad():
        for start in range(0, len(rows), batch_size):
            batch = rows[start : start + batch_size]
            encoded = tokenizer(
                [str(row["query"]) for row in batch],
                [str(row["text"]) for row in batch],
                truncation=True,
                max_length=max_length,
                padding=True,
                return_tensors="pt",
            )
            encoded = {key: value.to(device) for key, value in encoded.items()}
            logits = model(**encoded).logits.view(-1)
            all_logits.append(logits.detach().cpu().numpy().astype(np.float32))

    return np.concatenate(all_logits, axis=0)


def load_adapter_model_for_parity(
    base_model: str,
    adapter_dir: Path,
    allow_remote_download: bool,
) -> torch.nn.Module:
    base = load_model(base_model, allow_remote_download)
    try:
        model = PeftModel.from_pretrained(base, str(adapter_dir), local_files_only=True)
    except OSError:
        if not allow_remote_download:
            raise
        model = PeftModel.from_pretrained(base, str(adapter_dir), local_files_only=False)
    return model


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

    if args.train_objective == "pointwise":
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
        data_collator: Any = DataCollatorWithPadding(tokenizer=tokenizer)
    else:
        train_dataset = as_pairwise_dataset(train_rows)
        val_dataset = as_pairwise_dataset(val_rows)
        data_collator = PairwiseDataCollator(tokenizer=tokenizer, max_length=args.max_length)

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
        metric_for_best_model="f1" if args.train_objective == "pointwise" else "pairwise_accuracy",
        greater_is_better=True,
        seed=args.seed,
        remove_unused_columns=False if args.train_objective == "pairwise" else True,
        report_to="none",
    )

    if args.train_objective == "pointwise":
        trainer: Trainer = BCETrainer(
            model=model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset,
            processing_class=tokenizer,
            data_collator=data_collator,
            compute_metrics=compute_metrics_builder(args.metric_threshold),
        )
    else:
        trainer = PairwiseTrainer(
            model=model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset,
            processing_class=tokenizer,
            data_collator=data_collator,
            compute_metrics=compute_pairwise_metrics,
            pairwise_margin=args.pairwise_margin,
        )

    train_result = trainer.train()
    eval_metrics = trainer.evaluate()

    trainer.save_model(str(args.output_dir))
    tokenizer.save_pretrained(str(args.output_dir))
    trainer.save_state()

    parity_summary: dict[str, Any] | None = None
    if args.save_load_parity_check:
        if args.train_objective == "pairwise":
            parity_rows = [
                {"query": row["query"], "text": row["pos_text"]}
                for row in val_rows[: min(args.parity_slice_size, len(val_rows))]
            ]
        else:
            parity_rows = val_rows[: min(args.parity_slice_size, len(val_rows))]
        if parity_rows:
            trainer.model = trainer.model.to("cpu")
            trained_logits = score_rows(
                model=trainer.model,
                tokenizer=tokenizer,
                rows=parity_rows,
                max_length=args.max_length,
                batch_size=args.parity_batch_size,
            )
            reloaded_model = load_adapter_model_for_parity(
                base_model=args.base_model,
                adapter_dir=args.output_dir,
                allow_remote_download=args.allow_remote_download,
            ).to("cpu")
            reloaded_logits = score_rows(
                model=reloaded_model,
                tokenizer=tokenizer,
                rows=parity_rows,
                max_length=args.max_length,
                batch_size=args.parity_batch_size,
            )
            abs_diff = np.abs(trained_logits - reloaded_logits)
            parity_summary = {
                "enabled": True,
                "slice_size": len(parity_rows),
                "batch_size": args.parity_batch_size,
                "atol": args.parity_atol,
                "rtol": args.parity_rtol,
                "max_abs_logit_diff": float(abs_diff.max()) if abs_diff.size else 0.0,
                "mean_abs_logit_diff": float(abs_diff.mean()) if abs_diff.size else 0.0,
                "p95_abs_logit_diff": float(np.percentile(abs_diff, 95)) if abs_diff.size else 0.0,
                "allclose": bool(
                    np.allclose(
                        trained_logits,
                        reloaded_logits,
                        atol=args.parity_atol,
                        rtol=args.parity_rtol,
                    )
                ),
            }
            print("LoRA save/load parity check:")
            print(
                f"  slice={len(parity_rows)} | max_abs={parity_summary['max_abs_logit_diff']:.8f} | "
                + f"mean_abs={parity_summary['mean_abs_logit_diff']:.8f} | "
                + f"p95_abs={parity_summary['p95_abs_logit_diff']:.8f} | "
                + f"allclose={parity_summary['allclose']}"
            )
        else:
            parity_summary = {
                "enabled": True,
                "slice_size": 0,
                "error": "No validation rows available for parity check.",
            }

    run_summary = {
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "base_model": args.base_model,
        "train_objective": args.train_objective,
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
            "pairwise_margin": args.pairwise_margin,
        },
        "train_metrics": train_result.metrics,
        "eval_metrics": eval_metrics,
    }
    if parity_summary is not None:
        run_summary["save_load_parity_check"] = parity_summary
    with (args.output_dir / "run_summary.json").open("w", encoding="utf-8") as outfile:
        json.dump(run_summary, outfile, indent=2, sort_keys=True)
        outfile.write("\n")

    print(json.dumps(run_summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
