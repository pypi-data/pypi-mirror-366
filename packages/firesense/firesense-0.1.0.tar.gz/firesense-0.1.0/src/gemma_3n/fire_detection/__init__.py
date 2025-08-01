"""Fire detection module using Gemma 3N E4B model."""

from gemma_3n.fire_detection.config import FireDetectionConfig
from gemma_3n.fire_detection.detector import FireDetector

__all__ = ["FireDetectionConfig", "FireDetector"]