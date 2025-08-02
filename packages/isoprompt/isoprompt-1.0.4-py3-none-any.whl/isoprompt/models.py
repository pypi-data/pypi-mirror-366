"""
IsoPrompt - AI-powered prompt optimization tool.
Data structures for IsoPrompt.
"""

from typing import List

from pydantic import BaseModel


class IsoPromptMode(BaseModel):
    """
    A model for a IsoPrompt mode.
    """

    mode: str
    description: str
    usage: str
    capabilities: List[str]
    strictness: str
    require_citations: bool
    output_formats: List[str]
    industries: List[str]
    topics: List[str]


class IsoPromptDomain(BaseModel):
    """
    A model for a IsoPrompt domain.
    """

    domain: str
    description: str
    fields: List[str]
    applications: List[str]
