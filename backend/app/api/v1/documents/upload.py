from fastapi import APIRouter, UploadFile, File, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.document import UploadResponse
from app.repositories.document import DocumentRepository
from app.services.document.processor import DocumentProcessor
from app.utils.file_handler import FileHandler

router = APIRouter()


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
        
        # 4. 后台处理文档
        background_tasks.add_task(
            process_document_task,
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


def process_document_task(document_id: int, file_path: str):
    """后台任务：处理文档（异步调用AI分析）"""
    from app.core.database import SessionLocal
    import asyncio
    
    # 创建新的数据库会话
    db = SessionLocal()
    try:
        processor = DocumentProcessor(db)
        # 使用asyncio运行异步处理
        asyncio.run(processor.process(document_id, file_path))
    except Exception as e:
        print(f"文档处理任务失败: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

