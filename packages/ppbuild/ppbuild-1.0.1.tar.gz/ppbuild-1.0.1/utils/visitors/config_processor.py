"""Main configuration processor that orchestrates visitors."""

from typing import Any, Dict

from .config_elements import ApplicationConfig
from .environment_setup_visitor import EnvironmentSetupVisitor
from .parameter_extraction_visitor import ParameterExtractionVisitor
from .validation_visitor import ValidationVisitor


class ConfigProcessor:
    """Main processor that orchestrates configuration visitors."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.applications = {
            app_name: ApplicationConfig(app_name, app_config)
            for app_name, app_config in config.get("applications", {}).items()
        }

    def validate_configuration(self) -> ValidationVisitor:
        """Validate the configuration using ValidationVisitor."""
        validator = ValidationVisitor()

        for app in self.applications.values():
            app.accept(validator)

        return validator

    def extract_parameters(self) -> ParameterExtractionVisitor:
        """Extract parameter information using ParameterExtractionVisitor."""
        extractor = ParameterExtractionVisitor()

        for app in self.applications.values():
            app.accept(extractor)

        return extractor

    def extract_environment_setup(self) -> EnvironmentSetupVisitor:
        """Extract environment setup using EnvironmentSetupVisitor."""
        setup_visitor = EnvironmentSetupVisitor()

        for app in self.applications.values():
            app.accept(setup_visitor)

        return setup_visitor

    def process_all(self) -> Dict[str, Any]:
        """Process configuration with all visitors and return results."""
        validator = self.validate_configuration()
        parameter_extractor = self.extract_parameters()
        environment_extractor = self.extract_environment_setup()

        return {
            "validation": validator,
            "parameters": parameter_extractor,
            "environment": environment_extractor,
            "valid": not validator.has_errors(),
        }
