# API Reference

## Logger

### Methods

#### add(sink, **options)
Add a handler to the logger.

#### remove(handler_id)
Remove a handler by ID.

#### trace/debug/info/success/warning/error/critical(message, *args, **kwargs)
Log a message at the specified level.

#### bind(**kwargs)
Create a bound logger with extra context.

#### contextualize(**kwargs)
Create a context manager with temporary context.

#### catch(exception, **kwargs)
Decorator to catch exceptions.

## Handler

Base class for all handlers.

## Formatter

Format log records into strings.

## More documentation coming soon...
