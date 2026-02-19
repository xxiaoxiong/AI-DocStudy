from fastapi import APIRouter
from . import upload, manage, progress, detail

router = APIRouter()

# 先注册 upload 路由（更具体的路径 /documents/upload）
router.include_router(upload.router, prefix="/documents", tags=["documents"])
# 注册进度和详情路由（带 document_id 的路径，需在 manage 通用路由前注册）
router.include_router(progress.router, prefix="/documents", tags=["documents"])
router.include_router(detail.router, prefix="/documents", tags=["documents"])
# 最后注册 manage 路由（通用路径 /documents）
router.include_router(manage.router, prefix="/documents", tags=["documents"])



