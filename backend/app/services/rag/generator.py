"""
RAG问答生成器
"""
from typing import List, Dict, Optional
from app.services.rag.retriever import vector_retriever
from app.services.ai import get_llm_client
from app.services.ai.prompt_templates import format_rag_prompt


class RAGGenerator:
    """RAG问答生成器"""
    
    async def answer_question(
        self,
        document_id: int,
        question: str,
        top_k: int = 3
    ) -> Dict:
        """
        基于文档回答问题
        
        Args:
            document_id: 文档ID
            question: 用户问题
            top_k: 检索top-k个相关文档块
            
        Returns:
            包含答案和来源的字典
        """
        # 1. 向量检索相关文档块
        retrieved_chunks = vector_retriever.search(
            document_id=document_id,
            query=question,
            top_k=top_k
        )
        
        if not retrieved_chunks:
            return {
                "answer": "抱歉，我在文档中没有找到相关内容来回答您的问题。",
                "sources": [],
                "has_answer": False
            }
        
        # 2. 构建上下文
        context_parts = []
        sources = []
        
        for i, chunk in enumerate(retrieved_chunks, 1):
            context_parts.append(f"[片段{i}]\n{chunk['content']}\n")
            meta = chunk.get('metadata', {})
            sources.append({
                "chunk_id": chunk['id'],
                "content": chunk['content'][:200] + "..." if len(chunk['content']) > 200 else chunk['content'],
                "metadata": meta,
                "relevance_score": 1 - chunk.get('distance', 0),
                "document_id": meta.get('document_id', document_id),
                "document_title": meta.get('document_title', '')
            })
        
        context = "\n".join(context_parts)
        
        # 3. 构建Prompt
        prompt = format_rag_prompt(context=context, question=question)
        
        # 4. 调用LLM生成答案
        try:
            answer = await get_llm_client().generate(prompt, temperature=0.3)
            
            return {
                "answer": answer,
                "sources": sources,
                "has_answer": True
            }
        
        except Exception as e:
            raise Exception(f"生成答案失败: {str(e)}")
    
    async def answer_question_all(
        self,
        question: str,
        top_k: int = 5
    ) -> Dict:
        """
        跨所有文档回答问题
        """
        retrieved_chunks = vector_retriever.search_all(query=question, top_k=top_k)
        
        if not retrieved_chunks:
            return {
                "answer": "抱歉，我在所有文档中没有找到相关内容来回答您的问题。请先上传相关文档。",
                "sources": [],
                "has_answer": False
            }
        
        context_parts = []
        sources = []
        for i, chunk in enumerate(retrieved_chunks, 1):
            context_parts.append(f"[片段{i}]\n{chunk['content']}\n")
            meta = chunk.get('metadata', {})
            sources.append({
                "chunk_id": chunk['id'],
                "content": chunk['content'][:200] + "..." if len(chunk['content']) > 200 else chunk['content'],
                "metadata": meta,
                "relevance_score": 1 - chunk.get('distance', 0),
                "document_id": meta.get('document_id'),
                "document_title": meta.get('document_title', '')
            })
        
        context = "\n".join(context_parts)
        prompt = format_rag_prompt(context=context, question=question)
        
        try:
            answer = await get_llm_client().generate(prompt, temperature=0.3)
            return {"answer": answer, "sources": sources, "has_answer": True}
        except Exception as e:
            raise Exception(f"生成答案失败: {str(e)}")

    async def generate_related_questions(
        self,
        document_id: int,
        current_question: str,
        count: int = 3
    ) -> List[str]:
        """
        生成相关问题推荐
        
        Args:
            document_id: 文档ID
            current_question: 当前问题
            count: 生成数量
            
        Returns:
            相关问题列表
        """
        # 检索相关内容
        retrieved_chunks = vector_retriever.search(
            document_id=document_id,
            query=current_question,
            top_k=2
        )
        
        if not retrieved_chunks:
            return []
        
        # 构建上下文
        context = "\n".join([chunk['content'][:500] for chunk in retrieved_chunks])
        
        # 构建Prompt
        prompt = f"""基于以下文档内容，生成{count}个相关的问题。

文档内容：
{context}

当前问题：{current_question}

请生成{count}个与当前问题相关但角度不同的问题，每行一个问题，不要编号。"""
        
        try:
            response = await get_llm_client().generate(prompt, temperature=0.7)
            
            # 解析生成的问题
            questions = [q.strip() for q in response.split('\n') if q.strip()]
            questions = [q.lstrip('0123456789.-、 ') for q in questions]  # 去除编号
            
            return questions[:count]
        
        except Exception as e:
            print(f"生成相关问题失败: {str(e)}")
            return []


# 全局实例
rag_generator = RAGGenerator()



