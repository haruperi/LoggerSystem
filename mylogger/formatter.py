"""
Formatting classes for log output

This module provides advanced formatting capabilities including:
- Token-based format string parsing
- Nested field access (e.g., level.name, extra.user_id)
- Format specifications (alignment, width, precision)
- Color tag parsing (for Day 9 colorization)
"""

from typing import Any, List, Optional
import re
from datetime import datetime


class Token:
    """Represents a token in a format string
    
    A token can be either:
    - A literal string (plain text)
    - A field placeholder (e.g., {time}, {level.name})
    
    Attributes:
        type: 'literal' or 'field'
        value: The token's value (literal text or complete field string)
        field_name: Field name for field tokens (e.g., 'time', 'level.name')
        format_spec: Format specification (e.g., '<8', 'YYYY-MM-DD')
        color_tag: Optional color tag for the field (e.g., 'red', 'level')
    """
    
    def __init__(
        self,
        token_type: str,
        value: str,
        field_name: Optional[str] = None,
        format_spec: Optional[str] = None,
        color_tag: Optional[str] = None
    ):
        """Initialize a token
        
        Args:
            token_type: 'literal' or 'field'
            value: Token value
            field_name: Field name for field tokens
            format_spec: Format specification
            color_tag: Color tag name
        """
        self.type = token_type
        self.value = value
        self.field_name = field_name
        self.format_spec = format_spec
        self.color_tag = color_tag
    
    def __repr__(self) -> str:
        """Return string representation"""
        if self.type == 'literal':
            return f"Token(literal, {self.value!r})"
        else:
            return f"Token(field, {self.field_name!r}, spec={self.format_spec!r})"


class Formatter:
    """Format log records into strings
    
    This formatter supports:
    - Field placeholders: {time}, {level}, {message}
    - Nested access: {level.name}, {process.id}, {extra.user_id}
    - Format specs: {level:<8}, {elapsed:.2f}, {time:YYYY-MM-DD}
    - Color tags: <red>text</red>, <level>text</level> (parsed but not applied until Day 9)
    - Escaped braces: {{literal braces}}
    
    Attributes:
        format_string: Original format template string
        colorize: Whether to apply colors (implementation in Day 9)
        tokens: Parsed list of tokens
    """
    
    def __init__(self, format_string: str = None, colorize: bool = False):
        """Initialize formatter
        
        Args:
            format_string: Format template (if None, use default)
            colorize: Enable colorization (will be used in Day 9)
        """
        self.format_string = format_string or self._default_format()
        self.colorize = colorize
        self.tokens: List[Token] = []
        self._parse_format_string()
    
    def _default_format(self) -> str:
        """Return default format string
        
        Returns:
            Default format template
        """
        return "{time} | {level: <8} | {name}:{function}:{line} - {message}"
    
    def _parse_format_string(self) -> None:
        """Parse format string into tokens
        
        This method parses the format string and creates a list of tokens.
        It handles:
        - Field placeholders: {field_name:format_spec}
        - Color tags: <tag>content</tag>
        - Escaped braces: {{ and }}
        """
        self.tokens = []
        
        # More comprehensive pattern that handles escaped braces better
        # Process the string character by character for better control
        i = 0
        current_color = None
        
        while i < len(self.format_string):
            char = self.format_string[i]
            
            # Handle escaped braces
            if char == '{' and i + 1 < len(self.format_string) and self.format_string[i + 1] == '{':
                self.tokens.append(Token('literal', '{'))
                i += 2
                continue
            
            if char == '}' and i + 1 < len(self.format_string) and self.format_string[i + 1] == '}':
                self.tokens.append(Token('literal', '}'))
                i += 2
                continue
            
            # Handle color tags
            if char == '<':
                # Find the end of the tag
                end = self.format_string.find('>', i)
                if end != -1:
                    tag = self.format_string[i:end+1]
                    
                    if tag.startswith('</'):
                        # Closing color tag
                        current_color = None
                        self.tokens.append(Token('color_end', ''))
                    else:
                        # Opening color tag
                        color_name = tag[1:-1]
                        current_color = color_name
                        self.tokens.append(Token('color_start', color_name))
                    
                    i = end + 1
                    continue
            
            # Handle field placeholders
            if char == '{':
                # Find the matching closing brace
                end = self.format_string.find('}', i)
                if end != -1:
                    field_content = self.format_string[i+1:end]
                    
                    # Split on : to separate field name from format spec
                    if ':' in field_content:
                        field_name, format_spec = field_content.split(':', 1)
                    else:
                        field_name = field_content
                        format_spec = None
                    
                    self.tokens.append(Token(
                        'field',
                        self.format_string[i:end+1],
                        field_name=field_name,
                        format_spec=format_spec,
                        color_tag=current_color
                    ))
                    
                    i = end + 1
                    continue
            
            # Handle literal text
            # Collect consecutive non-special characters
            literal_start = i
            while i < len(self.format_string) and self.format_string[i] not in '{}<':
                i += 1
            
            if i > literal_start:
                self.tokens.append(Token('literal', self.format_string[literal_start:i]))
            else:
                # Single character that wasn't handled
                self.tokens.append(Token('literal', char))
                i += 1
    
    def format(self, record: 'LogRecord') -> str:
        """Format a log record using the parsed tokens
        
        Args:
            record: LogRecord to format
            
        Returns:
            Formatted string
        """
        try:
            result = []
            
            for token in self.tokens:
                if token.type == 'literal':
                    result.append(token.value)
                
                elif token.type == 'field':
                    # Get field value
                    value = self.get_field_value(record, token.field_name)
                    
                    # Apply format specification
                    formatted = self._apply_format_spec(value, token.format_spec, token.field_name)
                    
                    result.append(formatted)
                
                elif token.type == 'color_start':
                    # Color tags will be processed in Day 9
                    # For now, just skip them (no color applied)
                    pass
                
                elif token.type == 'color_end':
                    # Color tags will be processed in Day 9
                    pass
            
            return ''.join(result)
            
        except Exception as e:
            # Fallback to simple format if something goes wrong
            return f"[{record.level.name}] {record.message} [FORMAT ERROR: {e}]"
    
    def get_field_value(self, record: 'LogRecord', field_name: str) -> Any:
        """Extract field value from record with nested access support
        
        Supports:
        - Direct attributes: time, level, message, function, line
        - Nested access: level.name, process.id, thread.name
        - Extra dict access: extra.user_id, extra.request_id
        
        Args:
            record: LogRecord to extract from
            field_name: Field name with optional nested access
            
        Returns:
            Field value or '<missing>' if not found
        """
        try:
            # Handle nested field access
            parts = field_name.split('.')
            obj = record
            
            for i, part in enumerate(parts):
                # Special handling for 'extra' dict
                if part == 'extra' and i < len(parts) - 1:
                    # Access extra dict
                    next_part = parts[i + 1]
                    if isinstance(obj.extra, dict) and next_part in obj.extra:
                        return obj.extra[next_part]
                    else:
                        return '<missing>'
                
                # Regular attribute access
                if hasattr(obj, part):
                    obj = getattr(obj, part)
                elif isinstance(obj, dict) and part in obj:
                    obj = obj[part]
                else:
                    return f'<missing:{field_name}>'
            
            return obj
            
        except Exception:
            return f'<error:{field_name}>'
    
    def _apply_format_spec(self, value: Any, format_spec: Optional[str], field_name: str) -> str:
        """Apply format specification to a value
        
        Handles:
        - Alignment: <, >, ^
        - Width: numbers
        - Precision: .2f
        - Custom datetime formats: YYYY-MM-DD HH:mm:ss
        
        Args:
            value: Value to format
            format_spec: Format specification string
            field_name: Field name (for context-aware formatting)
            
        Returns:
            Formatted string
        """
        if format_spec is None or format_spec == '':
            return str(value)
        
        try:
            # Handle datetime formatting with custom tokens
            if isinstance(value, datetime) or field_name == 'time':
                if any(token in format_spec for token in ['YYYY', 'MM', 'DD', 'HH', 'mm', 'ss', 'SSS']):
                    # Custom datetime format
                    return self._format_datetime(value, format_spec)
            
            # Handle standard Python format specs
            # Check if it starts with alignment characters
            if format_spec and format_spec[0] in '<>^':
                # Has alignment
                return format(value, format_spec)
            elif format_spec and any(c.isdigit() for c in format_spec):
                # Has width or precision
                return format(value, format_spec)
            else:
                # Try as-is
                try:
                    return format(value, format_spec)
                except (ValueError, TypeError):
                    # If format fails, just convert to string
                    return str(value)
        
        except Exception:
            return str(value)
    
    def _format_datetime(self, dt: datetime, fmt: str) -> str:
        """Format datetime with custom tokens (Loguru-style)
        
        Supported tokens:
        - YYYY: 4-digit year (2024)
        - YY: 2-digit year (24)
        - MMMM: Full month name (January)
        - MMM: Abbreviated month (Jan)
        - MM: 2-digit month (01)
        - M: Month (1-12)
        - DD: 2-digit day (01)
        - D: Day (1-31)
        - HH: 2-digit hour 24h (00-23)
        - H: Hour 24h (0-23)
        - hh: 2-digit hour 12h (01-12)
        - h: Hour 12h (1-12)
        - mm: 2-digit minute (00-59)
        - m: Minute (0-59)
        - ss: 2-digit second (00-59)
        - s: Second (0-59)
        - SSS: Milliseconds (000-999)
        - A: AM/PM
        - a: am/pm
        
        Args:
            dt: datetime object to format
            fmt: Format string with custom tokens
            
        Returns:
            Formatted datetime string
        """
        if not isinstance(dt, datetime):
            return str(dt)
        
        # Import TimeUtils for datetime formatting
        try:
            from .utils import TimeUtils
            return TimeUtils.format_time(dt, fmt)
        except Exception:
            # Fallback to simple format
            return dt.strftime('%Y-%m-%d %H:%M:%S')
    
    def strip_colors(self, text: str) -> str:
        """Remove color tags from text
        
        Removes <tag>content</tag> patterns, leaving just the content.
        
        Args:
            text: Text with color tags
            
        Returns:
            Text without color tags
        """
        # Remove color tags but keep content
        result = re.sub(r'<[a-zA-Z_]+>', '', text)
        result = re.sub(r'</[a-zA-Z_]+>', '', result)
        return result
