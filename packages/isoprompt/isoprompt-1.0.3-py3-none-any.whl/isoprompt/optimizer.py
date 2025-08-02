"""Core prompt optimization functions."""

import os
import sys
from typing import Any, Dict, Optional

try:
    import openai
except ImportError:
    print(
        "Error: openai package not installed. Run: pip install openai", file=sys.stderr
    )
    sys.exit(1)

import json

from .constants import (
    DEFAULT_LLM_MODEL,
    DEFAULT_MODE,
    DEFAULT_TEMPERATURE,
    DEFAULT_MAX_TOKENS,
    SUPPORTED_LLM_MODELS,
)
from .domains import get_available_domain_names, is_domain_valid
from .modes import get_available_mode_names, is_mode_valid
from .templates import get_optimization_template


def create_openai_client() -> openai.OpenAI:
    """Create OpenAI client with API key validation."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY environment variable not set. "
            "Please set your OpenAI API key: "
            "export OPENAI_API_KEY='your-api-key'"
        )

    return openai.OpenAI(api_key=api_key)


def optimize_prompt(
    user_input: str,
    mode: str = DEFAULT_MODE,
    domain: Optional[str] = None,
    model: str = DEFAULT_LLM_MODEL,
    temperature: float = DEFAULT_TEMPERATURE,
    verbose: bool = False,
) -> str:
    """
    Optimize a user's basic prompt into a high-quality, production-ready prompt.

    Args:
        user_input: The user's basic prompt or request
        mode: Optimization mode (simple, reasoning, chain_of_thought,
              creative, analytical)
        domain: Optional domain specialization
        model: OpenAI model to use for optimization
        temperature: Temperature for generation (lower = more focused)
        verbose: Whether to print verbose output
    Returns:
        Optimized prompt string
    """
    client = create_openai_client()

    if verbose:
        print(
            f"🔧 Optimizing prompt with mode: {mode}, domain: {domain}, model: {model}, temperature: {temperature}."
        )

    # Get the optimization template
    system_prompt = get_optimization_template(mode, domain)
    user_prompt = f"User Query: {user_input}"

    if verbose:
        print(f"🔧 System Prompt: {system_prompt}.")
        print(f"🔧 User Prompt: {user_prompt}.")

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    if verbose:
        print(f"🔧 Messages: {json.dumps(messages, indent=4)}.")

    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,  # type: ignore
            temperature=temperature,
            max_tokens=DEFAULT_MAX_TOKENS,
        )

        content = response.choices[0].message.content
        if not content:
            raise ValueError("No content in OpenAI response.")

        if verbose:
            print(f"🔧 Response: {content}.")

        return content.strip()

    except Exception as e:
        raise Exception(f"Failed to optimize prompt: {e}.")


def validate_config(config: Dict[str, Any]) -> None:
    """
    Validate configuration parameters.

    Args:
        config: A dictionary containing the configuration parameters.
        mode: The mode to use for optimization.
        domain: The domain to use for optimization.
        model: The model to use for optimization.
        temperature: The temperature to use for optimization.

    Raises:
        ValueError: If the mode, domain, or temperature is invalid.
    """

    if not config:
        raise ValueError("No configuration provided.")

    if config.get("mode") and not is_mode_valid(config["mode"]):
        mode_names = get_available_mode_names()
        raise ValueError(f"Invalid mode. Available: {mode_names}.")

    if config.get("domain") and not is_domain_valid(config["domain"]):
        domain_names = get_available_domain_names()
        raise ValueError(f"Invalid domain. Available: {domain_names}.")

    temp = config.get("temperature", DEFAULT_TEMPERATURE)
    if not 0.0 <= temp <= 2.0:
        raise ValueError("Temperature must be between 0.0 and 2.0.")

    model = config.get("model", DEFAULT_LLM_MODEL)
    if model not in SUPPORTED_LLM_MODELS:
        raise ValueError(f"Invalid model. Available: {SUPPORTED_LLM_MODELS}.")
