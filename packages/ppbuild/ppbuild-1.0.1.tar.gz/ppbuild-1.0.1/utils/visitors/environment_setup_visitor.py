"""Environment setup visitor."""

from typing import Any, Dict

from .base_visitor import ConfigVisitor


class EnvironmentSetupVisitor(ConfigVisitor):
    """Visitor that processes environment setup configuration."""

    def __init__(self):
        self.environment_configs: Dict[str, Dict[str, Any]] = {}

    def visit_application(self, app):
        """Extract environment setup for application."""
        env_config = {}

        if directory := app.config.get("directory"):
            env_config["directory"] = directory

        if venv := app.config.get("venv"):
            env_config["venv"] = venv

        if env_vars := app.config.get("env_vars"):
            env_config["env_vars"] = env_vars

        if env_config:
            self.environment_configs[app.name] = env_config

    def visit_action(self, action):
        """Actions don't have environment setup."""
        pass

    def visit_parameter(self, parameter):
        """Parameters don't have environment setup."""
        pass

    def get_environment_config(self, app_name: str) -> Dict[str, Any]:
        """Get environment configuration for an application."""
        return self.environment_configs.get(app_name, {})
