"""
MyLogger - A Loguru-inspired logging library

A production-ready logging library inspired by Loguru, built with
Python standard library only.

Basic Usage:
    >>> from mylogger import logger
    >>> logger.info("Hello, World!")
    >>> logger.error("Something went wrong", user_id=123)
    >>> logger.warning("User {} logged in from {city}", "John", city="NYC")

Features:
    - Simple, intuitive API
    - Automatic frame inspection for caller context
    - Flexible message formatting (positional and named arguments)
    - Multiple log levels (TRACE, DEBUG, INFO, SUCCESS, WARNING, ERROR, CRITICAL)
    - Thread-safe logging
"""

from .logger import Logger, logger
from .level import (
    TRACE, DEBUG, INFO, SUCCESS, WARNING, ERROR, CRITICAL,
    DEFAULT_LEVELS
)
from .record import LogRecord, Level, FileInfo, ProcessInfo, ThreadInfo, ExceptionInfo
from .exceptions import (
    LoggerError, InvalidLevelError, HandlerNotFoundError,
    RotationError, FormatterError, CompressionError
)

__version__ = "1.0.0"
__all__ = [
    # Main logger interface
    "logger",
    "Logger",
    
    # Log levels
    "TRACE",
    "DEBUG", 
    "INFO",
    "SUCCESS",
    "WARNING",
    "ERROR",
    "CRITICAL",
    "DEFAULT_LEVELS",
    
    # Data structures
    "LogRecord",
    "Level",
    "FileInfo",
    "ProcessInfo",
    "ThreadInfo",
    "ExceptionInfo",
    
    # Exceptions
    "LoggerError",
    "InvalidLevelError",
    "HandlerNotFoundError",
    "RotationError",
    "FormatterError",
    "CompressionError",
]
