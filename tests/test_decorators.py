"""
Tests for decorators and utilities (Day 16)
"""

import pytest
from io import StringIO
import sys

from mylogger import Logger
from mylogger.level import Level


class TestCatchDecorator:
    """Test the @logger.catch decorator"""

    def test_catch_basic(self):
        """Test basic catch decorator functionality"""
        logger = Logger()
        output = StringIO()
        logger.add(output, level="TRACE", format="{level} | {message}")

        @logger.catch()
        def risky_function():
            return 1 / 0

        # Should not raise, should return None
        result = risky_function()
        assert result is None

        # Should have logged the exception
        log_output = output.getvalue()
        assert "ERROR" in log_output
        assert "An error occurred" in log_output

    def test_catch_with_custom_level(self):
        """Test catch with custom log level"""
        logger = Logger()
        output = StringIO()
        logger.add(output, level="TRACE", format="{level} | {message}")

        @logger.catch(level="WARNING")
        def risky_function():
            raise ValueError("Test error")

        risky_function()

        log_output = output.getvalue()
        assert "WARNING" in log_output

    def test_catch_with_custom_message(self):
        """Test catch with custom message"""
        logger = Logger()
        output = StringIO()
        logger.add(output, level="TRACE", format="{level} | {message}")

        @logger.catch(message="Custom error message")
        def risky_function():
            raise RuntimeError("Original error")

        risky_function()

        log_output = output.getvalue()
        assert "Custom error message" in log_output

    def test_catch_specific_exception(self):
        """Test catching only specific exception types"""
        logger = Logger()
        output = StringIO()
        logger.add(output, level="TRACE", format="{level} | {message}")

        @logger.catch(exception=ValueError)
        def function_with_valueerror():
            raise ValueError("Value error")

        @logger.catch(exception=ValueError)
        def function_with_typeerror():
            raise TypeError("Type error")

        # ValueError should be caught
        result1 = function_with_valueerror()
        assert result1 is None

        # TypeError should not be caught
        with pytest.raises(TypeError):
            function_with_typeerror()

    def test_catch_reraise(self):
        """Test catch with reraise=True"""
        logger = Logger()
        output = StringIO()
        logger.add(output, level="TRACE", format="{level} | {message}")

        @logger.catch(reraise=True)
        def risky_function():
            raise ValueError("Test error")

        # Should log AND reraise
        with pytest.raises(ValueError):
            risky_function()

        # Should still have logged
        log_output = output.getvalue()
        assert "ERROR" in log_output

    def test_catch_with_onerror_callback(self):
        """Test catch with onerror callback"""
        logger = Logger()
        output = StringIO()
        logger.add(output, level="TRACE", format="{level} | {message}")

        callback_called = []

        def error_callback(exc):
            callback_called.append(exc)

        @logger.catch(onerror=error_callback)
        def risky_function():
            raise ValueError("Test error")

        risky_function()

        assert len(callback_called) == 1
        assert isinstance(callback_called[0], ValueError)

    def test_catch_preserves_function_metadata(self):
        """Test that catch preserves function name and docstring"""
        logger = Logger()

        @logger.catch()
        def my_function():
            """This is my function"""
            pass

        assert my_function.__name__ == "my_function"
        assert my_function.__doc__ == "This is my function"

    def test_catch_with_return_value(self):
        """Test that catch returns function's return value on success"""
        logger = Logger()
        output = StringIO()
        logger.add(output, level="TRACE")

        @logger.catch()
        def successful_function():
            return "success"

        result = successful_function()
        assert result == "success"


class TestOptMethod:
    """Test the logger.opt() method"""

    def test_opt_with_exception_true(self):
        """Test opt with exception=True to capture current exception"""
        logger = Logger()
        output = StringIO()
        logger.add(output, level="TRACE", format="{level} | {message}")

        try:
            1 / 0
        except:
            logger.opt(exception=True).error("Division failed")

        log_output = output.getvalue()
        assert "ERROR" in log_output
        assert "Division failed" in log_output

    def test_opt_with_exception_instance(self):
        """Test opt with specific exception instance"""
        logger = Logger()
        output = StringIO()
        logger.add(output, level="TRACE", format="{level} | {message}")

        exc = ValueError("Test exception")
        logger.opt(exception=exc).error("Error occurred")

        log_output = output.getvalue()
        assert "ERROR" in log_output
        assert "Error occurred" in log_output

    def test_opt_depth_adjustment(self):
        """Test opt with depth adjustment for stack frames"""
        logger = Logger()
        output = StringIO()
        logger.add(output, level="TRACE", format="{function} | {message}")

        def wrapper_function():
            # Without depth adjustment, it logs from wrapper_function
            logger.info("From wrapper")
            # With depth=1, it should log from the caller
            logger.opt(depth=1).info("From caller")

        wrapper_function()

        log_output = output.getvalue()
        assert "wrapper_function" in log_output
        # The second log with depth=1 should show the test function name
        lines = log_output.strip().split("\n")
        assert len(lines) == 2

    def test_opt_returns_opt_logger(self):
        """Test that opt returns an OptLogger instance"""
        logger = Logger()
        opt_logger = logger.opt(exception=True)

        assert hasattr(opt_logger, "info")
        assert hasattr(opt_logger, "error")
        assert hasattr(opt_logger, "debug")

    def test_opt_with_all_log_levels(self):
        """Test that OptLogger supports all log levels"""
        logger = Logger()
        output = StringIO()
        logger.add(output, level="TRACE", format="{level} | {message}")

        opt_logger = logger.opt()

        opt_logger.trace("Trace message")
        opt_logger.debug("Debug message")
        opt_logger.info("Info message")
        opt_logger.success("Success message")
        opt_logger.warning("Warning message")
        opt_logger.error("Error message")
        opt_logger.critical("Critical message")

        log_output = output.getvalue()
        assert "TRACE" in log_output
        assert "DEBUG" in log_output
        assert "INFO" in log_output
        assert "SUCCESS" in log_output
        assert "WARNING" in log_output
        assert "ERROR" in log_output
        assert "CRITICAL" in log_output


class TestAddLevel:
    """Test the add_level() method"""

    def test_add_custom_level(self):
        """Test adding a custom log level"""
        logger = Logger()
        logger.add_level("VERBOSE", 15, color="cyan", icon="🔍")

        # Check level was added
        assert "VERBOSE" in logger.levels
        assert logger.levels["VERBOSE"].no == 15
        assert logger.levels["VERBOSE"].color == "cyan"
        assert logger.levels["VERBOSE"].icon == "🔍"

    def test_add_level_creates_method(self):
        """Test that add_level creates a logging method"""
        logger = Logger()
        logger.add_level("NOTICE", 22, color="blue")

        # Check method was created
        assert hasattr(logger, "notice")
        assert callable(logger.notice)

    def test_custom_level_logging(self):
        """Test logging with custom level"""
        logger = Logger()
        output = StringIO()
        logger.add(output, level="TRACE", format="{level} | {message}")

        logger.add_level("VERBOSE", 15, color="cyan")
        logger.verbose("Verbose message")

        log_output = output.getvalue()
        assert "VERBOSE" in log_output
        assert "Verbose message" in log_output

    def test_multiple_custom_levels(self):
        """Test adding multiple custom levels"""
        logger = Logger()
        output = StringIO()
        logger.add(output, level="TRACE", format="{level} | {message}")

        logger.add_level("NOTICE", 22, color="blue")
        logger.add_level("AUDIT", 45, color="magenta")

        logger.notice("Notice message")
        logger.audit("Audit message")

        log_output = output.getvalue()
        assert "NOTICE" in log_output
        assert "AUDIT" in log_output

    def test_custom_level_ordering(self):
        """Test that custom levels respect numeric ordering"""
        logger = Logger()
        output = StringIO()

        logger.add_level("VERBOSE", 15)  # Between DEBUG(10) and INFO(20)
        logger.add(output, level="VERBOSE", format="{level} | {message}")

        # DEBUG should not log (10 < 15)
        logger.debug("Debug message")
        # VERBOSE should log (15 >= 15)
        logger.verbose("Verbose message")
        # INFO should log (20 >= 15)
        logger.info("Info message")

        log_output = output.getvalue()
        assert "Debug message" not in log_output
        assert "Verbose message" in log_output
        assert "Info message" in log_output


class TestDisableEnable:
    """Test the disable() and enable() methods"""

    def test_disable_module(self):
        """Test disabling a specific module"""
        logger = Logger()
        output = StringIO()
        logger.add(output, level="TRACE", format="{module} | {level} | {message}")

        # First log to see what the module name is
        logger.info("First message")
        log_output = output.getvalue()

        # Extract the module name from the log
        module_name = log_output.split(" | ")[0]

        # Clear output
        output.truncate(0)
        output.seek(0)

        # Disable this test module
        logger.disable(module_name)

        logger.info("Should not appear")

        log_output = output.getvalue()
        # The log should be empty because this module is disabled
        assert log_output == ""

    def test_enable_module(self):
        """Test enabling a previously disabled module"""
        logger = Logger()
        output = StringIO()
        logger.add(output, level="TRACE", format="{level} | {message}")

        # Disable then enable
        logger.disable("test_decorators")
        logger.enable("test_decorators")

        logger.info("Should appear")

        log_output = output.getvalue()
        assert "Should appear" in log_output

    def test_disable_multiple_modules(self):
        """Test disabling multiple modules"""
        logger = Logger()

        logger.disable("module1")
        logger.disable("module2")
        logger.disable("module3")

        assert "module1" in logger._disabled
        assert "module2" in logger._disabled
        assert "module3" in logger._disabled

    def test_enable_nonexistent_module(self):
        """Test enabling a module that wasn't disabled (should not error)"""
        logger = Logger()

        # Should not raise an error
        logger.enable("nonexistent_module")

        assert "nonexistent_module" not in logger._disabled


class TestCombinedFeatures:
    """Test combining multiple Day 16 features"""

    def test_catch_with_custom_level(self):
        """Test catch decorator with custom level"""
        logger = Logger()
        output = StringIO()
        logger.add(output, level="TRACE", format="{level} | {message}")

        logger.add_level("SEVERE", 45)

        @logger.catch(level="SEVERE")
        def risky_function():
            raise ValueError("Test error")

        risky_function()

        log_output = output.getvalue()
        assert "SEVERE" in log_output

    def test_opt_with_custom_level(self):
        """Test opt with custom level"""
        logger = Logger()
        output = StringIO()
        logger.add(output, level="TRACE", format="{level} | {message}")

        logger.add_level("VERBOSE", 15)

        # Use opt with log() method and the custom level
        logger.opt().log("VERBOSE", "Verbose with opt")

        log_output = output.getvalue()
        assert "VERBOSE" in log_output


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
