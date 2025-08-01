"""FastAPI server for serving fire detection demo data."""

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
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

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent


@app.get("/api/demo/{video_id}")
async def get_demo(video_id: str) -> FileResponse:
    """Serve the JSON file for the specified video_id."""
    demo_file = PROJECT_ROOT / "demo" / f"{video_id}.json"

    if not demo_file.exists():
        # List available demos for helpful error message
        demo_dir = PROJECT_ROOT / "demo"
        available_demos = [f.stem for f in demo_dir.glob("*.json")]
        raise HTTPException(
            status_code=404,
            detail=f"Demo file not found: {video_id}.json. Available demos: {', '.join(available_demos)}",
        )

    # Return the JSON file directly
    return FileResponse(demo_file, media_type="application/json")


# Serve static video files from demo/videos directory
videos_dir = PROJECT_ROOT / "demo" / "videos"
if videos_dir.exists():
    app.mount("/demo/videos", StaticFiles(directory=str(videos_dir)), name="videos")
else:
    print(f"Warning: Videos directory not found at {videos_dir}")


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "service": "fire-detection-demo"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
