"""Field-name heuristics for personal data (used in contract / schema analysis)."""

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


def sensitive_types_for_field_name(key: str) -> list[str]:
    """Return sensitive data types that match a field name (for OpenAPI / GraphQL analysis)."""
    types: list[str] = []
    for pattern_type in FIELD_HINTS:
        if _key_matches_hint(key, pattern_type):
            types.append(pattern_type)
    return types
