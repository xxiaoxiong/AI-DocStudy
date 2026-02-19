import os
import hashlib
from pathlib import Path
from typing import Tuple
from fastapi import UploadFile
from app.core.config import settings


class FileHandler:
    """文件处理工具"""
    
    @staticmethod
    def get_file_hash(content: bytes) -> str:
        """计算文件hash"""
        return hashlib.sha256(content).hexdigest()
    
    @staticmethod
    def get_file_extension(filename: str) -> str:
        """获取文件扩展名"""
        return Path(filename).suffix.lower()
    
    @staticmethod
    def is_allowed_file(filename: str) -> bool:
        """检查文件类型是否允许"""
        allowed_extensions = {'.pdf', '.docx', '.doc', '.txt', '.md'}
        return FileHandler.get_file_extension(filename) in allowed_extensions
    
    @staticmethod
    async def save_upload_file(file: UploadFile, user_id: int) -> Tuple[str, int]:
        """
        保存上传的文件
        返回: (文件路径, 文件大小)
        """
        # 创建上传目录
        upload_dir = Path(settings.UPLOAD_DIR) / str(user_id)
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # 读取文件内容
        content = await file.read()
        file_size = len(content)
        
        # 检查文件大小
        if file_size > settings.MAX_UPLOAD_SIZE:
            raise ValueError(f"文件大小超过限制({settings.MAX_UPLOAD_SIZE / 1024 / 1024}MB)")
        
        # 生成文件名(使用hash避免重复)
        file_hash = FileHandler.get_file_hash(content)
        file_ext = FileHandler.get_file_extension(file.filename)
        filename = f"{file_hash}{file_ext}"
        file_path = upload_dir / filename
        
        # 保存文件
        with open(file_path, 'wb') as f:
            f.write(content)
        
        return str(file_path), file_size
    
    @staticmethod
    def delete_file(file_path: str) -> bool:
        """删除文件"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception:
            return False
    
    @staticmethod
    def get_file_type(filename: str) -> str:
        """获取文件类型"""
        ext = FileHandler.get_file_extension(filename)
        type_map = {
            '.pdf': 'pdf',
            '.docx': 'docx',
            '.doc': 'doc',
            '.txt': 'txt',
            '.md': 'markdown'
        }
        return type_map.get(ext, 'unknown')



