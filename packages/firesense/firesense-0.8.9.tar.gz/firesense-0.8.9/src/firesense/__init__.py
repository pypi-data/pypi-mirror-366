"""Gemma 3N - A modern Python project managed with uv."""

__version__ = "0.8.9"
__author__ = "Gregory Mulla"
__email__ = "gregory.cr.mulla@gmail.com"

from firesense.fire_detection.model import setup_model, gemma_fire_inference, FireDescription
from firesense.fire_detection.config import FireDetectionConfig
from firesense.fire_detection.inference import process_video_inference

__all__ = [
    "setup_model",
    "gemma_fire_inference", 
    "FireDescription",
    "FireDetectionConfig",
    "process_video_inference"
]
