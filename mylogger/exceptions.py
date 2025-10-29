"""
Custom exceptions for MyLogger

This module defines custom exception classes used throughout the logger.
All exceptions inherit from LoggerError for easy catching.
"""


class LoggerError(Exception):
    """Base exception for all logger-related errors
    
    All custom exceptions in the logger inherit from this class,
    allowing users to catch all logger errors with a single except clause.
    
    Example:
        >>> try:
        ...     logger.add_handler(invalid_handler)
        ... except LoggerError as e:
        ...     print(f"Logger error: {e}")
    """
    pass


class HandlerNotFoundError(LoggerError):
    """Raised when attempting to access a handler that doesn't exist
    
    This occurs when trying to remove or modify a handler using an
    invalid or expired handler ID.
    
    Example:
        >>> logger.remove(999)  # Non-existent handler ID
        HandlerNotFoundError: Handler with ID 999 not found
    """
    
    def __init__(self, handler_id: int):
        self.handler_id = handler_id
        super().__init__(f"Handler with ID {handler_id} not found")


class InvalidLevelError(LoggerError):
    """Raised when an invalid log level is specified
    
    This occurs when using a level name or number that isn't recognized
    by the logger.
    
    Example:
        >>> logger.log("INVALID_LEVEL", "message")
        InvalidLevelError: Invalid log level: INVALID_LEVEL
    """
    
    def __init__(self, level):
        self.level = level
        super().__init__(f"Invalid log level: {level}")


class RotationError(LoggerError):
    """Raised when file rotation fails
    
    This can occur if the file cannot be renamed, moved, or if there
    are permission issues during rotation.
    
    Example:
        >>> # File rotation fails due to permissions
        RotationError: Failed to rotate log file: Permission denied
    """
    pass


class FormatterError(LoggerError):
    """Raised when message formatting fails
    
    This occurs when the format string contains invalid tokens or
    when field access fails during formatting.
    
    Example:
        >>> # Invalid format token
        FormatterError: Unknown format field: invalid_field
    """
    pass


class CompressionError(LoggerError):
    """Raised when log file compression fails
    
    This can occur if the compression library is unavailable or if
    there are I/O errors during compression.
    
    Example:
        >>> # Compression fails
        CompressionError: Failed to compress log file: No such file
    """
    pass


class RetentionError(LoggerError):
    """Raised when log retention cleanup fails
    
    This occurs when old log files cannot be deleted or when
    retention policy evaluation fails.
    
    Example:
        >>> # Retention cleanup fails
        RetentionError: Failed to delete old log files: Permission denied
    """
    pass


class FilterError(LoggerError):
    """Raised when a filter function fails
    
    This occurs when a custom filter function raises an exception
    during log record evaluation.
    
    Example:
        >>> # Filter function raises exception
        FilterError: Filter function raised: ValueError
    """
    pass


class SinkError(LoggerError):
    """Raised when a sink (handler destination) is invalid or unavailable
    
    This occurs when trying to write to a sink that is closed, invalid,
    or otherwise unavailable.
    
    Example:
        >>> # Writing to closed file
        SinkError: Sink is closed or unavailable
    """
    pass
