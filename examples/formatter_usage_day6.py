"""
Advanced Formatter Examples - Day 6

This example demonstrates the advanced formatting features implemented in Day 6:
- Token-based parsing
- Nested field access
- Format specifications
- Custom datetime formats
- Escaped braces
- Color tag parsing (colors applied in Day 9)
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from mylogger import Logger


def example_1_basic_formatting():
    """Example 1: Basic field formatting"""
    print("\n" + "=" * 70)
    print("Example 1: Basic Field Formatting")
    print("=" * 70)
    
    logger = Logger()
    
    # Simple format
    logger.add(sys.stderr, format="{level} - {message}")
    logger.info("Simple format")
    
    logger.remove()
    print()


def example_2_nested_access():
    """Example 2: Nested field access"""
    print("\n" + "=" * 70)
    print("Example 2: Nested Field Access")
    print("=" * 70)
    
    logger = Logger()
    
    # Access nested fields
    logger.add(sys.stderr, format="{level.name} | {process.id} | {thread.name}")
    logger.info("Nested field access")
    
    logger.remove()
    print()


def example_3_extra_dict():
    """Example 3: Extra dictionary access"""
    print("\n" + "=" * 70)
    print("Example 3: Extra Dictionary Access")
    print("=" * 70)
    
    logger = Logger()
    
    # Access extra dictionary fields
    logger.add(sys.stderr, format="[{level}] {message} (user: {extra.user_id})")
    logger.info("User logged in", user_id=12345)
    logger.info("User action", user_id=67890, action="delete")
    
    logger.remove()
    print()


def example_4_alignment():
    """Example 4: Format specifications - alignment"""
    print("\n" + "=" * 70)
    print("Example 4: Format Specifications - Alignment")
    print("=" * 70)
    
    logger = Logger()
    
    # Left alignment
    logger.add(sys.stderr, format="[{level:<10}] {message}")
    logger.info("Left-aligned level")
    logger.error("Error message")
    logger.remove()
    
    print()
    
    # Right alignment
    logger.add(sys.stderr, format="[{level:>10}] {message}")
    logger.info("Right-aligned level")
    logger.error("Error message")
    logger.remove()
    
    print()
    
    # Center alignment
    logger.add(sys.stderr, format="[{level:^10}] {message}")
    logger.info("Center-aligned level")
    logger.error("Error message")
    logger.remove()
    
    print()


def example_5_datetime_formats():
    """Example 5: Custom datetime formatting"""
    print("\n" + "=" * 70)
    print("Example 5: Custom Datetime Formatting")
    print("=" * 70)
    
    logger = Logger()
    
    # Date only
    logger.add(sys.stderr, format="{time:YYYY-MM-DD} | {message}")
    logger.info("Date only format")
    logger.remove()
    
    # Time only
    logger.add(sys.stderr, format="{time:HH:mm:ss} | {message}")
    logger.info("Time only format")
    logger.remove()
    
    # Full datetime
    logger.add(sys.stderr, format="{time:YYYY-MM-DD HH:mm:ss} | {message}")
    logger.info("Full datetime format")
    logger.remove()
    
    # Custom format
    logger.add(sys.stderr, format="{time:YYYY/MM/DD HH:mm} | {message}")
    logger.info("Custom datetime format")
    logger.remove()
    
    print()


def example_6_escaped_braces():
    """Example 6: Escaped braces"""
    print("\n" + "=" * 70)
    print("Example 6: Escaped Braces")
    print("=" * 70)
    
    logger = Logger()
    
    # Use {{ and }} for literal braces
    logger.add(sys.stderr, format="{{literal}} {message} {{braces}}")
    logger.info("This has literal braces")
    
    logger.remove()
    print()


def example_7_complex_format():
    """Example 7: Complex format combining multiple features"""
    print("\n" + "=" * 70)
    print("Example 7: Complex Format")
    print("=" * 70)
    
    logger = Logger()
    
    # Comprehensive format
    complex_format = (
        "{time:YYYY-MM-DD HH:mm:ss} | "
        "{level:<8} | "
        "{name}:{function}:{line} | "
        "{message}"
    )
    
    logger.add(sys.stderr, format=complex_format)
    logger.info("Complex format example")
    logger.warning("Warning with complex format")
    logger.error("Error with complex format")
    
    logger.remove()
    print()


def example_8_color_tags():
    """Example 8: Color tags (parsed but not yet applied)"""
    print("\n" + "=" * 70)
    print("Example 8: Color Tags (Parsed, Applied in Day 9)")
    print("=" * 70)
    
    logger = Logger()
    
    # Color tags are parsed but colors won't show until Day 9
    colorful_format = "<green>{time}</green> | <level>{level:<8}</level> | {message}"
    
    logger.add(sys.stderr, format=colorful_format)
    logger.info("Color tags are parsed (colors in Day 9)")
    logger.warning("Warning message")
    logger.error("Error message")
    
    logger.remove()
    print()


def example_9_production_format():
    """Example 9: Production-ready format"""
    print("\n" + "=" * 70)
    print("Example 9: Production-Ready Format")
    print("=" * 70)
    
    logger = Logger()
    
    # Console format - concise
    console_format = "{time:HH:mm:ss} [{level:<8}] {message}"
    logger.add(sys.stderr, format=console_format, level="INFO")
    
    # File format - detailed
    file_format = (
        "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
        "{level:<8} | "
        "{process.id}:{thread.id} | "
        "{name}:{function}:{line} | "
        "{message}"
    )
    logger.add("app.log", format=file_format, level="DEBUG")
    
    # Test logging
    logger.debug("Debug info (only in file)")
    logger.info("Application started")
    logger.warning("High memory usage")
    logger.error("Connection failed")
    
    logger.remove()
    print("\nCheck app.log for detailed logs!")
    print()


def example_10_structured_logging():
    """Example 10: Structured logging with extra fields"""
    print("\n" + "=" * 70)
    print("Example 10: Structured Logging")
    print("=" * 70)
    
    logger = Logger()
    
    # Format that includes extra fields
    structured_format = (
        "[{level}] {message} | "
        "user={extra.user_id} | "
        "request={extra.request_id}"
    )
    
    logger.add(sys.stderr, format=structured_format)
    
    # Log with structured data
    logger.info("User login", user_id=123, request_id="abc-123")
    logger.warning("API rate limit", user_id=456, request_id="def-456")
    logger.error("Database error", user_id=789, request_id="ghi-789")
    
    logger.remove()
    print()


def main():
    """Run all examples"""
    print("\n" + "=" * 70)
    print("MYLOGGER DAY 6 - ADVANCED FORMATTER EXAMPLES")
    print("=" * 70)
    
    example_1_basic_formatting()
    example_2_nested_access()
    example_3_extra_dict()
    example_4_alignment()
    example_5_datetime_formats()
    example_6_escaped_braces()
    example_7_complex_format()
    example_8_color_tags()
    example_9_production_format()
    example_10_structured_logging()
    
    print("\n" + "=" * 70)
    print("ALL EXAMPLES COMPLETED")
    print("=" * 70)
    print("\nDay 6 Features Demonstrated:")
    print("  1. Basic field formatting - {level}, {message}")
    print("  2. Nested field access - {level.name}, {process.id}")
    print("  3. Extra dict access - {extra.user_id}")
    print("  4. Alignment specs - {level:<8}, {level:>10}, {level:^10}")
    print("  5. Custom datetime - {time:YYYY-MM-DD HH:mm:ss}")
    print("  6. Escaped braces - {{ and }}")
    print("  7. Complex formats - combining multiple features")
    print("  8. Color tags - <red>text</red> (colors in Day 9)")
    print("  9. Production formats - console and file")
    print("  10. Structured logging - with extra fields")
    print("\nNext: Days 7-8 focus on handler improvements")
    print("      Day 9 will add full color support!")


if __name__ == "__main__":
    main()

