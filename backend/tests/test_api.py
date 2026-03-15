"""Tests for FastAPI scan endpoint."""

import pytest
from fastapi.testclient import TestClient

from app.interface.api import app

client = TestClient(app)


def test_scan_returns_report() -> None:
    response = client.post(
        "/api/v1/scan",
        json={
            "email": "user@email.com",
            "name": "John Doe",
            "phone": "+551199999999",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "sensitive_fields" in data
    assert "risk_level" in data
    assert "score" in data
    assert "recommendations" in data
    types = {f["pattern_type"] for f in data["sensitive_fields"]}
    assert "email" in types
    assert "phone" in types
    assert data["risk_level"] == "medium"


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_stats_returns_aggregates() -> None:
    response = client.get("/api/v1/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_scans" in data
    assert "by_risk_level" in data
    assert isinstance(data["total_scans"], int)
    assert isinstance(data["by_risk_level"], dict)
