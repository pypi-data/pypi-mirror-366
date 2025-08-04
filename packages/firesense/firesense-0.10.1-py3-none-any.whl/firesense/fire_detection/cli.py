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
    video_id: str = typer.Argument(
        "yvJXFiDQaSc", help="Demo video ID to display (default: yvJXFiDQaSc)"
    ),
    port: int = typer.Option(8000, "--port", help="Server port for both API and UI"),
    no_browser: bool = typer.Option(
        False, "--no-browser", help="Don't open browser automatically"
    ),
    local: bool = typer.Option(
        False, "--local", help="Use localdemo folder instead of demo folder"
    ),
    ngrok: bool = typer.Option(
        False, "--ngrok", help="Expose server via ngrok tunnel for remote access"
    ),
) -> None:
    """Launch demo UI for pre-analyzed fire detection results."""

    # Workaround for typer bug with default arguments
    if video_id.isdigit() and len(video_id) == 1:
        video_id = "yvJXFiDQaSc"

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
        env=env,
    )

    # Wait for server to start
    time.sleep(2)

    # Set up ngrok tunnel if requested
    public_url = None
    ngrok_tunnel = None
    if ngrok:
        try:
            from pyngrok import ngrok as pyngrok
            from pyngrok.conf import PyngrokConfig

            # Configure pyngrok to not open browser
            pyngrok_config = PyngrokConfig(monitor_thread=False)

            console.print("[blue]Creating ngrok tunnel...[/blue]")
            ngrok_tunnel = pyngrok.connect(port, pyngrok_config=pyngrok_config)
            public_url = ngrok_tunnel.public_url
            console.print(f"[green]🌐 Ngrok tunnel created: {public_url}[/green]")
        except Exception as e:
            console.print(f"[yellow]⚠️  Could not create ngrok tunnel: {e}[/yellow]")
            console.print("[yellow]Continuing with local server only...[/yellow]")
            ngrok = False  # Disable ngrok for cleanup

    # Open browser
    if not no_browser:
        if public_url:
            url = f"{public_url}?id={video_id}"
            console.print(f"[blue]Opening browser at: {url}[/blue]")
        else:
            url = f"http://localhost:{port}?id={video_id}"
            console.print(f"[blue]Opening browser at: {url}[/blue]")
        webbrowser.open(url)

    console.print("\n[bold yellow]Demo server running![/bold yellow]")
    console.print(f"[blue]🌐 Local: http://localhost:{port}[/blue]")
    if public_url:
        console.print(f"[blue]🌍 Public: {public_url}[/blue]")
    console.print(f"[blue]📹 Video: {video_id}[/blue]")
    console.print("\n[dim]Press Ctrl+C to stop the server[/dim]")

    try:
        # Wait for process to exit
        while server_process.poll() is None:
            time.sleep(1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Shutting down server...[/yellow]")
    finally:
        # Cleanup ngrok tunnel
        if ngrok and ngrok_tunnel:
            try:
                from pyngrok import ngrok as pyngrok

                console.print("[yellow]Closing ngrok tunnel...[/yellow]")
                pyngrok.disconnect(ngrok_tunnel.public_url)
                pyngrok.kill()
            except Exception:
                pass  # Ignore errors during cleanup

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
    video_id: str = typer.Argument(
        "yvJXFiDQaSc", help="YouTube video ID or URL to analyze (default: yvJXFiDQaSc)"
    ),
    interval: float = typer.Option(
        1.0, "--interval", "-i", help="Frame extraction interval in seconds"
    ),
    output_dir: Path = typer.Option(
        ".", "--output", "-o", help="Output directory for results"
    ),
) -> None:
    """Download YouTube video, extract frames, and analyze for fire detection."""

    # Workaround for typer bug with default arguments
    if video_id.isdigit() and len(video_id) == 1:
        video_id = "yvJXFiDQaSc"

    console.print("[bold green]🔥 Starting Fire Detection Analysis[/bold green]")

    # Check GPU availability
    import torch

    gpu_available = torch.cuda.is_available()

    if not gpu_available:
        console.print("\n[yellow]⚠️  GPU Not Available - Using Mock Inference[/yellow]")
        console.print(
            "[dim]Running with mock inference that generates random results for demonstration.[/dim]"
        )
        console.print(
            "[dim]For real fire detection, a CUDA-capable GPU is required.[/dim]"
        )
        console.print()

    console.print(f"[blue]Video ID: {video_id}[/blue]")
    console.print(f"[blue]Frame interval: {interval}s[/blue]")
    console.print(f"[blue]Output directory: {output_dir}[/blue]")
    console.print(
        f"[blue]GPU Available: {'Yes' if gpu_available else 'No (Mock Mode)'}[/blue]"
    )

    try:
        # Run the appropriate analysis based on GPU availability
        if gpu_available:
            output_file = process_video_inference(
                video_id=video_id, interval_seconds=interval, output_dir=str(output_dir)
            )
        else:
            output_file = process_video_inference_mock(
                video_id=video_id, interval_seconds=interval, output_dir=str(output_dir)
            )

        console.print("\n[bold green]✅ Analysis complete![/bold green]")
        console.print(f"[blue]Results saved to: {output_file}[/blue]")

    except Exception as e:
        console.print(f"[red]Error during analysis: {e}[/red]")
        raise typer.Exit(1) from e


if __name__ == "__main__":
    app()
