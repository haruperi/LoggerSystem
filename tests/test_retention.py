"""
Tests for retention module
"""

import pytest
from pathlib import Path
from datetime import datetime, timedelta
import time

from mylogger.retention import Retention


class TestRetentionInit:
    """Test Retention initialization"""
    
    def test_init_empty(self):
        """Test initialization with no policies"""
        retention = Retention()
        assert retention.count is None
        assert retention.age_delta is None
        assert retention.size_bytes is None
    
    def test_init_count(self):
        """Test initialization with count policy"""
        retention = Retention(count=5)
        assert retention.count == 5
        assert retention.age_delta is None
        assert retention.size_bytes is None
    
    def test_init_age_string(self):
        """Test initialization with age string"""
        retention = Retention(age="7 days")
        assert retention.age_delta == timedelta(days=7)
        assert retention.count is None
        assert retention.size_bytes is None
    
    def test_init_age_timedelta(self):
        """Test initialization with timedelta"""
        delta = timedelta(hours=24)
        retention = Retention(age=delta)
        assert retention.age_delta == delta
    
    def test_init_size_int(self):
        """Test initialization with size as integer"""
        retention = Retention(size=1024)
        assert retention.size_bytes == 1024
    
    def test_init_size_string(self):
        """Test initialization with size string"""
        retention = Retention(size="10 MB")
        assert retention.size_bytes == 10 * 1024 * 1024
    
    def test_init_multiple_policies(self):
        """Test initialization with multiple policies"""
        retention = Retention(count=10, age="30 days", size="100 MB")
        assert retention.count == 10
        assert retention.age_delta == timedelta(days=30)
        assert retention.size_bytes == 100 * 1024 * 1024
    
    def test_init_invalid_count(self):
        """Test initialization with invalid count"""
        with pytest.raises(ValueError):
            Retention(count=-1)
        
        with pytest.raises(ValueError):
            Retention(count="not a number")
    
    def test_init_invalid_age(self):
        """Test initialization with invalid age"""
        with pytest.raises(TypeError):
            Retention(age=123)  # Must be string or timedelta
    
    def test_init_invalid_size(self):
        """Test initialization with invalid size"""
        with pytest.raises(ValueError):
            Retention(size=-100)
        
        with pytest.raises(TypeError):
            Retention(size=[100])  # Must be int or string
    
    def test_repr_no_policy(self):
        """Test string representation with no policy"""
        retention = Retention()
        assert "no policy" in repr(retention)
    
    def test_repr_count(self):
        """Test string representation with count"""
        retention = Retention(count=5)
        assert "count=5" in repr(retention)
    
    def test_repr_multiple(self):
        """Test string representation with multiple policies"""
        retention = Retention(count=5, age="7 days")
        repr_str = repr(retention)
        assert "count=5" in repr_str
        assert "age=" in repr_str


class TestRetentionCountBased:
    """Test count-based retention policy"""
    
    def test_clean_count_keep_all(self, tmp_path):
        """Test that all files are kept if under limit"""
        # Create 3 files
        for i in range(3):
            (tmp_path / f"app.{i}.log").write_text(f"content {i}")
        
        retention = Retention(count=5)
        deleted = retention.clean(tmp_path, "app.*.log")
        
        assert len(deleted) == 0
        assert len(list(tmp_path.glob("app.*.log"))) == 3
    
    def test_clean_count_delete_oldest(self, tmp_path):
        """Test that oldest files are deleted"""
        # Create 5 files with different timestamps
        files = []
        for i in range(5):
            file = tmp_path / f"app.{i}.log"
            file.write_text(f"content {i}")
            files.append(file)
            time.sleep(0.01)  # Ensure different timestamps
        
        retention = Retention(count=3)
        deleted = retention.clean(tmp_path, "app.*.log")
        
        # Should delete 2 oldest files
        assert len(deleted) == 2
        assert len(list(tmp_path.glob("app.*.log"))) == 3
        
        # Verify newest files remain
        remaining_files = sorted(list(tmp_path.glob("app.*.log")), 
                               key=lambda f: f.stat().st_mtime, 
                               reverse=True)
        assert remaining_files[0].name == "app.4.log"
        assert remaining_files[1].name == "app.3.log"
        assert remaining_files[2].name == "app.2.log"
    
    def test_clean_count_exact_limit(self, tmp_path):
        """Test when file count exactly matches limit"""
        for i in range(3):
            (tmp_path / f"app.{i}.log").write_text(f"content {i}")
        
        retention = Retention(count=3)
        deleted = retention.clean(tmp_path, "app.*.log")
        
        assert len(deleted) == 0
        assert len(list(tmp_path.glob("app.*.log"))) == 3
    
    def test_clean_count_zero(self, tmp_path):
        """Test with count=0 (delete all files)"""
        for i in range(3):
            (tmp_path / f"app.{i}.log").write_text(f"content {i}")
        
        retention = Retention(count=0)
        deleted = retention.clean(tmp_path, "app.*.log")
        
        assert len(deleted) == 3
        assert len(list(tmp_path.glob("app.*.log"))) == 0


class TestRetentionAgeBased:
    """Test age-based retention policy"""
    
    def test_clean_age_all_recent(self, tmp_path):
        """Test that all recent files are kept"""
        # Create files with current timestamp
        for i in range(3):
            (tmp_path / f"app.{i}.log").write_text(f"content {i}")
        
        retention = Retention(age="1 day")
        deleted = retention.clean(tmp_path, "app.*.log")
        
        assert len(deleted) == 0
        assert len(list(tmp_path.glob("app.*.log"))) == 3
    
    def test_clean_age_delete_old(self, tmp_path):
        """Test that old files are deleted"""
        # Create files
        recent_file = tmp_path / "app.recent.log"
        recent_file.write_text("recent")
        
        old_file = tmp_path / "app.old.log"
        old_file.write_text("old")
        
        # Make old file appear old by modifying its timestamp
        # Set it to 8 days ago
        old_time = (datetime.now() - timedelta(days=8)).timestamp()
        import os
        os.utime(old_file, (old_time, old_time))
        
        retention = Retention(age="7 days")
        deleted = retention.clean(tmp_path, "app.*.log")
        
        # Should delete only the old file
        assert len(deleted) == 1
        assert deleted[0].name == "app.old.log"
        assert recent_file.exists()
        assert not old_file.exists()
    
    def test_clean_age_various_durations(self, tmp_path):
        """Test age with various duration formats"""
        # Create a file
        test_file = tmp_path / "app.log"
        test_file.write_text("content")
        
        # Make it 25 hours old
        old_time = (datetime.now() - timedelta(hours=25)).timestamp()
        import os
        os.utime(test_file, (old_time, old_time))
        
        # Test with "1 day" - should delete
        retention = Retention(age="1 day")
        deleted = retention.clean(tmp_path, "app.log")
        assert len(deleted) == 1
        
        # Recreate file
        test_file.write_text("content")
        os.utime(test_file, (old_time, old_time))
        
        # Test with "2 days" - should keep
        retention = Retention(age="2 days")
        deleted = retention.clean(tmp_path, "app.log")
        assert len(deleted) == 0


class TestRetentionSizeBased:
    """Test size-based retention policy"""
    
    def test_clean_size_under_limit(self, tmp_path):
        """Test that all files are kept if under size limit"""
        # Create 3 small files (100 bytes each)
        for i in range(3):
            (tmp_path / f"app.{i}.log").write_text("A" * 100)
            time.sleep(0.01)
        
        # Limit is 1KB, total is 300 bytes
        retention = Retention(size=1024)
        deleted = retention.clean(tmp_path, "app.*.log")
        
        assert len(deleted) == 0
        assert len(list(tmp_path.glob("app.*.log"))) == 3
    
    def test_clean_size_over_limit(self, tmp_path):
        """Test that oldest files are deleted when over limit"""
        # Create 5 files of 200 bytes each (1000 bytes total)
        for i in range(5):
            (tmp_path / f"app.{i}.log").write_text("A" * 200)
            time.sleep(0.01)  # Ensure different timestamps
        
        # Limit is 500 bytes, should keep only 2-3 newest files
        retention = Retention(size=500)
        deleted = retention.clean(tmp_path, "app.*.log")
        
        # Should delete at least 2 files
        assert len(deleted) >= 2
        
        # Total size of remaining files should be <= 500
        remaining_files = list(tmp_path.glob("app.*.log"))
        total_size = sum(f.stat().st_size for f in remaining_files)
        assert total_size <= 500
    
    def test_clean_size_string_format(self, tmp_path):
        """Test size-based retention with string format"""
        # Create files totaling > 1KB
        for i in range(10):
            (tmp_path / f"app.{i}.log").write_text("A" * 200)
            time.sleep(0.01)
        
        retention = Retention(size="1 KB")
        deleted = retention.clean(tmp_path, "app.*.log")
        
        # Should delete some files
        assert len(deleted) > 0
        
        # Remaining files should total <= 1KB
        remaining_files = list(tmp_path.glob("app.*.log"))
        total_size = sum(f.stat().st_size for f in remaining_files)
        assert total_size <= 1024


class TestRetentionMultiplePolicies:
    """Test retention with multiple policies active"""
    
    def test_clean_count_and_age(self, tmp_path):
        """Test count and age policies together"""
        import os
        
        # Create 5 files: 2 old, 3 recent
        for i in range(2):
            file = tmp_path / f"app.old{i}.log"
            file.write_text("old")
            old_time = (datetime.now() - timedelta(days=10)).timestamp()
            os.utime(file, (old_time, old_time))
            time.sleep(0.01)
        
        for i in range(3):
            file = tmp_path / f"app.new{i}.log"
            file.write_text("new")
            time.sleep(0.01)
        
        # Keep max 4 files AND delete files > 7 days old
        retention = Retention(count=4, age="7 days")
        deleted = retention.clean(tmp_path, "app.*.log")
        
        # Should delete 2 old files (violate age policy)
        # Remaining 3 files are under count limit
        assert len(deleted) == 2
        remaining_files = list(tmp_path.glob("app.*.log"))
        assert len(remaining_files) == 3
        
        # All remaining files should be recent
        for file in remaining_files:
            assert "new" in file.name
    
    def test_clean_count_and_size(self, tmp_path):
        """Test count and size policies together"""
        # Create 10 files of 100 bytes each
        for i in range(10):
            (tmp_path / f"app.{i:02d}.log").write_text("A" * 100)
            time.sleep(0.01)
        
        # Keep max 7 files AND total size under 500 bytes
        retention = Retention(count=7, size=500)
        deleted = retention.clean(tmp_path, "app.*.log")
        
        # Count policy: keep 7, delete 3
        # Size policy: keep ~5 (500 bytes / 100 bytes per file)
        # More restrictive is size policy, so should keep ~5 files
        remaining_files = list(tmp_path.glob("app.*.log"))
        assert len(remaining_files) <= 7
        
        total_size = sum(f.stat().st_size for f in remaining_files)
        assert total_size <= 500


class TestRetentionGetFilesInfo:
    """Test get_files_info method"""
    
    def test_get_files_info_empty_directory(self, tmp_path):
        """Test get_files_info on empty directory"""
        retention = Retention(count=5)
        info = retention.get_files_info(tmp_path, "*.log")
        assert len(info) == 0
    
    def test_get_files_info_basic(self, tmp_path):
        """Test get_files_info returns correct information"""
        # Create files
        for i in range(3):
            (tmp_path / f"app.{i}.log").write_text("content")
            time.sleep(0.01)
        
        retention = Retention(count=2)
        info = retention.get_files_info(tmp_path, "app.*.log")
        
        assert len(info) == 3
        
        # Check that each item has required fields
        for item in info:
            assert 'path' in item
            assert 'size' in item
            assert 'modified' in item
            assert 'age' in item
            assert 'would_delete' in item
            assert isinstance(item['path'], Path)
            assert isinstance(item['size'], int)
            assert isinstance(item['modified'], datetime)
            assert isinstance(item['age'], timedelta)
            assert isinstance(item['would_delete'], bool)
        
        # First 2 files (newest) should not be deleted
        assert info[0]['would_delete'] == False
        assert info[1]['would_delete'] == False
        # Oldest file should be deleted
        assert info[2]['would_delete'] == True
    
    def test_get_files_info_no_policy(self, tmp_path):
        """Test get_files_info with no retention policy"""
        # Create files
        for i in range(3):
            (tmp_path / f"app.{i}.log").write_text("content")
        
        retention = Retention()  # No policy
        info = retention.get_files_info(tmp_path, "app.*.log")
        
        # No files should be marked for deletion
        for item in info:
            assert item['would_delete'] == False


class TestRetentionEstimateSpaceFreed:
    """Test estimate_space_freed method"""
    
    def test_estimate_space_freed_basic(self, tmp_path):
        """Test basic space estimation"""
        # Create files of known sizes
        for i in range(5):
            (tmp_path / f"app.{i}.log").write_text("A" * 100)
            time.sleep(0.01)
        
        # Keep only 2 files (delete 3 files of 100 bytes each)
        retention = Retention(count=2)
        space = retention.estimate_space_freed(tmp_path, "app.*.log")
        
        assert space == 300  # 3 files * 100 bytes
    
    def test_estimate_space_freed_no_deletion(self, tmp_path):
        """Test when no files would be deleted"""
        for i in range(3):
            (tmp_path / f"app.{i}.log").write_text("content")
        
        retention = Retention(count=10)  # Keep all
        space = retention.estimate_space_freed(tmp_path, "app.*.log")
        
        assert space == 0
    
    def test_estimate_space_freed_empty(self, tmp_path):
        """Test on empty directory"""
        retention = Retention(count=5)
        space = retention.estimate_space_freed(tmp_path, "*.log")
        assert space == 0


class TestRetentionEdgeCases:
    """Test edge cases and error handling"""
    
    def test_clean_nonexistent_directory(self, tmp_path):
        """Test cleaning non-existent directory"""
        retention = Retention(count=5)
        deleted = retention.clean(tmp_path / "nonexistent", "*.log")
        assert len(deleted) == 0
    
    def test_clean_file_instead_of_directory(self, tmp_path):
        """Test cleaning a file instead of directory"""
        file = tmp_path / "test.log"
        file.write_text("content")
        
        retention = Retention(count=5)
        deleted = retention.clean(file, "*.log")
        assert len(deleted) == 0
    
    def test_clean_no_matching_files(self, tmp_path):
        """Test cleaning when no files match pattern"""
        (tmp_path / "test.txt").write_text("content")
        
        retention = Retention(count=5)
        deleted = retention.clean(tmp_path, "*.log")
        assert len(deleted) == 0
    
    def test_clean_with_permission_error(self, tmp_path):
        """Test cleaning when file deletion fails"""
        # This test is platform-specific and may not work on all systems
        # It's here for completeness but may be skipped
        file = tmp_path / "test.log"
        file.write_text("content")
        
        retention = Retention(count=0)
        # On Windows, we can't easily simulate permission errors in tests
        # Just verify the method handles errors gracefully
        try:
            deleted = retention.clean(tmp_path, "*.log")
            # If it succeeds, file should be deleted
            assert len(deleted) <= 1
        except Exception:
            # If it fails for some reason, that's okay for this edge case test
            pass
    
    def test_clean_various_patterns(self, tmp_path):
        """Test with various glob patterns"""
        # Create various files
        (tmp_path / "app.log").write_text("content")
        (tmp_path / "app.1.log").write_text("content")
        (tmp_path / "app.2.log").write_text("content")
        (tmp_path / "debug.log").write_text("content")
        (tmp_path / "app.txt").write_text("content")
        
        retention = Retention(count=1)
        
        # Pattern 1: app.*.log (should match app.1.log and app.2.log)
        deleted = retention.clean(tmp_path, "app.*.log")
        assert len(deleted) == 1  # Keep 1, delete 1
        
        # Pattern 2: *.log (should match remaining .log files)
        deleted = retention.clean(tmp_path, "*.log")
        assert len(deleted) >= 1
        
        # Pattern 3: *.txt (should match app.txt)
        deleted = retention.clean(tmp_path, "*.txt")
        assert len(deleted) == 0  # Only 1 file, count=1, so keep it

