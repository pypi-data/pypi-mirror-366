# Publishing FireSense to PyPI

This guide explains how to publish the FireSense package to PyPI.

## Prerequisites

1. Create a PyPI account at https://pypi.org/account/register/
2. Create an API token at https://pypi.org/manage/account/token/

## Setup Authentication

Create a `.env` file in the project root:

```bash
TWINE_USERNAME=__token__
TWINE_PASSWORD=pypi-YOUR_ACTUAL_TOKEN_HERE
```

## Publishing

### Method 1: Using Make (Recommended)

```bash
# Build and publish in one command
make publish

# Clean build artifacts
make publish-clean
```

### Method 2: Manual Publishing

```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info/

# Build the package
uv run python -m build

# Upload to PyPI
python scripts/publish.py
```

### Method 3: GitHub Actions (Automated)

The package will automatically publish when you create a release on GitHub.
Make sure to set the `PYPI_API_TOKEN` secret in your repository settings.

## After Publishing

Once published, users can install FireSense with:

```bash
pip install firesense
```

## Version Management

To release a new version:

1. Update the version in `pyproject.toml` and `src/gemma_3n/__init__.py`
2. Commit the changes
3. Create a git tag: `git tag v0.2.0`
4. Push the tag: `git push origin v0.2.0`
5. Build and publish using `make publish`

## Troubleshooting

- If the package name is taken, you'll need to choose a different name in `pyproject.toml`
- Make sure all dependencies are properly specified
- Test the package thoroughly before publishing
- The `.env` file should never be committed to git