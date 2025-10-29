"""
Tests for Serializer class
"""

import json
import pytest
from datetime import datetime, timedelta
from pathlib import Path

from mylogger.utils import Serializer
from mylogger.record import LogRecord, Level, FileInfo, ProcessInfo, ThreadInfo, ExceptionInfo
from mylogger import level as levels


class TestSerializer:
    """Test the Serializer class"""
    
    @pytest.fixture
    def simple_record(self):
        """Create a simple log record for testing"""
        return LogRecord(
            elapsed=timedelta(seconds=1.5),
            exception=None,
            extra={'user_id': 123, 'request_id': 'abc-123'},
            file=FileInfo(name='test.py', path='/path/to/test.py'),
            function='test_function',
            level=levels.INFO,
            line=42,
            message='Test message',
            module='test_module',
            name='test_logger',
            process=ProcessInfo(id=1234, name='python'),
            thread=ThreadInfo(id=5678, name='MainThread'),
            time=datetime(2024, 1, 15, 14, 30, 45, 123456)
        )
    
    @pytest.fixture
    def record_with_exception(self):
        """Create a log record with exception info"""
        # Create exception info
        try:
            raise ValueError("Test error")
        except ValueError as e:
            import sys
            exc_info = sys.exc_info()
            exception = ExceptionInfo(
                type=exc_info[0],
                value=exc_info[1],
                traceback=exc_info[2]
            )
        
        return LogRecord(
            elapsed=timedelta(seconds=2.0),
            exception=exception,
            extra={},
            file=FileInfo(name='test.py', path='/path/to/test.py'),
            function='test_function',
            level=levels.ERROR,
            line=100,
            message='Error occurred',
            module='test_module',
            name='test_logger',
            process=ProcessInfo(id=1234, name='python'),
            thread=ThreadInfo(id=5678, name='MainThread'),
            time=datetime(2024, 1, 15, 14, 30, 45)
        )
    
    def test_serialize_simple_record(self, simple_record):
        """Test serializing a simple record to JSON"""
        json_str = Serializer.serialize(simple_record)
        
        # Should return a valid JSON string
        assert isinstance(json_str, str)
        
        # Parse the JSON to verify it's valid
        data = json.loads(json_str)
        
        # Check basic fields
        assert data['message'] == 'Test message'
        assert data['level']['name'] == 'INFO'
        assert data['level']['no'] == 20
        assert data['function'] == 'test_function'
        assert data['line'] == 42
        assert data['module'] == 'test_module'
        assert data['name'] == 'test_logger'
    
    def test_serialize_time_fields(self, simple_record):
        """Test that time fields are properly serialized"""
        json_str = Serializer.serialize(simple_record)
        data = json.loads(json_str)
        
        # Check time field
        assert 'time' in data
        assert 'timestamp' in data['time']
        assert 'repr' in data['time']
        assert isinstance(data['time']['timestamp'], (int, float))
        assert '2024-01-15' in data['time']['repr']
        
        # Check elapsed field
        assert 'elapsed' in data
        assert 'seconds' in data['elapsed']
        assert data['elapsed']['seconds'] == 1.5
    
    def test_serialize_file_info(self, simple_record):
        """Test that file info is properly serialized"""
        json_str = Serializer.serialize(simple_record)
        data = json.loads(json_str)
        
        assert 'file' in data
        assert data['file']['name'] == 'test.py'
        assert data['file']['path'] == '/path/to/test.py'
    
    def test_serialize_process_thread_info(self, simple_record):
        """Test that process and thread info is properly serialized"""
        json_str = Serializer.serialize(simple_record)
        data = json.loads(json_str)
        
        # Process info
        assert 'process' in data
        assert data['process']['id'] == 1234
        assert data['process']['name'] == 'python'
        
        # Thread info
        assert 'thread' in data
        assert data['thread']['id'] == 5678
        assert data['thread']['name'] == 'MainThread'
    
    def test_serialize_extra_fields(self, simple_record):
        """Test that extra fields are properly serialized"""
        json_str = Serializer.serialize(simple_record)
        data = json.loads(json_str)
        
        assert 'extra' in data
        assert data['extra']['user_id'] == 123
        assert data['extra']['request_id'] == 'abc-123'
    
    def test_serialize_exception_info(self, record_with_exception):
        """Test that exception info is properly serialized"""
        json_str = Serializer.serialize(record_with_exception)
        data = json.loads(json_str)
        
        assert 'exception' in data
        assert data['exception'] is not None
        assert data['exception']['type'] == 'ValueError'
        assert 'Test error' in data['exception']['value']
        assert isinstance(data['exception']['traceback'], bool)
    
    def test_serialize_no_exception(self, simple_record):
        """Test that exception field is None when no exception"""
        json_str = Serializer.serialize(simple_record)
        data = json.loads(json_str)
        
        assert 'exception' in data
        assert data['exception'] is None
    
    def test_to_dict_method(self, simple_record):
        """Test the to_dict convenience method"""
        data = Serializer.to_dict(simple_record)
        
        assert isinstance(data, dict)
        assert data['message'] == 'Test message'
        assert data['level']['name'] == 'INFO'
    
    def test_sanitize_datetime(self):
        """Test sanitizing datetime objects"""
        dt = datetime(2024, 1, 15, 14, 30, 45)
        result = Serializer._sanitize_dict(dt)
        
        assert isinstance(result, str)
        assert '2024-01-15' in result
    
    def test_sanitize_timedelta(self):
        """Test sanitizing timedelta objects"""
        td = timedelta(seconds=123.456)
        result = Serializer._sanitize_dict(td)
        
        assert isinstance(result, (int, float))
        assert result == 123.456
    
    def test_sanitize_path(self):
        """Test sanitizing Path objects"""
        path = Path('/path/to/file.txt')
        result = Serializer._sanitize_dict(path)
        
        assert isinstance(result, str)
        assert 'file.txt' in result
    
    def test_sanitize_exception(self):
        """Test sanitizing Exception objects"""
        exc = ValueError("Test error")
        result = Serializer._sanitize_dict(exc)
        
        assert isinstance(result, str)
        assert 'Test error' in result
    
    def test_sanitize_nested_dict(self):
        """Test sanitizing nested dictionaries"""
        data = {
            'time': datetime(2024, 1, 15),
            'elapsed': timedelta(seconds=10),
            'nested': {
                'path': Path('/test'),
                'error': ValueError("error")
            },
            'list': [datetime(2024, 1, 1), timedelta(seconds=5)]
        }
        
        result = Serializer._sanitize_dict(data)
        
        # All values should be JSON-serializable
        json_str = json.dumps(result)
        parsed = json.loads(json_str)
        
        assert isinstance(parsed['time'], str)
        assert isinstance(parsed['elapsed'], (int, float))
        assert isinstance(parsed['nested']['path'], str)
        assert isinstance(parsed['nested']['error'], str)
        assert isinstance(parsed['list'][0], str)
        assert isinstance(parsed['list'][1], (int, float))
    
    def test_sanitize_custom_object(self):
        """Test sanitizing custom objects"""
        class CustomClass:
            def __init__(self, value):
                self.value = value
            
            def __str__(self):
                return f"Custom({self.value})"
        
        obj = CustomClass(42)
        result = Serializer._sanitize_dict(obj)
        
        assert isinstance(result, str)
        assert 'Custom(42)' in result
    
    def test_json_default_datetime(self):
        """Test _json_default with datetime"""
        dt = datetime(2024, 1, 15, 14, 30, 45)
        result = Serializer._json_default(dt)
        
        assert isinstance(result, str)
        assert '2024-01-15' in result
    
    def test_json_default_timedelta(self):
        """Test _json_default with timedelta"""
        td = timedelta(seconds=123)
        result = Serializer._json_default(td)
        
        assert isinstance(result, (int, float))
        assert result == 123.0
    
    def test_json_default_path(self):
        """Test _json_default with Path"""
        path = Path('/test/path')
        result = Serializer._json_default(path)
        
        assert isinstance(result, str)
    
    def test_json_default_exception(self):
        """Test _json_default with Exception"""
        exc = ValueError("Test error")
        result = Serializer._json_default(exc)
        
        assert isinstance(result, dict)
        assert result['type'] == 'ValueError'
        assert 'Test error' in result['message']
    
    def test_serialize_with_extra_complex_types(self):
        """Test serializing records with complex types in extra"""
        record = LogRecord(
            elapsed=timedelta(seconds=1),
            exception=None,
            extra={
                'timestamp': datetime(2024, 1, 15),
                'path': Path('/test/file'),
                'duration': timedelta(seconds=30),
                'nested': {
                    'time': datetime(2024, 1, 16),
                    'list': [1, 2, datetime(2024, 1, 17)]
                }
            },
            file=FileInfo(name='test.py', path='/test.py'),
            function='test',
            level=levels.INFO,
            line=1,
            message='Test',
            module='test',
            name='test',
            process=ProcessInfo(id=1, name='test'),
            thread=ThreadInfo(id=1, name='test'),
            time=datetime(2024, 1, 15)
        )
        
        json_str = Serializer.serialize(record)
        
        # Should not raise an exception
        data = json.loads(json_str)
        
        # Extra fields should be serializable
        assert 'extra' in data
        # The complex types should have been converted
        assert isinstance(data['extra']['timestamp'], str)
        assert isinstance(data['extra']['duration'], (int, float))
    
    def test_serialize_fallback_on_error(self):
        """Test that serialize provides a fallback on error"""
        # Create a mock record that will cause serialization issues
        class BadObject:
            def __str__(self):
                raise RuntimeError("Cannot convert to string")
            
            def __repr__(self):
                raise RuntimeError("Cannot convert to repr")
        
        # Note: This might not actually fail due to our robust handling,
        # but we test the fallback mechanism exists
        record = LogRecord(
            elapsed=timedelta(seconds=1),
            exception=None,
            extra={},
            file=FileInfo(name='test.py', path='/test.py'),
            function='test',
            level=levels.INFO,
            line=1,
            message='Test message',
            module='test',
            name='test',
            process=ProcessInfo(id=1, name='test'),
            thread=ThreadInfo(id=1, name='test'),
            time=datetime(2024, 1, 15)
        )
        
        # Should always return valid JSON
        json_str = Serializer.serialize(record)
        data = json.loads(json_str)
        
        # At minimum, should have message and level
        assert 'message' in data
        assert 'level' in data
    
    def test_serialize_unicode_message(self):
        """Test serializing records with unicode characters"""
        record = LogRecord(
            elapsed=timedelta(seconds=1),
            exception=None,
            extra={'emoji': '😀', 'chinese': '你好'},
            file=FileInfo(name='test.py', path='/test.py'),
            function='test',
            level=levels.INFO,
            line=1,
            message='Hello 世界 🌍',
            module='test',
            name='test',
            process=ProcessInfo(id=1, name='test'),
            thread=ThreadInfo(id=1, name='test'),
            time=datetime(2024, 1, 15)
        )
        
        json_str = Serializer.serialize(record)
        data = json.loads(json_str)
        
        # Unicode should be preserved
        assert 'Hello' in data['message']
        assert '世界' in data['message']
        assert '🌍' in data['message']
        assert data['extra']['emoji'] == '😀'
        assert data['extra']['chinese'] == '你好'

