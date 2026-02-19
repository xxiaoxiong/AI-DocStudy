from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.repositories.base import BaseRepository
from app.models.qa import QARecord


class QARepository(BaseRepository[QARecord]):
    """问答记录Repository"""
    
    def __init__(self, db: Session):
        super().__init__(QARecord, db)
    
    def get_by_user(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[QARecord]:
        """获取用户的问答记录"""
        return self.db.query(self.model).filter(
            self.model.user_id == user_id
        ).order_by(self.model.created_at.desc()).offset(skip).limit(limit).all()
    
    def get_by_document(
        self,
        document_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[QARecord]:
        """获取文档的问答记录"""
        return self.db.query(self.model).filter(
            self.model.document_id == document_id
        ).order_by(self.model.created_at.desc()).offset(skip).limit(limit).all()
    
    def get_by_user_and_document(
        self,
        user_id: int,
        document_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[QARecord]:
        """获取用户在特定文档的问答记录"""
        return self.db.query(self.model).filter(
            self.model.user_id == user_id,
            self.model.document_id == document_id
        ).order_by(self.model.created_at.desc()).offset(skip).limit(limit).all()
    
    def count_by_user(self, user_id: int) -> int:
        """统计用户问答记录数量"""
        return self.db.query(func.count(self.model.id)).filter(
            self.model.user_id == user_id
        ).scalar()
    
    def count_by_document(self, document_id: int) -> int:
        """统计文档问答记录数量"""
        return self.db.query(func.count(self.model.id)).filter(
            self.model.document_id == document_id
        ).scalar()
    
    def update_feedback(self, qa_id: int, helpful: bool) -> Optional[QARecord]:
        """更新问答反馈"""
        qa_record = self.get(qa_id)
        if qa_record:
            qa_record.helpful = helpful
            self.db.commit()
            self.db.refresh(qa_record)
        return qa_record



