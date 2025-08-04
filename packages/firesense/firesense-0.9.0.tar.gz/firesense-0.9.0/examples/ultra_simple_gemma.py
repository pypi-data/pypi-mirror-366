#!/usr/bin/env python3
"""
Ultra Simple Gemma Example

The absolute minimal code to use Gemma for image description.

Usage:
    uv run examples/ultra_simple_gemma.py
"""

from io import BytesIO

import requests
import torch
from PIL import Image
from transformers import AutoModelForCausalLM, AutoTokenizer

# Hardcoded bee image URL
image_url = "https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/bee.jpg"

print("🐝 Ultra Simple Gemma Example\n")

# Download and save image
image = Image.open(BytesIO(requests.get(image_url).content))
image.save("/tmp/cow.jpg")

# Load Gemma 2B
print("Loading Gemma 2B...")
tokenizer = AutoTokenizer.from_pretrained("google/gemma-2-2b-it")

# Determine device
device = (
    "cuda"
    if torch.cuda.is_available()
    else "mps" if torch.backends.mps.is_available() else "cpu"
)
model = AutoModelForCausalLM.from_pretrained(
    "google/gemma-2-2b-it",
    torch_dtype=torch.float16 if device != "cpu" else torch.float32,
    low_cpu_mem_usage=True,
).to(device)

# Simple prompt
prompt = """<bos><start_of_turn>user
What do you see in the image at /tmp/cow.jpg?<end_of_turn>
<start_of_turn>model
In the image, I see """

# Generate description
inputs = tokenizer(prompt, return_tensors="pt").to(device)
outputs = model.generate(**inputs, max_new_tokens=100, do_sample=True, top_p=0.9)
response = tokenizer.decode(
    outputs[0][len(inputs["input_ids"][0]) :], skip_special_tokens=True
)

print("\n📝 Gemma says:")
print(response)
print("\n✅ Done!")
