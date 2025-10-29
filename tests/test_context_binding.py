"""
Tests for context binding and BoundLogger
"""

import pytest
from io import StringIO

from mylogger import Logger, level as levels
from mylogger.bound_logger import BoundLogger
from mylogger.context_manager import ContextManager


class TestLoggerExtra:
    """Test Logger's global extra dict"""

    def test_logger_has_extra_dict(self):
        """Test that Logger initializes with an empty extra dict"""
        logger = Logger()
        assert hasattr(logger, "extra")
        assert isinstance(logger.extra, dict)
        assert len(logger.extra) == 0

    def test_logger_extra_in_log_record(self):
        """Test that Logger.extra is included in log records"""
        output = StringIO()
        logger = Logger()
        logger.add(output, level="DEBUG", format="{message} | extra: {extra.user_id}")

        # Set global extra
        logger.extra["user_id"] = 12345

        logger.info("Test message")

        result = output.getvalue()
        assert "Test message" in result
        assert "12345" in result

    def test_logger_extra_persists_across_calls(self):
        """Test that Logger.extra persists across multiple log calls"""
        output = StringIO()
        logger = Logger()
        logger.add(output, level="DEBUG", format="{message} | user: {extra.user_id}")

        logger.extra["user_id"] = 999

        logger.info("First log")
        logger.info("Second log")

        result = output.getvalue()
        assert result.count("999") == 2  # Should appear in both logs


class TestBoundLoggerInit:
    """Test BoundLogger initialization"""

    def test_bound_logger_creation(self):
        """Test creating a BoundLogger"""
        logger = Logger()
        bound = BoundLogger(logger, request_id="REQ-123")

        assert bound._parent is logger
        assert bound._bound_extra == {"request_id": "REQ-123"}

    def test_bound_logger_multiple_context(self):
        """Test BoundLogger with multiple context values"""
        logger = Logger()
        bound = BoundLogger(logger, request_id="REQ-123", user="alice", session="sess-456")

        assert bound._bound_extra == {
            "request_id": "REQ-123",
            "user": "alice",
            "session": "sess-456",
        }

    def test_bound_logger_repr(self):
        """Test BoundLogger string representation"""
        logger = Logger()
        bound = BoundLogger(logger, request_id="REQ-123", user="alice")

        repr_str = repr(bound)
        assert "BoundLogger" in repr_str
        assert "request_id" in repr_str or "user" in repr_str


class TestBoundLoggerLogging:
    """Test logging with BoundLogger"""

    def test_bound_logger_includes_context(self):
        """Test that BoundLogger includes bound context in logs"""
        output = StringIO()
        logger = Logger()
        logger.add(output, level="DEBUG", format="{message} | req: {extra.request_id}")

        bound = logger.bind(request_id="REQ-123")
        bound.info("Test message")

        result = output.getvalue()
        assert "Test message" in result
        assert "REQ-123" in result

    def test_bound_logger_all_log_levels(self):
        """Test that all log levels work with BoundLogger"""
        output = StringIO()
        logger = Logger()
        logger.add(output, level="TRACE", format="{level.name} | {message} | {extra.ctx}")

        bound = logger.bind(ctx="test-context")

        bound.trace("Trace message")
        bound.debug("Debug message")
        bound.info("Info message")
        bound.success("Success message")
        bound.warning("Warning message")
        bound.error("Error message")
        bound.critical("Critical message")

        result = output.getvalue()
        assert result.count("test-context") == 7  # All 7 log calls
        assert "TRACE" in result
        assert "DEBUG" in result
        assert "INFO" in result
        assert "SUCCESS" in result
        assert "WARNING" in result
        assert "ERROR" in result
        assert "CRITICAL" in result

    def test_bound_logger_exception(self):
        """Test exception logging with BoundLogger"""
        output = StringIO()
        logger = Logger()
        logger.add(output, level="ERROR", format="{message} | {extra.request_id}", backtrace=False)

        bound = logger.bind(request_id="REQ-ERROR")

        try:
            1 / 0
        except:
            bound.exception("Error occurred")

        result = output.getvalue()
        assert "Error occurred" in result
        assert "REQ-ERROR" in result


class TestBoundLoggerChaining:
    """Test BoundLogger chaining"""

    def test_bind_chaining(self):
        """Test that bind() can be chained"""
        logger = Logger()

        bound1 = logger.bind(level1="value1")
        bound2 = bound1.bind(level2="value2")
        bound3 = bound2.bind(level3="value3")

        assert bound1._bound_extra == {"level1": "value1"}
        assert bound2._bound_extra == {"level1": "value1", "level2": "value2"}
        assert bound3._bound_extra == {"level1": "value1", "level2": "value2", "level3": "value3"}

    def test_bind_chaining_in_logs(self):
        """Test that chained context appears in logs"""
        output = StringIO()
        logger = Logger()
        logger.add(output, level="INFO", format="{message} | {extra.a} | {extra.b} | {extra.c}")

        bound = logger.bind(a=1).bind(b=2).bind(c=3)
        bound.info("Chained message")

        result = output.getvalue()
        assert "Chained message" in result
        assert "1" in result
        assert "2" in result
        assert "3" in result

    def test_bind_override(self):
        """Test that later bind() calls can override earlier ones"""
        logger = Logger()

        bound1 = logger.bind(key="value1")
        bound2 = bound1.bind(key="value2")

        assert bound1._bound_extra == {"key": "value1"}
        assert bound2._bound_extra == {"key": "value2"}


class TestContextManager:
    """Test ContextManager for temporary context"""

    def test_contextmanager_creation(self):
        """Test creating a ContextManager"""
        logger = Logger()
        cm = ContextManager(logger, request_id="REQ-123")

        assert cm._logger is logger
        assert cm._context == {"request_id": "REQ-123"}

    def test_contextmanager_repr(self):
        """Test ContextManager string representation"""
        logger = Logger()
        cm = ContextManager(logger, request_id="REQ-123")

        repr_str = repr(cm)
        assert "ContextManager" in repr_str
        assert "request_id" in repr_str

    def test_contextmanager_adds_context(self):
        """Test that context manager adds context to logger"""
        output = StringIO()
        logger = Logger()
        logger.add(output, level="INFO", format="{message} | req: {extra.request_id}")

        with logger.contextualize(request_id="REQ-TEMP"):
            logger.info("Inside context")

        result = output.getvalue()
        assert "Inside context" in result
        assert "REQ-TEMP" in result

    def test_contextmanager_removes_context(self):
        """Test that context is removed after exiting"""
        logger = Logger()

        assert len(logger.extra) == 0

        with logger.contextualize(temp_key="temp_value"):
            assert "temp_key" in logger.extra
            assert logger.extra["temp_key"] == "temp_value"

        # After exiting, context should be removed
        assert len(logger.extra) == 0

    def test_contextmanager_restores_previous_state(self):
        """Test that context manager restores previous extra state"""
        logger = Logger()
        logger.extra["permanent_key"] = "permanent_value"

        with logger.contextualize(temp_key="temp_value"):
            assert "permanent_key" in logger.extra
            assert "temp_key" in logger.extra

        # After exiting, only permanent key remains
        assert "permanent_key" in logger.extra
        assert "temp_key" not in logger.extra

    def test_contextmanager_nested(self):
        """Test nested context managers"""
        output = StringIO()
        logger = Logger()
        logger.add(output, level="INFO", format="{message} | a: {extra.a} | b: {extra.b}")

        with logger.contextualize(a=1):
            logger.info("Level 1")

            with logger.contextualize(b=2):
                logger.info("Level 2")

            logger.info("Back to level 1")

        logger.info("Outside context")

        result = output.getvalue()
        lines = result.strip().split("\n")

        assert "Level 1" in lines[0]
        assert "a: 1" in lines[0]

        assert "Level 2" in lines[1]
        assert "a: 1" in lines[1]
        assert "b: 2" in lines[1]

        assert "Back to level 1" in lines[2]
        assert "a: 1" in lines[2]


class TestContextPriority:
    """Test context priority and merging"""

    def test_bound_context_overrides_global(self):
        """Test that bound context overrides global extra"""
        output = StringIO()
        logger = Logger()
        logger.add(output, level="INFO", format="{message} | key: {extra.key}")

        logger.extra["key"] = "global"
        bound = logger.bind(key="bound")

        bound.info("Test")

        result = output.getvalue()
        assert "key: bound" in result

    def test_log_call_extra_overrides_bound(self):
        """Test that per-call extra overrides bound context"""
        output = StringIO()
        logger = Logger()
        logger.add(output, level="INFO", format="{message} | key: {extra.key}")

        bound = logger.bind(key="bound")
        bound.info("Test", extra={"key": "call"})

        result = output.getvalue()
        assert "key: call" in result

    def test_context_priority_chain(self):
        """Test complete priority chain: call > bound > global"""
        output = StringIO()
        logger = Logger()
        logger.add(
            output, level="INFO", format="{message} | a: {extra.a} | b: {extra.b} | c: {extra.c}"
        )

        logger.extra["a"] = "global_a"
        logger.extra["b"] = "global_b"
        logger.extra["c"] = "global_c"

        bound = logger.bind(b="bound_b", c="bound_c")
        bound.info("Test", extra={"c": "call_c"})

        result = output.getvalue()
        # a: from global, b: from bound, c: from call
        assert "a: global_a" in result
        assert "b: bound_b" in result
        assert "c: call_c" in result


class TestContextBindingEdgeCases:
    """Test edge cases and special scenarios"""

    def test_empty_bind(self):
        """Test binding with no context"""
        logger = Logger()
        bound = logger.bind()

        assert bound._bound_extra == {}

    def test_bind_with_none_values(self):
        """Test binding with None values"""
        logger = Logger()
        bound = logger.bind(key=None)

        assert bound._bound_extra == {"key": None}

    def test_bind_with_complex_values(self):
        """Test binding with complex data types"""
        logger = Logger()
        bound = logger.bind(list_val=[1, 2, 3], dict_val={"nested": "value"}, tuple_val=(1, 2))

        assert bound._bound_extra["list_val"] == [1, 2, 3]
        assert bound._bound_extra["dict_val"] == {"nested": "value"}
        assert bound._bound_extra["tuple_val"] == (1, 2)

    def test_contextmanager_with_exception(self):
        """Test that context is still removed even if exception occurs"""
        logger = Logger()
        logger.extra["before"] = "value"

        try:
            with logger.contextualize(temp="temporary"):
                assert "temp" in logger.extra
                raise ValueError("Test error")
        except ValueError:
            pass

        # Context should be restored even after exception
        assert "before" in logger.extra
        assert "temp" not in logger.extra

    def test_multiple_bound_loggers_independent(self):
        """Test that multiple BoundLoggers are independent"""
        logger = Logger()

        bound1 = logger.bind(id=1)
        bound2 = logger.bind(id=2)

        assert bound1._bound_extra == {"id": 1}
        assert bound2._bound_extra == {"id": 2}
        # Changing one doesn't affect the other
        bound1._bound_extra["id"] = 999
        assert bound2._bound_extra == {"id": 2}
