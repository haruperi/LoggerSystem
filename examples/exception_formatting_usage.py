"""
Exception Formatting Examples

This module demonstrates mylogger's beautiful exception formatting with:
- Detailed stack traces
- Colorized output
- Variable inspection (diagnose mode)
- Context lines around errors
"""

import sys
import os
from pathlib import Path

# Add parent directory to path to import mylogger
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from mylogger import Logger


def example_1_basic_exception():
    """Example 1: Basic exception logging"""
    print("\n" + "=" * 70)
    print("Example 1: Basic Exception Logging")
    print("=" * 70)

    logger = Logger()
    logger.add(sys.stderr, level="DEBUG", colorize=True)

    print("Logging a simple exception...")

    try:
        result = 10 / 0
    except Exception as e:
        logger.exception("Division by zero occurred!")

    print("\n[OK] Basic exception logged with full traceback")


def example_2_exception_with_backtrace_disabled():
    """Example 2: Exception without full backtrace"""
    print("\n" + "=" * 70)
    print("Example 2: Exception Without Backtrace")
    print("=" * 70)

    logger = Logger()
    logger.add(sys.stderr, level="DEBUG", colorize=True, backtrace=False)

    print("Logging exception without full backtrace...")

    try:
        numbers = [1, 2, 3]
        value = numbers[10]  # IndexError
    except Exception as e:
        logger.error("Index out of range!")

    print("\n[OK] Exception logged without backtrace (only message)")


def example_3_diagnose_mode():
    """Example 3: Diagnose mode shows variable values"""
    print("\n" + "=" * 70)
    print("Example 3: Diagnose Mode (Variable Inspection)")
    print("=" * 70)

    logger = Logger()
    logger.add(sys.stderr, level="DEBUG", colorize=True, diagnose=True)

    print("Logging exception with variable inspection...")

    try:
        username = "alice"
        user_id = 12345
        account_balance = 1000.50
        permissions = ["read", "write"]

        # Simulate an error
        discount = account_balance / 0
    except Exception as e:
        logger.exception("Failed to calculate discount!")

    print("\n[OK] Exception logged with local variables shown")


def example_4_nested_function_calls():
    """Example 4: Exception in nested function calls"""
    print("\n" + "=" * 70)
    print("Example 4: Nested Function Call Stack")
    print("=" * 70)

    logger = Logger()
    logger.add(sys.stderr, level="DEBUG", colorize=True)

    def process_data(data):
        """Process data - innermost function"""
        return data["missing_key"]  # KeyError

    def validate_input(data):
        """Validate input - middle function"""
        if not data:
            raise ValueError("Data cannot be empty")
        return process_data(data)

    def handle_request(data):
        """Handle request - outer function"""
        return validate_input(data)

    print("Logging exception with nested call stack...")

    try:
        data = {"name": "test"}
        handle_request(data)
    except Exception as e:
        logger.exception("Request handling failed!")

    print("\n[OK] Full call stack shown in traceback")


def example_5_file_logging_with_exceptions():
    """Example 5: Logging exceptions to file"""
    print("\n" + "=" * 70)
    print("Example 5: Exception Logging to File")
    print("=" * 70)

    log_file = Path("logs_exception_example") / "errors.log"
    log_file.parent.mkdir(exist_ok=True)

    logger = Logger()
    logger.add(
        str(log_file),
        level="ERROR",
        colorize=False,  # No colors in files
        backtrace=True,
        diagnose=True,
    )

    print(f"Logging exceptions to: {log_file}")

    try:
        config = {"host": "localhost", "port": 8080}
        timeout = config["timeout"]  # KeyError
    except Exception as e:
        logger.exception("Configuration error!")

    print(f"[OK] Exception logged to {log_file}")
    print(f"File size: {log_file.stat().st_size} bytes")


def example_6_exception_in_loop():
    """Example 6: Exceptions in loop iterations"""
    print("\n" + "=" * 70)
    print("Example 6: Exceptions in Loop")
    print("=" * 70)

    logger = Logger()
    logger.add(sys.stderr, level="WARNING", colorize=True, backtrace=False)

    print("Processing items with error handling...")

    items = [10, 5, 0, 2, -1]

    for i, item in enumerate(items):
        try:
            result = 100 / item
            logger.info(f"Item {i}: 100 / {item} = {result}")
        except ZeroDivisionError:
            logger.warning(f"Item {i}: Cannot divide by zero")
        except Exception as e:
            logger.exception(f"Item {i}: Unexpected error!")

    print("\n[OK] Loop continued despite exceptions")


def example_7_custom_exception():
    """Example 7: Custom exception with context"""
    print("\n" + "=" * 70)
    print("Example 7: Custom Exception Types")
    print("=" * 70)

    class DatabaseError(Exception):
        """Custom database exception"""

        pass

    class AuthenticationError(Exception):
        """Custom authentication exception"""

        pass

    logger = Logger()
    logger.add(sys.stderr, level="DEBUG", colorize=True, diagnose=True)

    print("Logging custom exceptions...")

    try:
        username = "test_user"
        password = "wrong_password"

        # Simulate authentication failure
        if password != "correct_password":
            raise AuthenticationError(f"Authentication failed for user: {username}")
    except AuthenticationError as e:
        logger.exception("User authentication failed!")

    print("\n[OK] Custom exception logged")


def example_8_exception_chaining():
    """Example 8: Exception chaining (raise from)"""
    print("\n" + "=" * 70)
    print("Example 8: Exception Chaining")
    print("=" * 70)

    logger = Logger()
    logger.add(sys.stderr, level="DEBUG", colorize=True)

    print("Logging chained exceptions...")

    try:
        try:
            # First exception
            data = {"value": "not_a_number"}
            number = int(data["value"])
        except ValueError as e:
            # Chain with a new exception
            raise RuntimeError("Failed to parse configuration") from e
    except Exception as e:
        logger.exception("Configuration parsing failed!")

    print("\n[OK] Chained exception logged")


def example_9_no_colorize_for_files():
    """Example 9: Comparison of colorized vs plain output"""
    print("\n" + "=" * 70)
    print("Example 9: Colorized vs Plain Output")
    print("=" * 70)

    # Colorized (for terminal)
    logger_color = Logger()
    logger_color.add(sys.stderr, level="DEBUG", colorize=True)

    # Plain (for files or piped output)
    logger_plain = Logger()
    log_file = Path("logs_exception_example") / "plain.log"
    logger_plain.add(str(log_file), level="DEBUG", colorize=False)

    print("Logging same exception to terminal (colorized) and file (plain)...")

    try:
        items = []
        first_item = items[0]
    except Exception as e:
        logger_color.debug("Terminal output (colorized):")
        # logger_color.exception("List is empty!")

        logger_plain.debug("File output (plain):")
        logger_plain.exception("List is empty!")

    print(f"\n[OK] Check {log_file} for plain output")


def example_10_real_world_scenario():
    """Example 10: Real-world error handling scenario"""
    print("\n" + "=" * 70)
    print("Example 10: Real-World Scenario - API Request Handler")
    print("=" * 70)

    logger = Logger()
    logger.add(sys.stderr, level="INFO", colorize=True, diagnose=True)

    def fetch_user_data(user_id):
        """Simulate fetching user data from API"""
        # Simulate different error scenarios
        if user_id < 0:
            raise ValueError("User ID must be positive")
        elif user_id == 0:
            raise KeyError("User not found")
        else:
            # Simulate network error
            raise ConnectionError("Failed to connect to database")

    def process_user_request(user_id):
        """Process a user request with proper error handling"""
        request_id = "REQ-12345"
        timestamp = "2025-10-29 17:00:00"

        logger.info(f"Processing request {request_id} for user {user_id}")

        try:
            user_data = fetch_user_data(user_id)
            logger.info(f"Successfully fetched data for user {user_id}")
            return user_data
        except ValueError as e:
            logger.error(f"Invalid user ID: {user_id}")
        except KeyError as e:
            logger.warning(f"User {user_id} not found")
        except ConnectionError as e:
            logger.exception(f"Database connection failed for request {request_id}")
        except Exception as e:
            logger.exception(f"Unexpected error processing request {request_id}")

    print("Simulating API request handling...")

    # Test different error scenarios
    process_user_request(-1)  # ValueError
    process_user_request(0)  # KeyError
    process_user_request(100)  # ConnectionError

    print("\n[OK] Real-world error handling demonstrated")


def main():
    print("=" * 70)
    print("Exception Formatting Examples - MyLogger")
    print("=" * 70)

    example_1_basic_exception()
    example_2_exception_with_backtrace_disabled()
    example_3_diagnose_mode()
    example_4_nested_function_calls()
    example_5_file_logging_with_exceptions()
    example_6_exception_in_loop()
    example_7_custom_exception()
    example_8_exception_chaining()
    example_9_no_colorize_for_files()
    example_10_real_world_scenario()

    print("\n" + "=" * 70)
    print("[OK] All exception formatting examples completed!")
    print("=" * 70)

    print("\nKey Features Demonstrated:")
    print("  - Full stack traces with file/line/function info")
    print("  - Colorized output for better readability")
    print("  - Variable inspection with diagnose=True")
    print("  - Context lines around error location")
    print("  - Backtrace control (show/hide full trace)")
    print("  - Custom exception types")
    print("  - Exception chaining")
    print("  - Real-world error handling patterns")


if __name__ == "__main__":
    main()
