from abc import ABC, abstractmethod
from typing import Any, Optional

from .adapters.file_source_adapter import FileSourceAdapter


class KnowledgeBaseStore(ABC):
    """Knowledge Base Store Abstract Base Class
    
    統一知識庫操作介面，實現 dependency injection pattern。
    為未來支援多種 vector store 後端做準備。
    """
    
    def __init__(self, file_source_adapter: FileSourceAdapter):
        """Initialize with file source adapter
        
        Args:
            file_source_adapter: FileSourceAdapter instance for file retrieval
        """
        self.file_source_adapter = file_source_adapter
    
    @abstractmethod
    async def refresh_knowledge_base(self) -> None:
        """刷新知識庫
        
        如果知識庫不存在，會自動建立；如果已存在，會進行更新。
        執行完整的文件處理流程：檔案載入 → 語義切分 → 向量化 → 索引建立。
        """
        pass
    
    @abstractmethod
    async def clear_knowledge_base(self) -> None:
        """清空知識庫
        
        移除所有向量資料和索引，重置知識庫為空白狀態。
        """
        pass
    
    @abstractmethod
    async def load_from_existing_collection(self) -> None:
        """從現有的向量資料庫 collection 載入知識庫索引
        
        直接使用已存在的向量索引，跳過文件掃描、載入和向量化流程。
        適用於索引已建立且無需更新的情境。
        
        Raises:
            RuntimeError: 當 collection 不存在或載入失敗時
            ValueError: 當 collection 配置不相容時
        """
        pass
    
    @abstractmethod
    async def query_knowledge_base(self, query: str, system_prompt: Optional[str] = None) -> str:
        """查詢知識庫
        
        使用 ReAct Agent 查詢相關文件片段，並產生回應。
        內部會建立 ReAct Agent 來處理查詢，提供更智能的回應。
        
        Args:
            query: 查詢字串
            system_prompt: 系統提示詞（可選）
            
        Returns:
            str: 查詢結果回應
        """
        pass