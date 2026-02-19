"""
Embedding服务 - 文档向量化
使用sentence-transformers的bge-large-zh模型
"""
from typing import List, Union
import numpy as np
from sentence_transformers import SentenceTransformer
from app.core.config import settings


class EmbeddingService:
    """Embedding服务"""
    
    _instance = None
    _model = None
    
    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """初始化模型"""
        if self._model is None:
            print(f"正在加载Embedding模型: {settings.EMBEDDING_MODEL}")
            self._model = SentenceTransformer(settings.EMBEDDING_MODEL)
            print("Embedding模型加载完成")
    
    def embed_text(self, text: str) -> List[float]:
        """
        对单个文本进行向量化
        
        Args:
            text: 输入文本
            
        Returns:
            向量列表
        """
        if not text or not text.strip():
            raise ValueError("文本不能为空")
        
        # 生成向量
        embedding = self._model.encode(text, convert_to_numpy=True)
        
        # 转换为列表
        return embedding.tolist()
    
    def embed_batch(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """
        批量对文本进行向量化
        
        Args:
            texts: 文本列表
            batch_size: 批处理大小
            
        Returns:
            向量列表的列表
        """
        if not texts:
            return []
        
        # 过滤空文本
        valid_texts = [t for t in texts if t and t.strip()]
        if not valid_texts:
            raise ValueError("没有有效的文本")
        
        # 批量生成向量
        embeddings = self._model.encode(
            valid_texts,
            batch_size=batch_size,
            convert_to_numpy=True,
            show_progress_bar=True
        )
        
        # 转换为列表
        return embeddings.tolist()
    
    def get_dimension(self) -> int:
        """获取向量维度"""
        return self._model.get_sentence_embedding_dimension()


# 全局实例
embedding_service = EmbeddingService()



