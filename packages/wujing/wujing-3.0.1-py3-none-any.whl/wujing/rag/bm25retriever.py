import json
import logging
import os
from typing import Any, Dict, List, Optional

from llama_index.core import QueryBundle
from llama_index.core.constants import DEFAULT_SIMILARITY_TOP_K
from llama_index.core.retrievers import BaseRetriever
from llama_index.core.schema import BaseNode, NodeWithScore, TextNode

from wujing.rag.duckdb_fts import DuckDBFTSDatabase, Document
from wujing.rag.tokenizer import ChineseTokenizer
from wujing.rag.stemmer import MixedLanguageStemmer


logger = logging.getLogger(__name__)

DEFAULT_PERSIST_FILENAME = "retriever.json"


class BM25Retriever(BaseRetriever):
    """增强的 BM25 检索器，基于 DuckDB FTS 内建的 BM25 算法

    这个检索器使用 DuckDB FTS 的内建 BM25 算法进行文档检索，
    充分利用 DuckDBFTSDatabase 的功能，包括高级中英文分词和词干提取。

    Args:
        nodes (List[BaseNode], optional):
            要索引的节点。如果未提供，将从现有数据库加载。
        tokenizer (ChineseTokenizer, optional):
            自定义分词器。默认使用 ChineseTokenizer。
        stemmer (MixedLanguageStemmer, optional):
            词干提取器。默认创建新的实例。
        duckdb_path (str, optional):
            DuckDB 数据库路径。默认为 ".diskcache/bm25.duckdb"。
        table_name (str, optional):
            数据库表名。默认为 "documents"。
        similarity_top_k (int, optional):
            返回结果数量。默认为 DEFAULT_SIMILARITY_TOP_K。
        use_stemming (bool, optional):
            是否使用词干提取。默认为 True。
        verbose (bool, optional):
            是否显示进度。默认为 False。
    """

    def __init__(
        self,
        nodes: Optional[List[BaseNode]] = None,
        tokenizer: Optional[ChineseTokenizer] = None,
        stemmer: Optional[MixedLanguageStemmer] = None,
        duckdb_path: str = ".diskcache/bm25retriever.duckdb",
        table_name: str = "documents",
        similarity_top_k: int = DEFAULT_SIMILARITY_TOP_K,
        use_stemming: bool = True,
        verbose: bool = False,
    ) -> None:
        self.duckdb_path = duckdb_path
        self.table_name = table_name
        self.similarity_top_k = similarity_top_k
        self.use_stemming = use_stemming
        self._verbose = verbose

        self.database = DuckDBFTSDatabase(
            db_file=duckdb_path,
            table_name=table_name,
            top_k=similarity_top_k,
            tokenizer=tokenizer,
            stemmer=stemmer,
            use_stemming=use_stemming,
        )

        # 如果提供了节点，则初始化数据库
        if nodes is not None:
            self._setup_database_with_nodes(nodes)

        super().__init__(verbose=verbose)

    def _setup_database_with_nodes(self, nodes: List[BaseNode]) -> None:
        """使用节点设置 DuckDB FTS 数据库，将节点转换为 Document 对象"""
        try:
            documents = []
            for i, node in enumerate(nodes):
                text = node.get_content()

                metadata = {"node_id": node.node_id or str(i), "node_index": str(i)}

                if hasattr(node, "metadata") and node.metadata:
                    for key, value in node.metadata.items():
                        metadata[f"node_{key}"] = str(value)

                documents.append(Document(text=text, metadata=metadata))

            self.database.initialize(documents)

            logger.info(f"成功初始化包含 {len(nodes)} 个节点的 DuckDB BM25 索引")
        except Exception as e:
            logger.error(f"DuckDB BM25 数据库初始化失败: {e}")
            raise

    @classmethod
    def from_defaults(
        cls,
        nodes: List[BaseNode],
        tokenizer: Optional[ChineseTokenizer] = None,
        stemmer: Optional[MixedLanguageStemmer] = None,
        duckdb_path: str = ".diskcache/bm25.duckdb",
        table_name: str = "documents",
        similarity_top_k: int = DEFAULT_SIMILARITY_TOP_K,
        use_stemming: bool = True,
        verbose: bool = False,
    ) -> "BM25Retriever":
        """从默认参数创建增强 BM25 检索器"""
        return cls(
            nodes=nodes,
            tokenizer=tokenizer,
            stemmer=stemmer,
            duckdb_path=duckdb_path,
            table_name=table_name,
            similarity_top_k=similarity_top_k,
            use_stemming=use_stemming,
            verbose=verbose,
        )

    @classmethod
    def from_documents(
        cls,
        documents: List[str],
        similarity_top_k: int = DEFAULT_SIMILARITY_TOP_K,
        use_stemming: bool = True,
        verbose: bool = False,
    ) -> "BM25Retriever":
        """从文档字符串列表创建增强 BM25 检索器"""
        nodes = [TextNode(text=doc) for doc in documents]
        return cls.from_defaults(
            nodes=nodes,
            similarity_top_k=similarity_top_k,
            use_stemming=use_stemming,
            verbose=verbose,
        )

    def get_persist_args(self) -> Dict[str, Any]:
        """获取持久化参数字典"""
        return {
            "similarity_top_k": self.similarity_top_k,
            "use_stemming": self.use_stemming,
            "duckdb_path": self.duckdb_path,
            "table_name": self.table_name,
            "_verbose": getattr(self, "_verbose", False),
        }

    def persist(self, path: str, **kwargs: Any) -> None:
        """持久化检索器到目录"""
        os.makedirs(path, exist_ok=True)

        with open(os.path.join(path, DEFAULT_PERSIST_FILENAME), "w", encoding="utf-8") as f:
            json.dump(self.get_persist_args(), f, indent=2, ensure_ascii=False)

        logger.info(f"检索器已持久化到: {path}")
        logger.info("注意：节点元信息已存储在 DuckDB 数据库中，无需单独保存")

    @classmethod
    def from_persist_dir(cls, path: str, **kwargs: Any) -> "BM25Retriever":
        """从目录加载检索器"""
        config_path = os.path.join(path, DEFAULT_PERSIST_FILENAME)
        if os.path.exists(config_path):
            with open(config_path, encoding="utf-8") as f:
                retriever_data = json.load(f)
        else:
            retriever_data = {}

        if "_verbose" in retriever_data:
            retriever_data["verbose"] = retriever_data.pop("_verbose")

        instance = cls(**retriever_data)

        logger.info("检索器已从持久化目录加载")
        logger.info("注意：节点元信息将从 DuckDB 数据库中动态加载")
        return instance

    def _retrieve(self, query_bundle: QueryBundle) -> List[NodeWithScore]:
        """执行 DuckDB BM25 检索，将检索结果转换为 NodeWithScore"""
        if not query_bundle.query_str.strip():
            logger.warning("查询字符串为空")
            return []

        try:
            document_results = self.database.retrieve(query_bundle.query_str)

            node_results = []
            for doc_result in document_results:
                document = doc_result["document"]
                score = doc_result["score"]

                node_id = document.metadata.get("node_id", "")

                text_node = TextNode(text=document.text, id_=node_id)

                node_metadata = {}
                for key, value in document.metadata.items():
                    if key.startswith("node_") and key not in ["node_id", "node_index"]:
                        original_key = key[5:]  # 移除 "node_" 前缀
                        node_metadata[original_key] = value

                if node_metadata:
                    text_node.metadata = node_metadata

                node_results.append(NodeWithScore(node=text_node, score=score))

            logger.info(f"DuckDB BM25 检索返回 {len(node_results)} 个结果")
            return node_results

        except Exception as e:
            logger.error(f"DuckDB BM25 检索失败: {e}")
            return []

    def clear_cache(self) -> None:
        """清空缓存"""
        if hasattr(self.database, "_tokenize_query") and hasattr(self.database._tokenize_query, "cache_clear"):
            self.database._tokenize_query.cache_clear()

        if self.database.tokenizer and hasattr(self.database.tokenizer, "clear_cache"):
            self.database.tokenizer.clear_cache()
        if self.database.stemmer and hasattr(self.database.stemmer, "clear_cache"):
            self.database.stemmer.clear_cache()

        logger.info("所有缓存已清空")

    def get_stats(self) -> Dict[str, Any]:
        """获取检索器统计信息"""
        stats = {
            "similarity_top_k": self.similarity_top_k,
            "use_stemming": self.use_stemming,
            "duckdb_path": self.duckdb_path,
            "table_name": self.table_name,
            "corpus_size": "存储在数据库中",
        }

        if self.database.tokenizer and hasattr(self.database.tokenizer, "get_stats"):
            stats["tokenizer_stats"] = self.database.tokenizer.get_stats()

        if self.database.stemmer and hasattr(self.database.stemmer, "get_cache_info"):
            stats["stemmer_cache"] = self.database.stemmer.get_cache_info()

        return stats

    def update_processors(
        self,
        tokenizer: Optional[ChineseTokenizer] = None,
        stemmer: Optional[MixedLanguageStemmer] = None,
        use_stemming: Optional[bool] = None,
    ) -> None:
        """更新分词器和词干提取器"""
        self.database.update_processors(
            tokenizer=tokenizer,
            stemmer=stemmer,
            use_stemming=use_stemming,
        )

        if use_stemming is not None:
            self.use_stemming = use_stemming

        logger.info("已更新处理器")

    def close(self) -> None:
        """关闭数据库连接"""
        if self.database:
            self.database.close()

    def __enter__(self) -> "BM25Retriever":
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """上下文管理器出口"""
        self.close()


def main():
    """主函数 - 演示增强BM25检索器的使用（基于 DuckDBFTSDatabase）"""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    documents = [
        "马斯克是特斯拉的首席执行官，该公司是电动汽车领域的领导者。",
        "他也是 SpaceX 的创始人和首席执行官，这是一家致力于太空探索的公司。",
        "此外，马斯克还参与了 Neuralink 和 The Boring Company 等项目。",
        "特斯拉不仅生产电动汽车，还涉足太阳能和储能解决方案。",
        "SpaceX 已经成功进行了多次火箭发射和回收，降低了太空探索的成本。",
        "Neuralink 旨在开发脑机接口技术，帮助治疗神经系统疾病。",
        "The Tesla Model S is an electric luxury sedan with impressive performance.",
        "SpaceX Falcon 9 rockets are designed for reliable and safe transport of satellites.",
        "Neuralink aims to create brain-computer interfaces for medical applications.",
    ]

    print("=== 增强BM25检索器演示（基于 DuckDBFTSDatabase）===")

    with BM25Retriever.from_documents(
        documents=documents,
        similarity_top_k=3,
        use_stemming=True,
        verbose=True,
    ) as retriever:
        print("\n=== 检索器统计信息 ===")
        stats = retriever.get_stats()
        for key, value in stats.items():
            print(f"{key}: {value}")
        print("-" * 70)

        queries = [
            "谁是特斯拉的CEO？",
            "SpaceX是做什么的？",
            "Neuralink的目标是什么？",
            "electric vehicles Tesla",
            "brain computer interface technology",
        ]

        for query in queries:
            print(f"\n查询: {query}")
            print("-" * 50)

            result = retriever.retrieve(QueryBundle(query_str=query))

            if result:
                for i, node_with_score in enumerate(result, 1):
                    print(f"{i}. 文档内容: {node_with_score.node.get_content()}")
                    print(f"   BM25 相关性分数: {node_with_score.score:.4f}")
            else:
                print("没有找到相关文档")
            print()

        persist_dir = "generated/bm25"
        print(f"\n=== 持久化检索器到: {persist_dir} ===")
        retriever.persist(persist_dir)

        print("\n=== 更新处理器演示 ===")
        new_tokenizer = ChineseTokenizer(min_token_length=1)
        retriever.update_processors(tokenizer=new_tokenizer, use_stemming=False)

        test_query = "马斯克CEO"
        print(f"更新处理器后查询: {test_query}")
        updated_result = retriever.retrieve(QueryBundle(query_str=test_query))

        print("更新处理器后的结果:")
        for i, node_with_score in enumerate(updated_result, 1):
            print(f"{i}. 文档内容: {node_with_score.node.get_content()}")
            print(f"   BM25 相关性分数: {node_with_score.score:.4f}")

        print("\n=== 缓存清理演示 ===")
        retriever.clear_cache()

        print("\n=== 性能对比测试 ===")
        import time

        test_query = "马斯克CEO特斯拉"

        start_time = time.time()
        result = retriever.retrieve(QueryBundle(query_str=test_query))
        end_time = time.time()

        print(f"DuckDB BM25 检索耗时: {(end_time - start_time) * 1000:.2f}ms")
        print(f"检索结果数量: {len(result)}")

    print("\n=== 从持久化目录加载检索器 ===")
    with BM25Retriever.from_persist_dir(persist_dir) as loaded_retriever:
        # 验证加载的检索器
        test_query = "特斯拉电动汽车"
        print(f"验证查询: {test_query}")
        loaded_result = loaded_retriever.retrieve(QueryBundle(query_str=test_query))

        print("验证加载的检索器结果:")
        for i, node_with_score in enumerate(loaded_result, 1):
            print(f"{i}. 文档内容: {node_with_score.node.get_content()}")
            print(f"   BM25 相关性分数: {node_with_score.score:.4f}")


if __name__ == "__main__":
    main()
    main()
