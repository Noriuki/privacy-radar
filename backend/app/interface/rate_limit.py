"""Simple in-memory rate limiter (per IP)."""

from collections import defaultdict
from time import time

# ip -> list of request timestamps (last 60 seconds)
_requests: dict[str, list[float]] = defaultdict(list)
LIMIT = 30
WINDOW_SEC = 60


def _clean_old(now: float, timestamps: list[float]) -> None:
    cutoff = now - WINDOW_SEC
    while timestamps and timestamps[0] < cutoff:
        timestamps.pop(0)


def is_rate_limited(ip: str) -> bool:
    """Return True if IP is over the limit (do not count this request)."""
    now = time()
    _clean_old(now, _requests[ip])
    if len(_requests[ip]) >= LIMIT:
        return True
    _requests[ip].append(now)
    return False


def get_retry_after(ip: str) -> int:
    """Seconds until the oldest request in window expires (when limited)."""
    now = time()
    _clean_old(now, _requests[ip])
    if len(_requests[ip]) < LIMIT:
        return 0
    return max(1, int(WINDOW_SEC - (now - _requests[ip][0])))
