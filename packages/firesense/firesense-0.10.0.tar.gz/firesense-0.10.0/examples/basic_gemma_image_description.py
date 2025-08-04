#!/usr/bin/env python3
"""
Basic Gemma Image Description Example

This script demonstrates the simplest usage of Gemma 2B model to describe an image.
It downloads an image from a URL and asks Gemma to describe what it sees.

Usage:
    uv run examples/basic_gemma_image_description.py
"""

from io import BytesIO

import requests
import torch
from PIL import Image
from transformers import AutoModelForCausalLM, AutoTokenizer


def download_image(url):
    """Download image from URL and return PIL Image."""
    response = requests.get(url)
    return Image.open(BytesIO(response.content))


def describe_image_with_gemma(image_url):
    """Use Gemma 2B to describe an image."""

    print("🚀 Basic Gemma Image Description Example")
    print("=" * 50)
    print(f"📸 Image URL: {image_url}")
    print("=" * 50)

    # Download the image
    print("\n📥 Downloading image...")
    image = download_image(image_url)
    print(f"✅ Image downloaded: {image.size[0]}x{image.size[1]} pixels")

    # Save image temporarily (Gemma processes images from file paths)
    temp_image_path = "/tmp/temp_image.jpg"
    image.save(temp_image_path)
    print(f"💾 Image saved temporarily to: {temp_image_path}")

    # Load Gemma 2B model
    print("\n🤖 Loading Gemma 2B model...")
    model_name = "google/gemma-2-2b-it"

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
        device_map="auto",
    )
    print("✅ Model loaded successfully")

    # Create a simple prompt for image description
    prompt = f"""<bos><start_of_turn>user
You are a helpful AI assistant. Please look at this image and describe what you see in detail.

Image: {temp_image_path}

Describe the image focusing on:
1. Main subject(s)
2. Colors and composition
3. Background elements
4. Overall mood or feeling

Description:<end_of_turn>
<start_of_turn>model
"""

    print("\n🔍 Analyzing image...")

    # Tokenize and generate response
    inputs = tokenizer(prompt, return_tensors="pt")

    # Generate description
    with torch.no_grad():
        outputs = model.generate(
            **inputs, max_new_tokens=200, temperature=0.7, do_sample=True, top_p=0.9
        )

    # Decode response
    response = tokenizer.decode(
        outputs[0][len(inputs["input_ids"][0]) :], skip_special_tokens=True
    )

    print("\n📝 Gemma's Image Description:")
    print("-" * 50)
    print(response.strip())
    print("-" * 50)

    # Clean up
    import os

    os.remove(temp_image_path)
    print("\n🧹 Temporary file cleaned up")
    print("✅ Example completed successfully!")


def main():
    """Main entry point."""
    # Hardcoded image URL as requested
    image_url = "https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/bee.jpg"

    try:
        describe_image_with_gemma(image_url)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
