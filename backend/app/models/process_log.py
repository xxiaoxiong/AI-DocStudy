from sqlalchemy import Column, Integer, String, Text, Enum, TIMESTAMP, ForeignKey, JSON, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class DocumentProcessLog(Base):
    """文档处理日志模型"""
    __tablename__ = "document_process_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey('documents.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # 处理进度
    status = Column(Enum('pending', 'parsing', 'analyzing', 'extracting', 'chunking', 'vectorizing', 'completed', 'failed'), 
                   default='pending', index=True)
    progress = Column(Float, default=0.0)  # 0-100
    current_step = Column(String(100))  # 当前步骤描述
    
    # 处理详情
    total_steps = Column(Integer, default=6)  # 总步骤数
    completed_steps = Column(Integer, default=0)  # 已完成步骤数
    
    # 日志信息
    logs = Column(JSON)  # 详细日志 [{"time": "...", "level": "info", "message": "..."}]
    
    # 处理结果统计
    parsed_text_length = Column(Integer)  # 解析文本长度
    sections_count = Column(Integer)  # 章节数量
    chunks_count = Column(Integer)  # 分块数量
    ai_analysis_time = Column(Float)  # AI分析耗时（秒）
    total_time = Column(Float)  # 总耗时（秒）
    
    # 错误信息
    error_message = Column(Text)
    error_traceback = Column(Text)
    
    # 时间戳
    started_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    completed_at = Column(TIMESTAMP, nullable=True)
    
    # 关系
    document = relationship("Document", back_populates="process_logs")

