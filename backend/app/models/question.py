from sqlalchemy import Column, Integer, String, Text, Enum, TIMESTAMP, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Question(Base):
    """题目模型"""
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey('documents.id', ondelete='CASCADE'), nullable=False, index=True)
    section_id = Column(Integer, ForeignKey('document_sections.id', ondelete='SET NULL'), nullable=True)
    type = Column(Enum('single', 'judge', 'essay'), nullable=False)
    difficulty = Column(Enum('easy', 'medium', 'hard'), default='medium')
    content = Column(Text, nullable=False)
    options = Column(JSON, nullable=True)
    answer = Column(Text, nullable=False)
    explanation = Column(Text)
    source_reference = Column(String(255))
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    # 关系
    document = relationship("Document", back_populates="questions")
    exam_questions = relationship("ExamQuestion", back_populates="question", cascade="all, delete-orphan")
    answer_records = relationship("AnswerRecord", back_populates="question", cascade="all, delete-orphan")

