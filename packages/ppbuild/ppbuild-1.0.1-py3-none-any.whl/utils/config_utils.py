import logging
import os
from pathlib import Path
from typing import Any, Dict

from .error_context import PPError, create_config_error
from .visitors import ConfigProcessor

logger = logging.getLogger("pp")


def get_config_paths():
    """Get configuration file paths."""
    config_name = os.getenv("PP_CONFIG_FILE", "pp.yaml")
    env_name = os.getenv("PP_ENV_FILE", ".pp.env")

    if base_dir := os.getenv("PP_BASE_DIR"):
        base_path = Path(base_dir)
        return base_path / config_name, base_path / env_name

    search_paths = [
        Path.cwd(),
        Path.home() / ".pp",
        Path.home(),
        Path(__file__).parent,
    ]

    # Find first existing config file
    for path in search_paths:
        config_file = path / config_name
        if config_file.exists():
            return config_file, path / env_name

    # Default to current directory if none found
    return Path.cwd() / config_name, Path.cwd() / env_name


def validate_and_process_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and process configuration using visitor pattern."""
    try:
        processor = ConfigProcessor(config)
        results = processor.process_all()
    except Exception as e:
        error_ctx = (
            create_config_error(
                "Failed to process configuration", processing_stage="initialization"
            )
            .with_component("ConfigProcessor")
            .with_exception(e)
            .build()
        )
        raise PPError(error_ctx)

    validator = results["validation"]

    if validator.has_errors():
        logger.error("Configuration validation failed:")
        logger.error(validator.get_error_summary())
        error_ctx = (
            create_config_error(
                "Configuration validation failed",
                error_count=len(validator.errors),
                errors=validator.errors[:3],
            )
            .with_component("ConfigValidator")
            .with_suggestions(
                [
                    "Check your pp.yaml syntax using a YAML validator",
                    "Ensure all required fields are present",
                    "Review the error details above",
                ]
            )
            .build()
        )
        raise PPError(error_ctx)

    if validator.warnings:
        logger.warning("Configuration warnings:")
        for warning in validator.warnings:
            logger.warning(f"  - {warning}")

    logger.debug("Configuration validation passed")
    return results
