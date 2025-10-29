"""
Tests for LogRecord - Day 18.4
Tests record creation, field population, and serialization
"""

import pytest
from datetime import datetime, timedelta
from mylogger.record import LogRecord, FileInfo, ProcessInfo, ThreadInfo, ExceptionInfo
from mylogger.level import Level
from mylogger import level as levels


class TestLogRecordCreation:
    """Test LogRecord creation and initialization"""
    
    def test_create_basic_record(self):
        """Test creating a basic log record with all required fields"""
        now = datetime.now()
        elapsed = timedelta(seconds=5)
        
        record = LogRecord(
            elapsed=elapsed,
            exception=None,
            extra={},
            file=FileInfo(name='test.py', path='/path/to/test.py'),
            function='test_function',
            level=levels.INFO,
            line=42,
            message='Test message',
            module='test_module',
            name='test_logger',
            process=ProcessInfo(id=1234, name='python'),
            thread=ThreadInfo(id=5678, name='MainThread'),
            time=now
        )
        
        assert record.message == 'Test message'
        assert record.level == levels.INFO
        assert record.line == 42
        assert record.function == 'test_function'
        assert record.module == 'test_module'
        assert record.time == now
        assert record.elapsed == elapsed
    
    def test_record_with_extra_data(self):
        """Test record with extra context data"""
        record = LogRecord(
            elapsed=timedelta(seconds=1),
            exception=None,
            extra={'user_id': 123, 'request_id': 'abc-123'},
            file=FileInfo(name='test.py', path='/path/to/test.py'),
            function='test_function',
            level=levels.INFO,
            line=10,
            message='User action',
            module='test_module',
            name='test_logger',
            process=ProcessInfo(id=1234, name='python'),
            thread=ThreadInfo(id=5678, name='MainThread'),
            time=datetime.now()
        )
        
        assert 'user_id' in record.extra
        assert record.extra['user_id'] == 123
        assert record.extra['request_id'] == 'abc-123'
    
    def test_record_with_exception(self):
        """Test record with exception information"""
        try:
            1 / 0
        except ZeroDivisionError:
            import sys
            exc_info = sys.exc_info()
            exception = ExceptionInfo(
                type=exc_info[0],
                value=exc_info[1],
                traceback=exc_info[2]
            )
        
        record = LogRecord(
            elapsed=timedelta(seconds=1),
            exception=exception,
            extra={},
            file=FileInfo(name='test.py', path='/path/to/test.py'),
            function='test_function',
            level=levels.ERROR,
            line=10,
            message='Error occurred',
            module='test_module',
            name='test_logger',
            process=ProcessInfo(id=1234, name='python'),
            thread=ThreadInfo(id=5678, name='MainThread'),
            time=datetime.now()
        )
        
        assert record.exception is not None
        assert record.exception.type is ZeroDivisionError


class TestLogRecordFieldAccess:
    """Test field access and properties"""
    
    @pytest.fixture
    def sample_record(self):
        """Create a sample record for testing"""
        return LogRecord(
            elapsed=timedelta(seconds=5.5),
            exception=None,
            extra={'user': 'alice', 'action': 'login'},
            file=FileInfo(name='app.py', path='/app/src/app.py'),
            function='handle_login',
            level=levels.SUCCESS,
            line=100,
            message='User logged in successfully',
            module='app',
            name='app_logger',
            process=ProcessInfo(id=9999, name='MainProcess'),
            thread=ThreadInfo(id=8888, name='Worker-1'),
            time=datetime(2024, 1, 15, 14, 30, 45, 123456)
        )
    
    def test_access_basic_fields(self, sample_record):
        """Test accessing basic record fields"""
        assert sample_record.message == 'User logged in successfully'
        assert sample_record.function == 'handle_login'
        assert sample_record.line == 100
        assert sample_record.module == 'app'
        assert sample_record.name == 'app_logger'
    
    def test_access_level(self, sample_record):
        """Test accessing level information"""
        assert sample_record.level.name == 'SUCCESS'
        assert sample_record.level.no == 25
    
    def test_access_file_info(self, sample_record):
        """Test accessing file information"""
        assert sample_record.file.name == 'app.py'
        assert sample_record.file.path == '/app/src/app.py'
    
    def test_access_process_info(self, sample_record):
        """Test accessing process information"""
        assert sample_record.process.id == 9999
        assert sample_record.process.name == 'MainProcess'
    
    def test_access_thread_info(self, sample_record):
        """Test accessing thread information"""
        assert sample_record.thread.id == 8888
        assert sample_record.thread.name == 'Worker-1'
    
    def test_access_time(self, sample_record):
        """Test accessing time information"""
        assert sample_record.time.year == 2024
        assert sample_record.time.month == 1
        assert sample_record.time.day == 15
        assert sample_record.time.hour == 14
        assert sample_record.time.minute == 30
        assert sample_record.time.second == 45
    
    def test_access_elapsed(self, sample_record):
        """Test accessing elapsed time"""
        assert sample_record.elapsed.total_seconds() == 5.5
    
    def test_access_extra(self, sample_record):
        """Test accessing extra data"""
        assert sample_record.extra['user'] == 'alice'
        assert sample_record.extra['action'] == 'login'


class TestLogRecordSerialization:
    """Test LogRecord serialization to dict"""
    
    def test_to_dict_basic(self):
        """Test converting record to dictionary"""
        now = datetime(2024, 1, 15, 10, 30, 45, 123456)
        record = LogRecord(
            elapsed=timedelta(seconds=10),
            exception=None,
            extra={'key': 'value'},
            file=FileInfo(name='test.py', path='/test.py'),
            function='test_func',
            level=levels.INFO,
            line=20,
            message='Test',
            module='test',
            name='logger',
            process=ProcessInfo(id=100, name='proc'),
            thread=ThreadInfo(id=200, name='thread'),
            time=now
        )
        
        data = record.to_dict()
        
        assert isinstance(data, dict)
        assert data['message'] == 'Test'
        assert data['level']['name'] == 'INFO'
        assert data['level']['no'] == 20
        assert data['function'] == 'test_func'
        assert data['line'] == 20
        assert data['module'] == 'test'
    
    def test_to_dict_nested_structures(self):
        """Test that nested objects are properly serialized"""
        record = LogRecord(
            elapsed=timedelta(seconds=5),
            exception=None,
            extra={},
            file=FileInfo(name='app.py', path='/app.py'),
            function='func',
            level=levels.DEBUG,
            line=10,
            message='Test',
            module='app',
            name='logger',
            process=ProcessInfo(id=123, name='python'),
            thread=ThreadInfo(id=456, name='MainThread'),
            time=datetime.now()
        )
        
        data = record.to_dict()
        
        # Check nested file info
        assert 'file' in data
        assert data['file']['name'] == 'app.py'
        assert data['file']['path'] == '/app.py'
        
        # Check nested process info
        assert 'process' in data
        assert data['process']['id'] == 123
        assert data['process']['name'] == 'python'
        
        # Check nested thread info
        assert 'thread' in data
        assert data['thread']['id'] == 456
        assert data['thread']['name'] == 'MainThread'
    
    def test_to_dict_datetime_handling(self):
        """Test that datetime is properly serialized"""
        now = datetime(2024, 1, 15, 10, 30, 45, 123456)
        record = LogRecord(
            elapsed=timedelta(seconds=5),
            exception=None,
            extra={},
            file=FileInfo(name='test.py', path='/test.py'),
            function='func',
            level=levels.INFO,
            line=1,
            message='Test',
            module='test',
            name='logger',
            process=ProcessInfo(id=1, name='proc'),
            thread=ThreadInfo(id=1, name='thread'),
            time=now
        )
        
        data = record.to_dict()
        
        assert 'time' in data
        assert 'timestamp' in data['time']
        assert 'repr' in data['time']
        assert isinstance(data['time']['timestamp'], float)
    
    def test_to_dict_timedelta_handling(self):
        """Test that timedelta is properly serialized"""
        elapsed = timedelta(seconds=123.456)
        record = LogRecord(
            elapsed=elapsed,
            exception=None,
            extra={},
            file=FileInfo(name='test.py', path='/test.py'),
            function='func',
            level=levels.INFO,
            line=1,
            message='Test',
            module='test',
            name='logger',
            process=ProcessInfo(id=1, name='proc'),
            thread=ThreadInfo(id=1, name='thread'),
            time=datetime.now()
        )
        
        data = record.to_dict()
        
        assert 'elapsed' in data
        assert 'seconds' in data['elapsed']
        assert 'repr' in data['elapsed']
        assert abs(data['elapsed']['seconds'] - 123.456) < 0.001
    
    def test_to_dict_extra_data(self):
        """Test that extra data is included in serialization"""
        record = LogRecord(
            elapsed=timedelta(seconds=1),
            exception=None,
            extra={'user_id': 123, 'request_id': 'req-456', 'nested': {'key': 'value'}},
            file=FileInfo(name='test.py', path='/test.py'),
            function='func',
            level=levels.INFO,
            line=1,
            message='Test',
            module='test',
            name='logger',
            process=ProcessInfo(id=1, name='proc'),
            thread=ThreadInfo(id=1, name='thread'),
            time=datetime.now()
        )
        
        data = record.to_dict()
        
        assert 'extra' in data
        assert data['extra']['user_id'] == 123
        assert data['extra']['request_id'] == 'req-456'
        assert data['extra']['nested']['key'] == 'value'


class TestLogRecordStringRepresentation:
    """Test string representations of LogRecord"""
    
    def test_repr(self):
        """Test __repr__ method"""
        record = LogRecord(
            elapsed=timedelta(seconds=1),
            exception=None,
            extra={},
            file=FileInfo(name='test.py', path='/test.py'),
            function='test_func',
            level=levels.INFO,
            line=42,
            message='Test message',
            module='test',
            name='logger',
            process=ProcessInfo(id=1, name='proc'),
            thread=ThreadInfo(id=1, name='thread'),
            time=datetime.now()
        )
        
        repr_str = repr(record)
        assert 'LogRecord' in repr_str
        assert 'INFO' in repr_str
        assert 'Test message' in repr_str
    
    def test_str(self):
        """Test __str__ method"""
        record = LogRecord(
            elapsed=timedelta(seconds=1),
            exception=None,
            extra={},
            file=FileInfo(name='test.py', path='/test.py'),
            function='test_func',
            level=levels.WARNING,
            line=42,
            message='Warning message',
            module='test',
            name='logger',
            process=ProcessInfo(id=1, name='proc'),
            thread=ThreadInfo(id=1, name='thread'),
            time=datetime.now()
        )
        
        str_repr = str(record)
        assert 'WARNING' in str_repr
        assert 'Warning message' in str_repr
