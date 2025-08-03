"""Parameter validation and substitution utilities."""

import logging
import re
import sys
from typing import Any, Dict, List

from .error_context import PPError, create_validation_error
from .strategies import parameter_registry

logger = logging.getLogger("pp")


def validate_parameter(
    param_name: str, param_config: Dict[str, Any], value: Any
) -> Any:
    """Validate and convert parameter value using strategy pattern."""
    return parameter_registry.validate_parameter(param_name, param_config, value)


def substitute_parameters(command: List[str], parameters: Dict[str, Any]) -> List[str]:
    """Substitute parameters in command using {param} and {param:flag} syntax."""
    result = []

    for arg in command:
        if not isinstance(arg, str):
            result.append(str(arg))
            continue

        # Find all parameter references in this argument
        param_refs = re.findall(r"\{([^}]+)\}", arg)

        if not param_refs:
            result.append(arg)
            continue

        # Process each parameter reference
        processed_arg = arg
        for param_ref in param_refs:
            if ":" in param_ref:
                # Conditional flag format: {param:--flag}
                param_name, flag = param_ref.split(":", 1)
                param_value = parameters.get(param_name)

                if param_value is True:
                    # Replace with the flag
                    processed_arg = processed_arg.replace(f"{{{param_ref}}}", flag)
                else:
                    # Remove the flag entirely
                    processed_arg = processed_arg.replace(f"{{{param_ref}}}", "")
            else:
                # Direct substitution: {param}
                param_name = param_ref
                param_value = parameters.get(param_name)

                if param_value is not None:
                    processed_arg = processed_arg.replace(
                        f"{{{param_ref}}}", str(param_value)
                    )
                else:
                    # Remove the parameter reference if no value
                    processed_arg = processed_arg.replace(f"{{{param_ref}}}", "")

        # Only add non-empty arguments
        if processed_arg.strip():
            result.append(processed_arg.strip())

    return result


def parse_action_parameters(action_config: Dict[str, Any], args) -> Dict[str, Any]:
    """Parse and validate action parameters from command line arguments."""
    parameters = {}
    param_configs = action_config.get("parameters", {})

    # Get parameter values from args or use defaults
    for param_name, param_config in param_configs.items():
        # Get value from command line args
        value = getattr(args, param_name, None)

        # For boolean parameters, handle the default properly
        if param_config.get("type") == "boolean":
            if value is None:
                value = param_config.get("default", False)
        elif value is None:
            value = param_config.get("default")

        # Validate and convert the parameter
        try:
            parameters[param_name] = validate_parameter(param_name, param_config, value)
        except (ValueError, PPError) as e:
            if isinstance(e, PPError):
                raise
            error_ctx = (
                create_validation_error(
                    f"Parameter validation failed for '{param_name}': {str(e)}",
                    parameter_name=param_name,
                    error_message=str(e),
                )
                .with_component("ParameterParser")
                .with_operation("parse_action_parameters")
                .with_exception(e)
                .build()
            )
            raise PPError(error_ctx)

    return parameters
