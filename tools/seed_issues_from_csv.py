#!/usr/bin/env python3
import sys, os, csv, requests

CSV_PATH = sys.argv[1] if len(sys.argv) > 1 else None
REPO = sys.argv[2] if len(sys.argv) > 2 else None   # org/repo
ASSIGNEE = sys.argv[3] if len(sys.argv) > 3 and sys.argv[3] else None
TOKEN = os.getenv("GITHUB_TOKEN")

if not (CSV_PATH and REPO and TOKEN):
    sys.exit("Usage: seed_issues_from_csv.py <csv> <org/repo> [assignee_login]; need GITHUB_TOKEN")

S = requests.Session()
S.headers.update({"Authorization": f"Bearer {TOKEN}", "Accept":"application/vnd.github+json"})

with open(CSV_PATH, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    required = {"Semana","Titulo","Descricao","Criterios","CodigoAluno","Squad"}
    if not required.issubset(set(reader.fieldnames or [])):
        sys.exit(f"CSV must have columns: {', '.join(sorted(required))}")

    for row in reader:
        semana = (row.get("Semana","SEM1")).strip().upper()
        titulo = row.get("Titulo","Tarefa").strip()
        desc   = row.get("Descricao","...").strip()
        crit   = row.get("Criterios","- [ ] `npm run check` passando").strip()
        codigo = row.get("CodigoAluno","ALN-000").strip()
        squad  = row.get("Squad","A").strip().upper()

        issue_title = f\"[{semana}] {titulo} — {codigo}/{squad}\"
        body = f\"\"\"## 📋 Descrição (Anônima)
Código do Aluno: **{codigo}**
Squad: **{squad}**

{desc}

## 🎯 Critérios de Aceite
{crit}

## 🏷 Semana e IA
- Semana: {semana}
- IA (via schedule): ver rótulos automáticos do PR (labeler.yml)

## 🧪 Validação
- `npm run check` deve passar
- Testar em 360px e 1280px
- Acessibilidade básica (foco visível, labels)
\"\"\"
        payload = {\"title\": issue_title, \"body\": body, \"labels\":[ \"Tipo:Tarefa\", semana ]}
        if ASSIGNEE:
            payload[\"assignees\"]= [ASSIGNEE]
        r = S.post(f\"https://api.github.com/repos/{REPO}/issues\", json=payload)
        r.raise_for_status()
        print(\"Criada:\", issue_title)
