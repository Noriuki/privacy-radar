"""CLI scanner for PrivacyRadar."""

import json
import sys
from pathlib import Path

from app.infrastructure.detection_engine import RuleBasedDetectionEngine


def _format_report(result) -> str:
    lines = [
        "",
        "=== Privacy Radar Report ===",
        "",
        "Sensitive Fields Detected:",
    ]
    for f in result.sensitive_fields:
        sample = f" (sample: {f.sample_value})" if f.sample_value else ""
        lines.append(f"  • {f.field_name} ({f.pattern_type}){sample}")
    lines.extend([
        "",
        f"Risk Level: {result.risk_level.value.title()}",
        f"Risk Score: {result.score}/100",
        "",
        "Recommendations:",
    ])
    seen = set()
    for r in result.risks:
        if r.recommendation not in seen:
            seen.add(r.recommendation)
            lines.append(f"  • {r.recommendation}")
    if not seen:
        lines.append("  • Review payload for unnecessary personal data; implement retention policy.")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    """CLI entrypoint. Usage: privacy-radar [file.json] or echo '{}' | privacy-radar"""
    args = sys.argv[1:]
    if not args:
        try:
            payload = json.load(sys.stdin)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON - {e}", file=sys.stderr)
            return 1
        if not isinstance(payload, dict):
            print("Error: Root must be a JSON object", file=sys.stderr)
            return 1
        engine = RuleBasedDetectionEngine()
        result = engine.scan_payload(payload)
        print(_format_report(result))
        return 0
    if args[0] in ("-h", "--help"):
        print("Usage: privacy-radar [file.json]")
        print("  With no args: read JSON from stdin and print privacy report.")
        print("  With file: scan file and print report.")
        return 0
    path = Path(args[0])
    if not path.exists():
        print(f"Error: File not found: {path}", file=sys.stderr)
        return 1
    try:
        payload = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    if not isinstance(payload, dict):
        print("Error: Root must be a JSON object", file=sys.stderr)
        return 1
    engine = RuleBasedDetectionEngine()
    result = engine.scan_payload(payload)
    print(f"File: {path}")
    print(_format_report(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
