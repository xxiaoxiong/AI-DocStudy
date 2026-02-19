from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class DocumentBase(BaseModel):
    """文档基础Schema"""
    title: str = Field(..., min_length=1, max_length=200)
    file_type: Optional[str] = None


class DocumentCreate(DocumentBase):
    """创建文档Schema"""
    file_path: str
    file_size: int
    uploaded_by: int
    status: str = "processing"


class DocumentUpdate(BaseModel):
    """更新文档Schema"""
    title: Optional[str] = None
    status: Optional[str] = None


class KeyConcept(BaseModel):
    """关键概念"""
    term: str
    definition: str


class DocumentResponse(DocumentBase):
    """文档响应Schema（增强版 - 包含AI分析结果）"""
    id: int
    file_path: str
    file_size: Optional[int] = None
    status: str
    
    # AI分析结果
    one_sentence_summary: Optional[str] = None
    summary: Optional[str] = None
    key_points: Optional[List[str]] = None
    key_concepts: Optional[List[KeyConcept]] = None
    document_type: Optional[str] = None
    difficulty_level: Optional[str] = None
    target_audience: Optional[str] = None
    learning_suggestions: Optional[List[str]] = None
    estimated_reading_time: Optional[str] = None
    common_questions: Optional[List[str]] = None
    
    uploaded_by: Optional[int] = None
    uploaded_at: datetime
    processed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        arbitrary_types_allowed = True


class DocumentListResponse(BaseModel):
    """文档列表响应Schema"""
    records: List[DocumentResponse]
    total: int
    page: int
    page_size: int


class UploadResponse(BaseModel):
    """上传响应Schema"""
    document_id: int
    status: str
    message: str


class DocumentSectionResponse(BaseModel):
    """文档章节响应Schema"""
    id: int
    document_id: int
    title: str
    content: Optional[str] = None
    level: int
    parent_id: Optional[int] = None
    order_index: int
    
    class Config:
        from_attributes = True


class DocumentDetailResponse(DocumentResponse):
    """文档详情响应Schema"""
    sections: List[DocumentSectionResponse] = []
    chunk_count: Optional[int] = 0
    qa_count: Optional[int] = 0

