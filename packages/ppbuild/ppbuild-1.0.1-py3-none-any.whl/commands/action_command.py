"""Action command implementation."""

import logging
import os
import subprocess
import sys
from typing import Any, Dict, List

from utils.error_context import (PPError, create_execution_error,
                                 create_system_error)
from utils.parameter_utils import (parse_action_parameters,
                                   substitute_parameters)
from utils.path_utils import expand_path, resolve_relative_path

from .base_command import Command, CommandContext


class ActionCommand(Command):
    """Command for executing specific application actions."""

    def __init__(
        self, app_name: str, action_name: str, context: CommandContext
    ) -> None:
        super().__init__(
            f"action:{app_name}:{action_name}",
            f"Execute {action_name} action for {app_name}",
        )
        self.app_name = app_name
        self.action_name = action_name
        self.context = context

    def validate(self) -> bool:
        """Validate the action exists and has valid configuration."""
        app_config = self.context.config["applications"].get(self.app_name, {})
        action_config = app_config.get("actions", {}).get(self.action_name)

        if not action_config:
            available_actions = list(app_config.get("actions", {}).keys())
            self.logger.error("Invalid %s action: %s", self.app_name, self.action_name)
            print(f"Available actions: {', '.join(available_actions)}")
            return False

        cmd = action_config.get("command")
        if not cmd:
            self.logger.error(
                "No command defined for %s action %s", self.app_name, self.action_name
            )
            return False

        return True

    def execute(self) -> Any:
        """Execute the action command."""
        if not self.validate():
            error_ctx = (
                create_execution_error(
                    f"Action validation failed: {self.app_name}:{self.action_name}",
                    app_name=self.app_name,
                    action_name=self.action_name,
                )
                .with_component("ActionCommand")
                .with_operation("execute")
                .build()
            )
            raise PPError(error_ctx)

        app_config = self.context.config["applications"][self.app_name]
        action_config = app_config["actions"][self.action_name]

        # Parse and validate parameters
        self._parse_parameters(action_config)

        # Get and process command
        cmd = action_config["command"]
        if self.context.parameters:
            cmd = self._substitute_parameters(cmd, self.context.parameters)
            self.logger.debug("Command after parameter substitution: %s", cmd)

        # Setup environment
        self._setup_environment(app_config)

        # Execute command
        self._run_command(cmd)

        self._executed = True
        return True

    def _parse_parameters(self, action_config: Dict[str, Any]) -> None:
        """Parse and validate action parameters."""
        if action_config.get("parameters"):
            self.context.parameters = parse_action_parameters(
                action_config, self.context.args
            )
            self.logger.debug("Parsed parameters: %s", self.context.parameters)

    def _substitute_parameters(
        self, command: List[str], parameters: Dict[str, Any]
    ) -> List[str]:
        """Substitute parameters in command."""
        return substitute_parameters(command, parameters)

    def _setup_environment(self, app_config: Dict[str, Any]) -> None:
        """Setup working directory and environment variables."""
        # Handle working directory
        if app_config.get("directory"):
            self._change_directory(app_config["directory"])

        # Handle virtual environment
        if app_config.get("venv"):
            self.context.env = self._activate_venv(app_config["venv"])

        # Handle environment variables
        if app_config.get("env_vars"):
            self.context.env.update(self._substitute_env_vars(app_config["env_vars"]))

    def _change_directory(self, directory: str) -> None:
        """Change to the specified directory."""
        directory_path = expand_path(directory)
        if not directory_path.is_dir():
            error_ctx = (
                create_system_error(
                    f"Working directory not found: {directory_path}",
                    directory_path=str(directory_path),
                    app_name=self.app_name,
                )
                .with_component("ActionCommand")
                .with_operation("_change_directory")
                .with_suggestion("Check that the directory path exists")
                .with_suggestion("Verify directory permissions")
                .build()
            )
            raise PPError(error_ctx)
        os.chdir(directory_path)
        self.context.working_directory = str(directory_path)
        self.logger.debug("Changed directory to %s", directory_path)

    def _activate_venv(self, venv_path: str) -> Dict[str, str]:
        """Activate a virtual environment and return the updated environment."""
        working_dir = getattr(self.context, "working_directory", None)
        venv_path_obj = resolve_relative_path(venv_path, working_dir)
        if not (venv_path_obj / "bin" / "activate").exists():
            error_ctx = (
                create_system_error(
                    f"Virtual environment not found: {venv_path_obj}",
                    venv_path=str(venv_path_obj),
                    app_name=self.app_name,
                )
                .with_component("ActionCommand")
                .with_operation("_activate_venv")
                .with_suggestion("Check that the virtual environment path exists")
                .with_suggestion("Create virtual environment: python -m venv <path>")
                .with_suggestion("Verify the path is correct in your configuration")
                .build()
            )
            raise PPError(error_ctx)

        env = self.context.env.copy()
        env["VIRTUAL_ENV"] = str(venv_path_obj)
        env["PATH"] = f"{venv_path_obj}/bin:{env.get('PATH', '')}"
        self.context.virtual_env = str(venv_path_obj)
        self.logger.info("Activated virtual environment: %s", venv_path_obj)
        return env

    def _substitute_env_vars(self, env_vars: Dict[str, str]) -> Dict[str, str]:
        """Substitute environment variables in the config."""
        result = {}
        for key, value in env_vars.items():
            if (
                isinstance(value, str)
                and value.startswith("${")
                and value.endswith("}")
            ):
                env_key = value[2:-1]
                result[key] = os.environ.get(env_key, "")
                if not result[key]:
                    self.logger.warning("Environment variable %s not set", env_key)
            else:
                result[key] = value
        return result

    def _run_command(self, cmd: List[str]) -> subprocess.CompletedProcess:
        """Run the command with the configured environment."""
        try:
            cmd = [str(c) for c in cmd]
            self.logger.debug("Running command: %s", " ".join(cmd))
            return subprocess.run(cmd, check=True, shell=False, env=self.context.env)
        except subprocess.CalledProcessError as e:
            error_ctx = (
                create_execution_error(
                    f"Command failed with exit code {e.returncode}: {' '.join(cmd)}",
                    command=" ".join(cmd),
                    exit_code=e.returncode,
                    app_name=self.app_name,
                    action_name=self.action_name,
                )
                .with_component("ActionCommand")
                .with_operation("_run_command")
                .with_exception(e)
                .with_suggestion("Check command syntax and parameters")
                .with_suggestion("Verify all required dependencies are installed")
                .build()
            )
            raise PPError(error_ctx)
        except FileNotFoundError as e:
            error_ctx = (
                create_system_error(
                    f"Command not found: {cmd[0]}",
                    command=cmd[0],
                    full_command=" ".join(cmd),
                    app_name=self.app_name,
                    action_name=self.action_name,
                )
                .with_component("ActionCommand")
                .with_operation("_run_command")
                .with_exception(e)
                .with_suggestion(f"Install the required command: {cmd[0]}")
                .with_suggestion("Check that the command is in your PATH")
                .with_suggestion("Verify the command name is spelled correctly")
                .build()
            )
            raise PPError(error_ctx)

    @property
    def logger(self) -> logging.Logger:
        """Get logger instance."""
        return logging.getLogger("pp")
