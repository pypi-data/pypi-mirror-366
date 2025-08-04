# FireSense

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

FireSense is an AI-powered fire detection system that uses the Gemma 3N E4B vision model to analyze video content for fire and smoke detection. It provides real-time analysis, comprehensive fire characteristics assessment, and emergency response recommendations.

## Features

- 🚀 **Fast Development**: Leverages uv for 10-100x faster dependency installation
- 📦 **Modern Packaging**: PEP 621 compliant with pyproject.toml
- 🔍 **Type Safety**: Full mypy strict mode support
- ✅ **Testing**: Comprehensive pytest setup with coverage
- 🎨 **Code Quality**: Pre-configured with ruff, black, and pre-commit
- 📚 **Documentation**: Ready for MkDocs with Material theme
- 🔄 **CI/CD**: GitHub Actions workflow included

## Quick Start

### Prerequisites

- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) package manager

### Installation

#### From PyPI (Recommended)

```bash
pip install firesense
```

#### From Source

1. Clone the repository:
```bash
git clone https://github.com/gregorymulla/firesense_ai.git
cd firesense_ai
```

2. Install with pip:
```bash
pip install -e ".[dev]"
```

#### Using uv (Fastest)

1. Install uv:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Install firesense:
```bash
uv pip install firesense
```

## Usage

### Running the Application

```bash
# Analyze a video file
firesense analyze video.mp4

# Analyze with custom settings
firesense analyze video.mp4 --interval 1.0 --confidence 0.8

# Preview frame extraction
firesense preview video.mp4 --frames 10

# Launch demo UI
firesense demo wildfire_example_01

# Process multiple videos
firesense batch /path/to/videos --pattern "*.mp4"
```

### Development Commands

```bash
# Run tests
make test

# Run linting
make lint

# Format code
make format

# Type check
make type-check

# Run all checks
make check

# Build documentation
make docs

# Clean build artifacts
make clean
```

## Project Structure

```
firesense/
├── src/gemma_3n/       # Source code
│   └── fire_detection/ # Fire detection system
│       ├── models/     # Data models and AI interface
│       ├── processing/ # Video and frame processing
│       └── vision/     # Computer vision utilities
├── tests/              # Test suite
│   ├── unit/           # Unit tests
│   └── integration/    # Integration tests
├── docs/               # Documentation
├── scripts/            # Utility scripts
└── .github/            # GitHub Actions
```

## Configuration

The application can be configured using environment variables with the `GEMMA_` prefix:

```bash
export GEMMA_DEBUG=true
export GEMMA_API_PORT=9000
export GEMMA_LOG_LEVEL=DEBUG
```

Or using a `.env` file:

```env
GEMMA_DEBUG=true
GEMMA_API_PORT=9000
GEMMA_LOG_LEVEL=DEBUG
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and checks (`make check`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Releasing

To publish a new release to PyPI, simply push a commit to the main branch with a message starting with "new release" followed by the version number:

```bash
git commit -m "new release 0.3.0"
git push origin main
```

The GitHub Actions workflow will automatically:
1. Extract the version from the commit message
2. Update the version in `pyproject.toml` and `__init__.py`
3. Build and publish the package to PyPI
4. Create a git tag
5. Create a GitHub release

**Note**: Make sure you have set up the `PYPI_API_TOKEN` secret in your GitHub repository settings.

## License

This project is licensed under the MIT License - see the LICENSE file for details.