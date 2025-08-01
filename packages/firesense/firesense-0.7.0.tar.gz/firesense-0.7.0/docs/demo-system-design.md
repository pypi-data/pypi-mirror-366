# Fire Detection Demo System Design

## Overview

A simplified fire detection demonstration system consisting of:
1. **FastAPI Server**: Serves pre-analyzed fire detection JSON results
2. **React UI**: Displays video and fire detection status
3. **CLI Integration**: `firesense demo <video_id>` command

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     CLI Command                              │
│                firesense demo <video_id>                     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                  Demo Launcher                               │
│  • Starts FastAPI server (port 8000)                        │
│  • Starts React dev server (port 3000)                      │
│  • Opens browser to http://localhost:3000?id=<video_id>    │
└─────────────────────────────────────────────────────────────┘
                     │
          ┌──────────┴──────────┐
          ▼                     ▼
┌─────────────────────┐ ┌─────────────────────┐
│   FastAPI Server    │ │    React UI         │
│  (Port 8000)        │ │   (Port 3000)       │
│                     │ │                     │
│  Endpoints:         │ │  Components:        │
│  • GET /api/demos   │ │  • VideoPlayer      │
│  • GET /api/demo/   │ │  • FireStatus       │
│    {video_id}       │ │  • SimplifiedUI     │
│  • Static files     │ │                     │
└─────────────────────┘ └─────────────────────┘
          │                     │
          └──────────┬──────────┘
                     ▼
          ┌─────────────────────┐
          │   Demo Data Files   │
          │  demo/*.json        │
          │  demo/videos/*.mp4  │
          └─────────────────────┘
```

## Component Details

### 1. FastAPI Server (`demo_server.py`)

```python
# Location: gemma_3n/src/gemma_3n/fire_detection/demo_server.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pathlib import Path
import json

app = FastAPI(title="Fire Detection Demo API")

# CORS for React development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # Vite default port
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/demo/{video_id}")
async def get_demo(video_id: str):
    """Serve the JSON file for the specified video_id"""
    demo_file = Path(f"demo/{video_id}.json")
    
    if not demo_file.exists():
        raise HTTPException(status_code=404, detail=f"Demo file not found: {video_id}.json")
    
    # Return the JSON file directly
    return FileResponse(demo_file, media_type="application/json")

# Serve static video files from demo/videos directory
from fastapi.staticfiles import StaticFiles
app.mount("/demo/videos", StaticFiles(directory="demo/videos"), name="videos")
```

### 2. React UI Structure

```
demo-ui/
├── package.json
├── vite.config.js
├── index.html
└── src/
    ├── main.jsx
    ├── App.jsx
    ├── components/
    │   ├── VideoPlayer.jsx
    │   └── FireStatus.jsx
    ├── hooks/
    │   └── useDemo.js
    └── styles/
        └── App.css
```

#### Key Components

**App.jsx**
```jsx
// Simplified main component
function App() {
  const videoId = new URLSearchParams(window.location.search).get('id');
  const { demoData, currentStatus, handleTimeUpdate } = useDemo(videoId);
  
  if (!videoId) {
    return <div className="error">No video ID provided. Use ?id=VIDEO_ID in URL.</div>;
  }
  
  if (!demoData) {
    return <div className="loading">Loading demo data...</div>;
  }
  
  return (
    <div className="demo-app">
      <header>
        <h1>Fire Detection Demo: {demoData.title || videoId}</h1>
      </header>
      <main className="demo-content">
        <VideoPlayer 
          videoUrl={demoData.video_url}
          detections={demoData.detections}
          onTimeUpdate={handleTimeUpdate}
        />
        <FireStatus 
          status={currentStatus}
          isDangerous={currentStatus?.is_dangerous}
        />
      </main>
    </div>
  );
}
```

**VideoPlayer.jsx**
```jsx
// Video player with detection overlay
function VideoPlayer({ videoUrl, detections, onTimeUpdate }) {
  const videoRef = useRef(null);
  
  return (
    <div className="video-container">
      <video 
        ref={videoRef}
        src={videoUrl}
        controls
        onTimeUpdate={(e) => onTimeUpdate(e.target.currentTime)}
      />
      {/* Optional: Overlay for bounding boxes */}
    </div>
  );
}
```

**FireStatus.jsx**
```jsx
// Simple fire detection status display
function FireStatus({ status, isDangerous }) {
  return (
    <div className={`fire-status ${isDangerous ? 'dangerous' : ''}`}>
      <h2>Fire Detection Status</h2>
      <div className="status-indicator">
        {status?.fire_detected ? (
          <div className="fire-detected">
            <span className="icon">🔥</span>
            <p>Fire Detected</p>
            <p className="confidence">
              Confidence: {(status.confidence * 100).toFixed(0)}%
            </p>
            {isDangerous && (
              <p className="danger-warning">⚠️ Dangerous Fire!</p>
            )}
          </div>
        ) : (
          <div className="no-fire">
            <span className="icon">✓</span>
            <p>No Fire Detected</p>
          </div>
        )}
      </div>
    </div>
  );
}
```

**useDemo.js Hook**
```javascript
// Hook for fetching and managing demo data
import { useState, useEffect, useCallback } from 'react';

export function useDemo(videoId) {
  const [demoData, setDemoData] = useState(null);
  const [currentStatus, setCurrentStatus] = useState(null);
  const [error, setError] = useState(null);
  
  // Fetch demo data on mount
  useEffect(() => {
    if (!videoId) return;
    
    const fetchDemo = async () => {
      try {
        const response = await fetch(`http://localhost:8000/api/demo/${videoId}`);
        if (!response.ok) {
          throw new Error(`Demo not found: ${videoId}`);
        }
        const data = await response.json();
        setDemoData(data);
        
        // Set initial status (first detection)
        if (data.detections && data.detections.length > 0) {
          setCurrentStatus(data.detections[0]);
        }
      } catch (err) {
        setError(err.message);
        console.error('Failed to fetch demo:', err);
      }
    };
    
    fetchDemo();
  }, [videoId]);
  
  // Update status based on video time
  const handleTimeUpdate = useCallback((currentTime) => {
    if (!demoData?.detections) return;
    
    // Find the detection closest to current time
    let closestDetection = demoData.detections[0];
    
    for (const detection of demoData.detections) {
      if (detection.timestamp <= currentTime) {
        closestDetection = detection;
      } else {
        break;
      }
    }
    
    setCurrentStatus(closestDetection);
  }, [demoData]);
  
  return { demoData, currentStatus, error, handleTimeUpdate };
}
```

### 3. Demo Data Format

```json
{
  "id": "wildfire_example_01",
  "title": "Wildfire Detection Example",
  "video_url": "/demo/videos/wildfire_example_01.mp4",
  "duration": 120.5,
  "fps": 30,
  "detections": [
    {
      "timestamp": 0.0,
      "fire_detected": false,
      "confidence": 0.0,
      "is_dangerous": false
    },
    {
      "timestamp": 15.5,
      "fire_detected": true,
      "confidence": 0.85,
      "is_dangerous": false,
      "fire_characteristics": {
        "intensity": "low",
        "spread_rate": "slow"
      }
    },
    {
      "timestamp": 45.0,
      "fire_detected": true,
      "confidence": 0.95,
      "is_dangerous": true,
      "fire_characteristics": {
        "intensity": "high",
        "spread_rate": "rapid"
      }
    }
  ]
}
```

### 4. CLI Integration

```python
# Add to cli.py

@app.command()
def demo(
    video_id: str = typer.Argument(..., help="Demo video ID to display"),
    api_port: int = typer.Option(8000, "--api-port", help="FastAPI server port"),
    ui_port: int = typer.Option(5173, "--ui-port", help="React dev server port (Vite default)"),
    no_browser: bool = typer.Option(False, "--no-browser", help="Don't open browser automatically"),
):
    """Launch demo UI for pre-analyzed fire detection results."""
    
    console.print(f"[bold green]🔥 Launching Fire Detection Demo[/bold green]")
    console.print(f"[blue]Video ID: {video_id}[/blue]")
    
    # Verify demo files exist
    project_root = Path(__file__).parent.parent.parent.parent
    demo_dir = project_root / "demo"
    demo_file = demo_dir / f"{video_id}.json"
    video_file = demo_dir / "videos" / f"{video_id}.mp4"
    
    if not demo_file.exists():
        console.print(f"[red]Error: Demo JSON file not found: {demo_file}[/red]")
        console.print("[yellow]Available demos:[/yellow]")
        for f in demo_dir.glob("*.json"):
            console.print(f"  - {f.stem}")
        raise typer.Exit(1)
    
    if not video_file.exists():
        console.print(f"[yellow]Warning: Video file not found: {video_file}[/yellow]")
        console.print("[yellow]The demo will work but video playback won't be available[/yellow]")
    
    # Change to project root for proper path resolution
    import os
    os.chdir(project_root)
    
    # Start FastAPI server
    console.print(f"[blue]Starting API server on port {api_port}...[/blue]")
    api_process = subprocess.Popen([
        sys.executable, "-m", "uvicorn",
        "src.gemma_3n.fire_detection.demo_server:app",
        "--port", str(api_port),
        "--host", "0.0.0.0",
        "--reload"
    ])
    
    # Start React dev server
    ui_dir = project_root / "demo-ui"
    if not ui_dir.exists():
        console.print(f"[red]Error: Demo UI not found at {ui_dir}[/red]")
        console.print("[yellow]Please run setup first to create the demo UI[/yellow]")
        api_process.terminate()
        raise typer.Exit(1)
    
    console.print(f"[blue]Starting UI server on port {ui_port}...[/blue]")
    ui_process = subprocess.Popen([
        "npm", "run", "dev", "--", "--port", str(ui_port)
    ], cwd=ui_dir)
    
    # Wait for servers to start
    time.sleep(3)
    
    # Open browser
    if not no_browser:
        url = f"http://localhost:{ui_port}?id={video_id}"
        console.print(f"[blue]Opening browser at: {url}[/blue]")
        webbrowser.open(url)
    
    console.print("\n[bold yellow]Demo servers running![/bold yellow]")
    console.print(f"[blue]📡 API: http://localhost:{api_port}[/blue]")
    console.print(f"[blue]🖥️  UI: http://localhost:{ui_port}[/blue]")
    console.print(f"[blue]📹 Video: {video_id}[/blue]")
    console.print("\n[dim]Press Ctrl+C to stop both servers[/dim]")
    
    try:
        # Wait for either process to exit
        while api_process.poll() is None and ui_process.poll() is None:
            time.sleep(1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Shutting down servers...[/yellow]")
    finally:
        # Cleanup both processes
        for process in [api_process, ui_process]:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
        
        console.print("[green]✅ Demo servers stopped[/green]")
```

## File Structure

```
gemma_3n/
├── demo/                          # Demo data directory
│   ├── wildfire_example_01.json   # Pre-analyzed results
│   ├── kitchen_fire_02.json       # Pre-analyzed results
│   └── videos/                    # Video files
│       ├── wildfire_example_01.mp4
│       └── kitchen_fire_02.mp4
├── demo-ui/                       # React UI application
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   └── src/
│       ├── main.jsx
│       ├── App.jsx
│       ├── components/
│       ├── hooks/
│       └── styles/
└── src/gemma_3n/fire_detection/
    ├── cli.py                     # Extended with demo command
    └── demo_server.py             # FastAPI server

```

## Implementation Steps

1. **Create FastAPI server** (`demo_server.py`)
   - Single endpoint `/api/demo/{video_id}` to serve JSON files
   - Static mount for video files at `/demo/videos`
   - CORS configuration for React development

2. **Create React UI** (`demo-ui/`)
   - Initialize Vite React project
   - Build VideoPlayer component with time tracking
   - Build FireStatus component for real-time status display
   - Implement useDemo hook for API integration

3. **Prepare demo data**
   - Create JSON files with pre-analyzed results
   - Include video URL path in JSON
   - Add timestamp-based detections with danger levels

4. **Extend CLI** (`cli.py`)
   - Add `demo` command to existing CLI
   - Manage both FastAPI and React dev servers
   - Automatic browser launching with video ID

5. **Create demo content**
   - Convert existing analysis results to demo format
   - Place videos in `demo/videos/` directory
   - Test complete workflow

## Summary

This design provides a simple but effective demonstration system for the fire detection capabilities:

- **Minimal Backend**: Single FastAPI endpoint serves JSON files directly
- **React UI**: Clean interface showing video and detection status side-by-side
- **CLI Integration**: Simple command `firesense demo <video_id>` launches everything
- **No GPU Required**: Uses pre-analyzed results, perfect for demos
- **Easy Setup**: Both servers start with one command

The system is designed to be:
- **Simple**: Minimal code and dependencies
- **Fast**: Quick to start and responsive
- **Extensible**: Easy to add new demo videos
- **Developer-friendly**: Hot reload on both frontend and backend