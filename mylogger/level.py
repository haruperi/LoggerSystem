"""
Log level definitions and utilities
"""

from .record import Level

# Default log levels
TRACE = Level(name="TRACE", no=5, color="cyan", icon="🔍")
DEBUG = Level(name="DEBUG", no=10, color="cyan", icon="🐛")
INFO = Level(name="INFO", no=20, color="white", icon="ℹ️")
SUCCESS = Level(name="SUCCESS", no=25, color="green", icon="✅")
WARNING = Level(name="WARNING", no=30, color="yellow", icon="⚠️")
ERROR = Level(name="ERROR", no=40, color="red", icon="❌")
CRITICAL = Level(name="CRITICAL", no=50, color="red", icon="🔥")

DEFAULT_LEVELS = {
    "TRACE": TRACE,
    "DEBUG": DEBUG,
    "INFO": INFO,
    "SUCCESS": SUCCESS,
    "WARNING": WARNING,
    "ERROR": ERROR,
    "CRITICAL": CRITICAL,
}
