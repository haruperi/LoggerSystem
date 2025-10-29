"""
Tests for FileHandler class

This module tests the FileHandler functionality including:
- Basic file output
- File creation and directory handling
- Append vs write modes
- File closing and reopening
- Thread safety
- Error handling
"""

import pytest
import tempfile
import threading
from pathlib import Path
from mylogger.handler import FileHandler
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


class TestFileHandlerBasic:
    """Test basic FileHandler functionality"""
    
    def test_init_with_string_path(self, tmp_path):
        """Test initialization with string path"""
        log_file = tmp_path / "test.log"
        formatter = Formatter("{message}")
        
        handler = FileHandler(str(log_file), levels.INFO, formatter)
        
        assert handler.path == log_file
        assert handler.level == levels.INFO
        assert handler.mode == 'a'
        assert handler.encoding == 'utf-8'
        assert handler.file_handle is not None
        
        handler.close()
    
    def test_init_with_path_object(self, tmp_path):
        """Test initialization with Path object"""
        log_file = tmp_path / "test.log"
        formatter = Formatter("{message}")
        
        handler = FileHandler(log_file, levels.INFO, formatter)
        
        assert handler.path == log_file
        assert isinstance(handler.path, Path)
        
        handler.close()
    
    def test_creates_file(self, tmp_path):
        """Test that handler creates the file"""
        log_file = tmp_path / "test.log"
        formatter = Formatter("{message}")
        
        assert not log_file.exists()
        
        handler = FileHandler(log_file, levels.INFO, formatter)
        
        assert log_file.exists()
        
        handler.close()
    
    def test_creates_parent_directories(self, tmp_path):
        """Test that handler creates parent directories"""
        log_file = tmp_path / "logs" / "subdir" / "test.log"
        formatter = Formatter("{message}")
        
        assert not log_file.parent.exists()
        
        handler = FileHandler(log_file, levels.INFO, formatter)
        
        assert log_file.parent.exists()
        assert log_file.exists()
        
        handler.close()
    
    def test_emit_basic(self, tmp_path):
        """Test basic emit to file"""
        log_file = tmp_path / "test.log"
        formatter = Formatter("{level.name} - {message}")
        handler = FileHandler(log_file, levels.INFO, formatter)
        
        # Emit a record
        record = create_test_record(levels.INFO, "Test message")
        handler.emit(record)
        
        handler.close()
        
        # Read and verify
        content = log_file.read_text()
        assert "INFO - Test message" in content
    
    def test_emit_multiple_records(self, tmp_path):
        """Test emitting multiple records"""
        log_file = tmp_path / "test.log"
        formatter = Formatter("{message}")
        handler = FileHandler(log_file, levels.DEBUG, formatter)
        
        # Emit multiple records
        for i in range(5):
            record = create_test_record(levels.INFO, f"Message {i}")
            handler.emit(record)
        
        handler.close()
        
        # Verify all messages
        content = log_file.read_text()
        lines = content.strip().split('\n')
        assert len(lines) == 5
        for i in range(5):
            assert f"Message {i}" in content
    
    def test_mode_append(self, tmp_path):
        """Test append mode (default)"""
        log_file = tmp_path / "test.log"
        formatter = Formatter("{message}")
        
        # Write first batch
        handler1 = FileHandler(log_file, levels.INFO, formatter, mode='a')
        handler1.emit(create_test_record(levels.INFO, "First"))
        handler1.close()
        
        # Write second batch (should append)
        handler2 = FileHandler(log_file, levels.INFO, formatter, mode='a')
        handler2.emit(create_test_record(levels.INFO, "Second"))
        handler2.close()
        
        # Verify both messages
        content = log_file.read_text()
        assert "First" in content
        assert "Second" in content
        lines = content.strip().split('\n')
        assert len(lines) == 2
    
    def test_mode_write(self, tmp_path):
        """Test write mode (overwrites)"""
        log_file = tmp_path / "test.log"
        formatter = Formatter("{message}")
        
        # Write first batch
        handler1 = FileHandler(log_file, levels.INFO, formatter, mode='w')
        handler1.emit(create_test_record(levels.INFO, "First"))
        handler1.close()
        
        # Write second batch (should overwrite)
        handler2 = FileHandler(log_file, levels.INFO, formatter, mode='w')
        handler2.emit(create_test_record(levels.INFO, "Second"))
        handler2.close()
        
        # Verify only second message
        content = log_file.read_text()
        assert "First" not in content
        assert "Second" in content
        lines = content.strip().split('\n')
        assert len(lines) == 1
    
    def test_encoding_utf8(self, tmp_path):
        """Test UTF-8 encoding (default)"""
        log_file = tmp_path / "test.log"
        formatter = Formatter("{message}")
        handler = FileHandler(log_file, levels.INFO, formatter, encoding='utf-8')
        
        # Emit with unicode characters
        record = create_test_record(levels.INFO, "Hello 世界 🌍")
        handler.emit(record)
        
        handler.close()
        
        # Verify encoding
        content = log_file.read_text(encoding='utf-8')
        assert "Hello 世界 🌍" in content
    
    def test_close_flushes_and_closes(self, tmp_path):
        """Test that close flushes and closes the file"""
        log_file = tmp_path / "test.log"
        formatter = Formatter("{message}")
        handler = FileHandler(log_file, levels.INFO, formatter)
        
        handler.emit(create_test_record(levels.INFO, "Test"))
        
        # Close should flush and close
        handler.close()
        
        # File handle should be None
        assert handler.file_handle is None
        
        # Data should be written
        content = log_file.read_text()
        assert "Test" in content
    
    def test_close_idempotent(self, tmp_path):
        """Test that close can be called multiple times"""
        log_file = tmp_path / "test.log"
        formatter = Formatter("{message}")
        handler = FileHandler(log_file, levels.INFO, formatter)
        
        # Close multiple times should not raise
        handler.close()
        handler.close()
        handler.close()


class TestFileHandlerFiltering:
    """Test FileHandler with filtering"""
    
    def test_level_filtering(self, tmp_path):
        """Test level-based filtering"""
        log_file = tmp_path / "test.log"
        formatter = Formatter("{level.name} - {message}")
        handler = FileHandler(log_file, levels.WARNING, formatter)
        
        # Emit various levels
        handler.emit(create_test_record(levels.DEBUG, "Debug message"))
        handler.emit(create_test_record(levels.INFO, "Info message"))
        handler.emit(create_test_record(levels.WARNING, "Warning message"))
        handler.emit(create_test_record(levels.ERROR, "Error message"))
        
        handler.close()
        
        # Only WARNING and above should be written
        content = log_file.read_text()
        assert "Debug message" not in content
        assert "Info message" not in content
        assert "Warning message" in content
        assert "Error message" in content
    
    def test_custom_filter(self, tmp_path):
        """Test custom filter function"""
        log_file = tmp_path / "test.log"
        formatter = Formatter("{message}")
        
        # Filter that only allows messages containing "important"
        def filter_func(record):
            return "important" in record.message.lower()
        
        handler = FileHandler(
            log_file,
            levels.DEBUG,
            formatter,
            filter_func=filter_func
        )
        
        # Emit various messages
        handler.emit(create_test_record(levels.INFO, "Regular message"))
        handler.emit(create_test_record(levels.INFO, "Important message"))
        handler.emit(create_test_record(levels.ERROR, "Important error"))
        handler.emit(create_test_record(levels.INFO, "Another message"))
        
        handler.close()
        
        # Only "important" messages should be written
        content = log_file.read_text()
        assert "Regular message" not in content
        assert "Important message" in content
        assert "Important error" in content
        assert "Another message" not in content


class TestFileHandlerThreadSafety:
    """Test FileHandler thread safety"""
    
    def test_concurrent_writes(self, tmp_path):
        """Test concurrent writes from multiple threads"""
        log_file = tmp_path / "test.log"
        formatter = Formatter("{message}")
        handler = FileHandler(log_file, levels.INFO, formatter)
        
        num_threads = 5
        num_messages = 10
        
        def write_messages(thread_id):
            for i in range(num_messages):
                record = create_test_record(levels.INFO, f"Thread {thread_id} message {i}")
                handler.emit(record)
        
        # Create and start threads
        threads = []
        for i in range(num_threads):
            thread = threading.Thread(target=write_messages, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        handler.close()
        
        # Verify all messages written
        content = log_file.read_text()
        lines = content.strip().split('\n')
        
        # Should have exactly num_threads * num_messages lines
        assert len(lines) == num_threads * num_messages
        
        # Each message should be present
        for i in range(num_threads):
            for j in range(num_messages):
                assert f"Thread {i} message {j}" in content
    
    def test_no_interleaved_lines(self, tmp_path):
        """Test that lines are not interleaved in concurrent writes"""
        log_file = tmp_path / "test.log"
        formatter = Formatter("{message}")
        handler = FileHandler(log_file, levels.INFO, formatter)
        
        num_threads = 10
        num_messages = 20
        
        def write_messages(thread_id):
            for i in range(num_messages):
                # Write longer messages to increase chance of interleaving if not thread-safe
                record = create_test_record(
                    levels.INFO,
                    f"Thread-{thread_id:02d}-Message-{i:03d}-" + "x" * 50
                )
                handler.emit(record)
        
        # Create and start threads
        threads = []
        for i in range(num_threads):
            thread = threading.Thread(target=write_messages, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        handler.close()
        
        # Verify no interleaved lines (each line should be complete)
        content = log_file.read_text()
        lines = content.strip().split('\n')
        
        for line in lines:
            # Each line should start with "Thread-" and end with 50 x's
            assert line.startswith("Thread-")
            assert line.endswith("x" * 50)


class TestFileHandlerErrorHandling:
    """Test FileHandler error handling"""
    
    def test_emit_with_closed_handler(self, tmp_path):
        """Test emitting after handler is closed"""
        log_file = tmp_path / "test.log"
        formatter = Formatter("{message}")
        handler = FileHandler(log_file, levels.INFO, formatter)
        
        # Close the handler
        handler.close()
        
        # Emit should not raise (reopens file)
        record = create_test_record(levels.INFO, "After close")
        handler.emit(record)
        
        handler.close()
        
        # Message should be written
        content = log_file.read_text()
        assert "After close" in content
    
    def test_invalid_encoding_raises(self, tmp_path):
        """Test that invalid encoding raises error"""
        log_file = tmp_path / "test.log"
        formatter = Formatter("{message}")
        
        with pytest.raises(LookupError):
            FileHandler(log_file, levels.INFO, formatter, encoding='invalid-encoding')
    
    def test_format_error_fallback(self, tmp_path):
        """Test fallback when formatter fails"""
        log_file = tmp_path / "test.log"
        
        # Create a formatter that will fail
        class ErrorFormatter:
            def format(self, record):
                raise ValueError("Format failed")
        
        handler = FileHandler(log_file, levels.INFO, ErrorFormatter())
        
        record = create_test_record(levels.INFO, "Test message")
        
        # Should use fallback format (from Handler base class)
        handler.emit(record)
        
        handler.close()
        
        # Should have fallback output
        content = log_file.read_text()
        assert "INFO" in content or "Test message" in content


class TestFileHandlerFormats:
    """Test FileHandler with different formats"""
    
    def test_simple_format(self, tmp_path):
        """Test with simple format"""
        log_file = tmp_path / "test.log"
        formatter = Formatter("{message}")
        handler = FileHandler(log_file, levels.INFO, formatter)
        
        handler.emit(create_test_record(levels.INFO, "Simple"))
        handler.close()
        
        content = log_file.read_text()
        assert content.strip() == "Simple"
    
    def test_detailed_format(self, tmp_path):
        """Test with detailed format"""
        log_file = tmp_path / "test.log"
        formatter = Formatter(
            "{time:YYYY-MM-DD HH:mm:ss} | {level.name: <8} | "
            "{name}:{function}:{line} | {message}"
        )
        handler = FileHandler(log_file, levels.INFO, formatter)
        
        handler.emit(create_test_record(levels.INFO, "Detailed"))
        handler.close()
        
        content = log_file.read_text()
        assert "INFO" in content
        assert "test_logger:test_function:1" in content
        assert "Detailed" in content
    
    def test_with_extra_fields(self, tmp_path):
        """Test with extra fields in format"""
        log_file = tmp_path / "test.log"
        formatter = Formatter("{message} | User: {extra.user_id}")
        handler = FileHandler(log_file, levels.INFO, formatter)
        
        record = create_test_record(levels.INFO, "User action", extra={"user_id": 12345})
        handler.emit(record)
        
        handler.close()
        
        content = log_file.read_text()
        assert "User action | User: 12345" in content


class TestFileHandlerPaths:
    """Test FileHandler path handling"""
    
    def test_relative_path(self, tmp_path):
        """Test with relative path"""
        import os
        original_cwd = os.getcwd()
        
        try:
            os.chdir(tmp_path)
            
            formatter = Formatter("{message}")
            handler = FileHandler("test.log", levels.INFO, formatter)
            
            handler.emit(create_test_record(levels.INFO, "Test"))
            handler.close()
            
            # File should exist in current directory
            assert (tmp_path / "test.log").exists()
            
        finally:
            os.chdir(original_cwd)
    
    def test_absolute_path(self, tmp_path):
        """Test with absolute path"""
        log_file = tmp_path / "absolute.log"
        formatter = Formatter("{message}")
        handler = FileHandler(log_file.absolute(), levels.INFO, formatter)
        
        handler.emit(create_test_record(levels.INFO, "Absolute"))
        handler.close()
        
        assert log_file.exists()
        content = log_file.read_text()
        assert "Absolute" in content
    
    def test_nested_directories(self, tmp_path):
        """Test with deeply nested directories"""
        log_file = tmp_path / "a" / "b" / "c" / "d" / "test.log"
        formatter = Formatter("{message}")
        handler = FileHandler(log_file, levels.INFO, formatter)
        
        handler.emit(create_test_record(levels.INFO, "Nested"))
        handler.close()
        
        assert log_file.exists()
        content = log_file.read_text()
        assert "Nested" in content


class TestFileHandlerIntegration:
    """Integration tests for FileHandler"""
    
    def test_multiple_handlers_same_file(self, tmp_path):
        """Test multiple handlers writing to the same file"""
        log_file = tmp_path / "shared.log"
        formatter = Formatter("{message}")
        
        handler1 = FileHandler(log_file, levels.INFO, formatter)
        handler2 = FileHandler(log_file, levels.INFO, formatter)
        
        handler1.emit(create_test_record(levels.INFO, "From handler 1"))
        handler2.emit(create_test_record(levels.INFO, "From handler 2"))
        
        handler1.close()
        handler2.close()
        
        # Both messages should be in file
        content = log_file.read_text()
        assert "From handler 1" in content
        assert "From handler 2" in content
    
    def test_different_levels_same_file(self, tmp_path):
        """Test handlers with different levels writing to same file"""
        log_file = tmp_path / "test.log"
        formatter = Formatter("{level.name} - {message}")
        
        handler_info = FileHandler(log_file, levels.INFO, formatter)
        handler_error = FileHandler(log_file, levels.ERROR, formatter)
        
        # INFO handler gets both
        handler_info.emit(create_test_record(levels.INFO, "Info message"))
        handler_info.emit(create_test_record(levels.ERROR, "Error message"))
        
        # ERROR handler gets only error
        handler_error.emit(create_test_record(levels.INFO, "Info message 2"))
        handler_error.emit(create_test_record(levels.ERROR, "Error message 2"))
        
        handler_info.close()
        handler_error.close()
        
        content = log_file.read_text()
        assert "INFO - Info message" in content
        assert "ERROR - Error message" in content
        assert "INFO - Info message 2" not in content  # Filtered by ERROR handler
        assert "ERROR - Error message 2" in content
    
    def test_colorize_disabled_for_files(self, tmp_path):
        """Test that colorize is disabled by default for files"""
        log_file = tmp_path / "test.log"
        formatter = Formatter("{message}")
        handler = FileHandler(log_file, levels.INFO, formatter)
        
        # Colorize should be False for files
        assert handler.colorize is False
        
        handler.close()

