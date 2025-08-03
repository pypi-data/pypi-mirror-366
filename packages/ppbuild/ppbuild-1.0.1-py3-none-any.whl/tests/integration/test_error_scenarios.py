"""Integration tests for error scenarios and edge cases."""

import os
import subprocess
from typing import Any, Dict
from unittest.mock import patch

import pytest

from commands.action_command import ActionCommand
from commands.app_command import AppCommand
from commands.base_command import CommandContext
from commands.command_invoker import CommandInvoker
from utils.error_context import PPError


class TestErrorScenarios:
    """Test various error scenarios and edge cases."""

    def test_invalid_application_name(self, test_config, mock_args):
        """Test handling of invalid application names."""
        args = mock_args(subcommand="nonexistent_app", action="run")
        context = CommandContext(config=test_config, env=os.environ.copy(), args=args)

        app_command = AppCommand("nonexistent_app", context)

        # Validation should fail
        assert not app_command.validate()

    def test_application_without_actions(self, mock_args):
        """Test handling of application without actions defined."""
        config = {
            "applications": {
                "no_actions_app": {
                    "help": "App without actions"
                    # Missing 'actions' key
                }
            }
        }

        args = mock_args(subcommand="no_actions_app", action="run")
        context = CommandContext(config=config, env=os.environ.copy(), args=args)

        app_command = AppCommand("no_actions_app", context)

        # Validation should fail
        assert not app_command.validate()

    def test_invalid_action_name(self, test_config, mock_args):
        """Test handling of invalid action names."""
        args = mock_args(subcommand="simple_app", action="nonexistent_action")
        context = CommandContext(config=test_config, env=os.environ.copy(), args=args)

        action_command = ActionCommand("simple_app", "nonexistent_action", context)

        # Validation should fail
        assert not action_command.validate()

    def test_action_without_command(self, mock_args):
        """Test handling of action without command defined."""
        config = {
            "applications": {
                "test_app": {
                    "actions": {
                        "no_command": {
                            "help": "Action without command"
                            # Missing 'command' key
                        }
                    }
                }
            }
        }

        args = mock_args(subcommand="test_app", action="no_command")
        context = CommandContext(config=config, env=os.environ.copy(), args=args)

        action_command = ActionCommand("test_app", "no_command", context)

        # Validation should fail
        assert not action_command.validate()

    def test_directory_not_found(self, mock_args):
        """Test handling of non-existent directory."""
        config = {
            "applications": {
                "test_app": {
                    "directory": "/nonexistent/directory",
                    "actions": {"run": {"command": ["echo", "test"]}},
                }
            }
        }

        args = mock_args(subcommand="test_app", action="run")
        context = CommandContext(config=config, env=os.environ.copy(), args=args)

        with patch("pathlib.Path.is_dir", return_value=False):
            action_command = ActionCommand("test_app", "run", context)

            with pytest.raises(PPError):
                action_command.execute()

    def test_virtual_environment_not_found(self, mock_args):
        """Test handling of non-existent virtual environment."""
        config = {
            "applications": {
                "test_app": {
                    "venv": "/nonexistent/venv",
                    "actions": {"run": {"command": ["echo", "test"]}},
                }
            }
        }

        args = mock_args(subcommand="test_app", action="run")
        context = CommandContext(config=config, env=os.environ.copy(), args=args)

        with patch("pathlib.Path.exists", return_value=False):
            action_command = ActionCommand("test_app", "run", context)

            with pytest.raises(PPError):
                action_command.execute()

    def test_subprocess_command_not_found(self, test_config, mock_args):
        """Test handling of subprocess FileNotFoundError."""
        args = mock_args(subcommand="simple_app", action="run")
        context = CommandContext(config=test_config, env=os.environ.copy(), args=args)

        with patch("subprocess.run") as mock_subprocess:
            mock_subprocess.side_effect = FileNotFoundError("Command not found")

            action_command = ActionCommand("simple_app", "run", context)

            with pytest.raises(PPError):
                action_command.execute()

    def test_subprocess_command_failure(self, test_config, mock_args):
        """Test handling of subprocess CalledProcessError."""
        args = mock_args(subcommand="simple_app", action="run")
        context = CommandContext(config=test_config, env=os.environ.copy(), args=args)

        with patch("subprocess.run") as mock_subprocess:
            mock_subprocess.side_effect = subprocess.CalledProcessError(1, ["echo"])

            action_command = ActionCommand("simple_app", "run", context)

            with pytest.raises(PPError):
                action_command.execute()

    def test_parameter_validation_required_missing(self, mock_args):
        """Test parameter validation with missing required parameter."""
        config = {
            "applications": {
                "test_app": {
                    "actions": {
                        "run": {
                            "parameters": {
                                "required_param": {"type": "string", "required": True}
                            },
                            "command": ["echo", "{required_param}"],
                        }
                    }
                }
            }
        }

        args = mock_args(subcommand="test_app", action="run", required_param=None)
        context = CommandContext(config=config, env=os.environ.copy(), args=args)

        action_command = ActionCommand("test_app", "run", context)

        with pytest.raises(PPError):
            action_command.execute()

    def test_parameter_validation_type_error(self, mock_args):
        """Test parameter validation with type conversion error."""
        config = {
            "applications": {
                "test_app": {
                    "actions": {
                        "run": {
                            "parameters": {
                                "number": {"type": "integer", "required": True}
                            },
                            "command": ["echo", "{number}"],
                        }
                    }
                }
            }
        }

        args = mock_args(subcommand="test_app", action="run", number="not_a_number")
        context = CommandContext(config=config, env=os.environ.copy(), args=args)

        action_command = ActionCommand("test_app", "run", context)

        with pytest.raises(PPError):
            action_command.execute()

    def test_parameter_validation_bounds_error(self, mock_args):
        """Test parameter validation with bounds checking error."""
        config = {
            "applications": {
                "test_app": {
                    "actions": {
                        "run": {
                            "parameters": {
                                "bounded_int": {
                                    "type": "integer",
                                    "min": 1,
                                    "max": 10,
                                    "required": True,
                                }
                            },
                            "command": ["echo", "{bounded_int}"],
                        }
                    }
                }
            }
        }

        args = mock_args(
            subcommand="test_app", action="run", bounded_int=15
        )  # Above max
        context = CommandContext(config=config, env=os.environ.copy(), args=args)

        action_command = ActionCommand("test_app", "run", context)

        with pytest.raises(PPError):
            action_command.execute()

    def test_command_invoker_validation_failure(self, test_config, mock_args):
        """Test CommandInvoker handling of validation failures."""
        args = mock_args(subcommand="nonexistent_app", action="run")
        context = CommandContext(config=test_config, env=os.environ.copy(), args=args)

        app_command = AppCommand("nonexistent_app", context)
        invoker = CommandInvoker()

        with pytest.raises(PPError):
            invoker.execute_command(app_command)

    def test_empty_configuration(self, mock_args):
        """Test handling of empty configuration."""
        config: Dict[str, Any] = {"applications": {}}

        args = mock_args(subcommand="any_app", action="run")
        context = CommandContext(config=config, env=os.environ.copy(), args=args)

        app_command = AppCommand("any_app", context)

        assert not app_command.validate()


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_command_list(self, mock_args):
        """Test handling of empty command list."""
        config: Dict[str, Any] = {
            "applications": {
                "test_app": {"actions": {"run": {"command": []}}}  # Empty command
            }
        }

        args = mock_args(subcommand="test_app", action="run")
        context = CommandContext(config=config, env=os.environ.copy(), args=args)

        # Empty command should fail validation
        action_command = ActionCommand("test_app", "run", context)

        # This should exit because empty command is invalid
        with pytest.raises(PPError):
            action_command.execute()

    def test_parameter_with_special_characters(self, mock_args):
        """Test parameter values with special characters."""
        config = {
            "applications": {
                "test_app": {
                    "actions": {
                        "run": {
                            "parameters": {
                                "message": {
                                    "type": "string",
                                    "default": "hello world & special chars!",
                                }
                            },
                            "command": ["echo", "{message}"],
                        }
                    }
                }
            }
        }

        args = mock_args(
            subcommand="test_app", action="run", message="test & more $ chars"
        )
        context = CommandContext(config=config, env=os.environ.copy(), args=args)

        with patch("subprocess.run") as mock_subprocess:
            mock_subprocess.return_value.returncode = 0

            action_command = ActionCommand("test_app", "run", context)
            action_command.execute()

            call_args = mock_subprocess.call_args[0][0]
            assert "test & more $ chars" in call_args

    def test_zero_and_negative_numeric_parameters(self, mock_args):
        """Test zero and negative numeric parameter values."""
        config = {
            "applications": {
                "test_app": {
                    "actions": {
                        "run": {
                            "parameters": {
                                "zero_int": {"type": "integer", "default": 0},
                                "negative_int": {"type": "integer", "default": -1},
                                "zero_float": {"type": "float", "default": 0.0},
                            },
                            "command": [
                                "echo",
                                "zero={zero_int}",
                                "neg={negative_int}",
                                "float={zero_float}",
                            ],
                        }
                    }
                }
            }
        }

        args = mock_args(subcommand="test_app", action="run")
        context = CommandContext(config=config, env=os.environ.copy(), args=args)

        with patch("subprocess.run") as mock_subprocess:
            mock_subprocess.return_value.returncode = 0

            action_command = ActionCommand("test_app", "run", context)
            action_command.execute()

            call_args = mock_subprocess.call_args[0][0]
            assert "zero=0" in call_args
            assert "neg=-1" in call_args
            assert "float=0.0" in call_args
