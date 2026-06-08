"""Function-calling / tool-use — registro de tools usadas pelo agente.

Reaproveita o LAB-001. Voce vai preencher 1 TODO aqui (sua tool especifica).
"""

from __future__ import annotations

import json
from typing import Any, Callable


# ============================================================================
# TODO 4 — Sua tool especifica do dominio
# ============================================================================
# Cada projeto precisa de UMA tool customizada que faca sentido para o problema.
# Exemplos por dominio:
#   - Livro tecnico:    lookup_chapter(chapter: int) -> str
#   - Changelog:        check_compat(lib: str, version: str) -> dict
#   - Podcast:          get_timestamp(quote: str) -> str
#   - Codigo:           run_snippet(code: str) -> str  (sandboxed)
#   - Documentos legais: cite_article(law: str, article: int) -> str
#
# 1. Implemente a funcao Python real abaixo (substitua o exemplo)
# 2. Adicione o schema JSON em TOOLS abaixo
# 3. Registre em TOOL_REGISTRY
# ============================================================================


# SEU CODIGO AQUI — TODO 4
def my_domain_tool(arg1: str) -> str:
    """Substitua esta funcao pela sua tool especifica.

    A funcao deve receber argumentos primitivos (str, int, float, bool) e
    retornar string com o resultado (sera passado de volta ao LLM como tool result).
    """
    return f"TODO: implementar tool para o argumento: {arg1}"


TOOLS: list[dict[str, Any]] = [
    # SEU CODIGO AQUI — TODO 4 (continuacao)
    # Adicione o schema JSON da sua tool. Modelo (referencia LAB-001):
    # {
    #     "type": "function",
    #     "function": {
    #         "name": "my_domain_tool",
    #         "description": "Descrever o que a tool faz em pt-BR — LLM le isso para decidir quando usar",
    #         "parameters": {
    #             "type": "object",
    #             "properties": {
    #                 "arg1": {"type": "string", "description": "..."},
    #             },
    #             "required": ["arg1"],
    #         },
    #     },
    # },
]


TOOL_REGISTRY: dict[str, Callable[..., str]] = {
    # "my_domain_tool": my_domain_tool,
}


def run_tool_call(name: str, arguments_json: str) -> str:
    """Executa uma tool call e retorna o resultado como string."""
    if name not in TOOL_REGISTRY:
        return f"ERROR: tool '{name}' nao registrada"
    try:
        kwargs = json.loads(arguments_json)
        return TOOL_REGISTRY[name](**kwargs)
    except Exception as e:
        return f"ERROR ao executar {name}: {e}"
