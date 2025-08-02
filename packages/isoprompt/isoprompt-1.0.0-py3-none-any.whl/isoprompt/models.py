"""
IsoPrompt - AI-powered prompt optimization tool.
Data structures for IsoPrompt.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel


class IsoPromptMode(BaseModel):
    """
    A model for a IsoPrompt mode.
    """

    name: str
    description: str
    examples: List[str]
    instructions: str
    parameters: Optional[Dict[str, str]] = None


class IsoPromptDomain(BaseModel):
    """
    A model for a IsoPrompt domain.
    """

    name: str
    description: str
    examples: List[str]
    instructions: str
    parameters: Optional[Dict[str, str]] = None
