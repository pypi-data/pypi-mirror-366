#!/usr/bin/env python3
"""YouTube video downloader for fire detection testing."""

from pathlib import Path

import typer
from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)

try:
    import yt_dlp

    YT_DLP_AVAILABLE = True
except ImportError:
    YT_DLP_AVAILABLE = False

app = typer.Typer(
    name="get-youtube",
    help="Download YouTube videos for fire detection testing",
    no_args_is_help=True,
)
console = Console()


def validate_video_id(video_id: str) -> str:
    """Validate and clean YouTube video ID.

    Args:
        video_id: YouTube video ID or URL

    Returns:
        Clean video ID

    Raises:
        ValueError: If video ID is invalid
    """
    # Handle full YouTube URLs
    if "youtube.com/watch?v=" in video_id:
        video_id = video_id.split("watch?v=")[1].split("&")[0]
    elif "youtu.be/" in video_id:
        video_id = video_id.split("youtu.be/")[1].split("?")[0]

    # Basic validation - YouTube video IDs are 11 characters
    if len(video_id) != 11:
        raise ValueError(f"Invalid YouTube video ID: {video_id}")

    # Check for valid characters (alphanumeric, -, _)
    valid_chars = set(
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_"
    )
    if not all(c in valid_chars for c in video_id):
        raise ValueError(f"Invalid characters in video ID: {video_id}")

    return video_id


class ProgressHook:
    """Progress hook for yt-dlp downloads."""

    def __init__(self, progress: Progress, task_id):
        """Initialize progress hook.

        Args:
            progress: Rich progress instance
            task_id: Progress task ID
        """
        self.progress = progress
        self.task_id = task_id
        self.total_bytes = None

    def __call__(self, d):
        """Handle progress updates from yt-dlp.

        Args:
            d: Progress dictionary from yt-dlp
        """
        if d["status"] == "downloading":
            if self.total_bytes is None and "total_bytes" in d:
                self.total_bytes = d["total_bytes"]
                self.progress.update(self.task_id, total=self.total_bytes)

            if "downloaded_bytes" in d:
                self.progress.update(self.task_id, completed=d["downloaded_bytes"])

        elif d["status"] == "finished":
            self.progress.update(self.task_id, completed=self.total_bytes or 100)


@app.command()
def download(
    video_id: str = typer.Argument(..., help="YouTube video ID or URL"),
    filename: str = typer.Argument(..., help="Output filename (e.g., fire_test.mp4)"),
    quality: str = typer.Option(
        "720p", "--quality", "-q", help="Video quality (720p, 1080p, worst, best)"
    ),
    output_dir: Path = typer.Option(
        Path("data/sample_videos"), "--output", "-o", help="Output directory"
    ),
    overwrite: bool = typer.Option(
        False, "--overwrite", "-f", help="Overwrite existing file"
    ),
    audio_only: bool = typer.Option(
        False, "--audio-only", "-a", help="Download audio only"
    ),
    max_duration: int | None = typer.Option(
        None, "--max-duration", "-d", help="Max duration in seconds"
    ),
):
    """Download a YouTube video for fire detection testing.

    Examples:
        get_youtube dQw4w9WgXcQ fire_test.mp4
        get_youtube https://www.youtube.com/watch?v=dQw4w9WgXcQ fire_demo.mp4 --quality 1080p
        get_youtube dQw4w9WgXcQ audio.mp4 --audio-only
    """
    if not YT_DLP_AVAILABLE:
        console.print("[red]Error: yt-dlp is not installed[/red]")
        console.print("Install with: [cyan]uv pip install -e '.[youtube]'[/cyan]")
        raise typer.Exit(1)

    try:
        # Validate video ID
        clean_video_id = validate_video_id(video_id)
        url = f"https://www.youtube.com/watch?v={clean_video_id}"

        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / filename

        # Check if file exists
        if output_path.exists() and not overwrite:
            console.print(f"[yellow]File already exists: {output_path}[/yellow]")
            console.print("Use --overwrite to replace it")
            raise typer.Exit(1)

        console.print("[bold blue]Downloading YouTube video[/bold blue]")
        console.print(f"Video ID: {clean_video_id}")
        console.print(f"URL: {url}")
        console.print(f"Output: {output_path}")
        console.print(f"Quality: {quality}")

        # Configure yt-dlp options
        ydl_opts = {
            "outtmpl": str(output_path.with_suffix("")),  # yt-dlp will add extension
            "format": _get_format_selector(quality, audio_only),
            "noplaylist": True,
            "extract_flat": False,
        }

        # Add duration filter if specified
        if max_duration:
            ydl_opts["match_filter"] = lambda info: (
                "Video too long" if info.get("duration", 0) > max_duration else None
            )

        # Download with progress tracking
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=console,
        ) as progress:

            task_id = progress.add_task("Downloading video...", total=100)

            # Add progress hook
            ydl_opts["progress_hooks"] = [ProgressHook(progress, task_id)]

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Get video info first
                progress.update(task_id, description="Getting video info...")
                info = ydl.extract_info(url, download=False)

                # Validate duration if specified
                if max_duration and info.get("duration", 0) > max_duration:
                    console.print(
                        f"[red]Video too long: {info.get('duration')}s > {max_duration}s[/red]"
                    )
                    raise typer.Exit(1)

                # Show video info
                title = info.get("title", "Unknown")
                duration = info.get("duration", 0)
                uploader = info.get("uploader", "Unknown")

                console.print("\n[bold]Video Info:[/bold]")
                console.print(f"Title: {title}")
                console.print(f"Uploader: {uploader}")
                console.print(
                    f"Duration: {duration}s ({duration//60}:{duration%60:02d})"
                )

                # Download the video
                progress.update(task_id, description="Downloading video...")
                ydl.download([url])

        # Find the downloaded file (yt-dlp might change the extension or have no extension)
        downloaded_files = list(output_dir.glob(f"{output_path.stem}*"))
        if downloaded_files:
            actual_file = downloaded_files[0]

            # Rename to desired filename if needed
            if actual_file != output_path:
                if output_path.exists():
                    output_path.unlink()
                actual_file.rename(output_path)

            console.print("\n[bold green]✅ Download completed![/bold green]")
            console.print(f"File saved: {output_path}")
            console.print(f"File size: {_format_bytes(output_path.stat().st_size)}")

            # Show usage example
            console.print("\n[bold]Test with fire detection:[/bold]")
            console.print(f"[cyan]uv run gemma-3n fire-detect {output_path}[/cyan]")

        else:
            console.print("[red]Error: Download completed but file not found[/red]")
            raise typer.Exit(1)

    except yt_dlp.DownloadError as e:
        console.print(f"[red]Download error: {e}[/red]")
        raise typer.Exit(1)
    except ValueError as e:
        console.print(f"[red]Validation error: {e}[/red]")
        raise typer.Exit(1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Download cancelled by user[/yellow]")
        raise typer.Exit(130)
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def info(
    video_id: str = typer.Argument(..., help="YouTube video ID or URL"),
):
    """Get information about a YouTube video without downloading."""
    if not YT_DLP_AVAILABLE:
        console.print("[red]Error: yt-dlp is not installed[/red]")
        console.print("Install with: [cyan]uv pip install -e '.[youtube]'[/cyan]")
        raise typer.Exit(1)

    try:
        clean_video_id = validate_video_id(video_id)
        url = f"https://www.youtube.com/watch?v={clean_video_id}"

        console.print("[bold blue]Getting video info...[/bold blue]")

        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            # Display video information
            from rich.table import Table

            table = Table(title=f"YouTube Video Info: {clean_video_id}")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="green")

            table.add_row("Title", info.get("title", "N/A"))
            table.add_row("Uploader", info.get("uploader", "N/A"))
            table.add_row(
                "Duration",
                f"{info.get('duration', 0)}s ({info.get('duration', 0)//60}:{info.get('duration', 0)%60:02d})",
            )
            table.add_row("View Count", f"{info.get('view_count', 0):,}")
            table.add_row("Upload Date", info.get("upload_date", "N/A"))
            table.add_row(
                "Description",
                (
                    info.get("description", "")[:100] + "..."
                    if len(info.get("description", "")) > 100
                    else info.get("description", "N/A")
                ),
            )

            # Available formats
            formats = info.get("formats", [])
            video_formats = [f for f in formats if f.get("vcodec") != "none"]
            if video_formats:
                qualities = list(
                    {
                        f"{f.get('height', 'N/A')}p"
                        for f in video_formats
                        if f.get("height")
                    }
                )
                table.add_row(
                    "Available Qualities",
                    ", ".join(
                        sorted(
                            qualities,
                            key=lambda x: int(x[:-1]) if x[:-1].isdigit() else 0,
                            reverse=True,
                        )
                    ),
                )

            console.print(table)

            # Show suitable for fire detection
            duration = info.get("duration", 0)
            if duration > 0:
                frames_at_2s = duration // 2
                console.print("\n[bold]Fire Detection Suitability:[/bold]")
                console.print(f"Frames to extract (2s interval): ~{frames_at_2s}")
                console.print(
                    f"Estimated processing time: ~{frames_at_2s * 0.5:.1f}s (CPU)"
                )

                if duration > 300:  # 5 minutes
                    console.print(
                        "[yellow]⚠️  Long video - consider using --max-duration flag[/yellow]"
                    )
                elif duration < 10:
                    console.print(
                        "[yellow]⚠️  Very short video - might not be suitable for testing[/yellow]"
                    )
                else:
                    console.print(
                        "[green]✅ Good length for fire detection testing[/green]"
                    )

    except Exception as e:
        console.print(f"[red]Error getting video info: {e}[/red]")
        raise typer.Exit(1)


def _get_format_selector(quality: str, audio_only: bool) -> str:
    """Get yt-dlp format selector based on quality and audio preferences.

    Args:
        quality: Quality preference
        audio_only: Whether to download audio only

    Returns:
        Format selector string
    """
    if audio_only:
        return "bestaudio/best"

    quality_map = {
        "worst": "worst[ext=mp4]/worst",
        "360p": "best[height<=360][ext=mp4]/best[height<=360]",
        "480p": "best[height<=480][ext=mp4]/best[height<=480]",
        "720p": "best[height<=720][ext=mp4]/best[height<=720]",
        "1080p": "best[height<=1080][ext=mp4]/best[height<=1080]",
        "best": "best[ext=mp4]/best",
    }

    return quality_map.get(quality, "best[height<=720][ext=mp4]/best[height<=720]")


def _format_bytes(num_bytes: int) -> str:
    """Format bytes to human readable string.

    Args:
        num_bytes: Number of bytes

    Returns:
        Formatted string
    """
    for unit in ["B", "KB", "MB", "GB"]:
        if abs(num_bytes) < 1024.0:
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024.0
    return f"{num_bytes:.1f} TB"


def main():
    """CLI entry point."""
    app()


if __name__ == "__main__":
    main()
