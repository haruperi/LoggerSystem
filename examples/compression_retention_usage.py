"""
Compression & Retention Examples

This module demonstrates how to use compression and retention features with mylogger.
These features help manage disk space by automatically compressing and cleaning up old log files.
"""

import sys
import os
import time
from pathlib import Path
from datetime import datetime, timedelta
import shutil

# Add parent directory to path to import mylogger
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from mylogger import Logger

# Ensure log directory exists
LOG_DIR = Path("logs_compression_retention_example")
LOG_DIR.mkdir(exist_ok=True)


def example_1_rotation_with_compression():
    """Example 1: Rotate and compress log files automatically"""
    print("\n" + "=" * 70)
    print("Example 1: Rotation with Compression")
    print("=" * 70)
    
    log_file = LOG_DIR / "compressed.log"
    
    log = Logger()
    handler_id = log.add(
        sink=str(log_file),
        level="INFO",
        format="{time:HH:mm:ss} | {level: <8} | {message}",
        rotation="5 KB",        # Rotate when file reaches 5 KB
        compression="gz"        # Compress rotated files with gzip
    )
    
    print(f"Logging to: {log_file}")
    print("Writing messages to trigger rotation and compression...")
    
    # Write enough messages to trigger multiple rotations
    for i in range(300):
        log.info(f"Message {i:04d}: This is some log content to fill up the file.")
        if i % 50 == 0:
            print(f"  ... Wrote {i} messages")
    
    log.remove(handler_id)  # Close the handler
    
    print("\nRotation and compression complete. Checking files:")
    all_files = sorted(list(LOG_DIR.glob("compressed.log*")))
    compressed_files = [f for f in all_files if f.suffix == '.gz']
    
    total_size = 0
    compressed_size = 0
    
    for f in all_files:
        size_kb = f.stat().st_size / 1024
        total_size += f.stat().st_size
        if f.suffix == '.gz':
            compressed_size += f.stat().st_size
        print(f"  - {f.name} ({size_kb:.2f} KB)")
    
    print(f"\nFound {len(compressed_files)} compressed files")
    print(f"Total size: {total_size / 1024:.2f} KB")
    print(f"Compressed files size: {compressed_size / 1024:.2f} KB")
    print(f"\n[OK] Rotation with compression example finished")


def example_2_retention_count_based():
    """Example 2: Keep only N most recent log files"""
    print("\n" + "=" * 70)
    print("Example 2: Count-Based Retention (Keep 3 files)")
    print("=" * 70)
    
    log_file = LOG_DIR / "retention_count.log"
    
    log = Logger()
    handler_id = log.add(
        sink=str(log_file),
        level="INFO",
        format="{time:HH:mm:ss} | {message}",
        rotation="2 KB",        # Rotate every 2 KB
        retention=3             # Keep only 3 most recent files
    )
    
    print(f"Logging to: {log_file}")
    print("Writing messages to trigger rotations...")
    
    # Write many messages to trigger multiple rotations
    for i in range(500):
        log.info(f"Log entry {i:04d} with additional text content")
        if i % 100 == 0:
            print(f"  ... Wrote {i} messages")
    
    log.remove(handler_id)
    
    print("\nRetention cleanup complete. Checking files:")
    remaining_files = sorted(list(LOG_DIR.glob("retention_count.log*")))
    
    for f in remaining_files:
        print(f"  - {f.name} ({f.stat().st_size / 1024:.2f} KB)")
    
    print(f"\n[OK] Should have at most 3 files (current + 2 rotated). Found: {len(remaining_files)}")
    assert len(remaining_files) <= 3, f"Expected <= 3 files, found {len(remaining_files)}"


def example_3_retention_age_based():
    """Example 3: Delete files older than X days (simulated)"""
    print("\n" + "=" * 70)
    print("Example 3: Age-Based Retention (Delete files > 7 days)")
    print("=" * 70)
    
    # Create some "old" files manually for demonstration
    old_file_1 = LOG_DIR / "old.2024-01-01_10-00-00-000000.log"
    old_file_2 = LOG_DIR / "old.2024-01-02_10-00-00-000000.log"
    recent_file = LOG_DIR / "old.log"
    
    old_file_1.write_text("Old content 1")
    old_file_2.write_text("Old content 2")
    recent_file.write_text("Recent content")
    
    # Make the files appear old (8 days ago)
    old_time = (datetime.now() - timedelta(days=8)).timestamp()
    os.utime(old_file_1, (old_time, old_time))
    os.utime(old_file_2, (old_time, old_time))
    
    print(f"Created 2 'old' files and 1 recent file")
    print(f"Files before cleanup:")
    for f in sorted(LOG_DIR.glob("old*.log")):
        age_days = (datetime.now() - datetime.fromtimestamp(f.stat().st_mtime)).days
        print(f"  - {f.name} (age: {age_days} days)")
    
    # Now add a logger with age-based retention
    log = Logger()
    handler_id = log.add(
        sink=str(recent_file),
        level="INFO",
        format="{time:HH:mm:ss} | {message}",
        rotation="1 KB",            # Rotate every 1 KB
        retention="7 days"          # Delete files older than 7 days
    )
    
    # Write a few messages to trigger rotation and retention check
    for i in range(100):
        log.info(f"New log entry {i}")
    
    log.remove(handler_id)
    
    print(f"\nFiles after age-based retention cleanup:")
    remaining_files = sorted(list(LOG_DIR.glob("old*.log")))
    for f in remaining_files:
        age_days = (datetime.now() - datetime.fromtimestamp(f.stat().st_mtime)).days
        print(f"  - {f.name} (age: {age_days} days)")
    
    print(f"\n[OK] Old files should be deleted. Found {len(remaining_files)} files")


def example_4_combined_rotation_compression_retention():
    """Example 4: All features together - Production-ready setup"""
    print("\n" + "=" * 70)
    print("Example 4: Combined Rotation + Compression + Retention")
    print("=" * 70)
    
    log_file = LOG_DIR / "production.log"
    
    log = Logger()
    handler_id = log.add(
        sink=str(log_file),
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
        rotation="10 KB",       # Rotate when file reaches 10 KB
        compression="gz",       # Compress rotated files
        retention=5             # Keep only 5 most recent files
    )
    
    print(f"Logging to: {log_file}")
    print("Production setup: Rotate at 10KB, compress, keep 5 files")
    print("Writing messages...")
    
    # Simulate production logging
    for i in range(1000):
        log.info(f"Production log entry {i:05d} - Important application event with details")
        if i % 200 == 0:
            print(f"  ... Wrote {i} messages")
    
    log.remove(handler_id)
    
    print("\nFinal state:")
    all_files = sorted(list(LOG_DIR.glob("production.log*")))
    
    regular_files = [f for f in all_files if f.suffix == '.log']
    compressed_files = [f for f in all_files if f.suffix == '.gz']
    
    print(f"\nRegular files: {len(regular_files)}")
    for f in regular_files:
        print(f"  - {f.name} ({f.stat().st_size / 1024:.2f} KB)")
    
    print(f"\nCompressed files: {len(compressed_files)}")
    total_compressed_size = 0
    for f in compressed_files:
        size_kb = f.stat().st_size / 1024
        total_compressed_size += f.stat().st_size
        print(f"  - {f.name} ({size_kb:.2f} KB)")
    
    print(f"\nTotal files: {len(all_files)} (should be <= 5 due to retention)")
    print(f"Total compressed size: {total_compressed_size / 1024:.2f} KB")
    print(f"\n[OK] Production example complete")
    assert len(all_files) <= 5, f"Expected <= 5 files, found {len(all_files)}"


def example_5_compression_formats():
    """Example 5: Different compression formats (gzip vs zip)"""
    print("\n" + "=" * 70)
    print("Example 5: Compression Formats Comparison")
    print("=" * 70)
    
    # Test gzip compression
    log_file_gz = LOG_DIR / "test_gz.log"
    log_gz = Logger()
    handler_id_gz = log_gz.add(
        sink=str(log_file_gz),
        level="INFO",
        rotation="5 KB",
        compression="gz"
    )
    
    print("Writing to gzip-compressed logger...")
    for i in range(300):
        log_gz.info(f"Test message {i} with some content")
    log_gz.remove(handler_id_gz)
    
    # Test zip compression
    log_file_zip = LOG_DIR / "test_zip.log"
    log_zip = Logger()
    handler_id_zip = log_zip.add(
        sink=str(log_file_zip),
        level="INFO",
        rotation="5 KB",
        compression="zip"
    )
    
    print("Writing to zip-compressed logger...")
    for i in range(300):
        log_zip.info(f"Test message {i} with some content")
    log_zip.remove(handler_id_zip)
    
    print("\nCompression comparison:")
    
    gz_files = list(LOG_DIR.glob("test_gz*.gz"))
    zip_files = list(LOG_DIR.glob("test_zip*.zip"))
    
    gz_total = sum(f.stat().st_size for f in gz_files)
    zip_total = sum(f.stat().st_size for f in zip_files)
    
    print(f"  Gzip files: {len(gz_files)} files, {gz_total / 1024:.2f} KB total")
    print(f"  Zip files:  {len(zip_files)} files, {zip_total / 1024:.2f} KB total")
    
    if gz_total < zip_total:
        savings = ((zip_total - gz_total) / zip_total) * 100
        print(f"  -> Gzip is {savings:.1f}% smaller (better for log files)")
    else:
        print(f"  -> Results similar")
    
    print(f"\n[OK] Compression formats example complete")


def example_6_manual_retention_check():
    """Example 6: Using Retention class directly to check what would be deleted"""
    print("\n" + "=" * 70)
    print("Example 6: Manual Retention Inspection")
    print("=" * 70)
    
    from mylogger.retention import Retention
    
    # Create some test files
    test_dir = LOG_DIR / "retention_test"
    test_dir.mkdir(exist_ok=True)
    
    for i in range(10):
        file = test_dir / f"app.{i:02d}.log"
        file.write_text(f"Content {i}\n" * 100)  # ~1KB each
        time.sleep(0.01)
    
    print(f"Created 10 test files in {test_dir}")
    
    # Inspect with count-based retention
    retention_count = Retention(count=5)
    info = retention_count.get_files_info(test_dir, "app.*.log")
    
    print(f"\nCount-based retention (keep 5):")
    for item in info:
        status = "DELETE" if item['would_delete'] else "KEEP  "
        print(f"  [{status}] {item['path'].name} ({item['size']} bytes)")
    
    # Estimate space that would be freed
    space_freed = retention_count.estimate_space_freed(test_dir, "app.*.log")
    print(f"\nWould free: {space_freed / 1024:.2f} KB")
    
    # Actually perform cleanup
    deleted = retention_count.clean(test_dir, "app.*.log")
    print(f"Deleted: {len(deleted)} files")
    
    remaining = list(test_dir.glob("app.*.log"))
    print(f"Remaining: {len(remaining)} files")
    
    print(f"\n[OK] Manual retention inspection complete")


def example_7_advanced_production_setup():
    """Example 7: Advanced production setup with multiple log files"""
    print("\n" + "=" * 70)
    print("Example 7: Advanced Production Setup")
    print("=" * 70)
    
    app_dir = LOG_DIR / "app_logs"
    app_dir.mkdir(exist_ok=True)
    
    log = Logger()
    
    # Main application log: rotate daily, compress, keep 30 days
    handler_id_1 = log.add(
        sink=str(app_dir / "app.log"),
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
        rotation="daily",
        compression="gz",
        retention="30 days"
    )
    
    # Error log: rotate at 50MB, compress, keep 10 files
    handler_id_2 = log.add(
        sink=str(app_dir / "errors.log"),
        level="ERROR",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
        rotation="50 MB",
        compression="gz",
        retention=10
    )
    
    # Debug log: rotate hourly, compress, keep 24 hours
    handler_id_3 = log.add(
        sink=str(app_dir / "debug.log"),
        level="DEBUG",
        format="{time:HH:mm:ss.SSS} | {level: <8} | {message}",
        rotation="1 hour",
        compression="gz",
        retention="1 day"
    )
    
    print(f"Logging to: {app_dir}")
    print("Setup:")
    print("  - app.log: daily rotation, compressed, 30 days retention")
    print("  - errors.log: 50MB rotation, compressed, keep 10 files")
    print("  - debug.log: hourly rotation, compressed, 24 hours retention")
    print("\nWriting sample messages...")
    
    # Write some sample messages
    for i in range(50):
        log.debug(f"Debug message {i}")
        log.info(f"Info message {i}")
        if i % 10 == 0:
            log.error(f"Error message {i}")
    
    # Clean up
    log.remove(handler_id_1)
    log.remove(handler_id_2)
    log.remove(handler_id_3)
    
    print("\nLog files created:")
    for f in sorted(app_dir.glob("*.log")):
        print(f"  - {f.name} ({f.stat().st_size / 1024:.2f} KB)")
    
    print(f"\n[OK] Advanced production setup example complete")


def main():
    print("=" * 70)
    print("Compression & Retention Examples - MyLogger")
    print("=" * 70)
    
    example_1_rotation_with_compression()
    example_2_retention_count_based()
    example_3_retention_age_based()
    example_4_combined_rotation_compression_retention()
    example_5_compression_formats()
    example_6_manual_retention_check()
    example_7_advanced_production_setup()
    
    print("\n" + "=" * 70)
    print("[OK] All compression and retention examples completed!")
    print("=" * 70)
    
    print(f"\nAll example files are in: {LOG_DIR.absolute()}")
    print("You can inspect the compressed files and retention behavior.")


if __name__ == "__main__":
    main()

