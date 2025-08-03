"""Convenience functions for common command building patterns."""

from typing import Any, Dict

from commands.action_command import ActionCommand
from commands.app_command import AppCommand

from .fluent_command_builder import FluentCommandBuilder


def build_app_command(app_name: str, config: Dict[str, Any], args: Any) -> AppCommand:
    """Build an application command with standard configuration."""
    return FluentCommandBuilder.for_app(app_name, config, args).build_app_command()


def build_action_command(
    app_name: str, action_name: str, config: Dict[str, Any], args: Any
) -> ActionCommand:
    """Build an action command with standard configuration."""
    return FluentCommandBuilder.for_action(
        app_name, action_name, config, args
    ).build_action_command()
