from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """应用配置"""
    
    # 应用配置
    APP_NAME: str = "AI-DocStudy"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # 数据库配置
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3307
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = "123456"
    MYSQL_DATABASE: str = "ai_docstudy"
    
    # Redis配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # JWT配置
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    # LLM配置
    LLM_PROVIDER: str = "deepseek"
    DEEPSEEK_API_KEY: str = "sk-798d4c62cf6d49369fa6ecbd66d69048"
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"
    INTERNAL_LLM_URL: str = "http://internal-llm:8000"
    
    # Embedding配置
    # 使用 bge-small 模型，更小更快（约200MB）
    EMBEDDING_MODEL: str = "./models/AI-ModelScope/bge-small-zh-v1___5"
    CHROMA_PERSIST_DIR: str = "./data/chroma_v2"
    
    # 文档配置
    UPLOAD_DIR: str = "./data/uploads"
    MAX_UPLOAD_SIZE: int = 52428800  # 50MB
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    
    # 缓存配置
    CACHE_TTL: int = 3600
    ENABLE_CACHE: bool = True
    
    @property
    def database_url(self) -> str:
        """数据库连接URL"""
        return f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}?charset=utf8mb4"
    
    @property
    def redis_url(self) -> str:
        """Redis连接URL"""
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

