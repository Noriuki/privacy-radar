"""In-memory scan statistics for observability demo."""

from collections import defaultdict
from time import time

_total_scans = 0
_by_risk_level = defaultdict(int)


def record_scan(risk_level: str) -> None:
    global _total_scans
    _total_scans += 1
    _by_risk_level[risk_level] += 1


def get_stats() -> dict:
    return {
        "total_scans": _total_scans,
        "by_risk_level": dict(_by_risk_level),
    }
