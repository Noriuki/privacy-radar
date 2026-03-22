# PrivacyRadar

Ferramenta full-stack de análise de privacidade que detecta riscos **LGPD** (Brasil) e **GDPR** (UE) em payloads e APIs. Backend em Python (FastAPI) e frontend em React (Vite), com front e back separados.

**Stack:** Python 3.11+, FastAPI, React 18, Vite, Docker Compose.

---

## Estrutura

```
privacy-radar/
├── docker-compose.yml   # api (8000) + web (5173)
├── backend/             # FastAPI, Clean Architecture
│   ├── app/             # domain, application, infrastructure, interface
│   ├── privacy_scan/    # detectors, rules, risk_scoring
│   ├── tests/
│   ├── run.py
│   ├── Dockerfile
│   └── pyproject.toml
├── frontend/            # React + Vite
│   ├── src/
│   │   ├── api/         # cliente HTTP (scanPayload)
│   │   ├── pages/       # HomePage (escanear payload, ver relatório)
│   │   └── components/
│   ├── package.json
│   └── Dockerfile
└── README.md
```

---

## Como rodar

**Com Make (recomendado):**

```bash
make install-backend   # uma vez
make install-frontend   # uma vez
make run-backend        # terminal 1
make run-frontend       # terminal 2
# ou: make docker-up   # sobe tudo com Docker
```

**Docker:**  
`cp .env.example .env && docker compose up --build`  
→ API http://localhost:8000 · Web http://localhost:5173

**Local – backend:**  
`cd backend` → `python3 -m venv .venv && source .venv/bin/activate` → `pip install -e .` → `python run.py`

**Local – frontend:**  
`cd frontend` → `npm install && npm run dev`  
(Configure `VITE_API_URL=http://localhost:8000` em `frontend/.env` se precisar.)

---

## LGPD & GDPR (resumo)

- **LGPD**: Lei brasileira; dados pessoais (nome, CPF, email, telefone, endereço etc.); princípios de finalidade, necessidade, transparência; direitos de acesso, correção, exclusão.
- **GDPR**: Regulamento europeu; conceitos equivalentes; dados pessoais incluem IP e identificadores; bases legais e minimização de dados.

O PrivacyRadar ajuda a **identificar** campos sensíveis em payloads JSON, **avaliar** nível de risco e **sugerir** boas práticas (criptografia, retenção, minimização).

---

## Funcionalidades

- **Escanear payload JSON** via API ou interface web.
- **Detectar dados sensíveis** por nome do campo e padrão (email, telefone, CPF, endereço, etc.).
- **Identificar riscos** com regras LGPD/GDPR e códigos (LGPD-CONTACT, GDPR-PII, etc.).
- **Relatório de conformidade** com nível de risco, score (0–100) e recomendações.
- **CLI** no backend: `privacy-radar [arquivo.json]` ou stdin.
- **Opcionais**: upload de arquivo JSON, escaneamento de schema OpenAPI.

---

## API (backend)

- **Base:** `http://localhost:8000`
- **Docs:** http://localhost:8000/docs
- **Health:** http://localhost:8000/health

Endpoints sob `/api/v1`:

| Método | Endpoint              | Descrição                                                        |
| ------ | --------------------- | ---------------------------------------------------------------- |
| GET    | `/api/v1/stats`       | Estatísticas (total de scans, por nível de risco)                |
| POST   | `/api/v1/scan`        | Escanear um JSON (body = payload). **Rate limit:** 30/min por IP |
| POST   | `/api/v1/scan/file`   | Upload de arquivo JSON (multipart, key `file`)                   |
| POST   | `/api/v1/scan/schema` | Escanear documento OpenAPI/JSON Schema                           |

**Exemplo POST /api/v1/scan:**

```json
// Request body
{
  "email": "user@email.com",
  "name": "John Doe",
  "phone": "+551199999999"
}

// Response: sensitive_fields, risks, risk_level, score, recommendations
```

---

## Frontend

Na **HomePage** você cola um JSON (objeto), clica em **Escanear** (ou usa **Ctrl+Enter**) e vê:

- Campos sensíveis detectados
- Nível de risco (Low / Medium / High / Critical) e score
- Riscos (código + descrição) com tooltip da recomendação
- Recomendações
- Botão **Copiar** para levar o relatório em JSON
- **Últimos escaneamentos** (até 5) com opção de restaurar
- **Exemplos** rápidos (Pessoal, Com CPF, Vazio)
- **Tema claro/escuro** (persistido)
- Barra de **estatísticas** da sessão (total de scans, por nível)

O front chama o backend em `VITE_API_URL` (default `http://localhost:8000`) no endpoint `/api/v1/scan`.

---

## Arquitetura (backend)

Clean Architecture:

- **domain**: entidades (SensitiveField, PrivacyRisk, ScanResult, RiskLevel).
- **application**: portas (DetectionEnginePort) e use case (ScanPayloadUseCase).
- **infrastructure**: RuleBasedDetectionEngine (usa `privacy_scan`).
- **interface**: FastAPI (rotas em `/api/v1`), schemas Pydantic, CLI, file/schema scan.

Módulo **privacy_scan**: `detectors.py` (padrões e nomes de campos), `rules.py` (riscos e recomendações), `risk_scoring.py` (score e nível).

---

## Riscos detectados (exemplos)

| Dado detectado    | Código          | Exemplo de recomendação                   |
| ----------------- | --------------- | ----------------------------------------- |
| Email / telefone  | LGPD-CONTACT    | Criptografar dados; política de retenção  |
| CPF / RG / CNPJ   | LGPD-IDENTIFIER | Tokenização; armazenar só se necessário   |
| Endereço / CEP    | LGPD-LOCATION   | Minimizar coleta; criptografia e retenção |
| Nome / data nasc. | GDPR-PII        | Base legal e consentimento; minimização   |
| IP                | GDPR-IP         | Anonimizar; documentar base legal         |
| Cartão            | PCI-SENSITIVE   | Não armazenar número bruto; tokenização   |

---

## Objetivo do projeto

Demonstrar conhecimento em **conformidade de privacidade** (LGPD/GDPR), **arquitetura de backend** (Clean Architecture) e **detecção de riscos em dados** (motor baseado em regras e scoring).
