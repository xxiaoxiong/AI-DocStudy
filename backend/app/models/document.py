from sqlalchemy import Column, Integer, String, Text, Enum, TIMESTAMP, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Document(Base):
    """文档模型（增强版 - 支持AI智能分析）"""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(20), nullable=False)
    file_size = Column(Integer)
    status = Column(Enum('processing', 'completed', 'failed'), default='processing', index=True)
    
    # AI分析结果字段
    one_sentence_summary = Column(String(500))  # 一句话总结
    summary = Column(Text)  # 详细摘要
    key_points = Column(JSON)  # 核心要点列表
    key_concepts = Column(JSON)  # 关键概念 [{"term": "术语", "definition": "定义"}]
    document_type = Column(String(100))  # 文档类型
    difficulty_level = Column(String(50))  # 难度等级
    target_audience = Column(String(200))  # 目标读者
    learning_suggestions = Column(JSON)  # 学习建议列表
    estimated_reading_time = Column(String(50))  # 预计阅读时间
    common_questions = Column(JSON)  # 常见问题列表
    
    uploaded_by = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'))
    uploaded_at = Column(TIMESTAMP, server_default=func.now())
    processed_at = Column(TIMESTAMP, nullable=True)
    
    # 关系
    uploader = relationship("User", back_populates="documents", lazy="noload")
    sections = relationship("DocumentSection", back_populates="document", cascade="all, delete-orphan", lazy="noload")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan", lazy="noload")
    questions = relationship("Question", back_populates="document", cascade="all, delete-orphan", lazy="noload")
    exams = relationship("Exam", back_populates="document", cascade="all, delete-orphan", lazy="noload")
    qa_records = relationship("QARecord", back_populates="document", cascade="all, delete-orphan", lazy="noload")
    process_logs = relationship("DocumentProcessLog", back_populates="document", cascade="all, delete-orphan", lazy="noload")


class DocumentSection(Base):
    """文档章节模型"""
    __tablename__ = "document_sections"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey('documents.id', ondelete='CASCADE'), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text)
    level = Column(Integer, default=1)
    parent_id = Column(Integer, ForeignKey('document_sections.id', ondelete='CASCADE'), nullable=True, index=True)
    order_index = Column(Integer, default=0)
    
    # 关系
    document = relationship("Document", back_populates="sections")
    parent = relationship("DocumentSection", remote_side=[id], backref="children")
    chunks = relationship("DocumentChunk", back_populates="section")


class DocumentChunk(Base):
    """文档分块模型"""
    __tablename__ = "document_chunks"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey('documents.id', ondelete='CASCADE'), nullable=False, index=True)
    section_id = Column(Integer, ForeignKey('document_sections.id', ondelete='SET NULL'), nullable=True)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    chunk_hash = Column(String(64), index=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    # 关系
    document = relationship("Document", back_populates="chunks")
    section = relationship("DocumentSection", back_populates="chunks")

