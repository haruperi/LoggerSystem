"""
Constants and default values
"""

# ANSI color codes
COLORS = {
    'black': '[30m',
    'red': '[31m',
    'green': '[32m',
    'yellow': '[33m',
    'blue': '[34m',
    'magenta': '[35m',
    'cyan': '[36m',
    'white': '[37m',
    'bright_black': '[90m',
    'bright_red': '[91m',
    'bright_green': '[92m',
    'bright_yellow': '[93m',
    'bright_blue': '[94m',
    'bright_magenta': '[95m',
    'bright_cyan': '[96m',
    'bright_white': '[97m',
    'reset': '[0m',
    'bold': '[1m',
    'dim': '[2m',
    'italic': '[3m',
    'underline': '[4m',
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
