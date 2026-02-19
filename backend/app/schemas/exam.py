"""
考试相关Schema
"""
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime


class ExamGenerateRequest(BaseModel):
    """生成考题请求"""
    document_id: Optional[int] = None  # None表示跨所有文档
    single_count: int = 5    # 单选题数量
    judge_count: int = 3     # 判断题数量
    essay_count: int = 2     # 简答题数量
    difficulty: str = "medium"  # easy/medium/hard


class QuestionItem(BaseModel):
    """题目"""
    id: int
    type: str  # single/judge/essay
    content: str
    options: Optional[Dict[str, str]] = None
    answer: Optional[str] = None   # 答题时不返回给前端
    explanation: Optional[str] = None

    class Config:
        from_attributes = True


class ExamSessionResponse(BaseModel):
    """考试会话响应（含题目，不含答案）"""
    exam_id: int
    title: str
    document_id: Optional[int] = None
    document_title: Optional[str] = None
    total_questions: int
    single_count: int
    judge_count: int
    essay_count: int
    difficulty: str
    questions: List[QuestionItem]
    created_at: datetime


class AnswerSubmitItem(BaseModel):
    """单题答案"""
    question_id: int
    user_answer: str


class ExamSubmitRequest(BaseModel):
    """提交答案请求"""
    exam_id: int
    answers: List[AnswerSubmitItem]
    time_spent: int = 0  # 答题耗时（秒）


class AnswerResultItem(BaseModel):
    """单题结果"""
    question_id: int
    type: str
    content: str
    options: Optional[Dict[str, str]] = None
    user_answer: str
    correct_answer: str
    is_correct: bool
    score: float
    ai_feedback: Optional[str] = None
    explanation: Optional[str] = None


class ExamResultResponse(BaseModel):
    """考试结果"""
    exam_id: int
    title: str
    document_title: Optional[str] = None
    total_score: float         # 实际得分
    max_score: float           # 满分
    percentage: float          # 得分率
    passed: bool               # 是否通过（>=60%）
    single_correct: int
    single_total: int
    judge_correct: int
    judge_total: int
    essay_score: float
    essay_max: float
    answers: List[AnswerResultItem]
    time_spent: int
    completed_at: datetime


class ExamHistoryItem(BaseModel):
    """历史记录条目"""
    exam_id: int
    title: str
    document_title: Optional[str] = None
    total_score: float
    max_score: float
    percentage: float
    passed: bool
    total_questions: int
    created_at: datetime

    class Config:
        from_attributes = True


class ExamHistoryResponse(BaseModel):
    """历史记录列表"""
    records: List[ExamHistoryItem]
    total: int
