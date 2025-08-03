"""Fluent interface for command building."""

from typing import Any, Dict

from .command_builder import CommandBuilder


class FluentCommandBuilder:
    """Fluent interface for common command building scenarios."""

    @staticmethod
    def for_app(app_name: str, config: Dict[str, Any], args: Any) -> CommandBuilder:
        """Create builder for application command."""
        return (
            CommandBuilder()
            .with_config(config)
            .with_args(args)
            .with_app_name(app_name)
            .auto_configure_from_app_config()
        )

    @staticmethod
    def for_action(
        app_name: str, action_name: str, config: Dict[str, Any], args: Any
    ) -> CommandBuilder:
        """Create builder for action command."""
        return (
            CommandBuilder()
            .with_config(config)
            .with_args(args)
            .with_app_name(app_name)
            .with_action_name(action_name)
            .auto_configure_from_app_config()
            .auto_configure_parameters()
        )

    @staticmethod
    def for_testing(app_name: str, action_name: str = "test") -> CommandBuilder:
        """Create builder for testing with minimal setup."""
        from unittest.mock import MagicMock

        mock_args = MagicMock()
        mock_args.subcommand = app_name
        mock_args.action = action_name

        test_config = {
            "applications": {
                app_name: {
                    "help": f"Test {app_name}",
                    "actions": {
                        action_name: {
                            "help": f"Test {action_name}",
                            "command": ["echo", "test"],
                        }
                    },
                }
            }
        }

        return (
            CommandBuilder()
            .with_config(test_config)
            .with_args(mock_args)
            .with_app_name(app_name)
            .with_action_name(action_name)
        )
