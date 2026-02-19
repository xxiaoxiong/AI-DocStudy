from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI培训教学系统 - 智能文档学习与考试平台",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "欢迎使用AI培训教学系统",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok"}


# 注册路由
from app.api.v1 import auth
from app.api.v1.documents import router as documents_router
from app.api.v1.documents.progress import router as progress_router
from app.api.v1.documents.detail import router as detail_router
# from app.api.v1.qa import router as qa_router  # 暂时禁用，需要安装PyTorch等依赖

app.include_router(auth.router, prefix="/api/v1/auth", tags=["认证"])
app.include_router(documents_router, prefix="/api/v1", tags=["文档"])
app.include_router(progress_router, prefix="/api/v1/documents", tags=["文档处理进度"])
app.include_router(detail_router, prefix="/api/v1/documents", tags=["文档处理详情"])
# app.include_router(qa_router, prefix="/api/v1/qa", tags=["问答"])  # 暂时禁用

# TODO: 其他路由
# from app.api.v1 import exam
# app.include_router(exam.router, prefix="/api/v1/exam", tags=["考试"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

