# Fire Detection System with Gemma 3N E4B

Welcome to the Fire Detection System documentation! This project uses the powerful Gemma 3N E4B model for real-time fire and wildfire detection in video streams.

## Why This Fire Detection System?

Our system provides advanced fire detection capabilities with:

- **AI-Powered Detection**: Uses Gemma 3N E4B model for accurate fire detection
- **Real-Time Analysis**: Stream processing for immediate fire alerts
- **Wildfire Assessment**: Comprehensive emergency level and spread risk analysis
- **Web Interface**: Interactive UI for video analysis and monitoring
- **Modern Tooling**: Built with uv, the fast Python package manager
- **Type Safety**: Full type hints with strict mypy checking

## Key Features

### 🚀 Performance
- Lightning-fast dependency management with uv
- Optimized project structure for quick imports
- Efficient configuration management

### 🛡️ Quality
- Comprehensive test coverage with pytest
- Code formatting with Black
- Linting with Ruff
- Type checking with mypy
- Pre-commit hooks for consistency

### 📦 Modern Python
- PEP 621 compliant `pyproject.toml`
- Source layout for better import isolation
- Pydantic for data validation
- Rich for beautiful terminal output

### 🔧 Developer Experience
- Simple Makefile commands
- Clear project structure
- Extensive documentation
- Easy configuration management

## Quick Example

```python
from firesense.fire_detection.config import FireDetectionConfig
from firesense.fire_detection.detector import FireDetector
from pathlib import Path

# Create fire detection configuration
config = FireDetectionConfig(
    device="auto",
    debug=True
)

# Initialize detector
detector = FireDetector(config)

# Analyze video for fire
video_path = Path("video.mp4")
result = detector.process_video_sync(video_path)

print(f"Fire detected in {result.summary.fire_detections} frames")
```

## Next Steps

- [Installation Guide](getting-started/installation.md) - Get started with Gemma 3N
- [Quick Start](getting-started/quickstart.md) - Build your first feature
- [API Reference](api/overview.md) - Explore the API documentation
- [Contributing](development/contributing.md) - Help improve Gemma 3N