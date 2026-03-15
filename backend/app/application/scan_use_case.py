"""Use case: scan a JSON payload for privacy risks."""

from typing import Any

from app.application.interfaces import DetectionEngineInterface
from app.domain.entities import ScanResult


class ScanPayloadUseCase:
    """Orchestrates scanning a payload via the detection engine."""

    def __init__(self, detection_engine: DetectionEngineInterface):
        self._engine = detection_engine

    def execute(self, payload: dict[str, Any]) -> ScanResult:
        """Run privacy scan on the given payload."""
        return self._engine.scan_payload(payload)
