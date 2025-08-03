"""Configuration elements that can be visited."""

from typing import Any, Dict


class ConfigElement:
    """Base class for configuration elements that can be visited."""

    def accept(self, visitor):
        """Accept a visitor and dispatch to appropriate visit method."""
        visitor.visit(self)


class ApplicationConfig(ConfigElement):
    """Configuration element representing an application."""

    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        self.actions = {
            action_name: ActionConfig(action_name, action_config)
            for action_name, action_config in config.get("actions", {}).items()
        }

    def accept(self, visitor):
        """Accept visitor and visit all actions."""
        visitor.visit_application(self)
        for action in self.actions.values():
            action.accept(visitor)


class ActionConfig(ConfigElement):
    """Configuration element representing an action."""

    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        self.parameters = {
            param_name: ParameterConfig(param_name, param_config)
            for param_name, param_config in config.get("parameters", {}).items()
        }

    def accept(self, visitor):
        """Accept visitor and visit all parameters."""
        visitor.visit_action(self)
        for parameter in self.parameters.values():
            parameter.accept(visitor)


class ParameterConfig(ConfigElement):
    """Configuration element representing a parameter."""

    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config

    def accept(self, visitor):
        """Accept visitor."""
        visitor.visit_parameter(self)
