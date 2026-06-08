# Corpus

Esta pasta recebe os PDFs do seu projeto.

## Como usar

1. Substitua o corpus pelos seus documentos (PDFs, ≤10 arquivos, ≤50MB total)
2. Se for usar os mesmos 3 papers do M2, copie de:
   ```bash
   cp ../../../../datasets/corpus/*.pdf data/corpus/   # se rodou o download.py do curso
   ```
3. Rode o pipeline pela primeira vez — ele indexa automaticamente em `data/chroma/`

## Restricoes

- Pelo menos 1 PDF (senao o pipeline aborta no ingest)
- Apenas texto extraivel (PDFs escaneados sem OCR nao funcionam — use `ocrmypdf` antes)
- Documentos sem direitos autorais ou com licenca compativel com uso publico (seu deploy
  vai expor a busca sobre eles)
