"""Base parameter strategy interface."""

from abc import ABC, abstractmethod
from typing import Any, Dict


class ParameterStrategy(ABC):
    """Abstract base class for parameter validation strategies."""

    @abstractmethod
    def validate_and_convert(
        self, param_name: str, param_config: Dict[str, Any], value: Any
    ) -> Any:
        """Validate and convert parameter value according to its configuration."""
        pass

    @abstractmethod
    def get_type_name(self) -> str:
        """Get the type name this strategy handles."""
        pass
