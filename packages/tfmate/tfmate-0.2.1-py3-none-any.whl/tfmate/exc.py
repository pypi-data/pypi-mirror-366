"""
Custom exceptions for tfmate.
"""

from typing import List


class StateFileError(Exception):
    """
    Exception raised when state file access fails
    """

    def __init__(
        self, location: str, reason: str, suggestions: List[str] | None = None
    ):
        """
        Initialize StateFileError.

        Args:
            location: Location where the error occurred
            reason: Reason for the error
            suggestions: List of suggestions to fix the error

        """
        self.location = location
        self.reason = reason
        self.suggestions = suggestions or []
        super().__init__(f"State file error at {location}: {reason}")


class CredentialError(Exception):
    """
    Exception raised when credential access fails
    """

    def __init__(self, message: str, suggestions: List[str]):
        """
        Initialize CredentialError.

        Args:
            message: Error message
            suggestions: List of suggestions to fix the error

        """
        self.message = message
        self.suggestions = suggestions
        super().__init__(
            f"{message}\nSuggestions:\n" + "\n".join(f"- {s}" for s in suggestions)
        )


class TerraformConfigError(Exception):
    """
    Exception raised when Terraform configuration is invalid
    """

    def __init__(
        self, message: str, field: str | None = None, value: str | None = None
    ):
        """
        Initialize TerraformConfigError.

        Args:
            message: Error message
            field: Field that caused the error
            value: Value that caused the error

        """
        self.message = message
        self.field = field
        self.value = value
        super().__init__(f"Terraform config error: {message}")
