"""
Formatting classes for log output

This module provides advanced formatting capabilities including:
- Token-based format string parsing
- Nested field access (e.g., level.name, extra.user_id)
- Format specifications (alignment, width, precision)
- Color tag parsing and colorization
"""

from typing import Any, List, Optional, Dict
import re
import os
from datetime import datetime
from .constants import COLORS, BG_COLORS


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


class Colorizer:
    """Handle ANSI color code application and stripping
    
    This class provides methods to:
    - Apply ANSI color codes to text
    - Map color names to ANSI codes
    - Map log levels to default colors
    - Strip color codes from text
    - Check for NO_COLOR environment variable
    
    Attributes:
        colors: Dictionary of color name to ANSI code mappings
        level_colors: Dictionary of log level to color mappings
    """
    
    def __init__(self):
        """Initialize the colorizer with color mappings"""
        # Combine foreground and background colors
        self.colors: Dict[str, str] = {**COLORS, **BG_COLORS}
        
        # Define default color scheme for log levels
        self.level_colors: Dict[str, str] = {
            'TRACE': 'dim+cyan',      # Dim cyan for trace
            'DEBUG': 'cyan',          # Cyan for debug
            'INFO': 'white',          # White for info
            'SUCCESS': 'bold+green',  # Bold green for success
            'WARNING': 'yellow',      # Yellow for warning
            'ERROR': 'red',           # Red for error
            'CRITICAL': 'bold+red',   # Bold red for critical
        }
    
    def colorize(self, text: str, color: str) -> str:
        """Apply color to text
        
        Args:
            text: Text to colorize
            color: Color name or combination (e.g., 'red', 'bold+green')
            
        Returns:
            Text with ANSI color codes
            
        Examples:
            >>> colorizer.colorize("Hello", "red")
            '\\x1b[31mHello\\x1b[0m'
            >>> colorizer.colorize("Bold", "bold+green")
            '\\x1b[1m\\x1b[32mBold\\x1b[0m'
        """
        if not color or not text:
            return text
        
        # Handle combined colors (e.g., 'bold+red')
        color_parts = color.split('+')
        
        # Build opening codes
        codes = []
        for part in color_parts:
            part = part.strip()
            if part in self.colors:
                codes.append(self.colors[part])
        
        if not codes:
            return text
        
        # Apply colors: codes + text + reset
        return ''.join(codes) + text + self.colors['reset']
    
    def get_level_color(self, level_name: str) -> str:
        """Get the default color for a log level
        
        Args:
            level_name: Log level name (e.g., 'INFO', 'ERROR')
            
        Returns:
            Color name or combination for the level
        """
        return self.level_colors.get(level_name.upper(), 'white')
    
    def colorize_level(self, text: str, level_name: str) -> str:
        """Colorize text using the level's default color
        
        Args:
            text: Text to colorize
            level_name: Log level name
            
        Returns:
            Colorized text
        """
        color = self.get_level_color(level_name)
        return self.colorize(text, color)
    
    def strip_colors(self, text: str) -> str:
        """Remove ANSI color codes from text
        
        Args:
            text: Text containing ANSI color codes
            
        Returns:
            Text without color codes
        """
        # Remove ANSI escape sequences
        ansi_pattern = re.compile(r'\x1b\[[0-9;]*m')
        return ansi_pattern.sub('', text)
    
    def should_colorize(self) -> bool:
        """Check if colorization should be enabled
        
        Checks the NO_COLOR environment variable. If set (to any value),
        colorization should be disabled.
        
        Returns:
            True if colorization should be enabled, False otherwise
        """
        # Check NO_COLOR environment variable
        # https://no-color.org/
        return not os.environ.get('NO_COLOR')
    
    def apply_color_tag(self, text: str, tag: str, level_name: Optional[str] = None) -> str:
        """Apply color based on a tag name
        
        Args:
            text: Text to colorize
            tag: Color tag (e.g., 'red', 'green', 'level')
            level_name: Optional level name for 'level' tag
            
        Returns:
            Colorized text
        """
        if tag == 'level' and level_name:
            return self.colorize_level(text, level_name)
        else:
            return self.colorize(text, tag)


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
            colorize: Enable colorization
        """
        self.format_string = format_string or self._default_format()
        self.colorize = colorize
        self.tokens: List[Token] = []
        self.colorizer = Colorizer()
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
            color_stack = []  # Track nested color tags
            
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
                    # Apply color if colorization is enabled
                    if self.colorize:
                        color_tag = token.value
                        color_stack.append(color_tag)
                        # Start capturing text for colorization
                        result.append('\x00COLOR_START:' + color_tag + '\x00')
                
                elif token.type == 'color_end':
                    # Close color tag if colorization is enabled
                    if self.colorize and color_stack:
                        color_stack.pop()
                        result.append('\x00COLOR_END\x00')
            
            # Join all parts
            formatted_text = ''.join(result)
            
            # Apply colors if enabled
            if self.colorize:
                formatted_text = self._apply_colors(formatted_text, record)
            
            return formatted_text
            
        except Exception as e:
            # Fallback to simple format if something goes wrong
            return f"[{record.level.name}] {record.message} [FORMAT ERROR: {e}]"
    
    def _apply_colors(self, text: str, record: 'LogRecord') -> str:
        """Apply color tags to formatted text
        
        Args:
            text: Formatted text with color markers
            record: LogRecord for level-based coloring
            
        Returns:
            Text with ANSI color codes
        """
        # Process color markers using a stack-based approach
        result = []
        i = 0
        color_stack = []
        
        while i < len(text):
            if text[i:i+1] == '\x00':
                # Find the end of the marker
                end = text.find('\x00', i + 1)
                if end != -1:
                    marker = text[i+1:end]
                    
                    if marker.startswith('COLOR_START:'):
                        # Extract and push color tag
                        color_tag = marker[12:]  # Skip 'COLOR_START:'
                        color_stack.append(color_tag)
                        i = end + 1
                        continue
                    
                    elif marker == 'COLOR_END':
                        # Pop the most recent color
                        if color_stack:
                            color_stack.pop()
                        i = end + 1
                        continue
            
            # Regular character - accumulate until next marker
            char_start = i
            while i < len(text) and text[i:i+1] != '\x00':
                i += 1
            
            # Get the text segment
            segment = text[char_start:i]
            
            if segment and color_stack:
                # Apply the current color
                color_tag = color_stack[-1]
                if color_tag == 'level':
                    segment = self.colorizer.colorize_level(segment, record.level.name)
                else:
                    segment = self.colorizer.colorize(segment, color_tag)
            
            result.append(segment)
        
        return ''.join(result)
    
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
