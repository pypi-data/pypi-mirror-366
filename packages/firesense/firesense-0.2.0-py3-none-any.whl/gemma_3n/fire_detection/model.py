"""Model setup and inference for Gemma 3N E4B fire detection."""

import os
import json
import torch
from pydantic import BaseModel, ValidationError
from transformers import TextStreamer

# Disable torch compile to avoid recompilation errors
os.environ["TORCH_COMPILE_DISABLE"] = "1"

# Increase dynamo cache size limit to avoid recompilation errors
torch._dynamo.config.cache_size_limit = 64

# Import unsloth only when needed to avoid GPU check at import time
FastModel = None


class FireDescription(BaseModel):
    """Schema for structured fire detection output."""
    has_flame: bool
    has_out_of_control_fire: bool


def setup_model():
    """Load the Gemma model for inference."""
    print("Loading Gemma model...")
    
    # Import unsloth when needed
    global FastModel
    if FastModel is None:
        try:
            from unsloth import FastModel
        except NotImplementedError as e:
            print(f"Warning: {e}")
            print("Falling back to standard transformers implementation...")
            # Fallback to standard transformers
            from transformers import AutoModelForCausalLM, AutoTokenizer
            
            model = AutoModelForCausalLM.from_pretrained(
                "unsloth/gemma-3n-E4B-it",
                device_map="auto",
                torch_dtype=torch.float16,
                load_in_4bit=True,
            )
            tokenizer = AutoTokenizer.from_pretrained("unsloth/gemma-3n-E4B-it")
            
            model.eval()
            torch.set_grad_enabled(False)
            
            print("Model loaded successfully using transformers!")
            return model, tokenizer
    
    # Disable torch compile for the model to avoid recompilation issues
    import torch._dynamo
    torch._dynamo.config.suppress_errors = True
    
    model, tokenizer = FastModel.from_pretrained(
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


def gemma_fire_inference(model, tokenizer, messages, max_new_tokens: int = 256) -> FireDescription:
    """Run fire detection inference on an image."""
    system_prompt = """
    You are **FireWatch**, a vision‑language model for real‑time fire detection.

On every image you receive, output **one digit only** (no words, no punctuation):

0 – No flame present  
1 – Benign or illusory flame (birthday candle, stove burner, lighter, match, or a fire video/animation on a TV, monitor, tablet, or phone)  
2 – Contained real flame (fire pit, barbecue, indoor fireplace)  
3 – Dangerous uncontrolled fire (spreading or uncontained flames / heavy smoke)

If unsure, choose the **higher, safer** category.

Return nothing except that single digit.
    """

    system_message = {
        "role": "system",
        "content": [
            {"type": "text", "text": system_prompt}
        ]
    }

    device = "cuda" if torch.cuda.is_available() else "cpu"
    
    tokenized = tokenizer.apply_chat_template(
        [system_message] + messages,
        add_generation_prompt=True,
        tokenize=True,
        return_dict=True,
        return_tensors="pt",
    ).to(device)

    # Use no_grad context to avoid recompilation
    with torch.no_grad():
        try:
            # Try with sdp_kernel context if available
            with torch.backends.cuda.sdp_kernel(enable_flash=False, enable_math=True, enable_mem_efficient=True):
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
        except:
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
    
    # Extract JSON from the response
    # Try to find JSON between ```json markers first
    json_start = full_text.find("```json")
    json_end = full_text.rfind("```")
    
    if json_start != -1 and json_end != -1 and json_start < json_end:
        json_str = full_text[json_start + len("```json"):json_end].strip()
    else:
        # Try to find raw JSON
        json_start = full_text.find("{")
        json_end = full_text.rfind("}") + 1
        if json_start != -1 and json_end > json_start:
            json_str = full_text[json_start:json_end]
        else:
            json_str = full_text

    try:
        data = json.loads(json_str)
        return FireDescription(**data)
    except (json.JSONDecodeError, ValidationError) as err:
        # Return a default response if parsing fails
        print(f"Warning: Failed to parse model output as JSON: {err}")
        return FireDescription(
            has_flame=False,
            has_out_of_control_fire=False
        )