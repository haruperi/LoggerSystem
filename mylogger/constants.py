"""
Constants and default values for MyLogger

This module contains ANSI color codes, default format strings,
level mappings, and other configuration constants.
"""

# ANSI color codes - Foreground colors
COLORS = {
    # Standard colors
    "black": "\x1b[30m",
    "red": "\x1b[31m",
    "green": "\x1b[32m",
    "yellow": "\x1b[33m",
    "blue": "\x1b[34m",
    "magenta": "\x1b[35m",
    "cyan": "\x1b[36m",
    "white": "\x1b[37m",
    # Bright/bold colors
    "bright_black": "\x1b[90m",
    "bright_red": "\x1b[91m",
    "bright_green": "\x1b[92m",
    "bright_yellow": "\x1b[93m",
    "bright_blue": "\x1b[94m",
    "bright_magenta": "\x1b[95m",
    "bright_cyan": "\x1b[96m",
    "bright_white": "\x1b[97m",
    # Formatting
    "reset": "\x1b[0m",
    "bold": "\x1b[1m",
    "dim": "\x1b[2m",
    "italic": "\x1b[3m",
    "underline": "\x1b[4m",
}

# ANSI background colors
BG_COLORS = {
    "bg_black": "\x1b[40m",
    "bg_red": "\x1b[41m",
    "bg_green": "\x1b[42m",
    "bg_yellow": "\x1b[43m",
    "bg_blue": "\x1b[44m",
    "bg_magenta": "\x1b[45m",
    "bg_cyan": "\x1b[46m",
    "bg_white": "\x1b[47m",
}

# Level name to number mapping
LEVEL_MAP = {
    "TRACE": 5,
    "DEBUG": 10,
    "INFO": 20,
    "SUCCESS": 25,
    "WARNING": 30,
    "ERROR": 40,
    "CRITICAL": 50,
}

# Reverse mapping (number to name)
LEVEL_NAMES = {v: k for k, v in LEVEL_MAP.items()}

# Default format string
DEFAULT_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
    "<level>{message}</level>"
)

# Simple format (no colors)
SIMPLE_FORMAT = (
    "{time:YYYY-MM-DD HH:mm:ss} | " "{level: <8} | " "{name}:{function}:{line} - " "{message}"
)

# Minimal format
MINIMAL_FORMAT = "{level: <8} | {message}"

# Detailed format (with module and thread)
DETAILED_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{process.id}</cyan>:<cyan>{thread.name}</cyan> | "
    "<cyan>{name}</cyan>:<cyan>{module}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
    "<level>{message}</level>"
)

# JSON format (for structured logging)
JSON_FORMAT = "{message}"  # Will use serialization instead

# Default datetime format patterns
DATETIME_FORMATS = {
    "YYYY": "%Y",  # 4-digit year (2024)
    "YY": "%y",  # 2-digit year (24)
    "MMMM": "%B",  # Full month name (January)
    "MMM": "%b",  # Abbreviated month (Jan)
    "MM": "%m",  # 2-digit month (01)
    "M": "%-m",  # Month without leading zero (1) - Unix only
    "DD": "%d",  # 2-digit day (01)
    "D": "%-d",  # Day without leading zero (1) - Unix only
    "HH": "%H",  # 2-digit hour 24h (00-23)
    "H": "%-H",  # Hour 24h without leading zero - Unix only
    "hh": "%I",  # 2-digit hour 12h (01-12)
    "h": "%-I",  # Hour 12h without leading zero - Unix only
    "mm": "%M",  # 2-digit minute (00)
    "m": "%-M",  # Minute without leading zero - Unix only
    "ss": "%S",  # 2-digit second (00)
    "s": "%-S",  # Second without leading zero - Unix only
    "SSS": "%f",  # Microseconds (will be truncated to milliseconds)
    "A": "%p",  # AM/PM
    "ZZ": "%z",  # Timezone offset (+0000)
    "Z": "%Z",  # Timezone name (UTC)
}

# Default file encoding
DEFAULT_ENCODING = "utf-8"

# Default buffer size for file handlers
DEFAULT_BUFFER_SIZE = -1  # System default (line buffered for text files)

# Environment variables
ENV_NO_COLOR = "NO_COLOR"
ENV_LOG_LEVEL = "MYLOGGER_LEVEL"
ENV_LOG_FORMAT = "MYLOGGER_FORMAT"

# Size multipliers for parse_size()
SIZE_UNITS = {
    "B": 1,
    "KB": 1024,
    "MB": 1024**2,
    "GB": 1024**3,
    "TB": 1024**4,
    "K": 1024,
    "M": 1024**2,
    "G": 1024**3,
    "T": 1024**4,
}

# Time multipliers for parse_duration()
TIME_UNITS = {
    "microsecond": 1e-6,
    "microseconds": 1e-6,
    "us": 1e-6,
    "millisecond": 1e-3,
    "milliseconds": 1e-3,
    "ms": 1e-3,
    "second": 1,
    "seconds": 1,
    "s": 1,
    "sec": 1,
    "secs": 1,
    "minute": 60,
    "minutes": 60,
    "m": 60,
    "min": 60,
    "mins": 60,
    "hour": 3600,
    "hours": 3600,
    "h": 3600,
    "hr": 3600,
    "hrs": 3600,
    "day": 86400,
    "days": 86400,
    "d": 86400,
    "week": 604800,
    "weeks": 604800,
    "w": 604800,
}

# Default logger name
DEFAULT_LOGGER_NAME = "mylogger"
