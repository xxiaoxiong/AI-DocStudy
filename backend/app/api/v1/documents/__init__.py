from fastapi import APIRouter
from . import upload, manage

router = APIRouter()

# 先注册 upload 路由（更具体的路径 /documents/upload）
router.include_router(upload.router, prefix="/documents", tags=["documents"])
# 再注册 manage 路由（通用路径 /documents）
router.include_router(manage.router, prefix="/documents", tags=["documents"])



