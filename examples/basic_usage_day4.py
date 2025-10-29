"""
Basic usage example for MyLogger (Day 4)

This example demonstrates the basic logging functionality implemented in Day 4:
- Basic logging methods (trace, debug, info, success, warning, error, critical)
- Message formatting with positional arguments
- Message formatting with named arguments
- Message formatting with mixed arguments
- Extra context via kwargs
- The public log() method with string and numeric levels
"""

import sys
import os

# Add parent directory to path to import mylogger
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from mylogger import logger


def main():
    print("=" * 60)
    print("MyLogger - Basic Usage Examples (Day 4)")
    print("=" * 60)
    print()

    # 1. Basic logging at different levels
    print("1. Basic Logging:")
    print("-" * 40)
    logger.trace("This is a trace message - lowest level")
    logger.debug("This is a debug message - for debugging")
    logger.info("This is an info message - general information")
    logger.success("This is a success message - operation succeeded!")
    logger.warning("This is a warning - something to be aware of")
    logger.error("This is an error - something went wrong")
    logger.critical("This is critical - urgent attention needed!")
    print()

    # 2. Message formatting with positional arguments
    print("2. Positional Argument Formatting:")
    print("-" * 40)
    name = "Alice"
    logger.info("User {} logged in", name)
    logger.info("Processing {} items from {}", 42, "database")
    logger.success("Completed task {} in {} seconds", "backup", 3.14)
    print()

    # 3. Message formatting with named arguments
    print("3. Named Argument Formatting:")
    print("-" * 40)
    logger.info("User {username} logged in", username="bob")
    logger.info("Order #{order_id} for ${amount:.2f}", order_id=12345, amount=99.99)
    logger.warning("Disk usage at {percent}% on {device}", percent=85, device="/dev/sda1")
    print()

    # 4. Mixed argument formatting
    print("4. Mixed Argument Formatting:")
    print("-" * 40)
    logger.info("User {} from {city}", "Charlie", city="New York")
    logger.success("Processed {} records for {user_type} users", 150, user_type="premium")
    print()

    # 5. Extra context via kwargs
    print("5. Extra Context (available in LogRecord):")
    print("-" * 40)
    logger.info("User logged in", user_id=123, session_id="abc-123", ip="192.168.1.1")
    logger.error("Failed to connect to database", error_code=500, retry_count=3, timeout=30)
    print()

    # 6. Using the log() method
    print("6. Using log() Method:")
    print("-" * 40)
    # With string level names
    logger.log("INFO", "Using log() with string level")
    logger.log("ERROR", "Error message via log() method")

    # With numeric level values
    logger.log(10, "DEBUG level (10)")
    logger.log(20, "INFO level (20)")
    logger.log(40, "ERROR level (40)")
    print()

    # 7. Error handling
    print("7. Graceful Error Handling:")
    print("-" * 40)
    # Missing arguments are handled gracefully
    logger.info("User {} from {}", "Dave")  # Missing second arg

    # Missing kwargs are handled gracefully
    logger.info("User {name} from {city}", name="Eve")  # Missing city

    # Invalid levels raise errors
    try:
        logger.log("INVALID_LEVEL", "This will fail")
    except Exception as e:
        print(f"Caught expected error: {type(e).__name__}")
    print()

    # 8. Real-world example
    print("8. Real-World Example:")
    print("-" * 40)

    def process_user_request(user_id, action):
        logger.info("Processing request", user_id=user_id, action=action)

        try:
            # Simulate some processing
            if action == "delete":
                raise PermissionError("User does not have delete permission")

            logger.success(
                "Request completed successfully", user_id=user_id, action=action, duration_ms=42
            )
        except PermissionError as e:
            logger.error("Request failed: {}", str(e), user_id=user_id, action=action, exception=e)

    process_user_request(user_id=100, action="read")
    process_user_request(user_id=200, action="delete")
    print()

    print("=" * 60)
    print("Note: Currently logs are output to stderr with basic formatting.")
    print("Full formatting, colors, and handlers will be added in Days 5-9.")
    print("=" * 60)


if __name__ == "__main__":
    main()
