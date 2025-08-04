"""Pytest configuration and fixtures."""

from pathlib import Path

import pytest
from rich.console import Console

from firesense.fire_detection.config import FireDetectionConfig


@pytest.fixture
def console():
    """Create test console."""
    return Console(force_terminal=True, width=80)


@pytest.fixture
def fire_detection_config():
    """Create test fire detection configuration."""
    return FireDetectionConfig(
        debug=True,
        verbose=True,
    )


@pytest.fixture
def sample_video_path():
    """Create sample video path for testing."""
    return Path("data/sample_videos/tree_fire.mp4")
