"""
Knowledge Base Factory - 知識庫工廠模式

提供統一的工廠方法來建立知識庫實例和適配器，
簡化使用者的初始化過程並支援多種配置方式。
"""

import os
from typing import Optional, Dict, Any
from qdrant_client import AsyncQdrantClient, QdrantClient

from .constants import QDRANT_ACTION_TIMEOUT

from .knowledge_base_store import KnowledgeBaseStore
from .knowledge_base_qdrant_store import KnowledgeBaseQdrantStore
from .adapters.file_source_adapter import FileSourceAdapter
from .adapters.local_directory_adapter import LocalDirectorySourceAdapter


def create_local_directory_adapter(directory: str) -> LocalDirectorySourceAdapter:
    """建立本地目錄適配器

    Args:
        directory: 本地目錄路徑

    Returns:
        LocalDirectorySourceAdapter: 本地目錄適配器實例

    Raises:
        ValueError: 目錄不存在或無法存取
    """
    if not os.path.exists(directory):
        raise ValueError(f"目錄不存在: {directory}")

    if not os.path.isdir(directory):
        raise ValueError(f"路徑不是目錄: {directory}")

    if not os.access(directory, os.R_OK):
        raise ValueError(f"目錄無法讀取: {directory}")

    print(f"📁 建立本地目錄適配器: {directory}")
    adapter = LocalDirectorySourceAdapter(directory)
    print(f"   集合名稱: {adapter.get_collection_name()}")
    print(f"   支援格式: {', '.join(adapter.supported_extensions)}")

    return adapter


async def knowledge_base_store_factory(
    file_source_adapter: FileSourceAdapter,
    qdrant_config: Optional[Dict[str, Any]] = None,
    embedding_model: str = "gemini-embedding-001",
    agent_model: str = "gemini-2.5-flash",
) -> KnowledgeBaseStore:
    """知識庫儲存工廠方法

    建立 KnowledgeBaseStore 實例，支援多種配置方式。

    Args:
        file_source_adapter: 檔案來源適配器
        qdrant_config: Qdrant 配置選項，預設使用記憶體模式
        embedding_model: 嵌入模型名稱
        agent_model: ReAct Agent 查詢時使用的模型名稱

    Returns:
        KnowledgeBaseStore: 知識庫儲存實例

    Raises:
        ValueError: 缺少必要配置或配置無效
        RuntimeError: 初始化失敗
    """
    print("🏭 建立知識庫儲存實例...")

    # Step 1: 設定 Google API Key
    google_api_key = os.getenv("GOOGLE_API_KEY")
    if not google_api_key:
        raise ValueError("未設定 Google API Key。請設定環境變數 GOOGLE_API_KEY。")

    print(f"   🔑 Google API Key: {'已設定' if google_api_key else '未設定'}")
    print(f"   🧠 嵌入模型: {embedding_model}")

    # Step 2: 設定 Qdrant 客戶端
    if qdrant_config is None:
        raise ValueError(
            "未提供 Qdrant 配置。請使用 get_qdrant_config() 取得配置或設定相關環境變數。"
        )

    # 顯示配置資訊
    if "host" in qdrant_config:
        print(
            f"   🌐 Qdrant 主機: {qdrant_config.get('host', 'localhost')}:{qdrant_config.get('port', 6333)}"
        )
    elif "path" in qdrant_config:
        print(f"   💾 Qdrant 本地: {qdrant_config['path']}")
    elif "location" in qdrant_config:
        print(f"   💾 Qdrant 模式: 記憶體模式")

    try:
        # 建立 AsyncQdrant 客戶端
        qdrant_client = QdrantClient(
            host=qdrant_config["host"],
            port=qdrant_config["port"],
            timeout=QDRANT_ACTION_TIMEOUT,
            api_key=qdrant_config.get("api_key"),
            prefix=qdrant_config.get("prefix"),
            https=qdrant_config.get("https", False),
            check_compatibility=False,
        )
        print("   ✅ Qdrant 客戶端已建立")
        qdrant_aclient = AsyncQdrantClient(
            host=qdrant_config["host"],
            port=qdrant_config["port"],
            timeout=QDRANT_ACTION_TIMEOUT,
            api_key=qdrant_config.get("api_key"),
            prefix=qdrant_config.get("prefix"),
            https=qdrant_config.get("https", False),
            check_compatibility=False,
        )
        print("   ✅ AsyncQdrant 客戶端已建立")

        # 建立知識庫儲存實例
        store = KnowledgeBaseQdrantStore(
            file_source_adapter=file_source_adapter,
            qdrant_client=qdrant_client,
            qdrant_aclient=qdrant_aclient,
            google_api_key=google_api_key,
            embedding_model=embedding_model,
            llm_model=agent_model,
        )

        print(f"   ✅ 知識庫儲存實例已建立")
        print(f"   📚 集合名稱: {store.collection_name}")

        return store

    except Exception as e:
        import traceback

        traceback.print_exc()
        print(f"   ❌ 建立知識庫儲存實例失敗: {e}")
        raise RuntimeError(f"初始化知識庫儲存失敗: {e}")


async def create_kb_store_from_local_dir(
    directory: str,
    qdrant_config: Optional[Dict[str, Any]] = None,
    embedding_model: str = "gemini-embedding-001",
    agent_model: str = "gemini-2.5-flash",
) -> KnowledgeBaseStore:
    """從本地目錄建立知識庫（便利方法）

    這是一個便利方法，結合了適配器建立和知識庫工廠方法。

    Args:
        directory: 本地目錄路徑
        qdrant_config: Qdrant 配置選項
        embedding_model: 嵌入模型名稱
        agent_model: ReAct Agent 查詢時使用的模型名稱

    Returns:
        KnowledgeBaseStore: 完整配置的知識庫實例

    Raises:
        ValueError: 目錄不存在或配置無效
        RuntimeError: 初始化失敗
    """
    print(f"🚀 從目錄建立知識庫: {directory}")

    try:
        # Step 1: 建立本地目錄適配器
        adapter = create_local_directory_adapter(directory)

        # Step 2: 建立知識庫儲存實例
        store = await knowledge_base_store_factory(
            file_source_adapter=adapter,
            qdrant_config=qdrant_config,
            embedding_model=embedding_model,
            agent_model=agent_model,
        )

        print(f"🎉 知識庫建立完成！")
        return store

    except Exception as e:
        import traceback

        traceback.print_exc()
        print(f"❌ 從目錄建立知識庫失敗: {e}")
        raise


def get_qdrant_config() -> Dict[str, Any]:
    """從環境變數取得 Qdrant 配置

    必要的環境變數:
    - QDRANT_HOST: Qdrant 主機位址

    可選的環境變數:
    - QDRANT_PORT: Qdrant 埠號 (預設: 6333)
    - QDRANT_API_KEY: API 金鑰
    - QDRANT_PREFIX: URL 前綴 (如 /qdrant)
    - QDRANT_HTTPS: 是否使用 HTTPS (預設: false)

    Returns:
        Dict[str, Any]: Qdrant 客戶端配置字典

    Raises:
        ValueError: 未設定必要的環境變數
    """
    # 檢查必要的環境變數
    host = os.getenv("QDRANT_HOST")
    if not host:
        raise ValueError("未設定 QDRANT_HOST 環境變數。請設定 Qdrant 主機位址。")

    config = {"host": host, "port": int(os.getenv("QDRANT_PORT", "6333"))}

    # API 金鑰
    api_key = os.getenv("QDRANT_API_KEY")
    if api_key:
        config["api_key"] = api_key

    # URL 前綴
    prefix = os.getenv("QDRANT_PREFIX")
    if prefix:
        config["prefix"] = prefix

    # HTTPS 設定
    https = os.getenv("QDRANT_HTTPS", "false").lower() == "true"
    config["https"] = https

    print(f"🌐 使用環境變數 Qdrant 配置: {host}:{config['port']}")
    if prefix:
        print(f"   前綴: {prefix}")
    if https:
        print(f"   HTTPS: 啟用")
    if api_key:
        print(f"   API Key: 已設定")

    return config
