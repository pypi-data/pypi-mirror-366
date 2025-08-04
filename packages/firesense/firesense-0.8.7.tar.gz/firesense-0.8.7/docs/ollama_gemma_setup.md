# Running Gemma-3n-e4b Vision Model with Ollama

This guide explains how to set up and run the Gemma-3n-e4b vision model using Ollama for local inference.

## Prerequisites

- Ollama installed on your system
- Sufficient GPU memory (8GB+ recommended)
- Python environment with required dependencies

## Installation

### 1. Install Ollama

If you haven't installed Ollama yet:

**macOS/Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Windows:**
Download from [ollama.com](https://ollama.com/download)

### 2. Create Modelfile for Gemma-3n-e4b

Create a file named `Modelfile.gemma3n` with the following content:

```dockerfile
FROM google/gemma-3n-e4b-it

# Set parameters for vision model
PARAMETER temperature 0.7
PARAMETER top_p 0.9
PARAMETER top_k 40

# System prompt for vision tasks
SYSTEM You are a helpful vision assistant capable of analyzing images and answering questions about them.
```

### 3. Create the Ollama Model

```bash
ollama create gemma3n-vision -f Modelfile.gemma3n
```

## Running the Model

### Basic Usage

Start the model:
```bash
ollama run gemma3n-vision
```

### Using with Python

```python
import ollama
import base64
from PIL import Image
import io

def encode_image(image_path):
    """Encode image to base64."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Example: Analyze an image
image_path = "path/to/your/image.jpg"
image_base64 = encode_image(image_path)

response = ollama.chat(
    model='gemma3n-vision',
    messages=[{
        'role': 'user',
        'content': 'What do you see in this image?',
        'images': [image_base64]
    }]
)

print(response['message']['content'])
```

### REST API Usage

You can also use the Ollama REST API:

```python
import requests
import json

def query_ollama_vision(image_path, prompt):
    """Query Ollama with an image."""
    image_base64 = encode_image(image_path)
    
    url = "http://localhost:11434/api/chat"
    payload = {
        "model": "gemma3n-vision",
        "messages": [{
            "role": "user",
            "content": prompt,
            "images": [image_base64]
        }],
        "stream": False
    }
    
    response = requests.post(url, json=payload)
    return response.json()

# Example usage
result = query_ollama_vision("image.jpg", "Describe this image")
print(result['message']['content'])
```

## Configuration Options

### Memory Management

For systems with limited GPU memory, you can adjust the model loading:

```bash
# Set GPU memory limit (in GB)
export OLLAMA_GPU_MEMORY=6

# Run with CPU only
export OLLAMA_GPU=false
```

### Performance Tuning

Modify the Modelfile parameters:

```dockerfile
PARAMETER num_gpu 999     # Number of layers to run on GPU
PARAMETER num_thread 8    # Number of CPU threads
PARAMETER batch_size 512  # Batch size for prompt processing
```

## Integration with Fire Detection

To use with the fire detection pipeline:

```python
import ollama
from pathlib import Path
import json

def analyze_frames_with_ollama(frames_dir, model="gemma3n-vision"):
    """Analyze extracted video frames for fire detection."""
    frames_dir = Path(frames_dir)
    results = []
    
    # Load metadata
    with open(frames_dir / "metadata.json") as f:
        metadata = json.load(f)
    
    # Analyze each frame
    for frame_info in metadata['frames']:
        frame_path = frames_dir / frame_info['filename']
        image_base64 = encode_image(str(frame_path))
        
        response = ollama.chat(
            model=model,
            messages=[{
                'role': 'user',
                'content': 'Is there any sign of fire or smoke in this image? Describe what you see.',
                'images': [image_base64]
            }]
        )
        
        results.append({
            'frame': frame_info['frame_number'],
            'timestamp': frame_info['timestamp'],
            'analysis': response['message']['content']
        })
    
    return results

# Example usage
results = analyze_frames_with_ollama("youtube_frames/VIDEO_ID")
```

## Troubleshooting

### Model Not Found
If Ollama can't find the model:
```bash
# Pull the base model first
ollama pull google/gemma-3n-e4b-it

# Then create your custom version
ollama create gemma3n-vision -f Modelfile.gemma3n
```

### GPU Memory Issues
If you encounter out of memory errors:
1. Reduce batch size in Modelfile
2. Use CPU fallback: `export OLLAMA_GPU=false`
3. Limit GPU layers: `PARAMETER num_gpu 20`

### Performance Issues
- Ensure Ollama service is running: `ollama serve`
- Check available models: `ollama list`
- Monitor GPU usage: `nvidia-smi` (NVIDIA GPUs)

## Additional Resources

- [Ollama Documentation](https://github.com/ollama/ollama)
- [Gemma Model Cards](https://huggingface.co/google/gemma-3n-e4b-it)
- [Ollama API Reference](https://github.com/ollama/ollama/blob/main/docs/api.md)