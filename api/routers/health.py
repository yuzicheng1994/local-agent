from fastapi import APIRouter

from models import HealthResponse

router = APIRouter(prefix="/health", tags=["健康检查"])


@router.get("/", response_model=HealthResponse)
async def health_check():
    """健康检查接口"""
    return HealthResponse(status="healthy", message="Agent service is running")
