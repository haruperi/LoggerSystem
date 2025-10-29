# Custom Logger System - Class Diagrams

## Overview
A Loguru-inspired logging system with minimal dependencies, focusing on ease of use, formatting, rotation, and filtering capabilities.

---

## 1. Core Logger Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                           Logger                                 │
├─────────────────────────────────────────────────────────────────┤
│ - handlers: List[Handler]                                        │
│ - levels: Dict[str, Level]                                       │
│ - extra: Dict[str, Any]                                          │
│ - exception_formatter: ExceptionFormatter                        │
├─────────────────────────────────────────────────────────────────┤
│ + add(sink, **options) -> int                                    │
│ + remove(handler_id: int) -> None                                │
│ + trace(message: str, *args, **kwargs) -> None                   │
│ + debug(message: str, *args, **kwargs) -> None                   │
│ + info(message: str, *args, **kwargs) -> None                    │
│ + success(message: str, *args, **kwargs) -> None                 │
│ + warning(message: str, *args, **kwargs) -> None                 │
│ + error(message: str, *args, **kwargs) -> None                   │
│ + critical(message: str, *args, **kwargs) -> None                │
│ + log(level: str, message: str, *args, **kwargs) -> None         │
│ + bind(**kwargs) -> Logger                                       │
│ + contextualize(**kwargs) -> ContextManager                      │
│ + catch(exception=Exception, **kwargs) -> Decorator              │
│ + opt(exception=None, **kwargs) -> Logger                        │
│ + level(name: str, no: int, color: str, icon: str) -> None      │
│ + disable(name: str) -> None                                     │
│ + enable(name: str) -> None                                      │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Handler System

```
┌─────────────────────────────────────────────────────────────────┐
│                         Handler (Base)                           │
├─────────────────────────────────────────────────────────────────┤
│ # id: int                                                        │
│ # sink: Any                                                      │
│ # formatter: Formatter                                           │
│ # level: Level                                                   │
│ # filter_func: Optional[Callable]                                │
│ # colorize: bool                                                 │
│ # serialize: bool                                                │
│ # backtrace: bool                                                │
│ # diagnose: bool                                                 │
│ # enqueue: bool                                                  │
│ # catch: bool                                                    │
├─────────────────────────────────────────────────────────────────┤
│ + emit(record: LogRecord) -> None                                │
│ + should_emit(record: LogRecord) -> bool                         │
│ + format(record: LogRecord) -> str                               │
│ + close() -> None                                                │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │
                ┌─────────────┼─────────────┐
                │             │             │
┌───────────────┴──────┐  ┌──┴──────────┐  ┌┴─────────────────┐
│   FileHandler        │  │ StreamHandler│  │  CallableHandler │
├──────────────────────┤  ├──────────────┤  ├──────────────────┤
│ - path: Path         │  │ - stream     │  │ - func: Callable │
│ - rotation: Rotation │  │              │  │                  │
│ - retention: str     │  │              │  │                  │
│ - compression: str   │  │              │  │                  │
│ - encoding: str      │  │              │  │                  │
│ - file_handle        │  │              │  │                  │
├──────────────────────┤  ├──────────────┤  ├──────────────────┤
│ + rotate() -> None   │  │ + flush()    │  │ + call()         │
│ + should_rotate()    │  │              │  │                  │
│ + compress() -> None │  │              │  │                  │
└──────────────────────┘  └──────────────┘  └──────────────────┘
```

---

## 3. Log Record Structure

```
┌─────────────────────────────────────────────────────────────────┐
│                          LogRecord                               │
├─────────────────────────────────────────────────────────────────┤
│ + elapsed: timedelta                                             │
│ + exception: Optional[ExceptionInfo]                             │
│ + extra: Dict[str, Any]                                          │
│ + file: FileInfo                                                 │
│ + function: str                                                  │
│ + level: Level                                                   │
│ + line: int                                                      │
│ + message: str                                                   │
│ + module: str                                                    │
│ + name: str                                                      │
│ + process: ProcessInfo                                           │
│ + thread: ThreadInfo                                             │
│ + time: datetime                                                 │
├─────────────────────────────────────────────────────────────────┤
│ + to_dict() -> Dict[str, Any]                                    │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│   ExceptionInfo  │    │    FileInfo      │    │   ProcessInfo    │
├──────────────────┤    ├──────────────────┤    ├──────────────────┤
│ + type: Type     │    │ + name: str      │    │ + id: int        │
│ + value: Exception│   │ + path: str      │    │ + name: str      │
│ + traceback      │    │                  │    │                  │
└──────────────────┘    └──────────────────┘    └──────────────────┘

┌──────────────────┐    ┌──────────────────┐
│   ThreadInfo     │    │      Level       │
├──────────────────┤    ├──────────────────┤
│ + id: int        │    │ + name: str      │
│ + name: str      │    │ + no: int        │
│                  │    │ + color: str     │
│                  │    │ + icon: str      │
└──────────────────┘    └──────────────────┘
```

---

## 4. Formatting System

```
┌─────────────────────────────────────────────────────────────────┐
│                        Formatter                                 │
├─────────────────────────────────────────────────────────────────┤
│ - format_string: str                                             │
│ - colorizer: Colorizer                                           │
│ - tokens: List[Token]                                            │
├─────────────────────────────────────────────────────────────────┤
│ + format(record: LogRecord) -> str                               │
│ + parse_format_string() -> List[Token]                           │
│ + apply_colors(text: str, record: LogRecord) -> str              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ uses
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         Colorizer                                │
├─────────────────────────────────────────────────────────────────┤
│ - enabled: bool                                                  │
│ - colors: Dict[str, str]                                         │
├─────────────────────────────────────────────────────────────────┤
│ + colorize(text: str, color: str) -> str                         │
│ + strip_colors(text: str) -> str                                 │
│ + get_level_color(level: str) -> str                             │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    ExceptionFormatter                            │
├─────────────────────────────────────────────────────────────────┤
│ - colorize: bool                                                 │
│ - backtrace: bool                                                │
│ - diagnose: bool                                                 │
├─────────────────────────────────────────────────────────────────┤
│ + format_exception(exc_info) -> str                              │
│ + format_traceback(tb) -> str                                    │
│ + format_frame(frame) -> str                                     │
│ + get_context_lines(filename, lineno) -> List[str]              │
└─────────────────────────────────────────────────────────────────┘
```

---

## 5. Rotation and Retention System

```
┌─────────────────────────────────────────────────────────────────┐
│                    Rotation (Abstract)                           │
├─────────────────────────────────────────────────────────────────┤
│ + should_rotate(file_path: Path, record: LogRecord) -> bool     │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │
        ┌─────────────────────┼──────────────────────┐
        │                     │                      │
┌───────┴────────┐  ┌─────────┴──────┐  ┌───────────┴─────────┐
│ SizeRotation   │  │  TimeRotation  │  │  CallbackRotation   │
├────────────────┤  ├────────────────┤  ├─────────────────────┤
│ - max_size     │  │ - interval     │  │ - callback: Callable│
│                │  │ - when: str    │  │                     │
│                │  │ - at_time      │  │                     │
├────────────────┤  ├────────────────┤  ├─────────────────────┤
│ + should_rotate│  │ + should_rotate│  │ + should_rotate     │
└────────────────┘  └────────────────┘  └─────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                       Retention                                  │
├─────────────────────────────────────────────────────────────────┤
│ - count: Optional[int]                                           │
│ - age: Optional[timedelta]                                       │
│ - total_size: Optional[int]                                      │
├─────────────────────────────────────────────────────────────────┤
│ + clean_old_files(directory: Path) -> None                       │
│ + should_delete(file: Path) -> bool                              │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      Compression                                 │
├─────────────────────────────────────────────────────────────────┤
│ - format: str  # "gz", "zip", "tar.gz", etc                     │
├─────────────────────────────────────────────────────────────────┤
│ + compress(file_path: Path) -> Path                              │
│ + decompress(file_path: Path) -> Path                            │
└─────────────────────────────────────────────────────────────────┘
```

---

## 6. Filter System

```
┌─────────────────────────────────────────────────────────────────┐
│                      Filter (Protocol)                           │
├─────────────────────────────────────────────────────────────────┤
│ + __call__(record: LogRecord) -> bool                            │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │
        ┌─────────────────────┼──────────────────────┐
        │                     │                      │
┌───────┴────────┐  ┌─────────┴──────┐  ┌───────────┴─────────┐
│  LevelFilter   │  │  ModuleFilter  │  │  CustomFilter       │
├────────────────┤  ├────────────────┤  ├─────────────────────┤
│ - min_level    │  │ - modules: List│  │ - func: Callable    │
│ - max_level    │  │ - exclude: bool│  │                     │
├────────────────┤  ├────────────────┤  ├─────────────────────┤
│ + __call__()   │  │ + __call__()   │  │ + __call__()        │
└────────────────┘  └────────────────┘  └─────────────────────┘
```

---

## 7. Context and Binding System

```
┌─────────────────────────────────────────────────────────────────┐
│                       ContextManager                             │
├─────────────────────────────────────────────────────────────────┤
│ - logger: Logger                                                 │
│ - extra: Dict[str, Any]                                          │
│ - previous_extra: Dict[str, Any]                                 │
├─────────────────────────────────────────────────────────────────┤
│ + __enter__() -> Logger                                          │
│ + __exit__(exc_type, exc_val, exc_tb) -> None                   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                       BoundLogger                                │
├─────────────────────────────────────────────────────────────────┤
│ - parent_logger: Logger                                          │
│ - bound_extra: Dict[str, Any]                                    │
├─────────────────────────────────────────────────────────────────┤
│ + trace/debug/info/etc(...) -> None                              │
│ + bind(**kwargs) -> BoundLogger                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 8. Async and Queue Support

```
┌─────────────────────────────────────────────────────────────────┐
│                       AsyncHandler                               │
├─────────────────────────────────────────────────────────────────┤
│ - queue: Queue                                                   │
│ - worker_thread: Thread                                          │
│ - stop_event: Event                                              │
│ - base_handler: Handler                                          │
├─────────────────────────────────────────────────────────────────┤
│ + emit(record: LogRecord) -> None                                │
│ + start_worker() -> None                                         │
│ + stop_worker() -> None                                          │
│ + worker_loop() -> None                                          │
└─────────────────────────────────────────────────────────────────┘
```

---

## 9. Utilities and Helpers

```
┌─────────────────────────────────────────────────────────────────┐
│                      FrameInspector                              │
├─────────────────────────────────────────────────────────────────┤
│ + get_caller_frame(depth: int) -> FrameType                      │
│ + extract_frame_info(frame: FrameType) -> Dict                   │
│ + get_module_name(frame: FrameType) -> str                       │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      TimeUtils                                   │
├─────────────────────────────────────────────────────────────────┤
│ + parse_duration(duration: str) -> timedelta                     │
│ + parse_size(size: str) -> int                                   │
│ + format_time(dt: datetime, fmt: str) -> str                     │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      Serializer                                  │
├─────────────────────────────────────────────────────────────────┤
│ + serialize(record: LogRecord) -> str                            │
│ + to_json(record: LogRecord) -> str                              │
└─────────────────────────────────────────────────────────────────┘
```

---

## 10. Complete System Interaction Diagram

```
┌─────────────┐
│    User     │
└──────┬──────┘
       │ logger.info("message")
       │
       ▼
┌─────────────────────────────────────┐
│           Logger                    │
│  - Creates LogRecord                │
│  - Adds context/extra               │
│  - Gets frame info                  │
└──────┬──────────────────────────────┘
       │
       │ For each handler
       ▼
┌─────────────────────────────────────┐
│          Handler                    │
│  1. Check if should emit (filter)   │
│  2. Format the record               │
│  3. Write to sink                   │
└──────┬──────────────────────────────┘
       │
       ├────────────┬─────────────┬──────────────┐
       │            │             │              │
       ▼            ▼             ▼              ▼
┌──────────┐  ┌──────────┐  ┌────────┐  ┌──────────────┐
│   File   │  │  Stream  │  │ Custom │  │   Async      │
│          │  │          │  │Function│  │   Queue      │
│  Rotation│  │  stdout  │  │        │  │   Worker     │
│Compression│ │  stderr  │  │        │  │              │
│Retention │  │          │  │        │  │              │
└──────────┘  └──────────┘  └────────┘  └──────────────┘
```

---

## Key Design Principles

1. **Separation of Concerns**: Each component has a single responsibility
2. **Extensibility**: Easy to add new handlers, formatters, and filters
3. **Lazy Evaluation**: Format strings and exceptions only when needed
4. **Thread Safety**: Use locks for shared resources
5. **Performance**: Minimize overhead in the hot path
6. **Simplicity**: Clean API with sensible defaults

---

## Usage Example Pattern

```python
# Simple usage
logger.info("Hello {name}", name="World")

# With context
with logger.contextualize(request_id="123"):
    logger.info("Processing request")

# Binding
request_logger = logger.bind(user_id=456)
request_logger.info("User action")

# Exception catching
@logger.catch
def my_function():
    raise ValueError("Error")

# Custom handler
logger.add("app.log", rotation="500 MB", retention="10 days")
logger.add(sys.stderr, level="WARNING", colorize=True)
logger.add(custom_function, serialize=True)
```
