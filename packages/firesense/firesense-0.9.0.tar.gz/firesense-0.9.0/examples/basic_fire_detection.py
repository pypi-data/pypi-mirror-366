#!/usr/bin/env python3
"""
Basic Fire Detection Example Script

This script demonstrates how to use the Gemma 3N E4B fire detection model
to analyze a video file frame by frame and produce DetectionResult objects.

Usage:
    cd gemma_3n
    uv run python examples/basic_fire_detection.py

Video Input: data/sample_videos/tree_fire.mp4
Output: Frame-by-frame DetectionResult objects with fire analysis
"""

import asyncio
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from firesense.fire_detection.config import FireDetectionConfig
from firesense.fire_detection.models.gemma_e4b import Gemma3NE4BInterface
from firesense.fire_detection.processing.video import VideoProcessor
from firesense.fire_detection.vision.processor import VisionProcessor


async def analyze_video_frame_by_frame(use_quantization=False):
    """Analyze video frame by frame and produce DetectionResult objects.

    Args:
        use_quantization: Enable model quantization (default: False)
    """

    # Configuration
    video_path = project_root / "data" / "sample_videos" / "tree_fire.mp4"

    if not video_path.exists():
        print(f"❌ Video file not found: {video_path}")
        print("Please ensure the video file exists before running this script.")
        return

    print(f"🎥 Analyzing video: {video_path}")
    print("📊 Processing frame by frame...")
    print(f"⚙️  Quantization: {'Enabled' if use_quantization else 'Disabled'}\n")

    # Create configuration with flexible quantization
    from firesense.fire_detection.config import Gemma3NE4BConfig

    model_config = Gemma3NE4BConfig(
        model_path="google/gemma-2-2b-it",
        use_quantization=use_quantization,
        quantization_type="4bit",
        quantization_compute_dtype="float16",
    )

    config = FireDetectionConfig(
        model=model_config,
        video={
            "frame_interval": 1.0,  # Analyze 1 frame per second
            "max_frames": 30,  # Limit to first 30 frames for demo
            "batch_size": 1,
            "async_processing": False,
        },
        detection={
            "confidence_threshold": 0.7,
            "save_positive_frames": False,  # Don't save frames in example
            "save_all_frames": False,
        },
        output={
            "output_dir": str(project_root / "examples" / "output"),
            "output_format": "json",
        },
        device="auto",
        verbose=True,
    )

    # Initialize components
    print("🔧 Initializing fire detection components...")
    video_processor = VideoProcessor(config.video)
    vision_processor = VisionProcessor(config.model)
    model_interface = Gemma3NE4BInterface(
        config.model, config.get_device(), detection_config=config.detection
    )

    # Load the model
    print(f"🤖 Loading {config.model.model_variant} model...")
    try:
        model_interface.load_model()
        print("✅ Model loaded successfully")
    except Exception as e:
        print(f"❌ Model loading failed: {e}")
        print("💡 Please ensure model files are properly installed")
        return

    print("\n🔥 Starting frame-by-frame fire detection analysis...")
    print("=" * 60)

    # Process video frame by frame
    detection_results = []
    frame_count = 0

    try:
        # Extract frames from video
        async for frame_data in video_processor.extract_frames(video_path):
            frame_count += 1

            print(f"\n📋 Frame {frame_count}:")
            print(f"   📱 Frame Number: {frame_data.frame_number}")
            print(f"   ⏱️  Timestamp: {frame_data.timestamp:.3f}s")
            print(f"   📐 Image Shape: {frame_data.image.shape}")

            # Convert frame to PIL Image for model processing
            pil_image = vision_processor.numpy_to_pil(frame_data.image)
            processed_image = vision_processor.preprocess_image(pil_image)

            # Perform fire detection on this frame
            print("   🔍 Analyzing frame for fire detection...")

            detection_result = await model_interface.detect_fire(
                processed_image, frame_data.frame_number, frame_data.timestamp
            )

            detection_results.append(detection_result)

            # Display results
            print(f"   🔥 Fire Detected: {detection_result.fire_detected}")
            print(f"   📊 Confidence: {detection_result.confidence:.3f}")
            print(
                f"   🎯 Fire Presence Probability: {detection_result.fire_presence_probability:.3f}"
            )
            print(
                f"   ⚠️  Uncontrolled Fire Probability: {detection_result.uncontrolled_fire_probability:.3f}"
            )
            print(f"   ⚡ Processing Time: {detection_result.processing_time:.3f}s")

            if detection_result.fire_detected and detection_result.fire_characteristics:
                fire_chars = detection_result.fire_characteristics
                print(f"   🚨 Fire Type: {fire_chars.fire_type}")
                print(f"   🎯 Emergency Level: {fire_chars.emergency_level}")
                print(f"   📞 911 Call Warranted: {fire_chars.call_911_warranted}")
                print(f"   📍 Location: {fire_chars.location}")
                print(f"   💨 Spread Potential: {fire_chars.spread_potential}")

                if fire_chars.call_911_warranted:
                    print("   🚨 *** EMERGENCY: IMMEDIATE ATTENTION REQUIRED ***")

            print(f"   📝 Model Variant: {detection_result.model_variant}")

            # Add a separator for readability
            print("-" * 40)

    except KeyboardInterrupt:
        print("\n⏹️  Analysis interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during analysis: {e}")
        return

    # Summary
    print("\n📈 Analysis Summary:")
    print("=" * 60)
    print(f"🎬 Total Frames Processed: {len(detection_results)}")

    fire_detections = [r for r in detection_results if r.fire_detected]
    print(f"🔥 Fire Detections: {len(fire_detections)}")

    if fire_detections:
        avg_confidence = sum(r.confidence for r in fire_detections) / len(
            fire_detections
        )
        print(f"📊 Average Fire Confidence: {avg_confidence:.3f}")

        emergency_frames = [
            r
            for r in fire_detections
            if r.fire_characteristics and r.fire_characteristics.call_911_warranted
        ]
        print(f"🚨 Emergency Frames (911 warranted): {len(emergency_frames)}")

        # Show timeline of fire detections
        if fire_detections:
            print("\n🕒 Fire Detection Timeline:")
            for result in fire_detections:
                status = (
                    "🚨 EMERGENCY"
                    if (
                        result.fire_characteristics
                        and result.fire_characteristics.call_911_warranted
                    )
                    else "🔥"
                )
                print(
                    f"   {status} Frame {result.frame_number} at {result.timestamp:.1f}s "
                    f"(confidence: {result.confidence:.1%})"
                )
    else:
        print("✅ No fire detected in the analyzed frames")

    total_processing_time = sum(r.processing_time for r in detection_results)
    print(f"⚡ Total Processing Time: {total_processing_time:.3f}s")
    print(
        f"📈 Average Time per Frame: {total_processing_time/len(detection_results):.3f}s"
    )

    print("\n🎯 Example completed successfully!")
    print("💡 Next step: Use this logic for webcam stream analysis")

    return detection_results


def main():
    """Main entry point for the basic fire detection example."""
    print("🔥 Gemma Fire Detection - Basic Example")
    print("=" * 50)
    print("📝 This script demonstrates frame-by-frame fire detection")
    print("🎥 Input: data/sample_videos/tree_fire.mp4")
    print("📊 Output: DetectionResult objects for each frame")
    print("=" * 50)

    # Parse command line arguments for quantization
    import argparse

    parser = argparse.ArgumentParser(description="Basic Fire Detection with Gemma 2B")
    parser.add_argument(
        "--use-quantization",
        action="store_true",
        default=False,
        help="Enable model quantization (default: False)",
    )
    args = parser.parse_args()

    # Run the async analysis
    try:
        asyncio.run(
            analyze_video_frame_by_frame(use_quantization=args.use_quantization)
        )
    except Exception as e:
        print(f"\n❌ Script failed: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
