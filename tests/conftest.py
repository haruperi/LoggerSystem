"""
Pytest configuration and fixtures
"""

import pytest
import tempfile
from pathlib import Path


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def temp_log_file(temp_dir):
    """Create a temporary log file path"""
    return temp_dir / "test.log"
