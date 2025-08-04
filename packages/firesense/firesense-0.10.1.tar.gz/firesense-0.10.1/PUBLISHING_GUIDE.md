# Publishing Guide for FireSense

## Manual Publishing with `make publish`

To publish a new version manually:

1. **Set up PyPI authentication**:
   ```bash
   cp .env.example .env
   ```
   Then edit `.env` and add your PyPI token:
   ```
   TWINE_PASSWORD=pypi-YOUR_ACTUAL_TOKEN_HERE
   ```

2. **Update version numbers**:
   - Edit `pyproject.toml` - change the `version` field
   - Edit `src/gemma_3n/__init__.py` - change `__version__`

3. **Build and publish**:
   ```bash
   make publish-clean  # Clean old builds
   make publish        # Build and upload to PyPI
   ```

## Automated Publishing with GitHub Actions

Simply commit with a message starting with "new release X.Y.Z":

```bash
git commit -m "new release 0.8.0"
git push
```

The GitHub Actions workflow will automatically update versions and publish.

**Note**: Make sure the `PYPI_API_TOKEN` secret is set in your GitHub repository settings.

## Troubleshooting

- If you get authentication errors, ensure your PyPI token:
  - Starts with `pypi-`
  - Has upload permissions for the `firesense` package
  - Is correctly set in `.env` (for manual) or GitHub secrets (for automated)

- If the build fails, ensure all dependencies are installed:
  ```bash
  uv add --dev build twine python-dotenv
  ```