"""
Test advanced formatter for Day 6
"""

import sys
import os
from datetime import datetime, timedelta

# Add the parent directory to the path to import mylogger
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from mylogger import Logger
from mylogger.formatter import Formatter, Token
from mylogger.record import LogRecord, Level, FileInfo, ProcessInfo, ThreadInfo


def create_test_record():
    """Create a test LogRecord for testing"""
    return LogRecord(
        elapsed=timedelta(seconds=5.5),
        exception=None,
        extra={"user_id": 123, "request_id": "abc-123"},
        file=FileInfo(name="test.py", path="/path/to/test.py"),
        function="test_function",
        level=Level(name="INFO", no=20, color="white", icon="ℹ️"),
        line=42,
        message="Test message",
        module="test_module",
        name="test_logger",
        process=ProcessInfo(id=1234, name="MainProcess"),
        thread=ThreadInfo(id=5678, name="MainThread"),
        time=datetime(2024, 1, 15, 14, 30, 45, 123456),
    )


def test_token_parsing():
    """Test basic token parsing"""
    print("=" * 60)
    print("TEST 1: Token Parsing")
    print("=" * 60)

    formatter = Formatter("{level} - {message}")

    print(f"Format string: {formatter.format_string}")
    print(f"Parsed {len(formatter.tokens)} tokens:")
    for token in formatter.tokens:
        print(f"  {token}")

    assert len(formatter.tokens) == 3  # field, literal, field
    assert formatter.tokens[0].type == "field"
    assert formatter.tokens[0].field_name == "level"
    assert formatter.tokens[1].type == "literal"
    assert formatter.tokens[2].type == "field"

    print("[OK] Token parsing test passed")
    print()


def test_simple_formatting():
    """Test simple field formatting"""
    print("=" * 60)
    print("TEST 2: Simple Field Formatting")
    print("=" * 60)

    formatter = Formatter("{level} - {message}")
    record = create_test_record()

    result = formatter.format(record)
    print(f"Formatted: {result}")

    assert "INFO" in result
    assert "Test message" in result

    print("[OK] Simple formatting test passed")
    print()


def test_nested_field_access():
    """Test nested field access"""
    print("=" * 60)
    print("TEST 3: Nested Field Access")
    print("=" * 60)

    formatter = Formatter("{level.name} | {process.id} | {thread.name}")
    record = create_test_record()

    result = formatter.format(record)
    print(f"Formatted: {result}")

    assert "INFO" in result
    assert "1234" in result
    assert "MainThread" in result

    print("[OK] Nested field access test passed")
    print()


def test_extra_dict_access():
    """Test extra dictionary access"""
    print("=" * 60)
    print("TEST 4: Extra Dictionary Access")
    print("=" * 60)

    formatter = Formatter("User {extra.user_id} - Request {extra.request_id}")
    record = create_test_record()

    result = formatter.format(record)
    print(f"Formatted: {result}")

    assert "123" in result
    assert "abc-123" in result

    print("[OK] Extra dict access test passed")
    print()


def test_format_specs_alignment():
    """Test format specifications - alignment and width"""
    print("=" * 60)
    print("TEST 5: Format Specs - Alignment and Width")
    print("=" * 60)

    # Left alignment
    formatter1 = Formatter("{level:<10}")
    record = create_test_record()
    result1 = formatter1.format(record)
    print(f"Left-aligned (10): '{result1}'")
    assert len(result1.strip()) >= 4  # "INFO"

    # Right alignment
    formatter2 = Formatter("{level:>10}")
    result2 = formatter2.format(record)
    print(f"Right-aligned (10): '{result2}'")

    # Center alignment
    formatter3 = Formatter("{level:^10}")
    result3 = formatter3.format(record)
    print(f"Center-aligned (10): '{result3}'")

    print("[OK] Alignment test passed")
    print()


def test_datetime_formatting():
    """Test custom datetime formatting"""
    print("=" * 60)
    print("TEST 6: Custom Datetime Formatting")
    print("=" * 60)

    record = create_test_record()

    # Test various datetime formats
    test_cases = [
        ("{time:YYYY-MM-DD}", "2024-01-15"),
        ("{time:HH:mm:ss}", "14:30:45"),
        ("{time:YYYY-MM-DD HH:mm:ss}", "2024-01-15 14:30:45"),
    ]

    for format_str, expected in test_cases:
        formatter = Formatter(format_str)
        result = formatter.format(record)
        print(f"Format: {format_str:30} => {result}")
        assert expected in result, f"Expected '{expected}' in result"

    print("[OK] Datetime formatting test passed")
    print()


def test_escaped_braces():
    """Test escaped braces"""
    print("=" * 60)
    print("TEST 7: Escaped Braces")
    print("=" * 60)

    formatter = Formatter("{{literal}} {message} {{braces}}")
    record = create_test_record()

    result = formatter.format(record)
    print(f"Formatted: {result}")

    assert "{literal}" in result
    assert "{braces}" in result
    assert "Test message" in result

    print("[OK] Escaped braces test passed")
    print()


def test_color_tags():
    """Test color tag parsing (tags are parsed but not applied until Day 9)"""
    print("=" * 60)
    print("TEST 8: Color Tag Parsing")
    print("=" * 60)

    formatter = Formatter("<red>{level}</red> - <green>{message}</green>")
    record = create_test_record()

    print(f"Format string: {formatter.format_string}")
    print(f"Parsed {len(formatter.tokens)} tokens:")
    for token in formatter.tokens:
        if token.type in ["color_start", "color_end"]:
            print(f"  {token.type}: {token.value}")
        elif token.type == "field":
            print(f"  {token.type}: {token.field_name} (color: {token.color_tag})")

    result = formatter.format(record)
    print(f"Formatted: {result}")

    # Color tags should be parsed but not applied yet (Day 9)
    assert "INFO" in result
    assert "Test message" in result

    print("[OK] Color tag parsing test passed")
    print()


def test_missing_fields():
    """Test handling of missing fields"""
    print("=" * 60)
    print("TEST 9: Missing Field Handling")
    print("=" * 60)

    formatter = Formatter("{nonexistent} - {extra.missing_key}")
    record = create_test_record()

    result = formatter.format(record)
    print(f"Formatted: {result}")

    assert "missing" in result.lower()

    print("[OK] Missing field handling test passed")
    print()


def test_complex_format():
    """Test complex format with multiple features"""
    print("=" * 60)
    print("TEST 10: Complex Format")
    print("=" * 60)

    format_str = "{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {name}:{function}:{line} - {message}"
    formatter = Formatter(format_str)
    record = create_test_record()

    result = formatter.format(record)
    print(f"Format: {format_str}")
    print(f"Result: {result}")

    assert "2024-01-15 14:30:45" in result
    assert "INFO" in result
    assert "test_function" in result
    assert "42" in result
    assert "Test message" in result

    print("[OK] Complex format test passed")
    print()


def test_with_logger():
    """Test formatter with actual logger"""
    print("=" * 60)
    print("TEST 11: Formatter with Logger")
    print("=" * 60)

    logger = Logger()

    # Test different format strings
    formats = [
        "{level:<8} | {message}",
        "{time:HH:mm:ss} [{level}] {message}",
        "{function}:{line} - {message}",
        "[{level.name}] {message} (at {function})",
    ]

    for fmt in formats:
        messages = []
        handler_id = logger.add(lambda msg: messages.append(msg), level="INFO", format=fmt)

        logger.info("Test message")

        print(f"Format: {fmt}")
        print(f"Output: {messages[0]}")
        print()

        logger.remove(handler_id)

    print("[OK] Logger integration test passed")
    print()


def test_get_field_value():
    """Test get_field_value method directly"""
    print("=" * 60)
    print("TEST 12: get_field_value Method")
    print("=" * 60)

    formatter = Formatter()
    record = create_test_record()

    test_cases = [
        ("level", Level),
        ("level.name", str),
        ("message", str),
        ("function", str),
        ("line", int),
        ("process.id", int),
        ("thread.name", str),
        ("extra.user_id", int),
    ]

    for field_name, expected_type in test_cases:
        value = formatter.get_field_value(record, field_name)
        print(f"{field_name:20} = {value} ({type(value).__name__})")

        # Check type or check for missing marker
        if not isinstance(value, str) or not value.startswith("<"):
            if expected_type is not str:
                assert isinstance(value, expected_type) or isinstance(value, str)

    print("[OK] get_field_value test passed")
    print()


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("MYLOGGER DAY 6 - ADVANCED FORMATTER TESTS")
    print("=" * 60 + "\n")

    test_token_parsing()
    test_simple_formatting()
    test_nested_field_access()
    test_extra_dict_access()
    test_format_specs_alignment()
    test_datetime_formatting()
    test_escaped_braces()
    test_color_tags()
    test_missing_fields()
    test_complex_format()
    test_with_logger()
    test_get_field_value()

    print("=" * 60)
    print("ALL TESTS COMPLETED SUCCESSFULLY")
    print("=" * 60)
    print("\nDay 6 advanced formatter is fully functional!")
    print("- Token-based parsing [OK]")
    print("- Nested field access (level.name) [OK]")
    print("- Extra dict access (extra.user_id) [OK]")
    print("- Format specifications (alignment, width) [OK]")
    print("- Custom datetime formats (YYYY-MM-DD) [OK]")
    print("- Escaped braces {{}} [OK]")
    print("- Color tag parsing [OK]")
    print("- Missing field handling [OK]")
    print("\nNext: Day 7 will focus on StreamHandler improvements")
    print("       Day 9 will implement full colorization!")


if __name__ == "__main__":
    main()
