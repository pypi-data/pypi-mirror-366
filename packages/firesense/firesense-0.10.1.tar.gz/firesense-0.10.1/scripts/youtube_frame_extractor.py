# pip install yt-dlp opencv-python

import tempfile
from pathlib import Path

import cv2
import yt_dlp


def validate_video_id(video_id):
    """Validate and clean YouTube video ID."""
    if "youtube.com/watch?v=" in video_id:
        video_id = video_id.split("watch?v=")[1].split("&")[0]
    elif "youtu.be/" in video_id:
        video_id = video_id.split("youtu.be/")[1].split("?")[0]

    if len(video_id) != 11:
        raise ValueError(f"Invalid YouTube video ID: {video_id}")

    return video_id


def download_and_extract_frames(
    video_id, interval_seconds=1, quality="720p", output_base_dir="youtube_frames"
):
    """Download YouTube video and extract frames at specified intervals."""

    # Validate video ID
    clean_video_id = validate_video_id(video_id)
    print(f"Processing YouTube video: {clean_video_id}")

    # Create output directory
    output_dir = Path(output_base_dir) / clean_video_id
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"Created output directory: {output_dir}")

    # Download video
    with tempfile.TemporaryDirectory() as tmp_dir:
        video_path = Path(tmp_dir) / f"{clean_video_id}.mp4"

        # Download video using yt-dlp
        print("Downloading video...")
        url = f"https://www.youtube.com/watch?v={clean_video_id}"
        ydl_opts = {
            "outtmpl": str(video_path),
            "format": f"best[height<={quality[:-1]}][ext=mp4]/best[height<={quality[:-1]}]/best",
            "quiet": True,
            "no_warnings": True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print("Video downloaded")

        # Extract frames
        print(f"Extracting frames (every {interval_seconds} second(s))...")
        cap = cv2.VideoCapture(str(video_path))

        if not cap.isOpened():
            raise ValueError(f"Cannot open video: {video_path}")

        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        interval_frames = int(fps * interval_seconds)

        frame_count = 0
        current_frame = 0
        extracted_frames = []

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

                extracted_frames.append(
                    {
                        "frame_number": frame_count,
                        "timestamp": timestamp,
                        "filename": frame_filename,
                    }
                )

                frame_count += 1

            current_frame += interval_frames

        cap.release()

        # Save metadata
        import json

        metadata_path = output_dir / "metadata.json"
        with open(metadata_path, "w") as f:
            json.dump(
                {
                    "video_id": clean_video_id,
                    "url": url,
                    "interval_seconds": interval_seconds,
                    "total_frames": len(extracted_frames),
                    "frames": extracted_frames,
                },
                f,
                indent=2,
            )

        print("\nSummary:")
        print(f"Video ID: {clean_video_id}")
        print(f"Output directory: {output_dir}")
        print(f"Total frames extracted: {len(extracted_frames)}")
        print(f"Frame interval: {interval_seconds} second(s)")
        if extracted_frames:
            print(f"Duration covered: {extracted_frames[-1]['timestamp']:.1f} seconds")

        return output_dir, extracted_frames


# Example usage:
if __name__ == "__main__":
    # Extract frames from a YouTube video
    video_id = "6evFKKruJ0c"  # Replace with your video ID
    output_dir, frames = download_and_extract_frames(video_id)

    # Process multiple videos
    # video_ids = ["video_id_1", "video_id_2", "video_id_3"]
    # for vid in video_ids:
    #     download_and_extract_frames(vid)
