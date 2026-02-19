"""
DeepSeek API客户端
"""
import httpx
from typing import List, Dict, Optional
from app.services.ai.llm_client import BaseLLMClient
from app.core.config import settings


class DeepSeekClient(BaseLLMClient):
    """DeepSeek API客户端"""
    
    def __init__(self):
        self.api_key = settings.DEEPSEEK_API_KEY
        self.base_url = settings.DEEPSEEK_BASE_URL
        self.client = httpx.AsyncClient(timeout=60.0)
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        聊天接口
        
        Args:
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大token数
            
        Returns:
            回复内容
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "deepseek-chat",
            "messages": messages,
            "temperature": temperature
        }
        
        if max_tokens:
            payload["max_tokens"] = max_tokens
        
        try:
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
        
        except httpx.HTTPStatusError as e:
            error_detail = e.response.text if hasattr(e, 'response') else str(e)
            raise Exception(f"DeepSeek API调用失败 (状态码: {e.response.status_code}): {error_detail}")
        except httpx.HTTPError as e:
            raise Exception(f"DeepSeek API网络错误: {str(e)}")
    
    async def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        生成接口
        
        Args:
            prompt: 提示词
            temperature: 温度参数
            max_tokens: 最大token数
            
        Returns:
            生成内容
        """
        messages = [{"role": "user", "content": prompt}]
        return await self.chat(messages, temperature, max_tokens)
    
    def __del__(self):
        """清理资源"""
        try:
            import asyncio
            asyncio.create_task(self.client.aclose())
        except:
            pass



