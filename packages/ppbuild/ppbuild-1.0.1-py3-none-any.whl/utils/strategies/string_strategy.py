"""String parameter validation strategy."""

from typing import Any, Dict

from ..error_context import PPError, create_validation_error
from .base_strategy import ParameterStrategy


class StringParameterStrategy(ParameterStrategy):
    """Strategy for handling string parameters."""

    def validate_and_convert(
        self, param_name: str, param_config: Dict[str, Any], value: Any
    ) -> str:
        """Validate and convert string parameter."""
        if value is None or value == "":
            if param_config.get("required", False):
                error_ctx = (
                    create_validation_error(
                        f"Required parameter '{param_name}' is missing",
                        parameter_name=param_name,
                        parameter_type="string",
                        required=True,
                    )
                    .with_component("StringParameterStrategy")
                    .with_suggestions(
                        [
                            f"Provide a value for parameter '{param_name}'",
                            "Use --help to see parameter requirements",
                        ]
                    )
                    .build()
                )
                raise PPError(error_ctx)
            return param_config.get("default", "")

        str_value = str(value)

        # Check choices if specified
        choices = param_config.get("choices")
        if choices and str_value not in choices:
            error_ctx = (
                create_validation_error(
                    f"Invalid choice for parameter '{param_name}'",
                    parameter_name=param_name,
                    parameter_type="string",
                    provided_value=str_value,
                    valid_choices=choices,
                )
                .with_component("StringParameterStrategy")
                .with_suggestions(
                    [
                        f"Choose one of: {', '.join(choices)}",
                        "Check the spelling of your choice",
                    ]
                )
                .build()
            )
            raise PPError(error_ctx)

        return str_value

    def get_type_name(self) -> str:
        return "string"
