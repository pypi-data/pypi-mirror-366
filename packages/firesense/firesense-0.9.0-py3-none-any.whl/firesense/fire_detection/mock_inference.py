"""Mock inference for fire detection when GPU is not available."""

import random
import time
from typing import Any

from .model import FireDescription


def mock_setup_model() -> tuple[Any, Any]:
    """Mock model setup that returns dummy objects."""
    print("Loading mock model (GPU not available)...")
    print("Using random inference for demonstration purposes.")

    # Return dummy objects that won't be used
    return None, None


def mock_gemma_fire_inference(
    model: Any,
    tokenizer: Any,
    messages: list[dict[str, Any]],
    max_new_tokens: int = 256,
) -> FireDescription:
    """Generate mock fire detection results with random values."""

    # Simulate inference delay (much faster than real inference)
    time.sleep(random.uniform(0.1, 0.3))

    # Generate random classification with weighted probabilities
    # 0: 60%, 1: 20%, 2: 15%, 3: 5%
    rand = random.random()
    if rand < 0.6:
        classification = 0  # No flame
    elif rand < 0.8:
        classification = 1  # Benign/illusory flame
    elif rand < 0.95:
        classification = 2  # Contained real flame
    else:
        classification = 3  # Dangerous uncontrolled fire

    return FireDescription(classification=classification)
