"""
Test basic logger functionality for Day 4
"""

import sys
import os
from io import StringIO

# Add the parent directory to the path to import mylogger
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from mylogger import logger, Logger


def test_basic_logging():
    """Test basic logging methods"""
    print("=" * 60)
    print("TEST 1: Basic Logging Methods")
    print("=" * 60)

    logger.trace("This is a TRACE message")
    logger.debug("This is a DEBUG message")
    logger.info("This is an INFO message")
    logger.success("This is a SUCCESS message")
    logger.warning("This is a WARNING message")
    logger.error("This is an ERROR message")
    logger.critical("This is a CRITICAL message")
    print()


def test_message_formatting_positional():
    """Test message formatting with positional arguments"""
    print("=" * 60)
    print("TEST 2: Message Formatting - Positional Arguments")
    print("=" * 60)

    logger.info("User {}", "John")
    logger.info("User {} logged in from {}", "John", "NYC")
    logger.info("Numbers: {}, {}, {}", 1, 2, 3)
    print()


def test_message_formatting_named():
    """Test message formatting with named arguments"""
    print("=" * 60)
    print("TEST 3: Message Formatting - Named Arguments")
    print("=" * 60)

    logger.info("User {name}", name="John")
    logger.info("User {name} logged in from {city}", name="John", city="NYC")
    logger.info("Order #{order_id} for ${amount:.2f}", order_id=12345, amount=99.99)
    print()


def test_message_formatting_mixed():
    """Test message formatting with mixed arguments"""
    print("=" * 60)
    print("TEST 4: Message Formatting - Mixed Arguments")
    print("=" * 60)

    logger.info("User {} from {city}", "John", city="NYC")
    logger.info("Processing {} items for {user}", 10, user="admin")
    print()


def test_extra_context():
    """Test extra context in kwargs"""
    print("=" * 60)
    print("TEST 5: Extra Context")
    print("=" * 60)

    logger.info("User logged in", user_id=123, session_id="abc123")
    logger.error("Failed to process request", error_code=500, url="/api/users")
    print()


def test_log_method():
    """Test the public log() method"""
    print("=" * 60)
    print("TEST 6: log() Method with String Levels")
    print("=" * 60)

    logger.log("INFO", "Using log() with string level")
    logger.log("ERROR", "Error via log() method")
    print()

    print("=" * 60)
    print("TEST 7: log() Method with Numeric Levels")
    print("=" * 60)

    logger.log(10, "DEBUG level (10)")
    logger.log(20, "INFO level (20)")
    logger.log(40, "ERROR level (40)")
    print()


def test_multiple_logger_instances():
    """Test multiple logger instances"""
    print("=" * 60)
    print("TEST 8: Multiple Logger Instances")
    print("=" * 60)

    logger1 = Logger()
    logger2 = Logger()

    logger1.info("Message from logger1")
    logger2.info("Message from logger2")

    # They should have different start times
    print(f"Logger1 start time: {logger1.start_time}")
    print(f"Logger2 start time: {logger2.start_time}")
    print()


def test_global_logger():
    """Test the global logger instance"""
    print("=" * 60)
    print("TEST 9: Global Logger Instance")
    print("=" * 60)

    from mylogger import logger as global_logger

    global_logger.info("Using global logger instance")
    global_logger.success("Global logger works!")
    print()


def test_exception_info():
    """Test logging with exception info"""
    print("=" * 60)
    print("TEST 10: Exception Info (Basic)")
    print("=" * 60)

    try:
        result = 1 / 0
    except ZeroDivisionError as e:
        # For now, just log with exception kwarg
        # Full exception formatting will come in Day 13
        logger.error("Division by zero occurred", exception=e)
    print()


def test_level_validation():
    """Test level validation"""
    print("=" * 60)
    print("TEST 11: Level Validation")
    print("=" * 60)

    # Valid level
    logger.log("INFO", "Valid level")

    # Invalid level should raise InvalidLevelError
    try:
        logger.log("INVALID", "This should fail")
    except Exception as e:
        print(f"[OK] Caught expected error: {type(e).__name__}: {e}", file=sys.stderr)

    # Invalid numeric level
    try:
        logger.log(999, "This should also fail")
    except Exception as e:
        print(f"[OK] Caught expected error: {type(e).__name__}: {e}", file=sys.stderr)
    print()


def test_formatting_error_handling():
    """Test that formatting errors are handled gracefully"""
    print("=" * 60)
    print("TEST 12: Formatting Error Handling")
    print("=" * 60)

    # Too few arguments
    logger.info("User {} from {}", "John")  # Missing second argument

    # Missing key
    logger.info("User {name} from {city}", name="John")  # Missing city

    print("[OK] Formatting errors handled gracefully (logs still output)")
    print()


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("MYLOGGER DAY 4 - BASIC LOGGER IMPLEMENTATION TESTS")
    print("=" * 60 + "\n")

    test_basic_logging()
    test_message_formatting_positional()
    test_message_formatting_named()
    test_message_formatting_mixed()
    test_extra_context()
    test_log_method()
    test_multiple_logger_instances()
    test_global_logger()
    test_exception_info()
    test_level_validation()
    test_formatting_error_handling()

    print("=" * 60)
    print("ALL TESTS COMPLETED")
    print("=" * 60)
    print("\nNote: Logs are currently printed to stderr with basic formatting.")
    print("Full formatting with colors will be implemented in Day 6 & 9.")
    print("Handler management will be implemented in Day 5.")


if __name__ == "__main__":
    main()
