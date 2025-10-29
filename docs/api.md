# API Reference

Complete API documentation for MyLogger.

## Table of Contents

- [Logger](#logger)
- [Handlers](#handlers)
- [Formatter](#formatter)
- [Data Structures](#data-structures)
- [Exceptions](#exceptions)
- [Utilities](#utilities)

---

## Logger

The main logging interface. Typically imported as `logger` from `mylogger`.

### Class: `Logger`

Main logger class that manages handlers and creates log records.

#### Attributes

- `handlers: List[Handler]` - List of registered handlers
- `levels: Dict[str, Level]` - Dictionary mapping level names to Level objects
- `extra: Dict[str, Any]` - Global extra context data applied to all log calls
- `start_time: datetime` - Timestamp when logger was initialized

#### Methods

##### `add(sink, **options) -> int`

Add a handler to the logger.

**Parameters:**

- `sink` (Union[str, Path, TextIO, Callable]) - Output destination:
  - String or Path: File path (creates FileHandler)
  - TextIO (sys.stdout, sys.stderr, etc.): Stream (creates StreamHandler)
  - Callable: Function (creates CallableHandler)
- `level` (Union[str, int], optional) - Minimum log level (default: "INFO")
- `format` (str, optional) - Format string for log records
- `filter` (Callable[[LogRecord], bool], optional) - Filter function
- `colorize` (bool, optional) - Enable colorization (default: auto-detect)
- `serialize` (bool, optional) - Serialize records to JSON (default: False)
- `backtrace` (bool, optional) - Show full backtrace in exceptions (default: True)
- `diagnose` (bool, optional) - Show variable values in exceptions (default: False)
- `enqueue` (bool, optional) - Use async handler (default: False)
- `catch` (bool, optional) - Catch handler errors (default: True)
- `rotation` (Union[str, int, Rotation], optional) - File rotation strategy
- `compression` (Union[str, Compression], optional) - Compression format
- `retention` (Union[str, int, Retention], optional) - Retention policy
- `mode` (str, optional) - File mode: 'a' (append) or 'w' (write) (default: 'a')
- `encoding` (str, optional) - File encoding (default: 'utf-8')

**Returns:** `int` - Handler ID for removal

**Raises:** `InvalidLevelError` if level is invalid

**Example:**

```python
from mylogger import logger

# Console handler
logger.add(sys.stderr, level="INFO")

# File handler with rotation
logger.add("app.log", level="DEBUG", rotation="100 MB")

# Multiple handlers
logger.add(sys.stdout, level="INFO")
logger.add("errors.log", level="ERROR")
```

##### `remove(handler_id=None) -> None`

Remove a handler from the logger.

**Parameters:**

- `handler_id` (int, optional) - ID of handler to remove. If None, removes all handlers.

**Raises:** `HandlerNotFoundError` if handler_id doesn't exist

**Example:**

```python
# Remove specific handler
handler_id = logger.add("app.log")
logger.remove(handler_id)

# Remove all handlers
logger.remove()
```

##### `trace(message, *args, **kwargs) -> None`

Log a TRACE level message.

**Parameters:**

- `message` (str) - Log message (may contain format placeholders)
- `*args` - Positional arguments for formatting
- `**kwargs` - Keyword arguments for formatting or extra context

**Example:**

```python
logger.trace("Entering function")
logger.trace("Variable x = {}", 42)
logger.trace("Processing {item}", item="data", count=10)
```

##### `debug(message, *args, **kwargs) -> None`

Log a DEBUG level message.

##### `info(message, *args, **kwargs) -> None`

Log an INFO level message.

##### `success(message, *args, **kwargs) -> None`

Log a SUCCESS level message.

##### `warning(message, *args, **kwargs) -> None`

Log a WARNING level message.

##### `error(message, *args, **kwargs) -> None`

Log an ERROR level message.

**Example with exception:**

```python
try:
    risky_operation()
except Exception as e:
    logger.error("Operation failed", exception=e)
```

##### `critical(message, *args, **kwargs) -> None`

Log a CRITICAL level message.

##### `log(level, message, *args, **kwargs) -> None`

Log a message at the specified level.

**Parameters:**

- `level` (Union[str, int]) - Log level name (e.g., "INFO") or numeric value (e.g., 20)
- `message` (str) - Log message
- `*args` - Positional arguments for formatting
- `**kwargs` - Keyword arguments

**Example:**

```python
logger.log("INFO", "User logged in")
logger.log(40, "This is an error")  # ERROR level
```

##### `bind(**kwargs) -> BoundLogger`

Create a bound logger with extra context.

**Parameters:**

- `**kwargs` - Context fields to bind

**Returns:** `BoundLogger` - Logger instance with bound context

**Example:**

```python
bound = logger.bind(request_id="123", user="alice")
bound.info("Processing request")  # Automatically includes request_id and user
```

##### `contextualize(**kwargs) -> ContextManager`

Create a context manager for temporary context.

**Parameters:**

- `**kwargs` - Context fields

**Returns:** `ContextManager` - Context manager

**Example:**

```python
with logger.contextualize(user="admin"):
    logger.info("Admin operation")  # Includes user=admin
    logger.info("Another log")       # Still includes user=admin
# Context removed after exit
```

##### `opt(**options) -> OptLogger`

Create a logger with temporary options.

**Parameters:**

- `exception` (Union[bool, Exception], optional) - Include exception info
- `depth` (int, optional) - Adjust stack frame depth

**Returns:** `OptLogger` - Logger wrapper with options

**Example:**

```python
# Include current exception automatically
logger.opt(exception=True).error("Error occurred")

# Adjust frame depth
logger.opt(depth=1).info("Message")
```

##### `catch(exception=Exception, *, level="ERROR", message="An error occurred", reraise=False, onerror=None) -> Callable`

Decorator to catch exceptions and log them.

**Parameters:**

- `exception` (Type[Exception], optional) - Exception types to catch (default: Exception)
- `level` (str, optional) - Log level for exceptions (default: "ERROR")
- `message` (str, optional) - Custom log message (default: "An error occurred")
- `reraise` (bool, optional) - Re-raise exception after logging (default: False)
- `onerror` (Callable, optional) - Callback on error

**Returns:** `Callable` - Decorator function

**Example:**

```python
@logger.catch()
def risky_function():
    return 1 / 0

@logger.catch(ValueError, level="WARNING", reraise=True)
def validate_input(value):
    if value < 0:
        raise ValueError("Negative value")
```

##### `add_level(name, no, color="white", icon="•") -> None`

Add a custom log level.

**Parameters:**

- `name` (str) - Level name
- `no` (int) - Numeric level value
- `color` (str, optional) - ANSI color code
- `icon` (str, optional) - Level icon

**Example:**

```python
logger.add_level("NOTICE", 35, color="blue", icon="ℹ")
logger.notice("This is a notice")
```

##### `disable(name) -> None`

Disable logging for a module or logger.

**Parameters:**

- `name` (str) - Module or logger name

**Example:**

```python
logger.disable("requests")  # Disable logging from requests module
```

##### `enable(name) -> None`

Enable logging for a module or logger.

**Parameters:**

- `name` (str) - Module or logger name

**Example:**

```python
logger.enable("requests")  # Re-enable logging from requests module
```

---

## Handlers

Handlers process log records and send them to different destinations.

### Class: `Handler` (Abstract Base Class)

Base class for all handlers. Cannot be instantiated directly.

#### Attributes

- `id: int` - Unique handler identifier
- `sink: Any` - Output destination
- `level: Level` - Minimum log level
- `formatter: Formatter` - Formatter instance
- `filter_func: Optional[Callable]` - Filter function
- `colorize: bool` - Enable colorization
- `serialize: bool` - Serialize to JSON
- `backtrace: bool` - Show full backtrace
- `diagnose: bool` - Show variable values
- `enqueue: bool` - Use async processing
- `catch: bool` - Catch handler errors

#### Methods

##### `emit(record: LogRecord) -> None`

Process and output a log record. Must be implemented by subclasses.

##### `should_emit(record: LogRecord) -> bool`

Check if record should be emitted based on level and filter.

##### `format(record: LogRecord) -> str`

Format a log record using the formatter.

##### `close() -> None`

Close the handler and release resources.

---

### Class: `StreamHandler`

Handler for stream output (console, stdout, stderr).

**Initialization:**

```python
handler = StreamHandler(stream, level, formatter, **options)
```

**Parameters:**

- `stream` (TextIO) - Output stream (sys.stdout, sys.stderr, etc.)
- `level` (Level) - Minimum log level
- `formatter` (Formatter) - Formatter instance
- `**options` - Additional options

**Example:**

```python
from mylogger.handler import StreamHandler
from mylogger.formatter import Formatter
from mylogger import level as levels

formatter = Formatter("{level} | {message}")
handler = StreamHandler(sys.stdout, levels.INFO, formatter)
```

---

### Class: `FileHandler`

Handler for file output with rotation, compression, and retention support.

**Initialization:**

```python
handler = FileHandler(path, level, formatter, **options)
```

**Parameters:**

- `path` (Union[str, Path]) - File path
- `level` (Level) - Minimum log level
- `formatter` (Formatter) - Formatter instance
- `mode` (str, optional) - File mode: 'a' (append) or 'w' (write)
- `encoding` (str, optional) - File encoding
- `rotation` (Union[str, int, Rotation], optional) - Rotation strategy
- `compression` (Union[str, Compression], optional) - Compression format
- `retention` (Union[str, int, Retention], optional) - Retention policy

**Example:**

```python
from mylogger.handler import FileHandler
from mylogger.rotation import SizeRotation
from mylogger.compression import Compression

formatter = Formatter("{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}")
rotation = SizeRotation("100 MB")
compression = Compression("gz")

handler = FileHandler(
    "app.log",
    levels.INFO,
    formatter,
    rotation=rotation,
    compression=compression
)
```

---

### Class: `CallableHandler`

Handler that calls a function with formatted or serialized records.

**Initialization:**

```python
handler = CallableHandler(func, level, formatter, **options)
```

**Parameters:**

- `func` (Callable[[str], None]) - Function to call with formatted message
- `level` (Level) - Minimum log level
- `formatter` (Formatter) - Formatter instance (or Serializer if serialize=True)
- `serialize` (bool, optional) - Pass JSON string instead of formatted string

**Example:**

```python
def send_to_api(message):
    requests.post("https://api.example.com/logs", json=message)

handler = CallableHandler(send_to_api, levels.ERROR, formatter, serialize=True)
```

---

### Class: `AsyncHandler`

Wrapper handler that processes records asynchronously in a background thread.

**Initialization:**

```python
handler = AsyncHandler(wrapped_handler, max_queue_size=100)
```

**Parameters:**

- `wrapped_handler` (Handler) - Handler to wrap
- `max_queue_size` (int, optional) - Maximum queue size
- `queue_full_action` (str, optional) - Action when queue full: 'block', 'drop', 'raise'

---

## Formatter

### Class: `Formatter`

Formats log records into strings using format specifications.

**Initialization:**

```python
formatter = Formatter(format_string="{time:YYYY-MM-DD} | {level} | {message}")
```

**Format String Syntax:**

- `{field}` - Basic field access: `{message}`, `{level}`, `{time}`
- `{field.subfield}` - Nested access: `{level.name}`, `{process.id}`, `{extra.user_id}`
- `{field:spec}` - Format specifications: `{level:<8}`, `{time:YYYY-MM-DD}`
- `<color>text</color>` - Color tags: `<red>Error</red>`, `<level>{level}</level>`

**Available Fields:**

- `time` - Timestamp (datetime)
- `level` - Log level (Level object)
- `message` - Log message (str)
- `name` - Logger name (str)
- `module` - Module name (str)
- `function` - Function name (str)
- `line` - Line number (int)
- `file` - File information (FileInfo)
- `process` - Process information (ProcessInfo)
- `thread` - Thread information (ThreadInfo)
- `elapsed` - Time elapsed since logger start (timedelta)
- `exception` - Exception information (ExceptionInfo)
- `extra` - Extra context dictionary

**Time Format Tokens:**

- `YYYY` - 4-digit year
- `MM` - 2-digit month
- `DD` - 2-digit day
- `HH` - 24-hour hour
- `mm` - Minutes
- `ss` - Seconds
- `SSS` - Milliseconds

**Example:**

```python
from mylogger.formatter import Formatter

# Simple format
formatter = Formatter("{level} | {message}")

# Detailed format with colors
formatter = Formatter(
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan> - "
    "<level>{message}</level>"
)
```

**Methods:**

##### `format(record: LogRecord) -> str`

Format a log record according to the format string.

##### `get_field_value(record: LogRecord, field_name: str) -> Any`

Get the value of a field from a log record.

---

## Data Structures

### Class: `LogRecord`

Contains all information about a log entry.

**Attributes:**

- `time: datetime` - Timestamp
- `level: Level` - Log level
- `message: str` - Log message
- `name: str` - Logger name
- `module: str` - Module name
- `function: str` - Function name
- `line: int` - Line number
- `file: FileInfo` - File information
- `process: ProcessInfo` - Process information
- `thread: ThreadInfo` - Thread information
- `elapsed: timedelta` - Time elapsed since logger start
- `exception: Optional[ExceptionInfo]` - Exception information
- `extra: Dict[str, Any]` - Extra context

**Methods:**

##### `to_dict() -> Dict[str, Any]`

Serialize the record to a dictionary.

---

### Class: `Level`

Represents a log level.

**Attributes:**

- `name: str` - Level name (e.g., "INFO")
- `no: int` - Numeric level (e.g., 20)
- `color: str` - ANSI color code
- `icon: str` - Level icon

**Predefined Levels:**

- `TRACE` (5)
- `DEBUG` (10)
- `INFO` (20)
- `SUCCESS` (25)
- `WARNING` (30)
- `ERROR` (40)
- `CRITICAL` (50)

---

### Class: `FileInfo`

File information dataclass.

**Attributes:**

- `name: str` - Filename
- `path: str` - Full file path
- `pathlib: Path` - Path object

---

### Class: `ProcessInfo`

Process information dataclass.

**Attributes:**

- `id: int` - Process ID
- `name: str` - Process name

---

### Class: `ThreadInfo`

Thread information dataclass.

**Attributes:**

- `id: int` - Thread ID
- `name: str` - Thread name

---

### Class: `ExceptionInfo`

Exception information dataclass.

**Attributes:**

- `type: Type[BaseException]` - Exception type
- `value: BaseException` - Exception instance
- `traceback: Optional[TracebackType]` - Traceback object

---

## Exceptions

### `LoggerError`

Base exception for all logger-related errors.

### `InvalidLevelError`

Raised when an invalid log level is used.

**Attributes:**

- `level` - The invalid level that was provided

### `HandlerNotFoundError`

Raised when trying to remove a non-existent handler.

**Attributes:**

- `handler_id` - The handler ID that was not found

### `RotationError`

Raised when file rotation fails.

### `FormatterError`

Raised when formatting fails.

### `CompressionError`

Raised when compression fails.

---

## Utilities

### File Rotation

#### Class: `SizeRotation`

Rotate files when they reach a certain size.

**Initialization:**

```python
from mylogger.rotation import SizeRotation

# Using integer bytes
rotation = SizeRotation(1024 * 1024)  # 1 MB

# Using size string
rotation = SizeRotation("10 MB")
rotation = SizeRotation("100 KB")
```

#### Class: `TimeRotation`

Rotate files based on time intervals.

**Initialization:**

```python
from mylogger.rotation import TimeRotation

# Daily rotation at midnight
rotation = TimeRotation("daily")

# Hourly rotation
rotation = TimeRotation("1 hour")

# Specific time
rotation = TimeRotation("00:00")  # Midnight
rotation = TimeRotation("12:30")  # 12:30 PM daily
```

---

### Compression

#### Class: `Compression`

Compress rotated log files.

**Initialization:**

```python
from mylogger.compression import Compression

# Gzip compression (default)
compression = Compression(format="gz")

# Zip compression
compression = Compression(format="zip")

# With options
compression = Compression(format="gz", compression_level=5, keep_original=False)
```

---

### Retention

#### Class: `Retention`

Manage log file retention policies.

**Initialization:**

```python
from mylogger.retention import Retention

# Keep 10 most recent files
retention = Retention(count=10)

# Keep files for 7 days
retention = Retention(age="7 days")

# Keep files under 1 GB total
retention = Retention(size="1 GB")

# Multiple policies
retention = Retention(count=10, age="30 days", size="500 MB")
```

---

## Module-Level Exports

The `mylogger` package exports:

```python
from mylogger import (
    logger,           # Global logger instance
    Logger,           # Logger class
    TRACE, DEBUG, INFO, SUCCESS, WARNING, ERROR, CRITICAL,  # Level constants
    LogRecord, Level, FileInfo, ProcessInfo, ThreadInfo, ExceptionInfo,  # Data structures
    InvalidLevelError, HandlerNotFoundError,  # Exceptions
    # ... etc
)
```

---

**See Also:**

- [User Guide](user_guide.md) - Detailed usage examples
- [Quick Start](quickstart.md) - Getting started guide
