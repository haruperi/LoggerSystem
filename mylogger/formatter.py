"""
Formatting classes for log output
"""

from typing import Any


class Formatter:
    """Format log records into strings
    
    This is a simple formatter for Day 5. A more advanced formatter
    with template parsing and color support will be implemented in Day 6.
    
    Attributes:
        format_string: Format template (simple for now)
        colorize: Whether to apply colors
    """
    
    def __init__(self, format_string: str = None, colorize: bool = False):
        """Initialize formatter
        
        Args:
            format_string: Format template (if None, use default)
            colorize: Enable colorization (for Day 9)
        """
        self.format_string = format_string or self._default_format()
        self.colorize = colorize
    
    def _default_format(self) -> str:
        """Return default format string
        
        Returns:
            Default format template
        """
        return "{time} | {level} | {name}:{function}:{line} - {message}"
    
    def format(self, record: 'LogRecord') -> str:
        """Format a log record
        
        This is a simple implementation for Day 5. A more sophisticated
        formatter with proper parsing will be implemented in Day 6.
        
        Args:
            record: LogRecord to format
            
        Returns:
            Formatted string
        """
        try:
            # Format time
            time_str = record.time.strftime('%Y-%m-%d %H:%M:%S')
            
            # Build the formatted message
            formatted = self.format_string
            
            # Replace placeholders (simple version)
            replacements = {
                '{time}': time_str,
                '{level}': f"{record.level.name: <8}",  # Left-aligned, 8 chars
                '{name}': record.name,
                '{function}': record.function,
                '{line}': str(record.line),
                '{message}': record.message,
                '{file}': record.file.name,
                '{module}': record.module,
                '{process}': str(record.process.id),
                '{thread}': str(record.thread.id),
                '{elapsed}': str(record.elapsed.total_seconds()),
            }
            
            for placeholder, value in replacements.items():
                formatted = formatted.replace(placeholder, value)
            
            return formatted
            
        except Exception as e:
            # Fallback to simple format if something goes wrong
            return f"[{record.level.name}] {record.message}"
    
    def get_field_value(self, record: 'LogRecord', field_name: str) -> Any:
        """Extract field value from record
        
        Args:
            record: LogRecord to extract from
            field_name: Field name (e.g., 'level', 'level.name', 'extra.user_id')
            
        Returns:
            Field value
        """
        # Simple implementation for now
        parts = field_name.split('.')
        obj = record
        
        for part in parts:
            if hasattr(obj, part):
                obj = getattr(obj, part)
            elif isinstance(obj, dict) and part in obj:
                obj = obj[part]
            else:
                return None
        
        return obj
