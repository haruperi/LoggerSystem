# MyLogger User Guide

Complete guide to using MyLogger in your applications.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Basic Usage](#basic-usage)
3. [Advanced Features](#advanced-features)
4. [Configuration Guide](#configuration-guide)
5. [Performance Tips](#performance-tips)
6. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Installation

MyLogger uses only the Python standard library - no dependencies needed!

```bash
# Clone or copy the mylogger package to your project
git clone <repository-url>
# Or simply use the package directly
```

### First Steps

```python
from mylogger import logger

# That's it! Start logging immediately.
# The logger comes pre-configured with production-ready defaults:
# - File: logs/app.log
# - Level: DEBUG
# - Rotation: 100 MB
# - Compression: gzip
# - Retention: 30 days

logger.info("Application started")
logger.success("Operation completed")
logger.error("Something went wrong")
```

**Default Configuration:**
The global `logger` instance automatically includes three production-ready handlers:

1. **Console Handler** (stderr):

   - ✅ INFO level and above
   - ✅ Colored output with timestamps
   - ✅ Format: `<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>`

2. **App Log File** (`logs/app.log`):

   - ✅ DEBUG level (captures all logs)
   - ✅ Detailed format with file/function/line info
   - ✅ Daily rotation
   - ✅ Gzip compression
   - ✅ 30-day retention

3. **Error Log File** (`logs/errors.log`):
   - ✅ ERROR and CRITICAL only
   - ✅ Rotates at 100 MB
   - ✅ Gzip compression
   - ✅ 90-day retention

You can customize or remove handlers as needed:

```python
# Remove all default handlers if you want custom configuration
logger.remove()

# Add custom handlers
logger.add("custom.log", level="INFO")
```

---

## Basic Usage

### Logging Methods

MyLogger provides convenient methods for each log level:

```python
logger.trace("Very detailed debugging")
logger.debug("Debug information")
logger.info("General information")
logger.success("Success message")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical error")
```

### Message Formatting

#### Positional Arguments

```python
logger.info("Processing {} items", 100)
logger.info("User {} logged in from {}", "John", "192.168.1.1")
```

#### Named Arguments

```python
logger.info("Hello, {name}!", name="World")
logger.info("Order #{id} total: ${amount:.2f}", id=12345, amount=99.99)
logger.info("User {name} from {city}", name="Alice", city="NYC")
```

#### Mixed Arguments

```python
logger.info("User {} from {city}", "John", city="NYC")
logger.info("Processing {} items for {user}", 10, user="admin")
```

### Adding Context

Add extra context fields that appear in formatted output:

```python
# Add context in the log call
logger.info("User action", user_id=123, action="login", ip="192.168.1.1")

# Global context (applies to all logs)
logger.extra['app_version'] = '1.2.3'
logger.info("Application started")  # Automatically includes app_version
```

### Exception Logging

```python
try:
    result = 1 / 0
except ZeroDivisionError as e:
    logger.error("Division failed", exception=e)
```

---

## Advanced Features

### Handlers

Handlers determine where log records are sent.

#### Console Output (StreamHandler)

```python
import sys
from mylogger import logger

# Default: stderr with automatic formatting
logger.add(sys.stderr, level="INFO")

# Custom format
logger.add(sys.stdout, level="DEBUG", format="{time:HH:mm:ss} | {level} | {message}")
```

#### File Output (FileHandler)

```python
# Simple file logging
logger.add("app.log", level="DEBUG")

# With custom format
logger.add("app.log",
          level="INFO",
          format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}")

# Append vs write mode
logger.add("app.log", mode="a")  # Append (default)
logger.add("app.log", mode="w")  # Overwrite
```

#### Custom Handler (CallableHandler)

```python
def send_to_api(message):
    # Send to external logging service
    requests.post("https://api.logs.com/entries", data=message)

# Pass formatted messages
logger.add(send_to_api, level="ERROR")

# Pass JSON serialized records
logger.add(send_to_api, level="ERROR", serialize=True)
```

### File Rotation

Automatically rotate log files when they get too large or after a time interval.

#### Size-Based Rotation

```python
from mylogger import logger

# Rotate at 10 MB
logger.add("app.log", rotation="10 MB")

# Using bytes
logger.add("app.log", rotation=1024 * 1024)  # 1 MB
```

#### Time-Based Rotation

```python
# Daily rotation at midnight
logger.add("app.log", rotation="daily")

# Hourly rotation
logger.add("app.log", rotation="1 hour")

# Every 30 minutes
logger.add("app.log", rotation="30 minutes")

# Specific time each day
logger.add("app.log", rotation="00:00")  # Midnight
logger.add("app.log", rotation="12:30")  # 12:30 PM
```

### Compression

Automatically compress rotated log files.

```python
# Gzip compression (default)
logger.add("app.log", rotation="100 MB", compression="gz")

# Zip compression
logger.add("app.log", rotation="100 MB", compression="zip")
```

### Retention

Automatically clean up old log files.

```python
# Keep only 10 most recent files
logger.add("app.log", rotation="100 MB", retention=10)

# Keep files for 7 days
logger.add("app.log", rotation="daily", retention="7 days")

# Keep files under 1 GB total
logger.add("app.log", rotation="100 MB", retention="1 GB")

# Multiple policies (most restrictive applies)
logger.add("app.log",
          rotation="100 MB",
          retention=Retention(count=10, age="30 days", size="500 MB"))
```

### Context Binding

Bind extra context to specific logger instances.

```python
# Create a bound logger for a request
request_logger = logger.bind(request_id="123", user="alice")

request_logger.info("Processing request")  # Includes request_id and user
request_logger.error("Validation failed")  # Still includes context

# Chaining
api_logger = logger.bind(api_version="v2").bind(endpoint="/users")
api_logger.info("API call")  # Includes both api_version and endpoint
```

### Context Managers

Temporarily add context for a code block.

```python
# Context applies to all logs in the block
with logger.contextualize(user="admin", operation="backup"):
    logger.info("Starting backup")
    logger.info("Backup in progress")
    logger.info("Backup completed")
# Context removed after block

# Nested contexts
with logger.contextualize(module="database"):
    logger.info("DB operation")
    with logger.contextualize(query="SELECT * FROM users"):
        logger.debug("Executing query")
        # Includes both module and query
```

### Exception Catching Decorator

Automatically catch and log exceptions.

```python
@logger.catch()
def risky_function():
    return 1 / 0  # Exception caught and logged automatically

# Catch specific exceptions
@logger.catch(ValueError)
def validate(value):
    if value < 0:
        raise ValueError("Negative value")

# Custom options
@logger.catch(level="WARNING", message="Validation failed", reraise=True)
def strict_validate(value):
    if value < 0:
        raise ValueError("Must be positive")
```

### Format Strings

Customize log record formatting.

**Basic Fields:**

```python
format="{time} | {level} | {message}"
format="{level: <8} | {message}"
format="{name}:{function}:{line} - {message}"
```

**Nested Fields:**

```python
format="{time:YYYY-MM-DD} | {level.name} | {process.id} | {message}"
format="User {extra.user_id} - {message}"
```

**Colors:**

```python
format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | {message}"
format="<red>ERROR</red> | <yellow>WARNING</yellow>"
```

**Time Formatting:**

```python
format="{time:YYYY-MM-DD HH:mm:ss}"  # 2024-01-15 14:30:45
format="{time:HH:mm:ss.SSS}"         # 14:30:45.123
```

### Filters

Filter which records get logged.

```python
# Custom filter function
def only_errors(record):
    return record.level.no >= 40

logger.add("errors.log", level="DEBUG", filter=only_errors)

# Filter by extra fields
def admin_only(record):
    return record.extra.get('user') == 'admin'

logger.add("admin.log", filter=admin_only)

# Built-in filters
from mylogger.filter import LevelFilter, ModuleFilter

# Only log WARNING and above
logger.add("warnings.log", filter=LevelFilter(min_level="WARNING"))

# Exclude specific modules
logger.add("app.log", filter=ModuleFilter(exclude=["requests", "urllib3"]))
```

### Multiple Handlers

Send logs to multiple destinations.

```python
# Console
logger.add(sys.stderr, level="INFO")

# File
logger.add("app.log", level="DEBUG")

# Errors to separate file
logger.add("errors.log", level="ERROR")

# API endpoint for critical errors
logger.add(send_to_api, level="CRITICAL", serialize=True)
```

### Async Logging

Use async handlers for non-blocking logging.

```python
# Enqueue log records in background thread
logger.add("app.log", level="INFO", enqueue=True)

# Custom queue size
logger.add("app.log", level="INFO", enqueue=True, max_queue_size=1000)
```

---

## Configuration Guide

### Environment Variables

Control logger behavior via environment variables:

```bash
# Disable colors
export NO_COLOR=1

# Set default log level
export MYLOGGER_LEVEL=DEBUG
```

### Global Logger Configuration

```python
from mylogger import logger

# Set global extra context
logger.extra['app_name'] = 'MyApp'
logger.extra['version'] = '1.0.0'

# Disable specific modules
logger.disable("requests")

# Enable modules
logger.enable("requests")

# Add custom level
logger.add_level("NOTICE", 35, color="blue", icon="ℹ")
logger.notice("Custom level message")
```

### Production Configuration

Recommended production setup:

```python
from mylogger import logger
import sys

# Console: INFO and above, colored
logger.add(
    sys.stderr,
    level="INFO",
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
           "<level>{level: <8}</level> | "
           "<cyan>{name}</cyan> | {message}",
    colorize=True
)

# File: All levels, rotated daily, compressed, retained 30 days
logger.add(
    "logs/app.log",
    level="DEBUG",
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | "
           "{name}:{function}:{line} | {message}",
    rotation="daily",
    compression="gz",
    retention="30 days",
    colorize=False  # No colors in files
)

# Error file: Only errors, retained 90 days
logger.add(
    "logs/errors.log",
    level="ERROR",
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | "
           "{name}:{function}:{line} | {message} | "
           "Process: {process.id} | Thread: {thread.id}",
    rotation="100 MB",
    compression="gz",
    retention="90 days"
)
```

---

## Performance Tips

### 1. Use Appropriate Log Levels

Don't log at DEBUG in production:

```python
# Development
logger.add(sys.stderr, level="DEBUG")

# Production
logger.add(sys.stderr, level="INFO")
```

### 2. Use Async for High-Throughput

If logging many records:

```python
logger.add("high_volume.log", level="INFO", enqueue=True)
```

### 3. Filter Out Unnecessary Logs

```python
# Only log errors to expensive handler
logger.add(send_to_api, level="ERROR", serialize=True)
```

### 4. Avoid Complex Formatting

Simple formats are faster:

```python
# Faster
logger.add("app.log", format="{level} | {message}")

# Slower (but more informative)
logger.add("app.log", format="{time:YYYY-MM-DD HH:mm:ss.SSS} | "
                             "{level: <8} | {name}:{function}:{line} | {message}")
```

### 5. Use File Rotation Wisely

Too frequent rotation causes overhead:

```python
# Good: Rotate at reasonable size
logger.add("app.log", rotation="100 MB")

# Avoid: Too small
logger.add("app.log", rotation="1 MB")  # Too many rotations
```

---

## Troubleshooting

### Logs Not Appearing

**Problem:** Logs aren't showing up.

**Solutions:**

1. Check handler level threshold:

   ```python
   logger.add(sys.stderr, level="INFO")  # Only INFO and above
   logger.debug("This won't appear")  # Below threshold
   ```

2. Check if handlers are added:

   ```python
   print(f"Handlers: {len(logger.handlers)}")
   ```

3. Check disabled modules:
   ```python
   logger.enable("your_module")  # Re-enable if disabled
   ```

### Colors Not Working

**Problem:** No colors in console output.

**Solutions:**

1. Check TTY:

   ```python
   logger.add(sys.stderr, colorize=True)  # Force colors
   ```

2. Check NO_COLOR environment variable:
   ```bash
   unset NO_COLOR
   ```

### File Not Created

**Problem:** Log file not being created.

**Solutions:**

1. Check permissions:

   ```python
   # Ensure directory exists and is writable
   logger.add("logs/app.log")  # Creates directory if needed
   ```

2. Check file mode:
   ```python
   logger.add("app.log", mode="w")  # Overwrite existing
   ```

### Rotation Not Working

**Problem:** Files not rotating.

**Solutions:**

1. Check rotation size:

   ```python
   # Ensure file reaches rotation size
   logger.add("app.log", rotation="1 MB")  # Small for testing
   ```

2. Check time rotation:
   ```python
   # Use specific time
   logger.add("app.log", rotation="00:00")  # Midnight
   ```

### Exception Formatting Not Showing

**Problem:** Exceptions not formatted nicely.

**Solutions:**

1. Enable diagnose mode:

   ```python
   logger.add(sys.stderr, diagnose=True)
   ```

2. Check backtrace:
   ```python
   logger.add(sys.stderr, backtrace=True)
   ```

### Performance Issues

**Problem:** Logging is slow.

**Solutions:**

1. Use async handlers:

   ```python
   logger.add("app.log", enqueue=True)
   ```

2. Reduce log level:

   ```python
   logger.add("app.log", level="WARNING")  # Less filtering
   ```

3. Simplify format:
   ```python
   logger.add("app.log", format="{message}")  # Simple format
   ```

---

## Examples

See the `examples/` directory for complete examples:

- `basic_usage.py` - Basic logging
- `file_rotation_usage.py` - File rotation
- `context_binding_usage.py` - Context binding
- `exception_formatting_usage.py` - Exception formatting
- `callable_handler_usage.py` - Custom handlers
- `multi_handler.py` - Multiple handlers

---

**Next Steps:**

- [API Reference](api.md) - Complete API documentation
- [Quick Start](quickstart.md) - Minimal setup guide
