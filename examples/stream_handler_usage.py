"""
StreamHandler Usage Examples

This module demonstrates various ways to use the StreamHandler
for console and stream-based output.
"""

import sys
import io
from mylogger.handler import StreamHandler
from mylogger.formatter import Formatter
from mylogger.record import LogRecord, FileInfo, ProcessInfo, ThreadInfo
from mylogger import level as levels
from datetime import datetime, timedelta


def create_sample_record(level, message):
    """Helper to create a sample log record"""
    return LogRecord(
        elapsed=timedelta(seconds=1.5),
        exception=None,
        extra={},
        file=FileInfo(name="app.py", path="/home/user/app.py"),
        function="main",
        level=level,
        line=42,
        message=message,
        module="app",
        name="myapp",
        process=ProcessInfo(id=1234, name="python"),
        thread=ThreadInfo(id=5678, name="MainThread"),
        time=datetime.now()
    )


def example_1_basic_stdout():
    """Example 1: Basic output to stdout"""
    print("\n=== Example 1: Basic stdout ===")
    
    # Create a simple formatter
    formatter = Formatter("{time:HH:mm:ss} | {level.name} | {message}")
    
    # Create handler for stdout
    handler = StreamHandler(sys.stdout, levels.INFO, formatter)
    
    # Emit some records
    handler.emit(create_sample_record(levels.INFO, "Application started"))
    handler.emit(create_sample_record(levels.SUCCESS, "Database connected"))
    handler.emit(create_sample_record(levels.WARNING, "Cache miss"))
    
    # Clean up
    handler.close()


def example_2_stderr_for_errors():
    """Example 2: Using stderr for errors"""
    print("\n=== Example 2: stderr for errors ===")
    
    # Create formatter with more detail for errors
    error_formatter = Formatter(
        "{time:HH:mm:ss.SSS} | {level.name: <8} | {name}:{function}:{line} | {message}"
    )
    
    # Create handler for stderr (errors only)
    error_handler = StreamHandler(sys.stderr, levels.ERROR, error_formatter)
    
    # These will be emitted to stderr
    error_handler.emit(create_sample_record(levels.ERROR, "Failed to connect to database"))
    error_handler.emit(create_sample_record(levels.CRITICAL, "System out of memory"))
    
    # This will be filtered out (below ERROR level)
    error_handler.emit(create_sample_record(levels.WARNING, "This won't appear"))
    
    # Clean up
    error_handler.close()


def example_3_custom_stream():
    """Example 3: Writing to a custom stream (StringIO)"""
    print("\n=== Example 3: Custom stream (StringIO) ===")
    
    # Create a StringIO stream for in-memory buffering
    stream = io.StringIO()
    
    formatter = Formatter("{level.name} - {message}")
    handler = StreamHandler(stream, levels.DEBUG, formatter)
    
    # Emit records
    handler.emit(create_sample_record(levels.DEBUG, "Debug information"))
    handler.emit(create_sample_record(levels.INFO, "Process started"))
    handler.emit(create_sample_record(levels.SUCCESS, "Task completed"))
    
    # Get the buffered output
    output = stream.getvalue()
    print("Buffered output:")
    print(output)
    
    # Clean up
    handler.close()


def example_4_colorization():
    """Example 4: Colorization control"""
    print("\n=== Example 4: Colorization ===")
    
    formatter = Formatter("{level.name} | {message}")
    
    # Explicitly enable colorization (for TTY)
    handler_color = StreamHandler(
        sys.stdout,
        levels.INFO,
        formatter,
        colorize=True
    )
    
    # Explicitly disable colorization
    handler_no_color = StreamHandler(
        sys.stdout,
        levels.INFO,
        formatter,
        colorize=False
    )
    
    print("\nWith colorization enabled:")
    handler_color.emit(create_sample_record(levels.INFO, "Colorized output"))
    
    print("\nWith colorization disabled:")
    handler_no_color.emit(create_sample_record(levels.INFO, "Plain output"))
    
    # Clean up
    handler_color.close()
    handler_no_color.close()


def example_5_custom_filter():
    """Example 5: Using a custom filter function"""
    print("\n=== Example 5: Custom filter ===")
    
    # Filter that only allows messages containing "important"
    def important_filter(record):
        return "important" in record.message.lower()
    
    formatter = Formatter("{level.name} | {message}")
    handler = StreamHandler(
        sys.stdout,
        levels.DEBUG,
        formatter,
        filter_func=important_filter
    )
    
    # Only the "important" message will be shown
    handler.emit(create_sample_record(levels.INFO, "Regular message"))
    handler.emit(create_sample_record(levels.INFO, "This is IMPORTANT"))
    handler.emit(create_sample_record(levels.WARNING, "Important warning"))
    handler.emit(create_sample_record(levels.INFO, "Another regular message"))
    
    # Clean up
    handler.close()


def example_6_multiple_handlers():
    """Example 6: Multiple handlers for different purposes"""
    print("\n=== Example 6: Multiple handlers ===")
    
    # Handler 1: Info and above to stdout
    info_formatter = Formatter("{level.name} | {message}")
    info_handler = StreamHandler(sys.stdout, levels.INFO, info_formatter)
    
    # Handler 2: Debug to a StringIO buffer
    debug_formatter = Formatter("[DEBUG] {time:HH:mm:ss} - {message}")
    debug_stream = io.StringIO()
    debug_handler = StreamHandler(debug_stream, levels.DEBUG, debug_formatter)
    
    # Emit records to both handlers
    records = [
        create_sample_record(levels.DEBUG, "Debug: Loading configuration"),
        create_sample_record(levels.INFO, "Application started"),
        create_sample_record(levels.DEBUG, "Debug: Initializing modules"),
        create_sample_record(levels.WARNING, "Configuration file not found"),
    ]
    
    print("\nStdout output (INFO and above):")
    for record in records:
        info_handler.emit(record)
        debug_handler.emit(record)
    
    print("\nDebug buffer output (all levels):")
    print(debug_stream.getvalue())
    
    # Clean up
    info_handler.close()
    debug_handler.close()


def example_7_different_formats():
    """Example 7: Different formats for different streams"""
    print("\n=== Example 7: Different formats ===")
    
    # Compact format for stdout
    compact_formatter = Formatter("{level.name} | {message}")
    stdout_handler = StreamHandler(sys.stdout, levels.INFO, compact_formatter)
    
    # Detailed format for a buffer
    detailed_formatter = Formatter(
        "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
        "{level.name: <8} | "
        "{name}:{function}:{line} | "
        "{message}"
    )
    buffer = io.StringIO()
    buffer_handler = StreamHandler(buffer, levels.INFO, detailed_formatter)
    
    # Emit the same record to both handlers
    record = create_sample_record(levels.INFO, "Processing request")
    
    print("\nCompact format (stdout):")
    stdout_handler.emit(record)
    
    buffer_handler.emit(record)
    print("\nDetailed format (buffer):")
    print(buffer.getvalue())
    
    # Clean up
    stdout_handler.close()
    buffer_handler.close()


def example_8_level_filtering():
    """Example 8: Level-based filtering"""
    print("\n=== Example 8: Level filtering ===")
    
    formatter = Formatter("{level.name: <8} | {message}")
    
    # Handler that only shows WARNING and above
    handler = StreamHandler(sys.stdout, levels.WARNING, formatter)
    
    # Try to emit various levels
    test_records = [
        (levels.TRACE, "This is TRACE - won't show"),
        (levels.DEBUG, "This is DEBUG - won't show"),
        (levels.INFO, "This is INFO - won't show"),
        (levels.WARNING, "This is WARNING - will show"),
        (levels.ERROR, "This is ERROR - will show"),
        (levels.CRITICAL, "This is CRITICAL - will show"),
    ]
    
    print("\nOnly WARNING and above:")
    for level, message in test_records:
        handler.emit(create_sample_record(level, message))
    
    # Clean up
    handler.close()


def example_9_file_like_object():
    """Example 9: Using any file-like object"""
    print("\n=== Example 9: File-like object ===")
    
    # Custom file-like object that collects messages
    class MessageCollector:
        def __init__(self):
            self.messages = []
        
        def write(self, text):
            self.messages.append(text)
        
        def flush(self):
            pass  # Nothing to flush for our collector
        
        def isatty(self):
            return False  # Not a TTY
    
    # Use the collector as a stream
    collector = MessageCollector()
    formatter = Formatter("{level.name} - {message}")
    handler = StreamHandler(collector, levels.INFO, formatter)
    
    # Emit some records
    handler.emit(create_sample_record(levels.INFO, "First message"))
    handler.emit(create_sample_record(levels.WARNING, "Second message"))
    handler.emit(create_sample_record(levels.ERROR, "Third message"))
    
    # Display collected messages
    print("\nCollected messages:")
    for i, msg in enumerate(collector.messages, 1):
        print(f"  {i}. {msg.strip()}")
    
    # Clean up
    handler.close()


def main():
    """Run all examples"""
    print("=" * 60)
    print("StreamHandler Usage Examples")
    print("=" * 60)
    
    example_1_basic_stdout()
    example_2_stderr_for_errors()
    example_3_custom_stream()
    example_4_colorization()
    example_5_custom_filter()
    example_6_multiple_handlers()
    example_7_different_formats()
    example_8_level_filtering()
    example_9_file_like_object()
    
    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()

