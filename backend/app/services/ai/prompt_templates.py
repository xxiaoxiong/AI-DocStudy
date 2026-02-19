"""
Prompt模板管理
"""

# RAG问答Prompt模板
RAG_QA_PROMPT = """你是一位专业的培训助教，请基于以下文档内容回答用户的问题。

文档内容：
{context}

用户问题：{question}

回答要求：
1. 只基于提供的文档内容回答，不要编造信息
2. 如果文档中没有相关信息，请明确告知用户
3. 回答要准确、清晰、有条理
4. 使用中文回答

请回答："""


# 文档智能分析Prompt（增强版）
DOCUMENT_ANALYSIS_PROMPT = """你是一位专业的文档分析专家，请对以下文档进行全面的智能分析。

文档内容：
{content}

请按以下JSON格式输出分析结果：
{{
  "one_sentence_summary": "用一句话概括文档核心内容（30字以内）",
  "summary": "详细摘要（200-300字，包含文档的主要内容、目的和价值）",
  "key_points": [
    "核心要点1：具体描述",
    "核心要点2：具体描述",
    "核心要点3：具体描述",
    "核心要点4：具体描述",
    "核心要点5：具体描述"
  ],
  "key_concepts": [
    {{"term": "关键术语1", "definition": "术语解释"}},
    {{"term": "关键术语2", "definition": "术语解释"}},
    {{"term": "关键术语3", "definition": "术语解释"}}
  ],
  "document_type": "文档类型（如：技术文档、政策法规、培训教材、学术论文等）",
  "difficulty_level": "难度等级（入门/中级/高级）",
  "target_audience": "目标读者群体",
  "learning_suggestions": [
    "学习建议1：具体的学习方法或注意事项",
    "学习建议2：具体的学习方法或注意事项",
    "学习建议3：具体的学习方法或注意事项"
  ],
  "estimated_reading_time": "预计阅读时间（分钟）",
  "common_questions": [
    "基于文档内容可能产生的常见问题1",
    "基于文档内容可能产生的常见问题2",
    "基于文档内容可能产生的常见问题3"
  ]
}}

注意：
1. 所有内容必须基于文档实际内容，不要编造
2. 关键概念要选择文档中最重要的专业术语
3. 学习建议要具体、可操作
4. 严格按照JSON格式输出，确保可以被解析"""


# 章节智能提取Prompt
SECTION_EXTRACTION_PROMPT = """请分析以下文档内容，智能提取章节结构。

文档内容：
{content}

请按以下格式输出JSON数组：
[
  {{"title": "第一章 标题", "level": 1, "summary": "本章节主要内容概述"}},
  {{"title": "1.1 小节标题", "level": 2, "summary": "本小节主要内容概述"}},
  {{"title": "第二章 标题", "level": 1, "summary": "本章节主要内容概述"}}
]

注意：
1. level=1表示一级标题，level=2表示二级标题
2. 只提取主要章节，不要过于细碎
3. 每个章节都要有简短的内容概述（20-50字）
4. 严格按照JSON格式输出"""


def format_rag_prompt(context: str, question: str) -> str:
    """
    格式化RAG问答Prompt
    
    Args:
        context: 文档上下文
        question: 用户问题
        
    Returns:
        格式化后的Prompt
    """
    return RAG_QA_PROMPT.format(context=context, question=question)


def format_document_analysis_prompt(content: str) -> str:
    """
    格式化文档智能分析Prompt
    
    Args:
        content: 文档内容
        
    Returns:
        格式化后的Prompt
    """
    # 限制内容长度，避免超过token限制
    max_length = 6000
    if len(content) > max_length:
        content = content[:max_length] + "...\n\n[文档内容过长，已截取前6000字进行分析]"
    
    return DOCUMENT_ANALYSIS_PROMPT.format(content=content)


def format_section_prompt(content: str) -> str:
    """
    格式化章节提取Prompt
    
    Args:
        content: 文档内容
        
    Returns:
        格式化后的Prompt
    """
    # 限制内容长度
    max_length = 4000
    if len(content) > max_length:
        content = content[:max_length] + "..."
    
    return SECTION_EXTRACTION_PROMPT.format(content=content)



