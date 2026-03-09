#!/usr/bin/env python3
"""Local demo inference for clause-conditioned binary LoRA detector."""

from __future__ import annotations

import argparse
from pathlib import Path

import torch
from peft import PeftConfig, PeftModel
from safetensors.torch import load_file
from transformers import AutoModelForSequenceClassification, AutoTokenizer


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--adapter-path",
        type=Path,
        default=Path("models/clause_binary_lora"),
        help="Path to saved LoRA adapter directory.",
    )
    parser.add_argument("--clause-type", required=True, help="Clause type label (for example: assignment).")

    text_group = parser.add_mutually_exclusive_group(required=True)
    text_group.add_argument("--text", help="Direct clause text input.")
    text_group.add_argument("--text-file", type=Path, help="Path to a UTF-8 text file containing clause text.")

    parser.add_argument("--max-length", type=int, default=256, help="Tokenizer max sequence length.")
    parser.add_argument("--threshold", type=float, default=0.5, help="Probability threshold for yes/no label.")
    parser.add_argument(
        "--allow-remote-download",
        action="store_true",
        help="Allow downloading missing model/tokenizer files if not available locally.",
    )
    return parser.parse_args()


def read_text(args: argparse.Namespace) -> str:
    if args.text is not None:
        return args.text.strip()

    text_path = args.text_file
    if text_path is None:
        raise ValueError("Either --text or --text-file must be provided.")

    text = text_path.read_text(encoding="utf-8").strip()
    if not text:
        raise ValueError(f"Text file is empty: {text_path}")
    return text


def load_tokenizer(adapter_path: Path, base_model: str, allow_remote_download: bool):
    try:
        return AutoTokenizer.from_pretrained(str(adapter_path), local_files_only=True)
    except OSError:
        try:
            return AutoTokenizer.from_pretrained(base_model, local_files_only=True)
        except OSError:
            if not allow_remote_download:
                raise
            return AutoTokenizer.from_pretrained(base_model, local_files_only=False)


def infer_num_labels_from_adapter(adapter_path: Path) -> int:
    weights_path = adapter_path / "adapter_model.safetensors"
    if not weights_path.exists():
        return 2

    state = load_file(str(weights_path))
    classifier_weight = state.get("base_model.model.classifier.weight")
    if classifier_weight is None:
        for key, value in state.items():
            if key.endswith("classifier.weight"):
                classifier_weight = value
                break
    if classifier_weight is None or classifier_weight.ndim != 2:
        return 2
    return int(classifier_weight.shape[0])


def load_base_model(base_model: str, num_labels: int, allow_remote_download: bool):
    try:
        model = AutoModelForSequenceClassification.from_pretrained(base_model, local_files_only=True)
    except OSError:
        if not allow_remote_download:
            raise
        model = AutoModelForSequenceClassification.from_pretrained(base_model, local_files_only=False)

    if model.config.num_labels != num_labels:
        if not hasattr(model.classifier, "in_features"):
            raise ValueError("Loaded base model classifier does not expose in_features for resizing.")
        in_features = int(model.classifier.in_features)
        use_bias = model.classifier.bias is not None
        resized = torch.nn.Linear(in_features, num_labels, bias=use_bias)
        resized = resized.to(dtype=model.classifier.weight.dtype)
        model.classifier = resized
        model.num_labels = num_labels
        model.config.num_labels = num_labels
        model.config.id2label = {i: f"LABEL_{i}" for i in range(num_labels)}
        model.config.label2id = {v: k for k, v in model.config.id2label.items()}
    return model


def main() -> None:
    args = parse_args()
    adapter_path = args.adapter_path

    if not adapter_path.exists():
        raise FileNotFoundError(f"Adapter path does not exist: {adapter_path}")

    input_text = read_text(args)

    peft_config = PeftConfig.from_pretrained(str(adapter_path))
    base_model_name = str(peft_config.base_model_name_or_path)
    num_labels = infer_num_labels_from_adapter(adapter_path)

    tokenizer = load_tokenizer(adapter_path, base_model_name, args.allow_remote_download)
    base_model = load_base_model(base_model_name, num_labels, args.allow_remote_download)
    model = PeftModel.from_pretrained(base_model, str(adapter_path), local_files_only=not args.allow_remote_download)
    model = model.to("cpu")
    model.eval()

    text_a = f"Clause type: {args.clause_type}. Does this chunk contain evidence for this clause?"
    encoded = tokenizer(text_a, input_text, truncation=True, max_length=args.max_length, return_tensors="pt")

    with torch.no_grad():
        logits = model(**encoded).logits
        if logits.shape[-1] == 1:
            probability = float(torch.sigmoid(logits.squeeze(-1)).item())
        else:
            probability = float(torch.softmax(logits, dim=-1)[0, 1].item())

    predicted_label = "yes" if probability >= args.threshold else "no"

    print(f"predicted_probability: {probability:.6f}")
    print(f"predicted_label: {predicted_label}")
    print(f"model_path: {adapter_path}")
    print(f"clause_type: {args.clause_type}")


if __name__ == "__main__":
    main()
