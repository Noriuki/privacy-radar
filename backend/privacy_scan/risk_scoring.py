"""Risk scoring for privacy scan results."""

from app.domain.entities import RiskLevel, SensitiveField, PrivacyRisk


TYPE_WEIGHTS = {
    "credit_card": 40,
    "cpf": 25,
    "rg": 25,
    "cnpj": 20,
    "date_of_birth": 15,
    "address": 12,
    "cep": 10,
    "email": 10,
    "phone": 10,
    "name": 8,
    "ip_address": 8,
    "default": 5,
}


def _score_from_fields(fields: list[SensitiveField]) -> float:
    total = 0.0
    for f in fields:
        total += TYPE_WEIGHTS.get(f.pattern_type, TYPE_WEIGHTS["default"])
    return min(100.0, total)


def _level_from_score(score: float) -> RiskLevel:
    if score >= 70:
        return RiskLevel.CRITICAL
    if score >= 45:
        return RiskLevel.HIGH
    if score >= 20:
        return RiskLevel.MEDIUM
    return RiskLevel.LOW


def calculate_risk_score(
    sensitive_fields: list[SensitiveField],
    risks: list[PrivacyRisk],
) -> tuple[float, RiskLevel]:
    score = _score_from_fields(sensitive_fields)
    if risks:
        severity_boost = {
            RiskLevel.CRITICAL: 25,
            RiskLevel.HIGH: 15,
            RiskLevel.MEDIUM: 5,
            RiskLevel.LOW: 0,
        }
        max_severity = max(r.severity for r in risks)
        score = min(100.0, score + severity_boost.get(max_severity, 0))
    level = _level_from_score(score)
    return round(score, 1), level
