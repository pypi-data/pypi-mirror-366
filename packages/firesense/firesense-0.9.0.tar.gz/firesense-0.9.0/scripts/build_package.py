#!/usr/bin/env python3
"""
Build script for firesense package.
Builds the demo UI and then builds the Python package.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path


def build_demo_ui():
    """Build the demo UI React app."""
    print("🔨 Building demo UI...")

    demo_ui_dir = Path("demo-ui")
    if not demo_ui_dir.exists():
        print("❌ Error: demo-ui directory not found")
        sys.exit(1)

    # Check if node_modules exists
    if not (demo_ui_dir / "node_modules").exists():
        print("📦 Installing demo UI dependencies...")
        result = subprocess.run(
            ["npm", "install"], cwd=demo_ui_dir, capture_output=True, text=True
        )
        if result.returncode != 0:
            print(f"❌ Error installing dependencies: {result.stderr}")
            sys.exit(1)

    # Build the UI
    print("🏗️  Building production UI...")
    result = subprocess.run(
        ["npm", "run", "build"], cwd=demo_ui_dir, capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"❌ Error building UI: {result.stderr}")
        sys.exit(1)

    # Verify build output exists
    dist_dir = demo_ui_dir / "dist"
    if not dist_dir.exists():
        print("❌ Error: UI build output not found")
        sys.exit(1)

    print("✅ Demo UI built successfully")

    # Copy built UI files to package source
    print("📂 Copying UI files to package...")
    src_ui_dir = Path("src/firesense/demo-ui")
    if src_ui_dir.exists():
        shutil.rmtree(src_ui_dir)
    shutil.copytree(dist_dir, src_ui_dir)
    print("✅ UI files copied to package")

    return True


def build_python_package():
    """Build the Python package."""
    print("📦 Building Python package...")

    # Clean previous builds
    for dir_name in ["dist", "build", "*.egg-info"]:
        for path in Path(".").glob(dir_name):
            if path.is_dir():
                shutil.rmtree(path)

    # Build the package
    result = subprocess.run(
        [sys.executable, "-m", "build"], capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"❌ Error building package: {result.stderr}")
        sys.exit(1)

    print("✅ Python package built successfully")

    # List built files
    dist_dir = Path("dist")
    if dist_dir.exists():
        print("\n📋 Built files:")
        for file in dist_dir.iterdir():
            print(f"  - {file.name}")

    return True


def main():
    """Main build process."""
    print("🚀 Starting firesense build process...\n")

    # Change to project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    os.chdir(project_root)

    # Build demo UI
    if not build_demo_ui():
        sys.exit(1)

    print()  # Empty line for readability

    # Build Python package
    if not build_python_package():
        sys.exit(1)

    print("\n✨ Build completed successfully!")
    print("\nTo publish to PyPI, run:")
    print("  python scripts/publish.py")


if __name__ == "__main__":
    main()
