from fastapi import APIRouter, HTTPException, Request

from api import get_agent_service
from models import ToolInfo, ToolsResponse

router = APIRouter(prefix="/tools", tags=["工具"])


@router.get("/", response_model=ToolsResponse)
async def get_available_tools(request: Request):
    """获取可用工具列表"""
    try:
        agent_service = get_agent_service(request)
        tools = agent_service.get_tools()

        tool_info = [
            ToolInfo(name=tool.name, description=tool.description)
            for tool in tools
        ]

        return ToolsResponse(tools=tool_info)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取工具列表时发生错误: {str(e)}")
