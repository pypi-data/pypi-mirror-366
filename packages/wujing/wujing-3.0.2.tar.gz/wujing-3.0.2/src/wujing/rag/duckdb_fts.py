import json
import logging
import os
import hashlib
from contextlib import contextmanager
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Dict, List, Optional, Self, Union, Annotated

from pydantic import validate_call, Field
from sqlalchemy import Engine, create_engine, text
from wujing.rag.tokenizer import ChineseTokenizer
from wujing.rag.stemmer import MixedLanguageStemmer

logger = logging.getLogger(__name__)


@dataclass
class Document:
    text: str
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        if not isinstance(self.text, str):
            raise TypeError("text must be a string")
        if not isinstance(self.metadata, dict):
            raise TypeError("metadata must be a dictionary")

    def to_dict(self) -> Dict[str, Union[str, Dict[str, str]]]:
        return {
            "text": self.text,
            "metadata": self.metadata,
        }


class DuckDBFTSDatabase:
    @validate_call(config=dict(arbitrary_types_allowed=True, validate_assignment=False))
    def __init__(
        self,
        db_file: str = ".diskcache/duckdb_fts.db",
        table_name: str = "documents",
        top_k: Annotated[int, Field(gt=0)] = 2,
        tokenizer: Optional[ChineseTokenizer] = None,
        stemmer: Optional[MixedLanguageStemmer] = None,
        use_stemming: bool = True,
    ):
        self.db_file = db_file
        self.table_name = table_name
        self.top_k = top_k
        self.use_stemming = use_stemming

        self.tokenizer = tokenizer if tokenizer is not None else ChineseTokenizer()
        self.stemmer = (
            stemmer
            if stemmer is not None
            else MixedLanguageStemmer(algorithm="porter", min_word_length=2)
            if use_stemming
            else None
        )

        self._engine: Optional[Engine] = None
        self._fts_setup_done = False

    def _process_text(self, text: str) -> List[str]:
        """处理文本：分词和可选的词干提取"""
        tokens = self.tokenizer.tokenize(text)
        if self.use_stemming and self.stemmer is not None:
            tokens = self.stemmer.stem_words(tokens)

        return tokens

    def _generate_document_id(self, document: Document) -> str:
        """为文档生成唯一标识符，基于文本内容和元数据的哈希值"""
        content = f"{document.text}|{json.dumps(document.metadata, sort_keys=True, ensure_ascii=False)}"
        return hashlib.md5(content.encode("utf-8")).hexdigest()

    @property
    def engine(self) -> Engine:
        if self._engine is None:
            os.makedirs(os.path.dirname(self.db_file), exist_ok=True)
            self._engine = create_engine(f"duckdb:///{self.db_file}")
        return self._engine

    @contextmanager
    def get_connection(self):
        conn = self.engine.connect()
        try:
            if not self._fts_setup_done:
                conn.execute(text("INSTALL fts;"))
                conn.execute(text("LOAD fts;"))
                self._fts_setup_done = True
            yield conn
        except Exception as e:
            logger.error(f"数据库操作失败: {e}")
            raise
        finally:
            conn.close()

    def _reset_and_setup_database(self) -> None:
        """重置并设置数据库"""
        try:
            if self._engine:
                self._engine.dispose()
                self._engine = None

            if os.path.exists(self.db_file):
                os.remove(self.db_file)
                logger.info(f"已删除数据库文件: {self.db_file}")

            self._fts_setup_done = False

            with self.get_connection() as conn:
                create_table_sql = f"""
                    CREATE TABLE IF NOT EXISTS {self.table_name} (
                        id TEXT PRIMARY KEY,
                        original_text TEXT NOT NULL,
                        tokenized_text TEXT NOT NULL,
                        metadata TEXT  -- Document 的元数据，JSON 格式
                    );
                """
                conn.execute(text(create_table_sql))
                conn.commit()
                logger.info(f"数据库表 {self.table_name} 创建成功")
        except Exception as e:
            logger.error(f"重置和设置数据库失败: {e}")
            raise

    @validate_call(config=dict(arbitrary_types_allowed=True, validate_assignment=False))
    def insert_data(self, data: list[Document], batch_size: int = 1000) -> None:
        """插入 Document 对象到数据库"""
        if not data:
            logger.warning("没有数据需要插入")
            return

        logger.info(f"开始批量插入 {len(data)} 个文档...")

        try:
            with self.get_connection() as conn:
                trans = conn.begin()

                try:
                    processed_data = []

                    for i, document in enumerate(data):
                        if not document.text.strip():
                            logger.warning(f"文档 {i} 文本内容为空，跳过")
                            continue

                        doc_id = self._generate_document_id(document)
                        processed_tokens = self._process_text(document.text)
                        tokenized_text = " ".join(processed_tokens)
                        metadata_json = json.dumps(document.metadata, ensure_ascii=False) if document.metadata else None

                        processed_data.append(
                            {
                                "id": doc_id,
                                "original_text": document.text,
                                "tokenized_text": tokenized_text,
                                "metadata": metadata_json,
                            }
                        )

                    # 使用 INSERT OR REPLACE 来实现幂等性
                    insert_sql = text(f"""
                        INSERT OR REPLACE INTO {self.table_name} (id, original_text, tokenized_text, metadata) 
                        VALUES (:id, :original_text, :tokenized_text, :metadata)
                    """)

                    for i in range(0, len(processed_data), batch_size):
                        batch = processed_data[i : i + batch_size]
                        conn.execute(insert_sql, batch)

                        if i + batch_size < len(processed_data):
                            logger.info(f"已处理 {i + len(batch)}/{len(data)} 个文档")

                    fts_index_sql = text(f"PRAGMA create_fts_index('{self.table_name}', 'id', 'tokenized_text');")
                    conn.execute(fts_index_sql)

                    trans.commit()
                    logger.info(f"成功插入 {len(processed_data)} 个文档并创建 FTS 索引")

                except Exception as e:
                    trans.rollback()
                    logger.error(f"插入文档失败，已回滚: {e}")
                    raise

        except Exception as e:
            logger.error(f"数据库操作失败: {e}")
            raise

    @validate_call(config=dict(arbitrary_types_allowed=True, validate_assignment=False))
    def initialize(self, documents: List[Document]) -> Self:
        """完整初始化数据库：重置、设置、插入文档数据"""
        try:
            logger.info("开始初始化数据库...")
            self._reset_and_setup_database()
            self.insert_data(documents)
            logger.info("数据库初始化完成")
            return self
        except Exception as e:
            logger.error(f"数据库初始化失败: {e}")
            raise

    def close(self) -> None:
        """关闭数据库连接"""
        try:
            if self._engine:
                self._engine.dispose()
                self._engine = None
                logger.info("数据库连接已关闭")
        except Exception as e:
            logger.error(f"关闭数据库连接失败: {e}")

    def __enter__(self) -> Self:
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """上下文管理器出口"""
        self.close()

    @lru_cache(maxsize=256)
    def _tokenize_query(self, query: str) -> str:
        """缓存查询分词结果"""
        processed_tokens = self._process_text(query)
        return " ".join(processed_tokens)

    @validate_call(config=dict(arbitrary_types_allowed=True, validate_assignment=False))
    def retrieve(self, query: str) -> List[Dict]:
        """执行 FTS 检索"""
        if not query.strip():
            logger.warning("查询字符串为空")
            return []

        try:
            tokenized_query = self._tokenize_query(query)

            if not tokenized_query.strip():
                logger.warning("分词后查询为空")
                return []

            with self.get_connection() as conn:
                fts_query = text(f"""
                    SELECT 
                        d.original_text,
                        d.metadata,
                        fts_scores.score
                    FROM (
                        SELECT 
                            id,
                            fts_main_{self.table_name}.match_bm25(id, :tokenized_query) AS score
                        FROM {self.table_name}
                        WHERE fts_main_{self.table_name}.match_bm25(id, :tokenized_query) IS NOT NULL
                        ORDER BY score DESC
                        LIMIT :top_k
                    ) AS fts_scores
                    INNER JOIN {self.table_name} d ON fts_scores.id = d.id
                    ORDER BY fts_scores.score DESC;
                """)

                results = conn.execute(fts_query, {"tokenized_query": tokenized_query, "top_k": self.top_k}).fetchall()

                logger.info(f"FTS 检索返回 {len(results)} 个结果")

            document_results = []
            for original_text, metadata_json, score in results:
                metadata = json.loads(metadata_json) if metadata_json else {}
                document = Document(text=original_text, metadata=metadata)
                document_results.append({"document": document, "score": float(score)})

            return document_results

        except Exception as e:
            logger.error(f"FTS 检索失败: {e}")
            return []

    def update_processors(
        self,
        tokenizer: Optional[ChineseTokenizer] = None,
        stemmer: Optional[MixedLanguageStemmer] = None,
        use_stemming: Optional[bool] = None,
    ) -> None:
        """更新分词器和词干提取器并清除相关缓存"""
        if tokenizer is not None:
            self.tokenizer = tokenizer
        if stemmer is not None:
            self.stemmer = stemmer
        if use_stemming is not None:
            self.use_stemming = use_stemming
            if not use_stemming:
                self.stemmer = None

        self._tokenize_query.cache_clear()
        logger.info("已更新处理器并清除缓存")


def main():
    """主函数 - 使用 Document 对象和自定义分词器、词干提取器"""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    # 创建 Document 对象
    documents = [
        Document("马斯克是特斯拉的首席执行官，该公司是电动汽车领域的领导者。", {"topic": "Tesla", "person": "马斯克"}),
        Document(
            "他也是 SpaceX 的创始人和首席执行官，这是一家致力于太空探索的公司。",
            {"topic": "SpaceX", "person": "马斯克"},
        ),
        Document(
            "此外，马斯克还参与了 Neuralink 和 The Boring Company 等项目。", {"topic": "其他项目", "person": "马斯克"}
        ),
        Document("特斯拉不仅生产电动汽车，还涉足太阳能和储能解决方案。", {"topic": "Tesla", "business": "能源"}),
        Document("SpaceX 成功实现了火箭的可重复使用，大大降低了发射成本。", {"topic": "SpaceX", "technology": "火箭"}),
        Document(
            "Neuralink 致力于开发脑机接口技术，可能革命性地改变医疗行业。",
            {"topic": "Neuralink", "technology": "脑机接口"},
        ),
    ]

    try:
        # 创建自定义分词器和词干提取器
        custom_tokenizer = ChineseTokenizer(min_token_length=2)
        custom_stemmer = MixedLanguageStemmer(algorithm="porter", min_word_length=2)

        with DuckDBFTSDatabase(
            db_file="generated/docs.duckdb",
            table_name="documents",
            top_k=3,
            tokenizer=custom_tokenizer,
            stemmer=custom_stemmer,
            use_stemming=True,
        ) as database:
            database.initialize(documents)

            queries = ["谁是特斯拉的CEO？", "SpaceX是做什么的？", "马斯克参与了哪些项目？"]

            for query in queries:
                logger.info(f"\n查询: {query}")
                result = database.retrieve(query)

                if result:
                    for i, doc_with_score in enumerate(result, 1):
                        document = doc_with_score["document"]
                        print(f"{i}. 文档内容: {document.text}")
                        print(f"   元数据: {document.metadata}")
                        print(f"   相关性分数 (BM25): {doc_with_score['score']:.4f}")
                else:
                    print("没有找到相关文档")
                print("-" * 50)

    except Exception as e:
        logger.error(f"程序执行失败: {e}")
        raise


if __name__ == "__main__":
    main()
