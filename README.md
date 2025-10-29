# MyLogger

A production-ready, Loguru-inspired logging library built with Python standard library only.

## 🚀 Quick Start

```python
from mylogger import logger

# Basic logging
logger.info("Hello, World!")
logger.success("Operation completed successfully")
logger.error("Something went wrong")

# Message formatting with positional arguments
logger.info("User {} logged in", "John")

# Message formatting with named arguments
logger.info("User {name} logged in from {city}", name="Alice", city="NYC")

# Extra context
logger.info("Request processed", user_id=123, duration_ms=45)

# Log at specific level
logger.log("WARNING", "This is a warning")
logger.log(40, "This is an error (level 40)")
```

## ✨ Features (Day 4 - Complete)

- ✅ **Simple, intuitive API** - Loguru-inspired interface
- ✅ **Multiple log levels** - TRACE, DEBUG, INFO, SUCCESS, WARNING, ERROR, CRITICAL
- ✅ **Flexible formatting** - Positional, named, and mixed argument formatting
- ✅ **Automatic context** - Captures file, function, line, process, thread info
- ✅ **Extra context** - Add custom fields via kwargs
- ✅ **Thread-safe** - Safe for multi-threaded applications
- ✅ **Exception handling** - Graceful error handling
- ✅ **Zero dependencies** - Python standard library only

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
logger.info("User {} from {city}", "Alice", city="New York")
```

### Extra Context

```python
# Add custom fields for structured logging
logger.info("User action",
            user_id=123,
            action="login",
            ip_address="192.168.1.1",
            session_id="abc-123")

logger.error("Database query failed",
             query="SELECT * FROM users",
             error_code=500,
             retry_count=3)
```

### Exception Logging

```python
try:
    result = 1 / 0
except ZeroDivisionError as e:
    logger.error("Division failed", exception=e)
```

## 🔧 Current Status

**Day 4 Complete**: Basic Logger Implementation ✅

The logger is fully functional with:

- All logging methods working
- Message formatting (positional, named, mixed)
- Automatic caller context capture
- Exception handling
- Extra context support

**Coming Next**:

- **Day 5**: Handler Management (file, console, callable handlers)
- **Day 6**: Formatter with color support
- **Day 7-8**: File and Stream handlers
- **Day 9**: Colorizer for beautiful console output
- **Day 11**: File rotation
- **Day 13**: Exception formatting with diagnosis
- **Day 14**: Context binding

## 📁 Project Structure

```
mylogger/
├── mylogger/
│   ├── __init__.py       # Public API
│   ├── logger.py         # Main Logger class
│   ├── record.py         # LogRecord and data structures
│   ├── level.py          # Log level definitions
│   ├── utils.py          # FrameInspector, TimeUtils
│   ├── constants.py      # Constants and defaults
│   ├── exceptions.py     # Custom exceptions
│   ├── handler.py        # Handler base class (Day 5)
│   └── formatter.py      # Formatter class (Day 6)
├── tests/
│   ├── test_basic_logger.py
│   └── ...
├── examples/
│   ├── basic_usage_day4.py
│   └── ...
└── docs/
    ├── logger_action_plan.md
    ├── logger_quick_checklist.md
    └── DAY_4_SUMMARY.md
```

## 🧪 Running Tests

```bash
# Run basic logger tests
python tests/test_basic_logger.py

# Run example
python examples/basic_usage_day4.py
```

## 📝 Current Output Format

Logs are currently output to stderr with basic formatting:

```
[LEVEL] message (filename:function:line)
```

Example output:

```
[INFO] User John logged in (main.py:process_user:42)
[ERROR] Database connection failed (db.py:connect:15)
[SUCCESS] File saved successfully (storage.py:save_file:89)
```

Full formatting with colors will be implemented in Days 6 & 9.

## 🎯 Design Principles

1. **Simple API** - Easy to use, hard to misuse
2. **Zero dependencies** - Standard library only
3. **Production-ready** - Thread-safe, well-tested
4. **Loguru-inspired** - Familiar to Loguru users
5. **Educational** - Clear code structure for learning

## 📚 Documentation

- [Day 4 Summary](docs/DAY_4_SUMMARY.md) - Detailed implementation notes
- [Action Plan](docs/logger_action_plan.md) - Full development roadmap
- [Quick Checklist](docs/logger_quick_checklist.md) - Feature checklist

## 🤝 Contributing

This is an educational project following a structured development plan. Each day implements specific features as outlined in the action plan.

## 📄 License

MIT License - Feel free to use and modify

## 🎓 Learning Resources

This project demonstrates:

- Frame inspection and stack manipulation
- Structured logging design patterns
- Thread-safe Python programming
- Test-driven development
- Clean code architecture

---

**Status**: Day 4 Complete ✅  
**Next Milestone**: Day 5 - Handler Management  
**Version**: 0.1.0
