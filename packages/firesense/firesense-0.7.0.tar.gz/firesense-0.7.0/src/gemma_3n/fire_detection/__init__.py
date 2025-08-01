"""Fire detection module using Gemma 3N E4B model."""

from .config import FireDetectionConfig
from .inference import process_video_inference

__all__ = ["FireDetectionConfig", "process_video_inference"]
