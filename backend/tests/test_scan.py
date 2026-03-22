"""Tests for privacy_scan modules (checklist + OpenAPI surface)."""

from privacy_scan.lgpd_checklist import evaluate_checklist
from privacy_scan.openapi_surface import analyze_openapi


def test_evaluate_checklist_high_score() -> None:
    answers = {
        "dados_clareza": "nao",
        "fora_brasil": "nao",
        "seguranca": "sim",
        "exclusao": "sim",
        "incidente": "sim",
    }
    r = evaluate_checklist(answers)
    assert r["score"] >= 70
    assert r["maturity"] in ("high", "medium", "low")


def test_analyze_openapi_finds_email_param() -> None:
    spec = {
        "openapi": "3.0.0",
        "info": {"title": "X", "version": "1"},
        "paths": {
            "/x": {
                "get": {
                    "parameters": [{"name": "email", "in": "query"}],
                    "responses": {"204": {"description": "no content"}},
                }
            }
        },
    }
    out = analyze_openapi(spec)
    assert len(out["endpoints"]) >= 1
    ep = out["endpoints"][0]
    assert any(p["field"] == "email" for p in ep["parameters_sensitive"])
