"""
Log file compression utilities

This module provides compression functionality for rotated log files.
Supports gzip and zip formats to save disk space.
"""

import gzip
import zipfile
from pathlib import Path
from typing import Optional, Union, Literal
import shutil
import os


class Compression:
    """Compress log files to save disk space
    
    Supports:
    - gzip (.gz) - Better compression, standard for logs
    - zip (.zip) - More compatible, supports multiple files
    
    After compression, the original file is deleted unless keep_original=True.
    
    Example:
        >>> compression = Compression("gz")
        >>> compressed = compression.compress(Path("app.log"))
        >>> print(compressed)  # app.log.gz
    """
    
    def __init__(
        self,
        format: Union[str, Literal["gz", "gzip", "zip"]] = "gz",
        compression_level: int = 9,
        keep_original: bool = False
    ):
        """Initialize compression settings
        
        Args:
            format: Compression format. Can be:
                - "gz" or "gzip": gzip compression
                - "zip": zip compression
            compression_level: Compression level (1-9). Higher = better compression
                but slower. Default is 9 (maximum compression).
            keep_original: If True, keep the original file after compression.
                Default is False (delete original after compression).
        
        Raises:
            ValueError: If format is not supported
            ValueError: If compression_level is not 1-9
        """
        # Normalize format
        format_lower = format.lower()
        if format_lower in ["gz", "gzip"]:
            self.format = "gz"
        elif format_lower == "zip":
            self.format = "zip"
        else:
            raise ValueError(
                f"Unsupported compression format: '{format}'. "
                "Expected 'gz', 'gzip', or 'zip'."
            )
        
        if not (1 <= compression_level <= 9):
            raise ValueError(
                f"compression_level must be 1-9, got {compression_level}"
            )
        
        self.compression_level = compression_level
        self.keep_original = keep_original
    
    def compress(self, file_path: Union[str, Path]) -> Optional[Path]:
        """Compress a log file
        
        Args:
            file_path: Path to the file to compress
            
        Returns:
            Path to the compressed file, or None if compression failed
            
        Raises:
            FileNotFoundError: If file_path doesn't exist
            
        Example:
            >>> compression = Compression("gz")
            >>> compressed = compression.compress("app.log")
            >>> print(compressed)
            app.log.gz
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not file_path.is_file():
            raise ValueError(f"Not a file: {file_path}")
        
        try:
            if self.format == "gz":
                compressed_path = self._compress_gzip(file_path)
            elif self.format == "zip":
                compressed_path = self._compress_zip(file_path)
            else:
                return None
            
            # Delete original file if requested
            if not self.keep_original and compressed_path:
                try:
                    file_path.unlink()
                except Exception:
                    pass  # Don't fail if we can't delete original
            
            return compressed_path
            
        except Exception as e:
            import sys
            sys.stderr.write(f"Compression error for {file_path}: {e}\n")
            return None
    
    def _compress_gzip(self, file_path: Path) -> Path:
        """Compress file using gzip
        
        Args:
            file_path: Path to file to compress
            
        Returns:
            Path to compressed file (.gz)
        """
        compressed_path = file_path.with_suffix(file_path.suffix + '.gz')
        
        with open(file_path, 'rb') as f_in:
            with gzip.open(
                compressed_path,
                'wb',
                compresslevel=self.compression_level
            ) as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        return compressed_path
    
    def _compress_zip(self, file_path: Path) -> Path:
        """Compress file using zip
        
        Args:
            file_path: Path to file to compress
            
        Returns:
            Path to compressed file (.zip)
        """
        compressed_path = file_path.with_suffix(file_path.suffix + '.zip')
        
        with zipfile.ZipFile(
            compressed_path,
            'w',
            compression=zipfile.ZIP_DEFLATED,
            compresslevel=self.compression_level
        ) as zipf:
            zipf.write(file_path, arcname=file_path.name)
        
        return compressed_path
    
    def decompress(self, file_path: Union[str, Path]) -> Optional[Path]:
        """Decompress a compressed log file
        
        Useful for reading old compressed logs.
        
        Args:
            file_path: Path to compressed file (.gz or .zip)
            
        Returns:
            Path to decompressed file, or None if decompression failed
            
        Example:
            >>> compression = Compression("gz")
            >>> decompressed = compression.decompress("app.log.gz")
            >>> print(decompressed)
            app.log
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        try:
            if file_path.suffix == '.gz':
                return self._decompress_gzip(file_path)
            elif file_path.suffix == '.zip':
                return self._decompress_zip(file_path)
            else:
                raise ValueError(f"Unknown compression format: {file_path.suffix}")
                
        except Exception as e:
            import sys
            sys.stderr.write(f"Decompression error for {file_path}: {e}\n")
            return None
    
    def _decompress_gzip(self, file_path: Path) -> Path:
        """Decompress gzip file
        
        Args:
            file_path: Path to .gz file
            
        Returns:
            Path to decompressed file
        """
        # Remove .gz extension
        if file_path.suffix == '.gz':
            decompressed_path = file_path.with_suffix('')
        else:
            decompressed_path = file_path.with_suffix('.decompressed')
        
        with gzip.open(file_path, 'rb') as f_in:
            with open(decompressed_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        return decompressed_path
    
    def _decompress_zip(self, file_path: Path) -> Path:
        """Decompress zip file
        
        Args:
            file_path: Path to .zip file
            
        Returns:
            Path to decompressed file (extracts first file in archive)
        """
        with zipfile.ZipFile(file_path, 'r') as zipf:
            # Extract first file
            names = zipf.namelist()
            if not names:
                raise ValueError(f"Empty zip file: {file_path}")
            
            # Extract to same directory
            zipf.extract(names[0], path=file_path.parent)
            return file_path.parent / names[0]
    
    def get_compression_ratio(self, original: Union[str, Path], compressed: Union[str, Path]) -> float:
        """Calculate compression ratio
        
        Args:
            original: Path to original file
            compressed: Path to compressed file
            
        Returns:
            Compression ratio as percentage (e.g., 75.5 means 75.5% smaller)
            
        Example:
            >>> ratio = compression.get_compression_ratio("app.log", "app.log.gz")
            >>> print(f"Compressed to {100-ratio:.1f}% of original size")
        """
        original_path = Path(original)
        compressed_path = Path(compressed)
        
        if not original_path.exists() or not compressed_path.exists():
            return 0.0
        
        original_size = original_path.stat().st_size
        compressed_size = compressed_path.stat().st_size
        
        if original_size == 0:
            return 0.0
        
        ratio = (1 - compressed_size / original_size) * 100
        return round(ratio, 2)
    
    def __repr__(self) -> str:
        """String representation"""
        return f"Compression(format='{self.format}', level={self.compression_level}, keep_original={self.keep_original})"
