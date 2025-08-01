from contextlib import asynccontextmanager

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from psycopg_pool import AsyncConnectionPool

from config import settings
from service import AgentService, ChatService, VectorStoreService


class ApplicationState:
    """应用状态管理类"""

    def __init__(self):
        self.vector_store_service = None
        self.agent_service = None
        self.chat_service = None
        self.checkpointer = None


@asynccontextmanager
async def lifespan(app):
    """应用生命周期管理"""
    # 初始化阶段
    connection_kwargs = {
        "autocommit": True,
        "prepare_threshold": 0,
    }

    async with AsyncConnectionPool(settings.db_uri, kwargs=connection_kwargs) as pool:
        # 创建checkpointer
        checkpointer = AsyncPostgresSaver(pool)
        await checkpointer.setup()

        # 初始化服务
        vector_store_service = VectorStoreService()
        await vector_store_service.initialize()

        agent_service = AgentService(checkpointer, vector_store_service)
        await agent_service.initialize()

        chat_service = ChatService(agent_service, checkpointer)

        # 保存到应用状态
        app.state.vector_store_service = vector_store_service
        app.state.agent_service = agent_service
        app.state.chat_service = chat_service
        app.state.checkpointer = checkpointer

        yield

        # 清理阶段（连接池会自动关闭）
