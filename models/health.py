from pydantic import BaseModel


class HealthResponse(BaseModel):
    """健康信息响应模型"""
    status: str
    message: str
