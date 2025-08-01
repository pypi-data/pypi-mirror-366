"""Model interfaces for fire detection."""

from gemma_3n.fire_detection.models.gemma_e4b import Gemma3NE4BInterface
from gemma_3n.fire_detection.models.results import DetectionResult, AnalysisSummary

__all__ = ["Gemma3NE4BInterface", "DetectionResult", "AnalysisSummary"]