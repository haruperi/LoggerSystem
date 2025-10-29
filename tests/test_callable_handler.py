"""
Tests for CallableHandler class with serialization
"""

import json
import pytest
from datetime import datetime, timedelta

from mylogger.handler import CallableHandler
from mylogger.formatter import Formatter
from mylogger.record import LogRecord, Level, FileInfo, ProcessInfo, ThreadInfo
from mylogger import level as levels


class TestCallableHandler:
    """Test the CallableHandler class"""

    @pytest.fixture
    def formatter(self):
        """Get a simple formatter"""
        return Formatter()

    @pytest.fixture
    def sample_record(self):
        """Create a sample log record"""
        return LogRecord(
            elapsed=timedelta(seconds=1.5),
            exception=None,
            extra={"user_id": 123},
            file=FileInfo(name="test.py", path="/path/to/test.py"),
            function="test_function",
            level=levels.INFO,
            line=42,
            message="Test message",
            module="test_module",
            name="test_logger",
            process=ProcessInfo(id=1234, name="python"),
            thread=ThreadInfo(id=5678, name="MainThread"),
            time=datetime(2024, 1, 15, 14, 30, 45),
        )

    def test_callable_handler_creation(self, formatter):
        """Test creating a CallableHandler"""
        output = []

        def callback(message):
            output.append(message)

        handler = CallableHandler(sink=callback, level=levels.INFO, formatter=formatter)

        assert handler.func == callback
        assert handler.serialize is False  # Default

    def test_callable_handler_invalid_sink(self, formatter):
        """Test that non-callable sink raises TypeError"""
        with pytest.raises(TypeError):
            CallableHandler(sink="not a callable", level=levels.INFO, formatter=formatter)

    def test_callable_handler_emit_formatted(self, formatter, sample_record):
        """Test CallableHandler emits formatted strings by default"""
        output = []

        def callback(message):
            output.append(message)

        handler = CallableHandler(
            sink=callback, level=levels.DEBUG, formatter=formatter, serialize=False
        )

        handler.emit(sample_record)

        assert len(output) == 1
        assert isinstance(output[0], str)
        assert "Test message" in output[0]

    def test_callable_handler_emit_serialized(self, formatter, sample_record):
        """Test CallableHandler emits JSON when serialize=True"""
        output = []

        def callback(json_str):
            output.append(json_str)

        handler = CallableHandler(
            sink=callback, level=levels.DEBUG, formatter=formatter, serialize=True
        )

        handler.emit(sample_record)

        assert len(output) == 1
        assert isinstance(output[0], str)

        # Should be valid JSON
        data = json.loads(output[0])
        assert data["message"] == "Test message"
        assert data["level"]["name"] == "INFO"
        assert data["line"] == 42

    def test_callable_handler_level_filtering(self, formatter, sample_record):
        """Test that CallableHandler respects level filtering"""
        output = []

        def callback(message):
            output.append(message)

        # Handler with WARNING level
        handler = CallableHandler(sink=callback, level=levels.WARNING, formatter=formatter)

        # Emit INFO record (should be filtered out)
        handler.emit(sample_record)

        assert len(output) == 0

    def test_callable_handler_with_filter(self, formatter, sample_record):
        """Test CallableHandler with custom filter function"""
        output = []

        def callback(message):
            output.append(message)

        def only_even_lines(record):
            return record.line % 2 == 0

        handler = CallableHandler(
            sink=callback, level=levels.DEBUG, formatter=formatter, filter_func=only_even_lines
        )

        # Line 42 is even, should pass
        handler.emit(sample_record)
        assert len(output) == 1

        # Create record with odd line number
        odd_record = LogRecord(
            elapsed=timedelta(seconds=1),
            exception=None,
            extra={},
            file=FileInfo(name="test.py", path="/test.py"),
            function="test",
            level=levels.INFO,
            line=43,  # Odd line
            message="Odd line",
            module="test",
            name="test",
            process=ProcessInfo(id=1, name="test"),
            thread=ThreadInfo(id=1, name="test"),
            time=datetime(2024, 1, 15),
        )

        handler.emit(odd_record)
        assert len(output) == 1  # Still 1, second record filtered out

    def test_callable_handler_error_handling_with_catch(self, formatter, sample_record):
        """Test that errors in callable are caught when catch=True"""

        def bad_callback(message):
            raise RuntimeError("Callback failed!")

        handler = CallableHandler(
            sink=bad_callback, level=levels.DEBUG, formatter=formatter, catch=True
        )

        # Should not raise exception
        handler.emit(sample_record)

    def test_callable_handler_error_handling_without_catch(self, formatter, sample_record):
        """Test that errors in callable are raised when catch=False"""

        def bad_callback(message):
            raise RuntimeError("Callback failed!")

        handler = CallableHandler(
            sink=bad_callback, level=levels.DEBUG, formatter=formatter, catch=False
        )

        # Should raise exception
        with pytest.raises(RuntimeError, match="Callback failed!"):
            handler.emit(sample_record)

    def test_callable_handler_multiple_calls(self, formatter):
        """Test CallableHandler with multiple emit calls"""
        output = []

        def callback(message):
            output.append(message)

        handler = CallableHandler(sink=callback, level=levels.DEBUG, formatter=formatter)

        # Emit multiple records
        for i in range(5):
            record = LogRecord(
                elapsed=timedelta(seconds=i),
                exception=None,
                extra={},
                file=FileInfo(name="test.py", path="/test.py"),
                function="test",
                level=levels.INFO,
                line=i,
                message=f"Message {i}",
                module="test",
                name="test",
                process=ProcessInfo(id=1, name="test"),
                thread=ThreadInfo(id=1, name="test"),
                time=datetime(2024, 1, 15),
            )
            handler.emit(record)

        assert len(output) == 5
        for i, msg in enumerate(output):
            assert f"Message {i}" in msg

    def test_callable_handler_serialized_extra_fields(self, formatter):
        """Test that extra fields are included in serialized output"""
        output = []

        def callback(json_str):
            output.append(json_str)

        handler = CallableHandler(
            sink=callback, level=levels.DEBUG, formatter=formatter, serialize=True
        )

        record = LogRecord(
            elapsed=timedelta(seconds=1),
            exception=None,
            extra={"user_id": 123, "request_id": "abc-123", "ip": "192.168.1.1"},
            file=FileInfo(name="test.py", path="/test.py"),
            function="test",
            level=levels.INFO,
            line=1,
            message="Request received",
            module="test",
            name="test",
            process=ProcessInfo(id=1, name="test"),
            thread=ThreadInfo(id=1, name="test"),
            time=datetime(2024, 1, 15),
        )

        handler.emit(record)

        data = json.loads(output[0])
        assert data["extra"]["user_id"] == 123
        assert data["extra"]["request_id"] == "abc-123"
        assert data["extra"]["ip"] == "192.168.1.1"

    def test_callable_handler_thread_safety(self, formatter):
        """Test that CallableHandler uses lock for thread safety"""
        import threading

        output = []
        lock = threading.Lock()

        def callback(message):
            with lock:
                output.append(message)

        handler = CallableHandler(sink=callback, level=levels.DEBUG, formatter=formatter)

        # Verify handler has a lock
        assert hasattr(handler, "_lock")

        # Create multiple threads that emit logs
        def emit_logs():
            for i in range(10):
                record = LogRecord(
                    elapsed=timedelta(seconds=i),
                    exception=None,
                    extra={},
                    file=FileInfo(name="test.py", path="/test.py"),
                    function="test",
                    level=levels.INFO,
                    line=i,
                    message=f"Thread {threading.current_thread().name} - {i}",
                    module="test",
                    name="test",
                    process=ProcessInfo(id=1, name="test"),
                    thread=ThreadInfo(
                        id=threading.get_ident(), name=threading.current_thread().name
                    ),
                    time=datetime(2024, 1, 15),
                )
                handler.emit(record)

        threads = [threading.Thread(target=emit_logs) for _ in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Should have 3 threads * 10 messages = 30 messages
        assert len(output) == 30

    def test_callable_handler_lambda_function(self, formatter, sample_record):
        """Test CallableHandler with lambda function"""
        output = []

        handler = CallableHandler(
            sink=lambda msg: output.append(msg.upper()), level=levels.DEBUG, formatter=formatter
        )

        handler.emit(sample_record)

        assert len(output) == 1
        assert "TEST MESSAGE" in output[0]

    def test_callable_handler_with_exception_record(self, formatter):
        """Test CallableHandler with record containing exception"""
        from mylogger.record import ExceptionInfo

        output = []

        def callback(json_str):
            output.append(json_str)

        handler = CallableHandler(
            sink=callback, level=levels.DEBUG, formatter=formatter, serialize=True
        )

        # Create exception info
        try:
            raise ValueError("Test error")
        except ValueError:
            import sys

            exc_info = sys.exc_info()
            exception = ExceptionInfo(type=exc_info[0], value=exc_info[1], traceback=exc_info[2])

        record = LogRecord(
            elapsed=timedelta(seconds=1),
            exception=exception,
            extra={},
            file=FileInfo(name="test.py", path="/test.py"),
            function="test",
            level=levels.ERROR,
            line=1,
            message="Error occurred",
            module="test",
            name="test",
            process=ProcessInfo(id=1, name="test"),
            thread=ThreadInfo(id=1, name="test"),
            time=datetime(2024, 1, 15),
        )

        handler.emit(record)

        data = json.loads(output[0])
        assert data["exception"] is not None
        assert data["exception"]["type"] == "ValueError"
        assert "Test error" in data["exception"]["value"]

    def test_callable_handler_close(self, formatter):
        """Test CallableHandler close method"""
        output = []

        handler = CallableHandler(
            sink=lambda msg: output.append(msg), level=levels.DEBUG, formatter=formatter
        )

        # Close should not raise exception
        handler.close()

    def test_callable_handler_class_method(self, formatter, sample_record):
        """Test CallableHandler with class method as callback"""

        class LogCollector:
            def __init__(self):
                self.logs = []

            def add_log(self, message):
                self.logs.append(message)

        collector = LogCollector()

        handler = CallableHandler(sink=collector.add_log, level=levels.DEBUG, formatter=formatter)

        handler.emit(sample_record)

        assert len(collector.logs) == 1
        assert "Test message" in collector.logs[0]

    def test_callable_handler_structured_logging(self, formatter):
        """Test CallableHandler for structured logging use case"""
        structured_logs = []

        def log_to_structured_store(json_str):
            """Simulates sending logs to a structured logging service"""
            data = json.loads(json_str)
            structured_logs.append(
                {
                    "timestamp": data["time"]["timestamp"],
                    "level": data["level"]["name"],
                    "message": data["message"],
                    "context": data["extra"],
                }
            )

        handler = CallableHandler(
            sink=log_to_structured_store, level=levels.DEBUG, formatter=formatter, serialize=True
        )

        # Emit several logs with context
        contexts = [
            {"user": "alice", "action": "login"},
            {"user": "bob", "action": "logout"},
            {"user": "charlie", "action": "view_page"},
        ]

        for ctx in contexts:
            record = LogRecord(
                elapsed=timedelta(seconds=1),
                exception=None,
                extra=ctx,
                file=FileInfo(name="test.py", path="/test.py"),
                function="test",
                level=levels.INFO,
                line=1,
                message=f"User {ctx['user']} performed {ctx['action']}",
                module="test",
                name="test",
                process=ProcessInfo(id=1, name="test"),
                thread=ThreadInfo(id=1, name="test"),
                time=datetime(2024, 1, 15),
            )
            handler.emit(record)

        assert len(structured_logs) == 3
        assert structured_logs[0]["context"]["user"] == "alice"
        assert structured_logs[1]["context"]["action"] == "logout"
        assert structured_logs[2]["message"] == "User charlie performed view_page"
