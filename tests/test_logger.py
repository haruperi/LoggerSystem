"""
Tests for Logger class - Day 18.1
Tests all logging methods, message formatting, level filtering, and handler add/remove
"""

import pytest
from io import StringIO
import tempfile
from pathlib import Path

from mylogger import logger, Logger
from mylogger import level as levels
from mylogger.exceptions import InvalidLevelError, HandlerNotFoundError


class TestLoggerBasicLogging:
    """Test basic logging methods - trace through critical"""
    
    def test_logger_exists(self):
        """Test that logger instance exists"""
        assert logger is not None
        assert isinstance(logger, Logger)
    
    def test_all_logging_levels(self):
        """Test all logging level methods exist and work"""
        test_logger = Logger()
        output = StringIO()
        test_logger.add(output, level="TRACE", format="{level.name} | {message}")
        
        # Test all logging methods
        test_logger.trace("trace message")
        test_logger.debug("debug message")
        test_logger.info("info message")
        test_logger.success("success message")
        test_logger.warning("warning message")
        test_logger.error("error message")
        test_logger.critical("critical message")
        
        result = output.getvalue()
        assert "TRACE" in result
        assert "DEBUG" in result
        assert "INFO" in result
        assert "SUCCESS" in result
        assert "WARNING" in result
        assert "ERROR" in result
        assert "CRITICAL" in result
    
    def test_log_method_with_string_level(self):
        """Test log() method with string level names"""
        test_logger = Logger()
        output = StringIO()
        test_logger.add(output, level="TRACE", format="{level.name} | {message}")
        
        test_logger.log("INFO", "Info message")
        test_logger.log("ERROR", "Error message")
        test_logger.log("DEBUG", "Debug message")
        
        result = output.getvalue()
        assert "INFO" in result and "Info message" in result
        assert "ERROR" in result and "Error message" in result
        assert "DEBUG" in result and "Debug message" in result
    
    def test_log_method_with_numeric_level(self):
        """Test log() method with numeric levels"""
        test_logger = Logger()
        output = StringIO()
        test_logger.add(output, level="TRACE", format="{level.name} - {level.no} | {message}")
        
        test_logger.log(10, "Level 10 (DEBUG)")
        test_logger.log(20, "Level 20 (INFO)")
        test_logger.log(40, "Level 40 (ERROR)")
        
        result = output.getvalue()
        assert "DEBUG" in result and "10" in result
        assert "INFO" in result and "20" in result
        assert "ERROR" in result and "40" in result


class TestLoggerMessageFormatting:
    """Test message formatting with args and kwargs"""
    
    def test_format_with_positional_args(self):
        """Test message formatting with positional arguments"""
        test_logger = Logger()
        output = StringIO()
        test_logger.add(output, level="INFO", format="{message}")
        
        test_logger.info("User {}", "John")
        test_logger.info("User {} from {}", "Alice", "NYC")
        test_logger.info("Values: {}, {}, {}", 1, 2, 3)
        
        result = output.getvalue()
        assert "User John" in result
        assert "User Alice from NYC" in result
        assert "Values: 1, 2, 3" in result
    
    def test_format_with_named_args(self):
        """Test message formatting with named arguments"""
        test_logger = Logger()
        output = StringIO()
        test_logger.add(output, level="INFO", format="{message}")
        
        test_logger.info("User {name}", name="John")
        test_logger.info("User {name} from {city}", name="Alice", city="NYC")
        test_logger.info("Price: ${amount:.2f}", amount=19.99)
        
        result = output.getvalue()
        assert "User John" in result
        assert "User Alice from NYC" in result
        assert "Price: $19.99" in result
    
    def test_format_with_mixed_args(self):
        """Test message formatting with both positional and named args"""
        test_logger = Logger()
        output = StringIO()
        test_logger.add(output, level="INFO", format="{message}")
        
        test_logger.info("User {} from {city}", "John", city="NYC")
        test_logger.info("Processing {} items for {user}", 10, user="admin")
        
        result = output.getvalue()
        assert "User John from NYC" in result
        assert "Processing 10 items for admin" in result
    
    def test_format_error_handling(self):
        """Test that formatting errors are handled gracefully"""
        test_logger = Logger()
        output = StringIO()
        test_logger.add(output, level="INFO", format="{message}")
        
        # Missing arguments - should not crash
        test_logger.info("User {} from {}", "John")  # Missing second arg
        test_logger.info("User {name} from {city}", name="John")  # Missing city
        
        result = output.getvalue()
        # Should still contain something (error message or partial format)
        assert len(result) > 0


class TestLoggerLevelFiltering:
    """Test level-based filtering"""
    
    def test_level_filtering(self):
        """Test that handlers respect level filtering"""
        test_logger = Logger()
        output = StringIO()
        test_logger.add(output, level="WARNING", format="{level.name} | {message}")
        
        test_logger.trace("Should not appear")
        test_logger.debug("Should not appear")
        test_logger.info("Should not appear")
        test_logger.warning("Should appear")
        test_logger.error("Should appear")
        test_logger.critical("Should appear")
        
        result = output.getvalue()
        assert "Should not appear" not in result
        assert result.count("Should appear") == 3
    
    def test_multiple_handlers_different_levels(self):
        """Test multiple handlers with different level filters"""
        test_logger = Logger()
        
        info_output = StringIO()
        error_output = StringIO()
        
        test_logger.add(info_output, level="INFO", format="{level.name}")
        test_logger.add(error_output, level="ERROR", format="{level.name}")
        
        test_logger.debug("Debug")
        test_logger.info("Info")
        test_logger.warning("Warning")
        test_logger.error("Error")
        test_logger.critical("Critical")
        
        info_result = info_output.getvalue()
        error_result = error_output.getvalue()
        
        # Info handler should get INFO, WARNING, ERROR, CRITICAL (4 messages)
        assert info_result.count("INFO") == 1
        assert info_result.count("WARNING") == 1
        assert info_result.count("ERROR") == 1
        assert info_result.count("CRITICAL") == 1
        assert "DEBUG" not in info_result
        
        # Error handler should get only ERROR and CRITICAL (2 messages)
        assert error_result.count("ERROR") == 1
        assert error_result.count("CRITICAL") == 1
        assert "INFO" not in error_result
        assert "WARNING" not in error_result


class TestLoggerHandlerManagement:
    """Test handler addition and removal"""
    
    def test_add_handler_returns_id(self):
        """Test that add() returns a handler ID"""
        test_logger = Logger()
        handler_id = test_logger.add(StringIO(), level="INFO")
        
        assert isinstance(handler_id, int)
        assert handler_id >= 0
    
    def test_add_multiple_handlers(self):
        """Test adding multiple handlers"""
        test_logger = Logger()
        
        id1 = test_logger.add(StringIO(), level="INFO")
        id2 = test_logger.add(StringIO(), level="DEBUG")
        id3 = test_logger.add(lambda msg: None, level="ERROR")
        
        assert id1 != id2 != id3
        assert len(test_logger.handlers) == 3
    
    def test_remove_handler_by_id(self):
        """Test removing a specific handler by ID"""
        test_logger = Logger()
        
        id1 = test_logger.add(StringIO(), level="INFO")
        id2 = test_logger.add(StringIO(), level="DEBUG")
        id3 = test_logger.add(StringIO(), level="ERROR")
        
        assert len(test_logger.handlers) == 3
        
        test_logger.remove(id2)
        assert len(test_logger.handlers) == 2
        
        # Should be able to remove others
        test_logger.remove(id1)
        test_logger.remove(id3)
        assert len(test_logger.handlers) == 0
    
    def test_remove_all_handlers(self):
        """Test removing all handlers"""
        test_logger = Logger()
        
        test_logger.add(StringIO(), level="INFO")
        test_logger.add(StringIO(), level="DEBUG")
        test_logger.add(StringIO(), level="ERROR")
        
        assert len(test_logger.handlers) == 3
        
        test_logger.remove()  # Remove all
        assert len(test_logger.handlers) == 0
    
    def test_remove_nonexistent_handler(self):
        """Test that removing nonexistent handler raises error"""
        test_logger = Logger()
        
        with pytest.raises(HandlerNotFoundError):
            test_logger.remove(99999)
    
    def test_add_stream_handler(self):
        """Test adding a stream handler"""
        test_logger = Logger()
        output = StringIO()
        
        handler_id = test_logger.add(output, level="INFO")
        test_logger.info("Test message")
        
        assert "Test message" in output.getvalue()
        test_logger.remove(handler_id)
    
    def test_add_file_handler(self, tmp_path):
        """Test adding a file handler"""
        test_logger = Logger()
        log_file = tmp_path / "test.log"
        
        handler_id = test_logger.add(str(log_file), level="INFO")
        test_logger.info("File test message")
        test_logger.remove(handler_id)
        
        assert log_file.exists()
        content = log_file.read_text()
        assert "File test message" in content
    
    def test_add_callable_handler(self):
        """Test adding a callable handler"""
        test_logger = Logger()
        messages = []
        
        handler_id = test_logger.add(lambda msg: messages.append(msg), level="INFO")
        test_logger.info("Callable test")
        test_logger.remove(handler_id)
        
        assert len(messages) == 1
        assert "Callable test" in messages[0]


class TestLoggerInvalidOperations:
    """Test invalid operations and error handling"""
    
    def test_invalid_level_string(self):
        """Test logging with invalid level string"""
        test_logger = Logger()
        
        with pytest.raises(InvalidLevelError):
            test_logger.log("INVALID_LEVEL", "message")
    
    def test_invalid_level_number(self):
        """Test logging with invalid level number"""
        test_logger = Logger()
        
        with pytest.raises(InvalidLevelError):
            test_logger.log(999, "message")
    
    def test_handler_with_invalid_level(self):
        """Test adding handler with invalid level"""
        test_logger = Logger()
        
        with pytest.raises(InvalidLevelError):
            test_logger.add(StringIO(), level="INVALID")


class TestLoggerExtraContext:
    """Test extra context in log calls"""
    
    def test_extra_in_log_call(self):
        """Test passing extra data in log calls"""
        test_logger = Logger()
        output = StringIO()
        test_logger.add(output, level="INFO", format="{message} | user={extra.user_id}")
        
        test_logger.info("User action", user_id=123)
        
        result = output.getvalue()
        assert "User action" in result
        assert "user=123" in result
    
    def test_multiple_extra_fields(self):
        """Test multiple extra fields"""
        test_logger = Logger()
        output = StringIO()
        test_logger.add(output, level="INFO", 
                       format="{message} | user={extra.user} | req={extra.request_id}")
        
        test_logger.info("Request processed", user="alice", request_id="req-456")
        
        result = output.getvalue()
        assert "user=alice" in result
        assert "req=req-456" in result


class TestLoggerThreadSafety:
    """Test thread-safety of logger operations"""
    
    def test_concurrent_handler_operations(self):
        """Test that handler add/remove is thread-safe"""
        import threading
        
        test_logger = Logger()
        handler_ids = []
        
        def add_handlers():
            for _ in range(10):
                hid = test_logger.add(StringIO(), level="INFO")
                handler_ids.append(hid)
        
        threads = [threading.Thread(target=add_handlers) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # Should have added 50 handlers (5 threads × 10 handlers)
        assert len(test_logger.handlers) == 50
        
        # Clean up
        test_logger.remove()
