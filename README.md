# MyLogger

A production-ready, Loguru-inspired logging library for Python. Built with **zero dependencies** - Python standard library only!

## ✨ Features

### Core Features

- ✅ **Simple, intuitive API** - Loguru-inspired interface that's easy to learn
- ✅ **Multiple log levels** - TRACE, DEBUG, INFO, SUCCESS, WARNING, ERROR, CRITICAL
- ✅ **Flexible message formatting** - Positional, named, and mixed argument formatting
- ✅ **Automatic context capture** - Captures file, function, line, process, thread info automatically
- ✅ **Extra context** - Add custom fields via kwargs for structured logging
- ✅ **Thread-safe** - Safe for multi-threaded applications
- ✅ **Exception handling** - Beautiful exception formatting with diagnosis

### Advanced Features

- ✅ **Multiple handlers** - Console, file, and custom handlers simultaneously
- ✅ **File rotation** - Size-based and time-based rotation
- ✅ **Compression** - Automatic gzip/zip compression of rotated logs
- ✅ **Retention** - Automated cleanup by count, age, or size
- ✅ **Context binding** - Bind extra context to logger instances
- ✅ **Exception decorator** - Auto-catch exceptions with `@logger.catch()`
- ✅ **Filters** - Filter logs by level, module, or custom logic
- ✅ **Custom formatters** - Flexible format strings with colors
- ✅ **Async logging** - Non-blocking logging with background queues
- ✅ **Structured logging** - JSON serialization support

### Zero Dependencies

- ✅ **Standard library only** - No external dependencies
- ✅ **Works everywhere** - Python 3.8+
- ✅ **Lightweight** - Minimal overhead

## 🚀 Quick Start

### Installation

No installation needed! Just use the package directly:

```python
from mylogger import logger

# Start logging immediately!
# The logger comes pre-configured with production-ready handlers:
# - Console output (INFO+, colored)
# - All logs to logs/app.log (DEBUG+, daily rotation, 30-day retention)
# - Errors to logs/errors.log (ERROR+, 90-day retention)
logger.info("Hello, World!")
```

The global `logger` instance is automatically configured with three production-ready handlers:

**Console Handler:**

- ✅ INFO level and above
- ✅ Colored output with timestamps and location info
- ✅ Format: Shows time, level, module:function:line, and message

**App Log File:**

- ✅ All levels (DEBUG+)
- ✅ Detailed format with file/function/line
- ✅ Daily rotation
- ✅ Gzip compression
- ✅ 30-day retention

**Error Log File:**

- ✅ ERROR and CRITICAL only
- ✅ Rotates at 100 MB
- ✅ Gzip compression
- ✅ 90-day retention

Or clone and use:

```bash
git clone <repository-url>
cd mylogger
```

### Basic Usage

```python
from mylogger import logger
import sys

# Add a console handler
logger.add(sys.stderr, level="INFO")

# Log messages
logger.info("Application started")
logger.success("Operation completed successfully")
logger.warning("This is a warning")
logger.error("Something went wrong")

# Message formatting
logger.info("User {} logged in", "John")
logger.info("User {name} from {city}", name="Alice", city="NYC")

# Extra context
logger.info("Request processed", user_id=123, duration_ms=45)
```

### File Logging with Rotation

```python
# Rotate at 100 MB, compress, keep 30 days
logger.add(
    "app.log",
    level="DEBUG",
    rotation="100 MB",
    compression="gz",
    retention="30 days"
)
```

## 📋 Log Levels

| Level    | Numeric Value | Usage                   |
| -------- | ------------- | ----------------------- |
| TRACE    | 5             | Very detailed debugging |
| DEBUG    | 10            | Debugging information   |
| INFO     | 20            | General information     |
| SUCCESS  | 25            | Success messages        |
| WARNING  | 30            | Warning messages        |
| ERROR    | 40            | Error messages          |
| CRITICAL | 50            | Critical errors         |

## 📖 Examples

### Basic Logging

```python
from mylogger import logger

logger.trace("Entering function")
logger.debug("Variable value: x=42")
logger.info("Server started on port 8080")
logger.success("User registration completed")
logger.warning("Cache is 80% full")
logger.error("Failed to connect to database")
logger.critical("System out of memory!")
```

### Message Formatting

```python
# Positional arguments
logger.info("Processing {} items", 100)
logger.info("User {} logged in from {}", "John", "192.168.1.1")

# Named arguments
logger.info("Hello, {name}!", name="World")
logger.info("Order #{id} total: ${amount:.2f}", id=12345, amount=99.99)

# Mixed arguments
logger.info("User {} from {city}", "John", city="NYC")
```

### Context Binding

```python
# Bind context for a request
request_logger = logger.bind(request_id="123", user="alice")
request_logger.info("Processing request")  # Includes request_id and user

# Context managers
with logger.contextualize(user="admin"):
    logger.info("Admin operation")
```

### Exception Handling

```python
# Auto-catch exceptions
@logger.catch()
def risky_function():
    return 1 / 0  # Exception automatically logged

# Manual exception logging
try:
    result = 1 / 0
except ZeroDivisionError as e:
    logger.error("Division failed", exception=e)
```

### File Rotation

```python
# Size-based rotation
logger.add("app.log", rotation="100 MB")

# Time-based rotation
logger.add("app.log", rotation="daily")
logger.add("app.log", rotation="1 hour")
logger.add("app.log", rotation="00:00")  # Midnight

# With compression and retention
logger.add(
    "app.log",
    rotation="100 MB",
    compression="gz",
    retention="30 days"
)
```

### Multiple Handlers

```python
# Console
logger.add(sys.stderr, level="INFO")

# File with all logs
logger.add("app.log", level="DEBUG")

# Errors to separate file
logger.add("errors.log", level="ERROR")

# Custom handler (send to API)
def send_to_api(message):
    requests.post("https://api.example.com/logs", data=message)

logger.add(send_to_api, level="CRITICAL", serialize=True)
```

### Custom Formatting

```python
# Simple format
logger.add(sys.stderr, format="{time:HH:mm:ss} | {level} | {message}")

# Detailed format with colors
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
           "<level>{level: <8}</level> | "
           "<cyan>{name}</cyan>:<cyan>{function}</cyan> - "
           "<level>{message}</level>"
)
```

See the [`examples/`](examples/) directory for more complete examples.

## 📚 Documentation

- **[Quick Start Guide](docs/quickstart.md)** - Get started in minutes
- **[User Guide](docs/user_guide.md)** - Complete usage guide
- **[API Reference](docs/api.md)** - Full API documentation
- **[Test Coverage](docs/TEST_COVERAGE_SUMMARY.md)** - Test status and coverage

## 🧪 Testing

Run the test suite:

```bash
pytest tests/ -v
```

**Test Status:** ✅ 405 tests passing

## 🏗️ Project Structure

```
mylogger/
├── mylogger/              # Main package
│   ├── __init__.py        # Public API
│   ├── logger.py          # Logger class
│   ├── handler.py          # Handlers (Stream, File, Callable)
│   ├── formatter.py       # Formatter and Colorizer
│   ├── record.py          # LogRecord and info classes
│   ├── level.py           # Log level definitions
│   ├── rotation.py        # File rotation
│   ├── compression.py     # File compression
│   ├── retention.py       # File retention
│   ├── exception_formatter.py  # Exception formatting
│   ├── bound_logger.py    # BoundLogger for context
│   ├── async_handler.py   # Async handler wrapper
│   └── ...
├── tests/                 # Test suite
├── examples/              # Usage examples
└── docs/                  # Documentation
```

## 🎯 Design Principles

1. **Simple API** - Easy to use, hard to misuse
2. **Zero Dependencies** - Standard library only
3. **Production-Ready** - Thread-safe, well-tested, robust error handling
4. **Loguru-Inspired** - Familiar to Loguru users
5. **Educational** - Clear code structure for learning

## 🚀 Production Configuration

Recommended setup for production:

```python
from mylogger import logger
import sys

# Console: INFO and above, colored
logger.add(
    sys.stderr,
    level="INFO",
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
           "<level>{level: <8}</level> | {message}",
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
    colorize=False
)

# Error file: Only errors, retained 90 days
logger.add(
    "logs/errors.log",
    level="ERROR",
    rotation="100 MB",
    compression="gz",
    retention="90 days"
)
```

## 📊 Performance

- **Fast** - Minimal overhead per log call
- **Async Support** - Non-blocking logging for high-throughput scenarios
- **Efficient** - Smart filtering and formatting

## 🔒 Thread Safety

All logger operations are thread-safe:

- Handler registration/removal
- Log record creation and formatting
- File writes

## 🐛 Error Handling

MyLogger never breaks your application:

- Handler errors are caught and logged to stderr
- Formatting errors have fallbacks
- Invalid operations raise clear exceptions

## 🤝 Contributing

This is an educational project demonstrating:

- Frame inspection and stack manipulation
- Structured logging design patterns
- Thread-safe Python programming
- Test-driven development
- Clean code architecture

## 📄 License

MIT License - Feel free to use and modify

## 🙏 Acknowledgments

Inspired by [Loguru](https://github.com/Delgan/loguru) - a fantastic logging library. MyLogger provides a similar API while being dependency-free.

## 📈 Status

**Current Status:** ✅ Complete and Production-Ready

All planned features from the action plan have been implemented:

- ✅ Core logging (Days 1-6)
- ✅ Handlers (Days 7-10)
- ✅ Advanced features (Days 11-17)
- ✅ Comprehensive tests (Days 18-19)
- ✅ Documentation (Day 20)

**Version:** 0.1.0

---

**Ready to use in production!** 🎉

For more information, see the [documentation](docs/) directory.
