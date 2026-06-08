"""Model routing cheap-first com fallback.

Reaproveita o notebook 05. Voce vai preencher 1 TODO aqui.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from openai import OpenAI


@dataclass(frozen=True)
class RouteDecision:
    model: str
    complexity: str  # "simple" | "complex"
    reason: str


# ------------------------------------------------------------------ TODO 6
def classify_complexity(query: str) -> RouteDecision:
    """Classifica complexidade da query para escolher modelo (cheap vs premium).

    Estrategia heuristica simples. Em producao, evoluiria para classifier treinado.
    """
    cheap_model = os.environ.get("CHEAP_MODEL", "gemini-2.5-flash-lite")
    premium_model = os.environ.get("PREMIUM_MODEL", "gemini-2.5-pro")

    query_normalizada = query.strip().lower()

    palavras_complexas = [
        "explique",
        "compare",
        "analise",
        "análise",
        "projete",
        "detalhe",
        "detalhar",
        "resuma",
        "relacione",
        "justifique",
        "avalie",
        "quais riscos",
        "passo a passo",
        "exemplos",
        "diferença",
        "diferenças",
    ]

    if any(palavra in query_normalizada for palavra in palavras_complexas):
        return RouteDecision(
            model=premium_model,
            complexity="complex",
            reason="A pergunta pede analise, comparacao, explicacao detalhada ou avaliacao.",
        )

    if len(query_normalizada) > 180:
        return RouteDecision(
            model=premium_model,
            complexity="complex",
            reason="A pergunta e longa e pode exigir raciocinio mais detalhado.",
        )

    if len(query_normalizada) < 60 and query_normalizada.endswith("?"):
        return RouteDecision(
            model=cheap_model,
            complexity="simple",
            reason="A pergunta e curta, direta e termina com interrogacao.",
        )

    return RouteDecision(
        model=cheap_model,
        complexity="simple",
        reason="A pergunta nao acionou criterios de complexidade.",
    )


def make_client() -> OpenAI:
    """Cliente OpenAI-compatible para o provider configurado."""
    if "GEMINI_API_KEY" in os.environ:
        return OpenAI(
            api_key=os.environ["GEMINI_API_KEY"],
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        )
    return OpenAI()
