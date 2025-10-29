"""
LogRecord and related data structures
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, Optional


@dataclass
class Level:
    """Log level information"""
    name: str
    no: int
    color: str
    icon: str
    
    def __eq__(self, other):
        return self.no == other.no if isinstance(other, Level) else False
    
    def __lt__(self, other):
        return self.no < other.no if isinstance(other, Level) else False
    
    def __hash__(self):
        return hash(self.name)


@dataclass
class FileInfo:
    """File information"""
    name: str
    path: str


@dataclass
class ProcessInfo:
    """Process information"""
    id: int
    name: str


@dataclass
class ThreadInfo:
    """Thread information"""
    id: int
    name: str


@dataclass
class ExceptionInfo:
    """Exception information"""
    type: type
    value: Exception
    traceback: Any


@dataclass
class LogRecord:
    """Complete log record with all context"""
    elapsed: timedelta
    exception: Optional[ExceptionInfo]
    extra: Dict[str, Any]
    file: FileInfo
    function: str
    level: Level
    line: int
    message: str
    module: str
    name: str
    process: ProcessInfo
    thread: ThreadInfo
    time: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert record to dictionary"""
        # TODO: Implement serialization
        return {}
