"""Pytest configuration and fixtures for pp_refactored tests."""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from commands.base_command import CommandContext


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def test_config():
    """Test configuration with various application types."""
    return {
        "applications": {
            "simple_app": {
                "help": "Simple test application",
                "default_action": "run",
                "actions": {
                    "run": {
                        "help": "Run the application",
                        "command": ["echo", "simple app running"],
                    }
                },
            },
            "param_app": {
                "help": "Application with parameters",
                "directory": "/tmp/test",
                "venv": "/tmp/venv",
                "env_vars": {"TEST_VAR": "test_value", "ENV_VAR": "${TEST_ENV_VAR}"},
                "default_action": "run",
                "actions": {
                    "run": {
                        "help": "Run with parameters",
                        "parameters": {
                            "name": {
                                "type": "string",
                                "required": True,
                                "help": "Name parameter",
                            },
                            "count": {
                                "type": "integer",
                                "default": 1,
                                "min": 1,
                                "max": 10,
                                "help": "Count parameter",
                            },
                            "verbose": {
                                "type": "boolean",
                                "default": False,
                                "help": "Verbose flag",
                            },
                            "mode": {
                                "type": "string",
                                "choices": ["dev", "prod", "test"],
                                "default": "dev",
                                "help": "Mode selection",
                            },
                        },
                        "command": [
                            "echo",
                            "name={name}",
                            "count={count}",
                            "{verbose:--verbose}",
                            "mode={mode}",
                        ],
                    },
                    "test": {
                        "help": "Test action",
                        "parameters": {
                            "coverage": {
                                "type": "boolean",
                                "default": True,
                                "help": "Generate coverage",
                            }
                        },
                        "command": ["pytest", "{coverage:--cov}"],
                    },
                },
            },
            "complex_app": {
                "help": "Complex application with multiple actions",
                "actions": {
                    "action1": {"help": "First action", "command": ["echo", "action1"]},
                    "action2": {
                        "help": "Second action",
                        "parameters": {
                            "param1": {
                                "type": "string",
                                "required": True,
                                "help": "Required parameter",
                            }
                        },
                        "command": ["echo", "action2", "{param1}"],
                    },
                    "action3": {"help": "Third action", "command": ["echo", "action3"]},
                },
            },
        }
    }


@pytest.fixture
def test_config_file(temp_dir, test_config):
    """Create a test configuration file."""
    config_file = temp_dir / "test_config.yaml"
    with open(config_file, "w") as f:
        yaml.dump(test_config, f)
    return config_file


@pytest.fixture
def test_env_file(temp_dir):
    """Create a test environment file."""
    env_file = temp_dir / "test_pp.env"
    env_content = """
TEST_ENV_VAR=from_env_file
DATABASE_URL=postgresql://test:test@localhost/testdb
API_KEY=test_api_key_123
DEBUG=true
"""
    with open(env_file, "w") as f:
        f.write(env_content.strip())
    return env_file


@pytest.fixture
def mock_args():
    """Mock argparse.Namespace object."""

    class MockArgs:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

    return MockArgs


@pytest.fixture
def command_context(test_config, mock_args):
    """Create a CommandContext for testing."""
    args = mock_args(subcommand="test_app", action="run")
    return CommandContext(config=test_config, env=os.environ.copy(), args=args)


@pytest.fixture
def mock_subprocess():
    """Mock subprocess.run for testing command execution."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        yield mock_run


@pytest.fixture
def mock_os_chdir():
    """Mock os.chdir for testing directory changes."""
    with patch("os.chdir") as mock_chdir:
        yield mock_chdir


@pytest.fixture
def mock_path_exists():
    """Mock Path.exists for testing file/directory existence."""
    with patch("pathlib.Path.exists") as mock_exists:
        mock_exists.return_value = True
        yield mock_exists


@pytest.fixture
def mock_path_is_dir():
    """Mock Path.is_dir for testing directory checks."""
    with patch("pathlib.Path.is_dir") as mock_is_dir:
        mock_is_dir.return_value = True
        yield mock_is_dir
