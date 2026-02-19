"""
考试模块 API
"""
import json
import traceback
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.exam import Exam, ExamQuestion
from app.models.question import Question
from app.models.answer import AnswerRecord
from app.repositories.document import DocumentRepository
from app.repositories.base import BaseRepository
from app.schemas.exam import (
    ExamGenerateRequest,
    ExamSessionResponse,
    QuestionItem,
    ExamSubmitRequest,
    ExamResultResponse,
    AnswerResultItem,
    ExamHistoryResponse,
    ExamHistoryItem,
)
from app.services.exam.generator import exam_generator

router = APIRouter()


# ── 简单 Repository 包装 ──────────────────────────────────────────────────────

class ExamRepository(BaseRepository[Exam]):
    def __init__(self, db: Session):
        super().__init__(Exam, db)

    def get_by_user(self, user_id: int, skip: int = 0, limit: int = 50) -> List[Exam]:
        return (
            self.db.query(Exam)
            .filter(Exam.created_by == user_id)
            .order_by(Exam.created_at.desc())
            .offset(skip).limit(limit).all()
        )

    def count_by_user(self, user_id: int) -> int:
        return self.db.query(Exam).filter(Exam.created_by == user_id).count()


class QuestionRepository(BaseRepository[Question]):
    def __init__(self, db: Session):
        super().__init__(Question, db)


class AnswerRepository(BaseRepository[AnswerRecord]):
    def __init__(self, db: Session):
        super().__init__(AnswerRecord, db)

    def get_by_exam(self, exam_id: int, user_id: int) -> List[AnswerRecord]:
        return (
            self.db.query(AnswerRecord)
            .filter(AnswerRecord.exam_id == exam_id, AnswerRecord.user_id == user_id)
            .all()
        )


# ── 辅助函数 ──────────────────────────────────────────────────────────────────

def _get_exam_result_from_db(exam_id: int, user_id: int, db: Session) -> Optional[dict]:
    """从DB读取已有的考试结果（用于历史查询）"""
    exam = db.get(Exam, exam_id)
    if not exam or exam.created_by != user_id:
        return None

    answers = (
        db.query(AnswerRecord)
        .filter(AnswerRecord.exam_id == exam_id, AnswerRecord.user_id == user_id)
        .all()
    )
    if not answers:
        return None

    questions_map = {
        eq.question_id: eq.question
        for eq in db.query(ExamQuestion).filter(ExamQuestion.exam_id == exam_id).all()
    }

    answer_items = []
    total_score = 0.0
    max_score = 0.0
    single_correct = judge_correct = 0
    single_total = judge_total = 0
    essay_score = essay_max = 0.0

    for ar in answers:
        q = db.get(Question, ar.question_id)
        if not q:
            continue
        score = float(ar.score or 0)
        total_score += score

        if q.type == "single":
            single_total += 1
            max_score += 10
            if ar.is_correct:
                single_correct += 1
        elif q.type == "judge":
            judge_total += 1
            max_score += 5
            if ar.is_correct:
                judge_correct += 1
        elif q.type == "essay":
            essay_max += 20
            max_score += 20
            essay_score += score

        options = q.options if isinstance(q.options, dict) else (json.loads(q.options) if q.options else None)
        answer_items.append(AnswerResultItem(
            question_id=q.id,
            type=q.type,
            content=q.content,
            options=options,
            user_answer=ar.user_answer or "",
            correct_answer=q.answer,
            is_correct=bool(ar.is_correct),
            score=score,
            ai_feedback=ar.ai_feedback,
            explanation=q.explanation,
        ))

    doc_title = None
    if exam.document_id:
        doc = db.get(type(exam).document.property.mapper.class_, exam.document_id) if False else None
        from app.models.document import Document
        doc = db.get(Document, exam.document_id)
        if doc:
            doc_title = doc.title

    percentage = (total_score / max_score * 100) if max_score > 0 else 0

    return ExamResultResponse(
        exam_id=exam.id,
        title=exam.title,
        document_title=doc_title,
        total_score=total_score,
        max_score=max_score,
        percentage=round(percentage, 1),
        passed=percentage >= 60,
        single_correct=single_correct,
        single_total=single_total,
        judge_correct=judge_correct,
        judge_total=judge_total,
        essay_score=essay_score,
        essay_max=essay_max,
        answers=answer_items,
        time_spent=exam.duration or 0,
        completed_at=answers[0].answered_at if answers else datetime.now(),
    )


# ── API 端点 ──────────────────────────────────────────────────────────────────

@router.post("/generate", response_model=ExamSessionResponse)
async def generate_exam(
    req: ExamGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    AI生成考题，创建考试会话

    - document_id=None 表示跨所有文档出题
    - 返回题目列表（不含答案）
    """
    try:
        doc_repo = DocumentRepository(db)
        doc_title = None

        if req.document_id:
            doc = doc_repo.get(req.document_id)
            if not doc:
                raise HTTPException(status_code=404, detail="文档不存在")
            if doc.status != "completed":
                raise HTTPException(status_code=400, detail="文档还在处理中，请稍后再试")
            doc_title = doc.title

        # AI生成题目
        print(f"[Exam] 用户 {current_user.id} 开始生成考题，文档={req.document_id}")
        raw_questions = await exam_generator.generate_questions(
            document_id=req.document_id,
            single_count=req.single_count,
            judge_count=req.judge_count,
            essay_count=req.essay_count,
            difficulty=req.difficulty,
        )

        # 持久化题目
        q_repo = QuestionRepository(db)
        saved_questions: List[Question] = []
        for rq in raw_questions:
            q_type = rq.get("type", "single")
            options = rq.get("options")
            q = q_repo.create({
                "document_id": req.document_id or None,
                "type": q_type if q_type in ("single", "judge", "essay") else "single",
                "difficulty": req.difficulty if req.difficulty in ("easy", "medium", "hard") else "medium",
                "content": rq.get("content", ""),
                "options": json.dumps(options, ensure_ascii=False) if options else None,
                "answer": rq.get("answer", ""),
                "explanation": rq.get("explanation", ""),
            })
            saved_questions.append(q)

        # 创建考试会话
        difficulty_map = {"easy": "简单", "medium": "中等", "hard": "困难"}
        title = f"{'《' + doc_title + '》' if doc_title else '全库'}考试 - {difficulty_map.get(req.difficulty, '中等')}"

        exam_repo = ExamRepository(db)
        exam = exam_repo.create({
            "document_id": req.document_id,
            "title": title,
            "description": f"共{len(saved_questions)}题",
            "duration": 0,
            "total_score": req.single_count * 10 + req.judge_count * 5 + req.essay_count * 20,
            "pass_score": 60,
            "created_by": current_user.id,
        })

        # 关联题目
        for idx, q in enumerate(saved_questions):
            score = 10 if q.type == "single" else (5 if q.type == "judge" else 20)
            db.add(ExamQuestion(exam_id=exam.id, question_id=q.id, score=score, order_index=idx))
        db.commit()

        # 构建响应（不含答案）
        question_items = []
        for q in saved_questions:
            options = None
            if q.options:
                try:
                    options = json.loads(q.options) if isinstance(q.options, str) else q.options
                except Exception:
                    options = None
            question_items.append(QuestionItem(
                id=q.id,
                type=q.type,
                content=q.content,
                options=options,
            ))

        return ExamSessionResponse(
            exam_id=exam.id,
            title=exam.title,
            document_id=req.document_id,
            document_title=doc_title,
            total_questions=len(saved_questions),
            single_count=req.single_count,
            judge_count=req.judge_count,
            essay_count=req.essay_count,
            difficulty=req.difficulty,
            questions=question_items,
            created_at=exam.created_at,
        )

    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"生成考题失败: {str(e)}")


@router.post("/submit", response_model=ExamResultResponse)
async def submit_exam(
    req: ExamSubmitRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    提交答案，AI审题，返回详细结果
    """
    try:
        exam = db.get(Exam, req.exam_id)
        if not exam:
            raise HTTPException(status_code=404, detail="考试不存在")
        if exam.created_by != current_user.id:
            raise HTTPException(status_code=403, detail="无权操作此考试")

        # 获取所有题目
        exam_questions = (
            db.query(ExamQuestion)
            .filter(ExamQuestion.exam_id == req.exam_id)
            .order_by(ExamQuestion.order_index)
            .all()
        )
        questions_map = {eq.question_id: db.get(Question, eq.question_id) for eq in exam_questions}
        answers_map = {a.question_id: a.user_answer for a in req.answers}

        answer_items: List[AnswerResultItem] = []
        total_score = 0.0
        max_score = 0.0
        single_correct = judge_correct = 0
        single_total = judge_total = 0
        essay_score_total = essay_max = 0.0

        for eq in exam_questions:
            q = questions_map.get(eq.question_id)
            if not q:
                continue

            user_answer = answers_map.get(q.id, "").strip()
            is_correct = False
            score = 0.0
            ai_feedback = None

            if q.type == "single":
                single_total += 1
                max_score += 10
                is_correct = user_answer.upper() == q.answer.strip().upper()
                score = 10.0 if is_correct else 0.0
                if is_correct:
                    single_correct += 1

            elif q.type == "judge":
                judge_total += 1
                max_score += 5
                # 兼容"正确"/"错误"/"true"/"false"/"对"/"错"
                def normalize(s: str) -> str:
                    s = s.strip().lower()
                    if s in ("正确", "true", "对", "是", "✓"):
                        return "正确"
                    return "错误"
                is_correct = normalize(user_answer) == normalize(q.answer)
                score = 5.0 if is_correct else 0.0
                if is_correct:
                    judge_correct += 1

            elif q.type == "essay":
                essay_max += 20
                max_score += 20
                # AI评阅
                grade = await exam_generator.grade_essay(
                    question_content=q.content,
                    reference_answer=q.answer,
                    explanation=q.explanation or "",
                    user_answer=user_answer,
                )
                score = round(grade["score"] / 100 * 20, 1)  # 转换为20分制
                is_correct = grade["is_correct"]
                ai_feedback = grade["feedback"]
                essay_score_total += score

            total_score += score

            # 保存答题记录
            options = None
            if q.options:
                try:
                    options = json.loads(q.options) if isinstance(q.options, str) else q.options
                except Exception:
                    options = None

            db.add(AnswerRecord(
                user_id=current_user.id,
                exam_id=req.exam_id,
                question_id=q.id,
                user_answer=user_answer,
                is_correct=is_correct,
                score=score,
                ai_feedback=ai_feedback,
                time_spent=req.time_spent // len(exam_questions) if exam_questions else 0,
            ))

            answer_items.append(AnswerResultItem(
                question_id=q.id,
                type=q.type,
                content=q.content,
                options=options,
                user_answer=user_answer,
                correct_answer=q.answer,
                is_correct=is_correct,
                score=score,
                ai_feedback=ai_feedback,
                explanation=q.explanation,
            ))

        # 更新考试耗时
        exam.duration = req.time_spent
        db.commit()

        percentage = round(total_score / max_score * 100, 1) if max_score > 0 else 0

        doc_title = None
        if exam.document_id:
            from app.models.document import Document
            doc = db.get(Document, exam.document_id)
            if doc:
                doc_title = doc.title

        return ExamResultResponse(
            exam_id=exam.id,
            title=exam.title,
            document_title=doc_title,
            total_score=total_score,
            max_score=max_score,
            percentage=percentage,
            passed=percentage >= 60,
            single_correct=single_correct,
            single_total=single_total,
            judge_correct=judge_correct,
            judge_total=judge_total,
            essay_score=essay_score_total,
            essay_max=essay_max,
            answers=answer_items,
            time_spent=req.time_spent,
            completed_at=datetime.now(),
        )

    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"提交答案失败: {str(e)}")


@router.get("/history", response_model=ExamHistoryResponse)
async def get_exam_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取考试历史记录"""
    exam_repo = ExamRepository(db)
    skip = (page - 1) * page_size
    exams = exam_repo.get_by_user(current_user.id, skip=skip, limit=page_size)
    total = exam_repo.count_by_user(current_user.id)

    records = []
    for exam in exams:
        answers = (
            db.query(AnswerRecord)
            .filter(AnswerRecord.exam_id == exam.id, AnswerRecord.user_id == current_user.id)
            .all()
        )
        if not answers:
            continue

        total_score = sum(float(a.score or 0) for a in answers)
        max_score = float(exam.total_score or 100)
        percentage = round(total_score / max_score * 100, 1) if max_score > 0 else 0

        doc_title = None
        if exam.document_id:
            from app.models.document import Document
            doc = db.get(Document, exam.document_id)
            if doc:
                doc_title = doc.title

        records.append(ExamHistoryItem(
            exam_id=exam.id,
            title=exam.title,
            document_title=doc_title,
            total_score=total_score,
            max_score=max_score,
            percentage=percentage,
            passed=percentage >= 60,
            total_questions=len(answers),
            created_at=exam.created_at,
        ))

    return ExamHistoryResponse(records=records, total=total)


@router.get("/result/{exam_id}", response_model=ExamResultResponse)
async def get_exam_result(
    exam_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取某次考试的详细结果"""
    result = _get_exam_result_from_db(exam_id, current_user.id, db)
    if not result:
        raise HTTPException(status_code=404, detail="考试记录不存在")
    return result
