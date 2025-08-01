from langchain.tools import tool
from langchain_community.vectorstores import Chroma


class KnowledgeBaseTool:
    """知识库工具类"""

    def __init__(self, vector_store: Chroma):
        self.vector_store = vector_store

    @tool
    def knowledge_base_retriever(self, query: str) -> str:
        """在知识库中搜索信息"""
        retrieved_docs = self.vector_store.similarity_search(query, k=3)

        if not retrieved_docs:
            return "在知识库中没有找到相关信息。"

        serialized = "\n\n".join(
            (f"来源: {doc.metadata}\n内容: {doc.page_content}")
            for doc in retrieved_docs
        )

        return serialized
