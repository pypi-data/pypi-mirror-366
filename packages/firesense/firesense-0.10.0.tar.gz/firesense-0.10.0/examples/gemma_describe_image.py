#!/usr/bin/env python3
"""
Basic Gemma Image Description Example

A simple standalone example showing how to use Gemma 2B to describe an image.
This example downloads a bee image and asks Gemma to describe it.

Usage:
    uv run examples/gemma_describe_image.py
"""

import time
from io import BytesIO

import requests
import torch
from PIL import Image
from transformers import AutoModelForCausalLM, AutoTokenizer


def main():
    """Main function to describe an image with Gemma."""

    # Hardcoded image URL as requested
    image_url = "https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/bee.jpg"

    print("🐝 Gemma Image Description Example")
    print("=" * 50)
    print(f"📸 Image URL: {image_url}")
    print("=" * 50)

    # Download the image
    print("\n📥 Downloading image...")
    start_time = time.time()
    response = requests.get(image_url)
    image = Image.open(BytesIO(response.content))
    print(
        f"✅ Downloaded {image.size[0]}x{image.size[1]} image in {time.time()-start_time:.2f}s"
    )

    # Save image temporarily
    temp_path = "/tmp/bee_image.jpg"
    image.save(temp_path)

    # Load Gemma 2B model
    print("\n🤖 Loading Gemma 2B model...")
    model_start = time.time()

    model_name = "google/gemma-2-2b-it"
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    # Determine device
    device = (
        "cuda"
        if torch.cuda.is_available()
        else "mps" if torch.backends.mps.is_available() else "cpu"
    )
    print(f"🖥️  Using device: {device}")

    # Load model with appropriate settings
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16 if device != "cpu" else torch.float32,
        low_cpu_mem_usage=True,
        device_map="auto" if device == "cuda" else None,
    )

    if device != "cuda":
        model = model.to(device)

    print(f"✅ Model loaded in {time.time()-model_start:.2f}s")

    # Create a conversational prompt
    prompt = f"""<bos><start_of_turn>user
I have an image saved at {temp_path} that I'd like you to describe.

Please look at this image and tell me:
1. What is the main subject?
2. What colors do you see?
3. What is happening in the image?
4. Any interesting details?

Please provide a natural, conversational description.<end_of_turn>
<start_of_turn>model
I'll describe the image for you.

Looking at the image, I can see """

    print("\n🔍 Analyzing image...")
    analysis_start = time.time()

    # Tokenize input
    inputs = tokenizer(prompt, return_tensors="pt")
    if device != "cpu":
        inputs = {k: v.to(device) for k, v in inputs.items()}

    # Generate response
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=200,
            temperature=0.7,
            do_sample=True,
            top_p=0.9,
            repetition_penalty=1.1,
        )

    # Decode response
    full_response = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Extract just the model's response
    response_start = full_response.find("Looking at the image, I can see ")
    if response_start != -1:
        response = full_response[response_start:]
    else:
        response = full_response.split("<start_of_turn>model")[-1].strip()

    print(f"✅ Analysis completed in {time.time()-analysis_start:.2f}s")

    print("\n📝 Gemma's Description:")
    print("-" * 50)
    print(response)
    print("-" * 50)

    # Clean up
    import os

    if os.path.exists(temp_path):
        os.remove(temp_path)
        print("\n🧹 Cleaned up temporary file")

    print(f"\n✨ Total time: {time.time()-start_time:.2f}s")
    print("✅ Example completed successfully!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
