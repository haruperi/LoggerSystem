"""
Tests for StreamHandler class

This module tests the StreamHandler functionality including:
- Basic stream output
- Console output to stderr/stdout
- TTY detection for colorization
- Stream flushing behavior
- Error handling
- Thread safety
"""

import pytest
import sys
import io
import threading
from mylogger.handler import StreamHandler
from mylogger.formatter import Formatter
from mylogger.record import LogRecord, FileInfo, ProcessInfo, ThreadInfo
from mylogger import level as levels
from datetime import datetime, timedelta


def create_test_record(level, message, extra=None):
    """Helper to create a test log record"""
    return LogRecord(
        elapsed=timedelta(seconds=0),
        exception=None,
        extra=extra or {},
        file=FileInfo(name="test.py", path="/path/to/test.py"),
        function="test_function",
        level=level,
        line=1,
        message=message,
        module="test_module",
        name="test_logger",
        process=ProcessInfo(id=1234, name="python"),
        thread=ThreadInfo(id=5678, name="MainThread"),
        time=datetime.now()
    )


class TestStreamHandler:
    """Test StreamHandler class"""
    
    def test_init_with_stdout(self):
        """Test initialization with stdout"""
        formatter = Formatter("{message}")
        handler = StreamHandler(sys.stdout, levels.INFO, formatter)
        
        assert handler.stream is sys.stdout
        assert handler.level == levels.INFO
        assert handler.formatter is formatter
    
    def test_init_with_stderr(self):
        """Test initialization with stderr"""
        formatter = Formatter("{message}")
        handler = StreamHandler(sys.stderr, levels.DEBUG, formatter)
        
        assert handler.stream is sys.stderr
        assert handler.level == levels.DEBUG
    
    def test_init_with_stringio(self):
        """Test initialization with StringIO"""
        stream = io.StringIO()
        formatter = Formatter("{message}")
        handler = StreamHandler(stream, levels.INFO, formatter)
        
        assert handler.stream is stream
    
    def test_emit_basic(self):
        """Test basic emit to stream"""
        stream = io.StringIO()
        formatter = Formatter("{level.name} - {message}")
        handler = StreamHandler(stream, levels.INFO, formatter)
        
        # Create and emit a log record
        record = create_test_record(levels.INFO, "Test message")
        handler.emit(record)
        
        # Check output
        output = stream.getvalue()
        assert "INFO - Test message" in output
        assert output.endswith('\n')
    
    def test_emit_multiple_records(self):
        """Test emitting multiple records"""
        stream = io.StringIO()
        formatter = Formatter("{message}")
        handler = StreamHandler(stream, levels.DEBUG, formatter)
        
        # Emit multiple records
        for i in range(3):
            record = create_test_record(levels.INFO, f"Message {i}")
            handler.emit(record)
        
        # Check all messages are in output
        output = stream.getvalue()
        assert "Message 0" in output
        assert "Message 1" in output
        assert "Message 2" in output
        assert output.count('\n') == 3
    
    def test_emit_with_level_filter(self):
        """Test that records below level threshold are not emitted"""
        stream = io.StringIO()
        formatter = Formatter("{level.name} - {message}")
        handler = StreamHandler(stream, levels.WARNING, formatter)
        
        # Create INFO record (below threshold)
        info_record = create_test_record(levels.INFO, "Info message")
        
        # Create WARNING record (at threshold)
        warning_record = create_test_record(levels.WARNING, "Warning message")
        
        # Emit both
        handler.emit(info_record)
        handler.emit(warning_record)
        
        # Only WARNING should be in output
        output = stream.getvalue()
        assert "Info message" not in output
        assert "Warning message" in output
    
    def test_emit_with_custom_filter(self):
        """Test emit with custom filter function"""
        stream = io.StringIO()
        formatter = Formatter("{message}")
        
        # Filter that only allows messages containing "important"
        def filter_func(record):
            return "important" in record.message.lower()
        
        handler = StreamHandler(
            stream,
            levels.DEBUG,
            formatter,
            filter_func=filter_func
        )
        
        # Create records
        record1 = create_test_record(levels.INFO, "Important message")
        record2 = create_test_record(levels.INFO, "Regular message")
        
        # Emit both
        handler.emit(record1)
        handler.emit(record2)
        
        # Only "Important message" should be in output
        output = stream.getvalue()
        assert "Important message" in output
        assert "Regular message" not in output
    
    def test_should_colorize_stringio(self):
        """Test colorize detection for StringIO (should be False)"""
        stream = io.StringIO()
        formatter = Formatter("{message}")
        handler = StreamHandler(stream, levels.INFO, formatter)
        
        # StringIO is not a TTY
        assert handler.colorize is False
    
    def test_should_colorize_explicit(self):
        """Test explicit colorize setting"""
        stream = io.StringIO()
        formatter = Formatter("{message}")
        
        # Explicitly enable colorization
        handler = StreamHandler(
            stream,
            levels.INFO,
            formatter,
            colorize=True
        )
        
        assert handler.colorize is True
    
    def test_close_flush_stream(self):
        """Test that close flushes and closes the stream"""
        stream = io.StringIO()
        formatter = Formatter("{message}")
        handler = StreamHandler(stream, levels.INFO, formatter)
        
        # Emit a record
        record = create_test_record(levels.INFO, "Test")
        handler.emit(record)
        
        # Get output before closing
        output = stream.getvalue()
        assert "Test" in output
        
        # Close should close the stream (for non-stdout/stderr)
        handler.close()
        
        # Stream should be closed
        assert stream.closed
    
    def test_close_does_not_close_stdout(self):
        """Test that close does not close stdout"""
        formatter = Formatter("{message}")
        handler = StreamHandler(sys.stdout, levels.INFO, formatter)
        
        # Close should not raise and stdout should remain open
        handler.close()
        
        assert not sys.stdout.closed
    
    def test_close_does_not_close_stderr(self):
        """Test that close does not close stderr"""
        formatter = Formatter("{message}")
        handler = StreamHandler(sys.stderr, levels.INFO, formatter)
        
        # Close should not raise and stderr should remain open
        handler.close()
        
        assert not sys.stderr.closed
    
    def test_thread_safety(self):
        """Test that emit is thread-safe"""
        stream = io.StringIO()
        formatter = Formatter("{message}")
        handler = StreamHandler(stream, levels.INFO, formatter)
        
        # Number of threads and messages per thread
        num_threads = 5
        num_messages = 10
        
        def emit_messages(thread_id):
            for i in range(num_messages):
                record = create_test_record(levels.INFO, f"Thread {thread_id} message {i}")
                handler.emit(record)
        
        # Create and start threads
        threads = []
        for i in range(num_threads):
            thread = threading.Thread(target=emit_messages, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check that all messages were written
        output = stream.getvalue()
        lines = output.strip().split('\n')
        
        # Should have exactly num_threads * num_messages lines
        assert len(lines) == num_threads * num_messages
        
        # Each thread's messages should be present
        for i in range(num_threads):
            for j in range(num_messages):
                assert f"Thread {i} message {j}" in output
    
    def test_emit_error_handling(self):
        """Test error handling in emit"""
        # Create a stream that will raise an error on write
        class ErrorStream:
            def write(self, data):
                raise IOError("Write failed")
            
            def flush(self):
                pass
            
            def isatty(self):
                return False
        
        stream = ErrorStream()
        formatter = Formatter("{message}")
        handler = StreamHandler(stream, levels.INFO, formatter)
        
        record = create_test_record(levels.INFO, "Test")
        
        # Emit should not raise (errors are caught and reported to stderr)
        # This should not raise an exception
        handler.emit(record)
    
    def test_format_error_fallback(self):
        """Test fallback formatting when formatter fails"""
        stream = io.StringIO()
        
        # Create a formatter that will fail
        class ErrorFormatter:
            def format(self, record):
                raise ValueError("Format failed")
        
        handler = StreamHandler(stream, levels.INFO, ErrorFormatter())
        
        record = create_test_record(levels.INFO, "Test message")
        
        # Should use fallback format
        handler.emit(record)
        
        output = stream.getvalue()
        # The base Handler.format() method has a fallback
        assert "INFO" in output or "Test message" in output
    
    def test_colorize_auto_detection(self):
        """Test automatic colorize detection based on TTY"""
        # Create a mock TTY stream
        class TTYStream(io.StringIO):
            def isatty(self):
                return True
        
        # Note: the _should_colorize method wraps isatty in a try-except
        # and checks if the stream has the isatty method
        stream = TTYStream()
        formatter = Formatter("{message}")
        
        # When colorize is not explicitly set, it should auto-detect
        handler = StreamHandler(stream, levels.INFO, formatter)
        
        # For a real TTY, this should be True
        # However, the implementation wraps this in hasattr checks
        # StringIO with isatty() returning True should work
        assert handler._should_colorize() is True
    
    def test_colorize_non_tty(self):
        """Test colorize disabled for non-TTY streams"""
        # Regular StringIO is not a TTY
        stream = io.StringIO()
        formatter = Formatter("{message}")
        handler = StreamHandler(stream, levels.INFO, formatter)
        
        # Should auto-detect as non-TTY and disable colors
        assert handler.colorize is False
    
    def test_different_levels(self):
        """Test handler with different log levels"""
        log_levels = [levels.TRACE, levels.DEBUG, levels.INFO, 
                      levels.SUCCESS, levels.WARNING, levels.ERROR, levels.CRITICAL]
        
        for log_level in log_levels:
            stream = io.StringIO()
            formatter = Formatter("{level.name} - {message}")
            handler = StreamHandler(stream, log_level, formatter)
            
            record = create_test_record(log_level, f"Test {log_level.name}")
            
            handler.emit(record)
            
            output = stream.getvalue()
            assert log_level.name in output
            assert f"Test {log_level.name}" in output
    
    def test_close_idempotent(self):
        """Test that close can be called multiple times"""
        stream = io.StringIO()
        formatter = Formatter("{message}")
        handler = StreamHandler(stream, levels.INFO, formatter)
        
        # Close multiple times should not raise
        handler.close()
        handler.close()
        handler.close()
    
    def test_emit_with_extra_fields(self):
        """Test emitting records with extra fields"""
        stream = io.StringIO()
        formatter = Formatter("{level.name} - {message} - User: {extra.user_id}")
        handler = StreamHandler(stream, levels.INFO, formatter)
        
        record = create_test_record(levels.INFO, "User action", extra={"user_id": 12345})
        
        handler.emit(record)
        
        output = stream.getvalue()
        assert "INFO - User action - User: 12345" in output


class TestStreamHandlerIntegration:
    """Integration tests for StreamHandler"""
    
    def test_stdout_and_stderr(self):
        """Test using both stdout and stderr"""
        formatter = Formatter("{level.name}: {message}")
        
        # Handler for stdout
        stdout_handler = StreamHandler(sys.stdout, levels.INFO, formatter)
        
        # Handler for stderr
        stderr_handler = StreamHandler(sys.stderr, levels.ERROR, formatter)
        
        # Both should be valid
        assert stdout_handler.stream is sys.stdout
        assert stderr_handler.stream is sys.stderr
    
    def test_multiple_handlers_same_stream(self):
        """Test multiple handlers writing to the same stream"""
        stream = io.StringIO()
        formatter1 = Formatter("{level.name}: {message}")
        formatter2 = Formatter("[{level.name}] {message}")
        
        handler1 = StreamHandler(stream, levels.INFO, formatter1)
        handler2 = StreamHandler(stream, levels.DEBUG, formatter2)
        
        record = create_test_record(levels.INFO, "Test")
        
        # Emit to both handlers
        handler1.emit(record)
        handler2.emit(record)
        
        # Both outputs should be in stream
        output = stream.getvalue()
        assert "INFO: Test" in output
        assert "[INFO] Test" in output
