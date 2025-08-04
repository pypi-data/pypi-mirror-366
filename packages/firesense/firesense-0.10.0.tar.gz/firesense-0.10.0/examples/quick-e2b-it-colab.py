import requests
import torch
from PIL import Image
from transformers import pipeline

print("Loading gemma-3n-e2b-it example for Colab...")

# Install required packages (uncomment if needed in Colab)
# !pip install transformers torch pillow accelerate

# Login to HuggingFace if required (uncomment and add your token)
# from huggingface_hub import login
# login(token="YOUR_HF_TOKEN")

# Load an example image
image_url = "https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/bee.jpg"
image = Image.open(requests.get(image_url, stream=True).raw)

# Save the image to a local file
local_image_path = "test_image.jpg"
image.save(local_image_path)
print(f"Image saved to: {local_image_path}")

# For Colab: Use CPU or GPU with memory optimization
if torch.cuda.is_available():
    device = "cuda"
    torch_dtype = torch.float16
    print("GPU available, using CUDA with float16")
else:
    device = "cpu"
    torch_dtype = torch.float32
    print("No GPU available, using CPU with float32")

print(f"Using device: {device}")
print(f"Using dtype: {torch_dtype}")
print("Loading model (this may take a few minutes)...")

try:
    # Load with memory optimization
    pipe = pipeline(
        "image-text-to-text",
        model="google/gemma-3n-e2b-it",
        device=device,
        torch_dtype=torch_dtype,
        low_cpu_mem_usage=True,  # Important for Colab
        device_map="auto" if device == "cuda" else None,  # Auto device mapping for GPU
    )
    print("Model loaded successfully!")

except RuntimeError as e:
    if "out of memory" in str(e).lower():
        print("GPU out of memory! Falling back to CPU...")
        torch.cuda.empty_cache()  # Clear GPU cache
        device = "cpu"
        torch_dtype = torch.float32

        pipe = pipeline(
            "image-text-to-text",
            model="google/gemma-3n-e2b-it",
            device=device,
            torch_dtype=torch_dtype,
            low_cpu_mem_usage=True,
        )
        print("Model loaded on CPU!")
    else:
        raise e

# Prepare messages
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

# Generate response with memory-efficient settings
print("Generating response...")
try:
    output = pipe(
        text=messages,
        max_new_tokens=100,  # Reduced for memory efficiency
        do_sample=False,  # Disable sampling for deterministic output
    )

    print("\nModel response:")
    print(output[0]["generated_text"][-1]["content"])

except Exception as e:
    print(f"Error during generation: {e}")
    print("\nTroubleshooting tips:")
    print("1. Try restarting the runtime and running again")
    print("2. Make sure you have enough RAM/GPU memory")
    print("3. Try using a smaller max_new_tokens value")
    print(
        "4. Ensure you're logged into HuggingFace if the model requires authentication"
    )

# Clean up to free memory
if "pipe" in locals():
    del pipe
    if device == "cuda":
        torch.cuda.empty_cache()
    print("\nMemory cleaned up!")
