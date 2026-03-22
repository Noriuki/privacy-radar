"""LGPD — 5 perguntas amplas e simples (para quem desenvolve)."""

from __future__ import annotations

from typing import Any

QUESTIONS: list[dict[str, Any]] = [
    {
        "id": "dados_clareza",
        "text": "Vocês **coletam ou guardam dados de pessoas** (cadastro, login, contato, documento) e isso está **claro para quem usa** o produto (site, app, política)?",
        "type": "single",
        "options": [
            {"value": "nao", "label": "Não — não guardamos dados pessoais reais"},
            {"value": "sim_claro", "label": "Sim — e está claro para o usuário"},
            {"value": "sim_nebuloso", "label": "Sim — mas pouco claro ou só para o time"},
            {"value": "nao_sei", "label": "Não sei dizer"},
        ],
    },
    {
        "id": "fora_brasil",
        "text": "Esses dados passam por **serviço ou servidor fora do Brasil**? (cloud, e-mail, analytics, etc.)",
        "type": "single",
        "options": [
            {"value": "nao", "label": "Não / só no Brasil"},
            {"value": "sim", "label": "Sim"},
            {"value": "nao_sei", "label": "Não sei"},
        ],
    },
    {
        "id": "seguranca",
        "text": "**Segurança básica** no dia a dia: HTTPS, senha não em texto puro no banco, pouca gente com acesso a produção?",
        "type": "single",
        "options": [
            {"value": "sim", "label": "Sim, ok"},
            {"value": "parcial", "label": "Em parte"},
            {"value": "nao", "label": "Não / não sei"},
        ],
    },
    {
        "id": "exclusao",
        "text": "Quem usa consegue **pedir para apagar ou corrigir** dados ou conta, de forma mais ou menos clara?",
        "type": "single",
        "options": [
            {"value": "sim", "label": "Sim"},
            {"value": "parcial", "label": "Só manual ou demorado"},
            {"value": "nao", "label": "Não"},
        ],
    },
    {
        "id": "incidente",
        "text": "Se **vazar** dado (vazamento, erro, acesso indevido), o time tem **alguma ideia** do que fazer?",
        "type": "single",
        "options": [
            {"value": "sim", "label": "Sim"},
            {"value": "parcial", "label": "Mais ou menos"},
            {"value": "nao", "label": "Não"},
        ],
    },
]


def evaluate_checklist(answers: dict[str, str]) -> dict[str, Any]:
    gaps: list[dict[str, str]] = []
    score = 100

    def penalize(points: int, article: str, title: str, gap: str) -> None:
        nonlocal score
        score = max(0, score - points)
        gaps.append({"article": article, "title": title, "gap": gap})

    dc = answers.get("dados_clareza")

    # Sem dados pessoais: só segurança + incidente (amplo)
    if dc == "nao":
        v = answers.get("seguranca")
        if v == "nao":
            penalize(10, "Art. 46 LGPD", "Segurança", "Mesmo sem dados de usuários, proteja o sistema: HTTPS, segredos, acesso.")
        elif v == "parcial":
            penalize(5, "Art. 46 LGPD", "Segurança", "Feche pendências: HTTPS, variáveis de ambiente, quem acessa produção.")
        v = answers.get("incidente")
        if v == "nao":
            penalize(8, "Art. 48 LGPD", "Incidente", "Um plano simples já ajuda: quem avisa, trocar chaves, checar logs.")
        elif v == "parcial":
            penalize(4, "Art. 48 LGPD", "Incidente", "Escreva em uma página o que fazer se algo vazar.")
        return _finish(score, gaps)

    # Com dados (ou em dúvida): avaliação ampla
    if dc == "sim_nebuloso":
        penalize(18, "Art. 6º LGPD", "Transparência", "Deixe explícito no produto para que serve cada dado (texto curto já ajuda).")
    elif dc == "nao_sei":
        penalize(15, "Art. 5º LGPD", "Mapeamento", "Liste onde guardam nome, e-mail, telefone, documento — planilha ou diagrama rápido.")

    if dc in ("sim_claro", "sim_nebuloso", "nao_sei"):
        v = answers.get("fora_brasil")
        if v == "sim":
            penalize(10, "Art. 33–36 LGPD", "Fora do Brasil", "Saiba quais ferramentas são e onde ficam os dados (contratos, região da cloud).")
        elif v == "nao_sei":
            penalize(14, "Art. 33–36 LGPD", "Fora do Brasil", "Confira painéis da cloud, e-mail e analytics — muitas vezes há dado fora do BR.")

    v = answers.get("seguranca")
    if v == "nao":
        penalize(22, "Art. 46 LGPD", "Segurança", "HTTPS, hash de senha, segredos fora do código e menos gente no banco de produção.")
    elif v == "parcial":
        penalize(11, "Art. 46 LGPD", "Segurança", "Priorize o que ainda está frágil (senha, chaves, permissões).")

    v = answers.get("exclusao")
    if v == "nao":
        penalize(16, "Art. 18 LGPD", "Titular", "Canal claro: botão, e-mail, ticket ou API para apagar/corrigir.")
    elif v == "parcial":
        penalize(8, "Art. 18 LGPD", "Titular", "Padronize o processo para não depender só de uma pessoa.")

    v = answers.get("incidente")
    if v == "nao":
        penalize(14, "Art. 48 LGPD", "Vazamento", "Mini-runbook: detectou → quem avisa → trocar senhas/chaves → registrar o que aprendeu.")
    elif v == "parcial":
        penalize(7, "Art. 48 LGPD", "Vazamento", "Teste o plano: outra pessoa do time consegue seguir?")

    return _finish(score, gaps)


def _finish(score: float, gaps: list[dict[str, str]]) -> dict[str, Any]:
    if score >= 75:
        maturity = "high"
    elif score >= 45:
        maturity = "medium"
    else:
        maturity = "low"

    recommendations = [g["gap"] for g in gaps[:8]]
    if not recommendations:
        recommendations = [
            "Quando mudar login, cadastro ou integrações, revise de novo estes pontos.",
        ]

    return {
        "score": round(score, 0),
        "maturity": maturity,
        "gaps": gaps,
        "recommendations": recommendations,
        "disclaimer": "Ferramenta educativa. Não substitui assessoria jurídica.",
    }
