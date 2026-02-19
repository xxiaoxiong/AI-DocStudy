from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional
import PyPDF2
import docx


class BaseParser(ABC):
    """文档解析器基类"""
    
    @abstractmethod
    def parse(self, file_path: str) -> str:
        """解析文档,返回文本内容"""
        pass


class PDFParser(BaseParser):
    """PDF解析器"""
    
    def parse(self, file_path: str) -> str:
        text = []
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text.append(page_text)
        except Exception as e:
            raise ValueError(f"PDF解析失败: {str(e)}")
        
        return '\n\n'.join(text)


class WordParser(BaseParser):
    """Word文档解析器"""
    
    def parse(self, file_path: str) -> str:
        try:
            doc = docx.Document(file_path)
            text = []
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text.append(paragraph.text)
            return '\n\n'.join(text)
        except Exception as e:
            raise ValueError(f"Word文档解析失败: {str(e)}")


class TextParser(BaseParser):
    """文本文件解析器"""
    
    def parse(self, file_path: str) -> str:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            # 尝试其他编码
            try:
                with open(file_path, 'r', encoding='gbk') as file:
                    return file.read()
            except Exception as e:
                raise ValueError(f"文本文件解析失败: {str(e)}")
        except Exception as e:
            raise ValueError(f"文本文件解析失败: {str(e)}")


class MarkdownParser(BaseParser):
    """Markdown文件解析器"""
    
    def parse(self, file_path: str) -> str:
        return TextParser().parse(file_path)


class DocumentParser:
    """文档解析器工厂"""
    
    def __init__(self):
        self.parsers = {
            '.pdf': PDFParser(),
            '.docx': WordParser(),
            '.doc': WordParser(),
            '.txt': TextParser(),
            '.md': MarkdownParser(),
        }
    
    def parse(self, file_path: str) -> str:
        """解析文档"""
        ext = Path(file_path).suffix.lower()
        parser = self.parsers.get(ext)
        
        if not parser:
            raise ValueError(f"不支持的文件类型: {ext}")
        
        return parser.parse(file_path)



