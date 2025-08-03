"""Integration tests for pp.py - Main CLI functionality."""

import os
from unittest.mock import MagicMock, patch

import pytest
import yaml

import pp
from commands.app_command import AppCommand
from commands.base_command import CommandContext
from commands.command_invoker import CommandInvoker
from utils.error_context import PPError


class TestPPIntegration:
    """Integration tests for the main pp functionality."""

    def test_load_config_success(self, test_config_file):
        """Test successful configuration loading."""
        config = pp.load_config(test_config_file)

        assert "applications" in config
        assert "simple_app" in config["applications"]
        assert config["applications"]["simple_app"]["help"] == "Simple test application"

    def test_load_config_file_not_found(self, temp_dir):
        """Test configuration loading with non-existent file."""
        non_existent_file = temp_dir / "non_existent.yaml"

        with pytest.raises(PPError):
            pp.load_config(non_existent_file)

    def test_load_config_invalid_yaml(self, temp_dir):
        """Test configuration loading with invalid YAML."""
        invalid_yaml_file = temp_dir / "invalid.yaml"
        with open(invalid_yaml_file, "w") as f:
            f.write("invalid: yaml: content: [")

        with pytest.raises(PPError):
            pp.load_config(invalid_yaml_file)

    def test_load_env_file_exists(self, test_env_file):
        """Test environment loading when file exists."""
        with patch.dict(os.environ, {}, clear=True):
            pp.load_env(test_env_file)

            assert os.environ.get("TEST_ENV_VAR") == "from_env_file"
            assert (
                os.environ.get("DATABASE_URL")
                == "postgresql://test:test@localhost/testdb"
            )

    def test_load_env_file_not_exists(self, temp_dir):
        """Test environment loading when file doesn't exist."""
        non_existent_env = temp_dir / ".non_existent.env"

        # Should not raise an exception
        pp.load_env(non_existent_env)

    @patch("pp.load_config")
    @patch("pp.load_env")
    @patch("pp.create_app_parser")
    @patch("argparse.ArgumentParser.parse_args")
    def test_main_no_subcommand(
        self, mock_parse_args, mock_create_parser, mock_load_env, mock_load_config
    ):
        """Test main function when no subcommand is provided."""
        # Provide valid configuration that passes validation
        valid_config = {
            "applications": {
                "test_app": {
                    "help": "Test application",
                    "actions": {
                        "run": {"help": "Run test", "command": ["echo", "test"]}
                    },
                }
            }
        }
        mock_load_config.return_value = valid_config
        mock_args = MagicMock()
        mock_args.subcommand = None
        mock_parse_args.return_value = mock_args

        with patch("argparse.ArgumentParser.print_help") as mock_help:
            with pytest.raises(SystemExit) as exc_info:
                pp.main()

            assert exc_info.value.code == 1
            mock_help.assert_called_once()

    @patch("subprocess.run")
    @patch("os.chdir")
    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.is_dir")
    def test_main_successful_execution(
        self,
        mock_is_dir,
        mock_exists,
        mock_chdir,
        mock_subprocess,
        test_config_file,
        test_env_file,
    ):
        """Test successful main execution with valid configuration."""
        # Setup mocks
        mock_exists.return_value = True
        mock_is_dir.return_value = True
        mock_subprocess.return_value.returncode = 0

        with open(test_config_file, "r", encoding="utf-8") as f:
            test_config = yaml.safe_load(f)

        with patch("pp.load_config", return_value=test_config):
            with patch("sys.argv", ["pp.py", "simple_app"]):
                try:
                    pp.main()
                except SystemExit as e:
                    # Should exit with code 0 on success
                    if e.code != 0:
                        pytest.fail(
                            f"Expected successful execution, got exit code {e.code}"
                        )

    def test_command_context_creation(self, test_config, mock_args):
        """Test CommandContext creation with proper initialization."""
        args = mock_args(subcommand="test_app", action="run", name="test")

        context = CommandContext(config=test_config, env=os.environ.copy(), args=args)

        assert context.config == test_config
        assert isinstance(context.env, dict)
        assert context.args == args
        assert context.working_directory is None
        assert context.virtual_env is None
        assert context.parameters == {}

    @patch("subprocess.run")
    def test_app_command_execution(self, mock_subprocess, test_config, mock_args):
        """Test AppCommand execution flow."""
        mock_subprocess.return_value.returncode = 0
        args = mock_args(subcommand="simple_app", action="run")

        context = CommandContext(config=test_config, env=os.environ.copy(), args=args)

        app_command = AppCommand("simple_app", context)
        invoker = CommandInvoker()

        result = invoker.execute_command(app_command)

        assert result is True
        assert app_command.executed
        mock_subprocess.assert_called_once()

    def test_command_invoker_history(self, test_config, mock_args):
        """Test CommandInvoker maintains command history."""
        args = mock_args(subcommand="simple_app", action="run")
        context = CommandContext(config=test_config, env=os.environ.copy(), args=args)

        app_command = AppCommand("simple_app", context)
        invoker = CommandInvoker()

        with patch("subprocess.run") as mock_subprocess:
            mock_subprocess.return_value.returncode = 0
            invoker.execute_command(app_command)

        history = invoker.get_command_history()
        assert len(history) == 1
        assert history[0] == app_command

        invoker.clear_history()
        assert len(invoker.get_command_history()) == 0
