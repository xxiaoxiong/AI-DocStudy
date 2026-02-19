from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.document import DocumentChunk, DocumentSection
from app.repositories.document import DocumentChunkRepository, DocumentSectionRepository
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()


class ChunkResponse(BaseModel):
    """分块响应"""
    id: int
    chunk_index: int
    content: str
    chunk_hash: str
    section_id: Optional[int] = None
    
    class Config:
        from_attributes = True


class SectionDetailResponse(BaseModel):
    """章节详情响应"""
    id: int
    title: str
    content: Optional[str] = None
    level: int
    order_index: int
    parent_id: Optional[int] = None
    
    class Config:
        from_attributes = True


class DocumentProcessDetailResponse(BaseModel):
    """文档处理详情响应"""
    document_id: int
    
    # 章节信息
    sections: List[SectionDetailResponse]
    sections_count: int
    
    # 分块信息
    chunks: List[ChunkResponse]
    chunks_count: int
    total_text_length: int
    
    # 向量化信息
    has_vectors: bool
    vector_count: int


@router.post("/{document_id}/re-vectorize")
async def re_vectorize_document(
    document_id: int = Path(..., description="文档ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """对已处理文档重新执行向量化（用于修复向量数据为空的文档）"""
    from app.repositories.document import DocumentRepository, DocumentChunkRepository
    from app.services.ai.embedding import embedding_service
    from app.services.rag.retriever import vector_retriever

    doc_repo = DocumentRepository(db)
    document = doc_repo.get(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="文档不存在")
    if document.uploaded_by != current_user.id:
        raise HTTPException(status_code=403, detail="无权操作此文档")

    chunk_repo = DocumentChunkRepository(db)
    chunks = chunk_repo.get_by_document(document_id)
    if not chunks:
        raise HTTPException(status_code=400, detail="文档没有分块数据，请重新上传文档")

    try:
        texts = [chunk.content if chunk.content else "" for chunk in chunks]
        embeddings = embedding_service.embed_batch(texts)

        # 清理旧向量
        try:
            vector_retriever.delete_collection(document_id)
        except Exception:
            pass

        chunks_data = [
            {
                "id": chunk.id,
                "content": chunk.content if chunk.content else "",
                "metadata": {"chunk_index": chunk.chunk_index, "document_id": document_id}
            }
            for chunk in chunks
        ]
        vector_retriever.add_documents(
            document_id=document_id,
            chunks=chunks_data,
            embeddings=embeddings
        )
        stored = vector_retriever.get_collection_count(document_id)
        return {"success": True, "message": f"向量化完成，共存储 {stored} 个分块"}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"向量化失败: {str(e)}")


@router.get("/{document_id}/process-detail", response_model=DocumentProcessDetailResponse)
async def get_document_process_detail(
    document_id: int = Path(..., description="文档ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取文档处理详情（章节、分块、向量等）"""
    
    # 获取章节
    section_repo = DocumentSectionRepository(db)
    sections = section_repo.get_by_document(document_id)
    
    # 获取分块
    chunk_repo = DocumentChunkRepository(db)
    chunks = chunk_repo.get_by_document(document_id)
    
    # 计算总文本长度
    total_text_length = sum(len(chunk.content) for chunk in chunks)
    
    # 检查向量化状态（查询Chroma获取真实数量）
    try:
        from app.services.rag.retriever import vector_retriever
        vector_count = vector_retriever.get_collection_count(document_id)
        has_vectors = vector_count > 0
    except Exception:
        has_vectors = False
        vector_count = 0
    
    return DocumentProcessDetailResponse(
        document_id=document_id,
        sections=[
            SectionDetailResponse(
                id=section.id,
                title=section.title,
                content=section.content,
                level=section.level,
                order_index=section.order_index,
                parent_id=section.parent_id
            )
            for section in sections
        ],
        sections_count=len(sections),
        chunks=[
            ChunkResponse(
                id=chunk.id,
                chunk_index=chunk.chunk_index,
                content=chunk.content,
                chunk_hash=chunk.chunk_hash,
                section_id=chunk.section_id
            )
            for chunk in chunks
        ],
        chunks_count=len(chunks),
        total_text_length=total_text_length,
        has_vectors=has_vectors,
        vector_count=vector_count
    )



