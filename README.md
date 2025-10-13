# ficr-teste (piloto LMF)

Fluxo: branch (feat/SEMx-...) → PR → CI (eslint/html-validate/prettier) → revisão → merge → Pages.

- Labels automáticos: `SEMx` + `IA:ON|IA:OFF` (via `.github/workflows/labeler.yml` conforme `policy/ia_schedule.json`).
- Métricas automáticas: `metrics.yml` gera `metrics/metrics.csv` (Processo + Produto).
- Issues anônimas: use `CodigoAluno` e `Squad` no título/corpo; não publique nome real.

Scripts:
- `npm run check` — qualidade local
