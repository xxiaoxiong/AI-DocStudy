"""
AI服务初始化
"""
from app.services.ai.llm_client import BaseLLMClient
from app.services.ai.deepseek import DeepSeekClient
from app.core.config import settings


def get_llm_client() -> BaseLLMClient:
    """
    工厂方法: 根据配置返回对应的LLM客户端
    
    Returns:
        LLM客户端实例
    """
    if settings.LLM_PROVIDER == "deepseek":
        return DeepSeekClient()
    else:
        raise ValueError(f"不支持的LLM提供商: {settings.LLM_PROVIDER}")


# 全局LLM客户端实例
llm_client = get_llm_client()



