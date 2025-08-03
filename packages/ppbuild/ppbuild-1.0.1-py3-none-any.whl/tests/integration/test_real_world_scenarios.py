"""Integration tests for real-world usage scenarios."""

import os
from unittest.mock import patch

from commands.app_command import AppCommand
from commands.base_command import CommandContext
from commands.command_invoker import CommandInvoker


class TestRealWorldScenarios:
    """Test realistic usage scenarios based on the test configuration."""

    def test_minimal_app_execution(self, mock_args):
        """Test execution of minimal application."""
        config = {
            "applications": {
                "minimal": {
                    "help": "Minimal test application",
                    "default_action": "run",
                    "actions": {
                        "run": {
                            "help": "Run minimal app",
                            "command": ["echo", "minimal app executed"],
                        }
                    },
                }
            }
        }

        args = mock_args(subcommand="minimal", action="run")
        context = CommandContext(config=config, env=os.environ.copy(), args=args)

        with patch("subprocess.run") as mock_subprocess:
            mock_subprocess.return_value.returncode = 0

            app_command = AppCommand("minimal", context)
            invoker = CommandInvoker()
            result = invoker.execute_command(app_command)

            assert result is True
            mock_subprocess.assert_called_once()
            call_args = mock_subprocess.call_args[0][0]
            assert call_args == ["echo", "minimal app executed"]

    def test_web_app_development_workflow(self, mock_args):
        """Test realistic web application development workflow."""
        config = {
            "applications": {
                "web_app": {
                    "help": "Realistic web application simulation",
                    "directory": "/tmp/webapp",
                    "venv": "/tmp/webapp/.venv",
                    "env_vars": {
                        "FLASK_ENV": "development",
                        "DATABASE_URL": "${TEST_DATABASE_URL}",
                        "SECRET_KEY": "${SECRET_KEY}",
                    },
                    "default_action": "run",
                    "actions": {
                        "run": {
                            "help": "Start the web application",
                            "parameters": {
                                "port": {
                                    "type": "integer",
                                    "default": 5000,
                                    "min": 1024,
                                    "max": 65535,
                                    "help": "Port to run on",
                                },
                                "debug": {
                                    "type": "boolean",
                                    "default": False,
                                    "help": "Enable debug mode",
                                },
                                "host": {
                                    "type": "string",
                                    "default": "127.0.0.1",
                                    "help": "Host to bind to",
                                },
                            },
                            "command": [
                                "flask",
                                "run",
                                "--host",
                                "{host}",
                                "--port",
                                "{port}",
                                "{debug:--debug}",
                            ],
                        },
                        "test": {
                            "help": "Run application tests",
                            "parameters": {
                                "coverage": {
                                    "type": "boolean",
                                    "default": True,
                                    "help": "Generate coverage report",
                                },
                                "verbose": {
                                    "type": "boolean",
                                    "default": False,
                                    "help": "Verbose test output",
                                },
                            },
                            "command": [
                                "python",
                                "-m",
                                "pytest",
                                "{coverage:--cov=src}",
                                "{verbose:-v}",
                            ],
                        },
                    },
                }
            }
        }

        # Test running the web app
        args = mock_args(
            subcommand="web_app", action="run", port=8080, debug=True, host="0.0.0.0"
        )
        context = CommandContext(config=config, env=os.environ.copy(), args=args)

        with patch("subprocess.run") as mock_subprocess:
            with patch("os.chdir"):
                with patch("pathlib.Path.exists", return_value=True):
                    with patch("pathlib.Path.is_dir", return_value=True):
                        mock_subprocess.return_value.returncode = 0

                        app_command = AppCommand("web_app", context)
                        invoker = CommandInvoker()
                        result = invoker.execute_command(app_command)

                        assert result is True
                        call_args = mock_subprocess.call_args[0][0]
                        assert "flask" in call_args
                        assert "--host" in call_args
                        assert "0.0.0.0" in call_args
                        assert "--port" in call_args
                        assert "8080" in call_args
                        assert "--debug" in call_args

        # Test running tests with coverage
        args = mock_args(
            subcommand="web_app", action="test", coverage=True, verbose=True
        )
        context = CommandContext(config=config, env=os.environ.copy(), args=args)

        with patch("subprocess.run") as mock_subprocess:
            with patch("os.chdir"):
                with patch("pathlib.Path.exists", return_value=True):
                    with patch("pathlib.Path.is_dir", return_value=True):
                        mock_subprocess.return_value.returncode = 0

                        app_command = AppCommand("web_app", context)
                        invoker = CommandInvoker()
                        result = invoker.execute_command(app_command)

                        assert result is True
                        call_args = mock_subprocess.call_args[0][0]
                        assert "pytest" in call_args
                        assert "--cov=src" in call_args
                        assert "-v" in call_args

    def test_parameter_comprehensive_validation(self, mock_args):
        """Test comprehensive parameter validation scenario."""
        config = {
            "applications": {
                "param_test": {
                    "help": "Parameter validation testing",
                    "default_action": "validate",
                    "actions": {
                        "validate": {
                            "help": "Test all parameter types",
                            "parameters": {
                                "required_string": {
                                    "type": "string",
                                    "required": True,
                                    "help": "Required string parameter",
                                },
                                "choice_string": {
                                    "type": "string",
                                    "choices": ["option1", "option2", "option3"],
                                    "default": "option1",
                                    "help": "String with choices",
                                },
                                "bounded_int": {
                                    "type": "integer",
                                    "default": 5,
                                    "min": 1,
                                    "max": 10,
                                    "help": "Integer with bounds",
                                },
                                "float_param": {
                                    "type": "float",
                                    "default": 3.14,
                                    "min": 0.0,
                                    "max": 10.0,
                                    "help": "Float with bounds",
                                },
                                "flag_true": {
                                    "type": "boolean",
                                    "default": True,
                                    "help": "Boolean defaulting to true",
                                },
                            },
                            "command": [
                                "echo",
                                "required_string={required_string}",
                                "choice_string={choice_string}",
                                "bounded_int={bounded_int}",
                                "float_param={float_param}",
                                "{flag_true:--flag-true}",
                            ],
                        }
                    },
                }
            }
        }

        args = mock_args(
            subcommand="param_test",
            action="validate",
            required_string="test_value",
            choice_string="option2",
            bounded_int=7,
            float_param=2.5,
            flag_true=True,
        )
        context = CommandContext(config=config, env=os.environ.copy(), args=args)

        with patch("subprocess.run") as mock_subprocess:
            mock_subprocess.return_value.returncode = 0

            app_command = AppCommand("param_test", context)
            invoker = CommandInvoker()
            result = invoker.execute_command(app_command)

            assert result is True
            call_args = mock_subprocess.call_args[0][0]
            assert "required_string=test_value" in call_args
            assert "choice_string=option2" in call_args
            assert "bounded_int=7" in call_args
            assert "float_param=2.5" in call_args
            assert "--flag-true" in call_args

    def test_environment_variable_substitution(self, mock_args):
        """Test environment variable substitution in real scenario."""
        config = {
            "applications": {
                "env_test": {
                    "help": "Environment setup testing",
                    "directory": "/tmp/test_directory",
                    "venv": "/tmp/test_venv",
                    "env_vars": {
                        "STATIC_VAR": "static_value",
                        "DYNAMIC_VAR": "${TEST_DYNAMIC_VAR}",
                        "EMPTY_VAR": "${NONEXISTENT_VAR}",
                    },
                    "default_action": "run",
                    "actions": {
                        "run": {"help": "Test environment setup", "command": ["env"]}
                    },
                }
            }
        }

        # Set up environment variable for substitution
        with patch.dict(os.environ, {"TEST_DYNAMIC_VAR": "dynamic_value"}):
            args = mock_args(subcommand="env_test", action="run")
            context = CommandContext(config=config, env=os.environ.copy(), args=args)

            with patch("subprocess.run") as mock_subprocess:
                with patch("os.chdir"):
                    with patch("pathlib.Path.exists", return_value=True):
                        with patch("pathlib.Path.is_dir", return_value=True):
                            mock_subprocess.return_value.returncode = 0

                            app_command = AppCommand("env_test", context)
                            invoker = CommandInvoker()
                            result = invoker.execute_command(app_command)

                            assert result is True

                            # Check environment variables were set correctly
                            call_env = mock_subprocess.call_args[1]["env"]
                            assert call_env["STATIC_VAR"] == "static_value"
                            assert call_env["DYNAMIC_VAR"] == "dynamic_value"
                            assert (
                                call_env["EMPTY_VAR"] == ""
                            )  # Should be empty for non-existent var

    def test_multi_action_application_workflow(self, mock_args):
        """Test multi-action application with different parameter sets."""
        config = {
            "applications": {
                "multi_action": {
                    "help": "Multi-action application for testing",
                    "default_action": "default",
                    "actions": {
                        "default": {
                            "help": "Default action",
                            "command": ["echo", "default action"],
                        },
                        "action_with_params": {
                            "help": "Action with parameters",
                            "parameters": {
                                "name": {
                                    "type": "string",
                                    "required": True,
                                    "help": "Name parameter",
                                },
                                "count": {
                                    "type": "integer",
                                    "default": 1,
                                    "help": "Count parameter",
                                },
                            },
                            "command": ["echo", "name={name}", "count={count}"],
                        },
                        "action_bool_flags": {
                            "help": "Action with boolean flags",
                            "parameters": {
                                "verbose": {
                                    "type": "boolean",
                                    "default": False,
                                    "help": "Verbose output",
                                },
                                "debug": {
                                    "type": "boolean",
                                    "default": True,
                                    "help": "Debug mode",
                                },
                            },
                            "command": [
                                "echo",
                                "{verbose:--verbose}",
                                "{debug:--debug}",
                            ],
                        },
                    },
                }
            }
        }

        # Test default action
        args = mock_args(subcommand="multi_action", action="default")
        context = CommandContext(config=config, env=os.environ.copy(), args=args)

        with patch("subprocess.run") as mock_subprocess:
            mock_subprocess.return_value.returncode = 0

            app_command = AppCommand("multi_action", context)
            invoker = CommandInvoker()
            result = invoker.execute_command(app_command)

            assert result is True
            call_args = mock_subprocess.call_args[0][0]
            assert call_args == ["echo", "default action"]

        # Test action with parameters
        args = mock_args(
            subcommand="multi_action",
            action="action_with_params",
            name="test_user",
            count=5,
        )
        context = CommandContext(config=config, env=os.environ.copy(), args=args)

        with patch("subprocess.run") as mock_subprocess:
            mock_subprocess.return_value.returncode = 0

            app_command = AppCommand("multi_action", context)
            invoker = CommandInvoker()
            result = invoker.execute_command(app_command)

            assert result is True
            call_args = mock_subprocess.call_args[0][0]
            assert "name=test_user" in call_args
            assert "count=5" in call_args

        # Test boolean flags
        args = mock_args(
            subcommand="multi_action",
            action="action_bool_flags",
            verbose=True,
            debug=False,
        )
        context = CommandContext(config=config, env=os.environ.copy(), args=args)

        with patch("subprocess.run") as mock_subprocess:
            mock_subprocess.return_value.returncode = 0

            app_command = AppCommand("multi_action", context)
            invoker = CommandInvoker()
            result = invoker.execute_command(app_command)

            assert result is True
            call_args = mock_subprocess.call_args[0][0]
            assert "--verbose" in call_args
            assert "--debug" not in call_args  # Should be omitted when False
