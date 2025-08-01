from lynceus.utils import format_exception_human_readable


class LynceusError(Exception):
    """Base Lynceus exception, all specific exceptions inherits from it."""

    def __init__(self, message, from_exception: Exception | None = None):
        """
        Initialize a LynceusError with a message and optional cause.

        Args:
            message: The error message
            from_exception: Optional exception that caused this error
        """
        super().__init__()
        self.__message = message
        if from_exception:
            self.__message += f"; caused by {format_exception_human_readable(from_exception, quote_message=True)}."

    def __str__(self):
        """
        Return the error message as a string.

        Returns:
            str: The formatted error message
        """
        return self.__message


class LynceusConfigError(LynceusError):
    """Exception raised for configuration-related errors."""


class LynceusFileError(LynceusError):
    """Exception raised for file operation errors."""
