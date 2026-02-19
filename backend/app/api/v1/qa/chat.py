from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.qa import (
    QACreate,
    QAResponse,
    QAListResponse,
    QAFeedback,
    RelatedQuestionsResponse
)
from typing import Optional
from app.repositories.qa import QARepository
from app.repositories.document import DocumentRepository
from app.services.rag.generator import rag_generator
import json

router = APIRouter()


@router.post("/ask", response_model=QAResponse)
async def ask_question(
    qa_create: QACreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    智能问答
    
    基于文档内容回答用户问题。document_id可选，不传则跨所有文档检索。
    """
    import traceback
    
    try:
        from app.services.rag.retriever import vector_retriever
        
        if qa_create.document_id:
            # 单文档模式
            doc_repo = DocumentRepository(db)
            document = doc_repo.get(qa_create.document_id)
            if not document:
                raise HTTPException(status_code=404, detail="文档不存在")
            if document.status != 'completed':
                raise HTTPException(status_code=400, detail="文档还在处理中，请稍后再试")
            try:
                vector_count = vector_retriever.get_collection_count(qa_create.document_id)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"向量数据库访问失败: {str(e)}")
            if vector_count == 0:
                raise HTTPException(status_code=400, detail="文档向量数据为空，请重新上传文档触发处理")
            print(f"[QA] 用户 {current_user.id} 对文档 {qa_create.document_id} 提问: {qa_create.question}")
            result = await rag_generator.answer_question(
                document_id=qa_create.document_id,
                question=qa_create.question,
                top_k=3
            )
        else:
            # 跨文档模式
            print(f"[QA] 用户 {current_user.id} 跨文档提问: {qa_create.question}")
            result = await rag_generator.answer_question_all(
                question=qa_create.question,
                top_k=5
            )
        
        print(f"[QA] 答案生成成功，来源数量: {len(result['sources'])}")
        
        # 保存问答记录
        qa_repo = QARepository(db)
        qa_record = qa_repo.create({
            "user_id": current_user.id,
            "document_id": qa_create.document_id,
            "question": qa_create.question,
            "answer": result["answer"],
            "sources": json.dumps(result["sources"], ensure_ascii=False),
            "helpful": None
        })
        
        return QAResponse(
            id=qa_record.id,
            document_id=qa_record.document_id,
            question=qa_record.question,
            answer=qa_record.answer,
            sources=result["sources"],
            has_answer=result["has_answer"],
            helpful=qa_record.helpful,
            user_id=qa_record.user_id,
            created_at=qa_record.created_at
        )
    
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"问答处理失败: {str(e)}"
        print(f"[QA] 错误: {error_msg}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=error_msg)


@router.get("/history", response_model=QAListResponse)
async def get_qa_history(
    document_id: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取问答历史记录
    
    可以按文档筛选
    """
    qa_repo = QARepository(db)
    skip = (page - 1) * page_size
    
    # 获取记录
    if document_id:
        records = qa_repo.get_by_user_and_document(
            user_id=current_user.id,
            document_id=document_id,
            skip=skip,
            limit=page_size
        )
        total = qa_repo.count_by_document(document_id)
    else:
        records = qa_repo.get_by_user(
            user_id=current_user.id,
            skip=skip,
            limit=page_size
        )
        total = qa_repo.count_by_user(current_user.id)
    
    # 构建响应
    qa_responses = []
    for record in records:
        sources = json.loads(record.sources) if record.sources else []
        qa_responses.append(QAResponse(
            id=record.id,
            document_id=record.document_id,
            question=record.question,
            answer=record.answer,
            sources=sources,
            has_answer=bool(sources),
            helpful=record.helpful,
            user_id=record.user_id,
            created_at=record.created_at
        ))
    
    return QAListResponse(
        records=qa_responses,
        total=total,
        page=page,
        page_size=page_size
    )


@router.post("/{qa_id}/feedback")
async def submit_feedback(
    qa_id: int,
    feedback: QAFeedback,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    提交问答反馈
    
    用户可以标记答案是否有帮助
    """
    qa_repo = QARepository(db)
    qa_record = qa_repo.get(qa_id)
    
    if not qa_record:
        raise HTTPException(status_code=404, detail="问答记录不存在")
    
    if qa_record.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权操作此记录")
    
    # 更新反馈
    qa_repo.update_feedback(qa_id, feedback.helpful)
    
    return {"success": True, "message": "反馈提交成功"}


@router.get("/related-questions", response_model=RelatedQuestionsResponse)
async def get_related_questions(
    document_id: int = Query(...),
    question: str = Query(..., min_length=1),
    count: int = Query(3, ge=1, le=5),
    current_user: User = Depends(get_current_user)
):
    """
    获取相关问题推荐
    
    基于当前问题生成相关问题
    """
    try:
        questions = await rag_generator.generate_related_questions(
            document_id=document_id,
            current_question=question,
            count=count
        )
        
        return RelatedQuestionsResponse(questions=questions)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成相关问题失败: {str(e)}")



