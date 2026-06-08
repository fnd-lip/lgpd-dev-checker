# Observability — Guia rápido

> **Quando ler:** se você quer atingir banda **"Excelente"** na rubrica de Custo/Latência (20% da nota) — exige métricas observáveis em produção.

## Estado atual do template

O template já vem com `src/observability/trace.py` que faz **structured logging** mínimo (trace_id por requisição, model, tokens, latência).

Isso atende a banda **"Sólido"** da rubrica. Para banda **"Excelente"**, recomendamos integrar **Langfuse**.

## Integração Langfuse (3 linhas)

**1. Conta gratuita:** crie em [langfuse.com](https://langfuse.com) → projeto novo → copie `LANGFUSE_PUBLIC_KEY` + `LANGFUSE_SECRET_KEY`

**2. Instalar + configurar:**

```bash
uv pip install langfuse
```

Adicione ao `.env`:

```
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_HOST=https://cloud.langfuse.com
```

**3. Decorar suas funções LLM:**

```python
from langfuse.decorators import observe

@observe()
def call_llm(prompt: str, model: str = "gpt-4o-mini") -> str:
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content
```

Isso já gera **traces automáticos** em `cloud.langfuse.com` com:

- Prompt completo enviado
- Resposta gerada
- Latência (ms)
- Custo estimado (USD)
- Tokens input/output

## O que mostrar no README do projeto

Para banda "Excelente", inclua na seção de Observabilidade:

- **Screenshot do dashboard Langfuse** com 10+ traces reais
- **P95 de latência** observado (valor numérico)
- **Hit rate do cache** (% de queries que pegaram cache)

## Alternativas

| Tool | Pros | Cons |
|---|---|---|
| **Langfuse** | Free tier generoso, focus em LLM, eval scores | Servidor externo |
| **W&B Weave** | Integra com experiments existentes, dashboards ricos | Conta W&B necessária |
| **Phoenix (Arize)** | Open-source, self-hostable | Setup mais complexo |
| **Structured logs only** | Zero dependência, já vem no template | Sem UI — análise manual |

## Trade-off

Para a turma M4-Mod4:
- **Modalidade A + trilha Basic/Intermediate:** structured logs do template já é suficiente para banda Sólido
- **Modalidade A + trilha Advanced ou Modalidade B:** integre Langfuse para banda Excelente
- Investimento: ~15 minutos de setup, ROI alto se você for explicar o projeto em entrevista
