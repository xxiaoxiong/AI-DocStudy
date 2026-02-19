"""
向量检索服务 - 使用Chroma
"""
from typing import List, Dict, Optional
import chromadb
from chromadb.config import Settings
from app.core.config import settings
from app.services.ai.embedding import embedding_service


class VectorRetriever:
    """向量检索器"""
    
    def __init__(self):
        """初始化Chroma客户端"""
        self.client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIR,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        print(f"Chroma客户端初始化完成，数据目录: {settings.CHROMA_PERSIST_DIR}")
    
    def get_or_create_collection(self, document_id: int):
        """
        获取或创建文档的collection
        
        Args:
            document_id: 文档ID
            
        Returns:
            Collection对象
        """
        collection_name = f"doc_{document_id}"
        
        # 获取或创建collection
        collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"document_id": document_id}
        )
        
        return collection
    
    def add_documents(
        self,
        document_id: int,
        chunks: List[Dict],
        embeddings: List[List[float]]
    ):
        """
        添加文档分块到向量数据库
        
        Args:
            document_id: 文档ID
            chunks: 分块列表，每个包含 id, content, metadata
            embeddings: 对应的向量列表
        """
        if not chunks or not embeddings:
            return
        
        if len(chunks) != len(embeddings):
            raise ValueError("分块数量和向量数量不匹配")
        
        collection = self.get_or_create_collection(document_id)
        
        # 准备数据
        ids = [str(chunk['id']) for chunk in chunks]
        documents = [chunk['content'] for chunk in chunks]
        metadatas = [chunk.get('metadata', {}) for chunk in chunks]
        
        # 添加到collection
        collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas
        )
        
        print(f"已添加 {len(chunks)} 个分块到文档 {document_id} 的向量库")
    
    def search(
        self,
        document_id: int,
        query: str,
        top_k: int = 3
    ) -> List[Dict]:
        """
        向量检索
        
        Args:
            document_id: 文档ID
            query: 查询文本
            top_k: 返回top-k个结果
            
        Returns:
            检索结果列表，每个包含 id, content, metadata, distance
        """
        # 获取collection
        collection = self.get_or_create_collection(document_id)
        
        # 检查collection是否为空
        if collection.count() == 0:
            print(f"文档 {document_id} 的向量库为空")
            return []
        
        # 查询向量化
        query_embedding = embedding_service.embed_text(query)
        
        # 执行检索
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )
        
        # 格式化结果
        formatted_results = []
        if results['ids'] and len(results['ids'][0]) > 0:
            for i in range(len(results['ids'][0])):
                formatted_results.append({
                    'id': results['ids'][0][i],
                    'content': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                    'distance': results['distances'][0][i] if results['distances'] else 0
                })
        
        return formatted_results
    
    def delete_collection(self, document_id: int):
        """
        删除文档的collection
        
        Args:
            document_id: 文档ID
        """
        collection_name = f"doc_{document_id}"
        try:
            self.client.delete_collection(name=collection_name)
            print(f"已删除文档 {document_id} 的向量库")
        except Exception as e:
            print(f"删除向量库失败: {str(e)}")
    
    def get_collection_count(self, document_id: int) -> int:
        """
        获取collection中的文档数量
        
        Args:
            document_id: 文档ID
            
        Returns:
            文档数量
        """
        collection = self.get_or_create_collection(document_id)
        return collection.count()


# 全局实例
vector_retriever = VectorRetriever()



