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
from .exceptions import InvalidLevelError, HandlerNotFoundError
from .handler import Handler, StreamHandler, FileHandler, CallableHandler
from .formatter import Formatter
from .bound_logger import BoundLogger
from pathlib import Path


class OptLogger:
    """Temporary logger wrapper with options applied
    
    This class wraps a Logger instance and applies options to a single log call.
    It's returned by Logger.opt() and should be used immediately.
    
    Attributes:
        _logger: The wrapped Logger instance
        _options: Options to apply (exception, depth, record, lazy)
    """
    
    def __init__(self, logger: 'Logger', **options):
        """Initialize OptLogger
        
        Args:
            logger: Logger instance to wrap
            **options: Options to apply
        """
        self._logger = logger
        self._options = options
    
    def _log_with_options(self, level: str, message: str, *args, **kwargs):
        """Log with options applied
        
        Args:
            level: Log level name
            message: Log message
            *args: Positional arguments for message formatting
            **kwargs: Keyword arguments for message formatting and context
        """
        # Apply depth option (adjust frame inspection)
        depth = self._options.get('depth', 0)
        
        # Apply exception option
        if 'exception' in self._options:
            exc = self._options['exception']
            if exc is True:
                # Use sys.exc_info() to get current exception
                import sys
                exc_info = sys.exc_info()
                if exc_info[0] is not None:
                    kwargs['exception'] = exc_info[1]
            elif exc is not None and exc is not False:
                # Use provided exception
                kwargs['exception'] = exc
        
        # Apply lazy option (deferred evaluation)
        # For now, we'll just pass through - full lazy evaluation is complex
        
        # Call the logger with adjusted depth
        # We need to adjust the frame depth for accurate file/line info
        original_depth = 2 + depth  # Account for this wrapper
        self._logger._log(level, message, *args, _depth=original_depth, **kwargs)
    
    def trace(self, message: str, *args, **kwargs):
        """Log trace with options"""
        self._log_with_options("TRACE", message, *args, **kwargs)
    
    def debug(self, message: str, *args, **kwargs):
        """Log debug with options"""
        self._log_with_options("DEBUG", message, *args, **kwargs)
    
    def info(self, message: str, *args, **kwargs):
        """Log info with options"""
        self._log_with_options("INFO", message, *args, **kwargs)
    
    def success(self, message: str, *args, **kwargs):
        """Log success with options"""
        self._log_with_options("SUCCESS", message, *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs):
        """Log warning with options"""
        self._log_with_options("WARNING", message, *args, **kwargs)
    
    def error(self, message: str, *args, **kwargs):
        """Log error with options"""
        self._log_with_options("ERROR", message, *args, **kwargs)
    
    def critical(self, message: str, *args, **kwargs):
        """Log critical with options"""
        self._log_with_options("CRITICAL", message, *args, **kwargs)
    
    def log(self, level: Union[str, int], message: str, *args, **kwargs):
        """Log at specified level with options"""
        if isinstance(level, int):
            # Find level name by number
            for name, lvl in self._logger.levels.items():
                if lvl.no == level:
                    level = name
                    break
        self._log_with_options(level, message, *args, **kwargs)


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
        self._disabled: set = set()  # Set of disabled module/logger names
        self._lock = threading.Lock()  # Thread lock for handler operations
        
    def add(self, sink: Any, **options) -> int:
        """Add a handler to the logger
        
        Automatically detects the handler type based on the sink:
        - str or Path: FileHandler
        - file-like object (stream): StreamHandler
        - callable: CallableHandler
        
        Args:
            sink: Output destination (file path, stream, or callable)
            **options: Handler configuration options:
                - level: Minimum level (str or int, default: TRACE/5)
                - format: Format string (default: simple format)
                - filter: Filter function (default: None)
                - colorize: Enable colors (default: auto-detect)
                - serialize: JSON serialization (default: False)
                - backtrace: Show full exception traceback (default: True)
                - diagnose: Show variable values in exception frames (default: False)
                - mode: File mode for FileHandler (default: 'a')
                - encoding: File encoding for FileHandler (default: 'utf-8')
                - rotation: Rotation strategy for FileHandler (default: None)
                  Can be: size string ("10 MB"), time string ("daily", "1 hour"),
                  or integer (bytes)
                - compression: Compression format for FileHandler (default: None)
                  Can be: "gz", "gzip", or "zip"
                - retention: Retention policy for FileHandler (default: None)
                  Can be: integer (keep N files), string (e.g., "7 days", "30 days")
            
        Returns:
            Handler ID for later removal
            
        Example:
            >>> handler_id = logger.add("app.log", level="INFO")
            >>> logger.add("app.log", rotation="10 MB")  # Rotate when 10MB
            >>> logger.add("app.log", rotation="daily")  # Rotate daily
            >>> logger.add("app.log", rotation="10 MB", compression="gz")  # Rotate and compress
            >>> logger.add("app.log", rotation="daily", retention=7)  # Keep 7 files
            >>> logger.add("app.log", retention="30 days")  # Delete files > 30 days
            >>> logger.add(sys.stderr, level="ERROR", colorize=True)
            >>> logger.add(lambda msg: print(msg), level="DEBUG")
        """
        with self._lock:
            # Parse options
            level = options.get('level', 'TRACE')
            format_string = options.get('format', None)
            filter_func = options.get('filter', None)
            colorize = options.get('colorize', None)
            serialize = options.get('serialize', False)
            backtrace = options.get('backtrace', True)
            diagnose = options.get('diagnose', False)
            
            # Get Level object
            if isinstance(level, str):
                level_obj = self._get_level(level)
            elif isinstance(level, int):
                level_obj = self._get_level(level)
            else:
                level_obj = level  # Assume it's already a Level object
            
            # Create formatter
            formatter = Formatter(
                format_string=format_string,
                colorize=colorize or False,
                backtrace=backtrace,
                diagnose=diagnose
            )
            
            # Determine handler type and create handler
            handler = None
            
            if isinstance(sink, (str, Path)):
                # File handler
                mode = options.get('mode', 'a')
                encoding = options.get('encoding', 'utf-8')
                rotation = options.get('rotation', None)
                compression = options.get('compression', None)
                retention = options.get('retention', None)
                handler = FileHandler(
                    sink=Path(sink),
                    level=level_obj,
                    formatter=formatter,
                    mode=mode,
                    encoding=encoding,
                    rotation=rotation,
                    compression=compression,
                    retention=retention,
                    filter_func=filter_func,
                    colorize=colorize or False,
                    serialize=serialize
                )
            
            elif hasattr(sink, 'write') and hasattr(sink, 'flush'):
                # Stream handler (has write and flush methods)
                handler = StreamHandler(
                    sink=sink,
                    level=level_obj,
                    formatter=formatter,
                    filter_func=filter_func,
                    colorize=colorize,
                    serialize=serialize
                )
            
            elif callable(sink):
                # Callable handler
                handler = CallableHandler(
                    sink=sink,
                    level=level_obj,
                    formatter=formatter,
                    filter_func=filter_func,
                    colorize=colorize or False,
                    serialize=serialize
                )
            
            else:
                raise ValueError(
                    f"Invalid sink type: {type(sink)}. "
                    f"Expected str, Path, file-like object, or callable."
                )
            
            # Assign unique ID
            self._handler_id_counter += 1
            handler.id = self._handler_id_counter
            
            # Add to handlers list
            self.handlers.append(handler)
            
            return handler.id
    
    def remove(self, handler_id: int = None) -> None:
        """Remove a handler by ID
        
        If no handler_id is provided, removes all handlers.
        
        Args:
            handler_id: ID of the handler to remove (None = remove all)
            
        Raises:
            HandlerNotFoundError: If handler_id is not found
            
        Example:
            >>> handler_id = logger.add("app.log")
            >>> logger.remove(handler_id)
            >>> logger.remove()  # Remove all handlers
        """
        with self._lock:
            if handler_id is None:
                # Remove all handlers
                for handler in self.handlers:
                    try:
                        handler.close()
                    except Exception:
                        pass
                self.handlers.clear()
                return
            
            # Find and remove specific handler
            for i, handler in enumerate(self.handlers):
                if handler.id == handler_id:
                    try:
                        handler.close()
                    except Exception:
                        pass
                    self.handlers.pop(i)
                    return
            
            # Handler not found
            raise HandlerNotFoundError(handler_id=handler_id)
    
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
    
    def exception(self, message: str, *args, **kwargs) -> None:
        """Log an exception with traceback
        
        This is a convenience method that logs at ERROR level and automatically
        captures the current exception information from sys.exc_info().
        Should be called from within an except block.
        
        Args:
            message: Log message (may contain format placeholders)
            *args: Positional arguments for formatting
            **kwargs: Keyword arguments for formatting or extra context
            
        Example:
            >>> try:
            ...     result = 1 / 0
            ... except:
            ...     logger.exception("Division failed!")
        """
        # Add exception info to kwargs if not already present
        if 'exception' not in kwargs:
            kwargs['exception'] = True  # Signal to capture current exception
        
        self._log("ERROR", message, *args, **kwargs)
    
    def bind(self, **kwargs) -> BoundLogger:
        """Create a bound logger with contextual information
        
        Returns a BoundLogger that automatically includes the provided
        context in all log records. This is useful for adding request IDs,
        user information, or any contextual data.
        
        Args:
            **kwargs: Key-value pairs to bind as context
            
        Returns:
            BoundLogger instance with bound context
            
        Example:
            >>> logger = Logger()
            >>> request_logger = logger.bind(request_id="REQ-123", user="alice")
            >>> request_logger.info("Processing request")
            # Log will include request_id and user in extra
            
            >>> # Chaining is supported
            >>> op_logger = request_logger.bind(operation="checkout")
            >>> op_logger.info("Starting checkout")
            # Log includes request_id, user, and operation
        """
        return BoundLogger(self, **kwargs)
    
    def contextualize(self, **kwargs) -> 'ContextManager':
        """Create a context manager for temporary context binding
        
        Returns a context manager that temporarily adds context to the
        logger's global extra dict. The context is automatically removed
        when exiting the context.
        
        Args:
            **kwargs: Key-value pairs to add as temporary context
            
        Returns:
            ContextManager instance for use in with statement
            
        Example:
            >>> logger = Logger()
            >>> with logger.contextualize(request_id="REQ-123"):
            ...     logger.info("Processing")  # Includes request_id
            ...     logger.info("Done")  # Includes request_id
            >>> logger.info("After context")  # No request_id
        """
        from .context_manager import ContextManager
        return ContextManager(self, **kwargs)
    
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
    
    def _log(self, level: Union[str, int], message: str, *args, _depth: int = 2, **kwargs) -> None:
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
            _depth: Stack frame depth adjustment (default: 2)
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
        
        # Get caller frame information
        frame = FrameInspector.get_caller_frame(depth=_depth)
        frame_info = FrameInspector.extract_frame_info(frame)
        
        # Check if this module is disabled
        module_name = frame_info['module']
        if module_name in self._disabled:
            return  # Skip logging for disabled modules
        
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
        # Priority: kwargs['extra'] > self.extra (global logger extra)
        record_extra = self.extra.copy()
        if 'extra' in kwargs:
            # Merge with extra from kwargs
            record_extra.update(kwargs.pop('extra'))
        else:
            # If no 'extra' in kwargs, add remaining kwargs as extra
            # (for backward compatibility)
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
        
        Sends the record to each registered handler. If no handlers
        are registered, outputs to stderr as a fallback.
        
        Args:
            record: LogRecord to dispatch
        """
        if not self.handlers:
            # Fallback: print to stderr if no handlers are registered
            print(
                f"[{record.level.name}] {record.message} "
                f"({record.file.name}:{record.function}:{record.line})",
                file=sys.stderr
            )
            return
        
        # Dispatch to all handlers
        for handler in self.handlers:
            try:
                handler.emit(record)
            except Exception as e:
                # Never let handler errors break logging
                try:
                    sys.stderr.write(
                        f"Error in handler {handler.id} ({type(handler).__name__}): {e}\n"
                    )
                except Exception:
                    # If even this fails, just silently continue
                    pass
    
    
    def catch(self, exception=Exception, *, level="ERROR", message="An error occurred", reraise=False, onerror=None):
        """Decorator to catch exceptions in functions
        
        Wraps a function in try/except and logs any exceptions that occur.
        Useful for preventing crashes and ensuring exceptions are logged.
        
        Args:
            exception: Exception type(s) to catch (default: Exception)
            level: Log level to use when catching exception (default: "ERROR")
            message: Custom message template (default: "An error occurred")
            reraise: Whether to reraise the exception after logging (default: False)
            onerror: Optional callback function(exception) called when error occurs
            
        Returns:
            Decorator function that wraps the target function
            
        Example:
            >>> @logger.catch()
            ... def risky_function():
            ...     return 1 / 0
            
            >>> @logger.catch(exception=ValueError, level="WARNING", reraise=True)
            ... def validate_data(data):
            ...     if not data:
            ...         raise ValueError("Data is empty")
        """
        import functools
        
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except exception as e:
                    # Log the exception
                    if message:
                        self.log(level, message, exception=e)
                    else:
                        self.log(level, f"Exception in {func.__name__}", exception=e)
                    
                    # Call onerror callback if provided
                    if onerror is not None and callable(onerror):
                        try:
                            onerror(e)
                        except Exception:
                            pass  # Don't let onerror break the catch
                    
                    # Reraise if requested
                    if reraise:
                        raise
                    
                    # Otherwise, return None
                    return None
            
            return wrapper
        
        return decorator
    
    def opt(self, *, exception=None, depth=0, record=False, lazy=False) -> 'OptLogger':
        """Return a logger wrapper with options applied to the next log call
        
        This method returns an OptLogger instance that applies options to a single
        log call. Useful for including exception info, adjusting stack depth, etc.
        
        Args:
            exception: Include exception info in the log
                - True: Use sys.exc_info() to get current exception
                - Exception instance: Use specific exception
                - False/None: No exception (default)
            depth: Stack depth adjustment for file/line info (default: 0)
                Positive values go deeper in the stack
            record: Whether to log with full LogRecord (not fully implemented)
            lazy: Defer message evaluation (not fully implemented)
            
        Returns:
            OptLogger instance that wraps this logger with options
            
        Example:
            >>> try:
            ...     1 / 0
            ... except:
            ...     logger.opt(exception=True).error("Division failed")
            
            >>> logger.opt(depth=1).info("Called from wrapper")
        """
        return OptLogger(self, exception=exception, depth=depth, record=record, lazy=lazy)
    
    def add_level(self, name: str, no: int, color: str = "white", icon: str = "") -> None:
        """Add a custom log level
        
        Creates a new log level and dynamically adds a logging method to the Logger class.
        
        Args:
            name: Name of the level (e.g., "VERBOSE", "NOTICE")
            no: Numeric level value (higher = more severe)
            color: ANSI color name for the level (default: "white")
            icon: Icon/emoji for the level (default: "")
            
        Example:
            >>> logger.add_level("VERBOSE", 15, color="cyan", icon="🔍")
            >>> logger.verbose("Verbose message")  # New method created automatically
        """
        # Create the Level object
        level = Level(name=name.upper(), no=no, color=color, icon=icon)
        
        # Add to levels dict
        self.levels[name.upper()] = level
        
        # Dynamically add logging method to Logger class
        method_name = name.lower()
        
        def log_method(self, message: str, *args, **kwargs):
            """Dynamically generated log method"""
            self._log(name.upper(), message, *args, **kwargs)
        
        # Set the method on the Logger class
        setattr(Logger, method_name, log_method)
    
    def disable(self, name: str) -> None:
        """Disable logging from a specific module or logger
        
        Args:
            name: Module name or logger name to disable (e.g., "requests", "urllib3")
            
        Example:
            >>> logger.disable("urllib3")  # Silence urllib3 logs
            >>> logger.disable("myapp.tests")  # Silence test module logs
        """
        self._disabled.add(name)
    
    def enable(self, name: str) -> None:
        """Enable logging from a previously disabled module or logger
        
        Args:
            name: Module name or logger name to enable
            
        Example:
            >>> logger.enable("urllib3")  # Re-enable urllib3 logs
        """
        self._disabled.discard(name)


# Create a global logger instance for convenience
logger = Logger()
