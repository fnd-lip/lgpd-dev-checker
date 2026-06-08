"""Function-calling / tool-use — registro de tools usadas pelo agente.

Reaproveita o LAB-001. Voce vai preencher 1 TODO aqui (sua tool especifica).
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Callable

from pypdf import PdfReader


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
def cite_article(article_number: int) -> str:
    """Retorna o texto de um artigo especifico da LGPD.

    A funcao recebe o numero do artigo e busca o texto correspondente
    no PDF local `data/corpus/lgpd.pdf`.
    """
    if article_number < 1:
        return "ERROR: informe um numero de artigo valido, por exemplo 5"

    project_root = Path(__file__).resolve().parents[2]
    lgpd_path = project_root / "data" / "corpus" / "lgpd.pdf"

    if not lgpd_path.exists():
        return f"ERROR: arquivo nao encontrado: {lgpd_path}"

    reader = PdfReader(str(lgpd_path))
    full_text = "\n".join(page.extract_text() or "" for page in reader.pages)
    text = re.sub(r"\s+", " ", full_text).strip()

    current_pattern = re.compile(
        rf"\bArt\.\s*{article_number}\s*(?:º|o|°)?\b",
        re.IGNORECASE,
    )

    current_match = current_pattern.search(text)
    if not current_match:
        return f"Art. {article_number} nao encontrado no PDF da LGPD."

    next_pattern = re.compile(
        rf"\bArt\.\s*{article_number + 1}\s*(?:º|o|°)?\b",
        re.IGNORECASE,
    )

    next_match = next_pattern.search(text, current_match.end())

    start = current_match.start()
    end = next_match.start() if next_match else len(text)

    return text[start:end].strip()


TOOLS: list[dict[str, Any]] = [
    # SEU CODIGO AQUI — TODO 4 (continuacao)
    # Adicione o schema JSON da sua tool. Modelo (referencia LAB-001):
       {
        "type": "function",
        "function": {
            "name": "cite_article",
            "description": (
                "Retorna o texto de um artigo especifico da LGPD a partir "
                "do PDF local do corpus. Use quando a pergunta mencionar "
                "um numero de artigo ou exigir citacao literal da LGPD."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "article_number": {
                        "type": "integer",
                        "description": "Numero do artigo da LGPD. Exemplo: 5, 6, 7, 18.",
                    },
                },
                "required": ["article_number"],
            },
        },
    },
]


TOOL_REGISTRY: dict[str, Callable[..., str]] = {
    "cite_article": cite_article,
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
