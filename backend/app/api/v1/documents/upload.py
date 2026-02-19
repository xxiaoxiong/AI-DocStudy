from fastapi import APIRouter, UploadFile, File, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.document import UploadResponse
from app.repositories.document import DocumentRepository
from app.services.document.processor import DocumentProcessor
from app.utils.file_handler import FileHandler
from concurrent.futures import ThreadPoolExecutor
import asyncio

router = APIRouter()

# 创建线程池执行器（用于真正的后台任务）
executor = ThreadPoolExecutor(max_workers=3)


@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    title: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """上传文档"""
    
    # 1. 验证文件类型
    if not FileHandler.is_allowed_file(file.filename):
        raise HTTPException(status_code=400, detail="不支持的文件类型")
    
    try:
        # 2. 保存文件
        file_path, file_size = await FileHandler.save_upload_file(file, current_user.id)
        
        # 3. 创建文档记录
        repo = DocumentRepository(db)
        document = repo.create({
            "title": title or file.filename,
            "file_path": file_path,
            "file_type": FileHandler.get_file_type(file.filename),
            "file_size": file_size,
            "uploaded_by": current_user.id,
            "status": "processing"
        })
        
        # 4. 在独立线程中处理文档（真正的异步，不阻塞主进程）
        executor.submit(
            process_document_task_sync,
            document.id,
            file_path
        )
        
        return UploadResponse(
            document_id=document.id,
            status="processing",
            message="文档上传成功，正在处理中"
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文档上传失败: {str(e)}")


def process_document_task_sync(document_id: int, file_path: str):
    """同步包装器：在独立线程中处理文档"""
    from app.core.database import SessionLocal
    
    # 创建新的数据库会话
    db = SessionLocal()
    try:
        # 重新加载配置，确保在后台任务中也能获取正确的配置
        from app.core.config import settings
        print(f"[后台任务] 文档 {document_id} 开始处理")
        print(f"[后台任务] 使用 API Key: {settings.DEEPSEEK_API_KEY[:10]}...{settings.DEEPSEEK_API_KEY[-10:]}")
        
        processor = DocumentProcessor(db)
        
        # 在新的事件循环中运行异步任务
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(processor.process(document_id, file_path))
            print(f"[后台任务] 文档 {document_id} 处理完成")
        finally:
            loop.close()
            
    except Exception as e:
        print(f"[后台任务] 文档 {document_id} 处理失败: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

