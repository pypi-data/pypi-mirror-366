"""Gemma 3N - A modern Python project managed with uv."""

__version__ = "0.10.1"
__author__ = "Gregory Mulla"
__email__ = "gregory.cr.mulla@gmail.com"

from firesense.fire_detection.config import FireDetectionConfig
from firesense.fire_detection.inference import process_video_inference
from firesense.fire_detection.model import (
    FireDescription,
    gemma_fire_inference,
    setup_model,
)

__all__ = [
    "FireDescription",
    "FireDetectionConfig",
    "gemma_fire_inference",
    "process_video_inference",
    "setup_model",
]
