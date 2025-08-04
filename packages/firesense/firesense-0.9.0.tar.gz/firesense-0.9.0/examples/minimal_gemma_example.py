#!/usr/bin/env python3
"""
Minimal Gemma Example - Image Description

The absolute simplest example of using Gemma to describe an image.
This reuses the existing fire detection model loader for convenience.

Usage:
    uv run examples/minimal_gemma_example.py
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

import asyncio
from io import BytesIO

import requests
from PIL import Image

from firesense.fire_detection.config import FireDetectionConfig, Gemma3NE4BConfig
from firesense.fire_detection.models.gemma_e4b import Gemma3NE4BInterface


async def describe_bee_image():
    """Use Gemma to describe the bee image."""

    # Hardcoded URL
    image_url = "https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/bee.jpg"

    print("🐝 Minimal Gemma Example")
    print(f"📸 Describing: {image_url}\n")

    # Download image
    image = Image.open(BytesIO(requests.get(image_url).content))

    # Configure model (reuse fire detection config)
    model_config = Gemma3NE4BConfig(
        model_path="google/gemma-2-2b-it", use_quantization=False
    )

    # Create custom detection config for general description
    detection_config = type(
        "obj",
        (object,),
        {
            "system_prompt": "You are a helpful AI that describes images clearly and concisely.",
            "detection_prompt": "Describe this image in 2-3 sentences. What do you see?",
        },
    )

    config = FireDetectionConfig(model=model_config)

    # Load model
    print("Loading Gemma 2B model...")
    model = Gemma3NE4BInterface(config.model, config.get_device(), detection_config)
    model.load_model()

    # Get description (using fire detection method but with custom prompts)
    print("Analyzing image...\n")
    result = await model.detect_fire(image, frame_number=1, timestamp=0.0)

    # The model's response will be in the raw_response field
    print("📝 Gemma says:")
    print("-" * 40)
    if "raw_response" in result.detection_details:
        print(result.detection_details["raw_response"])
    else:
        # Try to extract meaningful text from the result
        print(f"Fire detected: {result.fire_detected}")
        print(f"Confidence: {result.confidence}")
        print(f"Details: {result.detection_details}")
    print("-" * 40)


def main():
    """Run the example."""
    asyncio.run(describe_bee_image())


if __name__ == "__main__":
    main()
