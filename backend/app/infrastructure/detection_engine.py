"""Rule-based detection engine - adapter implementing DetectionEngineInterface."""

from typing import Any

from app.application.interfaces import DetectionEngineInterface
from app.domain.entities import ScanResult
from privacy_scan.detectors import detect_sensitive_fields
from privacy_scan.risk_scoring import calculate_risk_score
from privacy_scan.rules import get_privacy_risks


class RuleBasedDetectionEngine(DetectionEngineInterface):
    """Concrete detection engine using privacy_scan detectors and rules."""

    def scan_payload(self, payload: dict[str, Any]) -> ScanResult:
        sensitive_fields = detect_sensitive_fields(payload)
        risks = get_privacy_risks(sensitive_fields)
        score, risk_level = calculate_risk_score(sensitive_fields, risks)
        return ScanResult(
            sensitive_fields=sensitive_fields,
            risks=risks,
            risk_level=risk_level,
            score=score,
        )
