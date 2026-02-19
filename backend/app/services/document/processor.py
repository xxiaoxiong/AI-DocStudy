import hashlib
import json
import re
import time
import traceback
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from app.services.document.parser import DocumentParser
from app.repositories.document import DocumentRepository, DocumentSectionRepository, DocumentChunkRepository
from app.core.config import settings
from app.utils.process_logger import ProcessLogger


class DocumentProcessor:
    """文档处理器（增强版 - 集成AI智能分析和进度跟踪）"""
    
    def __init__(self, db: Session):
        self.db = db
        self.parser = DocumentParser()
        self.doc_repo = DocumentRepository(db)
        self.section_repo = DocumentSectionRepository(db)
        self.chunk_repo = DocumentChunkRepository(db)
        self.logger = None
    
    async def process(self, document_id: int, file_path: str):
        """处理文档（增强版 - 使用AI进行智能分析，带进度跟踪）"""
        # 创建进度跟踪器
        self.logger = ProcessLogger(self.db, document_id)
        self.logger.start()
        
        try:
            self.logger.add_log('info', f'开始处理文档 ID={document_id}')
            
            # 确保文件路径是绝对路径
            import os
            if not os.path.isabs(file_path):
                # 如果是相对路径，转换为绝对路径
                base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
                file_path = os.path.join(base_dir, file_path)
            
            self.logger.add_log('info', f'文件路径: {file_path}')
            
            # 检查文件是否存在
            if not os.path.exists(file_path):
                raise FileNotFoundError(f'文件不存在: {file_path}')
            
            # 步骤1: 解析文档 (0-20%)
            self.logger.update_step('parsing', '正在解析文档...', 5)
            text = self.parser.parse(file_path)
            
            if not text or len(text.strip()) < 10:
                self.logger.add_log('error', '文档内容为空或过短')
                self.doc_repo.update_status(document_id, 'failed')
                self.logger.fail('文档内容为空或过短')
                return
            
            self.logger.add_log('success', f'文档解析完成，共 {len(text)} 字')
            self.logger.set_statistics(parsed_text_length=len(text))
            self.logger.update_step('parsing', '文档解析完成', 20)
            
            # 步骤2: AI智能分析文档 (20-50%)
            self.logger.update_step('analyzing', '正在进行AI智能分析...', 25)
            ai_start_time = time.time()
            
            self.logger.add_log('info', '=' * 50)
            self.logger.add_log('info', '开始AI智能分析阶段')
            self.logger.add_log('info', '=' * 50)
            
            analysis_result = await self._ai_analyze_document(text)
            ai_time = time.time() - ai_start_time
            
            self.logger.add_log('info', '=' * 50)
            self.logger.add_log('info', 'AI分析阶段完成')
            self.logger.add_log('info', '=' * 50)
            
            if analysis_result:
                self.logger.add_log('info', '正在保存AI分析结果到数据库...')
                self.doc_repo.update_analysis(document_id, analysis_result)
                
                # 详细记录保存的数据
                self.logger.add_log('success', f'AI分析结果已保存，总耗时 {ai_time:.2f} 秒')
                self.logger.add_log('info', '保存的数据统计:', {
                    'one_sentence_summary': analysis_result.get('one_sentence_summary', '')[:50] + '...',
                    'summary_length': len(analysis_result.get('summary', '')),
                    'key_points_count': len(analysis_result.get('key_points', [])),
                    'key_concepts_count': len(analysis_result.get('key_concepts', [])),
                    'learning_suggestions_count': len(analysis_result.get('learning_suggestions', [])),
                    'common_questions_count': len(analysis_result.get('common_questions', []))
                })
                
                # 记录具体内容（用于调试）
                if analysis_result.get('key_points'):
                    self.logger.add_log('info', f'核心要点: {analysis_result.get("key_points")}')
                if analysis_result.get('common_questions'):
                    self.logger.add_log('info', f'常见问题: {analysis_result.get("common_questions")}')
                
                self.logger.set_statistics(ai_analysis_time=round(ai_time, 2))
            else:
                self.logger.add_log('error', 'AI分析返回了None，这不应该发生！')
            
            self.logger.update_step('analyzing', 'AI分析完成', 50)
            
            # 步骤3: 提取章节结构 (50-65%)
            self.logger.update_step('extracting', '正在提取章节结构...', 55)
            sections = await self._ai_extract_sections(document_id, text)
            if sections:
                self.section_repo.create_batch(sections)
                self.logger.add_log('success', f'提取了 {len(sections)} 个章节')
                self.logger.set_statistics(sections_count=len(sections))
            else:
                self.logger.add_log('warning', '未提取到章节')
            
            self.logger.update_step('extracting', '章节提取完成', 65)
            
            # 步骤4: 文档分块 (65-80%)
            self.logger.update_step('chunking', '正在进行文档分块...', 70)
            chunks = self._chunk_document(document_id, text)
            if chunks:
                chunk_records = self.chunk_repo.create_batch(chunks)
                self.logger.add_log('success', f'文档分块完成，共 {len(chunks)} 块')
                self.logger.set_statistics(chunks_count=len(chunks))
                
                # 步骤5: 向量化存储 (80-95%)
                self.logger.update_step('vectorizing', '正在进行向量化...', 85)
                try:
                    await self._vectorize_and_store(document_id, chunk_records)
                    self.logger.add_log('success', '向量化完成')
                except Exception as e:
                    self.logger.add_log('warning', f'向量化跳过: {str(e)}')
            
            self.logger.update_step('vectorizing', '向量化完成', 95)
            
            # 步骤6: 完成
            self.doc_repo.update_status(document_id, 'completed')
            self.logger.complete()
            
        except Exception as e:
            error_msg = str(e)
            error_trace = traceback.format_exc()
            
            self.logger.fail(error_msg, error_trace)
            self.doc_repo.update_status(document_id, 'failed')
    
    async def _ai_analyze_document(self, text: str) -> Optional[Dict]:
        """
        使用AI智能分析文档
        返回：摘要、要点、关键概念、学习建议等
        """
        try:
            from app.services.ai import get_llm_client
            from app.services.ai.prompt_templates import format_document_analysis_prompt
            
            self.logger.add_log('info', '开始AI分析流程')
            
            # 1. 获取LLM客户端
            self.logger.add_log('info', '正在初始化LLM客户端...')
            llm = get_llm_client()
            self.logger.add_log('success', 'LLM客户端初始化成功')
            
            # 2. 生成提示词
            self.logger.add_log('info', '正在生成分析提示词...')
            prompt = format_document_analysis_prompt(text)
            self.logger.add_log('success', f'提示词生成成功，长度: {len(prompt)} 字符')
            
            # 3. 调用AI
            self.logger.add_log('info', '正在调用DeepSeek API进行文档分析...')
            ai_start = time.time()
            response = await llm.generate(prompt, temperature=0.3)
            ai_duration = time.time() - ai_start
            
            self.logger.add_log('success', f'AI响应成功，耗时: {ai_duration:.2f}秒，响应长度: {len(response)} 字符')
            self.logger.add_log('info', f'AI响应内容预览: {response[:200]}...')
            
            # 4. 解析JSON响应
            self.logger.add_log('info', '正在解析AI响应JSON...')
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                self.logger.add_log('info', '从markdown代码块中提取JSON')
            else:
                json_str = response.strip()
                self.logger.add_log('info', '直接使用响应内容作为JSON')
            
            self.logger.add_log('info', f'待解析JSON长度: {len(json_str)} 字符')
            
            try:
                analysis = json.loads(json_str)
                self.logger.add_log('success', 'JSON解析成功')
            except json.JSONDecodeError as je:
                self.logger.add_log('error', f'JSON解析失败: {str(je)}')
                self.logger.add_log('error', f'JSON内容: {json_str[:500]}...')
                raise
            
            # 5. 验证数据
            key_points_count = len(analysis.get('key_points', []))
            key_concepts_count = len(analysis.get('key_concepts', []))
            common_questions_count = len(analysis.get('common_questions', []))
            
            self.logger.add_log('success', 'AI分析数据验证', {
                'has_summary': bool(analysis.get('summary')),
                'has_one_sentence_summary': bool(analysis.get('one_sentence_summary')),
                'key_points_count': key_points_count,
                'key_concepts_count': key_concepts_count,
                'learning_suggestions_count': len(analysis.get('learning_suggestions', [])),
                'common_questions_count': common_questions_count,
                'document_type': analysis.get('document_type', 'N/A'),
                'difficulty_level': analysis.get('difficulty_level', 'N/A')
            })
            
            # 6. 构造返回数据
            result = {
                'one_sentence_summary': analysis.get('one_sentence_summary', ''),
                'summary': analysis.get('summary', ''),
                'key_points': analysis.get('key_points', []),
                'key_concepts': analysis.get('key_concepts', []),
                'document_type': analysis.get('document_type', ''),
                'difficulty_level': analysis.get('difficulty_level', ''),
                'target_audience': analysis.get('target_audience', ''),
                'learning_suggestions': analysis.get('learning_suggestions', []),
                'estimated_reading_time': analysis.get('estimated_reading_time', ''),
                'common_questions': analysis.get('common_questions', [])
            }
            
            self.logger.add_log('success', 'AI分析完成，准备保存到数据库')
            return result
            
        except Exception as e:
            error_msg = f'AI分析失败: {str(e)}'
            self.logger.add_log('error', error_msg)
            
            # 记录详细错误信息
            import traceback
            error_trace = traceback.format_exc()
            self.logger.add_log('error', f'错误堆栈: {error_trace}')
            
            # 返回基础分析结果
            self.logger.add_log('warning', '使用基础分析结果作为降级方案')
            return {
                'summary': text[:300] + '...' if len(text) > 300 else text,
                'key_points': [],
                'key_concepts': [],
                'learning_suggestions': [],
                'common_questions': []
            }
    
    async def _ai_extract_sections(self, document_id: int, text: str) -> List[Dict]:
        """
        使用AI智能提取章节结构
        """
        try:
            from app.services.ai import get_llm_client
            from app.services.ai.prompt_templates import format_section_prompt
            
            llm = get_llm_client()
            prompt = format_section_prompt(text)
            
            self.logger.add_log('info', '正在使用AI提取章节结构...')
            response = await llm.generate(prompt, temperature=0.2)
            
            # 解析JSON响应
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                json_str = response.strip()
            
            sections_data = json.loads(json_str)
            
            # 转换为数据库格式
            sections = []
            for idx, section in enumerate(sections_data):
                sections.append({
                    'document_id': document_id,
                    'title': section.get('title', '')[:255],
                    'content': section.get('summary', ''),
                    'level': section.get('level', 1),
                    'parent_id': None,
                    'order_index': idx
                })
            
            self.logger.add_log('success', f'AI提取到 {len(sections)} 个章节')
            return sections
            
        except Exception as e:
            self.logger.add_log('warning', f'AI章节提取失败，使用规则方法: {str(e)}')
            # 降级到规则方法
            return self._extract_sections_by_rules(document_id, text)
    
    def _extract_sections_by_rules(self, document_id: int, text: str) -> List[Dict]:
        """
        使用规则方法提取章节结构（降级方案）
        """
        sections = []
        lines = text.split('\n')
        
        current_section = {
            'document_id': document_id,
            'title': '全文',
            'content': text[:500] + '...' if len(text) > 500 else text,
            'level': 1,
            'parent_id': None,
            'order_index': 0
        }
        sections.append(current_section)
        
        # 简单的章节识别
        section_index = 1
        for i, line in enumerate(lines):
            line = line.strip()
            if self._is_section_title(line):
                section_content = self._get_section_content(lines, i)
                sections.append({
                    'document_id': document_id,
                    'title': line[:255],
                    'content': section_content[:500] if section_content else '',
                    'level': 2,
                    'parent_id': None,
                    'order_index': section_index
                })
                section_index += 1
        
        return sections
    
    def _vectorize_and_store(self, document_id: int, chunk_records: List):
        """向量化文档分块并存储到Chroma"""
        try:
            from app.services.ai.embedding import embedding_service
            from app.services.rag.retriever import vector_retriever
            
            # 准备数据
            texts = [chunk.content for chunk in chunk_records]
            
            # 批量向量化
            print(f"正在向量化 {len(texts)} 个文档分块...")
            embeddings = embedding_service.embed_batch(texts)
            
            # 准备存储数据
            chunks_data = []
            for chunk in chunk_records:
                chunks_data.append({
                    'id': chunk.id,
                    'content': chunk.content,
                    'metadata': {
                        'chunk_index': chunk.chunk_index,
                        'document_id': document_id
                    }
                })
            
            # 存储到Chroma
            vector_retriever.add_documents(
                document_id=document_id,
                chunks=chunks_data,
                embeddings=embeddings
            )
            
            print(f"文档 {document_id} 向量化完成")
            
        except Exception as e:
            print(f"向量化失败: {str(e)}")
            # 向量化失败不影响文档处理状态
    
    def _is_section_title(self, line: str) -> bool:
        """判断是否是章节标题"""
        if not line or len(line) > 100:
            return False
        
        # 简单规则:以特定关键词开头
        keywords = ['第', '章', '节', '一、', '二、', '三、', '四、', '五、', 
                   '1.', '2.', '3.', '4.', '5.', '（一）', '（二）', '（三）']
        return any(line.startswith(kw) for kw in keywords)
    
    def _get_section_content(self, lines: List[str], start_index: int, max_lines: int = 50) -> str:
        """获取章节内容"""
        content_lines = []
        for i in range(start_index + 1, min(start_index + max_lines, len(lines))):
            line = lines[i].strip()
            if self._is_section_title(line):
                break
            if line:
                content_lines.append(line)
        return '\n'.join(content_lines)
    
    def _chunk_document(self, document_id: int, text: str) -> List[Dict]:
        """文档分块"""
        chunks = []
        chunk_size = settings.CHUNK_SIZE
        overlap = settings.CHUNK_OVERLAP
        
        # 按段落分割
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        current_chunk = []
        current_length = 0
        chunk_index = 0
        
        for paragraph in paragraphs:
            para_length = len(paragraph)
            
            # 如果当前块加上新段落超过限制,保存当前块
            if current_length + para_length > chunk_size and current_chunk:
                chunk_content = '\n\n'.join(current_chunk)
                chunks.append({
                    'document_id': document_id,
                    'section_id': None,
                    'chunk_index': chunk_index,
                    'content': chunk_content,
                    'chunk_hash': self._get_chunk_hash(chunk_content)
                })
                
                # 保留overlap部分
                if overlap > 0 and current_chunk:
                    overlap_text = current_chunk[-1]
                    current_chunk = [overlap_text]
                    current_length = len(overlap_text)
                else:
                    current_chunk = []
                    current_length = 0
                
                chunk_index += 1
            
            current_chunk.append(paragraph)
            current_length += para_length
        
        # 保存最后一个块
        if current_chunk:
            chunk_content = '\n\n'.join(current_chunk)
            chunks.append({
                'document_id': document_id,
                'section_id': None,
                'chunk_index': chunk_index,
                'content': chunk_content,
                'chunk_hash': self._get_chunk_hash(chunk_content)
            })
        
        return chunks
    
    def _get_chunk_hash(self, content: str) -> str:
        """计算chunk的hash"""
        return hashlib.sha256(content.encode()).hexdigest()

