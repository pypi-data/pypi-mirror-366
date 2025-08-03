"""Boolean parameter validation strategy."""

from typing import Any, Dict

from utils.error_context import PPError, create_validation_error

from .base_strategy import ParameterStrategy


class BooleanParameterStrategy(ParameterStrategy):
    """Strategy for handling boolean parameters."""

    def validate_and_convert(
        self, param_name: str, param_config: Dict[str, Any], value: Any
    ) -> bool:
        """Validate and convert boolean parameter."""
        if value is None:
            if param_config.get("required", False):
                error_ctx = (
                    create_validation_error(
                        f"Required boolean parameter '{param_name}' is missing",
                        parameter_name=param_name,
                        parameter_type="boolean",
                    )
                    .with_component("BooleanParameterStrategy")
                    .with_suggestion(f"Provide a value for --{param_name}")
                    .with_suggestion("Valid boolean values: true, false, yes, no, 1, 0")
                    .build()
                )
                raise PPError(error_ctx)
            return param_config.get("default", False)

        # Handle various boolean representations
        if isinstance(value, bool):
            return value

        if isinstance(value, str):
            lower_value = value.lower()
            if lower_value in ("true", "yes", "1", "on"):
                return True
            elif lower_value in ("false", "no", "0", "off", ""):
                return False
            else:
                error_ctx = (
                    create_validation_error(
                        f"Invalid boolean value for parameter '{param_name}': "
                        f"'{value}'",
                        parameter_name=param_name,
                        parameter_type="boolean",
                        provided_value=value,
                    )
                    .with_component("BooleanParameterStrategy")
                    .with_suggestion(
                        "Valid boolean values: true, false, yes, no, 1, 0, on, off"
                    )
                    .with_suggestion(f"Example: --{param_name}=true")
                    .build()
                )
                raise PPError(error_ctx)

        # Handle numeric values
        try:
            return bool(int(value))
        except (ValueError, TypeError):
            error_ctx = (
                create_validation_error(
                    f"Invalid boolean value for parameter '{param_name}': '{value}'",
                    parameter_name=param_name,
                    parameter_type="boolean",
                    provided_value=value,
                )
                .with_component("BooleanParameterStrategy")
                .with_suggestion(
                    "Valid boolean values: true, false, yes, no, 1, 0, on, off"
                )
                .with_suggestion(f"Example: --{param_name}=true")
                .build()
            )
            raise PPError(error_ctx)

    def get_type_name(self) -> str:
        return "boolean"
