"""Cache em 2 niveis: exact-match (SHA256) + semantic (cosine similarity).

Reaproveita o notebook 05. Voce vai preencher 1 TODO aqui.
"""

from __future__ import annotations

import hashlib
import re
from typing import Any

import numpy as np

class ExactCache:
    """Cache por hash SHA256 da query. Captura replays exatos (~10-15% das queries)."""

    def __init__(self) -> None:
        self._store: dict[str, str] = {}

    @staticmethod
    def _key(query: str) -> str:
        return hashlib.sha256(query.encode()).hexdigest()

    def get(self, query: str) -> str | None:
        return self._store.get(self._key(query))

    def put(self, query: str, answer: str) -> None:
        self._store[self._key(query)] = answer
        
    def clear(self) -> None:
        self._store.clear()

    def stats(self) -> dict[str, int]:
        return {"size": len(self._store)}


class SemanticCache:
    """Cache por similaridade de embedding. Captura parafrases (~20% adicional)."""

    def __init__(self, threshold: float = 0.93) -> None:
        self.threshold = threshold
        self._queries: list[str] = []
        self._embeddings: list[np.ndarray] = []
        self._answers: list[str] = []

    def _embed(self, text: str) -> np.ndarray:
        """Gera embedding lexical local usando hashing de tokens.

        Nao chama API externa. Serve para cache semantico simples e deterministico.
        """
        vector = np.zeros(384, dtype=float)

        tokens = re.findall(r"\w+", text.lower())

        for token in tokens:
            index = int(hashlib.sha256(token.encode()).hexdigest(), 16) % len(vector)
            vector[index] += 1.0

        norm = np.linalg.norm(vector)

        if norm == 0:
            return vector

        return vector / norm

    # ------------------------------------------------------------------ TODO 5
    def get(self, query: str) -> str | None:
        """Retorna resposta cacheada se similar a query alguma anterior, OU None."""
        if not self._queries:
            return None

        query_embedding = self._embed(query)
        similarities: list[float] = []

        for cached_embedding in self._embeddings:
            denominator = np.linalg.norm(query_embedding) * np.linalg.norm(cached_embedding)

            if denominator == 0:
                similarities.append(0.0)
                continue

            similarity = float(np.dot(query_embedding, cached_embedding) / denominator)
            similarities.append(similarity)

        best_index = int(np.argmax(similarities))
        best_similarity = similarities[best_index]

        if best_similarity >= self.threshold:
            return self._answers[best_index]

        return None

    def put(self, query: str, answer: str) -> None:
        self._queries.append(query)
        self._embeddings.append(self._embed(query))
        self._answers.append(answer)
    
    def clear(self) -> None:
        self._queries.clear()
        self._embeddings.clear()
        self._answers.clear()

    def stats(self) -> dict[str, Any]:
        return {"size": len(self._queries), "threshold": self.threshold}