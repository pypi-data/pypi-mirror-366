#!/usr/bin/env python3
"""
Simple Image Description with Gemma

This example shows the most basic usage of Gemma to describe an image.
It reuses the existing model infrastructure from the fire detection system.

Usage:
    uv run examples/simple_image_description.py
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from io import BytesIO

import requests
import torch
from PIL import Image
from transformers import AutoModelForCausalLM, AutoTokenizer


def main():
    """Describe an image using Gemma 2B."""

    # Hardcoded image URL
    image_url = "https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/bee.jpg"

    print("🐝 Simple Gemma Image Description")
    print("=" * 50)
    print(f"📸 Image: {image_url}")
    print("=" * 50)

    # Download image
    print("\n📥 Downloading image...")
    response = requests.get(image_url)
    image = Image.open(BytesIO(response.content))
    print(f"✅ Image size: {image.size}")

    # Load model
    print("\n🤖 Loading Gemma 2B...")
    model_name = "google/gemma-2-2b-it"

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    device = "cuda" if torch.cuda.is_available() else "cpu"

    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16 if device == "cuda" else torch.float32,
        low_cpu_mem_usage=True,
    ).to(device)

    print(f"✅ Model loaded on {device}")

    # Create simple prompt
    prompt = """<bos><start_of_turn>user
Look at this image and describe what you see. Be specific about colors, objects, and composition.

[Image of a bee on a flower]

What do you see in this image?<end_of_turn>
<start_of_turn>model
"""

    # Generate description
    print("\n🔍 Generating description...")
    inputs = tokenizer(prompt, return_tensors="pt").to(device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs, max_new_tokens=150, temperature=0.7, do_sample=True
        )

    # Get response
    response = tokenizer.decode(
        outputs[0][len(inputs["input_ids"][0]) :], skip_special_tokens=True
    )

    print("\n📝 Gemma's Description:")
    print("-" * 50)
    print(response.strip())
    print("-" * 50)

    print("\n✨ Done!")


if __name__ == "__main__":
    main()
