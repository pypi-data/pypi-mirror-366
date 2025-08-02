#!/usr/bin/env python3
"""Basic usage examples for IsoPrompt."""

from isoprompt import (
    optimize_prompt,
    get_available_mode_names,
    get_available_domain_names,
)

# Load environment variables
from dotenv import load_dotenv


def load_env():
    """Load the environment variables from the .env file."""
    env_loaded = load_dotenv(dotenv_path=".env")
    if env_loaded:
        print("🔧 Environment variables loaded from .env file.")
    else:
        print("🔧 No .env file found. Using default environment variables.")
        print("🔧 Please create a .env file with the following variables:")
        print("🔧 OPENAI_API_KEY=your_api_key")


def main():
    """Run the example."""
    load_env()
    # Simple prompt optimization
    prompt = "Write a blog post about AI"
    optimized = optimize_prompt(prompt)
    print(f"Optimized prompt:\n{optimized}\n")

    # Using a specific mode
    optimized_analytical = optimize_prompt(prompt, mode="analytical", temperature=0.5)
    print(f"Analytical prompt:\n{optimized_analytical}\n")

    # Using domain specialization
    optimized_tech = optimize_prompt(
        prompt, mode="analytical", domain="technology", temperature=0.5
    )
    print(f"Tech-focused prompt:\n{optimized_tech}\n")

    # List available modes
    modes = get_available_mode_names()
    print("Available modes:")
    for mode in modes:
        print(f"- {mode}")

    # List available domains
    domains = get_available_domain_names()
    print("\nAvailable domains:")
    for domain in domains:
        print(f"- {domain}")


if __name__ == "__main__":
    main()
