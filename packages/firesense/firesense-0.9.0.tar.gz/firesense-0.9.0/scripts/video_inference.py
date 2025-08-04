#!/usr/bin/env python3
"""
Video inference script that downloads YouTube videos, extracts frames, and runs fire detection inference.

Requirements:
pip install yt-dlp opencv-python transformers torch pydantic unsloth
"""

import json
import os
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path

# Disable torch compile to avoid recompilation errors
os.environ["TORCH_COMPILE_DISABLE"] = "1"

# Video processing imports
import cv2
import torch
import yt_dlp
from pydantic import BaseModel, ValidationError

# Model and inference imports
from unsloth import FastModel

# Increase dynamo cache size limit to avoid recompilation errors
torch._dynamo.config.cache_size_limit = 64


# === Schema for structured output ===
class FireDescription(BaseModel):
    has_flame: bool
    has_out_of_control_fire: bool


# === Model setup (from direct_inference.py) ===
def setup_model():
    """Load the Gemma model for inference."""
    print("Loading Gemma model...")

    # Disable torch compile for the model to avoid recompilation issues
    import torch._dynamo

    torch._dynamo.config.suppress_errors = True

    model, tokenizer = FastModel.from_pretrained(
        model_name="unsloth/gemma-3n-E4B-it",
        dtype=None,
        max_seq_length=1024,
        load_in_4bit=True,
        full_finetuning=False,
    )

    # Ensure model is in eval mode
    model.eval()

    # Disable gradient computation for inference
    torch.set_grad_enabled(False)

    print("Model loaded successfully!")
    return model, tokenizer


# === Inference function (from direct_inference.py) ===
def gemma_fire_inference(
    model, tokenizer, messages, max_new_tokens: int = 256
) -> FireDescription:
    """Run fire detection inference on an image."""
    system_prompt = """
    You are **FireSense**, a vision‑language model for real‑time fire detection.

On every image you receive, output **one digit only** (no words, no punctuation):

0 – No flame present
1 – Benign or illusory flame (birthday candle, stove burner, lighter, match, or a fire video/animation on a TV, monitor, tablet, or phone)
2 – Contained real flame (fire pit, barbecue, indoor fireplace)
3 – Dangerous uncontrolled fire (spreading or uncontained flames / heavy smoke)

If unsure, choose the **higher, safer** category.

Return nothing except that single digit.
    """

    system_message = {
        "role": "system",
        "content": [{"type": "text", "text": system_prompt}],
    }

    device = "cuda" if torch.cuda.is_available() else "cpu"

    tokenized = tokenizer.apply_chat_template(
        [system_message, *messages],
        add_generation_prompt=True,
        tokenize=True,
        return_dict=True,
        return_tensors="pt",
    ).to(device)

    # Use no_grad context to avoid recompilation
    with torch.no_grad():
        try:
            # Try with sdp_kernel context if available
            with torch.backends.cuda.sdp_kernel(
                enable_flash=False, enable_math=True, enable_mem_efficient=True
            ):
                output_ids = model.generate(
                    **tokenized,
                    max_new_tokens=max_new_tokens,
                    temperature=1.0,
                    top_p=0.95,
                    top_k=64,
                    streamer=None,  # Disable streaming for cleaner output
                    use_cache=True,  # Enable KV cache
                    pad_token_id=tokenizer.pad_token_id,
                    eos_token_id=tokenizer.eos_token_id,
                )
        except:
            # Fallback without sdp_kernel
            output_ids = model.generate(
                **tokenized,
                max_new_tokens=max_new_tokens,
                temperature=1.0,
                top_p=0.95,
                top_k=64,
                streamer=None,  # Disable streaming for cleaner output
                use_cache=True,  # Enable KV cache
                pad_token_id=tokenizer.pad_token_id,
                eos_token_id=tokenizer.eos_token_id,
            )

    full_text = tokenizer.decode(output_ids[0], skip_special_tokens=True)

    # Extract JSON from the response
    # Try to find JSON between ```json markers first
    json_start = full_text.find("```json")
    json_end = full_text.rfind("```")

    if json_start != -1 and json_end != -1 and json_start < json_end:
        json_str = full_text[json_start + len("```json") : json_end].strip()
    else:
        # Try to find raw JSON
        json_start = full_text.find("{")
        json_end = full_text.rfind("}") + 1
        if json_start != -1 and json_end > json_start:
            json_str = full_text[json_start:json_end]
        else:
            json_str = full_text

    try:
        data = json.loads(json_str)
        return FireDescription(**data)
    except (json.JSONDecodeError, ValidationError) as err:
        # Return a default response if parsing fails
        print(f"Warning: Failed to parse model output as JSON: {err}")
        return FireDescription(has_flame=False, has_out_of_control_fire=False)


# === Video processing functions (from youtube_frame_extractor.py) ===
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
    video_id, interval_seconds=1, quality="720p", output_base_dir="."
):
    """Download YouTube video and extract frames at specified intervals."""
    # Validate video ID
    clean_video_id = validate_video_id(video_id)
    print(f"Processing YouTube video: {clean_video_id}")

    # Create output directory with _frames suffix
    output_dir = Path(output_base_dir) / f"{clean_video_id}_frames"
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

        # Get video info
        video_info = {}
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                video_info = {
                    "title": info.get("title", "Unknown"),
                    "uploader": info.get("uploader", "Unknown"),
                    "duration": info.get("duration", 0),
                    "upload_date": info.get("upload_date", "Unknown"),
                }
        except Exception as e:
            print(f"Warning: Could not extract video info: {e}")

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
                        "path": str(frame_path),
                    }
                )

                frame_count += 1

            current_frame += interval_frames

        cap.release()

        return output_dir, extracted_frames, video_info


# === Main inference pipeline ===
def process_video_inference(video_id, interval_seconds=1, output_dir="."):
    """Process a YouTube video: download, extract frames, and run inference on each frame."""

    # Create output directory if specified
    output_path = Path(output_dir)
    if output_dir != ".":
        output_path.mkdir(exist_ok=True)

    # Extract frames
    print("\n=== Frame Extraction ===")
    frames_dir, frames_info, video_info = download_and_extract_frames(
        video_id, interval_seconds=interval_seconds, output_base_dir=output_path
    )

    # Load model
    print("\n=== Model Setup ===")
    model, tokenizer = setup_model()

    # Run inference on each frame
    print(f"\n=== Running Inference on {len(frames_info)} frames ===")
    inference_results = []

    for i, frame_info in enumerate(frames_info):
        print(f"\nProcessing frame {i+1}/{len(frames_info)}: {frame_info['filename']}")

        # Prepare message for inference
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": frame_info["path"]},
                    {"type": "text", "text": "Classify  0/1/2/3:"},
                ],
            }
        ]

        try:
            # Track inference time
            start_time = time.time()

            # Run inference
            fire_report = gemma_fire_inference(model, tokenizer, messages)

            # Calculate elapsed time
            elapsed_time = time.time() - start_time

            # Store results
            result = {
                "frame_number": frame_info["frame_number"],
                "timestamp": frame_info["timestamp"],
                "filename": frame_info["filename"],
                "inference": {
                    "has_flame": fire_report.has_flame,
                    "has_out_of_control_fire": fire_report.has_out_of_control_fire,
                },
                "inference_time_seconds": round(elapsed_time, 3),
            }
            inference_results.append(result)

            # Print result
            print(f"  - Has flame: {fire_report.has_flame}")
            print(f"  - Out of control: {fire_report.has_out_of_control_fire}")

            print(f"  - Inference time: {elapsed_time:.3f}s")

        except Exception as e:
            print(f"  - Error processing frame: {e}")
            inference_results.append(
                {
                    "frame_number": frame_info["frame_number"],
                    "timestamp": frame_info["timestamp"],
                    "filename": frame_info["filename"],
                    "inference": {
                        "has_flame": False,
                        "has_out_of_control_fire": False,
                        "description": f"Error: {e!s}",
                    },
                    "inference_time_seconds": 0.0,
                }
            )

    # Prepare final output
    clean_video_id = validate_video_id(video_id)

    # Calculate timing statistics for JSON
    inference_times = [
        r["inference_time_seconds"]
        for r in inference_results
        if r["inference_time_seconds"] > 0
    ]
    timing_stats = {
        "total_inference_time": (
            round(sum(inference_times), 2) if inference_times else 0
        ),
        "average_time_per_frame": (
            round(sum(inference_times) / len(inference_times), 3)
            if inference_times
            else 0
        ),
        "min_time": round(min(inference_times), 3) if inference_times else 0,
        "max_time": round(max(inference_times), 3) if inference_times else 0,
    }

    output_data = {
        "video_id": clean_video_id,
        "url": f"https://www.youtube.com/watch?v={clean_video_id}",
        "video_info": video_info,
        "processing_info": {
            "timestamp": datetime.now().isoformat(),
            "interval_seconds": interval_seconds,
            "total_frames": len(frames_info),
            "frames_directory": str(frames_dir),
        },
        "inference_performance": timing_stats,
        "inference_results": inference_results,
    }

    # Save results
    output_file = output_path / f"{clean_video_id}.json"
    with open(output_file, "w") as f:
        json.dump(output_data, f, indent=2)

    print(f"\n=== Results saved to: {output_file} ===")

    # Print summary
    flame_count = sum(1 for r in inference_results if r["inference"]["has_flame"])
    danger_count = sum(
        1 for r in inference_results if r["inference"]["has_out_of_control_fire"]
    )

    # Calculate timing statistics
    inference_times = [
        r["inference_time_seconds"]
        for r in inference_results
        if r["inference_time_seconds"] > 0
    ]
    if inference_times:
        avg_time = sum(inference_times) / len(inference_times)
        min_time = min(inference_times)
        max_time = max(inference_times)
        total_time = sum(inference_times)
    else:
        avg_time = min_time = max_time = total_time = 0

    print("\n=== Summary ===")
    print(f"Video ID: {clean_video_id}")
    print(f"Total frames analyzed: {len(inference_results)}")
    print(f"Frames with flame detected: {flame_count}")
    print(f"Frames with out-of-control fire: {danger_count}")
    print("\n=== Inference Performance ===")
    print(f"Total inference time: {total_time:.2f}s")
    print(f"Average time per frame: {avg_time:.3f}s")
    print(f"Min time: {min_time:.3f}s")
    print(f"Max time: {max_time:.3f}s")

    # Clean up GPU memory
    del model
    del tokenizer
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    return output_file


# === Main entry point ===
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python video_inference.py <youtube_video_id> [interval_seconds]")
        print("Example: python video_inference.py 6evFKKruJ0c 1")
        sys.exit(1)

    video_id = sys.argv[1]
    interval = int(sys.argv[2]) if len(sys.argv) > 2 else 1

    try:
        output_file = process_video_inference(video_id, interval_seconds=interval)
        print(f"\nSuccess! Results saved to: {output_file}")
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)
