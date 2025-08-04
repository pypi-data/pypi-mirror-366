# --- NEW imports -------------------------------------------------------------
import json

from pydantic import BaseModel, Field, ValidationError

# -----------------------------------------------------------------------------
from transformers import TextStreamer
from unsloth import FastModel

# 1.  Load (or keep) your model exactly as before -----------------------------
fourbit_models = [
    # … (unchanged list) …
]
model, tokenizer = FastModel.from_pretrained(
    model_name="unsloth/gemma-3n-E4B-it",
    dtype=None,
    max_seq_length=1024,
    load_in_4bit=True,
    full_finetuning=False,
)


# 2.  Declare the structured output schema -----------------------------------
class FireDescription(BaseModel):
    has_flame: bool = Field(
        description="Whether fire or flames are detected in the image"
    )
    has_out_of_control_fire: bool = Field(
        description=(
            "Is this a dangerous fire that is either out-of-control, "
            "likely to spread quickly, or burning where it shouldn’t "
            "be (e.g., outside a firepit)"
        )
    )
    description: str = Field(
        description="A short, natural‑language description of what’s happening"
    )


# 3.  Helper that                 (a) sends a system prompt telling Gemma to
#                                 return **only** JSON matching the schema
#                                 (b) parses & validates the reply ------------
def gemma_fire_inference(messages, max_new_tokens: int = 256) -> FireDescription:
    system_prompt = (
        "You are an image‑safety assistant.\n"
        "Respond with **one and only one** JSON object—no markdown fences, "
        "no surrounding text.\n\n"
        "• Markdown, narrative text, or explanations before or after the JSON.\n\n"
        "The JSON MUST match this exact schema, in this exact key order:\n"
        "{\n"
        '  "has_flame": boolean,                       # true if any flame is visible\n'
        '  "has_out_of_control_fire": boolean,         # true if fire is spreading or uncontained\n'
        '  "description": string                       # ≤ 12 words; focus ONLY on fire status\n'
        "}\n\n"
        "Formatting rules:\n"
        "• Use lowercase true/false for booleans.\n"
        "• Keep the description short, factual, and fire‑specific (e.g. "
        '"small contained campfire" or "large flames spreading to grass"). '
        "Do NOT mention people, objects, camera angles, colors, or anything unrelated "
        "to the fire hazard itself.\n"
        "• Do not output code‑block back‑ticks, explanations, or any text outside the JSON."
    )

    # 🟢  FIX: make the content a list of message parts
    system_message = {
        "role": "system",
        "content": [{"type": "text", "text": system_prompt}],
    }

    tokenized = tokenizer.apply_chat_template(
        [system_message, *messages],  # prepend system instructions
        add_generation_prompt=True,
        tokenize=True,
        return_dict=True,
        return_tensors="pt",
    ).to("cuda")

    output_ids = model.generate(
        **tokenized,
        max_new_tokens=max_new_tokens,
        temperature=1.0,
        top_p=0.95,
        top_k=64,
        streamer=TextStreamer(tokenizer, skip_prompt=True),
    )

    full_text = tokenizer.decode(output_ids[0], skip_special_tokens=True)
    json_str = full_text[
        full_text.find("```json") + len("```json") : full_text.rfind("```")
    ]

    print(json_str)
    try:
        data = json.loads(json_str)
        return FireDescription(**data)
    except (json.JSONDecodeError, ValidationError) as err:
        raise RuntimeError(
            f"Model output was not valid JSON for FireDescription:\n{full_text}"
        ) from err


# 4.  Example usage -----------------------------------------------------------
sloth_link = "/content/youtube_frames/6evFKKruJ0c/frame_0005_t5.0s.jpg"
messages = [
    {
        "role": "user",
        "content": [
            {"type": "image", "image": sloth_link},
            {"type": "text", "text": "Describe any fire hazards you see."},
        ],
    }
]

fire_report = gemma_fire_inference(messages)
# print(fire_report.model_dump())  # or use the pydantic object directly
