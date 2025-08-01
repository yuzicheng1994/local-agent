from exception import AgentNotInitializedException, VectorStoreNotInitializedException
from service import AgentService, ChatService


def get_chat_service(request) -> ChatService:
    """获取聊天服务依赖"""
    if not hasattr(request.app.state, 'chat_service') or not request.app.state.chat_service:
        raise AgentNotInitializedException()
    return request.app.state.chat_service


def get_agent_service(request) -> AgentService:
    """获取Agent服务依赖"""
    if not hasattr(request.app.state, 'agent_service') or not request.app.state.agent_service:
        raise VectorStoreNotInitializedException()
    return request.app.state.agent_service
