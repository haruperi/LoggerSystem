"""
Tests for Logger class
"""

import pytest
from mylogger import logger


def test_logger_exists():
    """Test that logger instance exists"""
    assert logger is not None


def test_basic_logging():
    """Test basic logging methods"""
    # These should not raise
    logger.trace("trace message")
    logger.debug("debug message")
    logger.info("info message")
    logger.success("success message")
    logger.warning("warning message")
    logger.error("error message")
    logger.critical("critical message")


# TODO: Add more tests
