from abc import ABC, abstractmethod
from typing import Any

from .models import AgentInfo


class AgentBox(ABC):
    """Base class for all agents - requires AgentInput/AgentOutput subclasses"""

    def __init__(self) -> None:
        self._initialized = False

    def setup(self) -> None:
        """Override this method to initialize your agent"""
        pass

    # TODO : add pre and post hook middlewares
    def pre_hook(self) -> None:
        """Optional pre-processing hook"""
        pass

    def post_hook(self) -> None:
        """Optional post-processing hook"""
        pass

    @abstractmethod
    def invoke(self, agent_input: Any) -> Any:
        """Main entry point - implement your agent logic here

        Must use AgentInput and AgentOutput subclasses for proper API documentation
        """
        pass

    @abstractmethod
    async def ainvoke(self, agent_input: Any) -> Any:
        """Main entry point - implement your agent logic here

        Must use AgentInput and AgentOutput subclasses for proper API documentation
        """
        pass

    @abstractmethod
    def stream(self, agent_input: Any) -> Any:
        """Main entry point - implement your agent logic here

        Must use AgentInput and AgentOutput subclasses for proper API documentation
        """
        pass

    @abstractmethod
    async def astream(self, agent_input: Any) -> Any:
        """Main entry point - implement your agent logic here

        Must use AgentInput and AgentOutput subclasses for proper API documentation
        """
        pass

    @abstractmethod
    def info(self) -> AgentInfo:
        """Return information about the agent"""
        pass

    def _ensure_setup(self) -> None:
        """Ensure setup is called once"""
        if not self._initialized:
            self.setup()
            self._initialized = True
