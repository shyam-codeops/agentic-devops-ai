"""
Base Agent abstraction.
"""

from abc import ABC, abstractmethod
from ..core.llm_provider import LLMProvider
from ..core.config import get_settings


class BaseAgent(ABC):
    """Abstract base class for all DevOps agents."""

    def __init__(self, name: str, role: str, llm: LLMProvider = None):
        self.name = name
        self.role = role
        self.settings = get_settings()
        self.llm = llm or LLMProvider(self.settings)

    @abstractmethod
    def run(self, *args, **kwargs):
        """Execute agent workflow."""
        pass
