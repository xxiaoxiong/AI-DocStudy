from sqlalchemy import Column, Integer, String, Text, Enum, TIMESTAMP, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class User(Base):
    """用户模型"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum('student', 'teacher', 'admin'), default='student')
    created_at = Column(TIMESTAMP, server_default=func.now())
    last_login = Column(TIMESTAMP, nullable=True)
    
    # 关系
    documents = relationship("Document", back_populates="uploader")
    qa_records = relationship("QARecord", back_populates="user")
    answer_records = relationship("AnswerRecord", back_populates="user")

