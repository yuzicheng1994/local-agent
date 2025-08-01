from typing import List

from pydantic import BaseModel


class ToolInfo(BaseModel):
    """工具信息模型"""
    name: str
    description: str


class ToolsResponse(BaseModel):
    """工具列表响应模型"""
    tools: List[ToolInfo]
