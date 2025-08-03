"""Integer parameter validation strategy."""

from typing import Any, Dict

from ..error_context import PPError, create_validation_error
from .base_strategy import ParameterStrategy


class IntegerParameterStrategy(ParameterStrategy):
    """Strategy for handling integer parameters."""

    def validate_and_convert(
        self, param_name: str, param_config: Dict[str, Any], value: Any
    ) -> int:
        """Validate and convert integer parameter."""
        if value is None or value == "":
            if param_config.get("required", False):
                error_ctx = (
                    create_validation_error(
                        f"Required parameter '{param_name}' is missing",
                        parameter_name=param_name,
                        parameter_type="integer",
                        required=True,
                    )
                    .with_component("IntegerParameterStrategy")
                    .build()
                )
                raise PPError(error_ctx)
            return param_config.get("default", 0)

        try:
            int_value = int(value)
        except (ValueError, TypeError) as e:
            error_ctx = (
                create_validation_error(
                    f"Invalid value for parameter '{param_name}': expected integer",
                    parameter_name=param_name,
                    parameter_type="integer",
                    provided_value=str(value),
                )
                .with_component("IntegerParameterStrategy")
                .with_exception(e)
                .build()
            )
            raise PPError(error_ctx)

        # Check bounds
        min_val = param_config.get("min")
        max_val = param_config.get("max")

        if min_val is not None and int_value < min_val:
            error_ctx = (
                create_validation_error(
                    f"Parameter '{param_name}' must be >= {min_val}",
                    parameter_name=param_name,
                    parameter_type="integer",
                    provided_value=int_value,
                    minimum_value=min_val,
                )
                .with_component("IntegerParameterStrategy")
                .build()
            )
            raise PPError(error_ctx)

        if max_val is not None and int_value > max_val:
            error_ctx = (
                create_validation_error(
                    f"Parameter '{param_name}' must be <= {max_val}",
                    parameter_name=param_name,
                    parameter_type="integer",
                    provided_value=int_value,
                    maximum_value=max_val,
                )
                .with_component("IntegerParameterStrategy")
                .build()
            )
            raise PPError(error_ctx)

        return int_value

    def get_type_name(self) -> str:
        return "integer"
