import chromadb
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma

from config import settings


class VectorStoreService:
    """向量存储服务类"""

    def __init__(self):
        self.embeddings = None
        self.chroma_client = None
        self.vector_store = None

    async def initialize(self):
        """初始化向量存储"""
        self.embeddings = OllamaEmbeddings(
            model=settings.embedding_model
        )

        self.chroma_client = chromadb.HttpClient(
            host=settings.chroma_host,
            port=settings.chroma_port
        )

        self.vector_store = Chroma(
            client=self.chroma_client,
            collection_name=settings.collection_name,
            embedding_function=self.embeddings,
        )

    def get_vector_store(self) -> Chroma:
        """获取向量存储实例"""
        if not self.vector_store:
            raise RuntimeError("向量存储未初始化")
        return self.vector_store
