import asyncio
import signal
import sys
import threading
import time
import webbrowser

import requests
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from api import chat, health, tools
from config import settings
from core import lifespan


def create_app() -> FastAPI:
    """创建FastAPI应用"""
    app = FastAPI(
        title="LangChain Agent Web Service",
        description="基于LangChain的智能Agent Web服务",
        version="1.0.0",
        lifespan=lifespan
    )

    # 添加CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 静态文件服务
    app.mount("/static", StaticFiles(directory="static"), name="static")

    # 注册路由
    app.include_router(health.router)
    app.include_router(chat.router)
    app.include_router(tools.router)

    @app.get("/")
    async def root():
        return RedirectResponse(url="/static/chat.html")

    return app


def check_windows_compatibility() -> bool:
    """检查Windows系统的asyncio兼容性"""
    if sys.platform.startswith('win'):
        print("🔍 检测为Windows系统")
        policy = asyncio.get_event_loop_policy()
        print(f"📋 当前事件循环策略: {type(policy).__name__}")

        if not isinstance(policy, asyncio.WindowsSelectorEventLoopPolicy):
            print("⚠️ 需要切换为WindowsSelectorEventLoopPolicy以兼容psycopg")
            return False
        else:
            print("✅ 事件循环策略已正确设置")
        return True
    print("📋 非Windows系统，跳过兼容性检查")
    return True


def signal_handler(sig, frame):
    """关闭信号处理"""
    print("\n🛑 正在关闭服务器...")
    sys.exit(0)


def open_browser_when_ready():
    """等待服务器就绪后打开浏览器"""
    url = f"http://localhost:{settings.port}"
    health_url = f"{url}/health"

    max_attempts = 30
    for attempt in range(max_attempts):
        try:
            response = requests.get(health_url, timeout=1)
            if response.status_code == 200:
                print("✅ 服务器已就绪，正在打开浏览器...")
                webbrowser.open(url)
                return
        except (requests.RequestException, Exception):
            time.sleep(1)

    print("⚠️ 服务器启动超时，请手动访问:", url)


def main():
    """主函数"""
    # Windows兼容性：设置事件循环策略
    if not check_windows_compatibility():
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)

    # 在后台线程中等待并打开浏览器
    threading.Thread(target=open_browser_when_ready, daemon=True).start()

    try:
        # 启动服务器
        print(f"🚀 正在启动Agent服务器，端口: {settings.port}")
        print("💡 按 Ctrl+C 停止服务器")

        app = create_app()
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=settings.port,
            log_level=settings.log_level
        )
    except KeyboardInterrupt:
        print("\n✅ 服务器已关闭")


if __name__ == "__main__":
    main()
