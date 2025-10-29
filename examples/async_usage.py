"""
Async Support Usage Examples (Day 17)

This example demonstrates:
1. Basic async/non-blocking logging
2. Queue management and overflow strategies
3. Performance benefits of async logging
4. Practical use cases
"""

import sys
import time
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from mylogger import Logger


def example_1_basic_async():
    """Example 1: Basic async logging"""
    print("=" * 60)
    print("Example 1: Basic Async Logging")
    print("=" * 60)
    
    logger = Logger()
    
    # Add async handler with enqueue=True
    logger.add(sys.stdout, level="INFO", format="{message}", enqueue=True)
    
    # Log messages - these return immediately without waiting for I/O
    logger.info("Message 1")
    logger.info("Message 2")
    logger.info("Message 3")
    
    # Give time for async processing
    time.sleep(0.2)
    
    print("\nAll messages logged asynchronously!")
    
    # Cleanup
    logger.remove()
    print()


def example_2_performance_comparison():
    """Example 2: Performance comparison - sync vs async"""
    print("=" * 60)
    print("Example 2: Performance Comparison")
    print("=" * 60)
    
    # Simulate slow I/O with a callable
    def slow_sink(message):
        """Simulated slow I/O operation"""
        time.sleep(0.05)  # 50ms delay per log
    
    # Synchronous logging
    logger_sync = Logger()
    logger_sync.add(slow_sink, level="INFO", format="{message}", enqueue=False)
    
    start_time = time.time()
    for i in range(10):
        logger_sync.info(f"Sync message {i}")
    sync_time = time.time() - start_time
    logger_sync.remove()
    
    print(f"Synchronous logging (10 messages): {sync_time:.3f}s")
    
    # Asynchronous logging
    logger_async = Logger()
    logger_async.add(slow_sink, level="INFO", format="{message}", enqueue=True)
    
    start_time = time.time()
    for i in range(10):
        logger_async.info(f"Async message {i}")
    async_time = time.time() - start_time
    
    print(f"Asynchronous logging (10 messages): {async_time:.3f}s")
    print(f"Speedup: {sync_time / async_time:.1f}x faster!")
    
    # Give async handler time to finish
    time.sleep(1.0)
    logger_async.remove()
    
    print()


def example_3_file_async():
    """Example 3: Async file logging"""
    print("=" * 60)
    print("Example 3: Async File Logging")
    print("=" * 60)
    
    logger = Logger()
    
    # Add async file handler
    logger.add(
        "logs/async_example.log",
        level="INFO",
        format="{time} | {level} | {message}",
        enqueue=True  # Non-blocking file writes
    )
    
    # Log many messages quickly
    print("Logging 100 messages asynchronously...")
    start_time = time.time()
    
    for i in range(100):
        logger.info(f"Async log entry {i}")
    
    elapsed = time.time() - start_time
    print(f"Logged 100 messages in {elapsed:.3f}s (non-blocking)")
    
    # Give time for background writing
    print("Waiting for background writes to complete...")
    time.sleep(0.5)
    
    logger.remove()
    print("File writing complete!")
    print()


def example_4_queue_overflow_block():
    """Example 4: Queue overflow - block strategy"""
    print("=" * 60)
    print("Example 4: Queue Overflow - Block Strategy")
    print("=" * 60)
    
    logger = Logger()
    
    # Small queue that blocks when full
    logger.add(
        sys.stdout,
        level="INFO",
        format="{message}",
        enqueue=True,
        max_queue_size=5,  # Small queue
        overflow_strategy='block'  # Block until space available
    )
    
    print("Logging with small queue (block strategy)...")
    
    # Log many messages - will block if queue fills up
    for i in range(20):
        logger.info(f"Message {i}")
    
    print("All messages queued (some blocked until space available)")
    
    # Give time to process
    time.sleep(0.5)
    logger.remove()
    print()


def example_5_queue_overflow_drop():
    """Example 5: Queue overflow - drop strategy"""
    print("=" * 60)
    print("Example 5: Queue Overflow - Drop Strategy")
    print("=" * 60)
    
    # Create a very slow sink to demonstrate dropping
    def very_slow_sink(message):
        time.sleep(0.5)  # Very slow
        print(message)
    
    logger = Logger()
    
    # Small queue that drops messages when full
    logger.add(
        very_slow_sink,
        level="INFO",
        format="{message}",
        enqueue=True,
        max_queue_size=2,  # Very small queue
        overflow_strategy='drop'  # Drop messages when full
    )
    
    print("Logging with very small queue (drop strategy)...")
    print("Some messages will be dropped due to slow processing\n")
    
    # Log many messages quickly - some will be dropped
    for i in range(10):
        logger.info(f"Message {i}")
    
    # Give time to process
    time.sleep(2.0)
    
    print("\nSome messages were dropped to prevent blocking")
    logger.remove()
    print()


def example_6_multiple_async_handlers():
    """Example 6: Multiple async handlers"""
    print("=" * 60)
    print("Example 6: Multiple Async Handlers")
    print("=" * 60)
    
    logger = Logger()
    
    # Add multiple async handlers
    logger.add(sys.stdout, level="INFO", format="[CONSOLE] {message}", enqueue=True)
    logger.add("logs/async_file1.log", level="DEBUG", enqueue=True)
    logger.add("logs/async_file2.log", level="WARNING", enqueue=True)
    
    # Log messages - all handlers process asynchronously
    logger.debug("Debug message (file1 only)")
    logger.info("Info message (console + file1)")
    logger.warning("Warning message (all handlers)")
    logger.error("Error message (all handlers)")
    
    # Give time for async processing
    time.sleep(0.3)
    
    logger.remove()
    print("\nMultiple async handlers completed!")
    print()


def example_7_mixed_sync_async():
    """Example 7: Mixed sync and async handlers"""
    print("=" * 60)
    print("Example 7: Mixed Sync and Async Handlers")
    print("=" * 60)
    
    logger = Logger()
    
    # Sync handler for console (immediate feedback)
    logger.add(sys.stdout, level="INFO", format="[SYNC] {message}", enqueue=False)
    
    # Async handler for file (non-blocking I/O)
    logger.add("logs/async_mixed.log", level="INFO", enqueue=True)
    
    print("Logging with mixed sync/async handlers...")
    
    for i in range(5):
        logger.info(f"Message {i}")
    
    # Sync messages appear immediately, async writes happen in background
    time.sleep(0.2)
    
    logger.remove()
    print()


def example_8_graceful_shutdown():
    """Example 8: Graceful shutdown with queue flush"""
    print("=" * 60)
    print("Example 8: Graceful Shutdown")
    print("=" * 60)
    
    logger = Logger()
    
    # Add async handler
    handler_id = logger.add(
        sys.stdout,
        level="INFO",
        format="{message}",
        enqueue=True
    )
    
    # Log messages
    for i in range(10):
        logger.info(f"Message {i}")
    
    print("\nRemoving handler (will flush queue)...")
    
    # Remove handler - automatically flushes remaining messages
    logger.remove(handler_id)
    
    print("Handler removed, all messages flushed!")
    print()


def example_9_high_volume_logging():
    """Example 9: High-volume logging scenario"""
    print("=" * 60)
    print("Example 9: High-Volume Logging")
    print("=" * 60)
    
    logger = Logger()
    
    # Async handler for high-volume logging
    logger.add(
        "logs/high_volume.log",
        level="INFO",
        format="{time} | {message}",
        enqueue=True,
        max_queue_size=1000  # Large queue for bursts
    )
    
    print("Logging 1000 messages...")
    start_time = time.time()
    
    for i in range(1000):
        logger.info(f"High volume message {i}")
    
    elapsed = time.time() - start_time
    print(f"Queued 1000 messages in {elapsed:.3f}s")
    print("Background thread is processing...")
    
    # Give time to process
    time.sleep(1.0)
    
    logger.remove()
    print("Processing complete!")
    print()


def example_10_async_with_rotation():
    """Example 10: Async logging with file rotation"""
    print("=" * 60)
    print("Example 10: Async with File Rotation")
    print("=" * 60)
    
    logger = Logger()
    
    # Async handler with rotation
    logger.add(
        "logs/rotating_async.log",
        level="INFO",
        format="{message}",
        enqueue=True,
        rotation="1 KB",  # Rotate when 1KB
        retention=3  # Keep 3 files
    )
    
    print("Logging with async rotation...")
    
    # Log enough to trigger rotation
    for i in range(100):
        logger.info(f"Message {i} with some padding to increase file size")
    
    # Give time for rotation to happen in background
    time.sleep(0.5)
    
    logger.remove()
    print("Async logging with rotation complete!")
    print()


def example_11_async_error_handling():
    """Example 11: Error handling in async mode"""
    print("=" * 60)
    print("Example 11: Error Handling in Async Mode")
    print("=" * 60)
    
    def sometimes_failing_sink(message):
        """Sink that occasionally fails"""
        import random
        if random.random() < 0.3:  # 30% chance of failure
            raise RuntimeError("Simulated error")
        print(message)
    
    logger = Logger()
    
    # Async handler with error-prone sink
    logger.add(
        sometimes_failing_sink,
        level="INFO",
        format="{message}",
        enqueue=True
    )
    
    print("Logging with error-prone sink (errors handled gracefully)...")
    
    for i in range(10):
        logger.info(f"Message {i}")
    
    # Give time to process
    time.sleep(0.5)
    
    logger.remove()
    print("\nErrors were handled, logging continued!")
    print()


def example_12_practical_web_app():
    """Example 12: Practical usage in web application"""
    print("=" * 60)
    print("Example 12: Practical Web Application Logging")
    print("=" * 60)
    
    logger = Logger()
    
    # Console for development (sync for immediate feedback)
    logger.add(sys.stdout, level="INFO", format="[CONSOLE] {message}", enqueue=False)
    
    # File for all logs (async for performance)
    logger.add(
        "logs/webapp.log",
        level="DEBUG",
        format="{time} | {level} | {message}",
        enqueue=True,
        rotation="10 MB"
    )
    
    # Error file (async, but important errors)
    logger.add(
        "logs/webapp_errors.log",
        level="ERROR",
        format="{time} | {level} | {message}",
        enqueue=True
    )
    
    # Simulate web requests
    print("Simulating web application requests...\n")
    
    for request_id in range(5):
        logger.info(f"Request {request_id} received")
        logger.debug(f"Processing request {request_id}")
        
        if request_id == 3:
            logger.error(f"Request {request_id} failed")
        else:
            logger.info(f"Request {request_id} completed")
    
    # Give time for async writes
    time.sleep(0.3)
    
    logger.remove()
    print("\nWeb application logging complete!")
    print()


def main():
    """Run all examples"""
    examples = [
        example_1_basic_async,
        example_2_performance_comparison,
        example_3_file_async,
        example_4_queue_overflow_block,
        example_5_queue_overflow_drop,
        example_6_multiple_async_handlers,
        example_7_mixed_sync_async,
        example_8_graceful_shutdown,
        example_9_high_volume_logging,
        example_10_async_with_rotation,
        example_11_async_error_handling,
        example_12_practical_web_app,
    ]
    
    for example in examples:
        example()
        input("Press Enter to continue to next example...")
        print("\n\n")


if __name__ == "__main__":
    # Create logs directory if it doesn't exist
    Path("logs").mkdir(exist_ok=True)
    main()

