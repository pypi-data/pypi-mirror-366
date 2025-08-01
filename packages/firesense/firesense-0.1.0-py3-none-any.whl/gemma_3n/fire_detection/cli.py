"""Command-line interface for fire detection system."""

import json
import logging
import subprocess
import sys
import time
import webbrowser
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.logging import RichHandler
from rich.table import Table

from gemma_3n.fire_detection.config import FireDetectionConfig  
from gemma_3n.fire_detection.detector import FireDetector

app = typer.Typer(
    name="fire-detector",
    help="Fire detection system using Gemma 3N E4B model",
    no_args_is_help=True,
)
console = Console()


def setup_logging(verbose: bool = False, debug: bool = False) -> None:
    """Setup logging configuration.
    
    Args:
        verbose: Enable verbose logging
        debug: Enable debug logging
    """
    level = logging.DEBUG if debug else (logging.INFO if verbose else logging.WARNING)
    
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(console=console, rich_tracebacks=True)]
    )


def launch_ui_mode(
    video_path: Path,
    interval: float,
    confidence: float,
    output_dir: Path,
    device: str,
    batch_size: int,
    save_frames: bool,
    format: str,
    model_path: str,
    stream: bool,
    verbose: bool,
    debug: bool
) -> None:
    """Launch web UI for interactive fire detection analysis."""
    
    console.print("[bold green]🔥 Launching Fire Detection UI...[/bold green]")
    
    # Look for React build first, then fall back to original UI
    project_root = Path(__file__).parent.parent.parent.parent
    react_ui_dir = project_root / "ui-react" / "dist"
    original_ui_dir = project_root / "ui"
    
    ui_dir = None
    
    # Check for React build
    if react_ui_dir.exists() and (react_ui_dir / "index.html").exists():
        ui_dir = react_ui_dir
        console.print("[blue]📱 Using React UI build[/blue]")
    # Fall back to original UI
    elif original_ui_dir.exists():
        ui_dir = original_ui_dir
        console.print("[blue]📄 Using original HTML UI[/blue]")
        
        # Check for required UI files in original UI
        required_files = ["index.html", "style.css", "script.js"]
        missing_files = [f for f in required_files if not (ui_dir / f).exists()]
        
        if missing_files:
            console.print(f"[red]Error: Missing UI files: {', '.join(missing_files)}[/red]")
            console.print(f"[yellow]Please ensure all UI files exist in: {ui_dir}[/yellow]")
            console.print("[blue]Tip: Build React UI with 'cd ui-react && npm run build'[/blue]")
            raise typer.Exit(1)
    else:
        console.print(f"[red]Error: No UI found. Checked:[/red]")
        console.print(f"[red]  - React build: {react_ui_dir}[/red]")
        console.print(f"[red]  - Original UI: {original_ui_dir}[/red]")
        console.print("[blue]Tip: Build React UI with 'cd ui-react && npm install && npm run build'[/blue]")
        raise typer.Exit(1)
    
    # Copy video to ui directory for access
    video_copy = ui_dir / video_path.name
    if not video_copy.exists():
        import shutil
        console.print(f"[blue]Copying video to UI directory...[/blue]")
        shutil.copy2(video_path, video_copy)
    
    # Create analysis configuration
    config_data = {
        "video_path": str(video_copy),
        "interval": interval,
        "confidence": confidence,
        "output_dir": str(output_dir),
        "device": device,
        "batch_size": batch_size,
        "save_frames": save_frames,
        "format": format,
        "model_path": model_path,
        "stream": stream,
        "verbose": verbose,
        "debug": debug
    }
    
    # Save configuration for UI to use
    config_file = ui_dir / "analysis_config.json"
    with open(config_file, 'w') as f:
        json.dump(config_data, f, indent=2)
    
    # Start simple HTTP server
    server_port = 9090
    server_process = None
    
    try:
        # Start HTTP server in background
        console.print(f"[blue]Starting HTTP server on port {server_port}...[/blue]")
        
        server_process = subprocess.Popen([
            sys.executable, "-m", "http.server", str(server_port)
        ], cwd=ui_dir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Wait a moment for server to start
        time.sleep(2)
        
        # Open browser
        ui_url = f"http://localhost:{server_port}"
        console.print(f"[green]✅ UI Server started successfully![/green]")
        console.print(f"[blue]Opening browser at: {ui_url}[/blue]")
        
        webbrowser.open(ui_url)
        
        console.print("\n[bold yellow]Fire Detection UI is now running![/bold yellow]")
        console.print(f"[blue]📁 Video: {video_path.name}[/blue]")
        stream_mode = "Real-time streaming" if stream else "Pre-analysis"
        console.print(f"[blue]⚙️  Config: {stream_mode}, Frame interval={interval}s, Confidence threshold={confidence}[/blue]")
        console.print(f"[blue]💻 URL: {ui_url}[/blue]")
        console.print("\n[dim]Press Ctrl+C to stop the server[/dim]")
        
        # Wait for interrupt
        try:
            while server_process.poll() is None:
                time.sleep(1)
        except KeyboardInterrupt:
            console.print("\n[yellow]🛑 Shutting down UI server...[/yellow]")
        
    except Exception as e:
        console.print(f"[red]Error starting UI server: {e}[/red]")
        raise typer.Exit(1)
    
    finally:
        # Clean up
        if server_process:
            server_process.terminate()
            try:
                server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server_process.kill()
        
        # Clean up temporary files
        try:
            if video_copy.exists() and video_copy != video_path:
                video_copy.unlink()
            if config_file.exists():
                config_file.unlink()
        except Exception:
            pass
        
        console.print("[green]✅ UI server stopped successfully[/green]")


@app.command()
def analyze(
    video_path: Path = typer.Argument(..., help="Path to video file to analyze"),
    interval: float = typer.Option(2.0, "--interval", "-i", help="Frame extraction interval in seconds"),
    confidence: float = typer.Option(0.7, "--confidence", "-c", help="Minimum confidence threshold"),
    output_dir: Path = typer.Option(Path("./output"), "--output", "-o", help="Output directory"),
    device: str = typer.Option("auto", "--device", "-d", help="Device to use (auto, cpu, cuda, mps)"),
    batch_size: int = typer.Option(1, "--batch-size", "-b", help="Batch size for processing"),
    save_frames: bool = typer.Option(True, "--save-frames/--no-save-frames", help="Save frames with fire"),
    format: str = typer.Option("json", "--format", "-f", help="Output format (json, csv, both)"),
    model_path: str = typer.Option("./models/gemma-3n-e4b", "--model-path", "-m", help="Path to model"),
    max_frames: Optional[int] = typer.Option(None, "--max-frames", help="Maximum frames to process"),
    start_time: float = typer.Option(0.0, "--start-time", help="Start time in seconds"),
    end_time: Optional[float] = typer.Option(None, "--end-time", help="End time in seconds"),
    ui: bool = typer.Option(False, "--ui", help="Launch web UI for interactive analysis"),
    stream: bool = typer.Option(False, "--stream", help="Stream frames for real-time analysis instead of pre-processing"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
    debug: bool = typer.Option(False, "--debug", help="Debug mode"),
):
    """Analyze video file for fire detection."""
    
    setup_logging(verbose, debug)
    
    if not video_path.exists():
        console.print(f"[red]Error: Video file not found: {video_path}[/red]")
        raise typer.Exit(1)
    
    # Launch UI mode if requested
    if ui:
        return launch_ui_mode(
            video_path=video_path,
            interval=interval,
            confidence=confidence,
            output_dir=output_dir,
            device=device,
            batch_size=batch_size,
            save_frames=save_frames,
            format=format,
            model_path=model_path,
            stream=stream,
            verbose=verbose,
            debug=debug
        )
    
    try:
        # Create configuration
        from gemma_3n.fire_detection.config import (
            Gemma3NE4BConfig,
            VideoProcessingConfig,
            DetectionConfig,
            OutputConfig
        )
        
        config = FireDetectionConfig(
            model=Gemma3NE4BConfig(model_path=model_path),
            video=VideoProcessingConfig(
                frame_interval=interval,
                max_frames=max_frames,
                start_time=start_time,
                end_time=end_time,
                batch_size=batch_size
            ),
            detection=DetectionConfig(
                confidence_threshold=confidence,
                save_positive_frames=save_frames
            ),
            output=OutputConfig(
                output_dir=output_dir,
                output_format=format
            ),
            device=device,
            debug=debug,
            verbose=verbose
        )
        
        # Initialize detector
        detector = FireDetector(config, console)
        
        # Process video (streaming or batch mode)
        if stream:
            console.print(f"[bold blue]🎥 Starting real-time streaming analysis...[/bold blue]")
            result = detector.process_video_stream(video_path)
        else:
            result = detector.process_video_sync(video_path)
        
        console.print(f"\n[bold green]Analysis complete![/bold green]")
        console.print(f"Results saved to: {output_dir}")
        
        if result.summary.fire_detections > 0:
            console.print(f"[bold red]🔥 Fire detected in {result.summary.fire_detections} frames![/bold red]")
        else:
            console.print(f"[bold green]✅ No fire detected[/bold green]")
        
    except Exception as e:
        console.print(f"[red]Error during analysis: {e}[/red]")
        if debug:
            console.print_exception()
        raise typer.Exit(1)


@app.command()
def preview(
    video_path: Path = typer.Argument(..., help="Path to video file"),
    frames: int = typer.Option(5, "--frames", "-n", help="Number of frames to preview"),
    interval: float = typer.Option(2.0, "--interval", "-i", help="Frame extraction interval"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """Preview frame extraction from video."""
    
    setup_logging(verbose)
    
    if not video_path.exists():
        console.print(f"[red]Error: Video file not found: {video_path}[/red]")
        raise typer.Exit(1)
    
    try:
        from gemma_3n.fire_detection.processing.frame_extractor import FrameExtractor
        from gemma_3n.fire_detection.config import VideoProcessingConfig
        
        config = VideoProcessingConfig(frame_interval=interval)
        extractor = FrameExtractor(config)
        
        # Get extraction stats
        stats = extractor.calculate_extraction_stats(video_path)
        
        # Show stats table
        table = Table(title=f"Video Analysis Preview: {video_path.name}")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Duration", f"{stats['video_duration']:.1f} seconds")
        table.add_row("FPS", f"{stats['video_fps']:.1f}")
        table.add_row("Total Frames", str(stats['total_frames']))
        table.add_row("Extraction Interval", f"{stats['extraction_interval']} seconds")
        table.add_row("Frames to Extract", str(stats['frames_to_extract']))
        table.add_row("Estimated Time", f"{stats['estimated_processing_time']:.1f} seconds")
        
        console.print(table)
        
        # Preview frames
        import asyncio
        preview_frames = asyncio.run(extractor.preview_extraction(video_path, frames))
        
        console.print(f"\n[bold]Preview extracted {len(preview_frames)} frames:[/bold]")
        for frame in preview_frames:
            console.print(f"  Frame {frame.frame_number}: {frame.timestamp:.3f}s")
        
    except Exception as e:
        console.print(f"[red]Error during preview: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def config(
    show: bool = typer.Option(False, "--show", help="Show current configuration"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Save config to file"),
):
    """Manage configuration settings."""
    
    try:
        config = FireDetectionConfig()
        
        if show:
            console.print("[bold]Current Configuration:[/bold]")
            console.print_json(config.model_dump_json(indent=2))
        
        if output:
            with open(output, 'w') as f:
                f.write(config.model_dump_json(indent=2))
            console.print(f"Configuration saved to: {output}")
        
        if not show and not output:
            console.print("Use --show to display configuration or --output to save it")
    
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def setup_model(
    model_path: Path = typer.Option(Path("./models/gemma-3n-e4b"), "--path", "-p", help="Model installation path"),
    force: bool = typer.Option(False, "--force", help="Force reinstall if model exists"),
):
    """Download and setup Gemma 3N E4B model."""
    
    if model_path.exists() and not force:
        console.print(f"[yellow]Model already exists at {model_path}[/yellow]")
        console.print("Use --force to reinstall")
        return
    
    try:
        console.print(f"[bold]Setting up Gemma 3N E4B model...[/bold]")
        console.print(f"Installation path: {model_path}")
        
        # Create model directory
        model_path.mkdir(parents=True, exist_ok=True)
        
        # Note: In a real implementation, this would download the actual model
        console.print("[yellow]Note: Model download functionality not implemented in this demo[/yellow]")
        console.print("[yellow]Please manually download the Gemma 3N E4B model to the specified path[/yellow]")
        
        # Create placeholder files to indicate setup
        (model_path / "config.json").write_text('{"model_type": "gemma-3n-e4b"}')
        (model_path / "README.txt").write_text("Gemma 3N E4B model files should be placed here")
        
        console.print(f"[green]Model setup completed at {model_path}[/green]")
        
    except Exception as e:
        console.print(f"[red]Error setting up model: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def batch(
    input_dir: Path = typer.Argument(..., help="Directory containing video files"),
    pattern: str = typer.Option("*.mp4", "--pattern", "-p", help="File pattern to match"),
    output_dir: Path = typer.Option(Path("./batch_output"), "--output", "-o", help="Output directory"),
    interval: float = typer.Option(2.0, "--interval", "-i", help="Frame extraction interval"),
    confidence: float = typer.Option(0.7, "--confidence", "-c", help="Confidence threshold"),
    device: str = typer.Option("auto", "--device", "-d", help="Device to use"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """Process multiple video files in batch."""
    
    setup_logging(verbose)
    
    if not input_dir.exists():
        console.print(f"[red]Error: Input directory not found: {input_dir}[/red]")
        raise typer.Exit(1)
    
    # Find video files
    video_files = list(input_dir.glob(pattern))
    
    if not video_files:
        console.print(f"[yellow]No video files found matching pattern: {pattern}[/yellow]")
        return
    
    console.print(f"[bold]Found {len(video_files)} video files to process[/bold]")
    
    try:
        # Process each video file
        for i, video_path in enumerate(video_files, 1):
            console.print(f"\n[bold cyan]Processing {i}/{len(video_files)}: {video_path.name}[/bold cyan]")
            
            # Create video-specific output directory
            video_output = output_dir / video_path.stem
            
            # Import config classes
            from gemma_3n.fire_detection.config import (
                VideoProcessingConfig,
                DetectionConfig,
                OutputConfig
            )
            
            # Create configuration
            config = FireDetectionConfig(
                video=VideoProcessingConfig(frame_interval=interval),
                detection=DetectionConfig(confidence_threshold=confidence),
                output=OutputConfig(output_dir=video_output),
                device=device,
                verbose=verbose
            )
            
            # Process video
            detector = FireDetector(config, console)
            result = detector.process_video_sync(video_path)
            
            if result.summary.fire_detections > 0:
                console.print(f"[red]🔥 Fire detected in {result.summary.fire_detections} frames[/red]")
            else:
                console.print(f"[green]✅ No fire detected[/green]")
        
        console.print(f"\n[bold green]Batch processing complete![/bold green]")
        console.print(f"Results saved to: {output_dir}")
        
    except Exception as e:
        console.print(f"[red]Error during batch processing: {e}[/red]")
        raise typer.Exit(1)


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
        if demo_dir.exists():
            for f in demo_dir.glob("*.json"):
                console.print(f"  - {f.stem}")
        else:
            console.print("[red]Demo directory not found![/red]")
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
        console.print("[yellow]Please ensure the demo-ui directory exists[/yellow]")
        api_process.terminate()
        raise typer.Exit(1)
    
    # Check if node_modules exists
    if not (ui_dir / "node_modules").exists():
        console.print("[yellow]Installing demo UI dependencies...[/yellow]")
        install_process = subprocess.run(
            ["npm", "install"],
            cwd=ui_dir,
            capture_output=True,
            text=True
        )
        if install_process.returncode != 0:
            console.print(f"[red]Failed to install dependencies: {install_process.stderr}[/red]")
            api_process.terminate()
            raise typer.Exit(1)
        console.print("[green]Dependencies installed successfully[/green]")
    
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


if __name__ == "__main__":
    app()