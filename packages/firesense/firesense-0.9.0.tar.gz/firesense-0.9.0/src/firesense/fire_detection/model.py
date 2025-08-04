"""Model setup and inference for Gemma 3N E4B fire detection."""

import os
from typing import Any

import torch
from pydantic import BaseModel

# Disable torch compile to avoid recompilation errors
os.environ["TORCH_COMPILE_DISABLE"] = "1"

# Increase dynamo cache size limit to avoid recompilation errors
torch._dynamo.config.cache_size_limit = 64

# Import unsloth only when needed to avoid GPU check at import time
FastModel = None


class FireDescription(BaseModel):
    """Schema for structured fire detection output."""

    classification: int  # 0, 1, 2, or 3

    @property
    def has_flame(self) -> bool:
        """Returns True if any flame is detected (classification > 0)."""
        return self.classification > 0

    @property
    def has_out_of_control_fire(self) -> bool:
        """Returns True if dangerous uncontrolled fire is detected (classification == 3)."""
        return self.classification == 3


def setup_model() -> tuple[Any, Any]:
    """Load the Gemma model for inference."""
    print("Loading Gemma model...")

    # Import unsloth when needed
    global FastModel
    if FastModel is None:
        try:
            from unsloth import FastModel  # type: ignore
        except NotImplementedError as e:
            print(f"Warning: {e}")
            print("Falling back to standard transformers implementation...")
            # Fallback to standard transformers
            import torch as torch_import
            from transformers import AutoModelForCausalLM, AutoTokenizer

            model = AutoModelForCausalLM.from_pretrained(
                "unsloth/gemma-3n-E4B-it",
                device_map="auto",
                torch_dtype=torch_import.float16,
                load_in_4bit=True,
            )
            tokenizer = AutoTokenizer.from_pretrained("unsloth/gemma-3n-E4B-it")  # type: ignore

            model.eval()
            torch_import.set_grad_enabled(False)

            print("Model loaded successfully using transformers!")
            return model, tokenizer

    # Disable torch compile for the model to avoid recompilation issues
    import torch._dynamo

    torch._dynamo.config.suppress_errors = True

    model, tokenizer = FastModel.from_pretrained(  # type: ignore
        model_name="unsloth/gemma-3n-E4B-it",
        dtype=None,
        max_seq_length=1024,
        load_in_4bit=True,
        full_finetuning=False,
    )

    # Ensure model is in eval mode
    model.eval()

    # Disable gradient computation for inference
    torch.set_grad_enabled(False)

    print("Model loaded successfully!")
    return model, tokenizer


def gemma_fire_inference(
    model: Any,
    tokenizer: Any,
    messages: list[dict[str, Any]],
    max_new_tokens: int = 256,
) -> FireDescription:
    """Run fire detection inference on an image."""


    system_prompt = """
You are **FireSense**, a vision-language model for fire detection in images.

On every image you receive, output **one character only** (no words, no punctuation):
N - No flame present
O - Benign or illusory flame (birthday candle, stove burner, lighter, match, or a fire video/animation on a TV, monitor, tablet, or phone)
D - Dangerous uncontrolled fire (spreading or uncontained flames / heavy smoke)

Return nothing except that character.
    """

    system_message = {
        "role": "system",
        "content": [{"type": "text", "text": system_prompt}],
    }

    device = "cuda" if torch.cuda.is_available() else "cpu"

    tokenized = tokenizer.apply_chat_template(
        [system_message, *messages],
        add_generation_prompt=True,
        tokenize=True,
        return_dict=True,
        return_tensors="pt",
    ).to(device)

    # Use no_grad context to avoid recompilation
    with torch.no_grad():
        try:
            # Try with sdp_kernel context if available
            with torch.backends.cuda.sdp_kernel(
                enable_flash=False, enable_math=True, enable_mem_efficient=True
            ):
                output_ids = model.generate(
                    **tokenized,
                    max_new_tokens=max_new_tokens,
                    temperature=1.0,
                    top_p=0.95,
                    top_k=64,
                    streamer=None,  # Disable streaming for cleaner output
                    use_cache=True,  # Enable KV cache
                    pad_token_id=tokenizer.pad_token_id,
                    eos_token_id=tokenizer.eos_token_id,
                )
        except Exception:
            # Fallback without sdp_kernel
            output_ids = model.generate(
                **tokenized,
                max_new_tokens=max_new_tokens,
                temperature=1.0,
                top_p=0.95,
                top_k=64,
                streamer=None,  # Disable streaming for cleaner output
                use_cache=True,  # Enable KV cache
                pad_token_id=tokenizer.pad_token_id,
                eos_token_id=tokenizer.eos_token_id,
            )

    full_text = tokenizer.decode(output_ids[0], skip_special_tokens=True)

    # Extract the character and convert to classification
    # Look for the last occurrence of N, O, or D in the response
    classification = None
    char_to_class = {
        'N': 0,  # No flame
        'O': 1,  # Benign or illusory flame  
        'D': 3   # Dangerous uncontrolled fire
    }
    
    for char in reversed(full_text):
        if char in char_to_class:
            classification = char_to_class[char]
            break

    if classification is None:
        # If no valid character found, default to 0 (no flame)
        print(
            f"Warning: No valid classification character found in model output: {full_text}"
        )
        classification = 0

    return FireDescription(classification=classification)
