from sqlalchemy import Column, Integer, Text, TIMESTAMP, ForeignKey, JSON, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class QARecord(Base):
    """问答记录模型"""
    __tablename__ = "qa_records"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    document_id = Column(Integer, ForeignKey('documents.id', ondelete='SET NULL'), nullable=True, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    sources = Column(JSON)
    helpful = Column(Boolean, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now(), index=True)
    
    # 关系
    user = relationship("User", back_populates="qa_records")
    document = relationship("Document", back_populates="qa_records")

