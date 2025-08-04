import base64

import ollama


def encode_image(image_path):
    """Encode image to base64."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


# Example: Analyze an image
image_path = "/content/img1.png"
image_base64 = encode_image(image_path)

response = ollama.chat(
    model="gemma3:4b",
    messages=[
        {
            "role": "user",
            "content": "What do you see in this image?",
            "images": [image_base64],
        }
    ],
)

print(response["message"]["content"])
