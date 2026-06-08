"""Smoke tests — rodam apos voce implementar TODOs 1-3 para validar minimo.

Uso: `uv run pytest tests/test_smoke.py -v`

Para destravar este teste, voce precisa de:
- TODOs 1-3 implementados em src/pipeline/rag.py
- Corpus em data/corpus/ com pelo menos 1 PDF
- .env configurado com API key
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest


@pytest.fixture(scope="module")
def pipeline():
    """Inicializa pipeline RAG com corpus de teste."""
    pytest.importorskip("dotenv")
    from dotenv import load_dotenv

    load_dotenv()

    if not (os.environ.get("GEMINI_API_KEY") or os.environ.get("OPENAI_API_KEY")):
        pytest.skip("API key nao configurada em .env")

    corpus_dir = Path("data/corpus")
    if not corpus_dir.exists() or not list(corpus_dir.glob("*.pdf")):
        pytest.skip("data/corpus/ vazio — adicione pelo menos 1 PDF")

    from src.pipeline.rag import build_rag_pipeline

    return build_rag_pipeline(corpus_dir=str(corpus_dir))


def test_pipeline_indexa_chunks(pipeline):
    """Apos ingest, collection deve ter >= 1 chunk."""
    assert pipeline.collection.count() > 0, "Esperado >=1 chunk indexado"


def test_retrieve_top_k(pipeline):
    """Retrieve deve retornar lista de dicts com campos esperados."""
    hits = pipeline.retrieve("teste de busca", k=3)
    assert isinstance(hits, list)
    assert len(hits) <= 3
    if hits:
        h = hits[0]
        assert "text" in h
        assert "source" in h
        assert "distance" in h


def test_answer_retorna_resposta_com_fonte(pipeline):
    """answer() deve retornar dict com 'answer' string nao-vazia e 'sources' lista."""
    result = pipeline.answer("Sobre o que e este corpus?")
    assert isinstance(result, dict)
    assert "answer" in result
    assert isinstance(result["answer"], str)
    assert len(result["answer"]) > 0
    assert "sources" in result
    assert isinstance(result["sources"], list)
