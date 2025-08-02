from abc import ABC, abstractmethod
from typing import List


class FileSourceAdapter(ABC):
    """File Source Adapter Abstract Base Class
    
    統一 file retrieval interface，為未來支援多種 file source 做準備。
    實現 dependency injection pattern，簡化 testing 和 configuration management。
    """
    
    @abstractmethod
    async def get_files(self) -> List[str]:
        """Retrieve all files to local temporary directory
        
        Returns:
            List[str]: Local file paths list
        """
        pass
    
    @abstractmethod
    def get_collection_name(self) -> str:
        """Get collection name for this file source
        
        Returns:
            str: Unique collection name for vector store
        """
        pass
    
    @abstractmethod
    def cleanup_temp_files(self, file_paths: List[str]) -> None:
        """Clean up temporary files
        
        Args:
            file_paths: List of file paths to clean up
        """
        pass