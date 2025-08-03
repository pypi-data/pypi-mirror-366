"""Parameter strategy registry."""

import logging
from typing import Any, Dict

from utils.error_context import PPError, create_validation_error

from .base_strategy import ParameterStrategy
from .boolean_strategy import BooleanParameterStrategy
from .float_strategy import FloatParameterStrategy
from .integer_strategy import IntegerParameterStrategy
from .string_strategy import StringParameterStrategy

logger = logging.getLogger("pp")


class ParameterStrategyRegistry:
    """Registry for parameter validation strategies."""

    def __init__(self):
        self._strategies: Dict[str, ParameterStrategy] = {}
        self._register_default_strategies()

    def _register_default_strategies(self):
        """Register default parameter strategies."""
        strategies = [
            StringParameterStrategy(),
            IntegerParameterStrategy(),
            FloatParameterStrategy(),
            BooleanParameterStrategy(),
        ]

        for strategy in strategies:
            self.register_strategy(strategy)

    def register_strategy(self, strategy: ParameterStrategy):
        """Register a parameter validation strategy."""
        self._strategies[strategy.get_type_name()] = strategy
        logger.debug(f"Registered parameter strategy: {strategy.get_type_name()}")

    def get_strategy(self, param_type: str) -> ParameterStrategy:
        """Get parameter strategy by type name."""
        strategy = self._strategies.get(param_type)
        if not strategy:
            available_types = list(self._strategies.keys())
            error_ctx = (
                create_validation_error(
                    f"Unknown parameter type: {param_type}",
                    parameter_type=param_type,
                    available_types=available_types,
                )
                .with_component("ParameterRegistry")
                .with_suggestion(
                    f"Use one of the supported types: {', '.join(available_types)}"
                )
                .build()
            )
            raise PPError(error_ctx)
        return strategy

    def validate_parameter(
        self, param_name: str, param_config: Dict[str, Any], value: Any
    ) -> Any:
        """Validate parameter using appropriate strategy."""
        param_type = param_config.get("type", "string")
        strategy = self.get_strategy(param_type)
        return strategy.validate_and_convert(param_name, param_config, value)


# Global registry instance
parameter_registry = ParameterStrategyRegistry()
