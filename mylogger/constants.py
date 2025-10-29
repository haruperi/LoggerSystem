"""
Constants and default values
"""

# ANSI color codes
COLORS = {
    'black': '\x1b[30m',
    'red': '\x1b[31m',
    'green': '\x1b[32m',
    'yellow': '\x1b[33m',
    'blue': '\x1b[34m',
    'magenta': '\x1b[35m',
    'cyan': '\x1b[36m',
    'white': '\x1b[37m',
    'bright_black': '\x1b[90m',
    'bright_red': '\x1b[91m',
    'bright_green': '\x1b[92m',
    'bright_yellow': '\x1b[93m',
    'bright_blue': '\x1b[94m',
    'bright_magenta': '\x1b[95m',
    'bright_cyan': '\x1b[96m',
    'bright_white': '\x1b[97m',
    'reset': '\x1b[0m',
    'bold': '\x1b[1m',
    'dim': '\x1b[2m',
    'italic': '\x1b[3m',
    'underline': '\x1b[4m',
}

# Default format string
DEFAULT_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
    "<level>{message}</level>"
)

# Environment variables
ENV_NO_COLOR = "NO_COLOR"
ENV_LOG_LEVEL = "MYLOGGER_LEVEL"
ENV_LOG_FORMAT = "MYLOGGER_FORMAT"
