"""
Log file retention policies

This module provides retention management for rotated log files.
Automatically cleans up old log files based on various policies:
- Count-based: Keep only N most recent files
- Age-based: Delete files older than X days
- Size-based: Keep total size under X bytes/MB/GB
"""

from pathlib import Path
from typing import Optional, Union, List
from datetime import datetime, timedelta
import os


class Retention:
    """Manage retention of rotated log files
    
    Implements various retention policies to automatically clean up old logs:
    - Count: Keep only the N most recent files
    - Age: Delete files older than X days
    - Size: Keep total log size under X bytes
    
    Example:
        >>> retention = Retention(count=10)  # Keep 10 most recent
        >>> retention.clean(Path("logs/"), "app*.log")
        
        >>> retention = Retention(age="7 days")  # Delete > 7 days old
        >>> retention.clean(Path("logs/"), "app*.log")
        
        >>> retention = Retention(size="100 MB")  # Keep total under 100MB
        >>> retention.clean(Path("logs/"), "app*.log")
    """
    
    def __init__(
        self,
        count: Optional[int] = None,
        age: Optional[Union[str, timedelta]] = None,
        size: Optional[Union[str, int]] = None
    ):
        """Initialize retention policy
        
        Args:
            count: Maximum number of files to keep. Keeps N most recent files.
                Example: count=10 keeps the 10 newest files
            age: Maximum age of files to keep. Older files are deleted.
                Can be timedelta or string like "7 days", "30 days", "1 week"
            size: Maximum total size of all log files. Keeps newest files until
                total size is under limit. Can be int (bytes) or string like "100 MB"
        
        Note:
            - If multiple policies are specified, ALL must be satisfied
            - If no policies specified, no cleanup will occur
            
        Raises:
            ValueError: If parameters are invalid
        """
        self.count = count
        self.age_delta: Optional[timedelta] = None
        self.size_bytes: Optional[int] = None
        
        # Validate and parse count
        if count is not None:
            if not isinstance(count, int) or count < 0:
                raise ValueError(f"count must be non-negative integer, got {count}")
        
        # Parse age parameter
        if age is not None:
            if isinstance(age, timedelta):
                self.age_delta = age
            elif isinstance(age, str):
                from .utils import TimeUtils
                self.age_delta = TimeUtils.parse_duration(age)
            else:
                raise TypeError(f"age must be str or timedelta, got {type(age)}")
        
        # Parse size parameter
        if size is not None:
            if isinstance(size, int):
                if size < 0:
                    raise ValueError(f"size must be non-negative, got {size}")
                self.size_bytes = size
            elif isinstance(size, str):
                from .utils import TimeUtils
                self.size_bytes = TimeUtils.parse_size(size)
            else:
                raise TypeError(f"size must be str or int, got {type(size)}")
    
    def clean(
        self,
        directory: Union[str, Path],
        pattern: str = "*.log"
    ) -> List[Path]:
        """Clean up old log files in directory based on retention policy
        
        Args:
            directory: Directory containing log files
            pattern: Glob pattern to match files (default: "*.log")
                Examples: "app*.log", "*.log.*", "debug.*.log"
            
        Returns:
            List of files that were deleted
            
        Example:
            >>> retention = Retention(count=5)
            >>> deleted = retention.clean(Path("logs/"), "app*.log")
            >>> print(f"Deleted {len(deleted)} files")
        """
        directory = Path(directory)
        
        if not directory.exists():
            return []
        
        if not directory.is_dir():
            return []
        
        # Find all matching files
        files = list(directory.glob(pattern))
        
        if not files:
            return []
        
        # Sort by modification time (newest first)
        files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
        
        files_to_delete = set()
        
        # Apply count-based retention
        if self.count is not None:
            if len(files) > self.count:
                files_to_delete.update(files[self.count:])
        
        # Apply age-based retention
        if self.age_delta is not None:
            cutoff_time = datetime.now() - self.age_delta
            cutoff_timestamp = cutoff_time.timestamp()
            
            for file in files:
                try:
                    if file.stat().st_mtime < cutoff_timestamp:
                        files_to_delete.add(file)
                except (OSError, IOError):
                    pass
        
        # Apply size-based retention
        if self.size_bytes is not None:
            total_size = 0
            for file in files:
                try:
                    file_size = file.stat().st_size
                    if total_size + file_size > self.size_bytes:
                        # This file and all older files should be deleted
                        files_to_delete.add(file)
                    else:
                        total_size += file_size
                except (OSError, IOError):
                    pass
        
        # Delete files
        deleted = []
        for file in files_to_delete:
            try:
                file.unlink()
                deleted.append(file)
            except Exception as e:
                import sys
                sys.stderr.write(f"Could not delete {file}: {e}\n")
        
        return deleted
    
    def get_files_info(
        self,
        directory: Union[str, Path],
        pattern: str = "*.log"
    ) -> List[dict]:
        """Get information about files matching pattern
        
        Useful for understanding what will be kept/deleted without actually
        deleting anything.
        
        Args:
            directory: Directory to scan
            pattern: Glob pattern to match files
            
        Returns:
            List of dicts with file information:
            - path: Path object
            - size: Size in bytes
            - modified: Modification timestamp
            - age: Age as timedelta
            - would_delete: Whether this file would be deleted by current policy
            
        Example:
            >>> retention = Retention(count=5)
            >>> info = retention.get_files_info(Path("logs/"))
            >>> for item in info:
            ...     status = "DELETE" if item['would_delete'] else "KEEP"
            ...     print(f"{status}: {item['path'].name} ({item['size']} bytes)")
        """
        directory = Path(directory)
        
        if not directory.exists() or not directory.is_dir():
            return []
        
        files = list(directory.glob(pattern))
        if not files:
            return []
        
        # Sort by modification time (newest first)
        files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
        
        now = datetime.now()
        result = []
        
        # Determine which files would be deleted
        files_to_delete = set()
        
        # Count-based
        if self.count is not None and len(files) > self.count:
            files_to_delete.update(files[self.count:])
        
        # Age-based
        if self.age_delta is not None:
            cutoff_time = now - self.age_delta
            cutoff_timestamp = cutoff_time.timestamp()
            for file in files:
                try:
                    if file.stat().st_mtime < cutoff_timestamp:
                        files_to_delete.add(file)
                except (OSError, IOError):
                    pass
        
        # Size-based
        if self.size_bytes is not None:
            total_size = 0
            for file in files:
                try:
                    file_size = file.stat().st_size
                    if total_size + file_size > self.size_bytes:
                        files_to_delete.add(file)
                    else:
                        total_size += file_size
                except (OSError, IOError):
                    pass
        
        # Build result list
        for file in files:
            try:
                stat = file.stat()
                modified = datetime.fromtimestamp(stat.st_mtime)
                age = now - modified
                
                result.append({
                    'path': file,
                    'size': stat.st_size,
                    'modified': modified,
                    'age': age,
                    'would_delete': file in files_to_delete
                })
            except (OSError, IOError):
                pass
        
        return result
    
    def estimate_space_freed(
        self,
        directory: Union[str, Path],
        pattern: str = "*.log"
    ) -> int:
        """Estimate how much space would be freed by cleanup
        
        Args:
            directory: Directory to scan
            pattern: Glob pattern to match files
            
        Returns:
            Estimated bytes that would be freed
            
        Example:
            >>> retention = Retention(age="7 days")
            >>> space = retention.estimate_space_freed(Path("logs/"))
            >>> print(f"Would free {space / 1024 / 1024:.1f} MB")
        """
        info = self.get_files_info(directory, pattern)
        return sum(item['size'] for item in info if item['would_delete'])
    
    def __repr__(self) -> str:
        """String representation"""
        parts = []
        if self.count is not None:
            parts.append(f"count={self.count}")
        if self.age_delta is not None:
            parts.append(f"age={self.age_delta}")
        if self.size_bytes is not None:
            parts.append(f"size={self.size_bytes}")
        
        if not parts:
            parts.append("no policy")
        
        return f"Retention({', '.join(parts)})"
