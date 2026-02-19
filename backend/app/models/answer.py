from sqlalchemy import Column, Integer, Text, TIMESTAMP, ForeignKey, DECIMAL, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class AnswerRecord(Base):
    """答题记录模型"""
    __tablename__ = "answer_records"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    exam_id = Column(Integer, ForeignKey('exams.id', ondelete='CASCADE'), nullable=True, index=True)
    question_id = Column(Integer, ForeignKey('questions.id', ondelete='CASCADE'), nullable=False)
    user_answer = Column(Text)
    is_correct = Column(Boolean, default=False)
    score = Column(DECIMAL(5, 2), default=0)
    ai_feedback = Column(Text)
    time_spent = Column(Integer, default=0)
    answered_at = Column(TIMESTAMP, server_default=func.now())
    
    # 关系
    user = relationship("User", back_populates="answer_records")
    exam = relationship("Exam", back_populates="answer_records")
    question = relationship("Question", back_populates="answer_records")

