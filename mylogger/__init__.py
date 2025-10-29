"""
MyLogger - A Loguru-inspired logging library
"""

from .logger import Logger

# Create a global logger instance
logger = Logger()

__version__ = "1.0.0"
__all__ = ["logger", "Logger"]
