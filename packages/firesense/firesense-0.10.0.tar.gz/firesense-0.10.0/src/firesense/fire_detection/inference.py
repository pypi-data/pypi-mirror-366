"""Main inference pipeline for fire detection on YouTube videos."""

import json
import time
from datetime import datetime, timezone
from pathlib import Path

import torch

from .model import gemma_fire_inference, setup_model
from .video import download_and_extract_frames, validate_video_id


def process_video_inference(
    video_id: str, interval_seconds: float = 1, output_dir: str = "."
) -> str:
    """Process a YouTube video: download, extract frames, and run inference on each frame."""

    # Always use localdemo directory structure
    demo_path = Path("localdemo")
    demo_path.mkdir(exist_ok=True)

    # Frames go under localdemo/frames/
    frames_base_dir = demo_path / "frames"
    frames_base_dir.mkdir(exist_ok=True)

    # Extract frames
    print("\n=== Frame Extraction ===")
    frames_dir, frames_info, video_info = download_and_extract_frames(
        video_id,
        interval_seconds=interval_seconds,
        output_base_dir=str(frames_base_dir),
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
                    {"type": "text", "text": "Classify:"},
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
                    "classification": fire_report.classification,  # Include raw classification for transparency
                },
                "inference_time_seconds": round(elapsed_time, 3),
            }
            inference_results.append(result)

            # Print result
            classification_labels = {
                0: "No flame",
                1: "Benign/illusory flame",
                2: "Contained real flame",
                3: "Dangerous uncontrolled fire",
            }
            print(
                f"  - Classification: {fire_report.classification} ({classification_labels.get(fire_report.classification, 'Unknown')})"
            )
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
                        "classification": 0,  # Default to 0 (no flame) on error
                        "error": f"Error: {e!s}",
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
            "timestamp": datetime.now(timezone.utc).isoformat(),  # noqa: UP017
            "interval_seconds": interval_seconds,
            "total_frames": len(frames_info),
            "frames_directory": str(frames_dir),
        },
        "inference_performance": timing_stats,
        "inference_results": inference_results,
    }

    # Save results to localdemo directory
    output_file = demo_path / f"{clean_video_id}.json"
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

    return str(output_file)
