"""
Exception formatting with stack traces, colorization, and diagnosis

This module provides beautiful exception formatting with:
- Detailed stack traces
- Colorized output
- Variable inspection in frames (diagnose mode)
- Context lines around error location
"""

import sys
import traceback
from typing import Optional, List, Tuple, Any, Dict
from pathlib import Path
import linecache


class ExceptionFormatter:
    """Format exceptions with beautiful output and optional diagnosis
    
    This formatter provides detailed exception information including:
    - Exception type and message
    - Complete stack trace with file/line/function information
    - Source code context lines
    - Local variable values in each frame (diagnose mode)
    - Colorized output for better readability
    
    Example:
        >>> formatter = ExceptionFormatter(colorize=True, diagnose=True)
        >>> try:
        ...     x = 1 / 0
        ... except Exception as e:
        ...     formatted = formatter.format_exception(sys.exc_info())
        ...     print(formatted)
    """
    
    def __init__(
        self,
        colorize: bool = False,
        backtrace: bool = True,
        diagnose: bool = False,
        max_context_lines: int = 5,
        max_value_length: int = 100
    ):
        """Initialize exception formatter
        
        Args:
            colorize: Enable colored output for terminals
            backtrace: Show full traceback (if False, only show exception message)
            diagnose: Show local variables in each frame
            max_context_lines: Number of context lines to show around error
            max_value_length: Maximum length for variable value strings
        """
        self.colorize = colorize
        self.backtrace = backtrace
        self.diagnose = diagnose
        self.max_context_lines = max_context_lines
        self.max_value_length = max_value_length
        
        # ANSI color codes
        self._colors = {
            'red': '\033[91m',
            'green': '\033[92m',
            'yellow': '\033[93m',
            'blue': '\033[94m',
            'magenta': '\033[95m',
            'cyan': '\033[96m',
            'white': '\033[97m',
            'bold': '\033[1m',
            'dim': '\033[2m',
            'reset': '\033[0m',
        }
    
    def _color(self, text: str, color: str) -> str:
        """Apply color to text if colorization is enabled
        
        Args:
            text: Text to colorize
            color: Color name (red, green, yellow, blue, magenta, cyan, white, bold, dim)
            
        Returns:
            Colored text if colorize=True, otherwise plain text
        """
        if not self.colorize:
            return text
        
        color_code = self._colors.get(color, '')
        reset = self._colors.get('reset', '')
        return f"{color_code}{text}{reset}"
    
    def format_exception(
        self,
        exc_info: Optional[Tuple[type, BaseException, Any]] = None
    ) -> str:
        """Format an exception with full details
        
        Args:
            exc_info: Exception info tuple from sys.exc_info() or exception object
                Can be (type, value, traceback) or just an Exception instance
                
        Returns:
            Formatted exception string
            
        Example:
            >>> try:
            ...     1 / 0
            ... except:
            ...     print(formatter.format_exception(sys.exc_info()))
        """
        if exc_info is None:
            exc_info = sys.exc_info()
        
        # Handle different input types
        if isinstance(exc_info, BaseException):
            # Single exception object
            exc_type = type(exc_info)
            exc_value = exc_info
            exc_tb = exc_info.__traceback__
        elif isinstance(exc_info, tuple) and len(exc_info) == 3:
            exc_type, exc_value, exc_tb = exc_info
        else:
            return "Invalid exception info"
        
        if exc_type is None:
            return ""
        
        # Build the formatted output
        lines = []
        
        # Add separator
        lines.append(self._color("─" * 70, "dim"))
        
        # Add exception header
        exc_name = exc_type.__name__
        exc_msg = str(exc_value) if exc_value else ""
        
        header = f"{exc_name}"
        if exc_msg:
            header += f": {exc_msg}"
        
        lines.append(self._color(header, "red") + self._color(" [Exception]", "dim"))
        
        if not self.backtrace:
            lines.append(self._color("─" * 70, "dim"))
            return "\n".join(lines)
        
        # Add traceback
        if exc_tb:
            lines.append("")
            lines.append(self._color("Traceback (most recent call last):", "bold"))
            
            tb_lines = self._format_traceback(exc_tb)
            lines.extend(tb_lines)
        
        # Add separator
        lines.append(self._color("─" * 70, "dim"))
        
        return "\n".join(lines)
    
    def _format_traceback(self, tb: Any) -> List[str]:
        """Format the traceback with context and optional diagnosis
        
        Args:
            tb: Traceback object
            
        Returns:
            List of formatted lines
        """
        lines = []
        
        # Extract stack frames
        frames = self._extract_frames(tb)
        
        for frame_info in frames:
            filename = frame_info['filename']
            lineno = frame_info['lineno']
            func_name = frame_info['function']
            code_line = frame_info['code']
            frame = frame_info['frame']
            
            # Format frame header
            # File location
            file_display = self._shorten_path(filename)
            location = f'  File "{file_display}", line {lineno}, in {func_name}'
            lines.append(self._color(location, "cyan"))
            
            # Show context lines
            if code_line:
                context_lines = self._get_context_lines(filename, lineno)
                if context_lines:
                    for ctx_lineno, ctx_line, is_error in context_lines:
                        line_num = f"{ctx_lineno:4d} "
                        
                        if is_error:
                            # Highlight error line
                            formatted = f"    {self._color('>', 'red')} {self._color(line_num, 'red')}{self._color(ctx_line, 'bold')}"
                        else:
                            # Regular context line
                            formatted = f"      {self._color(line_num, 'dim')}{ctx_line}"
                        
                        lines.append(formatted)
                else:
                    # Fallback if we can't read file
                    lines.append(f"      {code_line}")
            
            # Show local variables in diagnose mode
            if self.diagnose and frame:
                var_lines = self._format_frame_variables(frame)
                if var_lines:
                    lines.append(self._color("    Variables:", "yellow"))
                    lines.extend(var_lines)
            
            lines.append("")  # Blank line between frames
        
        return lines
    
    def _extract_frames(self, tb: Any) -> List[Dict[str, Any]]:
        """Extract frame information from traceback
        
        Args:
            tb: Traceback object
            
        Returns:
            List of dictionaries containing frame information
        """
        frames = []
        
        while tb is not None:
            frame = tb.tb_frame
            lineno = tb.tb_lineno
            
            code = frame.f_code
            filename = code.co_filename
            func_name = code.co_name
            
            # Get the actual code line
            code_line = linecache.getline(filename, lineno).strip()
            
            frames.append({
                'filename': filename,
                'lineno': lineno,
                'function': func_name,
                'code': code_line,
                'frame': frame
            })
            
            tb = tb.tb_next
        
        return frames
    
    def _get_context_lines(
        self,
        filename: str,
        lineno: int
    ) -> List[Tuple[int, str, bool]]:
        """Get context lines around the error line
        
        Args:
            filename: Source file path
            lineno: Line number of error
            
        Returns:
            List of tuples (line_number, line_text, is_error_line)
        """
        try:
            # Calculate line range
            start = max(1, lineno - self.max_context_lines // 2)
            end = lineno + self.max_context_lines // 2 + 1
            
            lines = []
            for i in range(start, end):
                line = linecache.getline(filename, i)
                if line:
                    # Remove trailing newline but keep indentation
                    line = line.rstrip('\n\r')
                    is_error = (i == lineno)
                    lines.append((i, line, is_error))
            
            return lines
        except Exception:
            return []
    
    def _format_frame_variables(self, frame: Any) -> List[str]:
        """Format local variables from a frame
        
        Args:
            frame: Frame object
            
        Returns:
            List of formatted variable lines
        """
        lines = []
        
        try:
            local_vars = frame.f_locals
            
            # Filter out special variables and functions
            filtered_vars = {
                k: v for k, v in local_vars.items()
                if not k.startswith('__') and not callable(v)
            }
            
            if not filtered_vars:
                return []
            
            # Format each variable
            for var_name, var_value in sorted(filtered_vars.items()):
                value_str = self._format_value(var_value)
                var_line = f"      {self._color(var_name, 'green')} = {value_str}"
                lines.append(var_line)
        
        except Exception:
            # If we can't access variables, just skip them
            pass
        
        return lines
    
    def _format_value(self, value: Any) -> str:
        """Format a variable value for display
        
        Args:
            value: Variable value
            
        Returns:
            Formatted string representation
        """
        try:
            # Get string representation
            if isinstance(value, str):
                value_str = repr(value)
            else:
                value_str = repr(value)
            
            # Truncate if too long
            if len(value_str) > self.max_value_length:
                value_str = value_str[:self.max_value_length] + "..."
            
            return self._color(value_str, "magenta")
        
        except Exception:
            return self._color("<unable to represent>", "dim")
    
    def _shorten_path(self, path: str) -> str:
        """Shorten file path for display
        
        Args:
            path: Full file path
            
        Returns:
            Shortened path
        """
        try:
            path_obj = Path(path)
            
            # If it's in site-packages, show package name
            parts = path_obj.parts
            if 'site-packages' in parts:
                idx = parts.index('site-packages')
                return str(Path(*parts[idx:]))
            
            # If it's in the current directory, use relative path
            try:
                rel_path = path_obj.relative_to(Path.cwd())
                return str(rel_path)
            except ValueError:
                pass
            
            # Show last 3 parts of path
            if len(parts) > 3:
                return ".../" + "/".join(parts[-3:])
            
            return path
        
        except Exception:
            return path
    
    def format_exception_only(
        self,
        exc_type: type,
        exc_value: BaseException
    ) -> str:
        """Format just the exception type and message, no traceback
        
        Args:
            exc_type: Exception type
            exc_value: Exception instance
            
        Returns:
            Formatted exception string
        """
        exc_name = exc_type.__name__
        exc_msg = str(exc_value) if exc_value else ""
        
        if exc_msg:
            return self._color(f"{exc_name}: {exc_msg}", "red")
        else:
            return self._color(exc_name, "red")
    
    def __repr__(self) -> str:
        """String representation"""
        return (
            f"ExceptionFormatter("
            f"colorize={self.colorize}, "
            f"backtrace={self.backtrace}, "
            f"diagnose={self.diagnose})"
        )

