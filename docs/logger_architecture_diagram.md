# Logger System - Simplified Architecture

## Component Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          USER APPLICATION                                │
│                                                                          │
│  from mylogger import logger                                            │
│                                                                          │
│  logger.info("Hello World")                                             │
│  logger.add("app.log", rotation="1 MB")                                 │
└──────────────────────────────────┬───────────────────────────────────────┘
                                   │
                                   │
┌──────────────────────────────────▼───────────────────────────────────────┐
│                            LOGGER (Core)                                 │
│                                                                          │
│  ┌────────────────┐  ┌──────────────┐  ┌─────────────────┐            │
│  │  Log Methods   │  │   Context    │  │   Decorators    │            │
│  │  • trace()     │  │   • bind()   │  │   • @catch      │            │
│  │  • debug()     │  │   • context  │  │   • @opt        │            │
│  │  • info()      │  │   • extra    │  │                 │            │
│  │  • success()   │  │              │  │                 │            │
│  │  • warning()   │  │              │  │                 │            │
│  │  • error()     │  │              │  │                 │            │
│  │  • critical()  │  │              │  │                 │            │
│  └────────────────┘  └──────────────┘  └─────────────────┘            │
│                                                                          │
│  Creates LogRecord → Calls Handlers → Returns                           │
└──────────────────────────────────┬───────────────────────────────────────┘
                                   │
                ┌──────────────────┼──────────────────┐
                │                  │                  │
                ▼                  ▼                  ▼
┌───────────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│   HANDLER #1          │ │   HANDLER #2     │ │   HANDLER #N     │
│                       │ │                  │ │                  │
│  ┌─────────────────┐ │ │ ┌──────────────┐ │ │ ┌──────────────┐ │
│  │   Filter        │ │ │ │   Filter     │ │ │ │   Filter     │ │
│  │   ✓ Level      │ │ │ │   ✓ Module   │ │ │ │   ✓ Custom   │ │
│  │   ✓ Module     │ │ │ │   ✓ Custom   │ │ │ │              │ │
│  └─────────────────┘ │ │ └──────────────┘ │ │ └──────────────┘ │
│          ↓            │ │        ↓         │ │        ↓         │
│  ┌─────────────────┐ │ │ ┌──────────────┐ │ │ ┌──────────────┐ │
│  │   Formatter     │ │ │ │  Formatter   │ │ │ │  Serializer  │ │
│  │   • Colorize    │ │ │ │  • Plain     │ │ │ │  • JSON      │ │
│  │   • Pattern     │ │ │ │  • Pattern   │ │ │ │              │ │
│  └─────────────────┘ │ │ └──────────────┘ │ │ └──────────────┘ │
│          ↓            │ │        ↓         │ │        ↓         │
│  ┌─────────────────┐ │ │ ┌──────────────┐ │ │ ┌──────────────┐ │
│  │   File Sink     │ │ │ │ Stream Sink  │ │ │ │ Custom Func  │ │
│  │   • app.log     │ │ │ │  • stderr    │ │ │ │ • Webhook    │ │
│  │   • Rotation    │ │ │ │              │ │ │ │ • Database   │ │
│  │   • Compress    │ │ │ │              │ │ │ │ • Email      │ │
│  │   • Retention   │ │ │ │              │ │ │ │              │ │
│  └─────────────────┘ │ │ └──────────────┘ │ │ └──────────────┘ │
└───────────────────────┘ └──────────────────┘ └──────────────────┘
```

---

## Data Flow Diagram

```
User Code
   │
   │ logger.info("User {name} logged in", name="John")
   │
   ▼
┌──────────────────────────────────────────────────┐
│ 1. Logger receives call                          │
│    • Inspect caller frame                        │
│    • Extract context (file, function, line)      │
└──────────────┬───────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────┐
│ 2. Create LogRecord                              │
│    • timestamp                                   │
│    • level (INFO)                                │
│    • message                                     │
│    • extra context                               │
│    • exception info (if any)                     │
│    • thread/process info                         │
└──────────────┬───────────────────────────────────┘
               │
               │ Pass to each handler
               │
    ┌──────────┼──────────┐
    │          │          │
    ▼          ▼          ▼
┌────────┐ ┌────────┐ ┌────────┐
│Handler1│ │Handler2│ │Handler3│
└───┬────┘ └───┬────┘ └───┬────┘
    │          │          │
    │ 3. Filter│          │
    │ ✓ Pass   │ ✗ Skip   │ ✓ Pass
    │          │          │
    ▼          │          ▼
┌────────┐    │      ┌────────┐
│Format  │    │      │Serialize
└───┬────┘    │      └───┬────┘
    │          │          │
    ▼          │          ▼
┌────────┐    │      ┌────────┐
│ Write  │    │      │ Send   │
│  to    │    │      │  to    │
│ File   │    │      │ Custom │
└────────┘    │      └────────┘
              │
           (Filtered out)
```

---

## Handler Lifecycle

```
Handler Added
      │
      ▼
┌─────────────────┐
│  Configuration  │
│  • Set sink     │
│  • Set level    │
│  • Set format   │
│  • Set rotation │
│  • Set filters  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐        ┌──────────────┐
│  Active State   │◄───────┤ Log Record   │
│  • Filter       │        │   Arrives    │
│  • Format       │        └──────────────┘
│  • Emit         │
│  • Rotate       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Closed State   │
│  • Flush buffer │
│  • Close file   │
│  • Cleanup      │
└─────────────────┘
```

---

## File Handler Detail

```
┌────────────────────────────────────────────┐
│          FileHandler                        │
├────────────────────────────────────────────┤
│                                            │
│  ┌──────────────────────────────────────┐ │
│  │         Write Operation              │ │
│  │                                      │ │
│  │  1. Check if rotation needed        │ │
│  │     • Size based?                   │ │
│  │     • Time based?                   │ │
│  │     • Custom callback?              │ │
│  │                                      │ │
│  │  2. If rotation needed:             │ │
│  │     • Close current file            │ │
│  │     • Rename with timestamp         │ │
│  │     • Compress old file (optional)  │ │
│  │     • Open new file                 │ │
│  │                                      │ │
│  │  3. Write formatted log             │ │
│  │                                      │ │
│  │  4. Check retention policy          │ │
│  │     • Delete old files by count     │ │
│  │     • Delete old files by age       │ │
│  │     • Delete old files by size      │ │
│  └──────────────────────────────────────┘ │
│                                            │
└────────────────────────────────────────────┘

File Structure:
app.log              ← Current log file
app.2024-01-01.log   ← Rotated
app.2024-01-02.log.gz ← Compressed
app.2024-01-03.log.gz
```

---

## Formatter Architecture

```
Format String:
"{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"

                    ↓

┌──────────────────────────────────────────────────┐
│           Formatter.parse_format_string()         │
│                                                  │
│  Tokenizes the format string into:              │
│  • Literal text                                 │
│  • Variable placeholders {name:format}          │
└──────────────┬───────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────┐
│            Formatter.format(record)               │
│                                                  │
│  For each token:                                │
│  • Literal → Output as is                       │
│  • Variable → Extract from record + apply format│
│  • Apply colors based on level                  │
└──────────────┬───────────────────────────────────┘
               │
               ▼
Final Output:
"2024-01-01 12:30:45 | INFO     | myapp:main:42 - User logged in"
```

---

## Exception Formatting

```
Exception Caught
       │
       ▼
┌─────────────────────────────────────┐
│   ExceptionFormatter                │
│                                     │
│   1. Format exception type & msg    │
│   2. For each frame in traceback:   │
│      • File path                    │
│      • Function name                │
│      • Line number                  │
│      • Source code (if diagnose)    │
│      • Local variables (if diagnose)│
│   3. Apply colors (if colorize)     │
│   4. Show full trace (if backtrace) │
└─────────────┬───────────────────────┘
              │
              ▼
Formatted Exception:
╭────────────────────────────────────╮
│ ValueError: Invalid input          │
│                                    │
│ File "app.py", line 42, in main    │
│   40 │ def main():                  │
│   41 │     value = "invalid"        │
│ ❱ 42 │     process(value)           │
│   43 │     return True              │
│                                    │
│ Local variables:                   │
│   value = "invalid"                │
╰────────────────────────────────────╯
```

---

## Thread Safety Model

```
┌─────────────────────────────────────┐
│        Main Thread                  │
│                                     │
│  logger.info("message") ───┐        │
│                            │        │
└────────────────────────────┼────────┘
                             │
                             ▼
                    ┌────────────────┐
                    │   Lock Queue   │
                    └────────┬───────┘
                             │
                   ┌─────────┴──────────┐
                   │                    │
                   ▼                    ▼
        ┌──────────────────┐  ┌──────────────────┐
        │   Sync Handler   │  │  Async Handler   │
        │   (with lock)    │  │  (enqueue=True)  │
        └────────┬─────────┘  └────────┬─────────┘
                 │                     │
                 │                     ▼
                 │            ┌────────────────┐
                 │            │  Worker Thread │
                 │            │  • Dequeue     │
                 │            │  • Process     │
                 │            │  • Write       │
                 │            └────────────────┘
                 │
                 ▼
          ┌─────────────┐
          │   Output    │
          └─────────────┘
```

---

## Context Binding Example

```
# Global logger
logger.info("Starting")
  ↓ message: "Starting"
  ↓ extra: {}

# Bound logger
request_logger = logger.bind(request_id="123", user="john")
  ↓ Creates BoundLogger with extra = {request_id: "123", user: "john"}

request_logger.info("Processing")
  ↓ message: "Processing"
  ↓ extra: {request_id: "123", user: "john"}

# Context manager
with logger.contextualize(trace_id="xyz"):
    logger.info("In context")
      ↓ message: "In context"
      ↓ extra: {trace_id: "xyz"}
    
    request_logger.info("Also in context")
      ↓ message: "Also in context"
      ↓ extra: {request_id: "123", user: "john", trace_id: "xyz"}

# After context
logger.info("Outside")
  ↓ message: "Outside"
  ↓ extra: {}
```
