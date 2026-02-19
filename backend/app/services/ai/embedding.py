"""
Embedding服务 - 文档向量化
使用sentence-transformers的bge-small-zh模型
"""
from typing import List, Union
import numpy as np
from sentence_transformers import SentenceTransformer
from app.core.config import settings


class EmbeddingService:
    """Embedding服务"""
    
    _instance = None
    _model = None
    _model_load_error = None
    
    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """初始化模型（延迟加载）"""
        pass
    
    def _ensure_model_loaded(self):
        """确保模型已加载"""
        if self._model is not None:
            return
        
        if self._model_load_error is not None:
            raise RuntimeError(
                f"Embedding模型加载失败: {self._model_load_error}\n"
                f"请检查:\n"
                f"1. 网络连接是否正常\n"
                f"2. 是否可以访问 HuggingFace (https://huggingface.co)\n"
                f"3. 或手动下载模型 {settings.EMBEDDING_MODEL} 到本地\n"
                f"4. 修改配置文件指向本地模型路径"
            )
        
        print(f"[Embedding] 正在加载模型: {settings.EMBEDDING_MODEL}")
        try:
            # 尝试使用国内镜像源
            import os
            os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
            
            # 检查模型路径是否存在（使用绝对路径）
            model_path = os.path.abspath(settings.EMBEDDING_MODEL)
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"模型路径不存在: {model_path}")
            
            print(f"[Embedding] 模型路径: {model_path}")
            self._model = SentenceTransformer(model_path)
            dimension = self._model.get_sentence_embedding_dimension()
            print(f"[Embedding] 模型加载完成，向量维度: {dimension}")
        except Exception as e:
            error_msg = str(e)
            self._model_load_error = error_msg
            print(f"[Embedding] 模型加载失败: {error_msg}")
            print(f"[Embedding] 提示: 请确保模型文件存在于 {settings.EMBEDDING_MODEL}")
            raise RuntimeError(
                f"Embedding模型加载失败: {error_msg}\n"
                f"请检查:\n"
                f"1. 模型路径是否正确: {settings.EMBEDDING_MODEL}\n"
                f"2. 模型文件是否完整\n"
                f"3. 网络连接是否正常（如需下载）\n"
                f"4. 是否有足够的磁盘空间"
            )
    
    def embed_text(self, text: str) -> List[float]:
        """
        对单个文本进行向量化
        
        Args:
            text: 输入文本
            
        Returns:
            向量列表
        """
        self._ensure_model_loaded()
        
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
            向量列表的列表（与输入texts长度一致，空文本用零向量填充）
        """
        self._ensure_model_loaded()
        
        if not texts:
            return []
        
        print(f"[Embedding] 开始批量向量化，共 {len(texts)} 个文本")
        
        # 记录空文本的位置，并用占位符替换
        text_mapping = []
        valid_texts = []
        for i, text in enumerate(texts):
            if text and text.strip():
                text_mapping.append((i, len(valid_texts)))
                valid_texts.append(text.strip())
            else:
                text_mapping.append((i, -1))  # -1 表示空文本
                print(f"[Embedding] 警告: 文本索引 {i} 为空")
        
        if not valid_texts:
            raise ValueError("没有有效的文本")
        
        print(f"[Embedding] 有效文本数量: {len(valid_texts)}")
        
        # 批量生成向量
        try:
            embeddings = self._model.encode(
                valid_texts,
                batch_size=batch_size,
                convert_to_numpy=True,
                show_progress_bar=True
            )
            print(f"[Embedding] 向量化完成，生成 {len(embeddings)} 个向量")
        except Exception as e:
            error_msg = f"向量化过程失败: {str(e)}"
            print(f"[Embedding] 错误: {error_msg}")
            raise RuntimeError(error_msg)
        
        # 获取向量维度
        dimension = embeddings.shape[1]
        print(f"[Embedding] 向量维度: {dimension}")
        
        # 构建完整的结果列表，空文本位置用零向量填充
        result = []
        for i, (orig_idx, valid_idx_map) in enumerate(text_mapping):
            if valid_idx_map == -1:
                # 空文本，使用零向量
                result.append([0.0] * dimension)
                print(f"[Embedding] 文本索引 {i} 使用零向量")
            else:
                result.append(embeddings[valid_idx_map].tolist())
        
        print(f"[Embedding] 返回 {len(result)} 个向量（包含零向量）")
        return result
    
    def get_dimension(self) -> int:
        """获取向量维度"""
        self._ensure_model_loaded()
        return self._model.get_sentence_embedding_dimension()


# 全局实例（延迟加载，不会在导入时立即加载模型）
embedding_service = EmbeddingService()

