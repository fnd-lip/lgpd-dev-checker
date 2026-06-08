"""Streamlit UI — entrada principal do app. Pronta para deploy 1-click no Streamlit Cloud.

Voce nao precisa editar quase nada aqui — ja faz integracao com:
- src.pipeline.rag (TODOs 1-3)
- src.pipeline.cache (TODO 5)
- src.pipeline.routing (TODO 6)
- src.pipeline.tools (TODO 4, opcional)
"""

from __future__ import annotations

import sys
from pathlib import Path

from dotenv import load_dotenv

# Adiciona o root do projeto no path para imports
_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT))

load_dotenv()

import streamlit as st  # noqa: E402

from src.observability.trace import trace, log_event  # noqa: E402
from src.pipeline.cache import ExactCache, SemanticCache  # noqa: E402
from src.pipeline.rag import build_rag_pipeline  # noqa: E402
from src.pipeline.routing import classify_complexity  # noqa: E402


# ---------------------------------------------------------------- Streamlit UI
st.set_page_config(page_title="Portfolio LLM Demo", page_icon=":robot:", layout="centered")

st.title(":robot: TODO — Substitua pelo titulo do seu projeto")
st.caption("TODO — Substitua: 1-sentence pitch do seu projeto")


# Inicializacao lazy de pipeline + caches
@st.cache_resource
def get_pipeline():
    return build_rag_pipeline(corpus_dir=str(_ROOT / "data" / "corpus"))


@st.cache_resource
def get_exact_cache():
    return ExactCache()


@st.cache_resource
def get_semantic_cache():
    return SemanticCache(threshold=0.93)


with st.spinner("Inicializando pipeline RAG..."):
    pipeline = get_pipeline()
    exact_cache = get_exact_cache()
    semantic_cache = get_semantic_cache()


# Sidebar — metricas e debug
with st.sidebar:
    st.header("Metricas")
    st.metric("Chunks indexados", pipeline.collection.count())
    st.metric("Exact cache", exact_cache.stats()["size"])
    st.metric("Semantic cache", semantic_cache.stats()["size"])

    if st.button("Limpar caches"):
        get_exact_cache.clear()
        get_semantic_cache.clear()
        st.success("Caches limpos. Recarregue a pagina.")


# Main — chat interface
query = st.text_input("Sua pergunta:", placeholder="Pergunte algo sobre o corpus indexado...")

if query:
    with trace("query_handle", query=query) as ctx:
        trace_id = ctx["trace_id"]

        # 1. Exact cache
        cached = exact_cache.get(query)
        if cached:
            st.success("Cache hit (exact)")
            st.write(cached)
            log_event("cache_hit", trace_id=trace_id, layer="exact")
            st.stop()

        # 2. Semantic cache
        try:
            cached = semantic_cache.get(query)
        except NotImplementedError:
            cached = None
            st.warning("Semantic cache nao implementado (TODO 5). Caindo no LLM real.")

        if cached:
            st.success("Cache hit (semantic)")
            st.write(cached)
            log_event("cache_hit", trace_id=trace_id, layer="semantic")
            st.stop()

        # 3. Pipeline RAG + Routing
        try:
            decision = classify_complexity(query)
            st.info(f"Routing: {decision.complexity} -> {decision.model}")
            log_event("route_decision", trace_id=trace_id, **decision.__dict__)
        except NotImplementedError:
            st.warning("Routing nao implementado (TODO 6). Usando modelo default.")

        try:
            result = pipeline.answer(query)
        except NotImplementedError as e:
            st.error(f"Pipeline nao implementado: {e}")
            st.info("Implemente TODOs 1-3 em `src/pipeline/rag.py` para destravar.")
            st.stop()

        # 4. Renderiza + cacheia
        st.write(result["answer"])
        if result.get("sources"):
            with st.expander("Fontes citadas"):
                for source, page in result["sources"]:
                    st.write(f"- `{source}:p{page}`")

        exact_cache.put(query, result["answer"])
        semantic_cache.put(query, result["answer"])
        log_event("answer_generated", trace_id=trace_id, sources=len(result.get("sources", [])))


st.divider()
st.caption(
    "TODO README — substitua por: problem statement, arquitetura, custo/latencia, decisoes de design. "
    "Veja `README.md` do projeto para a estrutura completa."
)
