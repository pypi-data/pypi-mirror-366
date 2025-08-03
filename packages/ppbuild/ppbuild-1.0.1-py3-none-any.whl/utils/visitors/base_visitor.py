"""Base visitor interface for configuration processing."""

from abc import ABC, abstractmethod


class ConfigVisitor(ABC):
    """Abstract base class for configuration visitors."""

    def visit(self, element):
        """Generic visit method - delegates to specific visit methods."""
        pass

    @abstractmethod
    def visit_application(self, app):
        """Visit an application configuration."""
        pass

    @abstractmethod
    def visit_action(self, action):
        """Visit an action configuration."""
        pass

    @abstractmethod
    def visit_parameter(self, parameter):
        """Visit a parameter configuration."""
        pass
