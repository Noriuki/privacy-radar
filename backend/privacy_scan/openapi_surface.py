"""OpenAPI contract surface analysis — per-endpoint personal data exposure map."""

from __future__ import annotations

from typing import Any

from privacy_scan.detectors import sensitive_types_for_field_name


def _resolve_ref(root: dict[str, Any], ref: str, visited: set[str]) -> dict[str, Any] | None:
    if not ref.startswith("#/"):
        return None
    if ref in visited:
        return None
    visited.add(ref)
    parts = ref.replace("#/", "").split("/")
    cur: Any = root
    for p in parts:
        if not isinstance(cur, dict) or p not in cur:
            return None
        cur = cur[p]
    return cur if isinstance(cur, dict) else None


def _collect_field_names(
    schema: dict[str, Any],
    root: dict[str, Any],
    visited_refs: set[str],
    prefix: str = "",
) -> list[str]:
    """Collect leaf field names from a JSON Schema object."""
    names: list[str] = []
    if not isinstance(schema, dict):
        return names
    if "$ref" in schema:
        resolved = _resolve_ref(root, schema["$ref"], visited_refs)
        if resolved:
            names.extend(_collect_field_names(resolved, root, visited_refs, prefix))
        return names
    if "allOf" in schema:
        for sub in schema["allOf"]:
            if isinstance(sub, dict):
                names.extend(_collect_field_names(sub, root, visited_refs, prefix))
        return names
    props = schema.get("properties")
    if isinstance(props, dict):
        for key, sub in props.items():
            path = f"{prefix}.{key}" if prefix else key
            names.append(key)
            if isinstance(sub, dict):
                names.extend(_collect_field_names(sub, root, visited_refs, path))
    items = schema.get("items")
    if isinstance(items, dict):
        names.extend(_collect_field_names(items, root, visited_refs, prefix))
    return names


def _sensitive_from_names(names: list[str]) -> list[dict[str, Any]]:
    """Map field names to sensitive types (dedupe)."""
    seen: set[tuple[str, str]] = set()
    out: list[dict[str, Any]] = []
    for name in names:
        for st in sensitive_types_for_field_name(name):
            key = (name, st)
            if key not in seen:
                seen.add(key)
                out.append({"field": name, "type": st})
    return out


def analyze_openapi(spec: dict[str, Any]) -> dict[str, Any]:
    """
    Walk OpenAPI 3.x document and build a per-operation surface map of
    fields that may carry personal data (by field name heuristics).
    """
    if not isinstance(spec, dict):
        return {"error": "Invalid OpenAPI document", "endpoints": [], "summary": {}}

    paths = spec.get("paths") or {}
    components = spec.get("components") or {}
    root = {**spec, "components": components}
    endpoints: list[dict[str, Any]] = []

    http_methods = ("get", "post", "put", "patch", "delete", "options", "head", "trace")

    for path_key, path_item in paths.items():
        if not isinstance(path_item, dict):
            continue
        for method in http_methods:
            op = path_item.get(method)
            if not isinstance(op, dict):
                continue
            visited: set[str] = set()
            param_names: list[str] = []
            for p in op.get("parameters") or []:
                if isinstance(p, dict) and p.get("name"):
                    param_names.append(p["name"])

            body_names: list[str] = []
            rb = op.get("requestBody")
            if isinstance(rb, dict):
                for _ct, content in (rb.get("content") or {}).items():
                    if not isinstance(content, dict):
                        continue
                    sch = content.get("schema")
                    if isinstance(sch, dict):
                        body_names.extend(_collect_field_names(sch, root, visited))

            response_names: list[str] = []
            for _code, resp in (op.get("responses") or {}).items():
                if not isinstance(resp, dict):
                    continue
                for _ct, content in (resp.get("content") or {}).items():
                    if not isinstance(content, dict):
                        continue
                    sch = content.get("schema")
                    if isinstance(sch, dict):
                        response_names.extend(_collect_field_names(sch, root, set()))

            sec = op.get("security") or path_item.get("security") or spec.get("security")
            has_security = bool(sec)

            sens_params = _sensitive_from_names(param_names)
            sens_body = _sensitive_from_names(body_names)
            sens_resp = _sensitive_from_names(response_names)

            if sens_params or sens_body or sens_resp or param_names or body_names or response_names:
                endpoints.append(
                    {
                        "path": path_key,
                        "method": method.upper(),
                        "security_documented": has_security,
                        "parameters_sensitive": sens_params,
                        "request_body_sensitive": sens_body,
                        "response_sensitive": sens_resp,
                        "parameter_names": param_names,
                        "request_field_sample": list(dict.fromkeys(body_names))[:30],
                        "response_field_sample": list(dict.fromkeys(response_names))[:30],
                    }
                )

    exposed = sum(1 for e in endpoints if e["parameters_sensitive"] or e["request_body_sensitive"] or e["response_sensitive"])
    without_sec = sum(1 for e in endpoints if not e["security_documented"] and (e["parameters_sensitive"] or e["request_body_sensitive"] or e["response_sensitive"]))

    return {
        "openapi_version": spec.get("openapi") or spec.get("swagger"),
        "title": (spec.get("info") or {}).get("title"),
        "endpoints": endpoints,
        "summary": {
            "total_operations_with_schema": len(endpoints),
            "operations_with_personal_data_fields": exposed,
            "operations_with_sensitive_data_and_no_security_doc": without_sec,
        },
        "recommendations": _contract_recommendations(endpoints, without_sec),
    }


def _contract_recommendations(endpoints: list[dict[str, Any]], without_sec: int) -> list[str]:
    recs = []
    if without_sec > 0:
        recs.append(
            f"Há {without_sec} operação(ões) com campos potencialmente pessoais e sem esquema de segurança explícito na operação — revise autenticação e documentação (Art. 46 LGPD — segurança).",
        )
    if any(e["request_body_sensitive"] or e["parameters_sensitive"] for e in endpoints):
        recs.append(
            "Minimize coleta: avalie se todos os campos pessoais em request são necessários à finalidade (Art. 6º, III — minimização).",
        )
    if any(e["response_sensitive"] for e in endpoints):
        recs.append(
            "Respostas com dados pessoais: considere paginação, filtro de campos e controle de acesso por perfil.",
        )
    if not recs:
        recs.append("Nenhum campo com nome heurístico de dado pessoal encontrado nas operações analisadas — valide com o time de negócio.")
    return recs


def analyze_graphql(schema_doc: dict[str, Any]) -> dict[str, Any]:
    """
    Analyze GraphQL introspection result or a simplified schema dump.
    Expects: { "data": { "__schema": { "types": [...] } } } } or { "__schema": {...} }.
    """
    schema = schema_doc.get("data", schema_doc) if isinstance(schema_doc, dict) else {}
    inner = schema.get("__schema") or schema_doc.get("__schema")
    if not isinstance(inner, dict):
        return {"error": "Schema GraphQL inválido: falta __schema.types", "types": [], "summary": {}}

    types_list = inner.get("types") or []
    findings: list[dict[str, Any]] = []

    for t in types_list:
        if not isinstance(t, dict):
            continue
        name = t.get("name") or ""
        if name.startswith("__"):
            continue
        kind = t.get("kind")
        if kind != "OBJECT":
            continue
        fields = t.get("fields") or []
        sensitive_fields: list[dict[str, str]] = []
        for f in fields:
            if not isinstance(f, dict):
                continue
            fname = f.get("name") or ""
            for st in sensitive_types_for_field_name(fname):
                sensitive_fields.append({"field": fname, "type": st})
        if sensitive_fields:
            findings.append({"type_name": name, "sensitive_fields": sensitive_fields})

    return {
        "graphql": True,
        "types_with_personal_data_hints": findings,
        "summary": {
            "object_types_scanned": sum(1 for t in types_list if isinstance(t, dict) and t.get("kind") == "OBJECT" and not str(t.get("name", "")).startswith("__")),
            "types_with_flagged_fields": len(findings),
        },
        "recommendations": [
            "Revise resolvers e permissões para tipos que expõem dados pessoais.",
            "Considere paginação e limites em listagens que retornam titulares.",
        ]
        if findings
        else ["Nenhum nome de campo heurístico de dado pessoal encontrado nos tipos OBJECT."],
    }
