import os
import hashlib
import time
import shutil
from tabnanny import verbose
from typing import Any, Optional, List, Dict

from llama_index.core import (
    SimpleDirectoryReader,
    Settings,
    Document,
    StorageContext,
    VectorStoreIndex,
)
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.storage.docstore import SimpleDocumentStore
from llama_index.core.node_parser import SemanticSplitterNodeParser
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.agent.workflow import ReActAgent, ToolCallResult, AgentStream
from llama_index.core.agent.react.formatter import ReActChatFormatter
from llama_index.core.tools import QueryEngineTool
from llama_index.core.workflow import Context
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
from llama_index.llms.google_genai import GoogleGenAI
from qdrant_client import AsyncQdrantClient, QdrantClient

from .knowledge_base_store import KnowledgeBaseStore
from .adapters.file_source_adapter import FileSourceAdapter


def generate_document_id(file_path: str, page_label: Optional[str] = None) -> str:
    """Generate MD5-based document ID from file_path and page_label

    Args:
        file_path: The file path
        page_label: Optional page label, defaults to empty string if None

    Returns:
        str: MD5 hash of file_path + page_label
    """
    page_label = page_label or ""  # Empty string if None
    content = f"{file_path}{page_label}"
    return hashlib.md5(content.encode("utf-8")).hexdigest()


class KnowledgeBaseQdrantStore(KnowledgeBaseStore):
    """Qdrant Knowledge Base Store Implementation

    基於 LlamaIndex 和 Qdrant 的知識庫實現。
    支援 Google GenAI embeddings 和語義切分處理。
    """

    def __init__(
        self,
        file_source_adapter: FileSourceAdapter,
        qdrant_client: QdrantClient,
        qdrant_aclient: AsyncQdrantClient,
        google_api_key: str,
        embedding_model: str = "gemini-embedding-001",
        llm_model: str = "gemini-2.5-flash",
    ):
        """Initialize Qdrant Knowledge Base Store

        Args:
            file_source_adapter: FileSourceAdapter instance
            qdrant_client: Qdrant client instance
            qdrant_client: AsyncQdrant client instance
            google_api_key: Google GenAI API key
            embedding_model: Embedding model name
            llm_model: ReAct Agent 查詢時使用的模型名稱
        """
        super().__init__(file_source_adapter)
        self.qdrant_client = qdrant_client
        self.qdrant_aclient = qdrant_aclient
        self.google_api_key = google_api_key
        self.embedding_model = embedding_model
        self.llm_model = llm_model
        self.collection_name = file_source_adapter.get_collection_name()

        # Cache directory for IngestionPipeline
        cache_base_dir = ".pipeline_cache"
        os.makedirs(cache_base_dir, exist_ok=True)
        self.cache_dir = os.path.join(cache_base_dir, f"storage_{self.collection_name}")

        # Initialize components
        self._setup_embeddings()
        self._setup_llm()
        self._setup_vector_store()
        self._setup_node_parser()

        # Will be set during rebuild
        self.index: Optional[VectorStoreIndex] = None
        self.query_engine: Optional[RetrieverQueryEngine] = None

    def _setup_embeddings(self) -> None:
        """設定 Google GenAI Embeddings"""
        self.embed_model = GoogleGenAIEmbedding(
            model_name=self.embedding_model,
            api_key=self.google_api_key,
            retries=5,
            timeout=30,
            retry_min_seconds=10,
            retry_max_seconds=30,
            retry_exponential_base=2,
        )
        # Set global embedding model
        Settings.embed_model = self.embed_model

    def _setup_llm(self) -> None:
        """設定 Google Gemini MultiModal LLM"""
        self.agent_llm = GoogleGenAI(
            model=self.llm_model, api_key=self.google_api_key  # 使用指定的 Gemini 模型
        )
        # Set global LLM
        Settings.llm = self.agent_llm

    def _setup_vector_store(self) -> None:
        """設定 Qdrant Vector Store with Hybrid Search"""
        self.vector_store = QdrantVectorStore(
            client=self.qdrant_client,
            aclient=self.qdrant_aclient,
            collection_name=self.collection_name,
            enable_hybrid=True,  # 解決向量命名問題
            fastembed_sparse_model="Qdrant/bm25",  # BM25 sparse vectors
            batch_size=20,  # 批次處理優化
        )

    def _setup_node_parser(self) -> None:
        """設定語意切分器"""
        self.node_parser = SemanticSplitterNodeParser(
            buffer_size=1,
            breakpoint_percentile_threshold=95,
            embed_model=self.embed_model,
        )
        # Set global node parser
        Settings.node_parser = self.node_parser

    def create_hybrid_query_engine(
        self, index: VectorStoreIndex
    ) -> RetrieverQueryEngine:
        """建立混合搜尋查詢引擎"""
        return index.as_query_engine(
            vector_store_query_mode="hybrid",
            similarity_top_k=2,  # Dense vector results
            sparse_top_k=12,  # Sparse vector results
            hybrid_top_k=3,  # Final fused results
            response_mode="tree_summarize",
            use_async=True,
        )

    def create_hybrid_agent(
        self, query_engine: RetrieverQueryEngine, system_prompt: Optional[str] = None
    ) -> ReActAgent:
        """建立支援混合搜尋的 ReAct Agent"""
        query_tool = QueryEngineTool.from_defaults(
            query_engine=query_engine,
            name="hybrid_knowledge_base_query",
            description=(
                "Query the knowledge base for relevant information and document content. "
                "Uses hybrid search technology combining semantic understanding and keyword matching "
                "to provide more accurate and comprehensive search results. "
                "Supports Traditional Chinese, Taiwan terminology, and mixed Chinese-English queries."
            ),
        )

        # Default system prompt in English
        default_agent_prompt = """
        - You MUST use English to answer questions.
        - You can only answer questions based on the tool results. If there is no information, respond that there is no information in the knowledge base. You must not answer on your own.
        - Use as much information as possible from the tool results to answer the question.
        """

        # Use provided system_prompt or default
        agent_prompt = (
            system_prompt if system_prompt is not None else default_agent_prompt
        )

        # Create custom formatter with system prompt
        custom_formatter = ReActChatFormatter.from_defaults(context=agent_prompt)

        return ReActAgent(
            tools=[query_tool],
            llm=self.agent_llm,
            formatter=custom_formatter,
        )

    async def refresh_knowledge_base(self) -> None:
        """刷新知識庫

        如果知識庫不存在，會自動建立；如果已存在，會進行更新。
        執行完整的文件處理流程：檔案載入 → 語義切分 → 向量化 → 索引建立
        """
        print(f"🔄 開始刷新知識庫: {self.collection_name}")

        # Step 1: 檔案掃描與載入
        print("📁 掃描檔案...")
        file_paths = await self.file_source_adapter.get_files()

        if not file_paths:
            print(f"❌ 未找到任何檔案，集合: {self.collection_name}")
            return

        print(f"   找到 {len(file_paths)} 個檔案")

        # Step 2: 準備處理（不清空知識庫，由 SimpleDocumentStore 處理重複）
        print("🚀 準備平行處理流程...")

        try:
            # Step 3: 文件載入與處理
            print("📖 載入文件...")
            documents = []
            successful_files = 0
            failed_files = 0

            for file_path in file_paths:
                try:
                    reader = SimpleDirectoryReader(input_files=[file_path])
                    docs = reader.load_data()

                    # Set custom doc_id and add metadata
                    for doc in docs:
                        file_path_meta = doc.metadata.get("file_path", file_path)
                        page_label = doc.metadata.get("page_label", "")

                        # Generate custom doc_id
                        doc.doc_id = generate_document_id(file_path_meta, page_label)

                        # Add basic metadata (remove redundant updates)
                        doc.metadata.update(
                            {
                                "file_path": file_path,
                                "file_name": os.path.basename(file_path),
                                "collection": self.collection_name,
                            }
                        )

                    documents.extend(docs)
                    successful_files += 1

                except Exception as e:
                    import traceback

                    traceback.print_exc()
                    print(f"   ⚠️  載入失敗 {file_path}: {e}")
                    failed_files += 1
                    continue

            if not documents:
                print("❌ 沒有成功載入任何文件")
                return

            print(f"   ✅ 成功載入: {successful_files} 檔案")
            if failed_files > 0:
                print(f"   ⚠️  載入失敗: {failed_files} 檔案")

            # Step 4: 使用 IngestionPipeline 進行批次處理 (含 Cache 機制)
            print("⚡ 使用 IngestionPipeline 進行批次處理...")
            print(f"   📁 Cache 目錄: {self.cache_dir}")

            # 批次處理設定
            BATCH_SIZE = 50
            MAX_RETRIES = 3
            RETRY_DELAY = 60  # seconds

            # Create IngestionPipeline with SimpleDocumentStore for duplicate detection
            pipeline = IngestionPipeline(
                transformations=[
                    self.node_parser,
                    self.embed_model,
                ],
                docstore=SimpleDocumentStore(),
                vector_store=self.vector_store,
            )

            # Load existing cache if available
            if os.path.exists(self.cache_dir):
                print("   📂 載入現有 cache...")
                try:
                    pipeline.load(self.cache_dir)
                    print("   ✅ Cache 載入成功")
                except Exception as e:
                    print(f"   ⚠️  Cache 載入失敗: {e}")
                    print("   🔄 將建立新的 cache")

            # 開始批次處理
            all_nodes = []
            total_batches = (len(documents) + BATCH_SIZE - 1) // BATCH_SIZE

            print(f"   📦 開始批次處理：{len(documents)} 個文件分為 {total_batches} 批")

            # 批次處理循環
            for batch_idx in range(total_batches):
                batch_start = batch_idx * BATCH_SIZE
                batch_end = min(batch_start + BATCH_SIZE, len(documents))
                batch = documents[batch_start:batch_end]

                print(
                    f"   📦 處理批次 {batch_idx + 1}/{total_batches} ({len(batch)} 個文件)"
                )

                # 重試機制
                batch_success = False
                for attempt in range(MAX_RETRIES):
                    try:
                        batch_nodes = pipeline.run(
                            documents=batch,
                            num_workers=1,  # 避免 multiprocessing 問題
                            show_progress=True,
                        )

                        all_nodes.extend(batch_nodes if batch_nodes else [])

                        # 每批處理完立即保存 cache
                        pipeline.persist(self.cache_dir)
                        print(
                            f"   ✅ 批次 {batch_idx + 1} 處理完成 ({len(batch_nodes) if batch_nodes else 0} 個節點)，cache 已保存"
                        )
                        batch_success = True
                        break

                    except Exception as e:
                        if attempt < MAX_RETRIES - 1:
                            print(
                                f"   ⚠️  批次 {batch_idx + 1} 失敗 (嘗試 {attempt + 1}/{MAX_RETRIES}): {e}"
                            )
                            print(f"   😴 等待 {RETRY_DELAY} 秒後重試...")
                            time.sleep(RETRY_DELAY)
                        else:
                            import traceback

                            traceback.print_exc()
                            print(f"   ❌ 批次 {batch_idx + 1} 最終失敗: {e}")
                            # 不立即 raise，繼續處理其他批次，最後統一報告失敗
                            raise e

                if not batch_success:
                    print(f"   ⚠️  跳過失敗的批次 {batch_idx + 1}，繼續處理剩餘批次")

            # 最終結果
            nodes = all_nodes
            print(f"   🎯 批次處理完成：總共處理 {len(nodes)} 個節點")
            # Step 5: 從 vector store 建立索引
            print("🔢 建立向量索引...")
            self.index = VectorStoreIndex.from_vector_store(
                vector_store=self.vector_store,
                embed_model=self.embed_model,
            )

            # Step 6: 驗證 Qdrant Collection 是否建立成功
            print("🔍 驗證 Qdrant Collection...")
            try:
                collections = await self.qdrant_aclient.get_collections()
                collection_names = [col.name for col in collections.collections]

                if self.collection_name not in collection_names:
                    print(f"❌ Qdrant Collection 建立失敗: {self.collection_name}")
                    print("   重建流程中止")
                    return

                # 獲取 collection 資訊確認有資料
                collection_info = await self.qdrant_aclient.get_collection(
                    self.collection_name
                )
                points_count = collection_info.points_count

                if points_count == 0:
                    print(
                        f"⚠️  Qdrant Collection 已建立但無資料: {self.collection_name}"
                    )
                    print("   可能是處理過程中發生問題")
                    return

                print(f"   ✅ Collection 建立成功，向量數量: {points_count}")

            except Exception as e:
                print(f"❌ 驗證 Qdrant Collection 失敗: {e}")
                print("   重建流程中止")
                return

            # Step 7: 建立混合搜尋查詢引擎
            print("🔍 設定混合搜尋引擎...")
            self.query_engine = self.create_hybrid_query_engine(self.index)

            print(f"✅ 知識庫刷新完成！")
            print(f"   處理文件數量: {len(documents)}")
            print(f"   處理節點數量: {len(nodes) if nodes else 0}")
            print(f"   向量數量: {points_count}")
            print(f"   集合名稱: {self.collection_name}")
            print(f"   批次處理: {total_batches} 批次 (每批 {BATCH_SIZE} 個文件)")
            print(f"   重試設定: 最多 {MAX_RETRIES} 次，間隔 {RETRY_DELAY} 秒")
            print(f"   Cache 目錄: {self.cache_dir}")

        except Exception as e:
            import traceback

            traceback.print_exc()
            print(f"❌ 刷新知識庫失敗: {e}")
            raise
        finally:
            # 清理暫存檔案
            self.file_source_adapter.cleanup_temp_files(file_paths)

    async def clear_knowledge_base(self) -> None:
        """清空知識庫

        移除所有向量資料和索引，清空快取，重置知識庫為空白狀態。
        """
        try:
            # Check if collection exists
            collections = await self.qdrant_aclient.get_collections()
            collection_names = [col.name for col in collections.collections]

            if self.collection_name in collection_names:
                # Delete collection from Qdrant
                await self.qdrant_aclient.delete_collection(self.collection_name)
                print(f"   🗑️  已刪除集合: {self.collection_name}")
            else:
                print(f"   ℹ️  集合不存在: {self.collection_name}")

            # Clear cache directory
            if os.path.exists(self.cache_dir):
                shutil.rmtree(self.cache_dir)
                print(f"   🗑️  已清空快取目錄: {self.cache_dir}")
            else:
                print(f"   ℹ️  快取目錄不存在: {self.cache_dir}")

            # Reset index and query engine
            self.index = None
            self.query_engine = None

            print(f"   ✅ 知識庫已清空")

        except Exception as e:
            print(f"   ❌ 清空知識庫失敗: {e}")
            raise

    async def query_knowledge_base(self, query: str, system_prompt: Optional[str] = None) -> str:
        """查詢知識庫

        使用 ReAct Agent 查詢相關文件片段，針對繁體中文和台灣用語優化。

        Args:
            query: 查詢字串（支援繁體中文和中英混合）
            system_prompt: 系統提示詞（可選）

        Returns:
            str: 查詢結果回應
        """
        if not self.query_engine:
            raise RuntimeError("知識庫尚未初始化，請先執行刷新")

        try:
            print(f"🤖 使用混合搜尋 ReAct Agent 查詢: {query}")

            # response = await self.query_engine.aquery(query)
            # print("📖 Query Engine Response: ")
            # print("-" * 50)
            # print(response)
            # Create hybrid agent
            agent = self.create_hybrid_agent(self.query_engine, system_prompt)

            # Create context for this session
            ctx = Context(agent)

            # Process query with agent and stream the thinking process
            print(f"🧠 Agent 思考過程：")
            print("-" * 50)

            handler = agent.run(query, ctx=ctx)

            # Stream the events to show thinking process
            async for ev in handler.stream_events():
                if isinstance(ev, ToolCallResult):
                    print(f"🔧 調用工具: {ev.tool_name}")
                    print(f"   參數: {ev.tool_kwargs}")
                    print(f"   結果: {str(ev.tool_output)[:200]}...")
                    for source_node in ev.tool_output.raw_output.source_nodes:
                        print(f"     -- 參考來源 node id: {source_node.node_id}")
                        print(f"     -- 參考來源 node 分數: {source_node.score}")
                        print(f"     -- 參考來源 node 內容: {source_node.text}")
                    print()
                elif isinstance(ev, AgentStream):
                    print(ev.delta, end="", flush=True)
                # else:
                #     print(ev)

            # Get final response
            response = await handler
            result = str(response)

            print()
            print("-" * 50)
            print(f"   ✅ Agent 查詢完成")
            return result

        except Exception as e:
            print(f"   ❌ 查詢失敗: {e}")
            raise

    async def load_from_existing_collection(self) -> None:
        """從現有 Qdrant collection 載入知識庫索引"""

        print(f"📥 載入現有知識庫索引: {self.collection_name}")

        try:
            # Phase 1: Collection Validation
            await self._validate_existing_collection()

            # Phase 2: Index Creation from Existing Vectors
            self._create_index_from_existing_vectors()

            # Phase 3: Query Engine Initialization
            self._initialize_query_components()

            # Phase 4: Success Confirmation
            await self._confirm_load_success()

        except Exception as e:
            print(f"❌ 載入失敗: {e}")
            # Reset to safe state
            self.index = None
            self.query_engine = None
            raise

    async def _validate_existing_collection(self) -> None:
        """驗證現有 collection 的存在性和相容性"""

        # Check collection existence
        collections = await self.qdrant_aclient.get_collections()
        collection_names = [col.name for col in collections.collections]

        if self.collection_name not in collection_names:
            raise RuntimeError(f"Collection 不存在: {self.collection_name}")

        # Get collection info
        collection_info = await self.qdrant_aclient.get_collection(self.collection_name)

        # Validate vector configuration
        vector_config = collection_info.config.params.vectors

        if isinstance(vector_config, dict):
            # Dense vector validation
            if "dense" in vector_config:
                dense_size = vector_config["dense"].size
                expected_size = 3072  # gemini-embedding-001 dimension

                if dense_size != expected_size:
                    raise ValueError(
                        f"向量維度不符: 期望 {expected_size}, 實際 {dense_size}"
                    )

        print(f"   ✅ Collection 驗證通過")

    def _create_index_from_existing_vectors(self) -> None:
        """從現有向量建立 VectorStoreIndex（優化版本）"""

        print("🔢 從現有向量建立索引...")

        # Create index from existing vector store with optimizations
        self.index = VectorStoreIndex.from_vector_store(
            vector_store=self.vector_store,
            embed_model=self.embed_model,
            show_progress=False,  # 載入模式不需要進度顯示
            use_async=False,  # Sync for faster small operations
        )

        print(f"   ✅ 索引建立完成")

    def _initialize_query_components(self) -> None:
        """初始化查詢引擎組件"""

        print("🔍 設定查詢引擎...")

        # Create hybrid query engine with same config as rebuild mode
        self.query_engine = self.create_hybrid_query_engine(self.index)

        print(f"   ✅ 查詢引擎設定完成")

    async def _confirm_load_success(self) -> None:
        """確認載入成功並顯示狀態資訊"""

        # Get collection statistics
        collection_info = await self.qdrant_aclient.get_collection(self.collection_name)

        points_count = collection_info.points_count

        print(f"✅ 知識庫載入完成！")
        print(f"   Collection: {self.collection_name}")
        print(f"   向量數量: {points_count}")
        print(f"   查詢模式: Hybrid Search (Dense + Sparse)")
