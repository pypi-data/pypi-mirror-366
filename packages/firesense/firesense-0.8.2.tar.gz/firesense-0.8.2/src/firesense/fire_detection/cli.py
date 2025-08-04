"""Command-line interface for fire detection system."""

import subprocess
import sys
import time
import webbrowser
from pathlib import Path
import importlib.resources

import typer
from rich.console import Console

from .inference import process_video_inference
from .mock_inference_pipeline import process_video_inference_mock

app = typer.Typer(
    name="firesense",
    help="Fire detection system using Gemma 3N E4B model",
    no_args_is_help=True,
)
console = Console()


@app.command()
def demo(
    video_id: str = typer.Argument("8khG4WzS70U", help="Demo video ID to display (default: 8khG4WzS70U)"),
    port: int = typer.Option(8000, "--port", help="Server port for both API and UI"),
    no_browser: bool = typer.Option(
        False, "--no-browser", help="Don't open browser automatically"
    ),
    local: bool = typer.Option(
        False, "--local", help="Use localdemo folder instead of demo folder"
    ),
) -> None:
    """Launch demo UI for pre-analyzed fire detection results."""

    console.print("[bold green]🔥 Launching Fire Detection Demo[/bold green]")
    console.print(f"[blue]Video ID: {video_id}[/blue]")
    console.print(f"[blue]Demo folder: {'localdemo' if local else 'demo'}[/blue]")

    # Verify demo files exist
    demo_dir = Path.cwd() / ("localdemo" if local else "demo")
    demo_file = demo_dir / f"{video_id}.json"

    if not demo_file.exists():
        console.print(f"[red]Error: Demo JSON file not found: {demo_file}[/red]")
        console.print("[yellow]Available demos:[/yellow]")
        if demo_dir.exists():
            for f in demo_dir.glob("*.json"):
                console.print(f"  - {f.stem}")
        else:
            console.print("[red]Demo directory not found![/red]")
        raise typer.Exit(1)

    # Use current working directory
    import os

    # Start FastAPI server with UI serving
    console.print(f"[blue]Starting demo server on port {port}...[/blue]")
    # Set environment variable for demo server to know which folder to use
    env = os.environ.copy()
    env["DEMO_LOCAL_MODE"] = "1" if local else "0"
    server_process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "firesense.fire_detection.demo_server:app",
            "--port",
            str(port),
            "--host",
            "0.0.0.0",
        ],
        env=env
    )

    # Wait for server to start
    time.sleep(2)

    # Open browser
    if not no_browser:
        url = f"http://localhost:{port}?id={video_id}"
        console.print(f"[blue]Opening browser at: {url}[/blue]")
        webbrowser.open(url)

    console.print("\n[bold yellow]Demo server running![/bold yellow]")
    console.print(f"[blue]🌐 Server: http://localhost:{port}[/blue]")
    console.print(f"[blue]📹 Video: {video_id}[/blue]")
    console.print("\n[dim]Press Ctrl+C to stop the server[/dim]")

    try:
        # Wait for process to exit
        while server_process.poll() is None:
            time.sleep(1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Shutting down server...[/yellow]")
    finally:
        # Cleanup process
        if server_process.poll() is None:
            server_process.terminate()
            try:
                server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server_process.kill()

        console.print("[green]✅ Demo server stopped[/green]")


@app.command()
def analyze(
    video_id: str = typer.Argument("8khG4WzS70U", help="YouTube video ID or URL to analyze (default: 8khG4WzS70U)"),
    interval: float = typer.Option(
        1.0, "--interval", "-i", help="Frame extraction interval in seconds"
    ),
    output_dir: Path = typer.Option(  # noqa: B008
        ".", "--output", "-o", help="Output directory for results"
    ),
) -> None:
    """Download YouTube video, extract frames, and analyze for fire detection."""

    console.print("[bold green]🔥 Starting Fire Detection Analysis[/bold green]")
    
    # Check GPU availability
    import torch
    gpu_available = torch.cuda.is_available()
    
    if not gpu_available:
        console.print("\n[yellow]⚠️  GPU Not Available - Using Mock Inference[/yellow]")
        console.print("[dim]Running with mock inference that generates random results for demonstration.[/dim]")
        console.print("[dim]For real fire detection, a CUDA-capable GPU is required.[/dim]")
        console.print()
    
    console.print(f"[blue]Video ID: {video_id}[/blue]")
    console.print(f"[blue]Frame interval: {interval}s[/blue]")
    console.print(f"[blue]Output directory: {output_dir}[/blue]")
    console.print(f"[blue]GPU Available: {'Yes' if gpu_available else 'No (Mock Mode)'}[/blue]")

    try:
        # Run the appropriate analysis based on GPU availability
        if gpu_available:
            output_file = process_video_inference(
                video_id=video_id, 
                interval_seconds=interval, 
                output_dir=str(output_dir)
            )
        else:
            output_file = process_video_inference_mock(
                video_id=video_id, 
                interval_seconds=interval, 
                output_dir=str(output_dir)
            )

        console.print("\n[bold green]✅ Analysis complete![/bold green]")
        console.print(f"[blue]Results saved to: {output_file}[/blue]")

    except Exception as e:
        console.print(f"[red]Error during analysis: {e}[/red]")
        raise typer.Exit(1) from e


if __name__ == "__main__":
    app()
