#!/usr/bin/env python3
"""Setup script for fire detection system."""

import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


def check_dependencies():
    """Check if required dependencies are installed."""
    console.print("[bold blue]Checking dependencies...[/bold blue]")

    required_packages = [
        ("torch", "torch"),
        ("transformers", "transformers"),
        ("opencv-python", "cv2"),
        ("pillow", "PIL"),
        ("numpy", "numpy"),
        ("pydantic", "pydantic"),
        ("typer", "typer"),
        ("rich", "rich"),
    ]

    missing_packages = []

    for package_name, import_name in required_packages:
        try:
            __import__(import_name)
            console.print(f"✅ {package_name}")
        except ImportError:
            console.print(f"❌ {package_name}")
            missing_packages.append(package_name)

    if missing_packages:
        console.print(f"\n[red]Missing packages: {', '.join(missing_packages)}[/red]")
        console.print("Run: [cyan]uv pip install -e '.[dev]'[/cyan]")
        return False

    console.print("\n[green]All dependencies installed![/green]")
    return True


def setup_directories():
    """Create necessary directories."""
    console.print("\n[bold blue]Setting up directories...[/bold blue]")

    directories = [
        Path("models/gemma-3n-e4b"),
        Path("output"),
        Path("examples"),
        Path("data/sample_videos"),
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        console.print(f"📁 Created: {directory}")

    console.print("\n[green]Directories created![/green]")


def create_model_placeholder():
    """Create model placeholder files."""
    console.print("\n[bold blue]Setting up model placeholder...[/bold blue]")

    model_dir = Path("models/gemma-3n-e4b")

    # Create config file
    config_content = """{
  "model_type": "gemma",
  "model_variant": "gemma-3n-e4b",
  "quantization": "4bit",
  "vision_encoder": "clip",
  "image_resolution": 336,
  "vocab_size": 256000,
  "hidden_size": 3072,
  "intermediate_size": 24576,
  "num_hidden_layers": 28,
  "num_attention_heads": 24,
  "num_key_value_heads": 8,
  "head_dim": 128,
  "max_position_embeddings": 8192,
  "rms_norm_eps": 1e-06,
  "rope_theta": 10000.0,
  "attention_bias": false,
  "attention_dropout": 0.0,
  "hidden_activation": "gelu_pytorch_tanh",
  "partial_rotary_factor": 0.5,
  "query_pre_attn_scalar": 128,
  "sliding_window": null,
  "hidden_dropout": 0.0,
  "torch_dtype": "float16",
  "use_cache": true
}"""

    (model_dir / "config.json").write_text(config_content)

    # Create README
    readme_content = """# Gemma 3N E4B Model

This directory should contain the Gemma 3N E4B model files.

## Required Files

- `config.json` - Model configuration (✅ created)
- `pytorch_model.bin` - Model weights (❌ download required)
- `tokenizer.json` - Tokenizer configuration (❌ download required)
- `tokenizer_config.json` - Tokenizer settings (❌ download required)
- `special_tokens_map.json` - Special tokens (❌ download required)

## Download Instructions

1. **Option 1: Hugging Face Hub** (when available)
   ```bash
   huggingface-cli download google/gemma-3n-e4b --local-dir ./models/gemma-3n-e4b
   ```

2. **Option 2: Manual Download**
   - Download model files from official source
   - Place all files in this directory
   - Ensure file permissions are correct

## Model Specifications

- **Architecture**: Gemma 3N with vision capabilities
- **Quantization**: 4-bit (E4B variant)
- **Size**: ~1.5GB (quantized)
- **Memory**: ~6GB GPU memory recommended
- **Vision Resolution**: 336x336 pixels

## Verification

To verify the model is correctly installed:

```bash
python -c "
from transformers import AutoTokenizer, AutoModelForCausalLM
tokenizer = AutoTokenizer.from_pretrained('./models/gemma-3n-e4b')
model = AutoModelForCausalLM.from_pretrained('./models/gemma-3n-e4b')
print('Model loaded successfully!')
"
```
"""

    (model_dir / "README.md").write_text(readme_content)

    console.print("📄 Created model configuration files")
    console.print(
        "[yellow]Note: Actual model weights need to be downloaded separately[/yellow]"
    )


def create_example_config():
    """Create example configuration file."""
    console.print("\n[bold blue]Creating example configuration...[/bold blue]")

    config_content = """{
  "model": {
    "model_variant": "gemma-3n-e4b",
    "model_path": "./models/gemma-3n-e4b",
    "quantization": "4bit",
    "max_new_tokens": 200,
    "temperature": 0.1,
    "top_p": 0.9,
    "image_resolution": 336
  },
  "video": {
    "frame_interval": 2.0,
    "max_frames": null,
    "start_time": 0.0,
    "end_time": null,
    "batch_size": 1,
    "async_processing": true
  },
  "detection": {
    "confidence_threshold": 0.7,
    "save_positive_frames": true,
    "save_all_frames": false,
    "frame_format": "jpg"
  },
  "output": {
    "output_dir": "./output",
    "results_filename": "fire_detection_results",
    "output_format": "json",
    "include_metadata": true
  },
  "device": "auto",
  "debug": false,
  "verbose": false
}"""

    Path("examples/fire_detection_config.json").write_text(config_content)
    console.print("📄 Created example configuration file")


def run_basic_test():
    """Run basic system test."""
    console.print("\n[bold blue]Running basic system test...[/bold blue]")

    try:
        # Test imports
        from firesense.fire_detection.config import FireDetectionConfig
        from firesense.fire_detection.processing.video import VideoProcessor

        # Test configuration
        config = FireDetectionConfig()
        console.print("✅ Configuration loading")

        # Test video processor (without actual video)
        video_config = config.video
        VideoProcessor(video_config)
        console.print("✅ Video processor initialization")

        console.print("\n[green]Basic system test passed![/green]")
        return True

    except Exception as e:
        console.print(f"\n[red]System test failed: {e}[/red]")
        return False


def display_usage_instructions():
    """Display usage instructions."""
    usage_panel = Panel.fit(
        """[bold green]Fire Detection System Setup Complete![/bold green]

[bold]Next Steps:[/bold]

1. [cyan]Download the Gemma 3N E4B model[/cyan]
   Place model files in: [yellow]./models/gemma-3n-e4b/[/yellow]

2. [cyan]Test with a video file[/cyan]
   [code]uv run gemma-3n fire-detect sample_video.mp4[/code]

   Or use the CLI directly:
   [code]python -m firesense.fire_detection.cli analyze sample_video.mp4[/code]

3. [cyan]Try the example script[/cyan]
   [code]python examples/fire_detection_example.py[/code]

4. [cyan]Run tests[/cyan]
   [code]pytest tests/unit/test_fire_detection.py -v[/code]

[bold]Configuration:[/bold]
- Example config: [yellow]examples/fire_detection_config.json[/yellow]
- Model directory: [yellow]./models/gemma-3n-e4b/[/yellow]
- Output directory: [yellow]./output/[/yellow]

[bold]Documentation:[/bold]
- Fire Detection README: [yellow]README_FIRE_DETECTION.md[/yellow]
- CLI help: [code]python -m firesense.fire_detection.cli --help[/code]
""",
        title="🔥 Fire Detection System",
        border_style="green",
    )

    console.print(usage_panel)


def main():
    """Main setup function."""
    console.print(
        Panel.fit(
            "[bold blue]Fire Detection System Setup[/bold blue]\n"
            "Setting up the Gemma 3N E4B fire detection system...",
            border_style="blue",
        )
    )

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:

        # Check dependencies
        task1 = progress.add_task("Checking dependencies...", total=None)
        if not check_dependencies():
            progress.update(task1, description="❌ Dependencies check failed")
            sys.exit(1)
        progress.update(task1, description="✅ Dependencies checked")

        # Setup directories
        task2 = progress.add_task("Setting up directories...", total=None)
        setup_directories()
        progress.update(task2, description="✅ Directories created")

        # Create model placeholder
        task3 = progress.add_task("Setting up model placeholder...", total=None)
        create_model_placeholder()
        progress.update(task3, description="✅ Model placeholder created")

        # Create example config
        task4 = progress.add_task("Creating example configuration...", total=None)
        create_example_config()
        progress.update(task4, description="✅ Example configuration created")

        # Run basic test
        task5 = progress.add_task("Running system test...", total=None)
        if not run_basic_test():
            progress.update(task5, description="❌ System test failed")
            sys.exit(1)
        progress.update(task5, description="✅ System test passed")

    console.print()
    display_usage_instructions()


if __name__ == "__main__":
    main()
