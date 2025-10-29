"""
Decorators and Utilities Usage Examples (Day 16)

This example demonstrates:
1. @logger.catch decorator for exception handling
2. logger.opt() for temporary options
3. add_level() for custom log levels
4. disable() and enable() for module control
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from mylogger import Logger


def example_1_catch_basic():
    """Example 1: Basic @logger.catch decorator"""
    print("=" * 60)
    print("Example 1: Basic @logger.catch Decorator")
    print("=" * 60)

    logger = Logger()
    logger.add(sys.stdout, level="INFO", format="{level} | {message}")

    @logger.catch()
    def risky_function():
        """This function will raise an exception"""
        return 1 / 0

    # Call the risky function - it logs the exception but doesn't crash
    result = risky_function()
    print(f"Function returned: {result}")  # Returns None after catching

    print()


def example_2_catch_with_options():
    """Example 2: @logger.catch with options"""
    print("=" * 60)
    print("Example 2: @logger.catch with Options")
    print("=" * 60)

    logger = Logger()
    logger.add(sys.stdout, level="INFO", format="{level} | {message}")

    # Custom level and message
    @logger.catch(level="WARNING", message="Database connection failed")
    def connect_to_database():
        raise ConnectionError("Cannot connect to database")

    # Catch specific exception types
    @logger.catch(exception=ValueError, level="WARNING")
    def parse_data(data):
        if not data:
            raise ValueError("Empty data")
        return int(data)

    connect_to_database()
    parse_data("")

    print()


def example_3_catch_reraise():
    """Example 3: @logger.catch with reraise"""
    print("=" * 60)
    print("Example 3: @logger.catch with Reraise")
    print("=" * 60)

    logger = Logger()
    logger.add(sys.stdout, level="INFO", format="{level} | {message}")

    @logger.catch(reraise=True, message="Error in critical function")
    def critical_function():
        raise RuntimeError("Critical error occurred")

    try:
        critical_function()
    except RuntimeError:
        print("Exception was reraised and caught here")

    print()


def example_4_catch_with_callback():
    """Example 4: @logger.catch with onerror callback"""
    print("=" * 60)
    print("Example 4: @logger.catch with Callback")
    print("=" * 60)

    logger = Logger()
    logger.add(sys.stdout, level="INFO", format="{level} | {message}")

    def error_handler(exception):
        """Custom error handler"""
        print(f"Custom handler: Caught {type(exception).__name__}: {exception}")

    @logger.catch(onerror=error_handler)
    def function_with_error():
        raise ValueError("Something went wrong")

    function_with_error()

    print()


def example_5_opt_with_exception():
    """Example 5: logger.opt() with exception info"""
    print("=" * 60)
    print("Example 5: logger.opt() with Exception")
    print("=" * 60)

    logger = Logger()
    logger.add(sys.stdout, level="INFO", format="{level} | {message}")

    try:
        result = 10 / 0
    except ZeroDivisionError:
        # Log with exception info from current exception context
        logger.opt(exception=True).error("Division by zero occurred")

    # Can also pass exception directly
    try:
        value = int("not a number")
    except ValueError as e:
        logger.opt(exception=e).error("Failed to convert value")

    print()


def example_6_opt_with_depth():
    """Example 6: logger.opt() with depth adjustment"""
    print("=" * 60)
    print("Example 6: logger.opt() with Depth Adjustment")
    print("=" * 60)

    logger = Logger()
    logger.add(sys.stdout, level="INFO", format="{file}:{line} | {function} | {message}")

    def wrapper_function():
        """Wrapper that logs from different depths"""
        # Normal log - shows wrapper_function
        logger.info("From wrapper (depth=0)")

        # Adjusted depth - shows calling function
        logger.opt(depth=1).info("From caller (depth=1)")

    wrapper_function()

    print()


def example_7_add_custom_level():
    """Example 7: Adding custom log levels"""
    print("=" * 60)
    print("Example 7: Adding Custom Log Levels")
    print("=" * 60)

    logger = Logger()
    logger.add(sys.stdout, level="TRACE", format="{level} | {message}")

    # Add custom levels
    logger.add_level("VERBOSE", 15, color="cyan", icon="🔍")
    logger.add_level("NOTICE", 22, color="blue", icon="📢")
    logger.add_level("AUDIT", 45, color="magenta", icon="📋")

    # Use the new levels
    logger.debug("Debug message (10)")
    logger.verbose("Verbose message (15)")
    logger.info("Info message (20)")
    logger.notice("Notice message (22)")
    logger.warning("Warning message (30)")
    logger.error("Error message (40)")
    logger.audit("Audit message (45)")
    logger.critical("Critical message (50)")

    print()


def example_8_custom_level_with_handler():
    """Example 8: Custom levels with specific handlers"""
    print("=" * 60)
    print("Example 8: Custom Levels with Handlers")
    print("=" * 60)

    logger = Logger()

    # Add custom levels
    logger.add_level("AUDIT", 45, color="magenta")
    logger.add_level("SECURITY", 47, color="red")

    # Handler only for audit and security
    logger.add(sys.stdout, level="AUDIT", format="{level} | {message}")

    logger.info("Regular info - won't show")
    logger.error("Regular error - won't show")
    logger.audit("Audit log entry - will show")
    logger.security("Security alert - will show")
    logger.critical("Critical - will show")

    print()


def example_9_disable_enable():
    """Example 9: Disabling and enabling modules"""
    print("=" * 60)
    print("Example 9: Disabling and Enabling Modules")
    print("=" * 60)

    logger = Logger()
    logger.add(sys.stdout, level="INFO", format="{level} | {message}")

    # Disable noisy third-party libraries (simulated)
    logger.disable("urllib3")
    logger.disable("requests")

    print("Disabled urllib3 and requests logging")

    # Re-enable if needed
    logger.enable("requests")
    print("Re-enabled requests logging")

    print()


def example_10_practical_catch_usage():
    """Example 10: Practical @logger.catch usage"""
    print("=" * 60)
    print("Example 10: Practical Usage - API Endpoint")
    print("=" * 60)

    logger = Logger()
    logger.add(sys.stdout, level="INFO", format="{level} | {function} | {message}")

    @logger.catch(level="ERROR", message="Failed to process request")
    def api_endpoint(user_id, data):
        """Simulated API endpoint"""
        if not user_id:
            raise ValueError("user_id is required")
        if not data:
            raise ValueError("data is required")

        # Process data
        result = {"status": "success", "user_id": user_id}
        return result

    # These will be logged but won't crash the application
    api_endpoint(None, {"key": "value"})
    api_endpoint(123, None)

    # This works
    result = api_endpoint(123, {"key": "value"})
    print(f"Success: {result}")

    print()


def example_11_combined_opt_and_catch():
    """Example 11: Combining opt() and catch()"""
    print("=" * 60)
    print("Example 11: Combining opt() and catch()")
    print("=" * 60)

    logger = Logger()
    logger.add(sys.stdout, level="INFO", format="{level} | {message}")

    @logger.catch(message="Error in processor")
    def process_data(data):
        """Process data with detailed error logging"""
        try:
            result = complex_operation(data)
            return result
        except Exception as e:
            # Use opt to add exception info in addition to catch
            logger.opt(exception=True).error(f"Complex operation failed for data: {data}")
            raise  # Reraise so catch can log it

    def complex_operation(data):
        if data < 0:
            raise ValueError("Data must be positive")
        return data * 2

    process_data(-5)

    print()


def example_12_custom_logger_subclass():
    """Example 12: Custom levels for application domain"""
    print("=" * 60)
    print("Example 12: Domain-Specific Custom Levels")
    print("=" * 60)

    logger = Logger()
    logger.add(sys.stdout, level="TRACE", format="{level:8} | {message}")

    # E-commerce application custom levels
    logger.add_level("ORDER", 24, color="green", icon="🛒")
    logger.add_level("PAYMENT", 26, color="yellow", icon="💳")
    logger.add_level("SHIPPING", 23, color="blue", icon="📦")

    # Use domain-specific logging
    logger.order("New order received: #12345")
    logger.shipping("Package shipped: tracking #ABC123")
    logger.payment("Payment processed: $99.99")
    logger.order("Order completed: #12345")

    print()


def example_13_opt_in_library():
    """Example 13: opt() for library development"""
    print("=" * 60)
    print("Example 13: opt() for Library Development")
    print("=" * 60)

    logger = Logger()
    logger.add(sys.stdout, level="INFO", format="{file}:{line} | {message}")

    def library_function():
        """Library function that uses opt for proper attribution"""
        # Using opt(depth=1) so logs show caller's location, not this function
        logger.opt(depth=1).info("Library operation completed")

    def user_code():
        """User's code calling the library"""
        library_function()

    user_code()

    print()


def example_14_error_recovery():
    """Example 14: Error recovery with catch"""
    print("=" * 60)
    print("Example 14: Error Recovery with Fallback")
    print("=" * 60)

    logger = Logger()
    logger.add(sys.stdout, level="INFO", format="{level} | {message}")

    def fallback_handler(exception):
        """Fallback when error occurs"""
        print(f"Fallback: Using default configuration due to {type(exception).__name__}")

    @logger.catch(message="Failed to load config", onerror=fallback_handler)
    def load_config(path):
        """Load configuration file"""
        raise FileNotFoundError(f"Config file not found: {path}")
        # Would normally return config

    config = load_config("/path/to/config.json")
    print(f"Config loaded: {config}")  # None, but app continues

    print()


def main():
    """Run all examples"""
    examples = [
        example_1_catch_basic,
        example_2_catch_with_options,
        example_3_catch_reraise,
        example_4_catch_with_callback,
        example_5_opt_with_exception,
        example_6_opt_with_depth,
        example_7_add_custom_level,
        example_8_custom_level_with_handler,
        example_9_disable_enable,
        example_10_practical_catch_usage,
        example_11_combined_opt_and_catch,
        example_12_custom_logger_subclass,
        example_13_opt_in_library,
        example_14_error_recovery,
    ]

    for example in examples:
        example()
        input("Press Enter to continue to next example...")
        print("\n\n")


if __name__ == "__main__":
    main()
