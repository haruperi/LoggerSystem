"""
File rotation strategies for log files

This module provides different rotation strategies that determine when
a log file should be rotated (closed, renamed, and a new file opened).
"""

from abc import ABC, abstractmethod
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Union


class Rotation(ABC):
    """Abstract base class for rotation strategies

    A rotation strategy determines when a log file should be rotated.
    Rotation involves closing the current file, renaming it with a timestamp,
    and opening a new file with the original name.
    """

    @abstractmethod
    def should_rotate(self, file_path: Path, record: "LogRecord") -> bool:  # pyright: ignore[reportUndefinedVariable]
        """Check if the file should be rotated

        Args:
            file_path: Path to the current log file
            record: The log record about to be written

        Returns:
            True if file should be rotated, False otherwise
        """
        pass

    @abstractmethod
    def reset(self) -> None:
        """Reset the rotation state after a rotation occurs

        This is called after a file is rotated to reset any internal
        state tracking (e.g., file size counter, last rotation time).
        """
        pass


class SizeRotation(Rotation):
    """Rotate log files based on file size

    This rotation strategy triggers when the log file reaches a specified size.

    Attributes:
        max_bytes: Maximum file size in bytes before rotation
        current_size: Current tracked size of the file

    Example:
        >>> rotation = SizeRotation("10 MB")
        >>> rotation = SizeRotation("500 KB")
        >>> rotation = SizeRotation(1024 * 1024)  # 1 MB in bytes
    """

    def __init__(self, max_size: Union[str, int]):
        """Initialize size-based rotation

        Args:
            max_size: Maximum size before rotation. Can be:
                - Integer: bytes (e.g., 1048576 for 1MB)
                - String: human-readable size (e.g., "10 MB", "500 KB")

        Raises:
            ValueError: If max_size is invalid or cannot be parsed
        """
        from .utils import TimeUtils

        if isinstance(max_size, str):
            self.max_bytes = TimeUtils.parse_size(max_size)
        elif isinstance(max_size, int):
            if max_size <= 0:
                raise ValueError(f"max_size must be positive, got {max_size}")
            self.max_bytes = max_size
        else:
            raise TypeError(f"max_size must be str or int, got {type(max_size)}")

        self.current_size = 0

    def should_rotate(self, file_path: Path, record: "LogRecord") -> bool:  # pyright: ignore[reportUndefinedVariable]
        """Check if file size exceeds maximum

        Args:
            file_path: Path to the current log file
            record: The log record about to be written (not used for size rotation)

        Returns:
            True if current file size >= max_bytes
        """
        try:
            # Get actual file size
            if file_path.exists():
                actual_size = file_path.stat().st_size
                self.current_size = actual_size
                return actual_size >= self.max_bytes
            return False
        except (OSError, IOError):
            # If we can't check file size, don't rotate
            return False

    def reset(self) -> None:
        """Reset the size counter after rotation"""
        self.current_size = 0

    def __repr__(self) -> str:
        """Return string representation"""
        return f"SizeRotation(max_bytes={self.max_bytes})"


class TimeRotation(Rotation):
    """Rotate log files based on time intervals

    This rotation strategy triggers at specific time intervals or times.

    Supports:
    - Fixed intervals: "1 hour", "30 minutes", "1 day"
    - Daily rotation: "daily" or "00:00"
    - Weekly rotation: "weekly" or "monday"
    - Monthly rotation: "monthly"
    - Specific time: "12:00", "18:30"

    Attributes:
        interval_type: Type of time rotation ('interval', 'daily', 'weekly', 'monthly', 'time')
        interval: timedelta for interval-based rotation
        rotation_time: Specific time of day for rotation (hours, minutes)
        last_rotation: Timestamp of last rotation
        next_rotation: Calculated next rotation time

    Example:
        >>> rotation = TimeRotation("1 hour")
        >>> rotation = TimeRotation("daily")
        >>> rotation = TimeRotation("12:00")
        >>> rotation = TimeRotation("monday")
    """

    def __init__(self, when: str):
        """Initialize time-based rotation

        Args:
            when: When to rotate. Can be:
                - "daily": Rotate at midnight
                - "weekly": Rotate on Monday at midnight
                - "monthly": Rotate on 1st of month at midnight
                - "HH:MM": Rotate at specific time (e.g., "12:00", "18:30")
                - "N unit": Rotate every N time units (e.g., "1 hour", "30 minutes")
                - "monday", "tuesday", etc.: Rotate on specific day at midnight

        Raises:
            ValueError: If 'when' format is not recognized
        """
        from .utils import TimeUtils

        self.when = when.lower().strip()
        self.last_rotation: Optional[datetime] = None
        self.next_rotation: Optional[datetime] = None

        # Parse the rotation schedule
        if self.when == "daily":
            self.interval_type = "daily"
            self.rotation_time = (0, 0)  # Midnight
        elif self.when == "weekly":
            self.interval_type = "weekly"
            self.rotation_time = (0, 0)  # Monday at midnight
        elif self.when == "monthly":
            self.interval_type = "monthly"
            self.rotation_time = (0, 0)  # 1st of month at midnight
        elif self.when in [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ]:
            self.interval_type = "weekday"
            self.weekday = self._parse_weekday(self.when)
            self.rotation_time = (0, 0)
        elif ":" in self.when:
            # Specific time like "12:00" or "18:30"
            self.interval_type = "time"
            self.rotation_time = self._parse_time(self.when)
        else:
            # Try to parse as interval like "1 hour", "30 minutes"
            try:
                self.interval = TimeUtils.parse_duration(self.when)
                self.interval_type = "interval"
            except ValueError:
                raise ValueError(
                    f"Invalid rotation schedule: '{when}'. "
                    "Expected 'daily', 'weekly', 'monthly', 'HH:MM', weekday name, or time interval."
                )

    def _parse_time(self, time_str: str) -> tuple[int, int]:
        """Parse time string like '12:00' or '18:30'

        Args:
            time_str: Time string in HH:MM format

        Returns:
            Tuple of (hour, minute)

        Raises:
            ValueError: If time format is invalid
        """
        try:
            parts = time_str.split(":")
            if len(parts) != 2:
                raise ValueError("Time must be in HH:MM format")

            hour = int(parts[0])
            minute = int(parts[1])

            if not (0 <= hour <= 23):
                raise ValueError(f"Hour must be 0-23, got {hour}")
            if not (0 <= minute <= 59):
                raise ValueError(f"Minute must be 0-59, got {minute}")

            return (hour, minute)
        except (ValueError, IndexError) as e:
            raise ValueError(f"Invalid time format '{time_str}': {e}")

    def _parse_weekday(self, day: str) -> int:
        """Parse weekday name to number (0=Monday, 6=Sunday)

        Args:
            day: Weekday name (case insensitive)

        Returns:
            Weekday number (0-6)
        """
        days = {
            "monday": 0,
            "tuesday": 1,
            "wednesday": 2,
            "thursday": 3,
            "friday": 4,
            "saturday": 5,
            "sunday": 6,
        }
        return days[day.lower()]

    def _calculate_next_rotation(self, now: datetime) -> datetime:
        """Calculate the next rotation time based on the schedule

        Args:
            now: Current datetime

        Returns:
            Next rotation datetime
        """
        if self.interval_type == "interval":
            # Simple interval-based rotation
            if self.last_rotation is None:
                return now + self.interval
            return self.last_rotation + self.interval

        elif self.interval_type == "daily":
            # Rotate at midnight
            next_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            if now >= next_date:
                next_date = next_date + timedelta(days=1)
            return next_date

        elif self.interval_type == "time":
            # Rotate at specific time each day
            hour, minute = self.rotation_time
            next_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if now >= next_time:
                next_time = next_time + timedelta(days=1)
            return next_time

        elif self.interval_type == "weekly":
            # Rotate on Monday at midnight
            days_until_monday = (7 - now.weekday()) % 7
            if days_until_monday == 0 and now.hour == 0 and now.minute == 0:
                days_until_monday = 7
            next_date = now + timedelta(days=days_until_monday)
            return next_date.replace(hour=0, minute=0, second=0, microsecond=0)

        elif self.interval_type == "weekday":
            # Rotate on specific weekday at midnight
            target_weekday = self.weekday
            current_weekday = now.weekday()
            days_until = (target_weekday - current_weekday) % 7
            if days_until == 0 and now.hour == 0 and now.minute == 0:
                days_until = 7
            next_date = now + timedelta(days=days_until)
            return next_date.replace(hour=0, minute=0, second=0, microsecond=0)

        elif self.interval_type == "monthly":
            # Rotate on 1st of month at midnight
            if now.day == 1 and now.hour == 0 and now.minute == 0:
                # Already at start of month, go to next month
                if now.month == 12:
                    next_date = now.replace(year=now.year + 1, month=1, day=1)
                else:
                    next_date = now.replace(month=now.month + 1, day=1)
            else:
                # Go to 1st of next month
                if now.month == 12:
                    next_date = now.replace(year=now.year + 1, month=1, day=1)
                else:
                    next_date = now.replace(month=now.month + 1, day=1)
            return next_date.replace(hour=0, minute=0, second=0, microsecond=0)

        return now + timedelta(days=1)  # Fallback

    def should_rotate(self, file_path: Path, record: "LogRecord") -> bool:  # pyright: ignore[reportUndefinedVariable]
        """Check if it's time to rotate based on schedule

        Args:
            file_path: Path to the current log file
            record: The log record about to be written

        Returns:
            True if current time >= next rotation time
        """
        now = record.time if hasattr(record, "time") else datetime.now()

        # Initialize on first check
        if self.last_rotation is None:
            self.last_rotation = now
            self.next_rotation = self._calculate_next_rotation(now)
            return False

        # Check if next rotation time has been reached
        if self.next_rotation and now >= self.next_rotation:
            return True

        return False

    def reset(self) -> None:
        """Reset rotation state after a rotation"""
        now = datetime.now()
        self.last_rotation = now
        self.next_rotation = self._calculate_next_rotation(now)

    def __repr__(self) -> str:
        """Return string representation"""
        return f"TimeRotation(when='{self.when}')"
