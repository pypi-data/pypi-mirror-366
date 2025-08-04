#!/usr/bin/env python3
"""
Publish package to PyPI with proper authentication.

Usage:
    python scripts/publish.py
"""

import os
import subprocess
import sys

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def publish():
    """Publish package to PyPI."""

    # Check for required environment variables
    username = os.getenv("TWINE_USERNAME", "__token__")
    password = os.getenv("TWINE_PASSWORD")
    repo_url = "https://upload.pypi.org/legacy/"

    if not password or password.startswith("pypi-YOUR"):
        print("Error: TWINE_PASSWORD not set in .env file")
        print("Please add your PyPI token to the .env file")
        print("Example:")
        print("  TWINE_PASSWORD=pypi-xxxxxxxxxxxx")
        sys.exit(1)

    # Set environment variables for twine
    env = os.environ.copy()
    env["TWINE_USERNAME"] = username
    env["TWINE_PASSWORD"] = password

    # Build command
    cmd = ["uv", "run", "twine", "upload", "dist/*"]

    print("Publishing to PyPI...")
    print(f"Repository: {repo_url}")
    print(f"Username: {username}")
    print("Password: [HIDDEN]")
    print()

    # Run twine
    try:
        subprocess.run(cmd, env=env, check=True)
        print("\nSuccessfully published to PyPI!")
        print("\nInstall with:")
        print("  pip install firesense")

    except subprocess.CalledProcessError as e:
        print(f"Error publishing to PyPI: {e}")
        sys.exit(1)


if __name__ == "__main__":
    publish()
