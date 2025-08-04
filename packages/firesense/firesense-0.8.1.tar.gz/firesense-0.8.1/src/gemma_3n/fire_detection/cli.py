"""Command-line interface for fire detection system."""

import subprocess
import sys
import time
import webbrowser
from pathlib import Path

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
    video_id: str = typer.Argument(..., help="Demo video ID to display"),
    api_port: int = typer.Option(8000, "--api-port", help="FastAPI server port"),
    ui_port: int = typer.Option(5173, "--ui-port", help="React dev server port"),
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

    # Start FastAPI server
    console.print(f"[blue]Starting API server on port {api_port}...[/blue]")
    # Set environment variable for demo server to know which folder to use
    env = os.environ.copy()
    env["DEMO_LOCAL_MODE"] = "1" if local else "0"
    api_process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "src.gemma_3n.fire_detection.demo_server:app",
            "--port",
            str(api_port),
            "--host",
            "0.0.0.0",
            "--reload",
        ],
        env=env
    )

    # Start React dev server
    # demo-ui is in the package installation directory
    package_root = Path(__file__).parent.parent.parent.parent
    ui_dir = package_root / "demo-ui"
    if not ui_dir.exists():
        console.print(f"[red]Error: Demo UI not found at {ui_dir}[/red]")
        api_process.terminate()
        raise typer.Exit(1)

    # Check if node_modules exists
    if not (ui_dir / "node_modules").exists():
        console.print("[yellow]Installing demo UI dependencies...[/yellow]")
        install_process = subprocess.run(
            ["npm", "install"], cwd=ui_dir, capture_output=True, text=True
        )
        if install_process.returncode != 0:
            console.print(
                f"[red]Failed to install dependencies: {install_process.stderr}[/red]"
            )
            api_process.terminate()
            raise typer.Exit(1)
        console.print("[green]Dependencies installed successfully[/green]")

    console.print(f"[blue]Starting UI server on port {ui_port}...[/blue]")
    ui_process = subprocess.Popen(
        ["npm", "run", "dev", "--", "--port", str(ui_port)], cwd=ui_dir
    )

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


@app.command()
def analyze(
    video_id: str = typer.Argument(..., help="YouTube video ID or URL to analyze"),
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
