"""Integration tests for parameter validation and substitution."""

import pytest

from utils.error_context import PPError
from utils.parameter_utils import (parse_action_parameters,
                                   substitute_parameters, validate_parameter)


class TestParameterValidation:
    """Test parameter validation functionality."""

    def test_string_parameter_validation(self):
        """Test string parameter validation."""
        param_config = {"type": "string", "required": True}

        # Valid string
        result = validate_parameter("test_param", param_config, "hello")
        assert result == "hello"

        # Required parameter missing
        with pytest.raises(PPError, match="Required parameter 'test_param' is missing"):
            validate_parameter("test_param", param_config, None)

        # String with choices
        param_config = {"type": "string", "choices": ["a", "b", "c"]}
        result = validate_parameter("test_param", param_config, "b")
        assert result == "b"

        # Invalid choice
        with pytest.raises(PPError, match="Invalid choice for parameter"):
            validate_parameter("test_param", param_config, "d")

    def test_integer_parameter_validation(self):
        """Test integer parameter validation."""
        param_config = {"type": "integer", "min": 1, "max": 10}

        # Valid integer
        result = validate_parameter("test_param", param_config, "5")
        assert result == 5

        # Below minimum
        with pytest.raises(PPError, match="must be >= 1"):
            validate_parameter("test_param", param_config, "0")

        # Above maximum
        with pytest.raises(PPError, match="must be <= 10"):
            validate_parameter("test_param", param_config, "11")

        # Invalid integer
        with pytest.raises(PPError, match="Invalid value"):
            validate_parameter("test_param", param_config, "not_a_number")

    def test_float_parameter_validation(self):
        """Test float parameter validation."""
        param_config = {"type": "float", "min": 0.0, "max": 1.0}

        # Valid float
        result = validate_parameter("test_param", param_config, "0.5")
        assert result == 0.5

        # Below minimum
        with pytest.raises(PPError):
            validate_parameter("test_param", param_config, "-0.1")

        # Above maximum
        with pytest.raises(PPError):
            validate_parameter("test_param", param_config, "1.1")

    def test_boolean_parameter_validation(self):
        """Test boolean parameter validation."""
        param_config = {"type": "boolean"}

        # Boolean values
        assert validate_parameter("test_param", param_config, True) is True
        assert validate_parameter("test_param", param_config, False) is False

        # String representations
        assert validate_parameter("test_param", param_config, "true") is True
        assert validate_parameter("test_param", param_config, "yes") is True
        assert validate_parameter("test_param", param_config, "1") is True
        assert validate_parameter("test_param", param_config, "on") is True

        assert validate_parameter("test_param", param_config, "false") is False
        assert validate_parameter("test_param", param_config, "no") is False
        assert validate_parameter("test_param", param_config, "0") is False
        assert validate_parameter("test_param", param_config, "off") is False

    def test_parameter_defaults(self):
        """Test parameter default value handling."""
        param_config = {"type": "string", "default": "default_value"}

        # Use default when None
        result = validate_parameter("test_param", param_config, None)
        assert result == "default_value"

        # Use default when empty string
        result = validate_parameter("test_param", param_config, "")
        assert result == "default_value"

    def test_unknown_parameter_type(self):
        """Test handling of unknown parameter types."""
        param_config = {"type": "unknown_type"}

        with pytest.raises(PPError):
            validate_parameter("test_param", param_config, "value")


class TestParameterSubstitution:
    """Test parameter substitution in commands."""

    def test_simple_parameter_substitution(self):
        """Test basic parameter substitution."""
        command = ["echo", "Hello {name}"]
        parameters = {"name": "World"}

        result = substitute_parameters(command, parameters)
        assert result == ["echo", "Hello World"]

    def test_multiple_parameter_substitution(self):
        """Test multiple parameter substitution in single argument."""
        command = ["echo", "{greeting} {name}!"]
        parameters = {"greeting": "Hello", "name": "World"}

        result = substitute_parameters(command, parameters)
        assert result == ["echo", "Hello World!"]

    def test_boolean_flag_substitution(self):
        """Test boolean flag substitution."""
        command = ["command", "{verbose:--verbose}", "{debug:--debug}"]

        # Both flags true
        parameters = {"verbose": True, "debug": True}
        result = substitute_parameters(command, parameters)
        assert result == ["command", "--verbose", "--debug"]

        # One flag true, one false
        parameters = {"verbose": True, "debug": False}
        result = substitute_parameters(command, parameters)
        assert result == ["command", "--verbose"]

        # Both flags false
        parameters = {"verbose": False, "debug": False}
        result = substitute_parameters(command, parameters)
        assert result == ["command"]

    def test_missing_parameter_substitution(self):
        """Test substitution with missing parameters."""
        command = ["echo", "Hello {name}", "{missing}"]
        parameters = {"name": "World"}

        result = substitute_parameters(command, parameters)
        assert result == ["echo", "Hello World"]  # Empty arguments are filtered out

    def test_empty_parameter_substitution(self):
        """Test substitution with empty parameter values."""
        command = ["echo", "Value: '{value}'", "Count: {count}"]
        parameters = {"value": "", "count": 0}

        result = substitute_parameters(command, parameters)
        assert result == ["echo", "Value: ''", "Count: 0"]

    def test_non_string_arguments(self):
        """Test substitution with non-string arguments."""
        command = ["echo", 123, True, "Hello {name}"]
        parameters = {"name": "World"}

        result = substitute_parameters(command, parameters)
        assert result == ["echo", "123", "True", "Hello World"]


class TestActionParameterParsing:
    """Test parsing of action parameters from command line arguments."""

    def test_parse_simple_parameters(self, mock_args):
        """Test parsing simple parameters."""
        action_config = {
            "parameters": {
                "name": {"type": "string", "required": True},
                "count": {"type": "integer", "default": 1},
            }
        }

        args = mock_args(name="test", count=5)

        result = parse_action_parameters(action_config, args)

        assert result["name"] == "test"
        assert result["count"] == 5

    def test_parse_boolean_parameters(self, mock_args):
        """Test parsing boolean parameters."""
        action_config = {
            "parameters": {
                "verbose": {"type": "boolean", "default": False},
                "debug": {"type": "boolean", "default": True},
            }
        }

        args = mock_args(verbose=True, debug=None)  # debug should use default

        result = parse_action_parameters(action_config, args)

        assert result["verbose"] is True
        assert result["debug"] is True  # Should use default

    def test_parse_parameters_with_defaults(self, mock_args):
        """Test parsing parameters with default values."""
        action_config = {
            "parameters": {
                "optional": {"type": "string", "default": "default_value"},
                "required": {"type": "string", "required": True},
            }
        }

        args = mock_args(optional=None, required="provided")

        result = parse_action_parameters(action_config, args)

        assert result["optional"] == "default_value"
        assert result["required"] == "provided"

    def test_parse_parameters_validation_error(self, mock_args):
        """Test parameter parsing with validation errors."""
        action_config = {
            "parameters": {"required": {"type": "string", "required": True}}
        }

        args = mock_args(required=None)

        with pytest.raises(PPError):
            parse_action_parameters(action_config, args)
