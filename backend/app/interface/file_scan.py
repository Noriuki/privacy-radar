"""File and API schema scanning utilities."""

import json
from pathlib import Path
from typing import Any

from app.infrastructure.detection_engine import RuleBasedDetectionEngine


def scan_json_file(file_path: Path) -> tuple[dict[str, Any] | None, Any]:
    """
    Load JSON from file and run privacy scan.
    Returns (payload, scan_result) or (None, None) on error.
    """
    try:
        payload = json.loads(file_path.read_text())
    except (OSError, json.JSONDecodeError):
        return None, None
    if not isinstance(payload, dict):
        return None, None
    engine = RuleBasedDetectionEngine()
    return payload, engine.scan_payload(payload)


def scan_directory(dir_path: Path, pattern: str = "*.json") -> list[tuple[Path, Any]]:
    """
    Scan all JSON files in a directory.
    Returns list of (path, scan_result) for each file.
    """
    results = []
    for path in dir_path.rglob(pattern):
        if not path.is_file():
            continue
        _, result = scan_json_file(path)
        if result is not None:
            results.append((path, result))
    return results


def scan_openapi_schema(schema: dict[str, Any]) -> Any:
    """
    Scan an OpenAPI schema for request/response bodies that may contain
    sensitive field names (e.g. email, phone in properties).
    Returns a ScanResult based on detected property names and examples.
    """
    engine = RuleBasedDetectionEngine()
    payload: dict[str, Any] = {}
    paths = schema.get("paths", {})
    for path_spec in paths.values():
        for method_spec in path_spec.values():
            if not isinstance(method_spec, dict):
                continue
            for content_key, content_spec in method_spec.get("requestBody", {}).get("content", {}).items():
                if "application/json" not in content_key and "json" not in content_key:
                    continue
                schema_ref = content_spec.get("schema", {})
                _merge_schema_into_payload(schema_ref, schema, payload)
            for code, response in method_spec.get("responses", {}).items():
                for content_key, content_spec in response.get("content", {}).items():
                    if "application/json" not in content_key and "json" not in content_key:
                        continue
                    schema_ref = content_spec.get("schema", {})
                    _merge_schema_into_payload(schema_ref, schema, payload)
    if not payload:
        payload = schema.get("components", {}).get("schemas", {})
        if isinstance(payload, dict):
            for first in payload.values():
                if isinstance(first, dict) and "properties" in first:
                    payload = first.get("properties", {})
                    break
    return engine.scan_payload(payload)


def _merge_schema_into_payload(
    schema_ref: dict,
    root_schema: dict,
    out: dict[str, Any],
) -> None:
    if "$ref" in schema_ref:
        ref = schema_ref["$ref"]
        if ref.startswith("#/components/schemas/"):
            name = ref.split("/")[-1]
            schema_ref = root_schema.get("components", {}).get("schemas", {}).get(name, {})
    props = schema_ref.get("properties", {})
    for key, prop_spec in props.items():
        if key in out:
            continue
        if "example" in prop_spec:
            out[key] = prop_spec["example"]
        elif "default" in prop_spec:
            out[key] = prop_spec["default"]
        else:
            out[key] = _example_for_type(prop_spec.get("type"), prop_spec.get("format"))


def _example_for_type(typ: str | None, fmt: str | None) -> str:
    if typ == "string":
        if fmt == "email":
            return "user@example.com"
        if fmt == "phone":
            return "+5511999999999"
        return "string"
    if typ == "integer" or typ == "number":
        return 0
    return ""
