from typing import Any, AsyncGenerator, Dict, List

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from models import ChatHistoryResponse, ChatRequest, ChatResponse
from service.agent_service import AgentService


class ChatService:
    """聊天服务类"""

    def __init__(self, agent_service: AgentService, checkpointer: AsyncPostgresSaver):
        self.agent_service = agent_service
        self.checkpointer = checkpointer

    async def chat(self, request: ChatRequest) -> ChatResponse:
        """处理聊天请求"""
        agent_executor = self.agent_service.get_agent_executor()
        thread_id = request.thread_id or "default"

        config = {"configurable": {"thread_id": thread_id}}
        input_message = {
            "role": "user",
            "content": request.message
        }

        response_messages = []
        async for step in agent_executor.astream(
                {"messages": [input_message]}, config, stream_mode="values"
        ):
            if step["messages"]:
                response_messages.append(step["messages"][-1])

        if response_messages:
            last_message = response_messages[-1]
            response_content = last_message.content if hasattr(last_message, 'content') else str(last_message)
        else:
            response_content = "抱歉，我没有得到有效的响应。"

        return ChatResponse(
            response=response_content,
            thread_id=thread_id
        )

    async def stream_chat(self, request: ChatRequest) -> AsyncGenerator[Dict[str, Any], None]:
        """处理流式聊天请求"""
        agent_executor = self.agent_service.get_agent_executor()
        thread_id = request.thread_id or "default"

        config = {"configurable": {"thread_id": thread_id}}
        input_message = {
            "role": "user",
            "content": request.message
        }

        try:
            async for step in agent_executor.astream(
                    {"messages": [input_message]}, config, stream_mode="values"
            ):
                if step["messages"]:
                    message = step["messages"][-1]
                    content = message.content if hasattr(message, 'content') else str(message)
                    yield {'content': content, 'thread_id': thread_id}

            yield {'done': True, 'thread_id': thread_id}

        except Exception as e:
            yield {'error': str(e)}

    async def get_chat_history(self, thread_id: str = "default") -> ChatHistoryResponse:
        """获取聊天历史"""
        config = {"configurable": {"thread_id": thread_id}}
        history = []

        try:
            checkpoints = []
            async for checkpoint_tuple in self.checkpointer.alist(config):
                checkpoints.append(checkpoint_tuple)

            if checkpoints:
                latest_checkpoint = checkpoints[0]

                if (latest_checkpoint.checkpoint and
                        'channel_values' in latest_checkpoint.checkpoint and
                        'messages' in latest_checkpoint.checkpoint['channel_values']):
                    messages = latest_checkpoint.checkpoint['channel_values']['messages']
                    history = self._parse_messages(messages)

            return ChatHistoryResponse(
                thread_id=thread_id,
                history=history,
                total_messages=len(history),
                total_checkpoints=len(checkpoints),
                status="success" if history else "no_history",
                latest_checkpoint_id=checkpoints[0].checkpoint['id'] if checkpoints else None,
                latest_timestamp=checkpoints[0].checkpoint['ts'] if checkpoints else None
            )

        except Exception as e:
            return ChatHistoryResponse(
                thread_id=thread_id,
                history=[],
                total_messages=0,
                total_checkpoints=0,
                status="no_history",
                message=f"该会话暂无历史记录: {str(e)}"
            )

    def _parse_messages(self, messages) -> List[Dict[str, Any]]:
        """解析消息历史"""
        history = []

        for msg in messages:
            if hasattr(msg, 'content') and hasattr(msg, 'type'):
                content = msg.content.strip() if msg.content else ""

                if not content or hasattr(msg, 'tool_calls') and msg.tool_calls or msg.type == 'tool':
                    continue

                role_map = {'human': 'user', 'ai': 'assistant', 'system': 'system'}
                role = role_map.get(msg.type, msg.type)

                if role in ['user', 'assistant', 'system']:
                    history.append({
                        "role": role,
                        "content": content,
                        "message_id": getattr(msg, 'id', None),
                        "type": msg.type
                    })

            elif isinstance(msg, dict):
                role = msg.get('role', 'unknown')
                content = msg.get('content', '').strip() if msg.get('content') else ""

                if not content or role == 'tool' or 'tool_calls' in msg:
                    continue

                if role in ['user', 'assistant', 'system']:
                    history.append({
                        "role": role,
                        "content": content,
                        "message_id": msg.get('id', None),
                        "type": role
                    })

        return history

    async def clear_chat_history(self, thread_id: str = "default") -> Dict[str, str]:
        """清除聊天历史"""
        config = {"configurable": {"thread_id": thread_id}}

        try:
            checkpoint_data = await self.checkpointer.aget(config)

            if checkpoint_data:
                await self.checkpointer.adelete_thread(thread_id)
                return {"message": f"已成功清除thread_id {thread_id} 的对话历史"}
            else:
                return {"message": f"thread_id {thread_id} 不存在历史记录"}

        except Exception as e:
            return {"message": f"清除thread_id {thread_id} 的历史记录时遇到问题: {str(e)}"}
