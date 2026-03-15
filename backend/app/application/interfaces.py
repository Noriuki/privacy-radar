"""Application interfaces for dependency inversion."""

from abc import ABC, abstractmethod
from typing import Any

from app.domain.entities import ScanResult


class DetectionEngineInterface(ABC):
    """Interface for the detection engine (implemented in infrastructure)."""

    @abstractmethod
    def scan_payload(self, payload: dict[str, Any]) -> ScanResult:
        """Scan a JSON-like payload and return privacy analysis result."""
        ...
