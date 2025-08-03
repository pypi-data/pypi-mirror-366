"""Parameter extraction visitor."""

from typing import Any, Dict

from .base_visitor import ConfigVisitor


class ParameterExtractionVisitor(ConfigVisitor):
    """Visitor that extracts parameter information for help generation."""

    def __init__(self):
        self.app_parameters: Dict[str, Dict[str, Dict[str, Any]]] = {}
        self.current_app: str = ""
        self.current_action: str = ""

    def visit_application(self, app):
        """Set current application context."""
        self.current_app = app.name
        if app.name not in self.app_parameters:
            self.app_parameters[app.name] = {}

    def visit_action(self, action):
        """Set current action context."""
        self.current_action = action.name
        if action.name not in self.app_parameters[self.current_app]:
            self.app_parameters[self.current_app][action.name] = {}

    def visit_parameter(self, parameter):
        """Extract parameter information."""
        self.app_parameters[self.current_app][self.current_action][parameter.name] = {
            "type": parameter.config.get("type", "string"),
            "required": parameter.config.get("required", False),
            "default": parameter.config.get("default"),
            "help": parameter.config.get("help", ""),
            "choices": parameter.config.get("choices"),
            "min": parameter.config.get("min"),
            "max": parameter.config.get("max"),
        }

    def get_parameters_for_action(
        self, app_name: str, action_name: str
    ) -> Dict[str, Dict[str, Any]]:
        """Get parameters for a specific application action."""
        return self.app_parameters.get(app_name, {}).get(action_name, {})
