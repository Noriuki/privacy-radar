"""API routes — LGPD checklist + OpenAPI/GraphQL contract analysis only."""

from typing import Any

from fastapi import APIRouter, HTTPException, Request

from app.interface.rate_limit import get_retry_after, is_rate_limited
from app.interface.schemas import (
    GraphQLContractResponse,
    LgpdChecklistReportResponse,
    LgpdChecklistSubmitRequest,
    OpenAPIContractResponse,
)
from privacy_scan.lgpd_checklist import QUESTIONS, evaluate_checklist
from privacy_scan.openapi_surface import analyze_graphql, analyze_openapi

router = APIRouter(tags=["privacy-radar"])


@router.get("/lgpd/questions")
def lgpd_questions():
    """Return the guided LGPD checklist (questions and options)."""
    return {"questions": QUESTIONS, "version": 1}


@router.post("/lgpd/submit", response_model=LgpdChecklistReportResponse)
def lgpd_submit(request: Request, body: LgpdChecklistSubmitRequest) -> LgpdChecklistReportResponse:
    """Submit checklist answers and receive maturity score, gaps (with LGPD articles), recommendations."""
    ip = request.client.host if request.client else "unknown"
    if is_rate_limited(ip):
        retry = get_retry_after(ip)
        raise HTTPException(
            status_code=429,
            detail="Too many requests. Try again later.",
            headers={"Retry-After": str(retry)},
        )
    answers = body.answers
    required = {q["id"] for q in QUESTIONS}
    missing = required - set(answers.keys())
    if missing:
        raise HTTPException(status_code=400, detail=f"Missing answers for: {sorted(missing)}")
    result = evaluate_checklist(answers)
    return LgpdChecklistReportResponse(
        score=result["score"],
        maturity=result["maturity"],
        gaps=[{"article": g["article"], "title": g["title"], "gap": g["gap"]} for g in result["gaps"]],
        recommendations=result["recommendations"],
        disclaimer=result["disclaimer"],
    )


@router.post("/contract/openapi", response_model=OpenAPIContractResponse)
def contract_openapi(request: Request, spec: dict[str, Any]) -> OpenAPIContractResponse:
    """Analyze an OpenAPI 3.x (or Swagger) JSON document — per-endpoint personal data surface map."""
    ip = request.client.host if request.client else "unknown"
    if is_rate_limited(ip):
        retry = get_retry_after(ip)
        raise HTTPException(status_code=429, detail="Too many requests.", headers={"Retry-After": str(retry)})
    out = analyze_openapi(spec)
    if out.get("error"):
        return OpenAPIContractResponse(error=out["error"], endpoints=[], summary={}, recommendations=[])
    return OpenAPIContractResponse(
        openapi_version=out.get("openapi_version"),
        title=out.get("title"),
        endpoints=out.get("endpoints") or [],
        summary=out.get("summary") or {},
        recommendations=out.get("recommendations") or [],
    )


@router.post("/contract/graphql", response_model=GraphQLContractResponse)
def contract_graphql(request: Request, schema_doc: dict[str, Any]) -> GraphQLContractResponse:
    """Analyze GraphQL introspection JSON — types/fields that may expose personal data (name heuristics)."""
    ip = request.client.host if request.client else "unknown"
    if is_rate_limited(ip):
        retry = get_retry_after(ip)
        raise HTTPException(status_code=429, detail="Too many requests.", headers={"Retry-After": str(retry)})
    out = analyze_graphql(schema_doc)
    if out.get("error"):
        return GraphQLContractResponse(error=out["error"], types_with_personal_data_hints=[], summary={}, recommendations=[])
    return GraphQLContractResponse(
        types_with_personal_data_hints=out.get("types_with_personal_data_hints") or [],
        summary=out.get("summary") or {},
        recommendations=out.get("recommendations") or [],
    )
