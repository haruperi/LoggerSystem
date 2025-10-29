"""
Custom exceptions for MyLogger
"""


class LoggerError(Exception):
    """Base exception for logger errors"""
    pass


class HandlerNotFoundError(LoggerError):
    """Raised when handler ID not found"""
    pass


class InvalidLevelError(LoggerError):
    """Raised when invalid log level specified"""
    pass


class RotationError(LoggerError):
    """Raised when rotation fails"""
    pass


class FormatterError(LoggerError):
    """Raised when formatting fails"""
    pass


class CompressionError(LoggerError):
    """Raised when compression fails"""
    pass
