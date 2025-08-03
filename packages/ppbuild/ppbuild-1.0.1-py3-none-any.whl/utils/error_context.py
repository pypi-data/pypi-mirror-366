"""Structured error context objects for better error handling."""

import traceback
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class ErrorSeverity(Enum):
    """Error severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories for better classification."""

    CONFIGURATION = "configuration"
    VALIDATION = "validation"
    EXECUTION = "execution"
    SYSTEM = "system"
    USER_INPUT = "user_input"
    DEPENDENCY = "dependency"


@dataclass
class ErrorContext:
    """Structured error context with detailed information."""

    # Core error information
    code: str
    message: str
    category: ErrorCategory
    severity: ErrorSeverity = ErrorSeverity.MEDIUM

    # Context information
    component: Optional[str] = None
    operation: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)

    # Error resolution
    suggestions: List[str] = field(default_factory=list)
    documentation_url: Optional[str] = None

    # Technical details
    exception: Optional[Exception] = None
    stack_trace: Optional[str] = None

    def __post_init__(self):
        """Post-initialization to capture stack trace if exception exists."""
        if self.exception and not self.stack_trace:
            self.stack_trace = "".join(
                traceback.format_exception(
                    type(self.exception), self.exception, self.exception.__traceback__
                )
            )

    def to_dict(self) -> Dict[str, Any]:
        """Convert error context to dictionary."""
        return {
            "code": self.code,
            "message": self.message,
            "category": self.category.value,
            "severity": self.severity.value,
            "component": self.component,
            "operation": self.operation,
            "details": self.details,
            "suggestions": self.suggestions,
            "documentation_url": self.documentation_url,
            "exception_type": type(self.exception).__name__ if self.exception else None,
        }

    def format_user_message(self) -> str:
        """Format user-friendly error message."""
        message_parts = [f"Error: {self.message}"]

        if self.component:
            message_parts.append(f"Component: {self.component}")

        if self.operation:
            message_parts.append(f"Operation: {self.operation}")

        if self.details:
            details_str = ", ".join([f"{k}={v}" for k, v in self.details.items()])
            message_parts.append(f"Details: {details_str}")

        if self.suggestions:
            message_parts.append("Suggestions:")
            for suggestion in self.suggestions:
                message_parts.append(f"  - {suggestion}")

        return "\n".join(message_parts)


class ErrorContextBuilder:
    """Builder for creating error contexts."""

    def __init__(self, code: str, message: str, category: ErrorCategory):
        self._error_context = ErrorContext(
            code=code, message=message, category=category
        )

    def with_severity(self, severity: ErrorSeverity) -> "ErrorContextBuilder":
        """Set error severity."""
        self._error_context.severity = severity
        return self

    def with_component(self, component: str) -> "ErrorContextBuilder":
        """Set component name."""
        self._error_context.component = component
        return self

    def with_operation(self, operation: str) -> "ErrorContextBuilder":
        """Set operation name."""
        self._error_context.operation = operation
        return self

    def with_detail(self, key: str, value: Any) -> "ErrorContextBuilder":
        """Add a detail key-value pair."""
        self._error_context.details[key] = value
        return self

    def with_details(self, details: Dict[str, Any]) -> "ErrorContextBuilder":
        """Add multiple details."""
        self._error_context.details.update(details)
        return self

    def with_suggestion(self, suggestion: str) -> "ErrorContextBuilder":
        """Add a suggestion for error resolution."""
        self._error_context.suggestions.append(suggestion)
        return self

    def with_suggestions(self, suggestions: List[str]) -> "ErrorContextBuilder":
        """Add multiple suggestions."""
        self._error_context.suggestions.extend(suggestions)
        return self

    def with_documentation(self, url: str) -> "ErrorContextBuilder":
        """Set documentation URL."""
        self._error_context.documentation_url = url
        return self

    def with_exception(self, exception: Exception) -> "ErrorContextBuilder":
        """Set the underlying exception."""
        self._error_context.exception = exception
        return self

    def build(self) -> ErrorContext:
        """Build the error context."""
        return self._error_context


class PPError(Exception):
    """Custom exception that carries structured error context."""

    def __init__(self, error_context: ErrorContext):
        self.error_context = error_context
        super().__init__(error_context.message)

    def __str__(self) -> str:
        return self.error_context.format_user_message()


# Common error context factory functions
def create_config_error(message: str, **kwargs) -> ErrorContextBuilder:
    """Create configuration error context builder."""
    return (
        ErrorContextBuilder("CONFIG_ERROR", message, ErrorCategory.CONFIGURATION)
        .with_severity(ErrorSeverity.HIGH)
        .with_suggestions(
            [
                "Check your pp.yaml configuration file",
                "Validate YAML syntax",
                "Ensure all required fields are present",
            ]
        )
        .with_details(kwargs)
    )


def create_validation_error(message: str, **kwargs) -> ErrorContextBuilder:
    """Create validation error context builder."""
    return (
        ErrorContextBuilder("VALIDATION_ERROR", message, ErrorCategory.VALIDATION)
        .with_severity(ErrorSeverity.MEDIUM)
        .with_suggestions(["Check input parameters", "Validate data types and formats"])
        .with_details(kwargs)
    )


def create_execution_error(message: str, **kwargs) -> ErrorContextBuilder:
    """Create execution error context builder."""
    return (
        ErrorContextBuilder("EXECUTION_ERROR", message, ErrorCategory.EXECUTION)
        .with_severity(ErrorSeverity.HIGH)
        .with_suggestions(
            [
                "Check command configuration",
                "Verify environment variables",
                "Ensure required dependencies are installed",
            ]
        )
        .with_details(kwargs)
    )


def create_system_error(message: str, **kwargs) -> ErrorContextBuilder:
    """Create system error context builder."""
    return (
        ErrorContextBuilder("SYSTEM_ERROR", message, ErrorCategory.SYSTEM)
        .with_severity(ErrorSeverity.CRITICAL)
        .with_suggestions(
            [
                "Check system permissions",
                "Verify file paths exist",
                "Check available disk space and memory",
            ]
        )
        .with_details(kwargs)
    )
