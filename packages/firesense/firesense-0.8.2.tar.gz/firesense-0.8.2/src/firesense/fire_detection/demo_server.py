"""FastAPI server for serving fire detection demo data."""

import os
from pathlib import Path
import importlib.resources
import shutil
import tempfile

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
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


@app.get("/api/demo/{video_id}")
async def get_demo(video_id: str) -> FileResponse:
    """Serve the JSON file for the specified video_id."""
    demo_file = PROJECT_ROOT / DEMO_FOLDER / f"{video_id}.json"

    if not demo_file.exists():
        # List available demos for helpful error message
        demo_dir = PROJECT_ROOT / DEMO_FOLDER
        available_demos = [f.stem for f in demo_dir.glob("*.json")] if demo_dir.exists() else []
        raise HTTPException(
            status_code=404,
            detail=f"Demo file not found: {video_id}.json in {DEMO_FOLDER} folder. Available demos: {', '.join(available_demos)}",
        )

    # Return the JSON file directly
    return FileResponse(demo_file, media_type="application/json")


# Serve static video files from demo/videos directory
videos_dir = PROJECT_ROOT / DEMO_FOLDER / "videos"
if videos_dir.exists():
    app.mount("/demo/videos", StaticFiles(directory=str(videos_dir)), name="videos")
else:
    print(f"Warning: Videos directory not found at {videos_dir}")

# Serve the built UI files
try:
    # Try to find the UI files in the installed package
    if hasattr(importlib.resources, 'files'):
        # Python 3.9+
        ui_files = importlib.resources.files('firesense').joinpath('../../share/firesense/demo-ui')
        if ui_files.is_dir():
            # Create a temporary directory and extract the UI files
            temp_ui_dir = Path(tempfile.mkdtemp(prefix="firesense_ui_"))
            # Copy all files from the package to temp directory
            import shutil
            for item in ui_files.iterdir():
                if item.is_file():
                    shutil.copy2(str(item), temp_ui_dir / item.name)
                elif item.is_dir():
                    shutil.copytree(str(item), temp_ui_dir / item.name)
            app.mount("/assets", StaticFiles(directory=str(temp_ui_dir / "assets")), name="assets")
            UI_DIR = temp_ui_dir
        else:
            UI_DIR = None
    else:
        # Fallback for older Python versions
        import pkg_resources
        try:
            ui_path = pkg_resources.resource_filename('firesense', '../../share/firesense/demo-ui')
            UI_DIR = Path(ui_path)
            if UI_DIR.exists():
                app.mount("/assets", StaticFiles(directory=str(UI_DIR / "assets")), name="assets")
            else:
                UI_DIR = None
        except:
            UI_DIR = None
except Exception as e:
    print(f"Warning: Could not load UI files from package: {e}")
    # Fallback to local development mode
    local_ui_dir = PROJECT_ROOT / "demo-ui" / "dist"
    if local_ui_dir.exists():
        UI_DIR = local_ui_dir
        app.mount("/assets", StaticFiles(directory=str(UI_DIR / "assets")), name="assets")
    else:
        UI_DIR = None


@app.get("/")
async def serve_ui() -> HTMLResponse:
    """Serve the main UI HTML file."""
    if UI_DIR is None:
        raise HTTPException(status_code=500, detail="UI files not found")
    
    index_file = UI_DIR / "index.html"
    if not index_file.exists():
        raise HTTPException(status_code=404, detail="index.html not found")
    
    with open(index_file, "r") as f:
        content = f.read()
    
    return HTMLResponse(content=content)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "service": "fire-detection-demo", "demo_folder": DEMO_FOLDER, "ui_loaded": UI_DIR is not None}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
