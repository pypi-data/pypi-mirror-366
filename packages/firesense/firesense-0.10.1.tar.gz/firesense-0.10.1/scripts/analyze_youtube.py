#!/usr/bin/env python3
"""YouTube video downloader and frame extractor."""

import json
import sys
import tempfile
from pathlib import Path
from typing import Any

import typer
from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.table import Table

try:
    import cv2

    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

try:
    import yt_dlp

    YT_DLP_AVAILABLE = True
except ImportError:
    YT_DLP_AVAILABLE = False

app = typer.Typer(
    name="analyze-youtube",
    help="Download YouTube videos and extract frames",
    no_args_is_help=True,
)
console = Console()


def validate_video_id(video_id: str) -> str:
    """Validate and clean YouTube video ID."""
    if "youtube.com/watch?v=" in video_id:
        video_id = video_id.split("watch?v=")[1].split("&")[0]
    elif "youtu.be/" in video_id:
        video_id = video_id.split("youtu.be/")[1].split("?")[0]

    if len(video_id) != 11:
        raise ValueError(f"Invalid YouTube video ID: {video_id}")

    return video_id


def download_video(video_id: str, output_path: Path, quality: str = "720p") -> bool:
    """Download YouTube video using yt-dlp."""
    if not YT_DLP_AVAILABLE:
        console.print("[red]Error: yt-dlp is not installed[/red]")
        console.print("Install with: [cyan]pip install yt-dlp[/cyan]")
        return False

    url = f"https://www.youtube.com/watch?v={video_id}"

    ydl_opts = {
        "outtmpl": str(output_path),
        "format": f"best[height<={quality[:-1]}][ext=mp4]/best[height<={quality[:-1]}]/best",
        "quiet": True,
        "no_warnings": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return True
    except Exception as e:
        console.print(f"[red]Download error: {e}[/red]")
        return False


def extract_frames_to_folder(
    video_path: Path, output_dir: Path, interval_seconds: int = 1
) -> list[dict[str, Any]]:
    """Extract frames from video at specified intervals and save to folder."""
    if not CV2_AVAILABLE:
        raise ImportError(
            "opencv-python is required. Install with: pip install opencv-python"
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    frames_info = []
    cap = cv2.VideoCapture(str(video_path))

    if not cap.isOpened():
        raise ValueError(f"Cannot open video: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    interval_frames = int(fps * interval_seconds)

    frame_count = 0
    current_frame = 0

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:

        total_extractions = (total_frames // interval_frames) + 1
        task = progress.add_task("Extracting frames...", total=total_extractions)

        while current_frame < total_frames:
            cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame)
            ret, frame = cap.read()
            if ret:
                # Save frame as image
                timestamp = current_frame / fps
                frame_filename = f"frame_{frame_count:04d}_t{timestamp:.1f}s.jpg"
                frame_path = output_dir / frame_filename

                # Save with high quality
                cv2.imwrite(str(frame_path), frame, [cv2.IMWRITE_JPEG_QUALITY, 95])

                frames_info.append(
                    {
                        "frame_number": frame_count,
                        "timestamp": timestamp,
                        "filename": frame_filename,
                        "path": frame_path,
                    }
                )

                frame_count += 1
                progress.advance(task)

            current_frame += interval_frames

    cap.release()
    return frames_info


@app.command()
def extract(
    video_id: str = typer.Argument(..., help="YouTube video ID or URL"),
    interval: int = typer.Option(
        1, "--interval", "-i", help="Seconds between frame extractions (default: 1)"
    ),
    quality: str = typer.Option(
        "720p", "--quality", "-q", help="Video quality to download"
    ),
    output_dir: Path = typer.Option(
        Path("youtube_frames"), "--output", "-o", help="Base output directory"
    ),
):
    """Download YouTube video and extract frames to a folder named after the video ID.

    Examples:
        analyze_youtube 6evFKKruJ0c
        analyze_youtube https://www.youtube.com/watch?v=6evFKKruJ0c --interval 2
        analyze_youtube video_id --quality 1080p --output custom_dir
    """
    try:
        # Validate video ID
        clean_video_id = validate_video_id(video_id)
        console.print(
            f"[bold blue]Processing YouTube video: {clean_video_id}[/bold blue]"
        )

        # Create output directory with video ID name
        video_output_dir = output_dir / clean_video_id
        video_output_dir.mkdir(parents=True, exist_ok=True)
        console.print(f"[green]✓ Created output directory: {video_output_dir}[/green]")

        # Download video to temporary location
        with tempfile.TemporaryDirectory() as tmp_dir:
            video_path = Path(tmp_dir) / f"{clean_video_id}.mp4"

            # Download video
            console.print("[yellow]Downloading video...[/yellow]")
            if not download_video(clean_video_id, video_path, quality):
                raise typer.Exit(1)

            console.print("[green]✓ Video downloaded[/green]")

            # Extract frames to output directory
            console.print(
                f"[yellow]Extracting frames (every {interval} second(s))...[/yellow]"
            )
            frames_info = extract_frames_to_folder(
                video_path, video_output_dir, interval
            )
            console.print(
                f"[green]✓ Extracted {len(frames_info)} frames to {video_output_dir}[/green]"
            )

            # Save video metadata
            metadata_path = video_output_dir / "metadata.json"
            # Convert Path objects to strings for JSON serialization
            frames_metadata = [
                {
                    "frame_number": f["frame_number"],
                    "timestamp": f["timestamp"],
                    "filename": f["filename"],
                }
                for f in frames_info
            ]

            with open(metadata_path, "w") as f:
                json.dump(
                    {
                        "video_id": clean_video_id,
                        "url": f"https://www.youtube.com/watch?v={clean_video_id}",
                        "interval_seconds": interval,
                        "total_frames": len(frames_info),
                        "frames": frames_metadata,
                    },
                    f,
                    indent=2,
                )

            # Summary
            console.print("\n[bold]Summary:[/bold]")
            console.print(f"Video ID: {clean_video_id}")
            console.print(f"Output directory: {video_output_dir}")
            console.print(f"Total frames extracted: {len(frames_info)}")
            console.print(f"Frame interval: {interval} second(s)")
            console.print(
                f"Duration covered: {frames_info[-1]['timestamp']:.1f} seconds"
                if frames_info
                else "0 seconds"
            )

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def batch(
    video_ids_file: Path = typer.Argument(
        ..., help="File containing YouTube video IDs (one per line)"
    ),
    interval: int = typer.Option(
        1, "--interval", "-i", help="Seconds between frame extractions"
    ),
    output_dir: Path = typer.Option(
        Path("youtube_frames"), "--output", "-o", help="Output directory"
    ),
):
    """Extract frames from multiple YouTube videos listed in a file."""
    if not video_ids_file.exists():
        console.print(f"[red]File not found: {video_ids_file}[/red]")
        raise typer.Exit(1)

    video_ids = video_ids_file.read_text().strip().split("\n")
    video_ids = [vid.strip() for vid in video_ids if vid.strip()]

    console.print(f"[bold]Processing {len(video_ids)} videos[/bold]")

    for i, video_id in enumerate(video_ids, 1):
        console.print(
            f"\n[bold blue]Video {i}/{len(video_ids)}: {video_id}[/bold blue]"
        )

        try:
            # Run extraction for each video
            result = sys.exit(
                app(
                    [
                        "extract",
                        video_id,
                        "--interval",
                        str(interval),
                        "--output",
                        str(output_dir),
                    ],
                    standalone_mode=False,
                )
            )

            if result == 0:
                console.print("[green]✓ Extraction completed[/green]")
            else:
                console.print("[red]✗ Extraction failed[/red]")
        except Exception as e:
            console.print(f"[red]✗ Error: {e}[/red]")


@app.command()
def info(
    video_id: str = typer.Argument(..., help="YouTube video ID or URL"),
):
    """Get information about a YouTube video without downloading."""
    if not YT_DLP_AVAILABLE:
        console.print("[red]Error: yt-dlp is not installed[/red]")
        console.print("Install with: [cyan]pip install yt-dlp[/cyan]")
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

            # Show frame extraction estimate
            duration = info.get("duration", 0)
            if duration > 0:
                frames_at_1s = duration
                console.print("\n[bold]Frame Extraction Estimate:[/bold]")
                console.print(f"Frames at 1s interval: ~{frames_at_1s}")
                console.print(
                    f"Estimated file size: ~{frames_at_1s * 50}KB - {frames_at_1s * 100}KB"
                )

                if duration > 300:  # 5 minutes
                    console.print(
                        "[yellow]⚠️  Long video - consider using larger interval[/yellow]"
                    )

    except Exception as e:
        console.print(f"[red]Error getting video info: {e}[/red]")
        raise typer.Exit(1)


def main():
    """CLI entry point."""
    app()


if __name__ == "__main__":
    main()
