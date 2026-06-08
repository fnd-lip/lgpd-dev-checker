"""RAG pipeline — chunk, embed, index, retrieve, generate.

Reaproveita as funcoes do notebook 02. Voce vai preencher 3 TODOs aqui.
"""
from __future__ import annotations
import os
from pathlib import Path
import re
import json
from src.pipeline.tools import run_tool_call

import chromadb
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
from langchain_text_splitters import RecursiveCharacterTextSplitter
from openai import OpenAI
from pypdf import PdfReader


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

        self.embed_fn = DefaultEmbeddingFunction()

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
        pdfs = sorted(self.corpus_dir.glob("*.pdf"))
        if not pdfs:
            raise RuntimeError(f"Nenhum PDF encontrado em {self.corpus_dir}")

        for caminho_pdf in pdfs:
            leitor = PdfReader(str(caminho_pdf))

            for numero_pagina, pagina in enumerate(leitor.pages, start=1):
                texto = (pagina.extract_text() or "").strip()

                if texto:
                    docs.append(
                        {
                            "text": texto,
                            "source": caminho_pdf.name,
                            "page": numero_pagina,
                        }
                    )
        if not docs:
            raise RuntimeError("Nenhum texto extraivel encontrado nos PDFs do corpus")

        # SEU CODIGO AQUI — TODO 1.B
        # Aplicar RecursiveCharacterTextSplitter com chunk_size=800, overlap=100
        # Quebrar cada doc em chunks e construir lista `chunks` com:
        # {"id": unique_id, "text": str, "source": str, "page": int}
        # Dica: reaproveite o notebook 02 (Etapa 2 — Chunking Recursivo).
        chunks: list[dict] = []
        divisor = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=100,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

        for indice_doc, doc in enumerate(docs):
            partes = divisor.split_text(doc["text"])

            for indice_chunk, parte in enumerate(partes):
                chunks.append(
                    {
                        "id": (
                            f"{doc['source']}"
                            f"-p{doc['page']}"
                            f"-d{indice_doc}"
                            f"-c{indice_chunk}"
                        ),
                        "text": parte,
                        "source": doc["source"],
                        "page": doc["page"],
                    }
                )

        if not chunks:
            raise RuntimeError("Nenhum chunk foi gerado a partir do corpus")

        # SEU CODIGO AQUI — TODO 1.C
        # Adicionar chunks no Chroma via self.collection.add(ids=, documents=, metadatas=)
        # Lembre de filtrar metadatas para conter apenas {source, page} (Chroma rejeita listas).
        batch_size = 100

        for inicio in range(0, len(chunks), batch_size):
            lote = chunks[inicio : inicio + batch_size]

            self.collection.add(
                ids=[chunk["id"] for chunk in lote],
                documents=[chunk["text"] for chunk in lote],
                metadatas=[
                    {
                        "source": chunk["source"],
                        "page": chunk["page"],
                    }
                    for chunk in lote
                ],
            )
        return self.collection.count()

    # ------------------------------------------------------------------ TODO 2
    def retrieve(self, query: str, k: int = 5) -> list[dict]:
        """Busca top-k chunks similares a query."""
        # SEU CODIGO AQUI — TODO 2
        # Usar self.collection.query(query_texts=[query], n_results=k)
        # Retornar lista de dicts: {"text", "source", "page", "distance"}
        # Dica: notebook 02, Etapa 4 — Retrieval.
        resultado = self.collection.query(
            query_texts=[query],
            n_results=k,
        )

        documentos = resultado.get("documents", [[]])[0]
        metadados = resultado.get("metadatas", [[]])[0]
        distancias = resultado.get("distances", [[]])[0]

        hits: list[dict] = []

        for texto, metadata, distancia in zip(documentos, metadados, distancias):
            metadata = metadata or {}

            hits.append(
                {
                    "text": texto,
                    "source": metadata.get("source", "desconhecido"),
                    "page": metadata.get("page", "?"),
                    "distance": distancia,
                }
            )

        return hits

    # ------------------------------------------------------------------ TODO 3
    def answer(self, question: str, k: int = 5) -> dict:
        """Pipeline completo: retrieve + augment + generate. Retorna {answer, sources}."""
        hits = self.retrieve(question, k=k)
        
        tool_context = ""

        article_match = re.search(
            r"\bart\.?\s*(\d+)|artigo\s+(\d+)",
            question,
            re.IGNORECASE,
        )

        if article_match:
            article_number = int(article_match.group(1) or article_match.group(2))
            tool_result = run_tool_call(
                "cite_article",
                json.dumps({"article_number": article_number}),
            )
            tool_context = f"\n\n[tool:cite_article]\n{tool_result}"

        # SEU CODIGO AQUI — TODO 3
        # 1. Montar contexto concatenando os textos dos hits com cabecalho [source:page]
        # 2. Construir prompt com PROMPT_TEMPLATE (definido abaixo)
        # 3. Chamar self.client.chat.completions.create(model=self.llm_model, ...)
        # 4. Retornar {"answer": resposta, "sources": [(s, p) for h in hits]}
        # Dica: notebook 02, Etapa 5 — Augment + Generate.
        if not hits:
            return {
                "answer": "Nao encontrado no corpus.",
                "sources": [],
            }

        contexto = "\n\n".join(
            f"[{hit['source']}:{hit['page']}]\n{hit['text']}"
            for hit in hits
        )

        if tool_context:
            contexto = f"{tool_context}\n\n{contexto}"

        prompt = PROMPT_TEMPLATE.format(
            context=contexto,
            question=question,
        )

        resposta = self.client.chat.completions.create(
            model=self.llm_model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            temperature=0.2,
        )

        conteudo = resposta.choices[0].message.content or ""

        fontes = list(
            dict.fromkeys(
                (hit["source"], hit["page"])
                for hit in hits
            )
        )

        return {
            "answer": conteudo,
            "sources": fontes,
        }


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
