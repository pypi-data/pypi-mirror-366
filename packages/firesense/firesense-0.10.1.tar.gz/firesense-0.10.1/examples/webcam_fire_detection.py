#!/usr/bin/env python3
"""
Webcam Fire Detection Example Script

This script demonstrates real-time fire detection using webcam stream,
analyzing 1 frame per second and producing DetectionResult objects.

Based on the logic from basic_fire_detection.py but adapted for live camera feed.

Usage:
    cd gemma_3n
    uv run python examples/webcam_fire_detection.py

Requirements:
    - Webcam connected to the system
    - OpenCV (cv2) installed via project dependencies

Input: Live webcam stream
Output: Real-time DetectionResult objects with fire analysis
"""

import asyncio
import sys
import time
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

import cv2

from firesense.fire_detection.config import FireDetectionConfig
from firesense.fire_detection.models.gemma_e4b import Gemma3NE4BInterface
from firesense.fire_detection.processing.video import FrameData
from firesense.fire_detection.vision.processor import VisionProcessor


class WebcamFireDetector:
    """Real-time webcam fire detection system."""

    def __init__(self, camera_index=0, analysis_interval=1.0, use_quantization=False):
        """Initialize webcam fire detector.

        Args:
            camera_index: Camera device index (usually 0 for default camera)
            analysis_interval: Seconds between fire detection analysis
            use_quantization: Enable model quantization (default: False)
        """
        self.camera_index = camera_index
        self.analysis_interval = analysis_interval
        self.cap = None
        self.running = False

        # Initialize fire detection components with flexible quantization
        self.config = FireDetectionConfig(
            model={
                "model_path": "google/gemma-2-2b-it",
                "use_quantization": use_quantization,
                "quantization_type": "4bit",
                "quantization_compute_dtype": "float16",
            },
            video={
                "frame_interval": analysis_interval,
                "batch_size": 1,
                "async_processing": False,
            },
            detection={
                "confidence_threshold": 0.9,
                "save_positive_frames": False,
                "save_all_frames": False,
            },
            output={
                "output_dir": str(project_root / "examples" / "webcam_output"),
                "output_format": "json",
            },
            device="auto",
            debug=True,
            verbose=True,
        )

        self.vision_processor = VisionProcessor(self.config.model)
        self.model_interface = Gemma3NE4BInterface(
            self.config.model,
            self.config.get_device(),
            detection_config=self.config.detection,
        )

        # Statistics
        self.frame_count = 0
        self.analysis_count = 0
        self.fire_detections = []
        self.start_time = None

    def initialize_camera(self):
        """Initialize the webcam."""
        print(f"📷 Initializing camera {self.camera_index}...")

        self.cap = cv2.VideoCapture(self.camera_index)

        if not self.cap.isOpened():
            raise RuntimeError(f"Cannot open camera {self.camera_index}")

        # Set camera properties for better performance
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)

        # Get actual camera properties
        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = self.cap.get(cv2.CAP_PROP_FPS)

        print(f"✅ Camera initialized: {width}x{height} @ {fps}fps")
        return True

    async def initialize_model(self):
        """Initialize the fire detection model."""
        print(f"🤖 Loading {self.config.model.model_variant} model...")
        try:
            self.model_interface.load_model()
            print("✅ Model loaded successfully")
        except Exception as e:
            print(f"❌ Model loading failed: {e}")
            print("💡 Please ensure model files are properly installed")
            raise RuntimeError("Model loading failed")

    def capture_frame(self):
        """Capture a single frame from the webcam.

        Returns:
            FrameData object or None if capture failed
        """
        ret, frame = self.cap.read()
        if not ret:
            return None

        # Convert BGR to RGB for fire detection model
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Calculate timestamp
        current_time = time.time()
        if self.start_time is None:
            self.start_time = current_time
        timestamp = current_time - self.start_time

        return FrameData(
            image=frame_rgb,
            frame_number=self.frame_count,
            timestamp=timestamp,
            metadata={
                "source": "webcam",
                "camera_index": self.camera_index,
                "capture_time": current_time,
            },
        )

    async def analyze_frame(self, frame_data):
        """Analyze a frame for fire detection.

        Args:
            frame_data: FrameData object to analyze

        Returns:
            DetectionResult object
        """
        # Convert to PIL Image and preprocess
        pil_image = self.vision_processor.numpy_to_pil(frame_data.image)
        processed_image = self.vision_processor.preprocess_image(pil_image)

        # Perform fire detection
        detection_result = await self.model_interface.detect_fire(
            processed_image, frame_data.frame_number, frame_data.timestamp
        )

        return detection_result

    def display_frame_with_results(self, frame_bgr, detection_result):
        """Display the camera frame with fire detection overlay.

        Args:
            frame_bgr: OpenCV frame in BGR format
            detection_result: DetectionResult object
        """
        # Create a copy for overlay
        display_frame = frame_bgr.copy()
        height, width = display_frame.shape[:2]

        # Add fire detection status overlay
        if detection_result.fire_detected:
            # Fire detected - red overlay
            color = (0, 0, 255)  # Red in BGR
            status_text = "🔥 FIRE DETECTED"
            confidence_text = f"Confidence: {detection_result.confidence:.1%}"

            # Add emergency warning if needed
            if (
                detection_result.fire_characteristics
                and detection_result.fire_characteristics.call_911_warranted
            ):
                cv2.rectangle(display_frame, (0, 0), (width, 80), (0, 0, 255), -1)
                cv2.putText(
                    display_frame,
                    "🚨 EMERGENCY - CALL 911",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (255, 255, 255),
                    2,
                )
                cv2.putText(
                    display_frame,
                    status_text,
                    (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 255),
                    2,
                )
            else:
                cv2.rectangle(display_frame, (0, 0), (width, 60), color, -1)
                cv2.putText(
                    display_frame,
                    status_text,
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 255, 255),
                    2,
                )
                cv2.putText(
                    display_frame,
                    confidence_text,
                    (10, 55),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 255, 255),
                    2,
                )
        else:
            # No fire - green overlay
            color = (0, 255, 0)  # Green in BGR
            status_text = "✅ No Fire Detected"
            cv2.rectangle(display_frame, (0, 0), (width, 40), color, -1)
            cv2.putText(
                display_frame,
                status_text,
                (10, 25),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2,
            )

        # Add frame info
        info_text = f"Frame: {detection_result.frame_number} | Time: {detection_result.timestamp:.1f}s"
        cv2.putText(
            display_frame,
            info_text,
            (10, height - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.4,
            (255, 255, 255),
            1,
        )

        # Add fire detection count
        fire_count = len([r for r in self.fire_detections if r.fire_detected])
        count_text = f"Fire Detections: {fire_count}"
        cv2.putText(
            display_frame,
            count_text,
            (width - 200, height - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.4,
            (255, 255, 255),
            1,
        )

        return display_frame

    def print_detection_result(self, detection_result):
        """Print detection result to console."""
        print(f"\n📋 Analysis #{self.analysis_count}:")
        print(f"   📱 Frame: {detection_result.frame_number}")
        print(f"   ⏱️  Time: {detection_result.timestamp:.1f}s")
        print(f"   🔥 Fire: {detection_result.fire_detected}")
        print(f"   📊 Confidence: {detection_result.confidence:.1%}")
        print(f"   🎯 Fire Presence: {detection_result.fire_presence_probability:.1%}")
        print(
            f"   ⚠️  Uncontrolled: {detection_result.uncontrolled_fire_probability:.1%}"
        )

        if detection_result.fire_detected and detection_result.fire_characteristics:
            fire_chars = detection_result.fire_characteristics
            print(f"   🚨 Type: {fire_chars.fire_type}")
            print(f"   📞 911 Call: {fire_chars.call_911_warranted}")
            print(f"   💨 Spread Risk: {fire_chars.spread_potential}")

            if fire_chars.call_911_warranted:
                print("   🚨 *** EMERGENCY DETECTED ***")

    async def run_detection_loop(self):
        """Main detection loop."""
        print("🔥 Starting real-time fire detection...")
        print(f"⏱️  Analysis interval: {self.analysis_interval}s")
        print("📷 Camera feed window will open")
        print("🛑 Press 'q' to quit or Ctrl+C in terminal")
        print("=" * 60)

        self.running = True
        last_analysis_time = 0

        try:
            while self.running:
                # Capture frame
                frame_data = self.capture_frame()
                if frame_data is None:
                    print("❌ Failed to capture frame")
                    break

                self.frame_count += 1

                # Check if it's time for fire detection analysis
                current_time = time.time()
                if current_time - last_analysis_time >= self.analysis_interval:
                    # Perform fire detection analysis
                    detection_result = await self.analyze_frame(frame_data)
                    self.fire_detections.append(detection_result)
                    self.analysis_count += 1
                    last_analysis_time = current_time

                    # Print results
                    self.print_detection_result(detection_result)

                    # Display frame with results
                    frame_bgr = cv2.cvtColor(frame_data.image, cv2.COLOR_RGB2BGR)
                    display_frame = self.display_frame_with_results(
                        frame_bgr, detection_result
                    )
                else:
                    # Just display the current frame
                    frame_bgr = cv2.cvtColor(frame_data.image, cv2.COLOR_RGB2BGR)
                    display_frame = frame_bgr.copy()

                    # Add "monitoring" overlay
                    height, width = display_frame.shape[:2]
                    cv2.rectangle(
                        display_frame, (0, 0), (width, 30), (100, 100, 100), -1
                    )
                    cv2.putText(
                        display_frame,
                        "🎥 Monitoring - Fire Detection Active",
                        (10, 20),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (255, 255, 255),
                        1,
                    )

                # Show the frame
                cv2.imshow("Fire Detection - Webcam", display_frame)

                # Check for quit key
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    print("🛑 Quit key pressed")
                    break

                # Small delay to prevent excessive CPU usage
                await asyncio.sleep(0.03)  # ~30 FPS display rate

        except KeyboardInterrupt:
            print("\n🛑 Interrupted by user")
        except Exception as e:
            print(f"\n❌ Error in detection loop: {e}")
        finally:
            self.running = False

    def cleanup(self):
        """Clean up resources."""
        if self.cap is not None:
            self.cap.release()
        cv2.destroyAllWindows()
        print("🧹 Resources cleaned up")

    def print_summary(self):
        """Print analysis summary."""
        print("\n📈 Webcam Fire Detection Summary:")
        print("=" * 60)
        print(f"🎬 Total Frames Captured: {self.frame_count}")
        print(f"🔍 Analysis Performed: {self.analysis_count}")

        fire_detections = [r for r in self.fire_detections if r.fire_detected]
        print(f"🔥 Fire Detections: {len(fire_detections)}")

        if fire_detections:
            avg_confidence = sum(r.confidence for r in fire_detections) / len(
                fire_detections
            )
            print(f"📊 Average Fire Confidence: {avg_confidence:.1%}")

            emergency_detections = [
                r
                for r in fire_detections
                if r.fire_characteristics and r.fire_characteristics.call_911_warranted
            ]
            print(f"🚨 Emergency Detections: {len(emergency_detections)}")

        if self.start_time:
            total_time = time.time() - self.start_time
            print(f"⏱️  Total Runtime: {total_time:.1f}s")
            if self.analysis_count > 0:
                print(
                    f"📈 Analysis Rate: {self.analysis_count/total_time:.2f} analyses/second"
                )


async def main(use_quantization=False):
    """Main entry point for webcam fire detection.

    Args:
        use_quantization: Enable model quantization (default: False)
    """
    print("🔥 Gemma 3N Fire Detection - Webcam Stream Example")
    print("=" * 60)
    print("📷 This script performs real-time fire detection on webcam stream")
    print("⏱️  Analysis frequency: 1 frame per second")
    print("📊 Output: Real-time DetectionResult objects")
    print(f"⚙️  Quantization: {'Enabled' if use_quantization else 'Disabled'}")
    print("=" * 60)

    # Create detector
    detector = WebcamFireDetector(
        camera_index=0, analysis_interval=1.0, use_quantization=use_quantization
    )

    try:
        # Initialize components
        detector.initialize_camera()
        await detector.initialize_model()

        # Run detection loop
        await detector.run_detection_loop()

    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    finally:
        # Cleanup
        detector.cleanup()
        detector.print_summary()

    print("🎯 Webcam fire detection completed!")
    return 0


if __name__ == "__main__":
    # Parse command line arguments for quantization
    import argparse

    parser = argparse.ArgumentParser(
        description="Webcam Fire Detection with Gemma 3N E4B"
    )
    parser.add_argument(
        "--use-quantization",
        action="store_true",
        default=False,
        help="Enable model quantization (default: False)",
    )
    args = parser.parse_args()

    sys.exit(asyncio.run(main(use_quantization=args.use_quantization)))
