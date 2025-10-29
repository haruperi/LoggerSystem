"""
Tests for compression module
"""

import pytest
from pathlib import Path
import gzip
import zipfile
import os

from mylogger.compression import Compression


class TestCompressionInit:
    """Test Compression initialization"""

    def test_init_default(self):
        """Test default initialization"""
        compression = Compression()
        assert compression.format == "gz"
        assert compression.compression_level == 9
        assert compression.keep_original == False

    def test_init_with_gz(self):
        """Test initialization with 'gz' format"""
        compression = Compression(format="gz")
        assert compression.format == "gz"

    def test_init_with_gzip(self):
        """Test initialization with 'gzip' format (normalized to 'gz')"""
        compression = Compression(format="gzip")
        assert compression.format == "gz"

    def test_init_with_zip(self):
        """Test initialization with 'zip' format"""
        compression = Compression(format="zip")
        assert compression.format == "zip"

    def test_init_with_invalid_format(self):
        """Test initialization with invalid format"""
        with pytest.raises(ValueError, match="Unsupported compression format"):
            Compression(format="rar")

    def test_init_with_compression_level(self):
        """Test initialization with custom compression level"""
        compression = Compression(compression_level=5)
        assert compression.compression_level == 5

    def test_init_with_invalid_compression_level_low(self):
        """Test initialization with too low compression level"""
        with pytest.raises(ValueError, match="compression_level must be 1-9"):
            Compression(compression_level=0)

    def test_init_with_invalid_compression_level_high(self):
        """Test initialization with too high compression level"""
        with pytest.raises(ValueError, match="compression_level must be 1-9"):
            Compression(compression_level=10)

    def test_init_keep_original(self):
        """Test initialization with keep_original=True"""
        compression = Compression(keep_original=True)
        assert compression.keep_original == True

    def test_repr(self):
        """Test string representation"""
        compression = Compression(format="gz", compression_level=5, keep_original=True)
        assert repr(compression) == "Compression(format='gz', level=5, keep_original=True)"


class TestGzipCompression:
    """Test gzip compression functionality"""

    def test_compress_gzip(self, tmp_path):
        """Test basic gzip compression"""
        # Create a test file
        test_file = tmp_path / "test.log"
        test_content = "This is a test log file\n" * 100
        test_file.write_text(test_content, encoding="utf-8")

        # Compress it
        compression = Compression(format="gz")
        compressed = compression.compress(test_file)

        # Check that compressed file exists
        assert compressed is not None
        assert compressed.exists()
        assert compressed.suffix == ".gz"
        assert compressed.name == "test.log.gz"

        # Check that original file was deleted (keep_original=False)
        assert not test_file.exists()

        # Verify compressed content
        with gzip.open(compressed, "rt", encoding="utf-8") as f:
            decompressed_content = f.read()
        assert decompressed_content == test_content

    def test_compress_gzip_keep_original(self, tmp_path):
        """Test gzip compression with keep_original=True"""
        test_file = tmp_path / "test.log"
        test_content = "Test content\n" * 50
        test_file.write_text(test_content, encoding="utf-8")

        compression = Compression(format="gz", keep_original=True)
        compressed = compression.compress(test_file)

        # Both files should exist
        assert compressed.exists()
        assert test_file.exists()

    def test_compress_gzip_different_levels(self, tmp_path):
        """Test different compression levels"""
        test_file = tmp_path / "test.log"
        test_content = "A" * 10000  # Repeated content compresses well
        test_file.write_text(test_content, encoding="utf-8")

        # Compress with level 1 (fast, less compression)
        compression_fast = Compression(format="gz", compression_level=1, keep_original=True)
        compressed_fast = compression_fast.compress(test_file)
        size_fast = compressed_fast.stat().st_size
        compressed_fast.unlink()

        # Compress with level 9 (slow, best compression)
        compression_best = Compression(format="gz", compression_level=9, keep_original=True)
        compressed_best = compression_best.compress(test_file)
        size_best = compressed_best.stat().st_size

        # Level 9 should be smaller than level 1 for highly compressible content
        assert size_best <= size_fast

    def test_compress_nonexistent_file(self, tmp_path):
        """Test compression of non-existent file"""
        compression = Compression(format="gz")
        with pytest.raises(FileNotFoundError):
            compression.compress(tmp_path / "nonexistent.log")

    def test_compress_directory(self, tmp_path):
        """Test compression of directory (should fail)"""
        compression = Compression(format="gz")
        with pytest.raises(ValueError, match="Not a file"):
            compression.compress(tmp_path)


class TestZipCompression:
    """Test zip compression functionality"""

    def test_compress_zip(self, tmp_path):
        """Test basic zip compression"""
        test_file = tmp_path / "test.log"
        test_content = "This is a test log file\n" * 100
        test_file.write_text(test_content, encoding="utf-8")

        compression = Compression(format="zip")
        compressed = compression.compress(test_file)

        # Check that compressed file exists
        assert compressed is not None
        assert compressed.exists()
        assert compressed.suffix == ".zip"
        assert compressed.name == "test.log.zip"

        # Check that original file was deleted
        assert not test_file.exists()

        # Verify compressed content (normalize line endings for cross-platform compatibility)
        with zipfile.ZipFile(compressed, "r") as zipf:
            assert "test.log" in zipf.namelist()
            decompressed_content = zipf.read("test.log").decode("utf-8")
        # Normalize line endings for comparison (Windows uses \r\n, Unix uses \n)
        assert decompressed_content.replace("\r\n", "\n") == test_content

    def test_compress_zip_keep_original(self, tmp_path):
        """Test zip compression with keep_original=True"""
        test_file = tmp_path / "test.log"
        test_content = "Test content\n" * 50
        test_file.write_text(test_content, encoding="utf-8")

        compression = Compression(format="zip", keep_original=True)
        compressed = compression.compress(test_file)

        # Both files should exist
        assert compressed.exists()
        assert test_file.exists()


class TestDecompression:
    """Test decompression functionality"""

    def test_decompress_gzip(self, tmp_path):
        """Test gzip decompression"""
        # Create and compress a file
        test_file = tmp_path / "test.log"
        test_content = "This is test content\n" * 50
        test_file.write_text(test_content, encoding="utf-8")

        compression = Compression(format="gz")
        compressed = compression.compress(test_file)

        # Decompress it
        decompressed = compression.decompress(compressed)

        # Check content
        assert decompressed.exists()
        assert decompressed.read_text(encoding="utf-8") == test_content

    def test_decompress_zip(self, tmp_path):
        """Test zip decompression"""
        # Create and compress a file
        test_file = tmp_path / "test.log"
        test_content = "This is test content\n" * 50
        test_file.write_text(test_content, encoding="utf-8")

        compression = Compression(format="zip")
        compressed = compression.compress(test_file)

        # Decompress it
        decompressed = compression.decompress(compressed)

        # Check content
        assert decompressed.exists()
        assert decompressed.read_text(encoding="utf-8") == test_content

    def test_decompress_nonexistent_file(self, tmp_path):
        """Test decompression of non-existent file"""
        compression = Compression()
        with pytest.raises(FileNotFoundError):
            compression.decompress(tmp_path / "nonexistent.gz")

    def test_decompress_unknown_format(self, tmp_path):
        """Test decompression of unsupported format"""
        test_file = tmp_path / "test.rar"
        test_file.write_text("content")

        compression = Compression()
        result = compression.decompress(test_file)
        assert result is None  # Should return None for unsupported format


class TestCompressionRatio:
    """Test compression ratio calculation"""

    def test_compression_ratio(self, tmp_path):
        """Test compression ratio calculation"""
        # Create a highly compressible file
        test_file = tmp_path / "test.log"
        test_content = "A" * 10000  # Very compressible
        test_file.write_text(test_content, encoding="utf-8")

        compression = Compression(format="gz", keep_original=True)
        compressed = compression.compress(test_file)

        ratio = compression.get_compression_ratio(test_file, compressed)

        # Should be highly compressed (>90% reduction)
        assert ratio > 90.0

    def test_compression_ratio_random_data(self, tmp_path):
        """Test compression ratio on less compressible data"""
        import random
        import string

        # Create less compressible data
        test_file = tmp_path / "test.log"
        random_content = "".join(random.choices(string.ascii_letters + string.digits, k=10000))
        test_file.write_text(random_content, encoding="utf-8")

        compression = Compression(format="gz", keep_original=True)
        compressed = compression.compress(test_file)

        ratio = compression.get_compression_ratio(test_file, compressed)

        # Should still have some compression, but less than highly compressible data
        assert 0 < ratio < 90.0

    def test_compression_ratio_nonexistent_files(self, tmp_path):
        """Test compression ratio with non-existent files"""
        compression = Compression()
        ratio = compression.get_compression_ratio(
            tmp_path / "nonexistent1.log", tmp_path / "nonexistent2.gz"
        )
        assert ratio == 0.0


class TestCompressionEdgeCases:
    """Test edge cases and error handling"""

    def test_compress_empty_file(self, tmp_path):
        """Test compression of empty file"""
        test_file = tmp_path / "empty.log"
        test_file.write_text("", encoding="utf-8")

        compression = Compression(format="gz")
        compressed = compression.compress(test_file)

        assert compressed.exists()

        # Decompress and verify
        decompressed = compression.decompress(compressed)
        assert decompressed.read_text(encoding="utf-8") == ""

    def test_compress_binary_file(self, tmp_path):
        """Test compression of binary file"""
        test_file = tmp_path / "binary.dat"
        binary_content = bytes(range(256)) * 10
        test_file.write_bytes(binary_content)

        compression = Compression(format="gz")
        compressed = compression.compress(test_file)

        assert compressed.exists()

        # Decompress and verify
        with gzip.open(compressed, "rb") as f:
            decompressed_content = f.read()
        assert decompressed_content == binary_content

    def test_compress_large_file(self, tmp_path):
        """Test compression of larger file"""
        test_file = tmp_path / "large.log"
        # Create 1MB of data
        large_content = "Test line " + ("A" * 90) + "\n"
        large_content = large_content * 10000  # Approx 1MB
        test_file.write_text(large_content, encoding="utf-8")

        compression = Compression(format="gz")
        compressed = compression.compress(test_file)

        assert compressed.exists()

        # Should be significantly compressed
        original_size = len(large_content)
        compressed_size = compressed.stat().st_size
        assert compressed_size < original_size * 0.1  # At least 90% reduction

    def test_compress_with_special_characters(self, tmp_path):
        """Test compression of file with special characters in name"""
        test_file = tmp_path / "test-file_123.log"
        test_content = "Content with special chars: ñ, ü, 中文\n" * 10
        test_file.write_text(test_content, encoding="utf-8")

        compression = Compression(format="gz")
        compressed = compression.compress(test_file)

        assert compressed.exists()
        assert compressed.name == "test-file_123.log.gz"

        # Verify content is preserved
        with gzip.open(compressed, "rt", encoding="utf-8") as f:
            decompressed_content = f.read()
        assert decompressed_content == test_content
