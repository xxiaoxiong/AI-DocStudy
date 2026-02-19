from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.document import (
    DocumentListResponse, 
    DocumentResponse, 
    DocumentDetailResponse,
    DocumentSectionResponse,
    DocumentUpdate
)
from app.repositories.document import DocumentRepository, DocumentSectionRepository
from app.utils.file_handler import FileHandler

router = APIRouter()


@router.get("", response_model=DocumentListResponse)
async def get_documents(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取文档列表"""
    try:
        repo = DocumentRepository(db)
        
        skip = (page - 1) * page_size
        
        # 始终按用户过滤，如果有status参数则额外过滤状态
        documents = repo.get_by_user(current_user.id, skip, page_size, status)
        total = repo.count_by_user(current_user.id, status)
        
        # 手动构造响应数据，避免关系字段序列化问题
        records = [
            DocumentResponse(
                id=doc.id,
                title=doc.title,
                file_type=doc.file_type,
                file_path=doc.file_path,
                file_size=doc.file_size,
                status=doc.status,
                uploaded_by=doc.uploaded_by,
                uploaded_at=doc.uploaded_at,
                processed_at=doc.processed_at
            )
            for doc in documents
        ]
        
        return DocumentListResponse(
            records=records,
            total=total,
            page=page,
            page_size=page_size
        )
    except Exception as e:
        import traceback
        print(f"获取文档列表失败: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"获取文档列表失败: {str(e)}")


@router.get("/{document_id}", response_model=DocumentDetailResponse)
async def get_document_detail(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取文档详情（包含AI分析结果）"""
    import json
    
    doc_repo = DocumentRepository(db)
    document = doc_repo.get(document_id)
    
    if not document:
        raise HTTPException(status_code=404, detail="文档不存在")
    
    if document.uploaded_by != current_user.id:
        raise HTTPException(status_code=403, detail="无权访问此文档")
    
    # 获取章节
    section_repo = DocumentSectionRepository(db)
    sections = section_repo.get_by_document(document_id)
    
    # 解析JSON字段
    key_points = []
    key_concepts = []
    learning_suggestions = []
    common_questions = []
    
    try:
        if document.key_points:
            key_points = json.loads(document.key_points) if isinstance(document.key_points, str) else document.key_points
    except:
        pass
    
    try:
        if document.key_concepts:
            key_concepts = json.loads(document.key_concepts) if isinstance(document.key_concepts, str) else document.key_concepts
    except:
        pass
    
    try:
        if document.learning_suggestions:
            learning_suggestions = json.loads(document.learning_suggestions) if isinstance(document.learning_suggestions, str) else document.learning_suggestions
    except:
        pass
    
    try:
        if document.common_questions:
            common_questions = json.loads(document.common_questions) if isinstance(document.common_questions, str) else document.common_questions
    except:
        pass
    
    # 手动构造响应数据
    return DocumentDetailResponse(
        id=document.id,
        title=document.title,
        file_type=document.file_type,
        file_path=document.file_path,
        file_size=document.file_size,
        status=document.status,
        one_sentence_summary=document.one_sentence_summary,
        summary=document.summary,
        key_points=key_points,
        key_concepts=key_concepts,
        document_type=document.document_type,
        difficulty_level=document.difficulty_level,
        target_audience=document.target_audience,
        learning_suggestions=learning_suggestions,
        estimated_reading_time=document.estimated_reading_time,
        common_questions=common_questions,
        uploaded_by=document.uploaded_by,
        uploaded_at=document.uploaded_at,
        processed_at=document.processed_at,
        sections=[
            DocumentSectionResponse(
                id=section.id,
                document_id=section.document_id,
                title=section.title,
                content=section.content,
                level=section.level,
                parent_id=section.parent_id,
                order_index=section.order_index
            )
            for section in sections
        ]
    )


@router.put("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: int,
    document_update: DocumentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新文档"""
    repo = DocumentRepository(db)
    document = repo.get(document_id)
    
    if not document:
        raise HTTPException(status_code=404, detail="文档不存在")
    
    if document.uploaded_by != current_user.id:
        raise HTTPException(status_code=403, detail="无权修改此文档")
    
    # 更新文档
    update_data = document_update.model_dump(exclude_unset=True)
    updated_document = repo.update(document_id, update_data)
    
    # 手动构造响应数据
    return DocumentResponse(
        id=updated_document.id,
        title=updated_document.title,
        file_type=updated_document.file_type,
        file_path=updated_document.file_path,
        file_size=updated_document.file_size,
        status=updated_document.status,
        uploaded_by=updated_document.uploaded_by,
        uploaded_at=updated_document.uploaded_at,
        processed_at=updated_document.processed_at
    )


@router.delete("/{document_id}")
async def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除文档"""
    try:
        repo = DocumentRepository(db)
        document = repo.get(document_id)
        
        if not document:
            raise HTTPException(status_code=404, detail="文档不存在")
        
        if document.uploaded_by != current_user.id:
            raise HTTPException(status_code=403, detail="无权删除此文档")
        
        # 1. 删除向量数据库中的数据
        try:
            from app.services.rag.retriever import vector_retriever
            vector_retriever.delete_collection(document_id)
            print(f"已删除文档 {document_id} 的向量数据")
        except Exception as e:
            print(f"删除向量数据失败（可忽略）: {str(e)}")
        
        # 2. 删除物理文件
        try:
            FileHandler.delete_file(document.file_path)
            print(f"已删除文档文件: {document.file_path}")
        except Exception as e:
            print(f"删除文件失败（可忽略）: {str(e)}")
        
        # 3. 删除数据库记录（会级联删除关联数据）
        success = repo.delete(document_id)
        
        if not success:
            raise HTTPException(status_code=500, detail="删除数据库记录失败")
        
        return {"success": True, "message": "文档删除成功"}
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"删除文档失败: {str(e)}")
        print(error_trace)
        raise HTTPException(status_code=500, detail=f"删除文档失败: {str(e)}")



