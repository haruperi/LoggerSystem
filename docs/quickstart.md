# Quick Start Guide

Get up and running with MyLogger in 5 minutes!

## Installation

No pip install needed! MyLogger is a single package with zero dependencies.

### Option 1: Direct Use

Simply copy the `mylogger` package to your project:

```python
from mylogger import logger
```

### Option 2: Clone Repository

```bash
git clone <repository-url>
cd mylogger
```

## First Steps

### 1. Basic Logging

```python
from mylogger import logger

# That's it! The logger is pre-configured with a file handler.
# Logs automatically go to logs/app.log with rotation, compression, and retention.

logger.info("Application started")
logger.success("Operation completed")
logger.error("Something went wrong")
```

**Default Configuration:**
The global `logger` comes with three production-ready handlers pre-configured:

1. **Console Handler** (stderr):

   - Level: INFO and above
   - Colored output with timestamps
   - Includes location info: module:function:line

2. **App Log File** (`logs/app.log`):

   - Level: DEBUG (all messages)
   - Detailed format with file/function/line info
   - Daily rotation
   - Gzip compression
   - 30-day retention

3. **Error Log File** (`logs/errors.log`):
   - Level: ERROR and CRITICAL only
   - Rotates at 100 MB
   - Gzip compression
   - 90-day retention

You can customize or remove handlers as needed:

```python
# Remove all default handlers
logger.remove()

# Or remove specific handlers by ID
handler_id = logger.add("custom.log")
logger.remove(handler_id)
```

### 2. Message Formatting

```python
# Positional arguments
logger.info("Processing {} items", 100)

# Named arguments
logger.info("User {name} logged in", name="John")

# Extra context
logger.info("Request processed", user_id=123, duration_ms=45)
```

### 3. File Logging

```python
# Simple file logging
logger.add("app.log", level="DEBUG")

# With rotation
logger.add("app.log", rotation="100 MB")
```

That's it! You're ready to go.

## Common Patterns

### Console + File

```python
from mylogger import logger
import sys

# Console: INFO and above
logger.add(sys.stderr, level="INFO")

# File: All levels
logger.add("app.log", level="DEBUG")
```

### Production Setup

```python
from mylogger import logger
import sys

# Console
logger.add(sys.stderr, level="INFO")

# Rotated log files
logger.add(
    "logs/app.log",
    level="DEBUG",
    rotation="100 MB",
    compression="gz",
    retention="30 days"
)
```

### Context Binding

```python
# Bind context for a request
request_logger = logger.bind(request_id="123")
request_logger.info("Processing")

# Or use context manager
with logger.contextualize(user="admin"):
    logger.info("Admin operation")
```

### Exception Catching

```python
@logger.catch()
def risky_function():
    return 1 / 0  # Automatically logged
```

## Next Steps

- **[User Guide](user_guide.md)** - Complete usage guide
- **[API Reference](api.md)** - Full API documentation
- **[Examples](../examples/)** - Complete examples

---

**That's all you need to get started!** 🚀
