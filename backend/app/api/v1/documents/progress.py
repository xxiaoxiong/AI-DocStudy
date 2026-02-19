from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.process_log import DocumentProcessLog
from pydantic import BaseModel
from typing import List, Optional
import json

router = APIRouter()


class LogEntry(BaseModel):
    """日志条目"""
    time: str
    level: str
    message: str
    details: Optional[dict] = None


class ProcessProgressResponse(BaseModel):
    """处理进度响应"""
    document_id: int
    status: str
    progress: float
    current_step: str
    completed_steps: int
    total_steps: int
    logs: List[LogEntry]
    
    # 统计信息
    parsed_text_length: Optional[int] = None
    sections_count: Optional[int] = None
    chunks_count: Optional[int] = None
    ai_analysis_time: Optional[float] = None
    total_time: Optional[float] = None
    
    # 错误信息
    error_message: Optional[str] = None
    
    # 时间
    started_at: str
    updated_at: str
    completed_at: Optional[str] = None


@router.get("/{document_id}/progress", response_model=ProcessProgressResponse)
async def get_document_progress(
    document_id: int = Path(..., description="文档ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取文档处理进度"""
    
    # 查询最新的处理日志
    log = db.query(DocumentProcessLog).filter(
        DocumentProcessLog.document_id == document_id
    ).order_by(DocumentProcessLog.id.desc()).first()
    
    if not log:
        raise HTTPException(status_code=404, detail="未找到处理日志")
    
    # 解析日志
    logs = []
    if log.logs:
        try:
            logs_data = json.loads(log.logs) if isinstance(log.logs, str) else log.logs
            logs = [LogEntry(**entry) for entry in logs_data]
        except:
            pass
    
    return ProcessProgressResponse(
        document_id=document_id,
        status=log.status,
        progress=log.progress or 0.0,
        current_step=log.current_step or '',
        completed_steps=log.completed_steps or 0,
        total_steps=log.total_steps or 6,
        logs=logs,
        parsed_text_length=log.parsed_text_length,
        sections_count=log.sections_count,
        chunks_count=log.chunks_count,
        ai_analysis_time=log.ai_analysis_time,
        total_time=log.total_time,
        error_message=log.error_message,
        started_at=log.started_at.strftime('%Y-%m-%d %H:%M:%S'),
        updated_at=log.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
        completed_at=log.completed_at.strftime('%Y-%m-%d %H:%M:%S') if log.completed_at else None
    )



