"""Domain entities for privacy scanning."""

from enum import Enum
from typing import Optional


class RiskLevel(str, Enum):
    """Privacy risk severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SensitiveField:
    """Represents a detected sensitive data field."""

    def __init__(
        self,
        field_path: str,
        field_name: str,
        pattern_type: str,
        sample_value: Optional[str] = None,
    ):
        self.field_path = field_path
        self.field_name = field_name
        self.pattern_type = pattern_type
        self.sample_value = sample_value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SensitiveField):
            return False
        return (
            self.field_path == other.field_path
            and self.field_name == other.field_name
            and self.pattern_type == other.pattern_type
        )


class PrivacyRisk:
    """Represents a privacy risk finding with recommendation."""

    def __init__(
        self,
        code: str,
        description: str,
        recommendation: str,
        severity: RiskLevel,
    ):
        self.code = code
        self.description = description
        self.recommendation = recommendation
        self.severity = severity


class ScanResult:
    """Result of a privacy scan over a payload."""

    def __init__(
        self,
        sensitive_fields: list[SensitiveField],
        risks: list[PrivacyRisk],
        risk_level: RiskLevel,
        score: float,
    ):
        self.sensitive_fields = sensitive_fields
        self.risks = risks
        self.risk_level = risk_level
        self.score = score
