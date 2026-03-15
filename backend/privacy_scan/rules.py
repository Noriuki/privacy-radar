"""Privacy risk rules based on LGPD/GDPR principles."""

from app.domain.entities import PrivacyRisk, RiskLevel, SensitiveField


def get_privacy_risks(sensitive_fields: list[SensitiveField]) -> list[PrivacyRisk]:
    risks: list[PrivacyRisk] = []
    types = {f.pattern_type for f in sensitive_fields}

    if not sensitive_fields:
        return risks

    if "cpf" in types or "rg" in types or "cnpj" in types:
        risks.append(
            PrivacyRisk(
                code="LGPD-IDENTIFIER",
                description="Personal or company identifiers (CPF/RG/CNPJ) detected.",
                recommendation="Store only when strictly necessary; prefer hashing or tokenization.",
                severity=RiskLevel.HIGH,
            )
        )

    if "credit_card" in types:
        risks.append(
            PrivacyRisk(
                code="PCI-SENSITIVE",
                description="Credit card data detected.",
                recommendation="Never store raw card numbers; use PCI-compliant tokenization.",
                severity=RiskLevel.CRITICAL,
            )
        )

    if "email" in types or "phone" in types:
        risks.append(
            PrivacyRisk(
                code="LGPD-CONTACT",
                description="Contact data (email/phone) detected.",
                recommendation="Encrypt personal data at rest; implement retention policy.",
                severity=RiskLevel.MEDIUM,
            )
        )

    if "address" in types or "cep" in types:
        risks.append(
            PrivacyRisk(
                code="LGPD-LOCATION",
                description="Address or location data detected.",
                recommendation="Minimize collection; encrypt and define retention period.",
                severity=RiskLevel.MEDIUM,
            )
        )

    if "name" in types or "date_of_birth" in types:
        risks.append(
            PrivacyRisk(
                code="GDPR-PII",
                description="Direct identifiers or date of birth detected.",
                recommendation="Ensure lawful basis and consent; implement data minimization.",
                severity=RiskLevel.MEDIUM,
            )
        )

    if "ip_address" in types:
        risks.append(
            PrivacyRisk(
                code="GDPR-IP",
                description="IP address detected (personal data under GDPR).",
                recommendation="Anonymize or pseudonymize; document legal basis.",
                severity=RiskLevel.MEDIUM,
            )
        )

    risks.append(
        PrivacyRisk(
            code="LGPD-BASELINE",
            description="Personal data present in payload.",
            recommendation="Encrypt personal data; implement retention policy; document purpose.",
            severity=RiskLevel.LOW,
        )
    )

    return risks
