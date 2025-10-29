"""
Utility functions and classes
"""

import sys
import linecache
import os
from datetime import timedelta
from typing import Any, Dict, Optional, List
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
                "filename": "<unknown>",
                "file_name": "<unknown>",
                "function": "<unknown>",
                "lineno": 0,
                "module": "<unknown>",
                "code_context": [],
                "context_line": "",
            }

        # Extract basic information from the frame
        code = frame.f_code
        filename = code.co_filename
        function = code.co_name
        lineno = frame.f_lineno
        module = frame.f_globals.get("__name__", "__main__")

        # Get the base filename
        file_name = os.path.basename(filename)

        # Get code context (5 lines around the current line)
        code_context, context_line = FrameInspector._get_code_context(
            filename, lineno, context_size=5
        )

        return {
            "filename": filename,
            "file_name": file_name,
            "function": function,
            "lineno": lineno,
            "module": module,
            "code_context": code_context,
            "context_line": context_line,
        }

    @staticmethod
    def _get_code_context(
        filename: str, lineno: int, context_size: int = 5
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
            return [], ""

    @staticmethod
    def clear_cache():
        """Clear the linecache

        This should be called if source files are modified during runtime
        to ensure fresh code context is retrieved.
        """
        linecache.checkcache()


class TimeUtils:
    """Time-related utility functions for parsing and formatting

    This class provides utilities for:
    - Parsing human-readable duration strings to timedelta
    - Parsing human-readable size strings to bytes
    - Formatting datetime with custom tokens (Loguru-style)
    """

    @staticmethod
    def parse_duration(duration: str) -> timedelta:
        """Parse duration string to timedelta

        Supports various formats:
        - "10 seconds", "5 minutes", "2 hours", "1 day"
        - "10s", "5m", "2h", "1d"
        - Multiple units: "1 day 2 hours 30 minutes"
        - Fractional values: "1.5 hours", "0.5 days"

        Args:
            duration: Duration string (e.g., "10 seconds", "5m", "2h 30m")

        Returns:
            timedelta object representing the duration

        Raises:
            ValueError: If duration format is invalid

        Examples:
            >>> TimeUtils.parse_duration("10 seconds")
            timedelta(seconds=10)
            >>> TimeUtils.parse_duration("5m")
            timedelta(seconds=300)
            >>> TimeUtils.parse_duration("1d 2h 30m")
            timedelta(days=1, seconds=9000)
        """
        from .constants import TIME_UNITS

        if not duration or not isinstance(duration, str):
            raise ValueError(f"Invalid duration: {duration}")

        # Import here to avoid circular imports
        import re

        # Clean up the string
        duration = duration.strip().lower()

        # Pattern to match: number (optional space) unit
        # Matches: "10s", "10 seconds", "10.5 hours", etc.
        pattern = r"(\d+\.?\d*)\s*([a-z]+)"
        matches = re.findall(pattern, duration)

        if not matches:
            raise ValueError(f"Invalid duration format: {duration}")

        total_seconds = 0.0

        for value_str, unit in matches:
            try:
                value = float(value_str)
            except ValueError:
                raise ValueError(f"Invalid number: {value_str}")

            if unit not in TIME_UNITS:
                raise ValueError(f"Unknown time unit: {unit}")

            total_seconds += value * TIME_UNITS[unit]

        return timedelta(seconds=total_seconds)

    @staticmethod
    def parse_size(size: str) -> int:
        """Parse size string to bytes

        Supports various formats:
        - "10 KB", "5 MB", "2 GB", "1 TB"
        - "10KB", "5MB", "2GB"
        - "10 K", "5 M", "2 G"
        - Just number: "1024" (interpreted as bytes)

        Args:
            size: Size string (e.g., "10 MB", "5KB", "1024")

        Returns:
            Size in bytes as integer

        Raises:
            ValueError: If size format is invalid

        Examples:
            >>> TimeUtils.parse_size("10 KB")
            10240
            >>> TimeUtils.parse_size("5MB")
            5242880
            >>> TimeUtils.parse_size("1024")
            1024
        """
        from .constants import SIZE_UNITS

        if not size:
            raise ValueError("Size string cannot be empty")

        import re

        # Clean up the string
        size_str = str(size).strip().upper()

        # Try to match: number (optional space) unit
        # Pattern matches: "10KB", "10 KB", "10K", "10 K", "10"
        pattern = r"^(\d+\.?\d*)\s*([A-Z]*)$"
        match = re.match(pattern, size_str)

        if not match:
            raise ValueError(f"Invalid size format: {size}")

        value_str, unit = match.groups()

        try:
            value = float(value_str)
        except ValueError:
            raise ValueError(f"Invalid number: {value_str}")

        # If no unit, assume bytes
        if not unit:
            return int(value)

        if unit not in SIZE_UNITS:
            raise ValueError(f"Unknown size unit: {unit}")

        return int(value * SIZE_UNITS[unit])

    @staticmethod
    def format_time(dt, fmt: str) -> str:
        """Format datetime with custom tokens (Loguru-style)

        Converts custom format tokens to Python strftime format.

        Supported tokens:
        - YYYY: 4-digit year (2024)
        - YY: 2-digit year (24)
        - MMMM: Full month name (January)
        - MMM: Abbreviated month (Jan)
        - MM: 2-digit month (01)
        - DD: 2-digit day (01)
        - HH: 2-digit hour 24h (00-23)
        - hh: 2-digit hour 12h (01-12)
        - mm: 2-digit minute (00-59)
        - ss: 2-digit second (00-59)
        - SSS: Milliseconds (000-999)
        - A: AM/PM

        Args:
            dt: datetime object to format
            fmt: Format string with custom tokens

        Returns:
            Formatted datetime string

        Examples:
            >>> from datetime import datetime
            >>> dt = datetime(2024, 1, 15, 14, 30, 45, 123456)
            >>> TimeUtils.format_time(dt, "YYYY-MM-DD HH:mm:ss")
            '2024-01-15 14:30:45'
            >>> TimeUtils.format_time(dt, "MMM DD, YYYY at hh:mm A")
            'Jan 15, 2024 at 02:30 PM'
        """
        from .constants import DATETIME_FORMATS
        from datetime import datetime

        if not isinstance(dt, datetime):
            raise ValueError(f"Expected datetime object, got {type(dt)}")

        result = fmt

        # Sort tokens by length (longest first) to avoid partial replacements
        # e.g., replace "YYYY" before "YY"
        sorted_tokens = sorted(DATETIME_FORMATS.items(), key=lambda x: len(x[0]), reverse=True)

        for token, strftime_code in sorted_tokens:
            if token in result:
                if token == "SSS":
                    # Special handling for milliseconds
                    milliseconds = dt.microsecond // 1000
                    result = result.replace(token, f"{milliseconds:03d}")
                elif token in ["M", "D", "H", "m", "s", "h"]:
                    # These format codes with '-' don't work on Windows
                    # Use the zero-padded version and strip leading zero if needed
                    if sys.platform == "win32":
                        # On Windows, use the zero-padded version
                        padded_token = token * 2  # M -> MM, D -> DD, etc.
                        if padded_token in DATETIME_FORMATS:
                            formatted = dt.strftime(DATETIME_FORMATS[padded_token])
                            # Strip leading zero
                            result = result.replace(token, formatted.lstrip("0") or "0")
                        else:
                            result = result.replace(token, dt.strftime(DATETIME_FORMATS[token]))
                    else:
                        result = result.replace(token, dt.strftime(DATETIME_FORMATS[token]))
                else:
                    result = result.replace(token, dt.strftime(strftime_code))

        return result


class Serializer:
    """Serialize log records to JSON

    This class converts LogRecord objects to JSON strings, handling
    all the special types that might not be directly serializable:
    - datetime objects → ISO format strings
    - timedelta objects → seconds (float)
    - Exception objects → string representation
    - Custom objects → repr() or str()
    - Path objects → string representation
    """

    @staticmethod
    def serialize(record: "LogRecord") -> str:
        """Serialize a log record to JSON string

        This method converts a LogRecord to a JSON string, handling
        all non-serializable objects appropriately.

        Args:
            record: LogRecord instance to serialize

        Returns:
            JSON string representation of the record

        Example:
            >>> from mylogger.record import LogRecord
            >>> json_str = Serializer.serialize(record)
            >>> print(json_str)
            {"level": {"name": "INFO", ...}, "message": "Hello", ...}
        """
        import json
        from datetime import datetime, timedelta  # noqa: F401 - Used in isinstance checks

        # Convert LogRecord to dictionary
        data = record.to_dict()

        # Serialize to JSON with custom handling
        try:
            return json.dumps(data, default=Serializer._json_default, ensure_ascii=False)
        except Exception as e:
            # Fallback: return a minimal JSON with error info
            return json.dumps(
                {
                    "level": record.level.name,
                    "message": record.message,
                    "serialization_error": str(e),
                }
            )

    @staticmethod
    def to_dict(record: "LogRecord") -> Dict[str, Any]:
        """Convert log record to dictionary

        This is a convenience method that calls the LogRecord's to_dict()
        method and post-processes it to ensure all values are JSON-serializable.

        Args:
            record: LogRecord instance to convert

        Returns:
            Dictionary with all record fields

        Example:
            >>> data = Serializer.to_dict(record)
            >>> print(data['level']['name'])
            'INFO'
        """
        data = record.to_dict()

        # Post-process to ensure all nested values are serializable
        return Serializer._sanitize_dict(data)

    @staticmethod
    def _sanitize_dict(obj: Any) -> Any:
        """Recursively sanitize dictionary values for JSON serialization

        This method walks through nested dictionaries and lists, converting
        non-serializable objects to serializable representations.

        Args:
            obj: Object to sanitize (can be dict, list, or any value)

        Returns:
            Sanitized object that is JSON-serializable
        """
        from datetime import datetime, timedelta
        from pathlib import Path

        if isinstance(obj, dict):
            return {key: Serializer._sanitize_dict(value) for key, value in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [Serializer._sanitize_dict(item) for item in obj]
        elif isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, timedelta):
            return obj.total_seconds()
        elif isinstance(obj, Path):
            return str(obj)
        elif isinstance(obj, Exception):
            return str(obj)
        elif isinstance(obj, (str, int, float, bool, type(None))):
            return obj
        else:
            # For any other type, try to convert to string
            try:
                return str(obj)
            except Exception:
                return repr(obj)

    @staticmethod
    def _json_default(obj: Any) -> Any:
        """Custom JSON encoder for non-serializable objects

        This function is used as the 'default' parameter in json.dumps()
        to handle objects that are not natively JSON-serializable.

        Args:
            obj: Object that json.dumps() cannot serialize

        Returns:
            JSON-serializable representation of the object

        Raises:
            TypeError: If object cannot be serialized (should not happen)
        """
        from datetime import datetime, timedelta
        from pathlib import Path

        # Handle datetime objects
        if isinstance(obj, datetime):
            return obj.isoformat()

        # Handle timedelta objects
        if isinstance(obj, timedelta):
            return obj.total_seconds()

        # Handle Path objects
        if isinstance(obj, Path):
            return str(obj)

        # Handle Exception objects
        if isinstance(obj, Exception):
            return {"type": type(obj).__name__, "message": str(obj), "repr": repr(obj)}

        # For any other type, try repr() or str()
        try:
            return str(obj)
        except Exception:
            return repr(obj)
