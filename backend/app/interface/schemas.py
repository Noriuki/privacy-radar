"""Pydantic schemas for API request/response."""

from pydantic import BaseModel, Field


class GapItem(BaseModel):
    """LGPD gap with article reference."""

    article: str
    title: str
    gap: str


class LgpdChecklistSubmitRequest(BaseModel):
    """Answers: question id -> selected option value."""

    answers: dict[str, str] = Field(..., description="Map of question id to answer value")


class LgpdChecklistReportResponse(BaseModel):
    """Result of LGPD checklist evaluation."""

    score: float
    maturity: str
    gaps: list[GapItem]
    recommendations: list[str]
    disclaimer: str


class ContractSummary(BaseModel):
    """Summary block for OpenAPI analysis."""

    total_operations_with_schema: int = 0
    operations_with_personal_data_fields: int = 0
    operations_with_sensitive_data_and_no_security_doc: int = 0


class OpenAPIContractResponse(BaseModel):
    """OpenAPI contract surface analysis."""

    openapi_version: str | None = None
    title: str | None = None
    endpoints: list[dict] = Field(default_factory=list)
    summary: dict = Field(default_factory=dict)
    recommendations: list[str] = Field(default_factory=list)
    error: str | None = None


class GraphQLContractResponse(BaseModel):
    """GraphQL schema surface analysis."""

    graphql: bool = True
    types_with_personal_data_hints: list[dict] = Field(default_factory=list)
    summary: dict = Field(default_factory=dict)
    recommendations: list[str] = Field(default_factory=list)
    error: str | None = None
