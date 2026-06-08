"""Cache em 2 niveis: exact-match (SHA256) + semantic (cosine similarity).

Reaproveita o notebook 05. Voce vai preencher 1 TODO aqui.
"""

from __future__ import annotations

import hashlib
import os
from typing import Any

import numpy as np
from openai import OpenAI


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

    def stats(self) -> dict[str, int]:
        return {"size": len(self._store)}


class SemanticCache:
    """Cache por similaridade de embedding. Captura parafrases (~20% adicional)."""

    def __init__(self, threshold: float = 0.93) -> None:
        self.threshold = threshold
        self._queries: list[str] = []
        self._embeddings: list[np.ndarray] = []
        self._answers: list[str] = []

        # Inicializa cliente para embeddings (mesmo provider do RAG)
        if "GEMINI_API_KEY" in os.environ:
            self._client = OpenAI(
                api_key=os.environ["GEMINI_API_KEY"],
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            )
            self._embed_model = os.environ.get("EMBED_MODEL", "gemini-embedding-001")
        else:
            self._client = OpenAI()
            self._embed_model = "text-embedding-3-small"

    def _embed(self, text: str) -> np.ndarray:
        r = self._client.embeddings.create(model=self._embed_model, input=text)
        return np.array(r.data[0].embedding)

    # ------------------------------------------------------------------ TODO 5
    def get(self, query: str) -> str | None:
        """Retorna resposta cacheada se similar a query alguma anterior, OU None."""
        if not self._queries:
            return None

        # SEU CODIGO AQUI — TODO 5
        # 1. Embedar a query (self._embed)
        # 2. Calcular similaridade cosseno contra todos self._embeddings:
        #    cos_sim = np.dot(e, em) / (np.linalg.norm(e) * np.linalg.norm(em))
        # 3. Pegar idx do maior; se sims[idx] >= self.threshold, retornar self._answers[idx]
        # 4. Caso contrario, retornar None
        # Dica: notebook 05, Etapa 4 — Semantic Cache.
        raise NotImplementedError("TODO 5: implementar SemanticCache.get()")

    def put(self, query: str, answer: str) -> None:
        self._queries.append(query)
        self._embeddings.append(self._embed(query))
        self._answers.append(answer)

    def stats(self) -> dict[str, Any]:
        return {"size": len(self._queries), "threshold": self.threshold}
