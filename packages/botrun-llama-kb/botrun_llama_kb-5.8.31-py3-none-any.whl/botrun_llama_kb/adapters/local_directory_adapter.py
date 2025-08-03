import os
import glob
from typing import List

from .file_source_adapter import FileSourceAdapter


class LocalDirectorySourceAdapter(FileSourceAdapter):
    """Local Directory Source Adapter - 階段一主要實現
    
    處理本地資料夾中的文件，支援 TXT, MD, PDF, CSV 格式。
    為階段一純文字處理的核心適配器實現。
    """
    
    def __init__(self, directory: str):
        """Initialize with local directory path
        
        Args:
            directory: Path to local directory containing documents
        """
        self.directory = directory
        self.supported_extensions = ['.txt', '.md', '.pdf', '.csv']
    
    async def get_files(self) -> List[str]:
        """獲取本地資料夾中的所有支援檔案
        
        Returns:
            List[str]: List of absolute file paths
        """
        files = []
        for ext in self.supported_extensions:
            pattern = os.path.join(self.directory, f"**/*{ext}")
            found_files = glob.glob(pattern, recursive=True)
            # Verify file format and accessibility
            for file_path in found_files:
                if self._is_valid_file(file_path):
                    files.append(file_path)
        return files
    
    def _is_valid_file(self, file_path: str) -> bool:
        """驗證檔案格式和可讀性
        
        Args:
            file_path: Path to file to validate
            
        Returns:
            bool: True if file is valid and accessible
        """
        try:
            # Check file exists and is readable
            if not os.path.isfile(file_path) or not os.access(file_path, os.R_OK):
                return False
                
            # Check file extension
            _, ext = os.path.splitext(file_path.lower())
            if ext not in self.supported_extensions:
                return False
                
            # Check file is not empty
            if os.path.getsize(file_path) == 0:
                return False
                
            return True
        except (OSError, IOError):
            return False
    
    def get_collection_name(self) -> str:
        """基於資料夾名稱生成 collection name
        
        Returns:
            str: Collection name in format 'kb_local_{dirname}_text'
        """
        dir_name = os.path.basename(self.directory.rstrip('/'))
        return f"kb_local_{dir_name}_text"
    
    def cleanup_temp_files(self, file_paths: List[str]) -> None:
        """本地檔案無需清理
        
        Args:
            file_paths: File paths (ignored for local files)
        """
        # Local files don't need cleanup
        pass