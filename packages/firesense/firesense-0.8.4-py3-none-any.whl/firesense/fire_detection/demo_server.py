"""FastAPI server for serving fire detection demo data."""

import os
from pathlib import Path
import importlib.resources
import shutil
import tempfile
import sys
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Fire Detection Demo API")

# CORS configuration for React development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
    ],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Use current working directory
PROJECT_ROOT = Path.cwd()

# Check if we should use localdemo folder
USE_LOCAL_DEMO = os.environ.get("DEMO_LOCAL_MODE", "0") == "1"
DEMO_FOLDER = "localdemo" if USE_LOCAL_DEMO else "demo"


def find_ui_directory() -> Optional[Path]:
    """Find the UI directory with detailed logging."""
    # First, try local development mode
    local_ui_dir = PROJECT_ROOT / "demo-ui" / "dist"
    if local_ui_dir.exists() and (local_ui_dir / "index.html").exists():
        print(f"✓ Found UI files in local development: {local_ui_dir}")
        return local_ui_dir
    
    # Try to find UI files in the installed package
    try:
        # Check common installation locations
        possible_paths = [
            # Site-packages data directory
            Path(sys.prefix) / "share" / "firesense" / "demo-ui",
            # Local share directory
            Path(sys.prefix) / "local" / "share" / "firesense" / "demo-ui",
            # Package directory (for editable installs)
            Path(__file__).parent.parent.parent.parent / "demo-ui" / "dist",
            # Alternative package data location
            Path(sys.prefix) / "firesense" / "demo-ui",
        ]
        
        print("Searching for UI files in installed locations...")
        for path in possible_paths:
            print(f"  Checking: {path}")
            if path.exists() and (path / "index.html").exists():
                print(f"✓ Found UI files at: {path}")
                return path
                
    except Exception as e:
        print(f"⚠️  Error searching for UI files: {e}")
    
    print("✗ UI files not found in any expected location!")
    print("  Expected locations checked:")
    print(f"  - Local dev: {local_ui_dir}")
    if 'possible_paths' in locals():
        for path in possible_paths:
            print(f"  - {path}")
    return None


# Initialize UI directory
UI_DIR = find_ui_directory()

# Mount assets if UI directory is found
if UI_DIR and UI_DIR.exists():
    assets_dir = UI_DIR / "assets"
    if assets_dir.exists():
        try:
            app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")
            print(f"✓ Mounted assets directory: {assets_dir}")
        except Exception as e:
            print(f"⚠️  Failed to mount assets directory: {e}")
    else:
        print(f"⚠️  Assets directory not found at {assets_dir}")


@app.get("/api/demo/{video_id}")
async def get_demo(video_id: str) -> FileResponse:
    """Serve the JSON file for the specified video_id."""
    demo_file = PROJECT_ROOT / DEMO_FOLDER / f"{video_id}.json"

    if not demo_file.exists():
        # List available demos for helpful error message
        demo_dir = PROJECT_ROOT / DEMO_FOLDER
        available_demos = [f.stem for f in demo_dir.glob("*.json")] if demo_dir.exists() else []
        
        error_detail = {
            "error": "Demo file not found",
            "video_id": video_id,
            "expected_file": str(demo_file),
            "demo_folder": DEMO_FOLDER,
            "available_demos": available_demos,
            "help": f"Make sure {video_id}.json exists in the {DEMO_FOLDER} folder"
        }
        
        return JSONResponse(
            status_code=404,
            content=error_detail
        )

    # Return the JSON file directly
    return FileResponse(demo_file, media_type="application/json")


# Serve static video files from demo/videos directory
videos_dir = PROJECT_ROOT / DEMO_FOLDER / "videos"
if videos_dir.exists():
    try:
        app.mount("/demo/videos", StaticFiles(directory=str(videos_dir)), name="videos")
        print(f"✓ Mounted videos directory: {videos_dir}")
    except Exception as e:
        print(f"⚠️  Failed to mount videos directory: {e}")
else:
    print(f"⚠️  Videos directory not found at {videos_dir}")


@app.get("/")
async def serve_ui() -> HTMLResponse:
    """Serve the main UI HTML file."""
    if UI_DIR is None:
        error_detail = {
            "error": "UI files not found",
            "message": "The demo UI files could not be located",
            "help": "Make sure to build the UI with: cd demo-ui && npm run build",
            "checked_locations": [
                str(PROJECT_ROOT / "demo-ui" / "dist"),
                str(Path(sys.prefix) / "share" / "firesense" / "demo-ui"),
                "and other standard locations"
            ]
        }
        return JSONResponse(
            status_code=500,
            content=error_detail
        )
    
    index_file = UI_DIR / "index.html"
    if not index_file.exists():
        error_detail = {
            "error": "index.html not found",
            "ui_directory": str(UI_DIR),
            "expected_file": str(index_file),
            "help": "The UI directory was found but index.html is missing"
        }
        return JSONResponse(
            status_code=404,
            content=error_detail
        )
    
    try:
        with open(index_file, "r") as f:
            content = f.read()
        
        # Inject a script to fix API URLs when accessed via ngrok or other proxies
        api_fix_script = """
<script>
// Fix API URLs for ngrok or other proxies
(function() {
    const originalFetch = window.fetch;
    window.fetch = function(url, ...args) {
        // If the URL starts with http://localhost:8000, replace it with the current origin
        if (typeof url === 'string' && url.startsWith('http://localhost:8000')) {
            url = url.replace('http://localhost:8000', window.location.origin);
        }
        return originalFetch(url, ...args);
    };
})();
</script>
"""
        # Inject the script right after the opening <head> tag
        content = content.replace('<head>', '<head>' + api_fix_script)
        
        return HTMLResponse(content=content)
    except Exception as e:
        error_detail = {
            "error": "Failed to read index.html",
            "file": str(index_file),
            "exception": str(e),
            "help": "Check file permissions and ensure the file is readable"
        }
        return JSONResponse(
            status_code=500,
            content=error_detail
        )


@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "fire-detection-demo",
        "demo_folder": DEMO_FOLDER,
        "ui_loaded": UI_DIR is not None,
        "ui_directory": str(UI_DIR) if UI_DIR else None
    }


@app.get("/debug/ui-status")
async def debug_ui_status() -> dict:
    """Debug endpoint to check UI file status."""
    ui_dir = find_ui_directory()
    
    status = {
        "ui_found": ui_dir is not None,
        "ui_directory": str(ui_dir) if ui_dir else None,
        "project_root": str(PROJECT_ROOT),
        "demo_folder": DEMO_FOLDER,
        "python_prefix": sys.prefix,
        "file_location": __file__,
    }
    
    if ui_dir:
        status["ui_files"] = {
            "index.html": (ui_dir / "index.html").exists(),
            "assets_dir": (ui_dir / "assets").exists(),
        }
        if (ui_dir / "assets").exists():
            status["ui_files"]["asset_count"] = len(list((ui_dir / "assets").glob("*")))
    
    # Check demo files
    demo_dir = PROJECT_ROOT / DEMO_FOLDER
    if demo_dir.exists():
        status["demo_files"] = [f.stem for f in demo_dir.glob("*.json")]
    else:
        status["demo_files"] = []
        status["demo_dir_exists"] = False
    
    return status


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)