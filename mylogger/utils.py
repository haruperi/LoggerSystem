"""
Utility functions and classes
"""

import sys
import inspect
import linecache
import os
from datetime import timedelta
from typing import Any, Dict, Optional, List
from pathlib import Path
from types import FrameType


class FrameInspector:
    """Inspect stack frames to extract caller information
    
    This class provides utilities to inspect the Python call stack
    and extract detailed information about the caller's context,
    including filename, function name, line number, module, and
    code context around the call site.
    """
    
    @staticmethod
    def get_caller_frame(depth: int = 0) -> Optional[FrameType]:
        """Get the caller's frame at specified depth
        
        Args:
            depth: Number of frames to go back in the call stack.
                  0 = current frame, 1 = caller, 2 = caller's caller, etc.
        
        Returns:
            Frame object at the specified depth, or None if not available
            
        Example:
            >>> frame = FrameInspector.get_caller_frame(1)  # Get caller's frame
            >>> if frame:
            ...     print(frame.f_code.co_name)  # Print function name
        """
        try:
            # sys._getframe() is faster than inspect.currentframe()
            frame = sys._getframe(depth + 1)  # +1 to skip this method itself
            return frame
        except (ValueError, AttributeError):
            # ValueError: call stack is not deep enough
            # AttributeError: sys._getframe is not available (some implementations)
            return None
    
    @staticmethod
    def extract_frame_info(frame: Optional[FrameType]) -> Dict[str, Any]:
        """Extract detailed information from a frame
        
        Args:
            frame: Frame object to extract information from
            
        Returns:
            Dictionary containing:
                - filename: Full path to the file
                - file_name: Base name of the file (e.g., 'main.py')
                - function: Function name where the call originated
                - lineno: Line number of the call
                - module: Module name (from __name__)
                - code_context: List of code lines around the call (5 lines)
                - context_line: The specific line where the call was made
                
        Example:
            >>> frame = sys._getframe(0)
            >>> info = FrameInspector.extract_frame_info(frame)
            >>> print(info['function'])  # Current function name
        """
        if frame is None:
            return {
                'filename': '<unknown>',
                'file_name': '<unknown>',
                'function': '<unknown>',
                'lineno': 0,
                'module': '<unknown>',
                'code_context': [],
                'context_line': '',
            }
        
        # Extract basic information from the frame
        code = frame.f_code
        filename = code.co_filename
        function = code.co_name
        lineno = frame.f_lineno
        module = frame.f_globals.get('__name__', '__main__')
        
        # Get the base filename
        file_name = os.path.basename(filename)
        
        # Get code context (5 lines around the current line)
        code_context, context_line = FrameInspector._get_code_context(
            filename, lineno, context_size=5
        )
        
        return {
            'filename': filename,
            'file_name': file_name,
            'function': function,
            'lineno': lineno,
            'module': module,
            'code_context': code_context,
            'context_line': context_line,
        }
    
    @staticmethod
    def _get_code_context(
        filename: str, 
        lineno: int, 
        context_size: int = 5
    ) -> tuple[List[str], str]:
        """Get code context around a specific line
        
        Args:
            filename: Path to the source file
            lineno: Line number (1-indexed)
            context_size: Number of lines to show before and after
            
        Returns:
            Tuple of (context_lines, current_line):
                - context_lines: List of lines around the target line
                - current_line: The specific line at lineno
                
        Note:
            Uses linecache which caches file contents for performance
        """
        try:
            # Get the specific line
            current_line = linecache.getline(filename, lineno).rstrip()
            
            # Get surrounding context
            start_line = max(1, lineno - context_size)
            end_line = lineno + context_size + 1
            
            context_lines = []
            for line_num in range(start_line, end_line):
                line = linecache.getline(filename, line_num).rstrip()
                if line:  # Only include non-empty lines
                    context_lines.append(line)
            
            return context_lines, current_line
            
        except (OSError, IOError):
            # File might not be accessible or might be <stdin>, <string>, etc.
            return [], ''
    
    @staticmethod
    def clear_cache():
        """Clear the linecache
        
        This should be called if source files are modified during runtime
        to ensure fresh code context is retrieved.
        """
        linecache.checkcache()


class TimeUtils:
    """Time-related utility functions"""
    
    @staticmethod
    def parse_duration(duration: str) -> timedelta:
        """Parse duration string to timedelta"""
        # TODO: Implement duration parsing
        # Examples: "10 seconds", "5 minutes", "2 hours", "1 day"
        return timedelta()
    
    @staticmethod
    def parse_size(size: str) -> int:
        """Parse size string to bytes"""
        # TODO: Implement size parsing
        # Examples: "10 KB", "5 MB", "2 GB"
        return 0
    
    @staticmethod
    def format_time(dt, fmt: str) -> str:
        """Format datetime with custom tokens"""
        # TODO: Implement custom time formatting
        # Convert YYYY-MM-DD to strftime format
        return str(dt)


class Serializer:
    """Serialize log records to JSON"""
    
    @staticmethod
    def serialize(record) -> str:
        """Serialize a log record"""
        # TODO: Implement JSON serialization
        return "{}"
    
    @staticmethod
    def to_json(record) -> str:
        """Convert record to JSON string"""
        # TODO: Implement JSON conversion
        return "{}"
