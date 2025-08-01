from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置类"""

    # 数据库配置
    db_uri: str

    # LLM配置
    llm_model: str
    llm_base_url: str
    llm_api_key: str

    # Embedding配置
    embedding_model: str

    # Chroma配置
    chroma_host: str
    chroma_port: int
    collection_name: str

    # 服务配置
    port: int = 8080
    log_level: str = "info"

    class Config:
        # 从.env文件读取环境变量
        env_file = ".env"
        # 环境变量名不区分大小写
        case_sensitive = False
        # 允许额外的环境变量存在
        extra = "ignore"


settings = Settings()
