"""
Colorizer Usage Examples

This module demonstrates various ways to use the Colorizer
for colored console output.
"""

import sys
import os
from mylogger.formatter import Colorizer, Formatter
from mylogger.handler import StreamHandler
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
        time=datetime.now(),
    )


def example_1_basic_colors():
    """Example 1: Basic color application"""
    print("\n=== Example 1: Basic Colors ===\n")

    colorizer = Colorizer()

    # Apply different colors
    print(colorizer.colorize("Red text", "red"))
    print(colorizer.colorize("Green text", "green"))
    print(colorizer.colorize("Blue text", "blue"))
    print(colorizer.colorize("Yellow text", "yellow"))
    print(colorizer.colorize("Cyan text", "cyan"))
    print(colorizer.colorize("Magenta text", "magenta"))
    print(colorizer.colorize("White text", "white"))


def example_2_combined_styles():
    """Example 2: Combined color styles"""
    print("\n=== Example 2: Combined Styles ===\n")

    colorizer = Colorizer()

    # Bold colors
    print(colorizer.colorize("Bold red", "bold+red"))
    print(colorizer.colorize("Bold green", "bold+green"))
    print(colorizer.colorize("Bold blue", "bold+blue"))

    print()

    # Dim colors
    print(colorizer.colorize("Dim red", "dim+red"))
    print(colorizer.colorize("Dim cyan", "dim+cyan"))

    print()

    # Other styles
    print(colorizer.colorize("Italic yellow", "italic+yellow"))
    print(colorizer.colorize("Underline magenta", "underline+magenta"))


def example_3_level_colors():
    """Example 3: Level-based coloring"""
    print("\n=== Example 3: Level Colors ===\n")

    colorizer = Colorizer()

    # Apply colors based on log levels
    print(colorizer.colorize_level("TRACE: Detailed trace message", "TRACE"))
    print(colorizer.colorize_level("DEBUG: Debug information", "DEBUG"))
    print(colorizer.colorize_level("INFO: General information", "INFO"))
    print(colorizer.colorize_level("SUCCESS: Operation completed", "SUCCESS"))
    print(colorizer.colorize_level("WARNING: Warning message", "WARNING"))
    print(colorizer.colorize_level("ERROR: Error occurred", "ERROR"))
    print(colorizer.colorize_level("CRITICAL: Critical failure", "CRITICAL"))


def example_4_strip_colors():
    """Example 4: Stripping colors"""
    print("\n=== Example 4: Strip Colors ===\n")

    colorizer = Colorizer()

    # Create colored text
    colored = colorizer.colorize("This is colored text", "green")
    print("Colored:", colored)

    # Strip colors
    stripped = colorizer.strip_colors(colored)
    print("Stripped:", stripped)

    print()

    # Multiple colors
    multi_colored = (
        colorizer.colorize("Red", "red")
        + " "
        + colorizer.colorize("Green", "green")
        + " "
        + colorizer.colorize("Blue", "blue")
    )
    print("Multi-colored:", multi_colored)
    print("Stripped:", colorizer.strip_colors(multi_colored))


def example_5_formatter_with_colors():
    """Example 5: Formatter with color tags"""
    print("\n=== Example 5: Formatter with Colors ===\n")

    # Create formatter with color tags
    formatter = Formatter(
        "<green>{time:HH:mm:ss}</green> | <level>{level.name: <8}</level> | {message}",
        colorize=True,
    )

    # Create and format records
    records = [
        create_sample_record(levels.INFO, "Application started"),
        create_sample_record(levels.WARNING, "Low memory"),
        create_sample_record(levels.ERROR, "Connection failed"),
        create_sample_record(levels.SUCCESS, "Task completed"),
    ]

    for record in records:
        print(formatter.format(record))


def example_6_formatter_without_colors():
    """Example 6: Formatter without colors"""
    print("\n=== Example 6: Formatter without Colors ===\n")

    # Same format but colors disabled
    formatter = Formatter(
        "<green>{time:HH:mm:ss}</green> | <level>{level.name: <8}</level> | {message}",
        colorize=False,
    )

    records = [
        create_sample_record(levels.INFO, "Application started"),
        create_sample_record(levels.ERROR, "Connection failed"),
    ]

    for record in records:
        print(formatter.format(record))


def example_7_colored_handler():
    """Example 7: StreamHandler with colors"""
    print("\n=== Example 7: StreamHandler with Colors ===\n")

    # Create formatter with colors
    formatter = Formatter(
        "<cyan>{time:HH:mm:ss}</cyan> | "
        "<level>{level.name: <8}</level> | "
        "<level>{message}</level>",
        colorize=True,
    )

    # Create handler for stdout
    handler = StreamHandler(sys.stdout, levels.DEBUG, formatter, colorize=True)

    # Emit records
    records = [
        create_sample_record(levels.DEBUG, "Debug: Loading configuration"),
        create_sample_record(levels.INFO, "Server started on port 8000"),
        create_sample_record(levels.WARNING, "High CPU usage detected"),
        create_sample_record(levels.ERROR, "Failed to connect to database"),
    ]

    for record in records:
        handler.emit(record)

    handler.close()


def example_8_custom_color_scheme():
    """Example 8: Custom color tags"""
    print("\n=== Example 8: Custom Color Tags ===\n")

    formatter = Formatter(
        "<bold>{time:HH:mm:ss}</bold> | "
        "<red>{level.name}</red> | "
        "<blue>{name}</blue>:<blue>{function}</blue>:<blue>{line}</blue> - "
        "<yellow>{message}</yellow>",
        colorize=True,
    )

    record = create_sample_record(levels.INFO, "Custom colored message")
    print(formatter.format(record))


def example_9_no_color_env():
    """Example 9: NO_COLOR environment variable"""
    print("\n=== Example 9: NO_COLOR Environment Variable ===\n")

    colorizer = Colorizer()

    # Check default
    print(f"Colorization enabled (default): {colorizer.should_colorize()}")

    # Set NO_COLOR
    print("\nSetting NO_COLOR=1...")
    os.environ["NO_COLOR"] = "1"

    colorizer2 = Colorizer()
    print(f"Colorization enabled (with NO_COLOR): {colorizer2.should_colorize()}")

    # Clean up
    del os.environ["NO_COLOR"]
    print("\nNO_COLOR removed")


def example_10_all_levels_colored():
    """Example 10: All log levels with colors"""
    print("\n=== Example 10: All Log Levels ===\n")

    formatter = Formatter(
        "<level>{level.name: <8}</level> | <level>{message}</level>", colorize=True
    )

    log_levels = [
        (levels.TRACE, "Trace level message"),
        (levels.DEBUG, "Debug level message"),
        (levels.INFO, "Info level message"),
        (levels.SUCCESS, "Success level message"),
        (levels.WARNING, "Warning level message"),
        (levels.ERROR, "Error level message"),
        (levels.CRITICAL, "Critical level message"),
    ]

    for level, message in log_levels:
        record = create_sample_record(level, message)
        print(formatter.format(record))


def example_11_bright_colors():
    """Example 11: Bright/bold color variants"""
    print("\n=== Example 11: Bright Colors ===\n")

    colorizer = Colorizer()

    # Regular vs bright colors
    print("Regular colors:")
    print(colorizer.colorize("  Red", "red"))
    print(colorizer.colorize("  Green", "green"))
    print(colorizer.colorize("  Blue", "blue"))

    print("\nBright colors:")
    print(colorizer.colorize("  Bright Red", "bright_red"))
    print(colorizer.colorize("  Bright Green", "bright_green"))
    print(colorizer.colorize("  Bright Blue", "bright_blue"))


def example_12_complex_formatting():
    """Example 12: Complex formatted output"""
    print("\n=== Example 12: Complex Formatting ===\n")

    formatter = Formatter(
        "<dim><cyan>{time:YYYY-MM-DD HH:mm:ss.SSS}</cyan></dim> | "
        "<level>{level.name: <8}</level> | "
        "<bold><white>{name}</white></bold>:"
        "<cyan>{function}</cyan>:"
        "<cyan>{line}</cyan> - "
        "<level>{message}</level>",
        colorize=True,
    )

    records = [
        create_sample_record(levels.INFO, "Starting application"),
        create_sample_record(levels.SUCCESS, "Database connected successfully"),
        create_sample_record(levels.WARNING, "Cache size exceeds limit"),
        create_sample_record(levels.ERROR, "Authentication failed"),
    ]

    for record in records:
        print(formatter.format(record))


def main():
    """Run all examples"""
    print("=" * 60)
    print("Colorizer Usage Examples")
    print("=" * 60)

    example_1_basic_colors()
    example_2_combined_styles()
    example_3_level_colors()
    example_4_strip_colors()
    example_5_formatter_with_colors()
    example_6_formatter_without_colors()
    example_7_colored_handler()
    example_8_custom_color_scheme()
    example_9_no_color_env()
    example_10_all_levels_colored()
    example_11_bright_colors()
    example_12_complex_formatting()

    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
