"""CLI — PrivacyRadar is API-first (LGPD checklist + contract analysis)."""

import sys


def main() -> int:
    print("PrivacyRadar: use a API REST ou o frontend.")
    print("  Docs: http://localhost:8000/docs")
    print("  Endpoints: GET /api/v1/lgpd/questions, POST /api/v1/lgpd/submit")
    print("             POST /api/v1/contract/openapi, POST /api/v1/contract/graphql")
    return 0


if __name__ == "__main__":
    sys.exit(main())
