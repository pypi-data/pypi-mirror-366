"""
File Source Adapters - 檔案來源適配器模組

提供統一的檔案來源介面，支援多種檔案來源的抽象化處理。
"""

from .file_source_adapter import FileSourceAdapter
from .local_directory_adapter import LocalDirectorySourceAdapter

__all__ = [
    "FileSourceAdapter",
    "LocalDirectorySourceAdapter",
]