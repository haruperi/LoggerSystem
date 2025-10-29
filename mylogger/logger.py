"""
Core Logger class implementation
"""

from typing import Any, Callable, Dict, List, Optional, Union
from datetime import datetime, timedelta
import threading
import sys
import os
import multiprocessing

from .record import LogRecord, Level, FileInfo, ProcessInfo, ThreadInfo, ExceptionInfo
from .level import DEFAULT_LEVELS
from .utils import FrameInspector
from .exceptions import InvalidLevelError


class Logger:
    """Main logger class
    
    This is the primary interface for logging. It manages handlers,
    creates log records, and dispatches them to the appropriate outputs.
    
    Attributes:
        handlers: List of registered handlers
        levels: Dictionary mapping level names to Level objects
        extra: Global extra context data
        start_time: Timestamp when logger was initialized
    
    Example:
        >>> logger = Logger()
        >>> logger.info("Hello, world!")
        >>> logger.error("Something went wrong", user_id=123)
    """
    
    def __init__(self):
        """Initialize a new logger instance"""
        self.handlers: List[Any] = []
        self.levels: Dict[str, Level] = DEFAULT_LEVELS.copy()
        self.extra: Dict[str, Any] = {}
        self.start_time: datetime = datetime.now()
        self._handler_id_counter: int = 0
        self._lock = threading.Lock()
        
    def add(self, sink: Any, **options) -> int:
        """Add a handler to the logger
        
        Args:
            sink: Output destination (file path, stream, or callable)
            **options: Handler configuration options
            
        Returns:
            Handler ID for later removal
        """
        # TODO: Implement handler addition (Day 5)
        raise NotImplementedError("Handler management will be implemented in Day 5")
    
    def remove(self, handler_id: int) -> None:
        """Remove a handler by ID
        
        Args:
            handler_id: ID of the handler to remove
        """
        # TODO: Implement handler removal (Day 5)
        raise NotImplementedError("Handler management will be implemented in Day 5")
    
    def trace(self, message: str, *args, **kwargs) -> None:
        """Log a trace message
        
        Args:
            message: Log message (may contain format placeholders)
            *args: Positional arguments for formatting
            **kwargs: Keyword arguments for formatting or extra context
        """
        self._log("TRACE", message, *args, **kwargs)
    
    def debug(self, message: str, *args, **kwargs) -> None:
        """Log a debug message
        
        Args:
            message: Log message (may contain format placeholders)
            *args: Positional arguments for formatting
            **kwargs: Keyword arguments for formatting or extra context
        """
        self._log("DEBUG", message, *args, **kwargs)
    
    def info(self, message: str, *args, **kwargs) -> None:
        """Log an info message
        
        Args:
            message: Log message (may contain format placeholders)
            *args: Positional arguments for formatting
            **kwargs: Keyword arguments for formatting or extra context
        """
        self._log("INFO", message, *args, **kwargs)
    
    def success(self, message: str, *args, **kwargs) -> None:
        """Log a success message
        
        Args:
            message: Log message (may contain format placeholders)
            *args: Positional arguments for formatting
            **kwargs: Keyword arguments for formatting or extra context
        """
        self._log("SUCCESS", message, *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs) -> None:
        """Log a warning message
        
        Args:
            message: Log message (may contain format placeholders)
            *args: Positional arguments for formatting
            **kwargs: Keyword arguments for formatting or extra context
        """
        self._log("WARNING", message, *args, **kwargs)
    
    def error(self, message: str, *args, **kwargs) -> None:
        """Log an error message
        
        Args:
            message: Log message (may contain format placeholders)
            *args: Positional arguments for formatting
            **kwargs: Keyword arguments for formatting or extra context
        """
        self._log("ERROR", message, *args, **kwargs)
    
    def critical(self, message: str, *args, **kwargs) -> None:
        """Log a critical message
        
        Args:
            message: Log message (may contain format placeholders)
            *args: Positional arguments for formatting
            **kwargs: Keyword arguments for formatting or extra context
        """
        self._log("CRITICAL", message, *args, **kwargs)
    
    def log(self, level: Union[str, int], message: str, *args, **kwargs) -> None:
        """Log a message at the specified level
        
        Args:
            level: Log level (name as string or numeric value)
            message: Log message (may contain format placeholders)
            *args: Positional arguments for formatting
            **kwargs: Keyword arguments for formatting or extra context
            
        Example:
            >>> logger.log("INFO", "User logged in")
            >>> logger.log(20, "User logged in")  # Same as INFO
        """
        # Normalize level to string
        if isinstance(level, int):
            # Find level name by number
            level_name = None
            for name, lvl in self.levels.items():
                if lvl.no == level:
                    level_name = name
                    break
            if level_name is None:
                raise InvalidLevelError(f"No level with number {level}")
            level = level_name
        
        self._log(level, message, *args, **kwargs)
    
    def _log(self, level: Union[str, int], message: str, *args, **kwargs) -> None:
        """Internal logging method
        
        This method:
        1. Validates the log level
        2. Formats the message with args/kwargs
        3. Inspects the call stack to get caller information
        4. Creates a LogRecord with all context
        5. Passes the record to all handlers
        
        Args:
            level: Log level name or number
            message: Log message (may contain format placeholders)
            *args: Positional arguments for formatting
            **kwargs: Keyword arguments for formatting or extra context
        """
        # Normalize level to Level object
        level_obj = self._get_level(level)
        
        # Extract exception info if present
        exception_info = kwargs.pop('exception', None)
        if exception_info is True:
            # Capture current exception
            exc_info = sys.exc_info()
            if exc_info[0] is not None:
                exception_info = ExceptionInfo(
                    type=exc_info[0],
                    value=exc_info[1],
                    traceback=exc_info[2]
                )
            else:
                exception_info = None
        elif isinstance(exception_info, tuple) and len(exception_info) == 3:
            # Exception info was passed directly
            exception_info = ExceptionInfo(
                type=exception_info[0],
                value=exception_info[1],
                traceback=exception_info[2]
            )
        elif isinstance(exception_info, BaseException):
            # Single exception object
            exception_info = ExceptionInfo(
                type=type(exception_info),
                value=exception_info,
                traceback=exception_info.__traceback__
            )
        else:
            exception_info = None
        
        # Format the message
        formatted_message = self._format_message(message, args, kwargs)
        
        # Get caller frame information (depth=2: _log -> calling method -> user code)
        frame = FrameInspector.get_caller_frame(depth=2)
        frame_info = FrameInspector.extract_frame_info(frame)
        
        # Get process and thread information
        try:
            process_info = ProcessInfo(
                id=os.getpid(),
                name=multiprocessing.current_process().name
            )
        except Exception:
            process_info = ProcessInfo(id=os.getpid(), name="MainProcess")
        
        thread_info = ThreadInfo(
            id=threading.get_ident(),
            name=threading.current_thread().name
        )
        
        # Create file info
        file_info = FileInfo(
            name=frame_info['file_name'],
            path=frame_info['filename']
        )
        
        # Calculate elapsed time
        elapsed = datetime.now() - self.start_time
        
        # Merge extra context
        record_extra = self.extra.copy()
        record_extra.update(kwargs)
        
        # Create the log record
        record = LogRecord(
            elapsed=elapsed,
            exception=exception_info,
            extra=record_extra,
            file=file_info,
            function=frame_info['function'],
            level=level_obj,
            line=frame_info['lineno'],
            message=formatted_message,
            module=frame_info['module'],
            name=frame_info['module'],
            process=process_info,
            thread=thread_info,
            time=datetime.now()
        )
        
        # Pass to all handlers (for now, just print to console)
        self._dispatch_record(record)
    
    def _get_level(self, level: Union[str, int]) -> Level:
        """Get Level object from name or number
        
        Args:
            level: Level name (string) or number (int)
            
        Returns:
            Level object
            
        Raises:
            InvalidLevelError: If level is not found
        """
        if isinstance(level, str):
            level_upper = level.upper()
            if level_upper not in self.levels:
                raise InvalidLevelError(f"Unknown level: {level}")
            return self.levels[level_upper]
        elif isinstance(level, int):
            # Find level by number
            for lvl in self.levels.values():
                if lvl.no == level:
                    return lvl
            raise InvalidLevelError(f"No level with number {level}")
        else:
            raise InvalidLevelError(f"Invalid level type: {type(level)}")
    
    def _format_message(self, message: str, args: tuple, kwargs: Dict[str, Any]) -> str:
        """Format the log message with args and kwargs
        
        Supports three formatting styles:
        1. Positional: logger.info("User {}", "John")
        2. Named: logger.info("User {name}", name="John")
        3. Mixed: logger.info("User {} from {city}", "John", city="NYC")
        
        Args:
            message: Message template string
            args: Positional arguments
            kwargs: Keyword arguments
            
        Returns:
            Formatted message string
        """
        if not args and not kwargs:
            return message
        
        try:
            # Try to format with both args and kwargs
            if args and kwargs:
                # Mixed mode: replace {} with args, then format with kwargs
                # First, replace {} placeholders with args
                formatted = message
                arg_index = 0
                result = []
                i = 0
                while i < len(formatted):
                    if formatted[i] == '{':
                        if i + 1 < len(formatted) and formatted[i + 1] == '}':
                            # Found empty {} placeholder
                            if arg_index < len(args):
                                result.append(str(args[arg_index]))
                                arg_index += 1
                                i += 2  # Skip {}
                                continue
                    result.append(formatted[i])
                    i += 1
                
                formatted = ''.join(result)
                # Now format with kwargs
                return formatted.format(**kwargs)
            
            elif args:
                # Only positional args - replace {} with args in order
                formatted = message
                arg_index = 0
                result = []
                i = 0
                while i < len(formatted):
                    if formatted[i] == '{':
                        if i + 1 < len(formatted) and formatted[i + 1] == '}':
                            # Found empty {} placeholder
                            if arg_index < len(args):
                                result.append(str(args[arg_index]))
                                arg_index += 1
                                i += 2  # Skip {}
                                continue
                    result.append(formatted[i])
                    i += 1
                
                return ''.join(result)
            
            else:
                # Only kwargs - standard format
                return message.format(**kwargs)
        
        except (KeyError, IndexError, ValueError) as e:
            # If formatting fails, return message with error indication
            # Don't crash logging due to formatting errors
            return f"{message} [FORMATTING ERROR: {e}]"
    
    def _dispatch_record(self, record: LogRecord) -> None:
        """Dispatch a log record to all handlers
        
        Args:
            record: LogRecord to dispatch
        """
        # For now, just print to stderr (will be replaced with handler system in Day 5)
        # Format: [LEVEL] message (file:line)
        print(
            f"[{record.level.name}] {record.message} "
            f"({record.file.name}:{record.function}:{record.line})",
            file=sys.stderr
        )
    
    def bind(self, **kwargs) -> 'Logger':
        """Create a bound logger with extra context
        
        Args:
            **kwargs: Extra context to bind
            
        Returns:
            BoundLogger instance (will be implemented in Day 14)
        """
        # TODO: Implement bind (Day 14)
        raise NotImplementedError("bind() will be implemented in Day 14")
    
    def contextualize(self, **kwargs):
        """Create a context manager with extra context
        
        Args:
            **kwargs: Extra context for the context manager
            
        Returns:
            ContextManager instance (will be implemented in Day 14)
        """
        # TODO: Implement contextualize (Day 14)
        raise NotImplementedError("contextualize() will be implemented in Day 14")
    
    def catch(self, exception=Exception, **kwargs):
        """Decorator to catch exceptions
        
        Args:
            exception: Exception type(s) to catch
            **kwargs: Additional options
            
        Returns:
            Decorator function (will be implemented in Day 16)
        """
        # TODO: Implement catch decorator (Day 16)
        raise NotImplementedError("catch() will be implemented in Day 16")
    
    def opt(self, **kwargs) -> 'Logger':
        """Return logger with options
        
        Args:
            **kwargs: Options to apply
            
        Returns:
            Logger with options applied (will be implemented in Day 16)
        """
        # TODO: Implement opt (Day 16)
        raise NotImplementedError("opt() will be implemented in Day 16")


# Create a global logger instance for convenience
logger = Logger()
