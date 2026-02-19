from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Exam(Base):
    """考试模型"""
    __tablename__ = "exams"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey('documents.id', ondelete='SET NULL'), nullable=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    duration = Column(Integer, default=60)
    total_score = Column(Integer, default=100)
    pass_score = Column(Integer, default=60)
    created_by = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'))
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    # 关系
    document = relationship("Document", back_populates="exams")
    exam_questions = relationship("ExamQuestion", back_populates="exam", cascade="all, delete-orphan")
    answer_records = relationship("AnswerRecord", back_populates="exam")


class ExamQuestion(Base):
    """考试题目关联模型"""
    __tablename__ = "exam_questions"
    
    id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(Integer, ForeignKey('exams.id', ondelete='CASCADE'), nullable=False, index=True)
    question_id = Column(Integer, ForeignKey('questions.id', ondelete='CASCADE'), nullable=False)
    score = Column(Integer, default=10)
    order_index = Column(Integer, default=0)
    
    # 关系
    exam = relationship("Exam", back_populates="exam_questions")
    question = relationship("Question", back_populates="exam_questions")

