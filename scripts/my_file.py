from datetime import datetime, timedelta
from mylogger.record import LogRecord, FileInfo, ProcessInfo, ThreadInfo, Level

def my_function():
    

    # Create a log record
    record = LogRecord(
        elapsed=timedelta(seconds=5.5),
        exception=None,
        extra={'user_id': 123, 'request_id': 'abc'},
        file=FileInfo(name="app.py", path="/app/app.py"),
        function="process_request",
        level=Level(name="INFO", no=20, color="white", icon="ℹ️"),
        line=42,
        message="User logged in successfully",
        module="myapp.auth",
        name="myapp",
        process=ProcessInfo(id=12345, name="python"),
        thread=ThreadInfo(id=67890, name="MainThread"),
        time=datetime.now()
    )

    # Simple string representation
    print(str(record))
    # Output: [INFO] User logged in successfully

    # Detailed representation
    print(repr(record))
    # Output: LogRecord(level=INFO, message='User logged in successfully', ...)

    # Serialize to dictionary
    data = record.to_dict()
    print(data['level']['name'])  # 'INFO'
    print(data['extra']['user_id'])  # 123
    print(data['time']['repr'])  # '2024-01-15T10:30:45'