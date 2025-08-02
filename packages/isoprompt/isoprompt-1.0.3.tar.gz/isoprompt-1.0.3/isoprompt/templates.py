"""
IsoPrompt - AI-powered prompt optimization tool.
Templates for IsoPrompt.
"""

import os
from typing import Optional

from .models import IsoPromptDomain, IsoPromptMode
from .modes import get_default_mode, get_available_modes
from .domains import get_default_domain, get_available_domains


def get_prompt_guidelines() -> str:
    """Get the prompt guidelines for prompt optimization."""
    with open(
        os.path.join(os.path.dirname(__file__), "prompts", "prompt_guidelines.md"), "r"
    ) as f:
        return f.read()


def construct_mode_instruction(mode: IsoPromptMode) -> str:
    """Construct the instruction for a mode."""
    mode_structure = f"""
        Mode: {mode.mode}
        Description: {mode.description}
        Usage: {mode.usage}
        Capabilities: {mode.capabilities}
        Strictness: {mode.strictness}
        Require Citations: {mode.require_citations}
        Output Formats: {mode.output_formats}
        Industries: {mode.industries}
        Topics: {mode.topics}
    """

    return mode_structure


def construct_domain_instruction(domain: IsoPromptDomain) -> str:
    """Construct the instruction for a domain."""
    domain_structure = f"""
        Domain: {domain.domain}
        Description: {domain.description}
        Fields: {domain.fields}
        Applications: {domain.applications}
    """

    return domain_structure


def get_mode_instructions(mode: str) -> str:
    """Get mode-specific instructions for prompt optimization."""

    default_mode = get_default_mode()
    modes = get_available_modes()
    mode_obj = next((m for m in modes if m.mode == mode), default_mode)

    return construct_mode_instruction(mode_obj)


def get_domain_instructions(domain: Optional[str] = None) -> str:
    """Get domain-specific instructions for prompt optimization."""

    default_domain = get_default_domain()
    if domain is None:
        return construct_domain_instruction(default_domain)

    domains = get_available_domains()
    domain_obj = next((d for d in domains if d.domain == domain), default_domain)

    return construct_domain_instruction(domain_obj)


def get_optimization_template(mode: str, domain: Optional[str] = None) -> str:
    """Get the main template for prompt optimization."""

    mode_instructions = get_mode_instructions(mode)
    domain_instructions = get_domain_instructions(domain)
    prompt_guidelines = get_prompt_guidelines()

    optimization_template = f"""
        You are a professional prompt engineer. Your job is to take a
        user's basic request and transform it into a high-quality,
        optimized prompt that will get better results from AI models.\n\n
        
        NOTE: Take the user's input and transform it into a production-ready prompt.
        Return the full optimized prompt with all improvements, format, structure, details, and style incorporated.
        
        Don't include text like this:
        
        "Certainly! Below is a highly optimized, detailed prompt designed to generate a comprehensive startup plan for an open-source research lab focused on frontier Large Language Model (LLM) research. The prompt incorporates clear instructions, structured format, and domain-specific considerations to ensure high-quality output."

        Skip text like the above and directly give the fully optimized prompt.

        Mode Instructions: \n
        '{mode_instructions}'.\n
        Domain Instructions: \n
        '{domain_instructions}'.\n\n
        
        Follow these guidelines for writing a good optimized prompt.

        Prompt Guidelines:\n 
        '{prompt_guidelines}'.\n\n
    """

    cleaned_prompt = ""

    lines = optimization_template.split("\n")
    for line in lines:
        if line.strip():
            cleaned_prompt += line.strip() + "\n"

    return cleaned_prompt
