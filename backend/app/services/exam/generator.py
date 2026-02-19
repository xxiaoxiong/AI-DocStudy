"""
AI出题生成器
"""
import json
import re
from typing import List, Dict, Optional
from app.services.ai import get_llm_client
from app.services.rag.retriever import vector_retriever


QUESTION_GENERATION_PROMPT = """你是一位专业的培训考试出题专家，请基于以下文档内容生成考试题目。

文档内容：
{context}

出题要求：
- 单选题数量：{single_count} 道（每题4个选项A/B/C/D，只有1个正确答案）
- 判断题数量：{judge_count} 道（答案为"正确"或"错误"）
- 简答题数量：{essay_count} 道（需要文字作答）
- 难度：{difficulty}

请严格按以下JSON格式输出，不要有任何其他文字：
{{
  "questions": [
    {{
      "type": "single",
      "content": "题目内容",
      "options": {{"A": "选项A", "B": "选项B", "C": "选项C", "D": "选项D"}},
      "answer": "A",
      "explanation": "解析说明"
    }},
    {{
      "type": "judge",
      "content": "判断题内容，该说法是否正确？",
      "options": null,
      "answer": "正确",
      "explanation": "解析说明"
    }},
    {{
      "type": "essay",
      "content": "简答题内容",
      "options": null,
      "answer": "参考答案要点",
      "explanation": "评分要点"
    }}
  ]
}}

注意：
1. 题目必须基于文档实际内容，不要编造
2. 单选题选项要有合理的干扰项
3. 简答题参考答案要包含主要得分点
4. 严格按JSON格式输出"""


ESSAY_GRADING_PROMPT = """你是一位专业的考试评卷老师，请对学生的简答题回答进行评分和点评。

题目：{question}

参考答案要点：{reference_answer}

评分要点：{explanation}

学生回答：{user_answer}

请按以下JSON格式输出评分结果：
{{
  "score": 得分（0-100的整数，根据答案完整性和准确性评分）,
  "is_correct": true或false（得分>=60则为true）,
  "feedback": "详细的评语，指出答对的部分和不足之处，给出改进建议"
}}

注意：严格按JSON格式输出，不要有其他文字"""


class ExamGenerator:
    """AI出题生成器"""

    async def generate_questions(
        self,
        document_id: Optional[int],
        single_count: int = 5,
        judge_count: int = 3,
        essay_count: int = 2,
        difficulty: str = "medium",
        top_k: int = 15
    ) -> List[Dict]:
        """
        基于文档内容生成题目

        Args:
            document_id: 文档ID，None表示跨所有文档
            single_count: 单选题数量
            judge_count: 判断题数量
            essay_count: 简答题数量
            difficulty: 难度 easy/medium/hard
            top_k: 检索chunk数量

        Returns:
            题目列表
        """
        # 检索文档内容
        if document_id:
            chunks = vector_retriever.search(
                document_id=document_id,
                query="文档主要内容知识点考点",
                top_k=top_k
            )
        else:
            chunks = vector_retriever.search_all(
                query="文档主要内容知识点考点",
                top_k=top_k
            )

        if not chunks:
            raise ValueError("未找到文档内容，请确认文档已完成处理")

        context = "\n\n".join([c["content"] for c in chunks])
        if len(context) > 8000:
            context = context[:8000]

        difficulty_map = {"easy": "简单", "medium": "中等", "hard": "困难"}
        difficulty_cn = difficulty_map.get(difficulty, "中等")

        prompt = QUESTION_GENERATION_PROMPT.format(
            context=context,
            single_count=single_count,
            judge_count=judge_count,
            essay_count=essay_count,
            difficulty=difficulty_cn
        )

        raw = await get_llm_client().generate(prompt, temperature=0.7)

        return self._parse_questions(raw)

    def _parse_questions(self, raw: str) -> List[Dict]:
        """解析AI返回的题目JSON"""
        # 提取JSON块
        match = re.search(r'\{[\s\S]*\}', raw)
        if not match:
            raise ValueError(f"AI返回格式错误，无法解析题目: {raw[:200]}")

        try:
            data = json.loads(match.group())
            questions = data.get("questions", [])
            if not questions:
                raise ValueError("AI未生成任何题目")
            return questions
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON解析失败: {e}\n原始内容: {raw[:300]}")

    async def grade_essay(
        self,
        question_content: str,
        reference_answer: str,
        explanation: str,
        user_answer: str
    ) -> Dict:
        """
        AI评阅简答题

        Returns:
            {"score": int, "is_correct": bool, "feedback": str}
        """
        if not user_answer or not user_answer.strip():
            return {
                "score": 0,
                "is_correct": False,
                "feedback": "未作答"
            }

        prompt = ESSAY_GRADING_PROMPT.format(
            question=question_content,
            reference_answer=reference_answer,
            explanation=explanation or reference_answer,
            user_answer=user_answer
        )

        raw = await get_llm_client().generate(prompt, temperature=0.3)

        match = re.search(r'\{[\s\S]*\}', raw)
        if not match:
            return {"score": 50, "is_correct": True, "feedback": raw[:500]}

        try:
            result = json.loads(match.group())
            score = int(result.get("score", 50))
            return {
                "score": score,
                "is_correct": result.get("is_correct", score >= 60),
                "feedback": result.get("feedback", "")
            }
        except Exception:
            return {"score": 50, "is_correct": True, "feedback": raw[:500]}


exam_generator = ExamGenerator()
