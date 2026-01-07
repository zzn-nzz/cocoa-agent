"""
Agent implementations for different AI systems.
"""

from .base import BaseAgent
from .cocoa_agent import CocoaAgent
from .openai_deep_research_agent import OpenAIDeepResearchAgent

__all__ = [
    "BaseAgent",
    "CocoaAgent",
    "OpenAIDeepResearchAgent",
]

