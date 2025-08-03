#!/usr/bin/env python3
"""pp: System manager for tools and environments"""

import argparse
import logging
import os
import sys
from pathlib import Path
from typing import Dict

import yaml
from dotenv import load_dotenv

from commands.command_invoker import CommandInvoker
from utils.builders import build_app_command
from utils.config_utils import get_config_paths, validate_and_process_config
from utils.error_context import (PPError, create_config_error,
                                 create_system_error)
from utils.parser_utils import create_parser_for_app
from utils.path_utils import expand_path

CONFIG_FILE_PATH, ENV_FILE_PATH = get_config_paths()

LOG_LEVEL = os.getenv("PP_LOG_LEVEL", "INFO").upper()

# Setup logging
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)],
)
logger = logging.getLogger("pp")


def load_config(config_path: Path = CONFIG_FILE_PATH) -> dict:
    """Load YAML configuration."""
    try:
        config_path = expand_path(config_path)
        if not config_path.exists():
            error_ctx = (
                create_config_error(
                    f"Configuration file {config_path} not found",
                    config_path=str(config_path),
                )
                # TODO: Implement init
                .with_suggestions(
                    [
                        f"Create configuration file at {config_path}",
                        "Use pp --init to create a sample configuration",
                        "Check PP_CONFIG_FILE environment variable",
                    ]
                ).build()
            )
            raise PPError(error_ctx)

        with config_path.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {"applications": {}}
    except (OSError, yaml.YAMLError) as e:
        error_ctx = (
            create_config_error(
                f"Failed to load config file {config_path}",
                config_path=str(config_path),
                error_type=type(e).__name__,
            )
            .with_exception(e)
            .build()
        )
        raise PPError(error_ctx)


def load_env(env_path: Path = ENV_FILE_PATH) -> None:
    """Load environment variables from .env file."""
    env_path = expand_path(env_path)
    if env_path.exists():
        load_dotenv(env_path)
        logger.debug("Loaded environment variables from %s", env_path)
    else:
        logger.debug("No .env file found at %s", env_path)


def create_app_parser(
    app_name: str, app_config: Dict, subparsers
) -> argparse.ArgumentParser:
    """Create argument parser for an application."""
    return create_parser_for_app(app_name, app_config, subparsers)


def main():
    """Main CLI entry point using Command pattern."""
    load_env()
    config = load_config()

    # Validate configuration using visitor pattern
    try:
        validate_and_process_config(config)
        logger.debug("Configuration processed successfully")
    except ValueError as e:
        error_ctx = (
            create_config_error(
                "Configuration validation failed", validation_error=str(e)
            )
            .with_component("ConfigValidator")
            .with_exception(e)
            .build()
        )
        logger.error(error_ctx.format_user_message())
        sys.exit(1)

    parser = argparse.ArgumentParser(
        description="pp: System manager for tools and environments",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="subcommand", help="Applications")

    # Create parsers for each application
    for app_name, app_config in config["applications"].items():
        create_app_parser(app_name, app_config, subparsers)

    args = parser.parse_args()

    if not args.subcommand:
        parser.print_help()
        sys.exit(1)

    # Create and execute application command using builder pattern
    app_command = build_app_command(args.subcommand, config, args)
    invoker = CommandInvoker()

    try:
        invoker.execute_command(app_command)
        logger.info("Completed %s", args.subcommand)
    except Exception as e:
        error_ctx = (
            create_system_error(
                f"Failed to execute {args.subcommand}",
                application=args.subcommand,
                action=getattr(args, "action", None),
            )
            .with_component("CommandInvoker")
            .with_exception(e)
            .build()
        )
        logger.error(error_ctx.format_user_message())
        sys.exit(1)


if __name__ == "__main__":
    main()
