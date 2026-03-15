"""Pydantic schemas for API request/response."""

from pydantic import BaseModel, ConfigDict, Field

from app.domain.entities import RiskLevel


class SensitiveFieldResponse(BaseModel):
    """A detected sensitive field in the report."""

    field_path: str
    field_name: str
    pattern_type: str
    sample_value: str | None = None


class RiskResponse(BaseModel):
    """A privacy risk with recommendation."""

    code: str
    description: str
    recommendation: str
    severity: RiskLevel


class ScanResponse(BaseModel):
    """Privacy scan report response."""

    model_config = ConfigDict(use_enum_values=True)

    sensitive_fields: list[SensitiveFieldResponse]
    risks: list[RiskResponse]
    risk_level: RiskLevel
    score: float
    recommendations: list[str] = Field(default_factory=list)
