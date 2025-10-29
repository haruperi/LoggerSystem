"""
Multiple handler configuration examples
"""

import sys
from mylogger import logger


def main():
    """Configure multiple handlers"""

    # Console: only warnings and above, colored
    logger.add(sys.stderr, level="WARNING", colorize=True)

    # File: all debug logs
    logger.add("logs/debug.log", level="DEBUG", rotation="1 day")

    # File: only errors with full diagnosis
    logger.add("logs/errors.log", level="ERROR", backtrace=True, diagnose=True)

    # JSON file for log aggregation
    logger.add("logs/app.json", level="INFO", serialize=True)

    # Test the handlers
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")


if __name__ == "__main__":
    main()
