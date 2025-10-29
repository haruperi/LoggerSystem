"""
Handler Management Examples - Day 5

This example demonstrates the handler management features implemented in Day 5:
- Adding handlers (stream, file, callable)
- Multiple output destinations
- Handler removal
- Level filtering
- Custom formats
- Filter functions
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from mylogger import Logger


def example_1_stream_handler():
    """Example 1: Stream handler (console output)"""
    print("\n" + "=" * 70)
    print("Example 1: Stream Handler (Console Output)")
    print("=" * 70)
    
    logger = Logger()
    
    # Add a handler for stderr
    logger.add(sys.stderr, level="INFO")
    
    logger.info("This goes to stderr")
    logger.debug("This won't appear (below INFO level)")
    logger.error("This also goes to stderr")
    
    # Clean up
    logger.remove()


def example_2_file_handler():
    """Example 2: File handler"""
    print("\n" + "=" * 70)
    print("Example 2: File Handler")
    print("=" * 70)
    
    logger = Logger()
    
    # Add a file handler
    logger.add("app.log", level="DEBUG")
    
    logger.debug("Debug message to file")
    logger.info("Info message to file")
    logger.error("Error message to file")
    
    print("Logs written to: app.log")
    
    # Clean up
    logger.remove()


def example_3_multiple_handlers():
    """Example 3: Multiple handlers simultaneously"""
    print("\n" + "=" * 70)
    print("Example 3: Multiple Handlers")
    print("=" * 70)
    
    logger = Logger()
    
    # Add multiple handlers
    h1 = logger.add(sys.stderr, level="WARNING")  # Console: warnings and errors
    h2 = logger.add("debug.log", level="DEBUG")    # File: everything
    h3 = logger.add("errors.log", level="ERROR")   # File: only errors
    
    print(f"Added 3 handlers: {h1}, {h2}, {h3}")
    
    logger.debug("Debug - only to debug.log")
    logger.info("Info - only to debug.log")
    logger.warning("Warning - to console and debug.log")
    logger.error("Error - to all three outputs")
    
    print("Logs written to: debug.log, errors.log, and stderr")
    
    # Clean up
    logger.remove()


def example_4_callable_handler():
    """Example 4: Callable handler"""
    print("\n" + "=" * 70)
    print("Example 4: Callable Handler (Custom Function)")
    print("=" * 70)
    
    logger = Logger()
    
    # Custom function to process logs
    def my_handler(message):
        print(f"[CUSTOM] {message}")
    
    # Add callable handler
    logger.add(my_handler, level="INFO")
    
    logger.info("This will be processed by my_handler")
    logger.error("So will this")
    
    # Clean up
    logger.remove()


def example_5_custom_format():
    """Example 5: Custom format string"""
    print("\n" + "=" * 70)
    print("Example 5: Custom Format Strings")
    print("=" * 70)
    
    logger = Logger()
    
    # Simple format
    format1 = "[{level}] {message}"
    logger.add(sys.stderr, level="INFO", format=format1)
    
    logger.info("Simple format")
    logger.error("Error with simple format")
    
    # Clean up
    logger.remove()
    
    # Detailed format
    format2 = "{time} [{level}] {name}:{function}:{line} - {message}"
    logger.add(sys.stderr, level="INFO", format=format2)
    
    logger.info("Detailed format")
    logger.error("Error with detailed format")
    
    # Clean up
    logger.remove()


def example_6_filter_function():
    """Example 6: Filter functions"""
    print("\n" + "=" * 70)
    print("Example 6: Filter Functions")
    print("=" * 70)
    
    logger = Logger()
    
    # Filter: only log messages containing "important"
    def important_only(record):
        return "important" in record.message.lower()
    
    # Add handler with filter
    logger.add(sys.stderr, level="DEBUG", filter=important_only)
    
    logger.info("Regular message - will be filtered out")
    logger.info("This is an IMPORTANT message - will appear")
    logger.error("Regular error - will be filtered out")
    logger.error("Important: critical error - will appear")
    
    # Clean up
    logger.remove()


def example_7_handler_removal():
    """Example 7: Handler removal"""
    print("\n" + "=" * 70)
    print("Example 7: Handler Removal")
    print("=" * 70)
    
    logger = Logger()
    
    # Add handlers
    h1 = logger.add(sys.stderr, level="INFO")
    h2 = logger.add(lambda msg: None, level="DEBUG")
    
    print(f"Added 2 handlers: {h1}, {h2}")
    
    logger.info("This goes to both handlers")
    
    # Remove one handler
    logger.remove(h1)
    print(f"Removed handler {h1}")
    
    logger.info("This only goes to handler 2 (silent)")
    
    # Remove all remaining handlers
    logger.remove()
    print("Removed all handlers")
    
    # This will go to stderr as fallback (no handlers registered)
    logger.info("Fallback to stderr (no handlers)")


def example_8_real_world():
    """Example 8: Real-world scenario"""
    print("\n" + "=" * 70)
    print("Example 8: Real-World Scenario")
    print("=" * 70)
    
    logger = Logger()
    
    # Setup logging for a web application:
    # - Console: warnings and errors (for monitoring)
    # - File: all logs (for debugging)
    # - Error file: only errors (for alerts)
    # - Custom function: send critical errors to monitoring system
    
    def send_to_monitoring(message):
        print(f"[MONITORING ALERT] {message}")
    
    # Console handler - warnings and errors
    logger.add(sys.stderr, level="WARNING", format="[{level}] {message}")
    
    # Debug file - everything
    logger.add("app_debug.log", level="DEBUG")
    
    # Error file - errors only
    logger.add("app_errors.log", level="ERROR")
    
    # Monitoring - critical only
    logger.add(send_to_monitoring, level="CRITICAL")
    
    # Simulate application logging
    logger.debug("Application started")
    logger.info("User 123 logged in")
    logger.warning("High memory usage detected")
    logger.error("Database connection failed")
    logger.critical("System out of memory!")
    
    print("\nLogs distributed to:")
    print("  - Console: warnings and errors")
    print("  - app_debug.log: all messages")
    print("  - app_errors.log: errors only")
    print("  - Monitoring: critical only")
    
    # Clean up
    logger.remove()


def main():
    """Run all examples"""
    print("\n" + "=" * 70)
    print("MYLOGGER DAY 5 - HANDLER MANAGEMENT EXAMPLES")
    print("=" * 70)
    
    example_1_stream_handler()
    example_2_file_handler()
    example_3_multiple_handlers()
    example_4_callable_handler()
    example_5_custom_format()
    example_6_filter_function()
    example_7_handler_removal()
    example_8_real_world()
    
    print("\n" + "=" * 70)
    print("ALL EXAMPLES COMPLETED")
    print("=" * 70)
    print("\nDay 5 Features Demonstrated:")
    print("  1. StreamHandler - console output")
    print("  2. FileHandler - file output")
    print("  3. Multiple handlers - simultaneous outputs")
    print("  4. CallableHandler - custom functions")
    print("  5. Custom formats - flexible formatting")
    print("  6. Filter functions - selective logging")
    print("  7. Handler removal - dynamic management")
    print("  8. Real-world scenario - production setup")
    print("\nNext: Day 6 will implement advanced formatting with templates and colors!")


if __name__ == "__main__":
    main()

