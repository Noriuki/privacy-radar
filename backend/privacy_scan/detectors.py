"""Sensitive data pattern detectors for LGPD/GDPR compliance."""

import re
from typing import Any

from app.domain.entities import SensitiveField


PATTERNS = {
    "email": re.compile(
        r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
        re.IGNORECASE,
    ),
    "phone": re.compile(
        r"^[\+]?[(]?[0-9]{2,3}[)]?[-\s\.]?[0-9]{4,5}[-\s\.]?[0-9]{4,5}$"
    ),
    "cpf": re.compile(r"^\d{3}\.?\d{3}\.?\d{3}-?\d{2}$"),
    "cnpj": re.compile(r"^\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}$"),
    "address": re.compile(
        r".*(rua|avenida|av\.?|r\.?|street|st\.?|alameda|travessa|number|nº|n°|\d{4,5}).*",
        re.IGNORECASE,
    ),
    "cep": re.compile(r"^\d{5}-?\d{3}$"),
    "rg": re.compile(r"^\d{1,2}\.?\d{3}\.?\d{3}-?[\dXx]$"),
    "date_of_birth": re.compile(r"^\d{4}-\d{2}-\d{2}$|^\d{2}/\d{2}/\d{4}$"),
    "ip_address": re.compile(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$"),
    "credit_card": re.compile(r"^\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}$"),
}

FIELD_HINTS = {
    "email": ["email", "e-mail", "email_address", "mail"],
    "phone": ["phone", "telefone", "celular", "mobile", "telephone", "phone_number"],
    "cpf": ["cpf", "document", "documento", "tax_id"],
    "cnpj": ["cnpj", "company_document"],
    "address": ["address", "endereco", "street", "rua", "logradouro", "complement", "city", "cidade"],
    "cep": ["cep", "zip", "zipcode", "postal_code"],
    "rg": ["rg", "identity", "identidade"],
    "date_of_birth": ["birth_date", "dob", "data_nascimento", "birthday", "date_of_birth"],
    "name": ["name", "nome", "full_name", "first_name", "last_name", "nome_completo"],
    "ip_address": ["ip", "ip_address", "client_ip"],
    "credit_card": ["credit_card", "card_number", "numero_cartao"],
}


def _key_matches_hint(key: str, hint_type: str) -> bool:
    key_lower = key.lower().replace("-", "_").replace(" ", "_")
    return key_lower in (h.lower() for h in FIELD_HINTS.get(hint_type, []))


def _matches_pattern(value: Any, pattern_type: str) -> bool:
    if not isinstance(value, str):
        value = str(value) if value is not None else ""
    pattern = PATTERNS.get(pattern_type)
    if not pattern:
        return False
    return bool(pattern.match(value.strip()))


def _detect_field_type(key: str, value: Any) -> str | None:
    for pattern_type, hints in FIELD_HINTS.items():
        if _key_matches_hint(key, pattern_type):
            if pattern_type in PATTERNS and value is not None:
                if _matches_pattern(value, pattern_type):
                    return pattern_type
            return pattern_type
    for pattern_type in PATTERNS:
        if value is not None and _matches_pattern(value, pattern_type):
            return pattern_type
    return None


def _flatten_payload(obj: Any, prefix: str = "") -> list[tuple[str, str, Any]]:
    out: list[tuple[str, str, Any]] = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            path = f"{prefix}.{k}" if prefix else k
            if isinstance(v, (dict, list)):
                out.extend(_flatten_payload(v, path))
            else:
                out.append((path, k, v))
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            path = f"{prefix}[{i}]"
            if isinstance(item, (dict, list)):
                out.extend(_flatten_payload(item, path))
            else:
                out.append((path, f"[{i}]", item))
    return out


def detect_sensitive_fields(payload: dict[str, Any]) -> list[SensitiveField]:
    sensitive: list[SensitiveField] = []
    for path, key, value in _flatten_payload(payload):
        detected_type = _detect_field_type(key, value)
        if detected_type:
            sample = str(value)[:50] + ("..." if len(str(value)) > 50 else "") if value is not None else None
            sensitive.append(
                SensitiveField(
                    field_path=path,
                    field_name=key,
                    pattern_type=detected_type,
                    sample_value=sample,
                )
            )
    return sensitive
