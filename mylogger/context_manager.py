"""
Context manager for temporary context binding

This module provides the ContextManager class for use with Python's
`with` statement to temporarily add context to a logger.
"""

from typing import Any, Dict


class ContextManager:
    """Context manager for temporary context binding
    
    This class provides a context manager that temporarily modifies
    a logger's global extra dict. The changes are automatically
    reverted when exiting the context.
    
    This is useful for adding context that should apply to multiple
    log calls within a specific scope, without permanently modifying
    the logger.
    
    Example:
        >>> logger = Logger()
        >>> logger.info("Before context")
        >>> with logger.contextualize(request_id="REQ-123"):
        ...     logger.info("Inside context")  # Has request_id
        ...     logger.debug("More logging")  # Has request_id
        >>> logger.info("After context")  # No request_id
    
    Attributes:
        _logger: The Logger instance to modify
        _context: Dictionary of context to add
        _saved_extra: Saved state of logger.extra before modification
    """
    
    def __init__(self, logger: 'Logger', **context):
        """Initialize the context manager
        
        Args:
            logger: The Logger instance to modify
            **context: Key-value pairs to add as temporary context
        """
        self._logger = logger
        self._context: Dict[str, Any] = context
        self._saved_extra: Dict[str, Any] = {}
    
    def __enter__(self) -> 'Logger':
        """Enter the context - add temporary context to logger
        
        Returns:
            The logger instance (for convenience)
        """
        # Save current extra state
        self._saved_extra = self._logger.extra.copy()
        
        # Update logger's extra with context
        self._logger.extra.update(self._context)
        
        return self._logger
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit the context - restore previous logger state
        
        Args:
            exc_type: Exception type (if any)
            exc_val: Exception value (if any)
            exc_tb: Exception traceback (if any)
            
        Returns:
            None (exceptions are not suppressed)
        """
        # Restore previous extra state
        self._logger.extra = self._saved_extra
    
    def __repr__(self) -> str:
        """String representation"""
        context_keys = ', '.join(self._context.keys())
        return f"ContextManager(context=[{context_keys}])"

