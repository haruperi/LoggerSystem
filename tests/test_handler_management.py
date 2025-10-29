"""
Test handler management for Day 5
"""

import sys
import os
from pathlib import Path
import tempfile

# Add the parent directory to the path to import mylogger
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from mylogger import logger, Logger


def test_add_stream_handler():
    """Test adding a stream handler"""
    print("=" * 60)
    print("TEST 1: Add Stream Handler")
    print("=" * 60)

    # Create a new logger instance
    test_logger = Logger()

    # Add stderr handler
    handler_id = test_logger.add(sys.stderr, level="INFO")
    print(f"Added stream handler with ID: {handler_id}")

    # Test logging
    test_logger.info("This should appear on stderr")
    test_logger.debug("This should NOT appear (below INFO level)")
    test_logger.error("This should appear on stderr")

    # Remove handler
    test_logger.remove(handler_id)
    print("[OK] Stream handler test passed")
    print()


def test_add_file_handler():
    """Test adding a file handler"""
    print("=" * 60)
    print("TEST 2: Add File Handler")
    print("=" * 60)

    # Create a new logger instance
    test_logger = Logger()

    # Create temp file
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".log") as f:
        log_file = f.name

    try:
        # Add file handler
        handler_id = test_logger.add(log_file, level="DEBUG")
        print(f"Added file handler with ID: {handler_id}, file: {log_file}")

        # Test logging
        test_logger.debug("This is a debug message")
        test_logger.info("This is an info message")
        test_logger.error("This is an error message")

        # Remove handler to flush
        test_logger.remove(handler_id)

        # Read and verify
        with open(log_file, "r") as f:
            contents = f.read()
            print(f"File contents:\n{contents}")
            assert "debug message" in contents
            assert "info message" in contents
            assert "error message" in contents

        print("[OK] File handler test passed")

    finally:
        # Cleanup
        if os.path.exists(log_file):
            os.unlink(log_file)

    print()


def test_add_callable_handler():
    """Test adding a callable handler"""
    print("=" * 60)
    print("TEST 3: Add Callable Handler")
    print("=" * 60)

    # Create a new logger instance
    test_logger = Logger()

    # Create a list to capture messages
    messages = []

    def capture_message(msg):
        messages.append(msg)

    # Add callable handler
    handler_id = test_logger.add(capture_message, level="WARNING")
    print(f"Added callable handler with ID: {handler_id}")

    # Test logging
    test_logger.info("This should NOT be captured")
    test_logger.warning("This should be captured")
    test_logger.error("This should also be captured")

    # Verify
    print(f"Captured {len(messages)} messages:")
    for msg in messages:
        print(f"  - {msg}")

    assert len(messages) == 2
    assert "warning" in messages[0].lower()
    assert "error" in messages[1].lower()

    # Remove handler
    test_logger.remove(handler_id)
    print("[OK] Callable handler test passed")
    print()


def test_multiple_handlers():
    """Test multiple handlers simultaneously"""
    print("=" * 60)
    print("TEST 4: Multiple Handlers")
    print("=" * 60)

    # Create a new logger instance
    test_logger = Logger()

    # Create temp file
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".log") as f:
        log_file = f.name

    try:
        # Add multiple handlers
        handler1 = test_logger.add(sys.stderr, level="INFO")
        handler2 = test_logger.add(log_file, level="DEBUG")
        handler3 = test_logger.add(lambda msg: None, level="ERROR")  # Silent handler

        print(f"Added 3 handlers: {handler1}, {handler2}, {handler3}")

        # Test logging
        test_logger.debug("Debug - only to file")
        test_logger.info("Info - to stderr and file")
        test_logger.error("Error - to all handlers")

        # Remove handlers
        test_logger.remove(handler1)
        test_logger.remove(handler2)
        test_logger.remove(handler3)

        # Verify file
        with open(log_file, "r") as f:
            contents = f.read()
            assert "Debug" in contents
            assert "Info" in contents
            assert "Error" in contents

        print("[OK] Multiple handlers test passed")

    finally:
        if os.path.exists(log_file):
            os.unlink(log_file)

    print()


def test_handler_removal():
    """Test handler removal"""
    print("=" * 60)
    print("TEST 5: Handler Removal")
    print("=" * 60)

    # Create a new logger instance
    test_logger = Logger()

    # Add handlers
    h1 = test_logger.add(lambda msg: None, level="INFO")
    h2 = test_logger.add(lambda msg: None, level="DEBUG")
    h3 = test_logger.add(lambda msg: None, level="ERROR")

    print(f"Added 3 handlers: {h1}, {h2}, {h3}")
    print(f"Handler count: {len(test_logger.handlers)}")
    assert len(test_logger.handlers) == 3

    # Remove one
    test_logger.remove(h2)
    print(f"After removing {h2}: {len(test_logger.handlers)} handlers")
    assert len(test_logger.handlers) == 2

    # Remove all
    test_logger.remove()
    print(f"After removing all: {len(test_logger.handlers)} handlers")
    assert len(test_logger.handlers) == 0

    print("[OK] Handler removal test passed")
    print()


def test_handler_level_filtering():
    """Test handler level filtering"""
    print("=" * 60)
    print("TEST 6: Handler Level Filtering")
    print("=" * 60)

    # Create a new logger instance
    test_logger = Logger()

    # Create lists to capture messages
    info_messages = []
    error_messages = []

    # Add handlers with different levels
    h1 = test_logger.add(lambda msg: info_messages.append(msg), level="INFO")
    h2 = test_logger.add(lambda msg: error_messages.append(msg), level="ERROR")

    print(f"Added INFO handler ({h1}) and ERROR handler ({h2})")

    # Test logging
    test_logger.debug("Debug message")
    test_logger.info("Info message")
    test_logger.error("Error message")
    test_logger.critical("Critical message")

    # Verify
    print(f"INFO handler captured: {len(info_messages)} messages")
    print(f"ERROR handler captured: {len(error_messages)} messages")

    assert len(info_messages) == 3  # info, error, critical
    assert len(error_messages) == 2  # error, critical

    # Cleanup
    test_logger.remove()

    print("[OK] Level filtering test passed")
    print()


def test_custom_format():
    """Test custom format strings"""
    print("=" * 60)
    print("TEST 7: Custom Format Strings")
    print("=" * 60)

    # Create a new logger instance
    test_logger = Logger()

    # Create temp file
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".log") as f:
        log_file = f.name

    try:
        # Add handler with custom format
        custom_format = "[{level}] {message} (at {function})"
        handler_id = test_logger.add(log_file, level="INFO", format=custom_format)

        print(f"Added handler with custom format: {custom_format}")

        # Test logging
        test_logger.info("Test message")

        # Remove handler to flush
        test_logger.remove(handler_id)

        # Verify
        with open(log_file, "r") as f:
            contents = f.read()
            print(f"Formatted output: {contents.strip()}")
            assert "[INFO" in contents
            assert "Test message" in contents
            assert "(at test_custom_format)" in contents

        print("[OK] Custom format test passed")

    finally:
        if os.path.exists(log_file):
            os.unlink(log_file)

    print()


def test_filter_function():
    """Test filter functions"""
    print("=" * 60)
    print("TEST 8: Filter Functions")
    print("=" * 60)

    # Create a new logger instance
    test_logger = Logger()

    # Create list to capture messages
    messages = []

    # Filter: only log messages containing "important"
    def important_filter(record):
        return "important" in record.message.lower()

    # Add handler with filter
    handler_id = test_logger.add(
        lambda msg: messages.append(msg), level="DEBUG", filter=important_filter
    )

    print("Added handler with filter: only 'important' messages")

    # Test logging
    test_logger.info("This is a regular message")
    test_logger.info("This is an IMPORTANT message")
    test_logger.error("Regular error")
    test_logger.error("Important error here")

    # Verify
    print(f"Captured {len(messages)} messages (should be 2):")
    for msg in messages:
        print(f"  - {msg}")

    assert len(messages) == 2

    # Cleanup
    test_logger.remove(handler_id)

    print("[OK] Filter function test passed")
    print()


def test_global_logger():
    """Test the global logger instance"""
    print("=" * 60)
    print("TEST 9: Global Logger Instance")
    print("=" * 60)

    from mylogger import logger as global_logger

    # Clean up any existing handlers
    global_logger.remove()

    # Add handler
    messages = []
    handler_id = global_logger.add(lambda msg: messages.append(msg), level="INFO")

    print(f"Added handler to global logger: {handler_id}")

    # Test logging
    global_logger.info("Test from global logger")
    global_logger.warning("Warning from global logger")

    # Verify
    print(f"Global logger captured: {len(messages)} messages")
    assert len(messages) == 2

    # Cleanup
    global_logger.remove(handler_id)

    print("[OK] Global logger test passed")
    print()


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("MYLOGGER DAY 5 - HANDLER MANAGEMENT TESTS")
    print("=" * 60 + "\n")

    test_add_stream_handler()
    test_add_file_handler()
    test_add_callable_handler()
    test_multiple_handlers()
    test_handler_removal()
    test_handler_level_filtering()
    test_custom_format()
    test_filter_function()
    test_global_logger()

    print("=" * 60)
    print("ALL TESTS COMPLETED SUCCESSFULLY")
    print("=" * 60)
    print("\nDay 5 handler management is fully functional!")
    print("- StreamHandler: Console output [OK]")
    print("- FileHandler: File output [OK]")
    print("- CallableHandler: Custom functions [OK]")
    print("- Multiple handlers: [OK]")
    print("- Handler removal: [OK]")
    print("- Level filtering: [OK]")
    print("- Custom formats: [OK]")
    print("- Filter functions: [OK]")


if __name__ == "__main__":
    main()
