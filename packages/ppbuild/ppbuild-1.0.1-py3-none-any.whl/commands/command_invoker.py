"""Command invoker for managing command execution."""

import logging
from typing import Any, List, Optional

from utils.error_context import PPError, create_execution_error

from .base_command import Command

logger = logging.getLogger("pp")


class CommandInvoker:
    """Invoker class that manages command execution."""

    def __init__(self) -> None:
        self._commands: List[Command] = []
        self._current_command: Optional[Command] = None

    def execute_command(self, command: Command) -> Any:
        """Execute a single command."""
        logger.debug("Executing command: %s", command.name)

        if not command.validate():
            error_ctx = (
                create_execution_error(
                    f"Command validation failed: {command.name}",
                    command_name=command.name,
                    command_type=type(command).__name__,
                )
                .with_component("CommandInvoker")
                .with_operation("execute_command")
                .with_suggestion("Check command configuration and parameters")
                .build()
            )
            raise PPError(error_ctx)

        try:
            result = command.execute()
            self._commands.append(command)
            self._current_command = command
            logger.info("Successfully executed command: %s", command.name)
            return result
        except Exception as e:
            logger.error("Failed to execute command %s: %s", command.name, e)
            raise

    def execute_commands(self, commands: List[Command]) -> List[Any]:
        """Execute multiple commands in sequence."""
        results = []
        for command in commands:
            result = self.execute_command(command)
            results.append(result)
        return results

    def undo_last_command(self) -> bool:
        """Undo the last executed command if possible."""
        if not self._current_command:
            logger.warning("No command to undo")
            return False

        if not self._current_command.can_undo():
            logger.warning(
                "Command %s does not support undo", self._current_command.name
            )
            return False

        try:
            self._current_command.undo()
            logger.info("Successfully undid command: %s", self._current_command.name)
            return True
        except Exception as e:
            logger.error("Failed to undo command %s: %s", self._current_command.name, e)
            return False

    def get_command_history(self) -> List[Command]:
        """Get list of executed commands."""
        return self._commands.copy()

    def clear_history(self) -> None:
        """Clear command execution history."""
        self._commands.clear()
        self._current_command = None
