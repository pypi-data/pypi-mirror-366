"""Core command builder implementation."""

import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

from commands.action_command import ActionCommand
from commands.app_command import AppCommand
from commands.base_command import CommandContext
from utils.parameter_utils import parse_action_parameters
from utils.path_utils import expand_path, resolve_relative_path

from ..error_context import (PPError, create_execution_error,
                             create_validation_error)

logger = logging.getLogger("pp")


class CommandBuilder:
    """Builder for constructing commands with complex setup."""

    def __init__(self):
        self.reset()

    def reset(self):
        """Reset the builder to initial state."""
        self._config: Optional[Dict[str, Any]] = None
        self._args: Optional[Any] = None
        self._base_env: Dict[str, str] = os.environ.copy()
        self._app_name: Optional[str] = None
        self._action_name: Optional[str] = None
        self._working_directory: Optional[Path] = None
        self._virtual_env: Optional[Path] = None
        self._env_vars: Dict[str, str] = {}
        self._parameters: Dict[str, Any] = {}
        self._context: Optional[CommandContext] = None
        return self

    def with_config(self, config: Dict[str, Any]):
        """Set the configuration."""
        self._config = config
        return self

    def with_args(self, args: Any):
        """Set the command line arguments."""
        self._args = args
        return self

    def with_app_name(self, app_name: str):
        """Set the application name."""
        self._app_name = app_name
        return self

    def with_action_name(self, action_name: str):
        """Set the action name."""
        self._action_name = action_name
        return self

    def with_working_directory(self, directory: str):
        """Set the working directory."""
        self._working_directory = expand_path(directory)
        return self

    def with_virtual_env(self, venv_path: str):
        """Set the virtual environment path."""
        self._virtual_env = expand_path(venv_path)
        return self

    def with_env_vars(self, env_vars: Dict[str, str]):
        """Set environment variables."""
        self._env_vars.update(env_vars)
        return self

    def with_env_var(self, key: str, value: str):
        """Set a single environment variable."""
        self._env_vars[key] = value
        return self

    def with_parameters(self, parameters: Dict[str, Any]):
        """Set command parameters."""
        self._parameters.update(parameters)
        return self

    def with_parameter(self, key: str, value: Any):
        """Set a single parameter."""
        self._parameters[key] = value
        return self

    def build_context(self) -> CommandContext:
        """Build the command context with all configured settings."""
        if not self._config:
            error_ctx = (
                create_validation_error(
                    "Configuration is required to build command context",
                    missing_component="configuration",
                )
                .with_component("CommandContextBuilder")
                .build()
            )
            raise PPError(error_ctx)
        if not self._args:
            error_ctx = (
                create_validation_error(
                    "Arguments are required to build command context",
                    missing_component="args",
                )
                .with_component("CommandContextBuilder")
                .build()
            )
            raise PPError(error_ctx)

        # Start with base environment
        env = self._base_env.copy()

        # Add configured environment variables with substitution
        for key, value in self._env_vars.items():
            if value.startswith("${") and value.endswith("}"):
                # Environment variable substitution
                env_key = value[2:-1]
                env[key] = os.environ.get(env_key, "")
                if not env[key]:
                    logger.warning("Environment variable %s not set", env_key)
            else:
                env[key] = value

        # Set up virtual environment in PATH if specified
        if self._virtual_env:
            venv_bin = self._virtual_env / "bin"
            if venv_bin.exists():
                current_path = env.get("PATH", "")
                env["PATH"] = f"{venv_bin}:{current_path}"
                env["VIRTUAL_ENV"] = str(self._virtual_env)
                logger.debug("Activated virtual environment: %s", self._virtual_env)

        # Create context
        context = CommandContext(config=self._config, env=env, args=self._args)

        # Set additional context properties
        if self._working_directory:
            context.working_directory = str(self._working_directory)
        if self._virtual_env:
            context.virtual_env = str(self._virtual_env)
        if self._parameters:
            context.parameters = self._parameters

        self._context = context
        return context

    def build_app_command(self) -> AppCommand:
        """Build an application command."""
        if not self._app_name:
            error_ctx = (
                create_validation_error(
                    "Application name is required to build command",
                    missing_component="app_name",
                )
                .with_component("CommandBuilder")
                .with_operation("build_app_command")
                .build()
            )
            raise PPError(error_ctx)

        if not self._context:
            self.build_context()

        if not self._context:
            error_ctx = (
                create_execution_error(
                    "Failed to build command context",
                    builder_state="context_creation_failed",
                )
                .with_component("CommandBuilder")
                .with_operation("build_app_command")
                .build()
            )
            raise PPError(error_ctx)

        return AppCommand(self._app_name, self._context)

    def build_action_command(self) -> ActionCommand:
        """Build an action command."""
        if not self._app_name:
            error_ctx = (
                create_validation_error(
                    "Application name is required to build action command",
                    missing_component="app_name",
                )
                .with_component("CommandBuilder")
                .with_operation("build_action_command")
                .build()
            )
            raise PPError(error_ctx)

        if not self._action_name:
            error_ctx = (
                create_validation_error(
                    "Action name is required to build action command",
                    missing_component="action_name",
                )
                .with_component("CommandBuilder")
                .with_operation("build_action_command")
                .build()
            )
            raise PPError(error_ctx)

        if not self._context:
            self.build_context()

        if not self._context:
            error_ctx = (
                create_execution_error(
                    "Failed to build command context",
                    builder_state="context_creation_failed",
                )
                .with_component("CommandBuilder")
                .with_operation("build_action_command")
                .build()
            )
            raise PPError(error_ctx)

        return ActionCommand(self._app_name, self._action_name, self._context)

    def auto_configure_from_app_config(self) -> "CommandBuilder":
        """Auto-configure builder from application configuration."""
        if not self._config or not self._app_name:
            error_ctx = (
                create_validation_error(
                    "Configuration and app name required for auto-configuration",
                    has_config=bool(self._config),
                    has_app_name=bool(self._app_name),
                )
                .with_component("CommandBuilder")
                .with_operation("auto_configure_from_app_config")
                .build()
            )
            raise PPError(error_ctx)

        app_config = self._config["applications"].get(self._app_name, {})

        # Set working directory if specified
        if directory := app_config.get("directory"):
            self.with_working_directory(directory)

        # Set virtual environment if specified
        if venv := app_config.get("venv"):
            venv_path = resolve_relative_path(venv, self._working_directory)
            self._virtual_env = venv_path

        # Set environment variables if specified
        if env_vars := app_config.get("env_vars"):
            self.with_env_vars(env_vars)

        return self

    def auto_configure_parameters(self) -> "CommandBuilder":
        """Auto-configure parameters from action configuration."""
        if not self._config or not self._app_name or not self._action_name:
            error_ctx = (
                create_validation_error(
                    "Configuration, app name, and action name required for "
                    "parameter auto-configuration",
                    has_config=bool(self._config),
                    has_app_name=bool(self._app_name),
                    has_action_name=bool(self._action_name),
                )
                .with_component("CommandBuilder")
                .with_operation("auto_configure_parameters")
                .build()
            )
            raise PPError(error_ctx)

        app_config = self._config["applications"][self._app_name]

        # Check if action exists before trying to access it
        if self._action_name not in app_config.get("actions", {}):
            logger.warning(
                "Action '%s' not found in app '%s'", self._action_name, self._app_name
            )
            return self

        action_config = app_config["actions"][self._action_name]

        # Parse parameters from args
        if action_config.get("parameters") and self._args:
            try:
                parameters = parse_action_parameters(action_config, self._args)
                self.with_parameters(parameters)
                logger.debug("Auto-configured parameters: %s", parameters)
            except Exception as e:
                logger.error("Failed to parse parameters: %s", e)
                raise

        return self
