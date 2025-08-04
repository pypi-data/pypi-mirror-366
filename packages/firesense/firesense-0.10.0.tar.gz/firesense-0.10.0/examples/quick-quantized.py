#!/usr/bin/env python3
"""
Example of using google/gemma-3n-e2b-it with 4-bit quantization.

This example demonstrates quantization for memory-efficient inference.
The gemma-3n-e2b-it model is quite large (~27GB unquantized).

Requirements for quantization:
- CUDA-capable GPU with 10GB+ VRAM recommended
- bitsandbytes library installed
- Linux OS (bitsandbytes has limited Windows/Mac support)

For systems with less memory, consider:
1. Using the CPU example (quick-e2b-it.py)
2. Using cloud GPU services (Colab, Paperspace, etc.)
3. Using smaller vision-language models
"""

import sys

import requests
import torch
from PIL import Image
from transformers import AutoModelForImageTextToText, BitsAndBytesConfig

# Check environment
print("=== Environment Check ===")
print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")

if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
    print(f"GPU Memory: {gpu_memory:.2f} GB")
else:
    print("\nNote: This example is designed for GPU inference with quantization.")
    print("For CPU inference, use the quick-e2b-it.py example instead.")
    sys.exit(0)

# Load example image
print("\n=== Loading Example Image ===")
image_url = "https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/bee.jpg"
image = Image.open(requests.get(image_url, stream=True).raw)
local_image_path = "/tmp/bee.jpg"
image.save(local_image_path)
print(f"Saved to: {local_image_path}")

# Quantization configuration
print("\n=== Quantization Configuration ===")
print("This example demonstrates 4-bit quantization settings.")
print("Note: The model may still be too large for GPUs with <10GB VRAM.")

# Show the configuration that would be used
quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_use_double_quant=True,
)

print("\nQuantization settings:")
print(f"- 4-bit precision: {quantization_config.load_in_4bit}")
print(f"- Compute dtype: {quantization_config.bnb_4bit_compute_dtype}")
print(f"- Quantization type: {quantization_config.bnb_4bit_quant_type}")
print(f"- Double quantization: {quantization_config.bnb_4bit_use_double_quant}")

print("\n=== Example Code for Loading with Quantization ===")
print("Here's how you would load the model with quantization on a suitable GPU:")

code_example = """
# Load the model with quantization (requires 10GB+ GPU)
model = AutoModelForImageTextToText.from_pretrained(
    "google/gemma-3n-e2b-it",
    quantization_config=quantization_config,
    device_map="auto",
    torch_dtype=torch.float16
)

# Create pipeline with the quantized model
pipe = pipeline(
    "image-text-to-text",
    model=model,
    tokenizer="google/gemma-3n-e2b-it",
    torch_dtype=torch.float16
)

# Prepare messages
messages = [
    {"role": "system",
     "content": [{"type": "text", "text": "You are a helpful assistant."}]},
    {"role": "user",
     "content": [
         {"type": "image", "image": "path/to/image.jpg"},
         {"type": "text", "text": "Describe this image in detail."}
     ]}
]

# Generate response
output = pipe(text=messages, max_new_tokens=200)
print(output[0]["generated_text"][-1]["content"])
"""

print(code_example)

print("\n=== Memory Requirements ===")
print("Approximate memory usage:")
print("- Full precision (FP16): ~27GB")
print("- 4-bit quantized: ~7-8GB")
print("- Plus overhead for inference: ~2-3GB")
print("\nTotal recommended: 10GB+ GPU VRAM")

print("\n=== Alternative Options ===")
print("If you don't have sufficient GPU memory:")
print("1. Use CPU inference: python examples/quick-e2b-it.py")
print("2. Use cloud GPUs: Google Colab Pro, Paperspace, AWS")
print("3. Try smaller models: BLIP-2, LLaVA-1.5-7b")
print("4. Use model APIs: Replicate, Hugging Face Inference API")

# Show how to check if quantization would work
if gpu_memory < 10:
    print(f"\n⚠️  Warning: Your GPU ({gpu_memory:.1f}GB) may not have enough memory.")
    print("   Consider using one of the alternative options above.")
else:
    print(f"\n✓ Your GPU ({gpu_memory:.1f}GB) should support quantized inference.")
    print("   You can try loading the model with the code example above.")

# Only attempt to load if GPU has enough memory
if gpu_memory >= 10:
    print("\n=== Attempting to Load Model ===")
    try:
        print("Loading model with quantization...")
        model = AutoModelForImageTextToText.from_pretrained(
            "google/gemma-3n-e2b-it",
            quantization_config=quantization_config,
            device_map="auto",
            torch_dtype=torch.float16,
        )

        # Create pipeline with the quantized model
        print("Creating pipeline...")
        from transformers import pipeline

        pipe = pipeline(
            "image-text-to-text",
            model=model,
            tokenizer="google/gemma-3n-e2b-it",
            torch_dtype=torch.float16,
        )

        # Prepare messages in the expected format
        messages = [
            {
                "role": "system",
                "content": [{"type": "text", "text": "You are a helpful assistant."}],
            },
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": local_image_path},
                    {"type": "text", "text": "Describe this image in detail."},
                ],
            },
        ]

        # Generate response
        print("Generating response...")
        output = pipe(text=messages, max_new_tokens=200)

        print("\n=== Model Response ===")
        print(output[0]["generated_text"][-1]["content"])

        # Show final memory usage
        print("\nFinal GPU Memory Usage:")
        print(f"Allocated: {torch.cuda.memory_allocated() / 1024**3:.2f} GB")
        print(f"Reserved: {torch.cuda.memory_reserved() / 1024**3:.2f} GB")

    except Exception as e:
        print(f"\nError loading model: {e}")
        print("\nThis is expected if your GPU doesn't have sufficient memory.")
        print("Please refer to the alternative options listed above.")
else:
    print("\n=== Skipping Model Loading ===")
    print("Your GPU doesn't meet the minimum memory requirements.")
    print("Please use one of the alternative options listed above.")
