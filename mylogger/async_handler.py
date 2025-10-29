"""
Async handler for non-blocking logging
"""

import queue
import threading
import atexit
import sys
from typing import Optional, Literal

from .handler import Handler
from .record import LogRecord


class AsyncHandler(Handler):
    """Asynchronous handler wrapper for non-blocking logging
    
    This handler wraps another handler and processes log records in a
    background thread using a queue. This prevents slow I/O operations
    (like file writes or network calls) from blocking the main thread.
    
    Attributes:
        wrapped_handler: The actual handler that processes records
        queue: Queue for passing records to worker thread
        worker_thread: Background thread that processes the queue
        max_queue_size: Maximum number of records in queue (0 = unlimited)
        overflow_strategy: How to handle full queue ('block', 'drop', or 'raise')
        _stop_flag: Event to signal worker thread to stop
        _stopped: Flag indicating if handler has been stopped
    """
    
    def __init__(
        self,
        wrapped_handler: Handler,
        max_queue_size: int = 0,
        overflow_strategy: Literal['block', 'drop', 'raise'] = 'block'
    ):
        """Initialize async handler
        
        Args:
            wrapped_handler: Handler to wrap (e.g., FileHandler, StreamHandler)
            max_queue_size: Maximum queue size (0 = unlimited, default)
            overflow_strategy: How to handle full queue:
                - 'block': Block until space available (default)
                - 'drop': Drop the record silently
                - 'raise': Raise queue.Full exception
        """
        # Initialize parent Handler with wrapped handler's attributes
        super().__init__(
            sink=wrapped_handler.sink,
            level=wrapped_handler.level,
            formatter=wrapped_handler.formatter,
            filter_func=wrapped_handler.filter_func,
            colorize=wrapped_handler.colorize,
            serialize=wrapped_handler.serialize,
            backtrace=wrapped_handler.backtrace,
            diagnose=wrapped_handler.diagnose,
            enqueue=True,  # This IS the async handler
            catch=wrapped_handler.catch
        )
        
        self.wrapped_handler = wrapped_handler
        self.max_queue_size = max_queue_size
        self.overflow_strategy = overflow_strategy
        
        # Create queue and worker thread
        self.queue: queue.Queue = queue.Queue(maxsize=max_queue_size)
        self._stop_flag = threading.Event()
        self._stopped = False
        
        # Start worker thread
        self.worker_thread = threading.Thread(
            target=self._worker,
            name=f"AsyncHandler-Worker-{id(self)}",
            daemon=True
        )
        self.worker_thread.start()
        
        # Register cleanup on exit
        atexit.register(self._cleanup)
    
    def emit(self, record: LogRecord) -> None:
        """Add record to queue for async processing
        
        This method is non-blocking (unless overflow_strategy='block' and queue is full).
        
        Args:
            record: LogRecord to emit
        """
        if self._stopped:
            return
        
        if not self.should_emit(record):
            return
        
        try:
            if self.overflow_strategy == 'block':
                # Block until space available
                self.queue.put(record, block=True)
            elif self.overflow_strategy == 'drop':
                # Drop record if queue is full
                self.queue.put(record, block=False)
            elif self.overflow_strategy == 'raise':
                # Raise exception if queue is full
                self.queue.put(record, block=False)
            else:
                # Default to blocking
                self.queue.put(record, block=True)
        except queue.Full:
            if self.overflow_strategy == 'drop':
                # Silently drop the record
                pass
            elif self.overflow_strategy == 'raise':
                # Re-raise the exception
                raise
            else:
                # This shouldn't happen with 'block' strategy
                sys.stderr.write(f"AsyncHandler queue full, record dropped\n")
    
    def _worker(self) -> None:
        """Worker thread that processes the queue
        
        Runs continuously until stop flag is set, processing records from the queue
        and passing them to the wrapped handler.
        """
        while not self._stop_flag.is_set():
            try:
                # Get record from queue with timeout to check stop flag periodically
                try:
                    record = self.queue.get(timeout=0.1)
                except queue.Empty:
                    continue
                
                # Process the record with wrapped handler
                try:
                    self.wrapped_handler.emit(record)
                except Exception as e:
                    # Don't let handler errors stop the worker thread
                    if self.catch:
                        sys.stderr.write(f"Error in async handler worker: {e}\n")
                    else:
                        # In non-catch mode, still print error but continue
                        sys.stderr.write(f"Error in async handler worker: {e}\n")
                
                # Mark task as done
                self.queue.task_done()
                
            except Exception as e:
                # Catch any unexpected errors in worker loop
                sys.stderr.write(f"Unexpected error in async handler worker: {e}\n")
        
        # Process remaining items in queue before stopping
        self._flush_queue()
    
    def _flush_queue(self) -> None:
        """Flush remaining items in queue
        
        Processes all remaining records in the queue. Used during shutdown.
        """
        while True:
            try:
                record = self.queue.get_nowait()
                try:
                    self.wrapped_handler.emit(record)
                except Exception as e:
                    sys.stderr.write(f"Error flushing async queue: {e}\n")
                self.queue.task_done()
            except queue.Empty:
                break
    
    def close(self) -> None:
        """Close the async handler and wait for queue to empty
        
        Stops the worker thread, flushes the queue, and closes the wrapped handler.
        """
        if self._stopped:
            return
        
        self._stopped = True
        
        # Wait for queue to empty (with timeout)
        try:
            self.queue.join()
        except Exception:
            pass
        
        # Signal worker to stop
        self._stop_flag.set()
        
        # Wait for worker thread to finish (with timeout)
        if self.worker_thread.is_alive():
            self.worker_thread.join(timeout=5.0)
        
        # Close wrapped handler
        try:
            self.wrapped_handler.close()
        except Exception as e:
            sys.stderr.write(f"Error closing wrapped handler: {e}\n")
    
    def _cleanup(self) -> None:
        """Cleanup method called on program exit
        
        Ensures proper shutdown of async handler when program terminates.
        """
        self.close()
    
    def __repr__(self) -> str:
        """String representation of AsyncHandler"""
        return f"AsyncHandler(wrapped={self.wrapped_handler}, queue_size={self.queue.qsize()}/{self.max_queue_size or 'unlimited'})"

