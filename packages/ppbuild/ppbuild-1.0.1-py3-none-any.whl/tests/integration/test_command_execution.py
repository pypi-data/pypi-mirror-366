"""Integration tests for command execution scenarios."""

import os
import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from commands.app_command import AppCommand
from commands.base_command import CommandContext
from commands.command_invoker import CommandInvoker
from utils.error_context import PPError


class TestCommandExecution:
    """Test various command execution scenarios."""

    def test_simple_command_execution(self, test_config, mock_args):
        """Test execution of simple command without parameters."""
        args = mock_args(subcommand="simple_app", action="run")
        context = CommandContext(config=test_config, env=os.environ.copy(), args=args)

        with patch("subprocess.run") as mock_subprocess:
            mock_subprocess.return_value.returncode = 0

            app_command = AppCommand("simple_app", context)
            invoker = CommandInvoker()
            result = invoker.execute_command(app_command)

            assert result is True
            mock_subprocess.assert_called_once()
            call_args = mock_subprocess.call_args
            assert call_args[0][0] == ["echo", "simple app running"]

    def test_command_with_parameters(self, test_config, mock_args):
        """Test execution of command with parameters."""
        args = mock_args(
            subcommand="param_app",
            action="run",
            name="test_name",
            count=3,
            verbose=True,
            mode="prod",
        )
        context = CommandContext(config=test_config, env=os.environ.copy(), args=args)

        with patch("subprocess.run") as mock_subprocess:
            with patch("os.chdir"):
                with patch("pathlib.Path.exists", return_value=True):
                    with patch("pathlib.Path.is_dir", return_value=True):
                        mock_subprocess.return_value.returncode = 0

                        app_command = AppCommand("param_app", context)
                        invoker = CommandInvoker()
                        result = invoker.execute_command(app_command)

                        assert result is True
                        mock_subprocess.assert_called_once()
                        call_args = mock_subprocess.call_args[0][0]

                        # Check parameter substitution
                        assert "name=test_name" in call_args
                        assert "count=3" in call_args
                        assert "--verbose" in call_args
                        assert "mode=prod" in call_args

    def test_boolean_parameter_handling(self, test_config, mock_args):
        """Test boolean parameter handling in commands."""
        # Test with verbose=True
        args = mock_args(
            subcommand="param_app", action="run", name="test", verbose=True
        )
        context = CommandContext(config=test_config, env=os.environ.copy(), args=args)

        with patch("subprocess.run") as mock_subprocess:
            with patch("os.chdir"):
                with patch("pathlib.Path.exists", return_value=True):
                    with patch("pathlib.Path.is_dir", return_value=True):
                        mock_subprocess.return_value.returncode = 0

                        app_command = AppCommand("param_app", context)
                        invoker = CommandInvoker()
                        invoker.execute_command(app_command)

                        call_args = mock_subprocess.call_args[0][0]
                        assert "--verbose" in call_args

        # Test with verbose=False (should not include flag)
        args.verbose = False
        context = CommandContext(config=test_config, env=os.environ.copy(), args=args)

        with patch("subprocess.run") as mock_subprocess:
            with patch("os.chdir"):
                with patch("pathlib.Path.exists", return_value=True):
                    with patch("pathlib.Path.is_dir", return_value=True):
                        mock_subprocess.return_value.returncode = 0

                        app_command = AppCommand("param_app", context)
                        invoker = CommandInvoker()
                        invoker.execute_command(app_command)

                        call_args = mock_subprocess.call_args[0][0]
                        assert "--verbose" not in call_args

    def test_environment_setup(self, test_config, mock_args):
        """Test environment setup (directory, venv, env vars)."""
        args = mock_args(subcommand="param_app", action="run", name="test")
        context = CommandContext(config=test_config, env=os.environ.copy(), args=args)

        with patch("subprocess.run") as mock_subprocess:
            with patch("os.chdir") as mock_chdir:
                with patch("pathlib.Path.exists", return_value=True):
                    with patch("pathlib.Path.is_dir", return_value=True):
                        mock_subprocess.return_value.returncode = 0

                        app_command = AppCommand("param_app", context)
                        invoker = CommandInvoker()
                        invoker.execute_command(app_command)

                        # Check directory change (handle macOS /private/tmp symlink)
                        mock_chdir.assert_called_once()
                        called_path = str(mock_chdir.call_args[0][0])
                        assert called_path.endswith("/tmp/test")

                        # Check environment variables
                        call_env = mock_subprocess.call_args[1]["env"]
                        assert call_env["TEST_VAR"] == "test_value"
                        assert "VIRTUAL_ENV" in call_env
                        assert "/tmp/venv/bin" in call_env["PATH"]

    def test_command_validation_failure(self, test_config, mock_args):
        """Test command validation failure scenarios."""
        # Test with non-existent application
        args = mock_args(subcommand="nonexistent_app", action="run")
        context = CommandContext(config=test_config, env=os.environ.copy(), args=args)

        app_command = AppCommand("nonexistent_app", context)

        assert not app_command.validate()

    def test_action_validation_failure(self, test_config, mock_args):
        """Test action validation failure scenarios."""
        # Test with non-existent action
        args = mock_args(subcommand="simple_app", action="nonexistent_action")
        context = CommandContext(config=test_config, env=os.environ.copy(), args=args)

        app_command = AppCommand("simple_app", context)

        with pytest.raises(PPError):
            app_command.execute()

    def test_parameter_validation_errors(self, test_config, mock_args):
        """Test parameter validation error scenarios."""
        # Test missing required parameter
        args = mock_args(
            subcommand="param_app", action="run"
        )  # Missing required 'name'
        context = CommandContext(config=test_config, env=os.environ.copy(), args=args)

        app_command = AppCommand("param_app", context)

        with pytest.raises(PPError):
            app_command.execute()

    def test_subprocess_failure_handling(self, test_config, mock_args):
        """Test handling of subprocess execution failures."""
        args = mock_args(subcommand="simple_app", action="run")
        context = CommandContext(config=test_config, env=os.environ.copy(), args=args)

        with patch("subprocess.run") as mock_subprocess:
            # Simulate command failure
            mock_subprocess.side_effect = subprocess.CalledProcessError(1, ["echo"])

            app_command = AppCommand("simple_app", context)
            invoker = CommandInvoker()

            with pytest.raises(PPError):
                invoker.execute_command(app_command)

    def test_file_not_found_handling(self, test_config, mock_args):
        """Test handling of FileNotFoundError during command execution."""
        args = mock_args(subcommand="simple_app", action="run")
        context = CommandContext(config=test_config, env=os.environ.copy(), args=args)

        with patch("subprocess.run") as mock_subprocess:
            # Simulate command not found
            mock_subprocess.side_effect = FileNotFoundError("Command not found")

            app_command = AppCommand("simple_app", context)
            invoker = CommandInvoker()

            with pytest.raises(PPError):
                invoker.execute_command(app_command)
