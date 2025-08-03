"""Application command implementation."""

import logging
import sys
from typing import Any, Optional

from helpers.config_helper import ContextHelper
from utils.error_context import PPError, create_execution_error

from .action_command import ActionCommand
from .base_command import Command, CommandContext


class AppCommand(Command):
    """Command for executing application actions."""

    def __init__(self, app_name: str, context: CommandContext) -> None:
        super().__init__(f"app:{app_name}", f"Execute {app_name} application")
        self.app_name = app_name
        self.context = context
        self.action_command: Optional[ActionCommand] = None
        self.context_helper = ContextHelper(self.context)

    def validate(self) -> bool:
        """Validate the application exists and has valid configuration."""
        app_config = self.context.config["applications"].get(self.app_name)
        if not app_config:
            self.logger.error("Application %s not found in config", self.app_name)
            return False

        if "actions" not in app_config:
            self.logger.error("Application %s must define 'actions'", self.app_name)
            return False

        return True

    def execute(self) -> Any:
        """Execute the application command."""
        if not self.validate():
            error_ctx = (
                create_execution_error(
                    f"Application validation failed: {self.app_name}",
                    app_name=self.app_name,
                )
                .with_component("AppCommand")
                .with_operation("execute")
                .build()
            )
            raise PPError(error_ctx)

        # todo: fix circular import at top-level import
        from utils.builders import FluentCommandBuilder

        builder = FluentCommandBuilder.for_action(
            self.app_name,
            self.get_action_name(),
            self.context.config,
            self.context.args,
        )

        self.action_command = builder.build_action_command()
        result = self.action_command.execute()
        self._executed = True
        self._result = result
        return result

    def get_action_name(self) -> str:
        """Get action name from args or use default action."""
        action_name = self.context_helper.get_action_name()
        default_action_name = self.context_helper.get_default_action_name()

        if action_name:
            self.logger.debug(
                "Using action %s for application %s",
                action_name,
                self.app_name,
            )
            return action_name
        if default_action_name:
            self.logger.debug(
                "Using default action %s for application %s",
                default_action_name,
                self.app_name,
            )
            return default_action_name
        # todo: check if only 1 action_name
        # todo: show help if more than 1 and none specified

        error_ctx = (
            create_execution_error(
                f"No action specified and no default action defined for "
                f"application {self.app_name}",
                app_name=self.app_name,
            )
            .with_component("AppCommand")
            .with_operation("get_action_name")
            .with_suggestion(f"Specify an action: pp {self.app_name} <action>")
            .with_suggestion("Add a default_action to your application configuration")
            .build()
        )
        raise PPError(error_ctx)

    @property
    def logger(self) -> logging.Logger:
        """Get logger instance."""
        return logging.getLogger("pp")
