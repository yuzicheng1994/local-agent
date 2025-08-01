import os
from typing import List

from langchain_community.tools import DuckDuckGoSearchResults
from langchain_core.prompts import ChatPromptTemplate
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.prebuilt import create_react_agent

from config import settings
from service.vector_store_service import VectorStoreService
from tools import KnowledgeBaseTool


class AgentService:
    """Agent服务类"""

    def __init__(self, checkpointer: AsyncPostgresSaver, vector_store_service: VectorStoreService):
        self.checkpointer = checkpointer
        self.vector_store_service = vector_store_service
        self.model = None
        self.tools = None
        self.agent_executor = None

    async def initialize(self):
        """初始化Agent服务"""
        # 初始化LLM模型
        self.model = ChatOpenAI(
            model=settings.llm_model,
            base_url=settings.llm_base_url,
            api_key=settings.llm_api_key,
            # 启用LangSmith追踪的标签
            tags=["langchain-agent", "chat"]
        )

        # 初始化工具
        await self._initialize_tools()

        # 创建Agent
        self._create_agent()

    async def _initialize_tools(self):
        """初始化工具列表"""
        # MCP客户端工具
        current_dir = os.getcwd()
        client = MultiServerMCPClient({
            "fetch": {
                "command": "uvx",
                "args": ["mcp-server-fetch"],
                "transport": "stdio"
            },
            "file_system": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-filesystem", current_dir],
                "transport": "stdio"
            }
        })
        mcp_tools = await client.get_tools()

        # 知识库工具
        knowledge_tool = KnowledgeBaseTool(
            self.vector_store_service.get_vector_store()
        )

        # 组合所有工具
        self.tools = [
                         DuckDuckGoSearchResults(),
                         knowledge_tool.knowledge_base_retriever
                     ] + mcp_tools

    def _create_agent(self):
        """创建Agent执行器"""
        system_prompt = """
        # 角色
        你是一个聪明的小助手，请始终使用中文回答用户的问题

        # 工具
        你拥有以下工具：
        - 知识库：可以搜索知识库中的信息
        - 文件系统：可以访问当前目录下的文件
        - 网页浏览：可以浏览网页
        - 网络搜索：可以搜索网络上的信息
        """

        prompt = ChatPromptTemplate([
            ("system", system_prompt.strip()),
            ("placeholder", "{messages}")
        ])

        self.agent_executor = create_react_agent(
            self.model,
            self.tools,
            checkpointer=self.checkpointer,
            prompt=prompt
        )

    def get_agent_executor(self):
        """获取Agent执行器"""
        if not self.agent_executor:
            raise RuntimeError("Agent未初始化")
        return self.agent_executor

    def get_tools(self) -> List:
        """获取工具列表"""
        if not self.tools:
            raise RuntimeError("工具未初始化")
        return self.tools
