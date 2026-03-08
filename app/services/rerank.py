"""Cross-encoder reranking service for retrieved chunk candidates."""

from __future__ import annotations

from typing import Any

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

        rescored.sort(key=lambda item: item["score"], reverse=True)
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

        flat_rescored: list[dict[str, Any]] = []
        for candidate, score in zip(flat_candidates, scores):
            flat_rescored.append(
                {
                    "doc_id": candidate["doc_id"],
                    "chunk_id": candidate["chunk_id"],
                    "score": float(score),
                    "start": candidate["start"],
                    "end": candidate["end"],
                    "text": candidate["text"],
                }
            )

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
