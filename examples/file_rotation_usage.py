"""
Example: File Rotation Usage

This example demonstrates how to use file rotation in mylogger.
File rotation automatically closes, renames, and opens new log files
based on size or time criteria.

Rotation strategies:
1. Size-based: Rotate when file reaches a certain size
2. Time-based: Rotate at specific times or intervals
"""

import time
from mylogger import Logger
from pathlib import Path


def example_1_size_rotation_bytes():
    """Example 1: Size-based rotation with bytes"""
    print("\n" + "=" * 70)
    print("Example 1: Size-Based Rotation (Bytes)")
    print("=" * 70)

    logger = Logger()
    # Rotate when file reaches 1024 bytes (1 KB)
    logger.add("logs/size_bytes.log", level="INFO", rotation=1024)

    print("\nWriting logs... File will rotate when it reaches 1024 bytes")

    # Write enough to trigger rotation
    for i in range(50):
        logger.info(f"Log entry {i:03d} with some text to fill up the file")

    # Check rotated files
    log_dir = Path("logs")
    if log_dir.exists():
        rotated_files = list(log_dir.glob("size_bytes*.log"))
        print(f"\n[Result] Created {len(rotated_files)} log file(s)")
        for f in sorted(rotated_files):
            size = f.stat().st_size
            print(f"  - {f.name}: {size} bytes")


def example_2_size_rotation_string():
    """Example 2: Size-based rotation with human-readable size"""
    print("\n" + "=" * 70)
    print("Example 2: Size-Based Rotation (Human-Readable)")
    print("=" * 70)

    logger = Logger()
    # Rotate when file reaches 5 KB
    logger.add("logs/size_string.log", level="INFO", rotation="5 KB")

    print("\nWriting logs... File will rotate when it reaches 5 KB")

    # Write enough to exceed 5KB
    for i in range(200):
        logger.info(f"Entry {i:04d}: " + "x" * 50)

    # Check results
    log_dir = Path("logs")
    if log_dir.exists():
        rotated_files = list(log_dir.glob("size_string*.log"))
        print(f"\n[Result] Created {len(rotated_files)} log file(s)")
        total_size = sum(f.stat().st_size for f in rotated_files)
        print(f"  Total size: {total_size:,} bytes ({total_size/1024:.1f} KB)")


def example_3_time_rotation_interval():
    """Example 3: Time-based rotation with interval"""
    print("\n" + "=" * 70)
    print("Example 3: Time-Based Rotation (Interval)")
    print("=" * 70)

    logger = Logger()
    # Rotate every 2 seconds (for demo purposes)
    logger.add("logs/time_interval.log", level="INFO", rotation="2 seconds")

    print("\nWriting logs... File will rotate every 2 seconds")

    # Write logs over 5 seconds
    for i in range(10):
        logger.info(f"Message {i+1} at {time.strftime('%H:%M:%S')}")
        time.sleep(0.6)  # 600ms between messages

    # Check results
    log_dir = Path("logs")
    if log_dir.exists():
        rotated_files = sorted(log_dir.glob("time_interval*.log"))
        print(f"\n[Result] Created {len(rotated_files)} log file(s)")
        for f in rotated_files:
            lines = len(f.read_text().splitlines())
            print(f"  - {f.name}: {lines} lines")


def example_4_time_rotation_daily():
    """Example 4: Daily rotation (demonstration)"""
    print("\n" + "=" * 70)
    print("Example 4: Daily Rotation (Set for Midnight)")
    print("=" * 70)

    logger = Logger()
    # Rotate daily at midnight
    logger.add("logs/daily.log", level="INFO", rotation="daily")

    print("\nRotation scheduled for midnight (00:00)")
    print("This file will rotate automatically when the day changes")

    # Write some logs
    logger.info("Application started")
    logger.info("Daily rotation is configured")
    logger.info("Logs will rotate at midnight")

    print("\n[Note] Daily rotation won't trigger in this demo")
    print("       In production, it would rotate at midnight automatically")


def example_5_time_rotation_specific():
    """Example 5: Rotation at specific time"""
    print("\n" + "=" * 70)
    print("Example 5: Rotation at Specific Time")
    print("=" * 70)

    logger = Logger()
    # Rotate at 14:30 (2:30 PM) every day
    logger.add("logs/specific_time.log", level="INFO", rotation="14:30")

    print("\nRotation scheduled for 14:30 (2:30 PM) daily")

    # Write logs
    logger.info("Configured for 14:30 rotation")
    logger.info(f"Current time: {time.strftime('%H:%M:%S')}")

    print("\n[Note] Will rotate when clock reaches 14:30")


def example_6_time_rotation_weekly():
    """Example 6: Weekly rotation"""
    print("\n" + "=" * 70)
    print("Example 6: Weekly Rotation (Mondays)")
    print("=" * 70)

    logger = Logger()
    # Rotate every Monday at midnight
    logger.add("logs/weekly.log", level="INFO", rotation="weekly")

    print("\nRotation scheduled for every Monday at midnight")

    logger.info("Weekly rotation configured")
    logger.info("Logs will rotate every Monday")

    print("\n[Note] Will rotate on Monday at 00:00")


def example_7_multiple_files_different_rotations():
    """Example 7: Multiple log files with different rotation strategies"""
    print("\n" + "=" * 70)
    print("Example 7: Multiple Files with Different Rotations")
    print("=" * 70)

    logger = Logger()

    # Main application log - size-based
    logger.add("logs/app.log", level="INFO", rotation="10 KB")

    # Error log - smaller rotation
    logger.add("logs/errors.log", level="ERROR", rotation="5 KB")

    # Debug log - time-based (hourly)
    logger.add("logs/debug.log", level="DEBUG", rotation="1 hour")

    print("\nConfigured 3 log files with different rotations:")
    print("  1. app.log    - Rotate at 10 KB")
    print("  2. errors.log - Rotate at 5 KB (errors only)")
    print("  3. debug.log  - Rotate every hour (debug and above)")

    # Write various levels
    for i in range(30):
        logger.debug(f"Debug message {i}")
        logger.info(f"Info message {i}")
        if i % 10 == 0:
            logger.error(f"Error message {i}")

    print("\n[Result] Logs written to all three files")


def example_8_rotation_filename_pattern():
    """Example 8: Understanding rotated filename pattern"""
    print("\n" + "=" * 70)
    print("Example 8: Rotated Filename Pattern")
    print("=" * 70)

    logger = Logger()
    logger.add("logs/pattern_demo.log", level="INFO", rotation=500)

    print("\nOriginal file: pattern_demo.log")
    print("Rotated files: pattern_demo.YYYY-MM-DD_HH-MM-SS-microseconds.log")
    print("\nExample rotated filenames:")
    print("  - pattern_demo.2025-10-29_14-30-45-123456.log")
    print("  - pattern_demo.2025-10-29_14-31-12-789012.log")

    # Trigger a few rotations
    for i in range(20):
        logger.info(f"Message {i:03d} " + "x" * 50)

    # Show actual files
    log_dir = Path("logs")
    if log_dir.exists():
        rotated_files = list(log_dir.glob("pattern_demo*.log"))
        print(f"\n[Actual Files] Created {len(rotated_files)} file(s):")
        for f in sorted(rotated_files):
            print(f"  - {f.name}")


def example_9_real_world_production():
    """Example 9: Real-world production configuration"""
    print("\n" + "=" * 70)
    print("Example 9: Real-World Production Configuration")
    print("=" * 70)

    logger = Logger()

    # Application logs - rotate daily, keep organized
    logger.add(
        "logs/production/app.log",
        level="INFO",
        rotation="daily",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
    )

    # Error logs - rotate at 50MB
    logger.add("logs/production/errors.log", level="ERROR", rotation="50 MB")

    # Access logs - rotate every 6 hours
    logger.add(
        "logs/production/access.log",
        level="INFO",
        rotation="6 hours",
        filter=lambda r: r.extra.get("type") == "access",
    )

    print("\nProduction configuration:")
    print("  1. Application logs - Daily rotation")
    print("  2. Error logs - 50 MB rotation")
    print("  3. Access logs - 6-hour rotation (filtered)")

    # Simulate application activity
    logger.info("Application started", app="MyApp", version="1.0.0")
    logger.info("Database connected", db="postgresql", host="localhost")
    logger.info("Request processed", type="access", method="GET", path="/api/users")
    logger.error("Database query failed", error="Connection timeout")
    logger.info("Request processed", type="access", method="POST", path="/api/orders")

    print("\n[Result] Logs written with production configuration")


def example_10_rotation_with_different_extensions():
    """Example 10: Rotation with different file extensions"""
    print("\n" + "=" * 70)
    print("Example 10: Rotation with Different Extensions")
    print("=" * 70)

    logger = Logger()

    # Log files with .txt extension
    logger.add("logs/output.txt", level="INFO", rotation="1 KB")

    print("\nRotation works with any file extension")
    print("Original: output.txt")
    print("Rotated: output.YYYY-MM-DD_HH-MM-SS-microseconds.txt")

    # Write logs
    for i in range(100):
        logger.info(f"Entry {i:03d} with text content")

    # Check files
    log_dir = Path("logs")
    if log_dir.exists():
        txt_files = list(log_dir.glob("output*.txt"))
        print(f"\n[Result] Created {len(txt_files)} .txt file(s)")


def example_11_rotation_comparison():
    """Example 11: Comparison of rotation strategies"""
    print("\n" + "=" * 70)
    print("Example 11: Rotation Strategy Comparison")
    print("=" * 70)

    print("\nRotation Strategy Comparison:\n")

    print("SIZE-BASED ROTATION:")
    print("  Pros:")
    print("    - Predictable file sizes")
    print("    - Good for disk space management")
    print("    - Fast to implement")
    print("  Cons:")
    print("    - Rotation times unpredictable")
    print("    - May rotate during peak times")
    print("  Use when:")
    print("    - Disk space is limited")
    print("    - File size matters more than time")
    print("    - Variable logging rate")

    print("\nTIME-BASED ROTATION:")
    print("  Pros:")
    print("    - Predictable rotation times")
    print("    - Easy to organize by date")
    print("    - Good for log analysis")
    print("  Cons:")
    print("    - File sizes vary")
    print("    - May create very large files")
    print("  Use when:")
    print("    - Time-based analysis needed")
    print("    - Consistent logging rate")
    print("    - Organizing logs by date")

    print("\nRECOMMENDATIONS:")
    print("  - Production apps: Daily rotation (easy to find logs)")
    print("  - High-traffic apps: Size-based (10-100 MB)")
    print("  - Debug logs: Hourly or size-based (small files)")
    print("  - Error logs: Daily or weekly (low volume)")


def cleanup_demo_files():
    """Clean up demonstration log files"""
    import shutil

    log_dir = Path("logs")
    if log_dir.exists():
        try:
            shutil.rmtree(log_dir)
            print("\n[Cleanup] Removed demo log files")
        except Exception as e:
            print(f"\n[Cleanup] Could not remove logs: {e}")


def main():
    """Run all examples"""
    print("\n" + "=" * 70)
    print("File Rotation Examples - MyLogger")
    print("=" * 70)

    # Create logs directory
    Path("logs").mkdir(exist_ok=True)

    try:
        example_1_size_rotation_bytes()
        example_2_size_rotation_string()
        example_3_time_rotation_interval()
        example_4_time_rotation_daily()
        example_5_time_rotation_specific()
        example_6_time_rotation_weekly()
        example_7_multiple_files_different_rotations()
        example_8_rotation_filename_pattern()
        example_9_real_world_production()
        example_10_rotation_with_different_extensions()
        example_11_rotation_comparison()

        print("\n" + "=" * 70)
        print("[OK] All examples completed!")
        print("=" * 70)

    finally:
        # Uncomment to clean up demo files
        cleanup_demo_files()


if __name__ == "__main__":
    main()
