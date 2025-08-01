from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class ChatMessage(BaseModel):
    """聊天消息模型"""
    role: str
    content: str


class ChatRequest(BaseModel):
    """聊天请求模型"""
    message: str
    thread_id: Optional[str] = "default"


class ChatResponse(BaseModel):
    """聊天响应模型"""
    response: str
    thread_id: str


class StreamChatRequest(BaseModel):
    """流式聊天请求模型"""
    message: str
    thread_id: Optional[str] = "default"


class ChatHistoryResponse(BaseModel):
    """聊天历史响应模型"""
    thread_id: str
    history: List[Dict[str, Any]]
    total_messages: int
    total_checkpoints: int
    status: str
    message: Optional[str] = None
    latest_checkpoint_id: Optional[str] = None
    latest_timestamp: Optional[str] = None
