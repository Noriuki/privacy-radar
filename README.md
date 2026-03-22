# PrivacyRadar

Assistente de **privacidade LGPD** com duas frentes: **5 perguntas amplas para desenvolvedores** (linguagem simples; depois dicas + referência a artigos) e **análise de contrato** OpenAPI / GraphQL (mapa de superfície por endpoint ou tipo).

**Não há análise de payload JSON solto** — o foco é processo (checklist) e contrato da API.

**Stack:** Python 3.11+, FastAPI, React 18, Vite, Docker Compose.

---

## Estrutura

```
privacy-radar/
├── docker-compose.yml
├── backend/
│   ├── app/interface/     # FastAPI, rotas, schemas
│   ├── privacy_scan/      # lgpd_checklist.py, openapi_surface.py, detectors.py
│   └── tests/
├── frontend/              # React + Vite (abas: LGPD | Contrato)
└── Makefile
```

---

## Como rodar

```bash
make install-backend && make install-frontend
make run-backend    # terminal 1 — http://localhost:8000/docs
make run-frontend   # terminal 2 — http://localhost:5173
```

**Docker:** `docker compose up --build`

---

## API (`/api/v1`)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/lgpd/questions` | Perguntas do checklist |
| POST | `/lgpd/submit` | Body `{ "answers": { "id_pergunta": "valor", ... } }` → relatório (score, maturidade, lacunas com artigos) |
| POST | `/contract/openapi` | JSON OpenAPI 3.x → mapa por operação |
| POST | `/contract/graphql` | JSON de introspection GraphQL → tipos/campos com heurística |

Rate limit: **30 req/min** por IP nos endpoints de escrita.

---

## LGPD & disclaimer

O checklist é **ferramenta educativa** para triagem interna; **não substitui assessoria jurídica**. A análise de contrato usa **heurística de nomes de campos** (email, cpf, etc.) — não substitui revisão de negócio nem testes de segurança.

---

## Objetivo do projeto

Demonstrar **conhecimento de LGPD** (artigos, lacunas), **arquitetura de API** (superfície de dados no OpenAPI/GraphQL) e **full-stack** (FastAPI + React).
