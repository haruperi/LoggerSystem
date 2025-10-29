"""
Tests for filter functionality
"""

import pytest
from io import StringIO
from pathlib import Path

from mylogger.filter import Filter, LevelFilter, ModuleFilter
from mylogger.logger import Logger
from mylogger.level import Level
from mylogger.record import LogRecord
from mylogger.handler import StreamHandler
from mylogger.formatter import Formatter


class TestFilterProtocol:
    """Test the Filter protocol and basic callable filters"""
    
    def test_simple_callable_filter(self):
        """Test a simple callable function as a filter"""
        # Create a logger with a filter that only allows ERROR and above
        logger = Logger()
        output = StringIO()
        
        # Filter function
        def error_only(record):
            return record.level.no >= 40
        
        logger.add(output, level="TRACE", filter=error_only)
        
        # Test logging
        logger.trace("Should not appear")
        logger.debug("Should not appear")
        logger.info("Should not appear")
        logger.warning("Should not appear")
        logger.error("Should appear")
        logger.critical("Should appear")
        
        result = output.getvalue()
        assert "Should not appear" not in result
        assert result.count("Should appear") == 2
    
    def test_lambda_filter(self):
        """Test using a lambda as a filter"""
        logger = Logger()
        output = StringIO()
        
        # Only log messages containing 'important'
        logger.add(output, level="TRACE", filter=lambda r: "important" in r.message)
        
        logger.info("Regular message")
        logger.info("This is important")
        logger.error("Another regular message")
        logger.error("Another important message")
        
        result = output.getvalue()
        assert "Regular message" not in result
        assert "Another regular message" not in result
        assert "This is important" in result
        assert "Another important message" in result
    
    def test_filter_with_extra_fields(self):
        """Test filtering based on extra fields"""
        logger = Logger()
        output = StringIO()
        
        # Filter for records with user='admin'
        def admin_only(record):
            return record.extra.get('user') == 'admin'
        
        logger.add(output, level="TRACE", filter=admin_only)
        
        logger.bind(user='admin').info("Admin action")
        logger.bind(user='guest').info("Guest action")
        logger.bind(user='admin').warning("Admin warning")
        
        result = output.getvalue()
        assert "Admin action" in result
        assert "Guest action" not in result
        assert "Admin warning" in result
    
    def test_filter_exception_handling(self):
        """Test that exceptions in filters don't break logging"""
        logger = Logger()
        output = StringIO()
        
        # Filter that raises an exception
        def broken_filter(record):
            raise ValueError("Filter error")
        
        logger.add(output, level="INFO", filter=broken_filter)
        
        # Should still log the message (filter exception is caught)
        logger.info("Test message")
        
        result = output.getvalue()
        assert "Test message" in result
    
    def test_filter_returns_false(self):
        """Test that filter returning False blocks the message"""
        logger = Logger()
        output = StringIO()
        
        # Filter that always returns False
        logger.add(output, level="TRACE", filter=lambda r: False)
        
        logger.info("Should not appear")
        logger.error("Should not appear")
        
        result = output.getvalue()
        assert result == ""
    
    def test_filter_returns_true(self):
        """Test that filter returning True allows the message"""
        logger = Logger()
        output = StringIO()
        
        # Filter that always returns True
        logger.add(output, level="TRACE", filter=lambda r: True)
        
        logger.trace("Should appear")
        logger.info("Should appear")
        
        result = output.getvalue()
        assert "Should appear" in result
        assert result.count("Should appear") == 2


class TestLevelFilter:
    """Test the LevelFilter class"""
    
    def test_level_filter_in_range(self):
        """Test filtering levels within a range"""
        filter_func = LevelFilter(min_level=20, max_level=40)
        
        # Create mock records
        trace_record = self._create_record("TRACE", "Trace message")
        debug_record = self._create_record("DEBUG", "Debug message")
        info_record = self._create_record("INFO", "Info message")
        warning_record = self._create_record("WARNING", "Warning message")
        error_record = self._create_record("ERROR", "Error message")
        critical_record = self._create_record("CRITICAL", "Critical message")
        
        # Test filter
        assert not filter_func(trace_record)  # 5 < 20
        assert not filter_func(debug_record)  # 10 < 20
        assert filter_func(info_record)       # 20 <= 20 <= 40
        assert filter_func(warning_record)    # 20 <= 30 <= 40
        assert filter_func(error_record)      # 20 <= 40 <= 40
        assert not filter_func(critical_record)  # 50 > 40
    
    def test_level_filter_min_only(self):
        """Test filtering with only minimum level"""
        filter_func = LevelFilter(min_level=30)  # WARNING and above
        
        info_record = self._create_record("INFO", "Info")
        warning_record = self._create_record("WARNING", "Warning")
        error_record = self._create_record("ERROR", "Error")
        
        assert not filter_func(info_record)
        assert filter_func(warning_record)
        assert filter_func(error_record)
    
    def test_level_filter_max_only(self):
        """Test filtering with only maximum level"""
        filter_func = LevelFilter(min_level=0, max_level=30)  # Up to WARNING
        
        info_record = self._create_record("INFO", "Info")
        warning_record = self._create_record("WARNING", "Warning")
        error_record = self._create_record("ERROR", "Error")
        
        assert filter_func(info_record)
        assert filter_func(warning_record)
        assert not filter_func(error_record)
    
    def test_level_filter_exact_level(self):
        """Test filtering for a single exact level"""
        filter_func = LevelFilter(min_level=30, max_level=30)  # Only WARNING
        
        info_record = self._create_record("INFO", "Info")
        warning_record = self._create_record("WARNING", "Warning")
        error_record = self._create_record("ERROR", "Error")
        
        assert not filter_func(info_record)
        assert filter_func(warning_record)
        assert not filter_func(error_record)
    
    def test_level_filter_integration(self):
        """Test LevelFilter integrated with logger"""
        logger = Logger()
        output = StringIO()
        
        # Only log INFO, SUCCESS, and WARNING (20-30)
        level_filter = LevelFilter(min_level=20, max_level=30)
        logger.add(output, level="TRACE", filter=level_filter)
        
        logger.trace("Trace")
        logger.debug("Debug")
        logger.info("Info")
        logger.success("Success")
        logger.warning("Warning")
        logger.error("Error")
        logger.critical("Critical")
        
        result = output.getvalue()
        assert "Trace" not in result
        assert "Debug" not in result
        assert "Info" in result
        assert "Success" in result
        assert "Warning" in result
        assert "Error" not in result
        assert "Critical" not in result
    
    def _create_record(self, level_name: str, message: str) -> LogRecord:
        """Helper to create a LogRecord"""
        from mylogger.level import DEFAULT_LEVELS
        from mylogger.record import FileInfo, ProcessInfo, ThreadInfo
        from datetime import datetime, timedelta
        import os
        import threading
        
        level = DEFAULT_LEVELS[level_name]
        
        return LogRecord(
            level=level,
            message=message,
            extra={},
            exception=None,
            file=FileInfo(name="test.py", path=str(Path(__file__).absolute())),
            function="test_function",
            line=1,
            module="test_module",
            name="test",
            process=ProcessInfo(id=os.getpid(), name="test_process"),
            thread=ThreadInfo(id=threading.get_ident(), name="test_thread"),
            time=datetime.now(),
            elapsed=timedelta(seconds=0)
        )


class TestModuleFilter:
    """Test the ModuleFilter class"""
    
    def test_module_filter_include(self):
        """Test including specific modules"""
        filter_func = ModuleFilter(modules=["module_a", "module_b"], exclude=False)
        
        record_a = self._create_record("module_a")
        record_b = self._create_record("module_b")
        record_c = self._create_record("module_c")
        
        assert filter_func(record_a)
        assert filter_func(record_b)
        assert not filter_func(record_c)
    
    def test_module_filter_exclude(self):
        """Test excluding specific modules"""
        filter_func = ModuleFilter(modules=["module_a", "module_b"], exclude=True)
        
        record_a = self._create_record("module_a")
        record_b = self._create_record("module_b")
        record_c = self._create_record("module_c")
        
        assert not filter_func(record_a)
        assert not filter_func(record_b)
        assert filter_func(record_c)
    
    def test_module_filter_single_module(self):
        """Test filtering a single module"""
        filter_func = ModuleFilter(modules=["test_module"], exclude=False)
        
        record_match = self._create_record("test_module")
        record_no_match = self._create_record("other_module")
        
        assert filter_func(record_match)
        assert not filter_func(record_no_match)
    
    def test_module_filter_empty_list(self):
        """Test module filter with empty module list"""
        filter_func_include = ModuleFilter(modules=[], exclude=False)
        filter_func_exclude = ModuleFilter(modules=[], exclude=True)
        
        record = self._create_record("any_module")
        
        # Empty include list = nothing passes
        assert not filter_func_include(record)
        # Empty exclude list = everything passes
        assert filter_func_exclude(record)
    
    def test_module_filter_integration(self):
        """Test ModuleFilter integrated with logger"""
        logger = Logger()
        output = StringIO()
        
        # Only log from test_module and main
        module_filter = ModuleFilter(modules=["test_module", "main"], exclude=False)
        logger.add(output, level="INFO", filter=module_filter)
        
        # We can't easily change the module name in the logger,
        # so this test will use the actual module name
        logger.info("Test message")
        
        result = output.getvalue()
        # The actual module will be "test_filter", not in our filter list
        # So this should not appear
        assert result == ""
    
    def _create_record(self, module_name: str) -> LogRecord:
        """Helper to create a LogRecord with specific module"""
        from mylogger.level import DEFAULT_LEVELS
        from mylogger.record import FileInfo, ProcessInfo, ThreadInfo
        from datetime import datetime, timedelta
        import os
        import threading
        
        return LogRecord(
            level=DEFAULT_LEVELS["INFO"],
            message="Test message",
            extra={},
            exception=None,
            file=FileInfo(name="test.py", path=str(Path(__file__).absolute())),
            function="test_function",
            line=1,
            module=module_name,
            name="test",
            process=ProcessInfo(id=os.getpid(), name="test_process"),
            thread=ThreadInfo(id=threading.get_ident(), name="test_thread"),
            time=datetime.now(),
            elapsed=timedelta(seconds=0)
        )


class TestCustomFilters:
    """Test creating custom filter classes"""
    
    def test_custom_filter_class(self):
        """Test a custom filter class"""
        
        class KeywordFilter:
            """Filter that checks if message contains any of the keywords"""
            
            def __init__(self, keywords):
                self.keywords = keywords
            
            def __call__(self, record):
                return any(kw in record.message for kw in self.keywords)
        
        filter_func = KeywordFilter(keywords=["error", "warning", "critical"])
        
        # Create records
        record1 = self._create_record("This is an error message")
        record2 = self._create_record("This is a normal message")
        record3 = self._create_record("This is a warning")
        record4 = self._create_record("Just info")
        
        assert filter_func(record1)
        assert not filter_func(record2)
        assert filter_func(record3)
        assert not filter_func(record4)
    
    def test_time_based_filter(self):
        """Test a custom time-based filter"""
        from datetime import datetime, timedelta
        
        class TimeRangeFilter:
            """Filter that only logs during certain hours"""
            
            def __init__(self, start_hour, end_hour):
                self.start_hour = start_hour
                self.end_hour = end_hour
            
            def __call__(self, record):
                hour = record.time.hour
                return self.start_hour <= hour < self.end_hour
        
        # Create filter for 9 AM to 5 PM
        filter_func = TimeRangeFilter(9, 17)
        
        # Create records with different times
        morning_time = datetime(2025, 1, 1, 10, 0)  # 10 AM - should pass
        evening_time = datetime(2025, 1, 1, 18, 0)  # 6 PM - should not pass
        night_time = datetime(2025, 1, 1, 23, 0)    # 11 PM - should not pass
        
        record_morning = self._create_record("Morning", time=morning_time)
        record_evening = self._create_record("Evening", time=evening_time)
        record_night = self._create_record("Night", time=night_time)
        
        assert filter_func(record_morning)
        assert not filter_func(record_evening)
        assert not filter_func(record_night)
    
    def test_threshold_filter(self):
        """Test a custom filter with configurable threshold"""
        
        class CounterFilter:
            """Filter that only allows every Nth message"""
            
            def __init__(self, n):
                self.n = n
                self.count = 0
            
            def __call__(self, record):
                self.count += 1
                return self.count % self.n == 0
        
        filter_func = CounterFilter(n=3)
        
        # Test: only every 3rd message should pass
        for i in range(10):
            record = self._create_record(f"Message {i}")
            result = filter_func(record)
            expected = (i + 1) % 3 == 0
            assert result == expected
    
    def _create_record(self, message: str, time=None) -> LogRecord:
        """Helper to create a LogRecord"""
        from mylogger.level import DEFAULT_LEVELS
        from mylogger.record import FileInfo, ProcessInfo, ThreadInfo
        from datetime import datetime, timedelta
        import os
        import threading
        
        return LogRecord(
            level=DEFAULT_LEVELS["INFO"],
            message=message,
            extra={},
            exception=None,
            file=FileInfo(name="test.py", path=str(Path(__file__).absolute())),
            function="test_function",
            line=1,
            module="test_module",
            name="test",
            process=ProcessInfo(id=os.getpid(), name="test_process"),
            thread=ThreadInfo(id=threading.get_ident(), name="test_thread"),
            time=time or datetime.now(),
            elapsed=timedelta(seconds=0)
        )


class TestCombiningFilters:
    """Test combining multiple filters"""
    
    def test_and_filter_combiner(self):
        """Test combining filters with AND logic"""
        
        class AndFilter:
            """Combine multiple filters with AND logic"""
            
            def __init__(self, *filters):
                self.filters = filters
            
            def __call__(self, record):
                return all(f(record) for f in self.filters)
        
        # Create two filters
        level_filter = LevelFilter(min_level=20, max_level=40)  # INFO to ERROR
        module_filter = ModuleFilter(modules=["test_module"], exclude=False)
        
        # Combine with AND
        combined = AndFilter(level_filter, module_filter)
        
        # Test records
        record_pass = self._create_record("INFO", "test_module")
        record_fail_level = self._create_record("TRACE", "test_module")
        record_fail_module = self._create_record("INFO", "other_module")
        
        assert combined(record_pass)
        assert not combined(record_fail_level)
        assert not combined(record_fail_module)
    
    def test_or_filter_combiner(self):
        """Test combining filters with OR logic"""
        
        class OrFilter:
            """Combine multiple filters with OR logic"""
            
            def __init__(self, *filters):
                self.filters = filters
            
            def __call__(self, record):
                return any(f(record) for f in self.filters)
        
        # Create two filters
        level_filter = LevelFilter(min_level=40)  # ERROR and above
        keyword_filter = lambda r: "urgent" in r.message.lower()
        
        # Combine with OR
        combined = OrFilter(level_filter, keyword_filter)
        
        # Test records
        record_error = self._create_record("ERROR", "test_module", "Regular error")
        record_urgent = self._create_record("INFO", "test_module", "Urgent info")
        record_neither = self._create_record("INFO", "test_module", "Regular info")
        
        assert combined(record_error)      # Passes level filter
        assert combined(record_urgent)     # Passes keyword filter
        assert not combined(record_neither)  # Passes neither
    
    def test_not_filter_combiner(self):
        """Test negating a filter"""
        
        class NotFilter:
            """Negate a filter"""
            
            def __init__(self, filter_func):
                self.filter = filter_func
            
            def __call__(self, record):
                return not self.filter(record)
        
        # Create a filter
        module_filter = ModuleFilter(modules=["test_module"], exclude=False)
        
        # Negate it
        not_filter = NotFilter(module_filter)
        
        # Test records
        record_test = self._create_record("INFO", "test_module")
        record_other = self._create_record("INFO", "other_module")
        
        assert not not_filter(record_test)  # Original would pass, negated fails
        assert not_filter(record_other)     # Original would fail, negated passes
    
    def test_complex_filter_combination(self):
        """Test complex filter combination"""
        
        class AndFilter:
            def __init__(self, *filters):
                self.filters = filters
            def __call__(self, record):
                return all(f(record) for f in self.filters)
        
        class OrFilter:
            def __init__(self, *filters):
                self.filters = filters
            def __call__(self, record):
                return any(f(record) for f in self.filters)
        
        # Create complex filter:
        # (ERROR or CRITICAL) AND (module_a or module_b) AND (contains "important")
        
        error_or_critical = OrFilter(
            lambda r: r.level.name == "ERROR",
            lambda r: r.level.name == "CRITICAL"
        )
        
        module_a_or_b = ModuleFilter(modules=["module_a", "module_b"], exclude=False)
        
        contains_important = lambda r: "important" in r.message
        
        complex_filter = AndFilter(error_or_critical, module_a_or_b, contains_important)
        
        # Test with mock records directly
        record_pass = self._create_record("ERROR", "module_a", "An important error")
        record_fail_level = self._create_record("INFO", "module_a", "An important message")
        record_fail_module = self._create_record("ERROR", "module_c", "An important error")
        record_fail_keyword = self._create_record("ERROR", "module_a", "Regular error")
        
        assert complex_filter(record_pass)
        assert not complex_filter(record_fail_level)
        assert not complex_filter(record_fail_module)
        assert not complex_filter(record_fail_keyword)
    
    def _create_record(self, level_name: str, module: str, message: str = "Test") -> LogRecord:
        """Helper to create a LogRecord"""
        from mylogger.level import DEFAULT_LEVELS
        from mylogger.record import FileInfo, ProcessInfo, ThreadInfo
        from datetime import datetime, timedelta
        import os
        import threading
        
        return LogRecord(
            level=DEFAULT_LEVELS[level_name],
            message=message,
            extra={},
            exception=None,
            file=FileInfo(name="test.py", path=str(Path(__file__).absolute())),
            function="test_function",
            line=1,
            module=module,
            name="test",
            process=ProcessInfo(id=os.getpid(), name="test_process"),
            thread=ThreadInfo(id=threading.get_ident(), name="test_thread"),
            time=datetime.now(),
            elapsed=timedelta(seconds=0)
        )


class TestMultipleHandlersWithDifferentFilters:
    """Test using different filters on different handlers"""
    
    def test_different_filters_per_handler(self):
        """Test that each handler can have its own filter"""
        logger = Logger()
        
        output_info = StringIO()
        output_errors = StringIO()
        output_urgent = StringIO()
        
        # Handler 1: Only INFO level
        info_filter = lambda r: r.level.name == "INFO"
        logger.add(output_info, level="TRACE", filter=info_filter, format="{level} | {message}")
        
        # Handler 2: Only ERROR and CRITICAL
        error_filter = LevelFilter(min_level=40)
        logger.add(output_errors, level="TRACE", filter=error_filter, format="{level} | {message}")
        
        # Handler 3: Only messages with "urgent"
        urgent_filter = lambda r: "urgent" in r.message.lower()
        logger.add(output_urgent, level="TRACE", filter=urgent_filter, format="{level} | {message}")
        
        # Log various messages
        logger.info("Regular info")
        logger.info("Urgent info")
        logger.error("Regular error")
        logger.error("Urgent error")
        logger.warning("Urgent warning")
        
        # Check outputs
        info_result = output_info.getvalue()
        errors_result = output_errors.getvalue()
        urgent_result = output_urgent.getvalue()
        
        # Handler 1 should have both INFO messages
        assert "Regular info" in info_result
        assert "Urgent info" in info_result
        assert "error" not in info_result.lower() or "error" not in info_result  # no ERROR level
        
        # Handler 2 should have both ERROR messages
        assert "Regular error" in errors_result
        assert "Urgent error" in errors_result
        assert "info" not in errors_result.lower() or "info" not in errors_result  # no INFO
        
        # Handler 3 should have all urgent messages
        assert "Urgent info" in urgent_result
        assert "Urgent error" in urgent_result
        assert "Urgent warning" in urgent_result
        assert "Regular" not in urgent_result
    
    def test_handler_with_no_filter(self):
        """Test that handlers without filters log everything above their level"""
        logger = Logger()
        
        output_with_filter = StringIO()
        output_no_filter = StringIO()
        
        # Handler with filter
        logger.add(output_with_filter, level="INFO", filter=lambda r: r.level.name == "ERROR")
        
        # Handler without filter
        logger.add(output_no_filter, level="INFO")
        
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        
        # With filter should only have ERROR
        with_filter_result = output_with_filter.getvalue()
        assert "Info message" not in with_filter_result
        assert "Warning message" not in with_filter_result
        assert "Error message" in with_filter_result
        
        # Without filter should have all messages at INFO and above
        no_filter_result = output_no_filter.getvalue()
        assert "Info message" in no_filter_result
        assert "Warning message" in no_filter_result
        assert "Error message" in no_filter_result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

