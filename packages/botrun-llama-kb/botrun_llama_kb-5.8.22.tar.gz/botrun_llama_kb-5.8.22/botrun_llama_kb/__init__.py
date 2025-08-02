"""
BotRun LlamaIndex Knowledge Base - 智慧知識庫系統

提供基於 LlamaIndex 的純文字知識庫功能，專門針對繁體中文優化。
"""

from .knowledge_base_store import KnowledgeBaseStore
from .knowledge_base_qdrant_store import KnowledgeBaseQdrantStore
from .adapters import FileSourceAdapter, LocalDirectorySourceAdapter
from .knowledge_base_factory import (
    create_kb_store_from_local_dir,
    create_local_directory_adapter,
    knowledge_base_store_factory,
    get_qdrant_config,
)

__version__ = "0.1.0"

__all__ = [
    "KnowledgeBaseStore",
    "KnowledgeBaseQdrantStore",
    "FileSourceAdapter",
    "LocalDirectorySourceAdapter",
    "create_kb_store_from_local_dir",
    "create_local_directory_adapter",
    "knowledge_base_store_factory",
    "get_qdrant_config",
]
