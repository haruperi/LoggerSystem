"""
Tests for file rotation functionality
"""

import pytest
import time
from pathlib import Path
from datetime import datetime, timedelta
import tempfile
import shutil

from mylogger.rotation import Rotation, SizeRotation, TimeRotation
from mylogger import Logger
from mylogger.record import LogRecord, Level, FileInfo, ProcessInfo, ThreadInfo
from mylogger import level as levels


class TestSizeRotation:
    """Test size-based rotation"""
    
    def test_size_rotation_with_int(self):
        """Test creating SizeRotation with integer bytes"""
        rotation = SizeRotation(1024)
        assert rotation.max_bytes == 1024
        assert rotation.current_size == 0
    
    def test_size_rotation_with_string(self):
        """Test creating SizeRotation with size string"""
        rotation = SizeRotation("10 KB")
        assert rotation.max_bytes == 10 * 1024
        
        rotation = SizeRotation("5 MB")
        assert rotation.max_bytes == 5 * 1024 * 1024
    
    def test_size_rotation_invalid_size(self):
        """Test that invalid size raises error"""
        with pytest.raises(ValueError):
            SizeRotation(-1)
        
        with pytest.raises(ValueError):
            SizeRotation(0)
    
    def test_size_rotation_should_rotate(self, tmp_path):
        """Test should_rotate returns True when size exceeded"""
        # Create a test file
        test_file = tmp_path / "test.log"
        test_file.write_text("x" * 100)  # 100 bytes
        
        rotation = SizeRotation(50)  # 50 bytes max
        
        # Create a dummy record
        record = LogRecord(
            elapsed=timedelta(seconds=1),
            exception=None,
            extra={},
            file=FileInfo(name='test.py', path='/test.py'),
            function='test',
            level=levels.INFO,
            line=1,
            message='Test',
            module='test',
            name='test',
            process=ProcessInfo(id=1, name='test'),
            thread=ThreadInfo(id=1, name='test'),
            time=datetime.now()
        )
        
        # Should rotate because file is 100 bytes, limit is 50
        assert rotation.should_rotate(test_file, record) is True
    
    def test_size_rotation_should_not_rotate(self, tmp_path):
        """Test should_rotate returns False when under size limit"""
        test_file = tmp_path / "test.log"
        test_file.write_text("x" * 30)  # 30 bytes
        
        rotation = SizeRotation(50)  # 50 bytes max
        
        record = LogRecord(
            elapsed=timedelta(seconds=1),
            exception=None,
            extra={},
            file=FileInfo(name='test.py', path='/test.py'),
            function='test',
            level=levels.INFO,
            line=1,
            message='Test',
            module='test',
            name='test',
            process=ProcessInfo(id=1, name='test'),
            thread=ThreadInfo(id=1, name='test'),
            time=datetime.now()
        )
        
        # Should not rotate because file is 30 bytes, limit is 50
        assert rotation.should_rotate(test_file, record) is False
    
    def test_size_rotation_reset(self):
        """Test reset clears the size counter"""
        rotation = SizeRotation(1024)
        rotation.current_size = 500
        
        rotation.reset()
        assert rotation.current_size == 0


class TestTimeRotation:
    """Test time-based rotation"""
    
    def test_time_rotation_daily(self):
        """Test creating daily rotation"""
        rotation = TimeRotation("daily")
        assert rotation.interval_type == "daily"
        assert rotation.rotation_time == (0, 0)
    
    def test_time_rotation_weekly(self):
        """Test creating weekly rotation"""
        rotation = TimeRotation("weekly")
        assert rotation.interval_type == "weekly"
    
    def test_time_rotation_monthly(self):
        """Test creating monthly rotation"""
        rotation = TimeRotation("monthly")
        assert rotation.interval_type == "monthly"
    
    def test_time_rotation_specific_time(self):
        """Test rotation at specific time"""
        rotation = TimeRotation("12:30")
        assert rotation.interval_type == "time"
        assert rotation.rotation_time == (12, 30)
        
        rotation = TimeRotation("09:00")
        assert rotation.rotation_time == (9, 0)
    
    def test_time_rotation_weekday(self):
        """Test rotation on specific weekday"""
        rotation = TimeRotation("monday")
        assert rotation.interval_type == "weekday"
        assert rotation.weekday == 0
        
        rotation = TimeRotation("friday")
        assert rotation.weekday == 4
    
    def test_time_rotation_interval(self):
        """Test interval-based rotation"""
        rotation = TimeRotation("1 hour")
        assert rotation.interval_type == "interval"
        assert rotation.interval == timedelta(hours=1)
        
        rotation = TimeRotation("30 minutes")
        assert rotation.interval == timedelta(minutes=30)
    
    def test_time_rotation_invalid_time(self):
        """Test invalid time format raises error"""
        with pytest.raises(ValueError):
            TimeRotation("25:00")  # Invalid hour
        
        with pytest.raises(ValueError):
            TimeRotation("12:60")  # Invalid minute
    
    def test_time_rotation_invalid_format(self):
        """Test invalid format raises error"""
        with pytest.raises(ValueError):
            TimeRotation("invalid")
    
    def test_time_rotation_should_rotate_interval(self):
        """Test interval-based rotation"""
        rotation = TimeRotation("1 hour")
        
        # Create record with current time
        now = datetime.now()
        record = LogRecord(
            elapsed=timedelta(seconds=1),
            exception=None,
            extra={},
            file=FileInfo(name='test.py', path='/test.py'),
            function='test',
            level=levels.INFO,
            line=1,
            message='Test',
            module='test',
            name='test',
            process=ProcessInfo(id=1, name='test'),
            thread=ThreadInfo(id=1, name='test'),
            time=now
        )
        
        # First check initializes
        assert rotation.should_rotate(Path("test.log"), record) is False
        assert rotation.last_rotation is not None
        assert rotation.next_rotation is not None
        
        # Create record 2 hours later (should rotate)
        future_record = LogRecord(
            elapsed=timedelta(seconds=1),
            exception=None,
            extra={},
            file=FileInfo(name='test.py', path='/test.py'),
            function='test',
            level=levels.INFO,
            line=1,
            message='Test',
            module='test',
            name='test',
            process=ProcessInfo(id=1, name='test'),
            thread=ThreadInfo(id=1, name='test'),
            time=now + timedelta(hours=2)
        )
        
        assert rotation.should_rotate(Path("test.log"), future_record) is True
    
    def test_time_rotation_reset(self):
        """Test reset updates rotation times"""
        rotation = TimeRotation("1 hour")
        
        # Initialize
        now = datetime.now()
        record = LogRecord(
            elapsed=timedelta(seconds=1),
            exception=None,
            extra={},
            file=FileInfo(name='test.py', path='/test.py'),
            function='test',
            level=levels.INFO,
            line=1,
            message='Test',
            module='test',
            name='test',
            process=ProcessInfo(id=1, name='test'),
            thread=ThreadInfo(id=1, name='test'),
            time=now
        )
        rotation.should_rotate(Path("test.log"), record)
        
        old_next = rotation.next_rotation
        
        # Reset
        time.sleep(0.01)  # Small delay
        rotation.reset()
        
        # Next rotation should be different
        assert rotation.next_rotation != old_next


class TestFileHandlerRotation:
    """Test rotation integration with FileHandler"""
    
    def test_file_handler_no_rotation(self, tmp_path):
        """Test FileHandler without rotation"""
        log_file = tmp_path / "app.log"
        
        logger = Logger()
        logger.add(str(log_file), level="INFO")
        
        logger.info("Test message 1")
        logger.info("Test message 2")
        
        # Should only have one file
        assert log_file.exists()
        assert len(list(tmp_path.glob("*.log"))) == 1
    
    def test_file_handler_size_rotation(self, tmp_path):
        """Test FileHandler with size-based rotation"""
        log_file = tmp_path / "app.log"
        
        logger = Logger()
        # Rotate every 100 bytes
        logger.add(str(log_file), level="INFO", rotation=100)
        
        # Write messages until rotation happens
        for i in range(20):
            logger.info(f"Test message number {i:03d} with some extra text to make it longer")
        
        # Should have rotated at least once
        log_files = list(tmp_path.glob("*.log"))
        assert len(log_files) >= 2
        
        # Original file should still exist
        assert log_file.exists()
        
        # Should have timestamped files
        rotated_files = [f for f in log_files if f != log_file]
        assert len(rotated_files) >= 1
        
        # Check filename pattern: app.YYYY-MM-DD_HH-MM-SS.log
        for f in rotated_files:
            assert f.stem.startswith("app.")
            assert len(f.stem.split(".")) >= 2
    
    def test_file_handler_time_rotation_manual(self, tmp_path):
        """Test FileHandler with time-based rotation (manual trigger)"""
        log_file = tmp_path / "app.log"
        
        logger = Logger()
        # Use a very short interval for testing
        logger.add(str(log_file), level="INFO", rotation="1 second")
        
        logger.info("Message 1")
        
        # Wait for rotation time
        time.sleep(1.1)
        
        logger.info("Message 2 - after rotation time")
        
        # Should have at least 2 files
        log_files = list(tmp_path.glob("*.log"))
        assert len(log_files) >= 2
    
    def test_file_handler_rotation_preserves_content(self, tmp_path):
        """Test that rotation preserves file content"""
        log_file = tmp_path / "app.log"
        
        logger = Logger()
        logger.add(str(log_file), level="INFO", rotation=100)
        
        # Write enough to trigger rotation
        messages = []
        for i in range(10):
            msg = f"Message {i:03d} with enough text to fill up the file quickly"
            messages.append(msg)
            logger.info(msg)
        
        # Read all log files
        all_content = []
        for log in sorted(tmp_path.glob("*.log")):
            content = log.read_text()
            all_content.append(content)
        
        combined = "\n".join(all_content)
        
        # All messages should be present somewhere
        for msg in messages:
            assert msg in combined
    
    def test_file_handler_rotation_with_string_size(self, tmp_path):
        """Test rotation with human-readable size string"""
        log_file = tmp_path / "app.log"
        
        logger = Logger()
        logger.add(str(log_file), level="INFO", rotation="1 KB")
        
        # Write enough to exceed 1KB
        for i in range(50):
            logger.info(f"Message {i:04d} " + "x" * 50)
        
        # Should have rotated
        log_files = list(tmp_path.glob("*.log"))
        assert len(log_files) >= 2


class TestRotationIntegration:
    """Integration tests for rotation"""
    
    def test_rotation_repr(self):
        """Test __repr__ methods"""
        size_rot = SizeRotation("10 MB")
        assert "SizeRotation" in repr(size_rot)
        assert "10485760" in repr(size_rot)  # 10MB in bytes
        
        time_rot = TimeRotation("daily")
        assert "TimeRotation" in repr(time_rot)
        assert "daily" in repr(time_rot)
    
    def test_multiple_rotations(self, tmp_path):
        """Test multiple rotations in succession"""
        log_file = tmp_path / "app.log"
        
        logger = Logger()
        # Very small size to force multiple rotations
        logger.add(str(log_file), level="INFO", rotation=50)
        
        # Write many messages to trigger multiple rotations
        for i in range(100):
            logger.info(f"Message {i:04d} with text")
        
        # Should have multiple rotated files
        log_files = list(tmp_path.glob("*.log"))
        assert len(log_files) >= 3  # Original + at least 2 rotated
    
    def test_rotation_with_different_extensions(self, tmp_path):
        """Test rotation preserves file extension"""
        log_file = tmp_path / "app.txt"
        
        logger = Logger()
        logger.add(str(log_file), level="INFO", rotation=100)
        
        for i in range(20):
            logger.info(f"Message {i:03d} with some text to fill the file")
        
        # Should have files with .txt extension
        txt_files = list(tmp_path.glob("*.txt"))
        assert len(txt_files) >= 2
        
        # All should have .txt extension
        for f in txt_files:
            assert f.suffix == ".txt"
