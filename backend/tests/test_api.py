"""Tests for FastAPI — LGPD checklist + contract analysis."""

import pytest
from fastapi.testclient import TestClient

from app.interface.api import app

client = TestClient(app)

MINIMAL_ANSWERS = {
    "dados_clareza": "nao",
    "fora_brasil": "nao",
    "seguranca": "sim",
    "exclusao": "sim",
    "incidente": "sim",
}

MINIMAL_OPENAPI = {
    "openapi": "3.0.0",
    "info": {"title": "Test API", "version": "1"},
    "paths": {
        "/users": {
            "get": {
                "parameters": [{"name": "email", "in": "query", "schema": {"type": "string"}}],
                "responses": {
                    "200": {
                        "description": "ok",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {"name": {"type": "string"}},
                                }
                            }
                        },
                    }
                },
            }
        }
    },
}


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_lgpd_questions() -> None:
    response = client.get("/api/v1/lgpd/questions")
    assert response.status_code == 200
    data = response.json()
    assert "questions" in data
    assert len(data["questions"]) == 5


def test_lgpd_submit() -> None:
    response = client.post("/api/v1/lgpd/submit", json={"answers": MINIMAL_ANSWERS})
    assert response.status_code == 200
    data = response.json()
    assert "score" in data
    assert "maturity" in data
    assert "gaps" in data
    assert "recommendations" in data
    assert "disclaimer" in data


def test_lgpd_submit_missing_answers() -> None:
    response = client.post("/api/v1/lgpd/submit", json={"answers": {"dados_clareza": "nao"}})
    assert response.status_code == 400


def test_contract_openapi() -> None:
    response = client.post("/api/v1/contract/openapi", json=MINIMAL_OPENAPI)
    assert response.status_code == 200
    data = response.json()
    assert "endpoints" in data
    assert "summary" in data
    assert data.get("title") == "Test API"


def test_contract_graphql_empty() -> None:
    response = client.post("/api/v1/contract/graphql", json={})
    assert response.status_code == 200
    data = response.json()
    assert "error" in data or "summary" in data
