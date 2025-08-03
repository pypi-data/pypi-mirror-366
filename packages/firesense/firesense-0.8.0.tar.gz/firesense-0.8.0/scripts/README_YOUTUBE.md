# YouTube Video Downloader for Fire Detection Testing

A utility script to download YouTube videos for testing the fire detection system.

## Installation

Install the YouTube download dependencies:

```bash
uv sync --extra youtube
```

## Usage

### Method 1: Wrapper Script (Recommended)

```bash
# Download a video by ID (simple wrapper)
./get_youtube VIDEO_ID filename.mp4

# Examples
./get_youtube 6evFKKruJ0c fire_test.mp4
./get_youtube ABC123XYZ demo.mp4 --quality 480p
```

### Method 2: Direct Python Script

```bash
# Download a video by ID
uv run python scripts/get_youtube.py download VIDEO_ID filename.mp4

# Download with specific quality
uv run python scripts/get_youtube.py download VIDEO_ID filename.mp4 --quality 720p

# Download short videos only (max 60 seconds)
uv run python scripts/get_youtube.py download VIDEO_ID filename.mp4 --max-duration 60
```

### Get Video Information

```bash
# Get info about a video before downloading
uv run python scripts/get_youtube.py info VIDEO_ID
```

### Examples

```bash
# Download a fire safety demonstration video (wrapper script)
./get_youtube 6evFKKruJ0c fire_demo.mp4 --quality 480p --max-duration 120

# Download using direct Python script
uv run python scripts/get_youtube.py download ABC123XYZ fire_demo.mp4 --quality 480p --max-duration 120

# Get info about a video
uv run python scripts/get_youtube.py info 6evFKKruJ0c

# Download with overwrite protection
./get_youtube ABC123XYZ test_video.mp4 --overwrite
```

## Command Options

### Download Command

- `video_id`: YouTube video ID or full URL
- `filename`: Output filename (e.g., `fire_test.mp4`)
- `--quality, -q`: Video quality (`720p`, `1080p`, `worst`, `best`) - default: `720p`
- `--output, -o`: Output directory - default: `data/sample_videos`
- `--overwrite, -f`: Overwrite existing files
- `--audio-only, -a`: Download audio only
- `--max-duration, -d`: Maximum duration in seconds

### Info Command

- `video_id`: YouTube video ID or URL to get information about

## Fire Detection Integration

Once downloaded, test videos with the fire detection system:

```bash
# Test with fire detection
uv run gemma-3n fire-detect data/sample_videos/your_video.mp4

# Or use the standalone CLI
uv run python -m gemma_3n.fire_detection.cli analyze data/sample_videos/your_video.mp4
```

## Video ID Formats

The script accepts various YouTube URL formats:

- Video ID: `dQw4w9WgXcQ`
- Full URL: `https://www.youtube.com/watch?v=dQw4w9WgXcQ`
- Short URL: `https://youtu.be/dQw4w9WgXcQ`

## Recommended Test Videos

For fire detection testing, look for videos with:

- **Duration**: 30 seconds to 5 minutes (optimal for testing)
- **Content**: Fire, flames, smoke, combustion demonstrations
- **Quality**: 480p or higher for better detection accuracy
- **Examples**:
  - Fire safety demonstrations
  - Controlled burn footage
  - Campfire videos
  - Industrial fire testing
  - Educational fire science content

## Fire Detection Suitability

The info command shows estimated suitability:

- **Frames to extract**: Based on 2-second intervals
- **Processing time**: Rough CPU estimate
- **Recommendations**: 
  - ✅ 10 seconds to 5 minutes: Good for testing
  - ⚠️ Under 10 seconds: Might be too short
  - ⚠️ Over 5 minutes: Consider using `--max-duration`

## Quality Settings

- `worst`: Lowest quality, fastest download
- `360p`: Low quality, good for quick tests  
- `480p`: Medium quality, balanced (recommended)
- `720p`: High quality, good detail (default)
- `1080p`: Full HD, best quality
- `best`: Highest available quality

## Output Structure

Downloaded videos are saved to:
```
data/sample_videos/
├── fire_demo.mp4
├── campfire_test.mp4
└── industrial_fire.mp4
```

## Error Handling

The script handles common issues:

- **Invalid video ID**: Validates format and characters
- **Video too long**: Respects `--max-duration` setting
- **Download errors**: Shows clear error messages
- **File conflicts**: Prevents overwriting unless `--overwrite` is used
- **Network issues**: Provides informative error messages

## Dependencies

- `yt-dlp>=2023.12.30`: YouTube download functionality
- `typer`: Command-line interface
- `rich`: Progress bars and formatting

## Legal Considerations

- Only download videos you have permission to use
- Respect copyright and terms of service
- Use for testing and educational purposes
- Consider video licensing before redistribution