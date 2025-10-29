"""
Handler classes for different output destinations
"""

from abc import ABC, abstractmethod
from typing import Any, Callable, Optional, TextIO, Union
from pathlib import Path
from datetime import datetime
import sys
import threading


class Handler(ABC):
    """Abstract base class for all handlers
    
    A handler determines where and how log records are outputted.
    Each handler has a sink (destination), level threshold, formatter,
    and optional filter function.
    
    Attributes:
        id: Unique identifier for this handler
        sink: Output destination (stream, file path, or callable)
        level: Minimum level for this handler to emit
        formatter: Formatter instance to format records
        filter_func: Optional filter function
        colorize: Whether to apply colors (for terminals)
        serialize: Whether to serialize to JSON
        backtrace: Show full traceback for exceptions
        diagnose: Show variables in exception frames
        enqueue: Use async queue (not implemented in Day 5)
        catch: Catch errors in emit() (not implemented in Day 5)
    """
    
    def __init__(
        self,
        sink: Any,
        level: 'Level',
        formatter: 'Formatter',
        filter_func: Optional[Callable] = None,
        colorize: bool = None,
        serialize: bool = False,
        backtrace: bool = True,
        diagnose: bool = False,
        enqueue: bool = False,
        catch: bool = True,
    ):
        """Initialize a handler
        
        Args:
            sink: Output destination
            level: Minimum Level object for emission
            formatter: Formatter instance
            filter_func: Optional filter function(record) -> bool
            colorize: Enable colorization (None = auto-detect)
            serialize: Serialize records to JSON
            backtrace: Show full exception traceback
            diagnose: Show variables in exception frames
            enqueue: Use async queue (for Day 17)
            catch: Catch errors in emit() (for Day 16)
        """
        self.id: int = 0  # Will be set by Logger
        self.sink: Any = sink
        self.level: 'Level' = level
        self.formatter: 'Formatter' = formatter
        self.filter_func: Optional[Callable] = filter_func
        self.colorize: bool = colorize if colorize is not None else self._should_colorize()
        self.serialize: bool = serialize
        self.backtrace: bool = backtrace
        self.diagnose: bool = diagnose
        self.enqueue: bool = enqueue
        self.catch: bool = catch
        self._lock = threading.Lock()
        
    def _should_colorize(self) -> bool:
        """Determine if output should be colorized
        
        Returns:
            True if colorization should be enabled
        """
        # Default: no colorization (can be overridden by subclasses)
        return False
    
    @abstractmethod
    def emit(self, record: 'LogRecord') -> None:
        """Emit a log record (must be implemented by subclasses)
        
        Args:
            record: LogRecord to emit
        """
        pass
    
    def should_emit(self, record: 'LogRecord') -> bool:
        """Check if this handler should emit the given record
        
        Checks level threshold and applies filter function if present.
        
        Args:
            record: LogRecord to check
            
        Returns:
            True if record should be emitted, False otherwise
        """
        # Check level threshold
        if record.level < self.level:
            return False
        
        # Apply filter function if present
        if self.filter_func is not None:
            try:
                return self.filter_func(record)
            except Exception:
                # If filter raises an exception, emit the record
                return True
        
        return True
    
    def format(self, record: 'LogRecord') -> str:
        """Format a log record using the formatter
        
        Args:
            record: LogRecord to format
            
        Returns:
            Formatted string
        """
        try:
            return self.formatter.format(record)
        except Exception as e:
            # Fallback to simple formatting if formatter fails
            return f"[{record.level.name}] {record.message} (formatter error: {e})"
    
    def close(self) -> None:
        """Close the handler and release resources
        
        Default implementation does nothing. Override in subclasses
        that need cleanup (e.g., closing files).
        """
        pass


class StreamHandler(Handler):
    """Handler for stream output (console, stderr, stdout, etc.)
    
    This handler writes log records to any file-like object (stream).
    Commonly used for console output to sys.stderr or sys.stdout.
    
    Attributes:
        stream: The output stream (file-like object)
    """
    
    def __init__(
        self,
        sink: TextIO,
        level: 'Level',
        formatter: 'Formatter',
        **options
    ):
        """Initialize stream handler
        
        Args:
            sink: Stream to write to (sys.stderr, sys.stdout, etc.)
            level: Minimum level
            formatter: Formatter instance
            **options: Additional handler options
        """
        super().__init__(sink, level, formatter, **options)
        self.stream: TextIO = sink
    
    def _should_colorize(self) -> bool:
        """Auto-detect if stream supports colors
        
        Returns:
            True if stream is a TTY
        """
        try:
            return hasattr(self.stream, 'isatty') and self.stream.isatty()
        except Exception:
            return False
    
    def emit(self, record: 'LogRecord') -> None:
        """Write formatted record to stream
        
        Args:
            record: LogRecord to emit
        """
        if not self.should_emit(record):
            return
        
        try:
            with self._lock:
                formatted = self.format(record)
                self.stream.write(formatted + '\n')
                self.stream.flush()
        except Exception as e:
            # Don't let handler errors break logging
            sys.stderr.write(f"Error in StreamHandler: {e}\n")
    
    def close(self) -> None:
        """Flush the stream
        
        Note: Does not close sys.stdout or sys.stderr
        """
        try:
            if self.stream not in (sys.stdout, sys.stderr):
                self.stream.close()
            else:
                self.stream.flush()
        except Exception:
            pass


class FileHandler(Handler):
    """Handler for file output
    
    This handler writes log records to a file. Supports file rotation,
    compression, and retention (to be implemented in later days).
    
    Attributes:
        path: Path to the log file
        mode: File open mode ('a' for append, 'w' for write)
        encoding: File encoding (default 'utf-8')
        file_handle: Open file handle
        rotation: Optional rotation strategy
    """
    
    def __init__(
        self,
        sink: Path,
        level: 'Level',
        formatter: 'Formatter',
        mode: str = 'a',
        encoding: str = 'utf-8',
        buffering: int = 1,  # Line buffered
        rotation: Optional[Union[str, int, 'Rotation']] = None,
        **options
    ):
        """Initialize file handler
        
        Args:
            sink: Path to log file (str or Path)
            level: Minimum level
            formatter: Formatter instance
            mode: File open mode ('a' or 'w')
            encoding: File encoding
            buffering: Buffering mode (1 = line buffered)
            rotation: Rotation strategy. Can be:
                - None: No rotation (default)
                - str: Time-based rotation (e.g., "1 hour", "daily", "12:00")
                - int: Size-based rotation in bytes
                - str: Size-based rotation (e.g., "10 MB", "500 KB")
                - Rotation: Custom rotation strategy instance
            **options: Additional handler options
        """
        super().__init__(sink, level, formatter, **options)
        self.path: Path = Path(sink) if not isinstance(sink, Path) else sink
        self.mode: str = mode
        self.encoding: str = encoding
        self.buffering: int = buffering
        self.file_handle: Optional[TextIO] = None
        self.rotation: Optional['Rotation'] = self._parse_rotation(rotation)
        
        # Create parent directories if needed
        self.path.parent.mkdir(parents=True, exist_ok=True)
        
        # Open the file
        self._open_file()
    
    def _parse_rotation(self, rotation: Optional[Union[str, int, 'Rotation']]) -> Optional['Rotation']:
        """Parse rotation parameter into a Rotation instance
        
        Args:
            rotation: Rotation specification
            
        Returns:
            Rotation instance or None
        """
        if rotation is None:
            return None
        
        # Already a Rotation instance
        from .rotation import Rotation, SizeRotation, TimeRotation
        if isinstance(rotation, Rotation):
            return rotation
        
        # Integer or size string -> SizeRotation
        if isinstance(rotation, int):
            return SizeRotation(rotation)
        
        if isinstance(rotation, str):
            # Try to determine if it's a size or time specification
            # Size specifications contain size units: KB, MB, GB, etc.
            size_units = ['B', 'KB', 'MB', 'GB', 'TB', 'K', 'M', 'G', 'T']
            upper_rotation = rotation.upper()
            
            # Check if it looks like a size specification
            is_size = any(unit in upper_rotation for unit in size_units)
            
            if is_size:
                try:
                    return SizeRotation(rotation)
                except (ValueError, TypeError):
                    # If size parsing fails, try time rotation
                    pass
            
            # Try time rotation
            try:
                return TimeRotation(rotation)
            except ValueError:
                # Last attempt: try size rotation
                try:
                    return SizeRotation(rotation)
                except (ValueError, TypeError):
                    raise ValueError(
                        f"Invalid rotation specification: '{rotation}'. "
                        "Expected size (e.g., '10 MB'), time interval (e.g., '1 hour'), "
                        "or schedule (e.g., 'daily', '12:00')."
                    )
        
        raise TypeError(
            f"rotation must be None, int, str, or Rotation instance, got {type(rotation)}"
        )
    
    def _should_colorize(self) -> bool:
        """Files should not have colors by default
        
        Returns:
            False (no colors for file output)
        """
        return False
    
    def _open_file(self) -> None:
        """Open the log file for writing"""
        try:
            self.file_handle = open(
                self.path,
                mode=self.mode,
                encoding=self.encoding,
                buffering=self.buffering
            )
        except Exception as e:
            sys.stderr.write(f"Error opening log file {self.path}: {e}\n")
            raise
    
    def _rotate(self) -> None:
        """Perform file rotation
        
        This method:
        1. Closes the current file
        2. Renames it with a timestamp
        3. Opens a new file with the original name
        4. Resets the rotation strategy
        """
        try:
            # Close current file
            if self.file_handle is not None:
                self.file_handle.flush()
                self.file_handle.close()
                self.file_handle = None
            
            # Generate rotated filename with timestamp (including microseconds for uniqueness)
            now = datetime.now()
            timestamp = now.strftime("%Y-%m-%d_%H-%M-%S") + f"-{now.microsecond:06d}"
            
            # Get file parts
            stem = self.path.stem  # Filename without extension
            suffix = self.path.suffix  # Extension including the dot
            parent = self.path.parent
            
            # Create rotated filename: app.log -> app.2024-01-15_14-30-45.log
            rotated_path = parent / f"{stem}.{timestamp}{suffix}"
            
            # Rename current file to rotated name
            if self.path.exists():
                self.path.rename(rotated_path)
            
            # Reset rotation strategy
            if self.rotation:
                self.rotation.reset()
            
            # Open new file
            self._open_file()
            
        except Exception as e:
            sys.stderr.write(f"Error during file rotation: {e}\n")
            # Try to reopen the original file even if rotation failed
            if self.file_handle is None:
                try:
                    self._open_file()
                except Exception:
                    pass
    
    def emit(self, record: 'LogRecord') -> None:
        """Write formatted record to file
        
        Checks if rotation is needed before writing.
        
        Args:
            record: LogRecord to emit
        """
        if not self.should_emit(record):
            return
        
        try:
            with self._lock:
                # Check if rotation is needed
                if self.rotation and self.rotation.should_rotate(self.path, record):
                    self._rotate()
                
                # Ensure file is open
                if self.file_handle is None:
                    self._open_file()
                
                # Write the record
                formatted = self.format(record)
                self.file_handle.write(formatted + '\n')
                self.file_handle.flush()
        except Exception as e:
            if self.catch:
                sys.stderr.write(f"Error in FileHandler: {e}\n")
            else:
                raise
    
    def close(self) -> None:
        """Close the file handle"""
        try:
            with self._lock:
                if self.file_handle is not None:
                    self.file_handle.flush()
                    self.file_handle.close()
                    self.file_handle = None
        except Exception:
            pass


class CallableHandler(Handler):
    """Handler for callable/function output
    
    This handler calls a user-provided function with each log record.
    The function receives either a formatted string or a LogRecord object.
    
    Attributes:
        func: The callable to invoke
    """
    
    def __init__(
        self,
        sink: Callable,
        level: 'Level',
        formatter: 'Formatter',
        **options
    ):
        """Initialize callable handler
        
        Args:
            sink: Callable function(message: str) or function(record: LogRecord)
            level: Minimum level
            formatter: Formatter instance
            **options: Additional handler options
        """
        super().__init__(sink, level, formatter, **options)
        if not callable(sink):
            raise TypeError(f"Sink must be callable, got {type(sink)}")
        self.func: Callable = sink
    
    def emit(self, record: 'LogRecord') -> None:
        """Call the function with the record
        
        If serialize=True, the function receives a JSON string.
        Otherwise, it receives a formatted string.
        
        Args:
            record: LogRecord to emit
        """
        if not self.should_emit(record):
            return
        
        try:
            with self._lock:
                if self.serialize:
                    # Serialize to JSON and pass as string
                    from .utils import Serializer
                    json_str = Serializer.serialize(record)
                    self.func(json_str)
                else:
                    # Format and pass as string
                    formatted = self.format(record)
                    self.func(formatted)
        except Exception as e:
            if self.catch:
                # Don't let handler errors break logging
                sys.stderr.write(f"Error in CallableHandler: {e}\n")
            else:
                raise
