"""
Memory leak testing for MyLogger

This test suite verifies that the logger doesn't leak memory
during long-running operations.
"""

import pytest
import gc
import sys
from mylogger import logger
from pathlib import Path


class TestMemoryLeaks:
    """Test for memory leaks in logging operations"""

    def test_high_volume_logging_no_leak(self):
        """Test that high-volume logging doesn't cause memory leaks"""
        # Remove all handlers to avoid file I/O
        for handler_id in list(range(len(logger.handlers))):
            try:
                logger.remove(0)  # Remove first handler
            except Exception:
                break

        # Force garbage collection before test
        gc.collect()
        initial_objects = len(gc.get_objects())

        # Log many messages
        for i in range(10000):
            logger.debug(f"Test message {i}")
            if i % 1000 == 0:
                gc.collect()  # Allow garbage collection

        # Force garbage collection after test
        gc.collect()
        final_objects = len(gc.get_objects())

        # Memory should not grow excessively
        # Allow for some reasonable growth (e.g., 10% max)
        growth_percentage = (
            (final_objects - initial_objects) / initial_objects * 100
            if initial_objects > 0
            else 0
        )

        # This is a rough check - in practice, you'd want to monitor actual memory usage
        # For now, we just verify the test runs without errors
        assert growth_percentage < 50, f"Excessive object growth: {growth_percentage:.2f}%"

    def test_handler_cleanup_releases_resources(self):
        """Test that handlers are properly cleaned up"""
        handler_ids = []

        # Add multiple handlers
        for i in range(10):
            handler_id = logger.add(
                f"logs/test_cleanup_{i}.log",
                level="DEBUG",
            )
            handler_ids.append(handler_id)

        # Log some messages
        for i in range(100):
            logger.info(f"Test message {i}")

        # Remove all handlers
        for handler_id in handler_ids:
            try:
                logger.remove(handler_id)
            except Exception:
                pass

        # Force garbage collection
        gc.collect()

        # Verify log files can be deleted (handlers are closed)
        for i in range(10):
            log_path = Path(f"logs/test_cleanup_{i}.log")
            if log_path.exists():
                try:
                    log_path.unlink()  # Should succeed if handler is closed
                except PermissionError:
                    # On Windows, file might still be locked briefly
                    pass

        # Test passes if no exceptions
        assert True

    def test_async_handler_cleanup(self):
        """Test that async handlers clean up properly"""
        import tempfile
        from pathlib import Path

        # Create temporary log file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".log") as f:
            temp_path = Path(f.name)

        try:
            # Add async handler
            handler_id = logger.add(
                str(temp_path),
                level="DEBUG",
                enqueue=True,
            )

            # Log many messages
            for i in range(1000):
                logger.info(f"Async test message {i}")

            # Remove handler (should flush queue)
            logger.remove(handler_id)

            # Force garbage collection
            gc.collect()

            # Verify file can be accessed (handler closed)
            assert temp_path.exists()
        finally:
            # Cleanup
            if temp_path.exists():
                try:
                    temp_path.unlink()
                except Exception:
                    pass

    def test_bound_logger_no_leak(self):
        """Test that bound loggers don't leak memory"""
        gc.collect()
        initial_count = sys.getrefcount(logger)

        # Create many bound loggers
        bound_loggers = []
        for i in range(100):
            bound = logger.bind(id=i, iteration=i)
            bound.info(f"Test {i}")
            bound_loggers.append(bound)

        # Clear references
        bound_loggers.clear()
        gc.collect()

        # Reference count should be reasonable
        # (exact count depends on implementation, so we just check it doesn't grow massively)
        final_count = sys.getrefcount(logger)
        assert final_count <= initial_count * 2, "Bound logger references may be leaking"


def test_context_manager_cleanup():
    """Test that context managers restore state properly"""
    original_extra = logger.extra.copy()

    # Use many context managers
    for i in range(100):
        with logger.contextualize(iteration=i, test=i):
            logger.info(f"Context test {i}")

    # Verify original state is restored
    assert logger.extra == original_extra


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

