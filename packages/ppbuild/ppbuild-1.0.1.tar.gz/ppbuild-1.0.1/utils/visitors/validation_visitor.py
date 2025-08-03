"""Configuration validation visitor."""

import logging
from typing import List

from .base_visitor import ConfigVisitor

logger = logging.getLogger("pp")


class ValidationVisitor(ConfigVisitor):
    """Visitor that validates configuration structure and content."""

    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def visit_application(self, app):
        """Validate application configuration."""
        logger.debug(f"Validating application: {app.name}")

        # Check required fields
        if not app.config.get("help"):
            self.warnings.append(f"Application '{app.name}' missing help text")

        # Check actions exist
        if not app.config.get("actions"):
            self.errors.append(f"Application '{app.name}' has no actions defined")

        # Validate default action exists
        default_action = app.config.get("default_action")
        if default_action and default_action not in app.actions:
            self.errors.append(
                f"Application '{app.name}' default_action "
                f"'{default_action}' not found in actions"
            )

        # Validate directory path if specified
        directory = app.config.get("directory")
        if directory and not isinstance(directory, str):
            self.errors.append(f"Application '{app.name}' directory must be a string")

    def visit_action(self, action):
        """Validate action configuration."""
        logger.debug(f"Validating action: {action.name}")

        # Check required fields
        if not action.config.get("help"):
            self.warnings.append(f"Action '{action.name}' missing help text")

        if not action.config.get("command"):
            self.errors.append(f"Action '{action.name}' missing command")
        else:
            command = action.config["command"]
            if not isinstance(command, list) or not command:
                self.errors.append(
                    f"Action '{action.name}' command must be a non-empty list"
                )

    def visit_parameter(self, parameter):
        """Validate parameter configuration."""
        logger.debug(f"Validating parameter: {parameter.name}")

        param_type = parameter.config.get("type", "string")
        valid_types = {"string", "integer", "float", "boolean"}

        if param_type not in valid_types:
            self.errors.append(
                f"Parameter '{parameter.name}' has invalid type '{param_type}'. "
                f"Valid types: {', '.join(valid_types)}"
            )

        # Validate type-specific constraints
        if param_type in ("integer", "float"):
            min_val = parameter.config.get("min")
            max_val = parameter.config.get("max")

            if min_val is not None and max_val is not None and min_val > max_val:
                self.errors.append(
                    f"Parameter '{parameter.name}' min value ({min_val}) "
                    f"greater than max value ({max_val})"
                )

        # Validate choices
        choices = parameter.config.get("choices")
        if choices and not isinstance(choices, list):
            self.errors.append(f"Parameter '{parameter.name}' choices must be a list")

        # Check default value is valid if specified
        default = parameter.config.get("default")
        if default is not None and choices and default not in choices:
            self.errors.append(
                f"Parameter '{parameter.name}' default value '{default}' "
                f"not in choices: {choices}"
            )

    def has_errors(self) -> bool:
        """Check if validation found any errors."""
        return len(self.errors) > 0

    def get_error_summary(self) -> str:
        """Get a summary of validation errors and warnings."""
        summary = []

        if self.errors:
            summary.append(f"Errors ({len(self.errors)}):")
            for error in self.errors:
                summary.append(f"  - {error}")

        if self.warnings:
            summary.append(f"Warnings ({len(self.warnings)}):")
            for warning in self.warnings:
                summary.append(f"  - {warning}")

        return "\n".join(summary) if summary else "No validation issues found"
