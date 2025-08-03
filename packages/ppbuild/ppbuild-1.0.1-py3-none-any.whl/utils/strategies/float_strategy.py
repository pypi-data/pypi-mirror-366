"""Float parameter validation strategy."""

from typing import Any, Dict

from utils.error_context import PPError, create_validation_error

from .base_strategy import ParameterStrategy


class FloatParameterStrategy(ParameterStrategy):
    """Strategy for handling float parameters."""

    def validate_and_convert(
        self, param_name: str, param_config: Dict[str, Any], value: Any
    ) -> float:
        """Validate and convert float parameter."""
        if value is None or value == "":
            if param_config.get("required", False):
                error_ctx = (
                    create_validation_error(
                        f"Required float parameter '{param_name}' is missing",
                        parameter_name=param_name,
                        parameter_type="float",
                    )
                    .with_component("FloatParameterStrategy")
                    .with_suggestion(f"Provide a numeric value for --{param_name}")
                    .with_suggestion("Example: --{param_name}=3.14")
                    .build()
                )
                raise PPError(error_ctx)
            return param_config.get("default", 0.0)

        try:
            float_value = float(value)
        except (ValueError, TypeError):
            error_ctx = (
                create_validation_error(
                    f"Invalid float value for parameter '{param_name}': '{value}'",
                    parameter_name=param_name,
                    parameter_type="float",
                    provided_value=value,
                )
                .with_component("FloatParameterStrategy")
                .with_suggestion("Provide a valid numeric value")
                .with_suggestion(f"Example: --{param_name}=3.14")
                .build()
            )
            raise PPError(error_ctx)

        # Check bounds
        min_val = param_config.get("min")
        max_val = param_config.get("max")

        if min_val is not None and float_value < min_val:
            error_ctx = (
                create_validation_error(
                    f"Parameter '{param_name}' value {float_value} is below "
                    f"minimum {min_val}",
                    parameter_name=param_name,
                    parameter_type="float",
                    provided_value=float_value,
                    minimum_value=min_val,
                )
                .with_component("FloatParameterStrategy")
                .with_suggestion(f"Provide a value >= {min_val}")
                .build()
            )
            raise PPError(error_ctx)

        if max_val is not None and float_value > max_val:
            error_ctx = (
                create_validation_error(
                    f"Parameter '{param_name}' value {float_value} is above "
                    f"maximum {max_val}",
                    parameter_name=param_name,
                    parameter_type="float",
                    provided_value=float_value,
                    maximum_value=max_val,
                )
                .with_component("FloatParameterStrategy")
                .with_suggestion(f"Provide a value <= {max_val}")
                .build()
            )
            raise PPError(error_ctx)

        return float_value

    def get_type_name(self) -> str:
        return "float"
