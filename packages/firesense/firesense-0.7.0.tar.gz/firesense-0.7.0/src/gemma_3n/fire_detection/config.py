"""Configuration models for fire detection system."""

from pathlib import Path
from typing import Any, Literal

import torch
from pydantic import BaseModel, Field, validator


class Gemma3NE4BConfig(BaseModel):
    """Configuration for Gemma 3N E4B model."""

    # Model specifications
    model_variant: str = Field(default="gemma-2-2b-it", description="Model variant")
    model_path: str = Field(
        default="google/gemma-2-2b-it", description="Model path (Hugging Face or local)"
    )

    # Quantization settings (optional)
    use_quantization: bool = Field(
        default=False, description="Enable model quantization"
    )
    quantization_type: str = Field(
        default="4bit", description="Quantization type (4bit, 8bit)"
    )
    quantization_compute_dtype: str = Field(
        default="float16", description="Compute dtype for quantization"
    )

    # E4B optimizations
    use_flash_attention: bool = Field(default=True, description="Use flash attention")
    gradient_checkpointing: bool = Field(
        default=False, description="Gradient checkpointing"
    )
    max_memory: dict[int, str] = Field(
        default={0: "6GB"}, description="GPU memory allocation"
    )

    # Inference settings
    max_new_tokens: int = Field(
        default=200, ge=50, le=1000, description="Max tokens to generate"
    )
    temperature: float = Field(
        default=0.1, ge=0.0, le=2.0, description="Sampling temperature"
    )
    top_p: float = Field(default=0.9, ge=0.0, le=1.0, description="Top-p sampling")
    repetition_penalty: float = Field(
        default=1.1, ge=1.0, le=2.0, description="Repetition penalty"
    )

    # Vision settings
    vision_encoder: str = Field(default="clip", description="Vision encoder type")
    image_resolution: int = Field(default=336, description="Image resolution")
    patch_size: int = Field(default=14, description="Vision patch size")

    @validator("model_path")
    def validate_model_path(cls, v: str) -> str:
        """Validate model path exists."""
        path = Path(v)
        if not path.exists():
            # Don't fail validation if model doesn't exist - it might be downloaded later
            pass
        return v


class VideoProcessingConfig(BaseModel):
    """Configuration for video processing."""

    # Frame extraction
    frame_interval: float = Field(
        default=1.0, ge=0.1, le=60.0, description="Seconds between frames"
    )
    max_frames: int | None = Field(
        default=None, ge=1, description="Maximum frames to process"
    )
    start_time: float = Field(default=0.0, ge=0.0, description="Start time in seconds")
    end_time: float | None = Field(
        default=None, ge=0.0, description="End time in seconds"
    )

    # Video formats
    supported_formats: list[str] = Field(
        default=[".mp4", ".avi", ".mov", ".mkv", ".webm"],
        description="Supported video formats",
    )

    # Processing optimization
    async_processing: bool = Field(default=True, description="Use async processing")
    batch_size: int = Field(
        default=1, ge=1, le=32, description="Batch size for processing"
    )
    max_workers: int = Field(default=4, ge=1, le=16, description="Max worker processes")

    @validator("end_time")
    def validate_end_time(cls, v: float | None, values: dict[str, Any]) -> float | None:
        """Validate end time is after start time."""
        if v is not None and "start_time" in values:
            start_time = values["start_time"]
            if v <= start_time:
                raise ValueError("end_time must be greater than start_time")
        return v


class DetectionConfig(BaseModel):
    """Configuration for fire detection."""

    # Detection thresholds
    confidence_threshold: float = Field(
        default=0.7, ge=0.0, le=1.0, description="Minimum confidence for fire detection"
    )

    # Output settings
    save_positive_frames: bool = Field(
        default=True, description="Save frames with fire detected"
    )
    save_all_frames: bool = Field(
        default=False, description="Save all processed frames"
    )
    frame_format: Literal["jpg", "png"] = Field(
        default="jpg", description="Frame image format"
    )

    # Analysis settings
    enable_temporal_analysis: bool = Field(
        default=True, description="Enable temporal analysis"
    )
    temporal_window: int = Field(
        default=5, ge=1, le=20, description="Frames for temporal analysis"
    )

    # Prompt templates
    system_prompt: str = Field(
        default="You are a fire detection expert analyzing video frames for safety monitoring.",
        description="System prompt for the model",
    )

    detection_prompt: str = Field(
        default="""Analyze this frame for fire or flames. Provide:
1. Fire detected: Yes/No
2. Confidence: 0-100%
3. If fire detected, describe: location, intensity, color, spread risk

Respond in JSON format.""",
        description="Detection prompt template",
    )


class OutputConfig(BaseModel):
    """Configuration for output and results."""

    # Output paths
    output_dir: Path = Field(default=Path("./output"), description="Output directory")
    results_filename: str = Field(
        default="fire_detection_results", description="Results filename"
    )

    # Output formats
    output_format: Literal["json", "csv", "both"] = Field(
        default="both", description="Output format"
    )
    include_metadata: bool = Field(default=True, description="Include video metadata")
    include_timestamps: bool = Field(
        default=True, description="Include frame timestamps"
    )

    # Compression
    compress_results: bool = Field(default=False, description="Compress output files")

    @validator("output_dir")
    def validate_output_dir(cls, v: Path) -> Path:
        """Create output directory if it doesn't exist."""
        v.mkdir(parents=True, exist_ok=True)
        return v


class FireDetectionConfig(BaseModel):
    """Complete configuration for fire detection system."""

    # Sub-configurations
    model: Gemma3NE4BConfig = Field(default_factory=Gemma3NE4BConfig)
    video: VideoProcessingConfig = Field(default_factory=VideoProcessingConfig)
    detection: DetectionConfig = Field(default_factory=DetectionConfig)
    output: OutputConfig = Field(default_factory=OutputConfig)

    # Hardware settings
    device: str = Field(
        default="auto", description="Device to use: auto, cpu, cuda, mps"
    )

    # Debug settings
    debug: bool = Field(default=False, description="Enable debug mode")
    verbose: bool = Field(default=False, description="Enable verbose logging")

    def get_device(self) -> str:
        """Get the actual device to use."""
        if self.device == "auto":
            if torch.cuda.is_available():
                return "cuda"
            elif torch.backends.mps.is_available():
                return "mps"
            else:
                return "cpu"
        return self.device

    @validator("device")
    def validate_device(cls, v: str) -> str:
        """Validate device availability."""
        if v == "cuda" and not torch.cuda.is_available():
            raise ValueError("CUDA is not available")
        elif v == "mps" and not torch.backends.mps.is_available():
            raise ValueError("MPS is not available")
        return v

    class Config:
        """Pydantic configuration."""

        validate_assignment = True
        use_enum_values = True
