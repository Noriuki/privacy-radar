"""API routes for scan endpoints."""

import json
from typing import Any

from fastapi import APIRouter, File, HTTPException, Request, UploadFile

from app.application.scan_use_case import ScanPayloadUseCase
from app.infrastructure.detection_engine import RuleBasedDetectionEngine
from app.interface.file_scan import scan_openapi_schema
from app.interface.rate_limit import get_retry_after, is_rate_limited
from app.interface.schemas import RiskResponse, ScanResponse, SensitiveFieldResponse
from app.interface.stats import get_stats, record_scan

router = APIRouter(tags=["scan"])

_engine = RuleBasedDetectionEngine()
_scan_use_case = ScanPayloadUseCase(_engine)


def _build_recommendations(risks: list) -> list[str]:
    seen = set()
    recs = []
    for r in risks:
        if r.recommendation and r.recommendation not in seen:
            seen.add(r.recommendation)
            recs.append(r.recommendation)
    if not recs:
        recs = ["Review payload for unnecessary personal data; implement retention policy."]
    return recs


def _result_to_response(result):
    return ScanResponse(
        sensitive_fields=[
            SensitiveFieldResponse(
                field_path=f.field_path,
                field_name=f.field_name,
                pattern_type=f.pattern_type,
                sample_value=f.sample_value,
            )
            for f in result.sensitive_fields
        ],
        risks=[
            RiskResponse(
                code=r.code,
                description=r.description,
                recommendation=r.recommendation,
                severity=r.severity,
            )
            for r in result.risks
        ],
        risk_level=result.risk_level,
        score=result.score,
        recommendations=_build_recommendations(result.risks),
    )


@router.get("/stats")
def stats():
    """Return scan statistics (total, by risk level). Useful for dashboards and observability."""
    return get_stats()


@router.post("/scan", response_model=ScanResponse)
def scan_payload(request: Request, payload: dict[str, Any]) -> ScanResponse:
    """
    Scan a JSON payload for sensitive data and privacy risks.
    Send the JSON body directly (e.g. {"email": "...", "name": "...", "phone": "..."}).
    Rate limited to 30 requests per minute per IP.
    """
    ip = request.client.host if request.client else "unknown"
    if is_rate_limited(ip):
        retry = get_retry_after(ip)
        raise HTTPException(
            status_code=429,
            detail="Too many requests. Try again later.",
            headers={"Retry-After": str(retry)},
        )
    try:
        result = _scan_use_case.execute(payload)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    record_scan(result.risk_level.value)
    return _result_to_response(result)


@router.post("/scan/file", response_model=ScanResponse)
def scan_file_upload(request: Request, file: UploadFile = File(...)) -> ScanResponse:
    """Scan a JSON file upload (multipart form, key "file"). Rate limited."""
    ip = request.client.host if request.client else "unknown"
    if is_rate_limited(ip):
        retry = get_retry_after(ip)
        raise HTTPException(status_code=429, detail="Too many requests.", headers={"Retry-After": str(retry)})
    try:
        content = file.file.read()
        payload = json.loads(content.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON file: {e}") from e
    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="JSON root must be an object")
    result = _scan_use_case.execute(payload)
    record_scan(result.risk_level.value)
    return _result_to_response(result)


@router.post("/scan/schema", response_model=ScanResponse)
def scan_schema(request: Request, schema: dict[str, Any]) -> ScanResponse:
    """Scan an OpenAPI/JSON Schema document for sensitive field names. Rate limited."""
    ip = request.client.host if request.client else "unknown"
    if is_rate_limited(ip):
        retry = get_retry_after(ip)
        raise HTTPException(status_code=429, detail="Too many requests.", headers={"Retry-After": str(retry)})
    try:
        result = scan_openapi_schema(schema)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    record_scan(result.risk_level.value)
    return _result_to_response(result)
