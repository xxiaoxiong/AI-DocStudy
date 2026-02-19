from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from app.repositories.base import BaseRepository
from app.models.document import Document, DocumentSection, DocumentChunk


class DocumentRepository(BaseRepository[Document]):
    """文档Repository"""
    
    def __init__(self, db: Session):
        super().__init__(Document, db)
    
    def get_by_user(self, user_id: int, skip: int = 0, limit: int = 100, status: Optional[str] = None) -> List[Document]:
        """获取用户的文档列表"""
        from sqlalchemy.orm import noload
        
        query = self.db.query(self.model).options(
            noload(self.model.uploader),
            noload(self.model.sections),
            noload(self.model.chunks),
            noload(self.model.questions),
            noload(self.model.exams),
            noload(self.model.qa_records)
        ).filter(
            self.model.uploaded_by == user_id
        )
        if status:
            query = query.filter(self.model.status == status)
        return query.order_by(self.model.uploaded_at.desc()).offset(skip).limit(limit).all()
    
    def get_by_status(self, status: str, skip: int = 0, limit: int = 100) -> List[Document]:
        """根据状态获取文档"""
        from sqlalchemy.orm import noload
        
        return self.db.query(self.model).options(
            noload(self.model.uploader),
            noload(self.model.sections),
            noload(self.model.chunks),
            noload(self.model.questions),
            noload(self.model.exams),
            noload(self.model.qa_records)
        ).filter(
            self.model.status == status
        ).order_by(self.model.uploaded_at.desc()).offset(skip).limit(limit).all()
    
    def count_by_user(self, user_id: int, status: Optional[str] = None) -> int:
        """统计用户文档数量"""
        query = self.db.query(func.count(self.model.id)).filter(
            self.model.uploaded_by == user_id
        )
        if status:
            query = query.filter(self.model.status == status)
        result = query.scalar()
        return result if result is not None else 0
    
    def update_status(self, document_id: int, status: str) -> Optional[Document]:
        """更新文档状态"""
        from sqlalchemy.orm import noload
        
        document = self.db.query(self.model).options(
            noload(self.model.uploader),
            noload(self.model.sections),
            noload(self.model.chunks),
            noload(self.model.questions),
            noload(self.model.exams),
            noload(self.model.qa_records)
        ).filter(self.model.id == document_id).first()
        
        if document:
            document.status = status
            if status == 'completed':
                document.processed_at = datetime.now()
            self.db.commit()
            self.db.refresh(document)
        return document
    
    def update_analysis(self, document_id: int, analysis: dict) -> Optional[Document]:
        """更新文档的AI分析结果"""
        from sqlalchemy.orm import noload
        import json
        
        document = self.db.query(self.model).options(
            noload(self.model.uploader),
            noload(self.model.sections),
            noload(self.model.chunks),
            noload(self.model.questions),
            noload(self.model.exams),
            noload(self.model.qa_records)
        ).filter(self.model.id == document_id).first()
        
        if document:
            # 更新各个字段
            document.one_sentence_summary = analysis.get('one_sentence_summary', '')
            document.summary = analysis.get('summary', '')
            document.key_points = json.dumps(analysis.get('key_points', []), ensure_ascii=False)
            document.key_concepts = json.dumps(analysis.get('key_concepts', []), ensure_ascii=False)
            document.document_type = analysis.get('document_type', '')
            document.difficulty_level = analysis.get('difficulty_level', '')
            document.target_audience = analysis.get('target_audience', '')
            document.learning_suggestions = json.dumps(analysis.get('learning_suggestions', []), ensure_ascii=False)
            document.estimated_reading_time = analysis.get('estimated_reading_time', '')
            document.common_questions = json.dumps(analysis.get('common_questions', []), ensure_ascii=False)
            
            self.db.commit()
            self.db.refresh(document)
        return document


class DocumentSectionRepository(BaseRepository[DocumentSection]):
    """文档章节Repository"""
    
    def __init__(self, db: Session):
        super().__init__(DocumentSection, db)
    
    def get_by_document(self, document_id: int) -> List[DocumentSection]:
        """获取文档的所有章节"""
        return self.db.query(self.model).filter(
            self.model.document_id == document_id
        ).order_by(self.model.order_index).all()
    
    def create_batch(self, sections: List[dict]) -> List[DocumentSection]:
        """批量创建章节"""
        db_sections = [self.model(**section) for section in sections]
        self.db.add_all(db_sections)
        self.db.commit()
        for section in db_sections:
            self.db.refresh(section)
        return db_sections


class DocumentChunkRepository(BaseRepository[DocumentChunk]):
    """文档分块Repository"""
    
    def __init__(self, db: Session):
        super().__init__(DocumentChunk, db)
    
    def get_by_document(self, document_id: int) -> List[DocumentChunk]:
        """获取文档的所有分块"""
        return self.db.query(self.model).filter(
            self.model.document_id == document_id
        ).order_by(self.model.chunk_index).all()
    
    def create_batch(self, chunks: List[dict]) -> List[DocumentChunk]:
        """批量创建分块"""
        db_chunks = [self.model(**chunk) for chunk in chunks]
        self.db.add_all(db_chunks)
        self.db.commit()
        for chunk in db_chunks:
            self.db.refresh(chunk)
        return db_chunks

