# %pip install transformers torch bitsandbytes pillow requests

# from huggingface_hub import notebook_login

# notebook_login()


from datetime import datetime

import requests
import torch
from transformers import AutoProcessor, Gemma3nForConditionalGeneration

t1 = datetime.now()


model_id = "google/gemma-3n-e4b-it"

model = Gemma3nForConditionalGeneration.from_pretrained(
    model_id,
    device_map="auto",
    torch_dtype=torch.bfloat16,
).eval()

processor = AutoProcessor.from_pretrained(model_id)

# Download the image to a local file
image_url = "https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/bee.jpg"
local_image_path = "image.jpg"
response = requests.get(image_url, stream=True)
if response.status_code == 200:
    with open(local_image_path, "wb") as f:
        for chunk in response.iter_content(1024):
            f.write(chunk)
    print(f"Image downloaded to {local_image_path}")
else:
    print(f"Failed to download image. Status code: {response.status_code}")
    exit()  # Exit if image download fails


messages = [
    {
        "role": "system",
        "content": [{"type": "text", "text": "You are a helpful assistant."}],
    },
    {
        "role": "user",
        "content": [
            {"type": "image", "image": local_image_path},  # Use the local image path
            {"type": "text", "text": "Is there an out of control fire in this image?"},
        ],
    },
]

inputs = processor.apply_chat_template(
    messages,
    add_generation_prompt=True,
    tokenize=True,
    return_dict=True,
    return_tensors="pt",
).to(model.device)

input_len = inputs["input_ids"].shape[-1]

from datetime import datetime

t1 = datetime.now()

with torch.inference_mode():
    generation = model.generate(
        **inputs, max_new_tokens=100, do_sample=False, cache_implementation="static"
    )
    generation = generation[0][input_len:]
print("inference elapsed:", datetime.now() - t1)

t1 = datetime.now()
decoded = processor.decode(generation, skip_special_tokens=True)
print(decoded)
print("decode elapsed:", datetime.now() - t1)

# Clean up GPU memory
del model
del processor
del inputs
del generation
if torch.cuda.is_available():
    torch.cuda.empty_cache()
    print("GPU memory cleared!")
