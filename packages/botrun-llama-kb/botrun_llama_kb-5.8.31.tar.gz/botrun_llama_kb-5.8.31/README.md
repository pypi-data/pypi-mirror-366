# BotRun LlamaIndex Knowledge Base

一個基於 LlamaIndex 和 Qdrant 實作的智慧知識庫系統，專為繁體中文和台灣用語優化，支援多格式文件處理和語義搜尋。

## 📋 專案簡介

BotRun LlamaIndex Knowledge Base 是一個企業級的知識庫解決方案，具備以下特色：

- **智慧文件處理**: 支援 TXT、MD、PDF、CSV 等多種格式
- **Hybrid Search**: 結合語義搜尋（Dense Vectors）和關鍵字匹配（Sparse Vectors）
  - https://qdrant.tech/articles/hybrid-search/
  - Dense Vectors: 擅長捕捉文本的語義細微差別
  - Sparse Vectors: 精確地識別關鍵詞
- **語義搜尋 (Dense)**: 使用 Google GenAI Embedding (gemini-embedding-001) 進行語義理解
- **關鍵字搜尋 (Sparse)**: 整合 FastEmbed BM25 進行精確關鍵字匹配
- **ReAct Agent**: 整合智慧代理進行互動式查詢
- **繁體中文優化**: 針對台灣用語和繁體中文進行特別優化
- **模組化架構**: 使用 Constructor Dependency Injection 設計模式
- **向量儲存**: 基於 Qdrant 的高效能 Hybrid 向量資料庫

## 🚀 快速開始

### 環境需求

- Python 3.11+
- uv (套件管理，更快的 pip 和 virtualenv 替代品)
- Qdrant 服務 (本地或遠端)
- Google GenAI API Key

### 安裝

1. **clone 專案**:
```bash
git clone <repository-url>
cd botrun-llama-kb
```

2. **安裝 dependencies**:
```bash
uv sync
```

3. **設定環境變數**:

創建 `.env` 檔案或設定以下環境變數：

```bash
# Google GenAI API Key (必要)
GOOGLE_API_KEY=your_google_api_key_here

# Qdrant 配置 (根據你的 Qdrant 服務設定)
QDRANT_HOST=localhost          # 預設: localhost
QDRANT_PORT=6333              # 預設: 6333
QDRANT_API_KEY=               # 如果需要認證
QDRANT_PREFIX=/qdrant         # API 路徑前綴
QDRANT_HTTPS=false            # 是否使用 HTTPS
```

### 使用方式

#### 程式化使用

根據不同的使用情境，有三種主要的操作模式：

##### 1. 完全重建模式 (全新建立或完全清空重建)

```python
import asyncio
from botrun_llama_kb.knowledge_base_factory import create_kb_store_from_local_dir, get_qdrant_config

async def full_rebuild():
    # 建立知識庫實例
    kb_store = await create_kb_store_from_local_dir(
        directory="path/to/your/documents",
        qdrant_config=get_qdrant_config(),  # 自動從環境變數讀取
        embedding_model="gemini-embedding-001",
        agent_model="gemini-2.5-flash"
    )
    
    # ⚠️  完全清空知識庫和快取 (會刪除所有資料!)
    await kb_store.clear_knowledge_base()
    
    # 刷新知識庫 (重新處理所有文件)
    await kb_store.refresh_knowledge_base()
    
    # 查詢測試
    result = await kb_store.query_knowledge_base("你的問題")
    print(result)

asyncio.run(full_rebuild())
```

##### 2. 增量更新模式 (檢查更新並同步)

```python
import asyncio
from botrun_llama_kb.knowledge_base_factory import create_kb_store_from_local_dir

async def incremental_update():
    # 建立知識庫實例
    kb_store = await create_kb_store_from_local_dir(
        directory="path/to/your/documents"
    )
    
    # 🔄 智能刷新 (如果不存在會建立，存在則檢查更新)
    await kb_store.refresh_knowledge_base()
    
    # 查詢測試
    result = await kb_store.query_knowledge_base("你的問題")
    print(result)

asyncio.run(incremental_update())
```

##### 3. 快速載入模式 (直接使用現有索引)

```python
import asyncio
from botrun_llama_kb.knowledge_base_factory import create_kb_store_from_local_dir

async def fast_load():
    # 建立知識庫實例
    kb_store = await create_kb_store_from_local_dir(
        directory="path/to/your/documents"  # 目錄用於確定 collection 名稱
    )
    
    # ⚡ 直接載入現有的向量索引 (最快速)
    await kb_store.load_from_existing_collection()
    
    # 查詢測試
    result = await kb_store.query_knowledge_base("你的問題")
    print(result)

asyncio.run(fast_load())
```

##### 使用情境說明

| 模式 | 使用時機 | 優點 | 缺點 |
|------|----------|------|------|
| **完全重建** | 首次建立、文件大幅變更、快取損壞 | 確保資料完整性、清理舊快取 | 處理時間最長 |
| **增量更新** | 日常使用、文件有增減 | 智能檢測更新、利用快取加速 | 中等處理時間 |
| **快速載入** | 開發測試、生產服務啟動 | 啟動最快速、無需重新處理 | 需要現有索引存在 |

##### 進階配置範例

```python
import asyncio
from botrun_llama_kb.knowledge_base_factory import create_kb_store_from_local_dir

async def advanced_usage():
    # 自訂 Qdrant 配置
    qdrant_config = {
        "host": "your-qdrant-host.com",
        "port": 443,
        "api_key": "your-api-key",
        "prefix": "/qdrant",
        "https": True
    }
    
    # 建立知識庫實例
    kb_store = await create_kb_store_from_local_dir(
        directory="path/to/your/documents",
        qdrant_config=qdrant_config,
        embedding_model="gemini-embedding-001",  # 或 "text-embedding-004"
        agent_model="gemini-2.5-flash"          # 或 "gemini-2.5-pro"
    )
    
    # 根據需求選擇操作模式
    # await kb_store.clear_knowledge_base()        # 完全清空
    # await kb_store.refresh_knowledge_base()      # 智能刷新
    # await kb_store.load_from_existing_collection()  # 快速載入
    
    # 查詢知識庫 (支援繁體中文和台灣用語)
    # 基本查詢 (使用預設系統提示)
    result = await kb_store.query_knowledge_base("你的問題")
    print(result)
    
    # 自訂系統提示的查詢
    custom_prompt = """
    - 請用學術風格回答問題
    - 盡量引用原始資料
    - 回答要詳細且結構化
    """
    result = await kb_store.query_knowledge_base("你的問題", custom_prompt)
    print(result)

asyncio.run(advanced_usage())
```

## 🏗️ 系統架構

### 核心模組

```
botrun_llama_kb/
├── adapters/                          # 文件來源適配器
│   ├── file_source_adapter.py         # 抽象基類
│   └── local_directory_adapter.py     # 本地目錄實現
├── knowledge_base_store.py            # 知識庫抽象介面
├── knowledge_base_qdrant_store.py     # Qdrant 實現
├── knowledge_base_factory.py          # 工廠模式建構器
└── constants.py                       # 常數定義
```

### 設計模式

1. **Abstract Factory Pattern**: `FileSourceAdapter` 支援不同資料來源
2. **Strategy Pattern**: `KnowledgeBaseStore` 支援不同實現方式
3. **Dependency Injection**: Constructor 注入依賴項目
4. **Factory Method**: `knowledge_base_factory` 統一建構流程

### 核心組件

- **FileSourceAdapter**: 負責文件掃描和載入
- **KnowledgeBaseStore**: 知識庫核心操作界面
- **QdrantVectorStore**: 混合向量儲存和檢索 (Dense + Sparse)
- **GoogleGenAIEmbedding**: Dense 向量化 (gemini-embedding-001, 3072維)
- **FastEmbed BM25**: Sparse 向量化 (Qdrant/bm25 關鍵字匹配)
- **SemanticSplitterNodeParser**: 語義切分
- **Hybrid Query Engine**: 混合搜尋查詢引擎
- **ReActAgent**: 智慧查詢代理 (支援混合搜尋與可自訂系統提示)

### 批次處理與容錯機制

系統採用 **IngestionPipeline** 進行大量檔案的批次處理，具備完整的容錯和斷點續傳機制：

```
批次處理流程:
檔案載入 → IngestionPipeline (批次: 50 檔案/批)
    ├── 文件 ID 生成 (MD5: file_path + page_label)
    ├── 重複檢測 (SimpleDocumentStore)
    ├── 語義切分 (SemanticSplitterNodeParser)
    ├── 向量化處理 (GoogleGenAI Embedding)
    ├── 失敗重試 (最多 3 次，間隔 60 秒)
    └── 快取持久化 (每批次完成後立即保存)
```

**容錯機制參數**:
- `BATCH_SIZE=50`: 每批次處理檔案數量
- `MAX_RETRIES=3`: 批次失敗最大重試次數
- `RETRY_DELAY=60`: 重試間隔 (秒)
- `num_workers=1`: 順序處理避免 multiprocessing 問題
- **快取目錄**: `.pipeline_cache/storage_{collection_name}/`
- **斷點續傳**: 基於 doc_id 的增量處理

**GoogleGenAI 連線優化**:
- `retries=5`: API 重試次數
- `timeout=30`: 連線逾時 (秒)
- `retry_min_seconds=10`: 最小重試間隔
- `retry_max_seconds=30`: 最大重試間隔
- `retry_exponential_base=2`: 指數退避基數

### 混合搜尋架構

系統採用 **Dense + Sparse 混合搜尋** 架構，結合語義理解和關鍵字匹配：

```
查詢處理流程:
使用者查詢 → Hybrid Query Engine
    ├── Dense Vector Search (語義搜尋)
    │   ├── Google GenAI Embedding (gemini-embedding-001)
    │   └── 語義相似度匹配 (similarity_top_k=2)
    ├── Sparse Vector Search (關鍵字搜尋)  
    │   ├── FastEmbed BM25 (Qdrant/bm25)
    │   └── 關鍵字精確匹配 (sparse_top_k=12)
    └── Fusion Algorithm (結果融合)
        └── LlamaIndex 內建融合 (hybrid_top_k=3)
```

**核心配置參數**:
- `enable_hybrid=True`: 啟用混合搜尋模式
- `fastembed_sparse_model="Qdrant/bm25"`: BM25 稀疏向量模型
- `similarity_top_k=2`: Dense 向量搜尋結果數
- `sparse_top_k=12`: Sparse 向量搜尋結果數  
- `hybrid_top_k=3`: 最終融合結果數
- `batch_size=20`: 批次處理優化

## 🔧 進階配置

### 自訂嵌入模型

```python
# 在 sh/kb_cli.py 中修改
GEMINI_EMBEDDING_MODEL = "gemini-embedding-001"  # 或其他支援的模型
```

### 自訂 Agent 模型

```python
# 在 sh/kb_cli.py 中修改
GEMINI_AGENT_MODEL = "gemini-2.5-flash"  # 或 gemini-pro
```

### Qdrant 高級配置

```python
qdrant_config = {
    "host": "your-qdrant-host.com",
    "port": 443,
    "api_key": "your-api-key",
    "prefix": "/qdrant",
    "https": True
}
```

## 📊 支援的文件格式

| 格式 | 支援程度 | 說明 |
|------|----------|------|
| `.txt` | ✅ 完整支援 | 純文字檔案 |
| `.md` | ✅ 完整支援 | Markdown 格式 |
| `.pdf` | ✅ 文字內容 | 提取純文字內容 |
| `.csv` | ✅ 表格資料 | 結構化資料處理 |

## 📖 API 參考

### 核心方法

#### `query_knowledge_base(query: str, system_prompt: Optional[str] = None) -> str`

查詢知識庫並取得 AI 回應。

**參數:**
- `query` (str): 使用者查詢內容
- `system_prompt` (Optional[str]): 自訂系統提示詞，控制 AI 回應風格和行為

**回傳值:**
- `str`: AI 處理後的回應內容

**預設行為:**
當 `system_prompt` 為 `None` 時，系統使用預設的英文系統提示：
```
- You can only answer questions based on the tool results. If there is no information, respond that there is no information in the knowledge base. You must not answer on your own.
```

**使用範例:**

```python
# 基本查詢
result = await kb_store.query_knowledge_base("什麼是機器學習?")

# 自訂系統提示的查詢
custom_prompt = """
- 請用繁體中文和台灣用語回答
- 只能根據工具結果回答問題
- 如果沒有資訊，就回知識庫裡面沒有資訊
- 回答時儘可能引用相關資料
"""
result = await kb_store.query_knowledge_base("什麼是機器學習?", custom_prompt)
```

**其他核心方法:**

- `refresh_knowledge_base()`: 智慧刷新知識庫（增量更新）
- `clear_knowledge_base()`: 完全清空知識庫和快取
- `load_from_existing_collection()`: 從現有向量集合快速載入

## 🧪 測試與驗證

專案提供完整的測試流程：

```bash
# 執行完整測試
python sh/kb_cli.py

```

## 套件管理

### 新增/移除套件
```bash
# 新增套件
uv add <package-name>

# 移除套件
uv remove <package-name>

# 同步依賴（安裝所有依賴）
uv sync

# 運行 Python 腳本
uv run python script.py
```

### 更新 `requirements.txt`
```bash
# 匯出所有依賴 (包含開發依賴)
uv export --all-extras --format requirements-txt --output-file requirements.txt

# 只匯出生產依賴
uv export --format requirements-txt --output-file requirements.txt

# 匯出特定 extra 的依賴
uv export --extra dev --format requirements-txt --output-file requirements-dev.txt
```