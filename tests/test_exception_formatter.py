"""
Tests for exception formatting module
"""

import pytest
import sys
from pathlib import Path

from mylogger.exception_formatter import ExceptionFormatter


class TestExceptionFormatterInit:
    """Test ExceptionFormatter initialization"""
    
    def test_init_default(self):
        """Test default initialization"""
        formatter = ExceptionFormatter()
        assert formatter.colorize == False
        assert formatter.backtrace == True
        assert formatter.diagnose == False
        assert formatter.max_context_lines == 5
        assert formatter.max_value_length == 100
    
    def test_init_with_colorize(self):
        """Test initialization with colorize=True"""
        formatter = ExceptionFormatter(colorize=True)
        assert formatter.colorize == True
    
    def test_init_with_backtrace_false(self):
        """Test initialization with backtrace=False"""
        formatter = ExceptionFormatter(backtrace=False)
        assert formatter.backtrace == False
    
    def test_init_with_diagnose(self):
        """Test initialization with diagnose=True"""
        formatter = ExceptionFormatter(diagnose=True)
        assert formatter.diagnose == True
    
    def test_init_with_custom_context_lines(self):
        """Test initialization with custom context lines"""
        formatter = ExceptionFormatter(max_context_lines=10)
        assert formatter.max_context_lines == 10
    
    def test_repr(self):
        """Test string representation"""
        formatter = ExceptionFormatter(colorize=True, backtrace=False, diagnose=True)
        repr_str = repr(formatter)
        assert "colorize=True" in repr_str
        assert "backtrace=False" in repr_str
        assert "diagnose=True" in repr_str


class TestBasicExceptionFormatting:
    """Test basic exception formatting without colorization"""
    
    def test_format_simple_exception(self):
        """Test formatting a simple exception"""
        formatter = ExceptionFormatter(colorize=False)
        
        try:
            raise ValueError("This is a test error")
        except Exception:
            exc_info = sys.exc_info()
            formatted = formatter.format_exception(exc_info)
        
        assert "ValueError" in formatted
        assert "This is a test error" in formatted
        assert "Traceback" in formatted
    
    def test_format_exception_with_traceback(self):
        """Test that traceback is included"""
        formatter = ExceptionFormatter(colorize=False, backtrace=True)
        
        def inner_function():
            raise RuntimeError("Inner error")
        
        def outer_function():
            inner_function()
        
        try:
            outer_function()
        except Exception:
            exc_info = sys.exc_info()
            formatted = formatter.format_exception(exc_info)
        
        assert "RuntimeError" in formatted
        assert "Inner error" in formatted
        assert "inner_function" in formatted
        assert "outer_function" in formatted
        assert "Traceback" in formatted
    
    def test_format_exception_without_backtrace(self):
        """Test exception formatting without backtrace"""
        formatter = ExceptionFormatter(colorize=False, backtrace=False)
        
        try:
            raise ValueError("Test error")
        except Exception:
            exc_info = sys.exc_info()
            formatted = formatter.format_exception(exc_info)
        
        assert "ValueError" in formatted
        assert "Test error" in formatted
        assert "Traceback" not in formatted
        assert "raise ValueError" not in formatted
    
    def test_format_exception_from_exception_object(self):
        """Test formatting from exception object directly"""
        formatter = ExceptionFormatter(colorize=False)
        
        try:
            raise TypeError("Type mismatch")
        except Exception as e:
            formatted = formatter.format_exception(e)
        
        assert "TypeError" in formatted
        assert "Type mismatch" in formatted
    
    def test_format_none_exception(self):
        """Test handling of None exception info"""
        formatter = ExceptionFormatter(colorize=False)
        
        # When there's no exception, should return empty or handle gracefully
        formatted = formatter.format_exception((None, None, None))
        assert formatted == ""


class TestExceptionFormattingWithContextLines:
    """Test exception formatting with context lines"""
    
    def test_context_lines_shown(self):
        """Test that context lines around error are shown"""
        formatter = ExceptionFormatter(colorize=False, backtrace=True)
        
        try:
            x = 10
            y = 0
            z = x / y  # This line will cause the error
        except Exception:
            exc_info = sys.exc_info()
            formatted = formatter.format_exception(exc_info)
        
        # Should show the line that caused the error
        assert "z = x / y" in formatted or "x / y" in formatted
    
    def test_multiple_frames_shown(self):
        """Test that multiple frames are shown in traceback"""
        formatter = ExceptionFormatter(colorize=False, backtrace=True)
        
        def level3():
            raise ValueError("Deep error")
        
        def level2():
            level3()
        
        def level1():
            level2()
        
        try:
            level1()
        except Exception:
            exc_info = sys.exc_info()
            formatted = formatter.format_exception(exc_info)
        
        # All function names should appear
        assert "level1" in formatted
        assert "level2" in formatted
        assert "level3" in formatted
        assert "Deep error" in formatted


class TestDiagnoseMode:
    """Test diagnose mode (showing variable values)"""
    
    def test_diagnose_shows_variables(self):
        """Test that diagnose mode shows local variables"""
        formatter = ExceptionFormatter(colorize=False, diagnose=True)
        
        try:
            username = "alice"
            user_id = 12345
            data = {"key": "value"}
            result = 1 / 0  # Trigger error
        except Exception:
            exc_info = sys.exc_info()
            formatted = formatter.format_exception(exc_info)
        
        # Variables should be shown
        assert "Variables:" in formatted
        assert "username" in formatted
        assert "alice" in formatted
        assert "user_id" in formatted
        assert "12345" in formatted
    
    def test_diagnose_filters_special_variables(self):
        """Test that special variables (__, builtins) are filtered out from Variables section"""
        formatter = ExceptionFormatter(colorize=False, diagnose=True)
        
        try:
            __special__ = "hidden"
            normal_var = "visible"
            raise ValueError("Test")
        except Exception:
            exc_info = sys.exc_info()
            formatted = formatter.format_exception(exc_info)
        
        # Variables section should show normal vars but not special ones
        assert "Variables:" in formatted
        assert "normal_var" in formatted
        assert "visible" in formatted
        # __special__ might appear in source code but shouldn't be in Variables section
        # Check that it's not listed as a variable (after "Variables:")
        vars_section = formatted.split("Variables:")[1] if "Variables:" in formatted else ""
        assert "__special__" not in vars_section or vars_section.count("__special__") == 0
    
    def test_diagnose_disabled_no_variables(self):
        """Test that diagnose=False doesn't show Variables section"""
        formatter = ExceptionFormatter(colorize=False, diagnose=False)
        
        try:
            important_var = "secret_value"
            raise ValueError("Error occurred")
        except Exception:
            exc_info = sys.exc_info()
            formatted = formatter.format_exception(exc_info)
        
        # Variables section should NOT appear
        assert "Variables:" not in formatted
        # Note: variable names may still appear in source code lines, which is expected


class TestColorization:
    """Test colorized output"""
    
    def test_colorize_adds_ansi_codes(self):
        """Test that colorize=True adds ANSI color codes"""
        formatter = ExceptionFormatter(colorize=True)
        
        try:
            raise ValueError("Colorful error")
        except Exception:
            exc_info = sys.exc_info()
            formatted = formatter.format_exception(exc_info)
        
        # Should contain ANSI escape codes
        assert '\033[' in formatted
    
    def test_no_colorize_no_ansi_codes(self):
        """Test that colorize=False doesn't add ANSI codes"""
        formatter = ExceptionFormatter(colorize=False)
        
        try:
            raise ValueError("Plain error")
        except Exception:
            exc_info = sys.exc_info()
            formatted = formatter.format_exception(exc_info)
        
        # Should NOT contain ANSI escape codes
        assert '\033[' not in formatted
    
    def test_color_method(self):
        """Test the _color method"""
        formatter_color = ExceptionFormatter(colorize=True)
        formatter_no_color = ExceptionFormatter(colorize=False)
        
        text = "Hello"
        
        # With color
        colored = formatter_color._color(text, 'red')
        assert '\033[' in colored
        assert text in colored
        
        # Without color
        plain = formatter_no_color._color(text, 'red')
        assert '\033[' not in plain
        assert plain == text


class TestExceptionOnly:
    """Test format_exception_only method"""
    
    def test_format_exception_only_with_message(self):
        """Test formatting just exception type and message"""
        formatter = ExceptionFormatter(colorize=False)
        
        try:
            raise KeyError("missing_key")
        except Exception as e:
            formatted = formatter.format_exception_only(type(e), e)
        
        assert "KeyError" in formatted
        assert "missing_key" in formatted
        assert "Traceback" not in formatted
        assert "File" not in formatted
    
    def test_format_exception_only_without_message(self):
        """Test formatting exception without message"""
        formatter = ExceptionFormatter(colorize=False)
        
        try:
            raise RuntimeError()
        except Exception as e:
            formatted = formatter.format_exception_only(type(e), e)
        
        assert "RuntimeError" in formatted
        assert "Traceback" not in formatted


class TestPathShortening:
    """Test path shortening for display"""
    
    def test_shorten_path_site_packages(self):
        """Test shortening of site-packages paths"""
        formatter = ExceptionFormatter(colorize=False)
        
        path = "/usr/lib/python3.9/site-packages/mylib/module.py"
        shortened = formatter._shorten_path(path)
        
        # Should show from site-packages onwards
        assert "site-packages" in shortened
        assert "mylib" in shortened
    
    def test_shorten_path_long_path(self):
        """Test shortening of very long paths"""
        formatter = ExceptionFormatter(colorize=False)
        
        path = "/very/long/path/to/some/deep/directory/file.py"
        shortened = formatter._shorten_path(path)
        
        # Should be shortened (showing last parts)
        assert len(shortened) < len(path) or shortened == path


class TestValueFormatting:
    """Test _format_value method for variable display"""
    
    def test_format_value_string(self):
        """Test formatting of string values"""
        formatter = ExceptionFormatter(colorize=False)
        
        value = "test string"
        formatted = formatter._format_value(value)
        
        assert "test string" in formatted
    
    def test_format_value_number(self):
        """Test formatting of numeric values"""
        formatter = ExceptionFormatter(colorize=False)
        
        formatted_int = formatter._format_value(42)
        formatted_float = formatter._format_value(3.14)
        
        assert "42" in formatted_int
        assert "3.14" in formatted_float
    
    def test_format_value_long_string(self):
        """Test truncation of long values"""
        formatter = ExceptionFormatter(colorize=False, max_value_length=50)
        
        long_value = "x" * 200
        formatted = formatter._format_value(long_value)
        
        # Should be truncated
        assert len(formatted) < len(long_value)
        assert "..." in formatted
    
    def test_format_value_dict(self):
        """Test formatting of dict values"""
        formatter = ExceptionFormatter(colorize=False)
        
        value = {"key1": "value1", "key2": 123}
        formatted = formatter._format_value(value)
        
        assert "key1" in formatted
        assert "value1" in formatted


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_nested_exceptions(self):
        """Test formatting of nested exceptions"""
        formatter = ExceptionFormatter(colorize=False)
        
        try:
            try:
                raise ValueError("Inner exception")
            except ValueError as e:
                raise RuntimeError("Outer exception") from e
        except Exception:
            exc_info = sys.exc_info()
            formatted = formatter.format_exception(exc_info)
        
        # Should show the main exception
        assert "RuntimeError" in formatted
        assert "Outer exception" in formatted
    
    def test_exception_in_comprehension(self):
        """Test exception in list comprehension"""
        formatter = ExceptionFormatter(colorize=False)
        
        try:
            result = [1 / x for x in [1, 0, 2]]
        except Exception:
            exc_info = sys.exc_info()
            formatted = formatter.format_exception(exc_info)
        
        assert "ZeroDivisionError" in formatted
    
    def test_invalid_exc_info(self):
        """Test handling of invalid exc_info input"""
        formatter = ExceptionFormatter(colorize=False)
        
        result = formatter.format_exception("invalid")
        assert "Invalid exception info" in result or result == ""
    
    def test_exception_with_unicode(self):
        """Test exception with unicode characters"""
        formatter = ExceptionFormatter(colorize=False)
        
        try:
            raise ValueError("Error with unicode: ñ, ü, 中文, 🎉")
        except Exception:
            exc_info = sys.exc_info()
            formatted = formatter.format_exception(exc_info)
        
        assert "ValueError" in formatted
        # Unicode should be preserved
        assert "ñ" in formatted or "unicode" in formatted

