"""RAG pipeline — chunk, embed, index, retrieve, generate.

Reaproveita as funcoes do notebook 02. Voce vai preencher 3 TODOs aqui.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from openai import OpenAI


def _make_client() -> tuple[OpenAI, str]:
    """Inicializa cliente OpenAI-compatible conforme provider escolhido no .env."""
    if "GEMINI_API_KEY" in os.environ:
        client = OpenAI(
            api_key=os.environ["GEMINI_API_KEY"],
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        )
        embed_api_base = "https://generativelanguage.googleapis.com/v1beta/openai/"
    elif "OPENAI_API_KEY" in os.environ:
        client = OpenAI()
        embed_api_base = None
    else:
        raise RuntimeError("Configure GEMINI_API_KEY ou OPENAI_API_KEY no .env")
    return client, embed_api_base


class RAGPipeline:
    """Pipeline RAG end-to-end com Chroma local."""

    def __init__(
        self,
        corpus_dir: str = "data/corpus",
        persist_dir: str = "data/chroma",
        collection_name: str = "docs",
        llm_model: str | None = None,
        embed_model: str | None = None,
    ) -> None:
        self.client, embed_api_base = _make_client()
        self.llm_model = llm_model or os.environ.get("LLM_MODEL", "gemini-2.5-flash-lite")
        self.embed_model = embed_model or os.environ.get("EMBED_MODEL", "gemini-embedding-001")

        embed_kwargs: dict[str, Any] = {
            "api_key": os.environ.get("GEMINI_API_KEY") or os.environ.get("OPENAI_API_KEY"),
            "model_name": self.embed_model,
        }
        if embed_api_base:
            embed_kwargs["api_base"] = embed_api_base
        self.embed_fn = OpenAIEmbeddingFunction(**embed_kwargs)

        self.corpus_dir = Path(corpus_dir)
        self.persist_dir = persist_dir
        self.collection_name = collection_name

        chroma = chromadb.PersistentClient(path=persist_dir)
        self.collection = chroma.get_or_create_collection(
            name=collection_name, embedding_function=self.embed_fn
        )

    # ------------------------------------------------------------------ TODO 1
    def ingest_and_index(self) -> int:
        """Le PDFs de `corpus_dir`, faz chunking e indexa em Chroma.

        Retorna numero de chunks indexados.

        Ja deixei a estrutura do ciclo. Voce completa as 3 partes marcadas.
        """
        # SEU CODIGO AQUI — TODO 1.A
        # Iterar por todos os PDFs em self.corpus_dir.
        # Para cada PDF, ler todas as paginas com PdfReader e extrair texto.
        # Acumular numa lista `docs` com dicts: {"text": str, "source": str, "page": int}
        # Dica: reaproveite o snippet do notebook 02 (Etapa 1 — Ingestao de PDFs).
        docs: list[dict] = []

        # SEU CODIGO AQUI — TODO 1.B
        # Aplicar RecursiveCharacterTextSplitter com chunk_size=800, overlap=100
        # Quebrar cada doc em chunks e construir lista `chunks` com:
        # {"id": unique_id, "text": str, "source": str, "page": int}
        # Dica: reaproveite o notebook 02 (Etapa 2 — Chunking Recursivo).
        chunks: list[dict] = []

        # SEU CODIGO AQUI — TODO 1.C
        # Adicionar chunks no Chroma via self.collection.add(ids=, documents=, metadatas=)
        # Lembre de filtrar metadatas para conter apenas {source, page} (Chroma rejeita listas).

        return self.collection.count()

    # ------------------------------------------------------------------ TODO 2
    def retrieve(self, query: str, k: int = 5) -> list[dict]:
        """Busca top-k chunks similares a query."""
        # SEU CODIGO AQUI — TODO 2
        # Usar self.collection.query(query_texts=[query], n_results=k)
        # Retornar lista de dicts: {"text", "source", "page", "distance"}
        # Dica: notebook 02, Etapa 4 — Retrieval.
        raise NotImplementedError("TODO 2: implementar retrieve()")

    # ------------------------------------------------------------------ TODO 3
    def answer(self, question: str, k: int = 5) -> dict:
        """Pipeline completo: retrieve + augment + generate. Retorna {answer, sources}."""
        hits = self.retrieve(question, k=k)

        # SEU CODIGO AQUI — TODO 3
        # 1. Montar contexto concatenando os textos dos hits com cabecalho [source:page]
        # 2. Construir prompt com PROMPT_TEMPLATE (definido abaixo)
        # 3. Chamar self.client.chat.completions.create(model=self.llm_model, ...)
        # 4. Retornar {"answer": resposta, "sources": [(s, p) for h in hits]}
        # Dica: notebook 02, Etapa 5 — Augment + Generate.
        raise NotImplementedError("TODO 3: implementar answer()")


PROMPT_TEMPLATE = """Voce e um assistente tecnico. Responda APENAS com base no contexto abaixo.
Se a informacao nao estiver no contexto, diga "Nao encontrado no corpus".
Sempre cite a fonte usando o formato [arquivo:pagina].

CONTEXTO:
{context}

PERGUNTA: {question}

RESPOSTA:"""


def build_rag_pipeline(corpus_dir: str = "data/corpus") -> RAGPipeline:
    """Factory: cria pipeline e indexa corpus se ainda nao indexado."""
    pipeline = RAGPipeline(corpus_dir=corpus_dir)
    if pipeline.collection.count() == 0:
        pipeline.ingest_and_index()
    return pipeline
