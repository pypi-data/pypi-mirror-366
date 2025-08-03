"""Parser utilities for creating argument parsers."""

import argparse
import logging
import sys
from typing import Any, Dict

from .error_context import PPError, create_config_error

logger = logging.getLogger("pp")


def create_parser_for_app(
    app_name: str, app_config: Dict[str, Any], subparsers
) -> argparse.ArgumentParser:
    """Create argument parser for an application."""
    help_text = app_config.get("help", f"Run {app_name}")
    app_parser = subparsers.add_parser(app_name, help=help_text)

    if "actions" not in app_config:
        error_ctx = (
            create_config_error(
                f"Application '{app_name}' must define 'actions'",
                app_name=app_name,
                missing_field="actions",
            )
            .with_component("ParserUtils")
            .with_operation("create_parser_for_app")
            .with_suggestion(
                f"Add an 'actions' section to {app_name} in your configuration"
            )
            .with_suggestion(
                "Example: actions: { run: { command: ['echo', 'hello'] } }"
            )
            .build()
        )
        raise PPError(error_ctx)

    actions = app_config["actions"]
    default_action = app_config.get("default_action")

    # If there's only one action or a clear default, simplify the interface
    if len(actions) == 1 or (default_action and len(actions) <= 3):
        # Add action as optional argument for simpler UX
        action_choices = list(actions.keys())
        app_parser.add_argument(
            "action",
            nargs="?",
            choices=action_choices,
            default=default_action,
            help=(
                f"Action to perform (default: {default_action})"
                if default_action
                else "Action to perform"
            ),
        )

        # Add all parameters from all actions
        all_parameters = {}
        for action_name, action_config in actions.items():
            parameters = action_config.get("parameters", {})
            for param_name, param_config in parameters.items():
                if param_name not in all_parameters:
                    param_copy = param_config.copy()
                    param_copy["required"] = False
                    all_parameters[param_name] = param_copy

        # Add parameter arguments
        for param_name, param_config in all_parameters.items():
            add_parameter_argument(app_parser, param_name, param_config)
    else:
        # Create subparsers for each action for complex applications
        action_subparsers = app_parser.add_subparsers(
            dest="action", help="Available actions", metavar="ACTION"
        )

        # Create a parser for each action with its specific parameters
        for action_name, action_config in actions.items():
            action_help = action_config.get("help", f"Run {action_name}")
            action_parser = action_subparsers.add_parser(action_name, help=action_help)

            # Add parameters specific to this action
            parameters = action_config.get("parameters", {})
            for param_name, param_config in parameters.items():
                add_parameter_argument(action_parser, param_name, param_config)

        # Set default action if specified
        if default_action:
            app_parser.set_defaults(action=default_action)

    return app_parser


def add_parameter_argument(
    parser: argparse.ArgumentParser, param_name: str, param_config: Dict[str, Any]
) -> None:
    """Add a single parameter argument to parser."""
    param_type = param_config.get("type", "string")
    required = param_config.get("required", False)
    default = param_config.get("default")
    help_text = param_config.get("help", f"{param_name} parameter")
    choices = param_config.get("choices")

    # Convert parameter name to CLI argument format
    arg_name = f"--{param_name.replace('_', '-')}"

    kwargs = {
        "dest": param_name,
        "help": help_text,
    }

    # Handle different parameter types
    if param_type == "boolean":
        # Boolean parameters are flags
        kwargs["action"] = "store_true"
        if default is True:
            # If default is True, make it store_false instead
            kwargs["action"] = "store_false"
            arg_name = f"--no-{param_name.replace('_', '-')}"
    else:
        # For non-boolean types, set required and default
        if required:
            kwargs["required"] = True
        elif default is not None:
            kwargs["default"] = default

        if param_type == "integer":
            kwargs["type"] = int
        elif param_type == "float":
            kwargs["type"] = float
        else:  # string
            kwargs["type"] = str

        # Add choices if specified
        if choices:
            kwargs["choices"] = choices

    parser.add_argument(arg_name, **kwargs)
