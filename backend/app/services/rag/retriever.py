"""
向量检索服务 - 使用Chroma
"""
import os
import shutil
from typing import List, Dict, Optional
import chromadb
from chromadb.config import Settings
from app.core.config import settings


class VectorRetriever:
    """向量检索器"""
    
    def __init__(self):
        """延迟初始化，首次使用时才创建Chroma客户端"""
        self._client = None
    
    def _get_client(self) -> chromadb.PersistentClient:
        """获取Chroma客户端（懒加载，自动处理旧版本schema不兼容问题）"""
        if self._client is not None:
            return self._client
        
        persist_dir = settings.CHROMA_PERSIST_DIR
        os.makedirs(persist_dir, exist_ok=True)
        
        try:
            self._client = chromadb.PersistentClient(
                path=persist_dir,
                settings=Settings(anonymized_telemetry=False, allow_reset=True)
            )
            # 做一次探测，确认schema正常
            self._client.list_collections()
            print(f"[Chroma] 客户端初始化完成，数据目录: {persist_dir}")
        except Exception as e:
            print(f"[Chroma] 检测到数据库异常({e})，正在重置...")
            self._client = None
            sqlite_path = os.path.join(persist_dir, "chroma.sqlite3")
            if os.path.exists(sqlite_path):
                try:
                    os.remove(sqlite_path)
                    print("[Chroma] 已删除旧数据库文件")
                except Exception as rm_err:
                    print(f"[Chroma] 无法删除旧数据库文件: {rm_err}，尝试备份...")
                    try:
                        shutil.move(sqlite_path, sqlite_path + ".bak")
                        print("[Chroma] 已备份旧数据库文件")
                    except Exception:
                        raise RuntimeError(
                            f"Chroma数据库schema不兼容且无法自动重置，请手动删除: {sqlite_path}\n原始错误: {e}"
                        )
            self._client = chromadb.PersistentClient(
                path=persist_dir,
                settings=Settings(anonymized_telemetry=False, allow_reset=True)
            )
            print("[Chroma] 数据库已重置，重新初始化完成")
        
        return self._client
    
    def get_or_create_collection(self, document_id: int):
        """
        获取或创建文档的collection
        
        Args:
            document_id: 文档ID
            
        Returns:
            Collection对象
        """
        collection_name = f"doc_{document_id}"
        collection = self._get_client().get_or_create_collection(
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
            raise ValueError("分块列表和向量列表不能为空")
        
        if len(chunks) != len(embeddings):
            raise ValueError(f"分块数量({len(chunks)})和向量数量({len(embeddings)})不匹配")
        
        print(f"[Chroma] 准备添加 {len(chunks)} 个分块到文档 {document_id}")
        
        collection = self.get_or_create_collection(document_id)
        
        # 准备数据
        ids = []
        documents = []
        metadatas = []
        valid_embeddings = []
        
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            # 验证数据完整性
            if 'id' not in chunk:
                print(f"[Chroma] 警告: 分块 {i} 缺少id字段，跳过")
                continue
            
            if 'content' not in chunk:
                print(f"[Chroma] 警告: 分块 {i} 缺少content字段，跳过")
                continue
            
            if not embedding or len(embedding) == 0:
                print(f"[Chroma] 警告: 分块 {i} 的向量为空，跳过")
                continue
            
            ids.append(str(chunk['id']))
            documents.append(chunk['content'])
            metadatas.append(chunk.get('metadata', {}))
            valid_embeddings.append(embedding)
        
        if not ids:
            raise ValueError("没有有效的分块可以添加")
        
        print(f"[Chroma] 实际添加 {len(ids)} 个有效分块")
        
        # 添加到collection
        try:
            collection.add(
                ids=ids,
                documents=documents,
                embeddings=valid_embeddings,
                metadatas=metadatas
            )
            print(f"[Chroma] 成功添加 {len(ids)} 个分块到文档 {document_id} 的向量库")
        except Exception as e:
            error_msg = f"Chroma添加数据失败: {str(e)}"
            print(f"[Chroma] 错误: {error_msg}")
            raise ValueError(error_msg)
    
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
        # 延迟导入，避免在不需要时加载embedding模型
        from app.services.ai.embedding import embedding_service
        
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
    
    def search_all(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        跨所有文档向量检索
        
        Args:
            query: 查询文本
            top_k: 每个collection返回top-k个结果
            
        Returns:
            检索结果列表（按相关度排序），每个包含 id, content, metadata, distance
        """
        from app.services.ai.embedding import embedding_service
        
        client = self._get_client()
        collections = client.list_collections()
        if not collections:
            return []
        
        query_embedding = embedding_service.embed_text(query)
        all_results = []
        
        for col_info in collections:
            try:
                col = client.get_collection(name=col_info.name)
                if col.count() == 0:
                    continue
                results = col.query(
                    query_embeddings=[query_embedding],
                    n_results=min(top_k, col.count()),
                    include=["documents", "metadatas", "distances"]
                )
                if results['ids'] and len(results['ids'][0]) > 0:
                    for i in range(len(results['ids'][0])):
                        all_results.append({
                            'id': results['ids'][0][i],
                            'content': results['documents'][0][i],
                            'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                            'distance': results['distances'][0][i] if results['distances'] else 0
                        })
            except Exception as e:
                print(f"[Chroma] 跨文档检索 {col_info.name} 失败: {e}")
                continue
        
        # 按距离排序，取最相关的top_k个
        all_results.sort(key=lambda x: x['distance'])
        return all_results[:top_k]

    def delete_collection(self, document_id: int):
        """
        删除文档的collection
        
        Args:
            document_id: 文档ID
        """
        collection_name = f"doc_{document_id}"
        self._get_client().delete_collection(name=collection_name)
        print(f"[Chroma] 已删除文档 {document_id} 的向量库")
    
    def get_collection_count(self, document_id: int) -> int:
        """
        获取collection中的文档数量
        
        Args:
            document_id: 文档ID
            
        Returns:
            文档数量，如果collection不存在返回0
        """
        collection_name = f"doc_{document_id}"
        try:
            collection = self._get_client().get_collection(name=collection_name)
            return collection.count()
        except Exception:
            return 0


# 全局实例
vector_retriever = VectorRetriever()



