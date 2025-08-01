import json

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse

from api import get_chat_service
from models import (
    ChatHistoryResponse,
    ChatRequest,
    ChatResponse,
    StreamChatRequest,
)
from service import ChatService

router = APIRouter(prefix="/chat", tags=["聊天"])


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest, app_request: Request):
    """普通聊天接口"""
    try:
        chat_service: ChatService = get_chat_service(app_request)
        return await chat_service.chat(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理请求时发生错误: {str(e)}")


@router.post("/stream")
async def stream_chat(request: StreamChatRequest, app_request: Request):
    """流式聊天接口"""
    try:
        chat_service: ChatService = get_chat_service(app_request)

        async def generate_stream():
            try:
                async for data in chat_service.stream_chat(request):
                    yield f"data: {json.dumps(data)}\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"

        return StreamingResponse(
            generate_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理流式请求时发生错误: {str(e)}")


@router.get("/history/{thread_id}", response_model=ChatHistoryResponse)
async def get_chat_history(thread_id: str, app_request: Request):
    """获取对话历史"""
    try:
        chat_service: ChatService = get_chat_service(app_request)
        return await chat_service.get_chat_history(thread_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取历史记录时发生错误: {str(e)}")


@router.delete("/history/{thread_id}")
async def clear_chat_history(thread_id: str, app_request: Request):
    """清除对话历史"""
    try:
        chat_service: ChatService = get_chat_service(app_request)
        return await chat_service.clear_chat_history(thread_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"清除历史记录时发生错误: {str(e)}")
