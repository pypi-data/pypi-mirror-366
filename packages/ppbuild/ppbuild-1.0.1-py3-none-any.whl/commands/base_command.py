"""Base command interface for the Command pattern."""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

logger = logging.getLogger("pp")


class Command(ABC):
    """Abstract base class for all commands."""

    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self._executed = False
        self._result: Optional[Any] = None

    @abstractmethod
    def execute(self) -> Any:
        """Execute the command and return result."""
        pass

    @abstractmethod
    def validate(self) -> bool:
        """Validate command can be executed."""
        pass

    def can_undo(self) -> bool:
        """Check if command supports undo operation."""
        return False

    def undo(self) -> Any:
        """Undo the command if supported."""
        if not self.can_undo():
            raise NotImplementedError(f"Command {self.name} does not support undo")

    @property
    def executed(self) -> bool:
        """Check if command has been executed."""
        return self._executed

    @property
    def result(self) -> Any:
        """Get the result of the last execution."""
        return self._result


class CommandContext:
    """Context object passed to commands containing shared state."""

    def __init__(self, config: Dict[str, Any], env: Dict[str, str], args: Any):
        self.config = config
        self.env = env
        self.args = args
        self.working_directory: Optional[str] = None
        self.virtual_env: Optional[str] = None
        self.parameters: Dict[str, Any] = {}
