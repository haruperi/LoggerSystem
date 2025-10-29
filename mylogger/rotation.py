"""
Log file rotation strategies
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class Rotation(ABC):
    """Base rotation class"""
    
    @abstractmethod
    def should_rotate(self, file_path: Path, record: Any) -> bool:
        """Check if rotation is needed"""
        pass


class SizeRotation(Rotation):
    """Rotate based on file size"""
    
    def __init__(self, max_size: int):
        self.max_size = max_size
        
    def should_rotate(self, file_path: Path, record: Any) -> bool:
        """Check if file size exceeds threshold"""
        if not file_path.exists():
            return False
        return file_path.stat().st_size >= self.max_size


class TimeRotation(Rotation):
    """Rotate based on time"""
    
    def __init__(self, interval: str):
        self.interval = interval
        self.last_rotation = None
        
    def should_rotate(self, file_path: Path, record: Any) -> bool:
        """Check if time interval has passed"""
        # TODO: Implement time-based rotation check
        return False
