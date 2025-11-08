"""
Embedding store implementations.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any, DefaultDict, Iterable, List, Sequence, Tuple


class InMemoryEmbeddingStore:
    """Simple in-memory embedding store for prototyping."""

    modality = "generic"

    def __init__(self, modality: str = "generic") -> None:
        self.modality = modality
        self._store: DefaultDict[str, List[Any]] = defaultdict(list)

    def add_embeddings(self, user_id: str, embeddings: Iterable[Any]) -> None:
        self._store[user_id].extend(list(embeddings))

    def delete_user(self, user_id: str) -> None:
        if user_id in self._store:
            del self._store[user_id]

    def query(self, embedding: Any, top_k: int = 5) -> Sequence[Tuple[str, float, dict[str, Any]]]:
        results: List[Tuple[str, float, dict[str, Any]]] = []
        for user_id, embeddings in self._store.items():
            score = max((self._score(embedding, stored) for stored in embeddings), default=0.0)
            metadata = {"num_samples": len(embeddings)}
            results.append((user_id, score, metadata))
        results.sort(key=lambda item: item[1], reverse=True)
        return results[:top_k]

    def list_users(self) -> Sequence[str]:
        return tuple(sorted(self._store.keys()))

    def _score(self, a: Any, b: Any) -> float:
        if a == b:
            return 1.0
        return 0.0

