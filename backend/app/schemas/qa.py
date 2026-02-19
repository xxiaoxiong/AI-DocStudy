from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime


class QABase(BaseModel):
    """问答基础Schema"""
    document_id: Optional[int] = None
    question: str = Field(..., min_length=1, max_length=1000)


class QACreate(QABase):
    """创建问答Schema"""
    pass


class QASource(BaseModel):
    """问答来源Schema"""
    chunk_id: str
    content: str
    metadata: Dict = {}
    relevance_score: float
    document_id: Optional[int] = None
    document_title: Optional[str] = None


class QAResponse(QABase):
    """问答响应Schema"""
    id: int
    answer: str
    sources: List[QASource] = []
    has_answer: bool
    helpful: Optional[bool] = None
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class QAListResponse(BaseModel):
    """问答列表响应Schema"""
    records: List[QAResponse]
    total: int
    page: int
    page_size: int


class QAFeedback(BaseModel):
    """问答反馈Schema"""
    helpful: bool


class RelatedQuestionsResponse(BaseModel):
    """相关问题响应Schema"""
    questions: List[str]



