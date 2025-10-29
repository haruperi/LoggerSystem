"""
BoundLogger for context binding

This module provides the BoundLogger class which allows you to bind
contextual information to a logger instance. All log calls from a
BoundLogger automatically include the bound context.
"""

from typing import Any, Dict, Union


class BoundLogger:
    """A logger with bound contextual information
    
    BoundLogger wraps a parent Logger and automatically adds bound
    context to all log records. This is useful for adding request IDs,
    user information, or any other contextual data that should be
    included in all logs from a specific scope.
    
    Example:
        >>> logger = Logger()
        >>> request_logger = logger.bind(request_id="REQ-123", user="alice")
        >>> request_logger.info("Processing request")
        # Logs will include request_id and user in extra context
        
        >>> # Chaining is supported
        >>> operation_logger = request_logger.bind(operation="checkout")
        >>> operation_logger.info("Starting checkout")
        # Logs will include request_id, user, and operation
    
    Attributes:
        _parent: The parent Logger instance
        _bound_extra: Dictionary of bound context data
    """
    
    def __init__(self, parent: 'Logger', **bound_extra):
        """Initialize a BoundLogger
        
        Args:
            parent: The parent Logger instance to wrap
            **bound_extra: Key-value pairs to bind as context
        """
        self._parent = parent
        self._bound_extra: Dict[str, Any] = bound_extra
    
    def bind(self, **kwargs) -> 'BoundLogger':
        """Create a new BoundLogger with additional context
        
        Returns a new BoundLogger that includes both the current
        bound context and the new context. This supports chaining.
        
        Args:
            **kwargs: Additional context to bind
            
        Returns:
            New BoundLogger with merged context
            
        Example:
            >>> logger = Logger()
            >>> user_logger = logger.bind(user_id=123)
            >>> request_logger = user_logger.bind(request_id="REQ-456")
            >>> request_logger.info("Processing")
            # Includes both user_id and request_id
        """
        # Merge current bound context with new context
        merged_extra = {**self._bound_extra, **kwargs}
        return BoundLogger(self._parent, **merged_extra)
    
    def _log_with_context(self, level: Union[str, int], message: str, *args, **kwargs) -> None:
        """Internal method to log with bound context
        
        Args:
            level: Log level
            message: Log message
            *args: Positional arguments for message formatting
            **kwargs: Keyword arguments (will be merged with bound context)
        """
        # Merge bound extra with kwargs extra
        # Priority: kwargs > bound_extra
        merged_extra = {**self._bound_extra}
        
        # If kwargs has 'extra', merge it
        if 'extra' in kwargs:
            merged_extra.update(kwargs.pop('extra'))
        
        # Add merged extra back to kwargs
        kwargs['extra'] = merged_extra
        
        # Call parent logger's _log method
        self._parent._log(level, message, *args, **kwargs)
    
    # Implement all logging methods
    
    def trace(self, message: str, *args, **kwargs) -> None:
        """Log a trace message with bound context
        
        Args:
            message: Log message
            *args: Positional arguments for formatting
            **kwargs: Keyword arguments
        """
        self._log_with_context("TRACE", message, *args, **kwargs)
    
    def debug(self, message: str, *args, **kwargs) -> None:
        """Log a debug message with bound context
        
        Args:
            message: Log message
            *args: Positional arguments for formatting
            **kwargs: Keyword arguments
        """
        self._log_with_context("DEBUG", message, *args, **kwargs)
    
    def info(self, message: str, *args, **kwargs) -> None:
        """Log an info message with bound context
        
        Args:
            message: Log message
            *args: Positional arguments for formatting
            **kwargs: Keyword arguments
        """
        self._log_with_context("INFO", message, *args, **kwargs)
    
    def success(self, message: str, *args, **kwargs) -> None:
        """Log a success message with bound context
        
        Args:
            message: Log message
            *args: Positional arguments for formatting
            **kwargs: Keyword arguments
        """
        self._log_with_context("SUCCESS", message, *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs) -> None:
        """Log a warning message with bound context
        
        Args:
            message: Log message
            *args: Positional arguments for formatting
            **kwargs: Keyword arguments
        """
        self._log_with_context("WARNING", message, *args, **kwargs)
    
    def error(self, message: str, *args, **kwargs) -> None:
        """Log an error message with bound context
        
        Args:
            message: Log message
            *args: Positional arguments for formatting
            **kwargs: Keyword arguments
        """
        self._log_with_context("ERROR", message, *args, **kwargs)
    
    def critical(self, message: str, *args, **kwargs) -> None:
        """Log a critical message with bound context
        
        Args:
            message: Log message
            *args: Positional arguments for formatting
            **kwargs: Keyword arguments
        """
        self._log_with_context("CRITICAL", message, *args, **kwargs)
    
    def exception(self, message: str, *args, **kwargs) -> None:
        """Log an exception with traceback and bound context
        
        Args:
            message: Log message
            *args: Positional arguments for formatting
            **kwargs: Keyword arguments
        """
        # Add exception flag
        if 'exception' not in kwargs:
            kwargs['exception'] = True
        self._log_with_context("ERROR", message, *args, **kwargs)
    
    def log(self, level: Union[str, int], message: str, *args, **kwargs) -> None:
        """Log a message at the specified level with bound context
        
        Args:
            level: Log level (name or number)
            message: Log message
            *args: Positional arguments for formatting
            **kwargs: Keyword arguments
        """
        self._log_with_context(level, message, *args, **kwargs)
    
    def contextualize(self, **kwargs) -> 'ContextManager':
        """Create a context manager for temporary context binding
        
        Note: This delegates to the parent logger's contextualize method.
        The bound context from this BoundLogger will still be applied
        to all logs within the context manager.
        
        Args:
            **kwargs: Key-value pairs to add as temporary context
            
        Returns:
            ContextManager instance for use in with statement
            
        Example:
            >>> bound = logger.bind(user_id=123)
            >>> with bound.contextualize(request_id="REQ-456"):
            ...     bound.info("Processing")
            # Log includes both user_id and request_id
        """
        from .context_manager import ContextManager
        return ContextManager(self._parent, **kwargs)
    
    def __repr__(self) -> str:
        """String representation"""
        bound_keys = ', '.join(self._bound_extra.keys())
        return f"BoundLogger(bound=[{bound_keys}])"

