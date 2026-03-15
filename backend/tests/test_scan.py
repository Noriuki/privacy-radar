"""Tests for scan use case and detection engine."""

import pytest

from app.infrastructure.detection_engine import RuleBasedDetectionEngine


@pytest.fixture
def engine() -> RuleBasedDetectionEngine:
    return RuleBasedDetectionEngine()


def test_scan_detects_email_and_phone(engine: RuleBasedDetectionEngine) -> None:
    payload = {
        "email": "user@email.com",
        "name": "John Doe",
        "phone": "+551199999999",
    }
    result = engine.scan_payload(payload)
    types = {f.pattern_type for f in result.sensitive_fields}
    assert "email" in types
    assert "phone" in types
    assert "name" in types
    assert result.risk_level.value in ("low", "medium", "high", "critical")
    assert 0 <= result.score <= 100


def test_scan_detects_cpf(engine: RuleBasedDetectionEngine) -> None:
    payload = {"cpf": "123.456.789-00"}
    result = engine.scan_payload(payload)
    assert any(f.pattern_type == "cpf" for f in result.sensitive_fields)


def test_scan_empty_payload(engine: RuleBasedDetectionEngine) -> None:
    result = engine.scan_payload({})
    assert len(result.sensitive_fields) == 0
    assert result.risk_level.value == "low"
    assert result.score == 0
