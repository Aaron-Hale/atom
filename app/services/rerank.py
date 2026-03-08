"""Cross-encoder reranking service for retrieved chunk candidates."""

from __future__ import annotations

from typing import Any

import numpy as np
from sentence_transformers import CrossEncoder


class BaseReranker:
    """Rerank vector candidates with a cross-encoder relevance model."""

    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L6-v2") -> None:
        self.model_name = model_name
        self._model = self._load_model(model_name)

    @staticmethod
    def _load_model(model_name: str) -> CrossEncoder:
        try:
            return CrossEncoder(model_name, local_files_only=True)
        except OSError:
            # Local-first: fall back to remote fetch only if cache miss.
            return CrossEncoder(model_name, local_files_only=False)
        except TypeError:
            # Backward compatibility with older sentence-transformers variants.
            try:
                return CrossEncoder(model_name, automodel_args={"local_files_only": True})
            except OSError:
                return CrossEncoder(model_name, automodel_args={"local_files_only": False})

    @staticmethod
    def _to_candidates(
        candidates: list[dict[str, Any]],
        scores: np.ndarray | list[float] | tuple[float, ...],
        *,
        sort_desc: bool = True,
    ) -> list[dict[str, Any]]:
        rescored: list[dict[str, Any]] = []
        for candidate, score in zip(candidates, scores):
            rescored.append(
                {
                    "doc_id": candidate["doc_id"],
                    "chunk_id": candidate["chunk_id"],
                    "score": float(score),
                    "start": candidate["start"],
                    "end": candidate["end"],
                    "text": candidate["text"],
                }
            )
        if sort_desc:
            rescored.sort(key=lambda item: item["score"], reverse=True)
        return rescored

    def rerank(
        self,
        query: str,
        candidates: list[dict[str, Any]],
        top_k: int | None = None,
    ) -> list[dict[str, Any]]:
        if not candidates:
            return []

        pairs = [(query, str(candidate["text"])) for candidate in candidates]
        scores = self._model.predict(pairs)
        rescored = self._to_candidates(candidates, scores)
        if top_k is None:
            return rescored
        return rescored[:top_k]

    def rerank_batch(
        self,
        queries: list[str],
        candidate_lists: list[list[dict[str, Any]]],
        top_k: int | None = None,
        batch_size: int = 64,
    ) -> list[list[dict[str, Any]]]:
        if len(queries) != len(candidate_lists):
            raise ValueError("queries and candidate_lists must have the same length")

        pair_counts = [len(candidates) for candidates in candidate_lists]
        if not any(pair_counts):
            return [[] for _ in queries]

        pairs: list[tuple[str, str]] = []
        flat_candidates: list[dict[str, Any]] = []
        for query, candidates in zip(queries, candidate_lists):
            for candidate in candidates:
                pairs.append((query, str(candidate["text"])))
                flat_candidates.append(candidate)

        scores = self._model.predict(
            pairs,
            batch_size=batch_size,
            show_progress_bar=False,
        )

        flat_rescored = self._to_candidates(flat_candidates, scores, sort_desc=False)

        reranked_lists: list[list[dict[str, Any]]] = []
        start = 0
        for count in pair_counts:
            subset = flat_rescored[start : start + count]
            subset.sort(key=lambda item: item["score"], reverse=True)
            if top_k is not None:
                subset = subset[:top_k]
            reranked_lists.append(subset)
            start += count

        return reranked_lists


class LoraReranker:
    """Rerank vector candidates with a LoRA-adapted cross-encoder."""

    def __init__(
        self,
        model_name: str = "cross-encoder/ms-marco-MiniLM-L6-v2",
        adapter_path: str = "models/reranker_lora",
    ) -> None:
        self.model_name = model_name
        self.adapter_path = adapter_path
        self._tokenizer, self._model = self._load_model(model_name=model_name, adapter_path=adapter_path)

    @staticmethod
    def _load_model(model_name: str, adapter_path: str):
        import torch
        from peft import PeftModel
        from transformers import AutoModelForSequenceClassification, AutoTokenizer

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        try:
            tokenizer = AutoTokenizer.from_pretrained(adapter_path, local_files_only=True)
        except OSError:
            tokenizer = AutoTokenizer.from_pretrained(model_name, local_files_only=True)

        try:
            base_model = AutoModelForSequenceClassification.from_pretrained(
                model_name,
                local_files_only=True,
            )
        except OSError:
            base_model = AutoModelForSequenceClassification.from_pretrained(
                model_name,
                local_files_only=False,
            )

        try:
            model = PeftModel.from_pretrained(base_model, adapter_path, local_files_only=True)
        except OSError:
            model = PeftModel.from_pretrained(base_model, adapter_path, local_files_only=False)
        model = model.to(device)
        model.eval()
        return tokenizer, model

    def _predict(
        self,
        pairs: list[tuple[str, str]],
        batch_size: int = 32,
    ) -> np.ndarray:
        import torch

        if not pairs:
            return np.asarray([], dtype=np.float32)

        device = next(self._model.parameters()).device
        scores: list[np.ndarray] = []
        with torch.no_grad():
            for start in range(0, len(pairs), batch_size):
                batch = pairs[start : start + batch_size]
                encoded = self._tokenizer(
                    [item[0] for item in batch],
                    [item[1] for item in batch],
                    padding=True,
                    truncation=True,
                    max_length=512,
                    return_tensors="pt",
                )
                encoded = {key: value.to(device) for key, value in encoded.items()}
                logits = self._model(**encoded).logits.view(-1)
                scores.append(logits.detach().cpu().numpy())
        return np.concatenate(scores).astype(np.float32)

    def rerank(
        self,
        query: str,
        candidates: list[dict[str, Any]],
        top_k: int | None = None,
    ) -> list[dict[str, Any]]:
        if not candidates:
            return []
        pairs = [(query, str(candidate["text"])) for candidate in candidates]
        scores = self._predict(pairs)
        rescored = BaseReranker._to_candidates(candidates, scores)
        if top_k is None:
            return rescored
        return rescored[:top_k]

    def rerank_batch(
        self,
        queries: list[str],
        candidate_lists: list[list[dict[str, Any]]],
        top_k: int | None = None,
        batch_size: int = 64,
    ) -> list[list[dict[str, Any]]]:
        if len(queries) != len(candidate_lists):
            raise ValueError("queries and candidate_lists must have the same length")

        pair_counts = [len(candidates) for candidates in candidate_lists]
        if not any(pair_counts):
            return [[] for _ in queries]

        pairs: list[tuple[str, str]] = []
        flat_candidates: list[dict[str, Any]] = []
        for query, candidates in zip(queries, candidate_lists):
            for candidate in candidates:
                pairs.append((query, str(candidate["text"])))
                flat_candidates.append(candidate)

        scores = self._predict(pairs, batch_size=batch_size)
        flat_rescored = BaseReranker._to_candidates(flat_candidates, scores, sort_desc=False)

        reranked_lists: list[list[dict[str, Any]]] = []
        start = 0
        for count in pair_counts:
            subset = flat_rescored[start : start + count]
            subset.sort(key=lambda item: item["score"], reverse=True)
            if top_k is not None:
                subset = subset[:top_k]
            reranked_lists.append(subset)
            start += count

        return reranked_lists
