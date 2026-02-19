"""
文档处理进度跟踪器
"""
import json
import time
from datetime import datetime
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from app.models.process_log import DocumentProcessLog


class ProcessLogger:
    """文档处理进度跟踪器"""
    
    def __init__(self, db: Session, document_id: int):
        self.db = db
        self.document_id = document_id
        self.log_record = None
        self.logs = []
        self.start_time = time.time()
        
    def start(self):
        """开始处理"""
        self.log_record = DocumentProcessLog(
            document_id=self.document_id,
            status='pending',
            progress=0.0,
            current_step='准备开始处理',
            total_steps=6,
            completed_steps=0,
            logs=[]
        )
        self.db.add(self.log_record)
        self.db.commit()
        self.db.refresh(self.log_record)
        
        self.add_log('info', '文档处理任务已创建')
        return self.log_record.id
    
    def update_step(self, status: str, step_name: str, progress: float):
        """更新处理步骤"""
        if not self.log_record:
            return
        
        self.log_record.status = status
        self.log_record.current_step = step_name
        self.log_record.progress = progress
        self.log_record.completed_steps = int(progress / 100 * self.log_record.total_steps)
        self.log_record.logs = json.dumps(self.logs, ensure_ascii=False)
        
        self.db.commit()
        self.add_log('info', f'开始: {step_name}')
    
    def add_log(self, level: str, message: str, details: Optional[Dict] = None):
        """添加日志"""
        log_entry = {
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'level': level,  # info, warning, error, success
            'message': message
        }
        if details:
            log_entry['details'] = details
        
        self.logs.append(log_entry)
        
        # 实时更新到数据库
        if self.log_record:
            self.log_record.logs = json.dumps(self.logs, ensure_ascii=False)
            self.db.commit()
    
    def set_statistics(self, **kwargs):
        """设置统计信息"""
        if not self.log_record:
            return
        
        for key, value in kwargs.items():
            if hasattr(self.log_record, key):
                setattr(self.log_record, key, value)
        
        self.db.commit()
    
    def complete(self):
        """完成处理"""
        if not self.log_record:
            return
        
        total_time = time.time() - self.start_time
        
        self.log_record.status = 'completed'
        self.log_record.progress = 100.0
        self.log_record.current_step = '处理完成'
        self.log_record.completed_steps = self.log_record.total_steps
        self.log_record.total_time = round(total_time, 2)
        self.log_record.completed_at = datetime.now()
        self.log_record.logs = json.dumps(self.logs, ensure_ascii=False)
        
        self.db.commit()
        
        self.add_log('success', f'文档处理完成，总耗时 {total_time:.2f} 秒')
    
    def fail(self, error_message: str, error_traceback: Optional[str] = None):
        """处理失败"""
        if not self.log_record:
            return
        
        total_time = time.time() - self.start_time
        
        self.log_record.status = 'failed'
        self.log_record.current_step = '处理失败'
        self.log_record.error_message = error_message
        self.log_record.error_traceback = error_traceback
        self.log_record.total_time = round(total_time, 2)
        self.log_record.completed_at = datetime.now()
        self.log_record.logs = json.dumps(self.logs, ensure_ascii=False)
        
        self.db.commit()
        
        self.add_log('error', f'处理失败: {error_message}')
    
    def get_progress(self) -> Dict:
        """获取当前进度"""
        if not self.log_record:
            return {}
        
        self.db.refresh(self.log_record)
        
        return {
            'status': self.log_record.status,
            'progress': self.log_record.progress,
            'current_step': self.log_record.current_step,
            'completed_steps': self.log_record.completed_steps,
            'total_steps': self.log_record.total_steps,
            'logs': json.loads(self.log_record.logs) if self.log_record.logs else []
        }

