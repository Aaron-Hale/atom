"""FAISS-backed retrieval service for chunk candidates."""

from __future__ import annotations

import json
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


class RetrievalService:
    def __init__(
        self,
        index_path: Path | str = "data/faiss.index",
        metadata_path: Path | str = "data/chunk_metadata.jsonl",
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
    ) -> None:
        self.index_path = Path(index_path)
        self.metadata_path = Path(metadata_path)
        self.model_name = model_name

        self._index = faiss.read_index(str(self.index_path))
        self._metadata = self._load_metadata(self.metadata_path)
        self._model = SentenceTransformer(self.model_name, local_files_only=True)

        if self._index.ntotal != len(self._metadata):
            raise ValueError(
                f"Index vectors ({self._index.ntotal}) != metadata rows ({len(self._metadata)})"
            )

    @staticmethod
    def _load_metadata(path: Path) -> list[dict[str, object]]:
        rows: list[dict[str, object]] = []
        with path.open("r", encoding="utf-8") as infile:
            for line in infile:
                line = line.strip()
                if not line:
                    continue
                rows.append(json.loads(line))
        return rows

    def retrieve(self, query: str, top_k: int = 5) -> list[dict[str, object]]:
        if top_k <= 0:
            return []

        query_vec = self._model.encode(
            [query],
            convert_to_numpy=True,
            normalize_embeddings=True,
        )
        query_vec = np.asarray(query_vec, dtype=np.float32)

        scores, indices = self._index.search(query_vec, top_k)

        results: list[dict[str, object]] = []
        for idx, score in zip(indices[0], scores[0]):
            if idx < 0:
                continue
            row = self._metadata[int(idx)]
            results.append(
                {
                    "doc_id": row["doc_id"],
                    "chunk_id": row["chunk_id"],
                    "score": float(score),
                    "start": row["start"],
                    "end": row["end"],
                    "text": row["text"],
                }
            )
        return results


def retrieve(
    query: str,
    top_k: int = 5,
    index_path: Path | str = "data/faiss.index",
    metadata_path: Path | str = "data/chunk_metadata.jsonl",
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
) -> list[dict[str, object]]:
    service = RetrievalService(
        index_path=index_path,
        metadata_path=metadata_path,
        model_name=model_name,
    )
    return service.retrieve(query=query, top_k=top_k)
