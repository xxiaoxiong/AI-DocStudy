"""
LLM客户端抽象基类
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional


class BaseLLMClient(ABC):
    """LLM客户端抽象基类"""
    
    @abstractmethod
    def chat(
        self, 
        messages: List[Dict[str, str]], 
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        聊天接口
        
        Args:
            messages: 消息列表，格式 [{"role": "user", "content": "..."}]
            temperature: 温度参数
            max_tokens: 最大token数
            
        Returns:
            回复内容
        """
        pass
    
    @abstractmethod
    def generate(
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
        pass



