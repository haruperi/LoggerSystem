"""
FileHandler Usage Examples

This module demonstrates various ways to use the FileHandler
for file-based logging.
"""

import sys
from pathlib import Path
from mylogger.handler import FileHandler
from mylogger.formatter import Formatter
from mylogger.record import LogRecord, FileInfo, ProcessInfo, ThreadInfo
from mylogger import level as levels
from datetime import datetime, timedelta


def create_sample_record(level, message, extra=None):
    """Helper to create a sample log record"""
    return LogRecord(
        elapsed=timedelta(seconds=1.5),
        exception=None,
        extra=extra or {},
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


def example_1_basic_file_logging():
    """Example 1: Basic file logging"""
    print("\n=== Example 1: Basic File Logging ===")
    
    # Create a simple file handler
    formatter = Formatter("{time:HH:mm:ss} | {level.name} | {message}")
    handler = FileHandler("logs/app.log", levels.INFO, formatter)
    
    # Emit some records
    handler.emit(create_sample_record(levels.INFO, "Application started"))
    handler.emit(create_sample_record(levels.SUCCESS, "Database connected"))
    handler.emit(create_sample_record(levels.WARNING, "Cache miss"))
    handler.emit(create_sample_record(levels.ERROR, "Failed to load config"))
    
    # Clean up
    handler.close()
    
    print("[OK] Logged to logs/app.log")
    print(f"  File size: {Path('logs/app.log').stat().st_size} bytes")


def example_2_append_vs_write_mode():
    """Example 2: Append vs Write mode"""
    print("\n=== Example 2: Append vs Write Mode ===")
    
    formatter = Formatter("{message}")
    
    # Append mode (default) - adds to existing file
    print("\nAppend mode:")
    handler_append = FileHandler("logs/append.log", levels.INFO, formatter, mode='a')
    handler_append.emit(create_sample_record(levels.INFO, "First message"))
    handler_append.close()
    
    handler_append2 = FileHandler("logs/append.log", levels.INFO, formatter, mode='a')
    handler_append2.emit(create_sample_record(levels.INFO, "Second message"))
    handler_append2.close()
    
    append_content = Path("logs/append.log").read_text()
    print(f"  Lines in append.log: {len(append_content.strip().split(chr(10)))}")
    
    # Write mode - overwrites existing file
    print("\nWrite mode:")
    handler_write = FileHandler("logs/write.log", levels.INFO, formatter, mode='w')
    handler_write.emit(create_sample_record(levels.INFO, "First message"))
    handler_write.close()
    
    handler_write2 = FileHandler("logs/write.log", levels.INFO, formatter, mode='w')
    handler_write2.emit(create_sample_record(levels.INFO, "Second message"))
    handler_write2.close()
    
    write_content = Path("logs/write.log").read_text()
    print(f"  Lines in write.log: {len(write_content.strip().split(chr(10)))}")


def example_3_nested_directories():
    """Example 3: Automatic directory creation"""
    print("\n=== Example 3: Nested Directories ===")
    
    # FileHandler automatically creates parent directories
    nested_path = "logs/2024/01/15/application.log"
    formatter = Formatter("{level.name} - {message}")
    handler = FileHandler(nested_path, levels.INFO, formatter)
    
    handler.emit(create_sample_record(levels.INFO, "Nested directory logging"))
    handler.close()
    
    print(f"[OK] Created nested path: {nested_path}")
    print(f"  File exists: {Path(nested_path).exists()}")


def example_4_different_log_levels():
    """Example 4: Separate files for different log levels"""
    print("\n=== Example 4: Separate Files by Level ===")
    
    formatter = Formatter("{time:HH:mm:ss} | {level.name} | {message}")
    
    # Info and above to app.log
    info_handler = FileHandler("logs/app.log", levels.INFO, formatter)
    
    # Errors only to error.log
    error_handler = FileHandler("logs/error.log", levels.ERROR, formatter)
    
    # Debug everything to debug.log
    debug_handler = FileHandler("logs/debug.log", levels.DEBUG, formatter)
    
    # Emit various levels
    records = [
        create_sample_record(levels.DEBUG, "Debug information"),
        create_sample_record(levels.INFO, "Application started"),
        create_sample_record(levels.WARNING, "Low memory warning"),
        create_sample_record(levels.ERROR, "Database connection failed"),
    ]
    
    for record in records:
        info_handler.emit(record)
        error_handler.emit(record)
        debug_handler.emit(record)
    
    # Clean up
    info_handler.close()
    error_handler.close()
    debug_handler.close()
    
    print("[OK] app.log: INFO and above")
    print(f"  Lines: {len(Path('logs/app.log').read_text().strip().split(chr(10)))}")
    print("[OK] error.log: ERROR and above")
    print(f"  Lines: {len(Path('logs/error.log').read_text().strip().split(chr(10)))}")
    print("[OK] debug.log: All levels")
    print(f"  Lines: {len(Path('logs/debug.log').read_text().strip().split(chr(10)))}")


def example_5_custom_formatting():
    """Example 5: Custom log formatting"""
    print("\n=== Example 5: Custom Formatting ===")
    
    # Simple format
    simple_formatter = Formatter("{message}")
    simple_handler = FileHandler("logs/simple.log", levels.INFO, simple_formatter)
    simple_handler.emit(create_sample_record(levels.INFO, "Simple message"))
    simple_handler.close()
    
    # Detailed format
    detailed_formatter = Formatter(
        "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
        "{level.name: <8} | "
        "{process.id} | "
        "{thread.name} | "
        "{name}:{function}:{line} | "
        "{message}"
    )
    detailed_handler = FileHandler("logs/detailed.log", levels.INFO, detailed_formatter)
    detailed_handler.emit(create_sample_record(levels.INFO, "Detailed message"))
    detailed_handler.close()
    
    # JSON-like format
    json_formatter = Formatter(
        '{{"time":"{time:YYYY-MM-DD HH:mm:ss}","level":"{level.name}","message":"{message}"}}'
    )
    json_handler = FileHandler("logs/json.log", levels.INFO, json_formatter)
    json_handler.emit(create_sample_record(levels.INFO, "JSON message"))
    json_handler.close()
    
    print("[OK] simple.log:", Path("logs/simple.log").read_text().strip())
    print("[OK] detailed.log:", Path("logs/detailed.log").read_text().strip()[:60] + "...")
    print("[OK] json.log:", Path("logs/json.log").read_text().strip())


def example_6_with_extra_context():
    """Example 6: Logging with extra context"""
    print("\n=== Example 6: Extra Context ===")
    
    formatter = Formatter(
        "{time:HH:mm:ss} | {level.name} | "
        "User:{extra.user_id} | Request:{extra.request_id} | "
        "{message}"
    )
    handler = FileHandler("logs/context.log", levels.INFO, formatter)
    
    # Emit with context
    handler.emit(create_sample_record(
        levels.INFO,
        "User logged in",
        extra={"user_id": "user123", "request_id": "req-456"}
    ))
    
    handler.emit(create_sample_record(
        levels.INFO,
        "Data processed",
        extra={"user_id": "user456", "request_id": "req-789"}
    ))
    
    handler.close()
    
    print("[OK] Logged with context to logs/context.log")
    content = Path("logs/context.log").read_text()
    print("  Sample:", content.strip().split('\n')[0])


def example_7_custom_filter():
    """Example 7: Filtering log messages"""
    print("\n=== Example 7: Custom Filters ===")
    
    formatter = Formatter("{level.name} | {message}")
    
    # Filter: only "important" messages
    def important_filter(record):
        return "important" in record.message.lower()
    
    handler = FileHandler(
        "logs/important.log",
        levels.DEBUG,
        formatter,
        filter_func=important_filter
    )
    
    # Emit various messages
    handler.emit(create_sample_record(levels.INFO, "Regular startup"))
    handler.emit(create_sample_record(levels.INFO, "Important security update"))
    handler.emit(create_sample_record(levels.ERROR, "Important: Database error"))
    handler.emit(create_sample_record(levels.DEBUG, "Debug information"))
    
    handler.close()
    
    print("[OK] Only 'important' messages logged")
    content = Path("logs/important.log").read_text()
    print(f"  Lines: {len(content.strip().split(chr(10)))}")
    print(f"  Content:\n{content}")


def example_8_unicode_support():
    """Example 8: Unicode and emoji support"""
    print("\n=== Example 8: Unicode Support ===")
    
    formatter = Formatter("{level.name} {level.icon} | {message}")
    handler = FileHandler("logs/unicode.log", levels.INFO, formatter, encoding='utf-8')
    
    # Emit with various unicode characters
    handler.emit(create_sample_record(levels.INFO, "Hello 世界 🌍"))
    handler.emit(create_sample_record(levels.SUCCESS, "Task completed ✓"))
    handler.emit(create_sample_record(levels.ERROR, "Error occurred ⚠️"))
    
    handler.close()
    
    print("[OK] Unicode and emoji logged to logs/unicode.log")
    content = Path("logs/unicode.log").read_text(encoding='utf-8')
    print(f"  {len(content.strip().split(chr(10)))} lines logged with unicode characters")


def example_9_path_object_usage():
    """Example 9: Using Path objects"""
    print("\n=== Example 9: Path Objects ===")
    
    # Using pathlib.Path objects
    log_dir = Path("logs") / "structured"
    log_file = log_dir / "app.log"
    
    formatter = Formatter("{message}")
    handler = FileHandler(log_file, levels.INFO, formatter)
    
    handler.emit(create_sample_record(levels.INFO, "Using Path objects"))
    handler.close()
    
    print(f"[OK] Logged to: {log_file}")
    print(f"  Absolute path: {log_file.absolute()}")
    print(f"  Exists: {log_file.exists()}")


def example_10_multiple_concurrent_handlers():
    """Example 10: Multiple handlers, same file"""
    print("\n=== Example 10: Multiple Handlers, Same File ===")
    
    formatter = Formatter("{level.name} | {message}")
    
    # Two handlers writing to the same file (safe due to locking)
    handler1 = FileHandler("logs/shared.log", levels.INFO, formatter)
    handler2 = FileHandler("logs/shared.log", levels.INFO, formatter)
    
    # Both write to the same file
    handler1.emit(create_sample_record(levels.INFO, "From handler 1"))
    handler2.emit(create_sample_record(levels.INFO, "From handler 2"))
    handler1.emit(create_sample_record(levels.ERROR, "Error from handler 1"))
    handler2.emit(create_sample_record(levels.WARNING, "Warning from handler 2"))
    
    handler1.close()
    handler2.close()
    
    print("[OK] Multiple handlers wrote to logs/shared.log")
    content = Path("logs/shared.log").read_text()
    print(f"  Total lines: {len(content.strip().split(chr(10)))}")


def example_11_production_setup():
    """Example 11: Production-ready setup"""
    print("\n=== Example 11: Production Setup ===")
    
    # Different handlers for different purposes
    
    # 1. General application log
    app_formatter = Formatter(
        "{time:YYYY-MM-DD HH:mm:ss} | {level.name: <8} | {message}"
    )
    app_handler = FileHandler("logs/production/app.log", levels.INFO, app_formatter)
    
    # 2. Detailed debug log
    debug_formatter = Formatter(
        "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level.name: <8} | "
        "{name}:{function}:{line} | {message}"
    )
    debug_handler = FileHandler("logs/production/debug.log", levels.DEBUG, debug_formatter)
    
    # 3. Error log only
    error_formatter = Formatter(
        "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level.name} | "
        "{process.id} | {name}:{function}:{line} | {message}"
    )
    error_handler = FileHandler("logs/production/error.log", levels.ERROR, error_formatter)
    
    # Simulate application activity
    records = [
        create_sample_record(levels.DEBUG, "Application initialized"),
        create_sample_record(levels.INFO, "Server started on port 8000"),
        create_sample_record(levels.INFO, "Database connection established"),
        create_sample_record(levels.WARNING, "High memory usage detected"),
        create_sample_record(levels.ERROR, "Failed to process request"),
        create_sample_record(levels.DEBUG, "Request processed in 150ms"),
    ]
    
    for record in records:
        app_handler.emit(record)
        debug_handler.emit(record)
        error_handler.emit(record)
    
    # Clean up
    app_handler.close()
    debug_handler.close()
    error_handler.close()
    
    print("[OK] Production logs created:")
    print(f"  app.log: {len(Path('logs/production/app.log').read_text().strip().split(chr(10)))} lines")
    print(f"  debug.log: {len(Path('logs/production/debug.log').read_text().strip().split(chr(10)))} lines")
    print(f"  error.log: {len(Path('logs/production/error.log').read_text().strip().split(chr(10)))} lines")


def cleanup_logs():
    """Clean up example log files"""
    import shutil
    logs_dir = Path("logs")
    if logs_dir.exists():
        shutil.rmtree(logs_dir)
    print("\n[OK] Cleaned up log files")


def main():
    """Run all examples"""
    print("=" * 60)
    print("FileHandler Usage Examples")
    print("=" * 60)
    
    example_1_basic_file_logging()
    example_2_append_vs_write_mode()
    example_3_nested_directories()
    example_4_different_log_levels()
    example_5_custom_formatting()
    example_6_with_extra_context()
    example_7_custom_filter()
    example_8_unicode_support()
    example_9_path_object_usage()
    example_10_multiple_concurrent_handlers()
    example_11_production_setup()
    
    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)
    
    # Uncomment to clean up log files
    # cleanup_logs()


if __name__ == "__main__":
    main()

