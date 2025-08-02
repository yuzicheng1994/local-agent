import os

import chromadb
from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()


def create_vector_store():
    # 加载文档、进行切分、创建向量嵌入，并将其持久化存储到 ChromaDB。
    print("正在从 './knowledge_base' 文件夹加载文档...")

    # 匹配.txt .pdf .docx .doc文件
    loader = DirectoryLoader(
        './knowledge_base/',
        glob="**/*[.txt,.pdf,.docx,.doc]",
        show_progress=True,
        use_multithreading=True
    )
    documents = loader.load()

    # 如果没有载入任何文档，就提前结束
    if not documents:
        print("未找到任何文档，请检查 'knowledge_base' 文件夹。")
        return

    print(f"已载入 {len(documents)} 份文档。正在将文档切分为小块...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(documents)

    print(f"已切分为 {len(chunks)} 个小块。正在创建并存储到 ChromaDB...")
    embeddings = OllamaEmbeddings(
        model=os.getenv("EMBEDDING_MODEL")
    )

    # 初始化chroma客户端
    client = chromadb.HttpClient(host=os.getenv("CHROMA_HOST"), port=int(os.getenv("CHROMA_PORT")))

    # 文档列表创建新的Chroma向量存储实例
    _ = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        client=client,
        collection_name=os.getenv("COLLECTION_NAME", "agent_knowledge_base")
    )

    print("文件已成功创建并保存至ChromaDB!")


if __name__ == "__main__":
    create_vector_store()
